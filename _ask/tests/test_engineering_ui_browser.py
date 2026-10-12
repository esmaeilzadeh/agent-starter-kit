"""Legacy browser journeys migrated to the connected workbench outline."""
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
sys.path.insert(0, str(Path(__file__).parent))
from engineering_fixture import evidence_workbench, workbench_model
from engineering_model.actions import edit
from engineering_model.admission import load_published, validate_current
from engineering_model.projection import inspect_evidence


class WorkbenchBrowserJourney(unittest.TestCase):
    def _server(self, root):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        env = dict(os.environ, ASK_MODEL_ROOT=str(root), ASK_PYTHON=sys.executable,
                   PYTHONPATH=str(ROOT / "_ask/scripts"))
        server = subprocess.Popen([str(ROOT / "ask"), "ui", "--server.headless=true",
                                   f"--server.port={port}", "--server.address=127.0.0.1"],
                                  cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{port}"
        for _ in range(120):
            if server.poll() is not None:
                self.fail(f"Streamlit exited before startup with code {server.returncode}")
            try:
                with urlopen(url, timeout=1):
                    return server, url
            except (URLError, TimeoutError):
                time.sleep(.1)
        server.terminate()
        self.fail("Streamlit did not become ready")

    @staticmethod
    def open_route(page, label):
        button = page.get_by_role("button", name=label, exact=False).first
        expect(button).to_be_visible(timeout=7000)
        button.click()

    @staticmethod
    def open_result(page, test_id):
        route_key = "st-key-" + re.sub(r"[^A-Za-z0-9_-]", "-", f"route:result:{test_id}")
        button = page.locator(f'[class~="{route_key}"]').get_by_role("button")
        expect(button).to_be_visible(timeout=7000)
        button.click()

    @staticmethod
    def choose_option(page, value):
        control = page.get_by_label("Option")
        control.click()
        page.get_by_role("option", name=value, exact=False).click()

    @staticmethod
    def _shutdown(server):
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)

    def test_stale_spec_then_refresh_and_persist_in_new_browser_session(self):
        consumer, historical = evidence_workbench()
        self.addCleanup(consumer.close)
        root = consumer.root
        current_sha = consumer.git("rev-parse", "HEAD")
        historical_evidence = inspect_evidence(root, "w", historical)
        current_evidence = inspect_evidence(root, "w", current_sha)
        historical_case = next(test for scenario in historical_evidence["scenarios"]
                               for test in scenario["evidence"]["tests"] if test["test_id"] == "U")
        self.assertEqual(historical_case["final_execution"]["outcome"], "passed")
        self.assertEqual(historical_case["final_execution"]["case_id"], "test_app.Cases.test_unit")
        self.assertEqual(historical_evidence["status"], "historical")
        self.assertEqual(current_evidence["status"], "unavailable")
        self.assertEqual(historical_evidence["work_id"], "w")
        self.assertEqual(historical_case["test_id"], "U")
        self.assertEqual(historical_case["final_execution"]["source_sha"], historical)
        self.assertTrue(historical_case["final_execution"]["execution_id"])
        self.assertEqual(historical_case["final_execution"]["phase"], "final_green")
        server, url = self._server(root)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    headless=True,
                    **({"channel": os.environ["ASK_BROWSER_CHANNEL"]}
                       if os.environ.get("ASK_BROWSER_CHANNEL") else {
                           "executable_path": os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                           or pw.chromium.executable_path}),
                    args=["--no-sandbox"],
                )
                first_context = browser.new_context()
                first = first_context.new_page()
                first.goto(url, wait_until="domcontentloaded")
                expect(first.get_by_role("button", name="Uppercase behavior", exact=False)).to_be_visible()

                # E has a recorded historical pass; U has a current miss plus that historical run.
                self.open_result(first, "E")
                expect(first.get_by_text("Selected test: E · revision-bound planned identity", exact=True)).to_be_visible()
                expect(first.get_by_text("Passed", exact=False)).to_be_visible()
                expect(first.get_by_text("Historical evidence", exact=False)).to_be_visible()
                self.open_result(first, "U")
                expect(first.get_by_text("Selected test: U · revision-bound planned identity", exact=True)).to_be_visible()
                expect(first.get_by_text("No recorded execution is attached to this selected test.", exact=True)).to_be_visible()
                expect(first.get_by_text("Current evidence is unavailable", exact=False)).to_be_visible()
                expect(first.get_by_text("Historical evidence", exact=False)).to_be_visible()
                expect(first.get_by_role("heading", name="Test source", exact=True)).to_be_visible()
                expect(first.get_by_text("Exact HELLO output", exact=True)).to_be_visible()
                expect(first.get_by_text("test_app.py", exact=False)).to_be_visible()
                debug = first.locator("summary").filter(has_text="Technical details and identifiers")
                debug.click()
                expect(first.get_by_text("Snapshot digest", exact=True)).to_be_visible()
                expect(first.get_by_text("test_app.Cases.test_unit", exact=False)).to_be_visible()
                self.open_route(first, "Uppercase assertion")
                expect(first.get_by_text("test_app.py", exact=False)).to_be_visible()
                expect(first.get_by_text("test_app.Cases.test_unit", exact=False)).to_be_visible()
                self.open_route(first, "Build")
                expect(first.get_by_text("choice", exact=False)).to_be_visible()
                expect(first.get_by_text("Blockers", exact=False)).to_be_visible()

                self.open_route(first, "Decision")
                expect(first.get_by_role("button", name="Resolve decision")).to_be_visible()

                before, diagnostics = validate_current(root, "w")
                self.assertEqual(diagnostics, [], diagnostics)
                spec = dict(consumer.spec)
                spec["criteria"][0]["then"] = ["Reject invalid input"]
                plan_path = root / "work/w/test-plan.json"
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                plan["spec_digest"] = hashlib.sha256(json.dumps(
                    spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                changed = edit(root, "w", before.identity["digest"], {
                    "commands": [],
                    "files": {"specs/current/w.json": json.dumps(spec),
                              "work/w/test-plan.json": json.dumps(plan)},
                })
                self.assertTrue(changed["valid"], changed)
                stale_baseline = load_published(root, "w")
                self.assertIsNotNone(stale_baseline)
                state_dir = root / "work/w/traceability/model-state"
                pointer_path = state_dir / "current.json"
                stale_pointer = pointer_path.read_bytes()
                stale_generation_id = json.loads(stale_pointer)["generation"]
                stale_generation_path = state_dir / "generations" / stale_generation_id / "manifest.json"
                stale_generation = stale_generation_path.read_bytes()
                definition_paths = [root / "work/w/engineering-model.json",
                                    root / "specs/current/w.json", plan_path]
                stale_submission_bytes = {path: path.read_bytes() for path in definition_paths}
                self.choose_option(first, "one")
                first.get_by_label("Actor").fill("Browser developer")
                first.get_by_label("Rationale").fill("Use the amended requirement")
                first.get_by_role("button", name="Resolve decision").click()
                expect(first.get_by_text("No change was saved", exact=False)).to_be_visible()
                unchanged = load_published(root, "w")
                self.assertEqual(unchanged.identity, stale_baseline.identity,
                                 "stale submission does not change publication identity")
                self.assertEqual(pointer_path.read_bytes(), stale_pointer,
                                 "stale submission leaves the publication pointer unchanged")
                self.assertEqual(json.loads(pointer_path.read_bytes())["generation"], stale_generation_id)
                self.assertEqual(stale_generation_path.read_bytes(), stale_generation,
                                 "stale submission leaves selected generation bytes unchanged")
                self.assertEqual({path: path.read_bytes() for path in definition_paths},
                                 stale_submission_bytes,
                                 "stale choice cannot publish model or linked definition bytes")
                choice = next(node for node in unchanged.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["lifecycle"], "open")
                self.assertEqual(choice["history"], [])

                first.get_by_role("button", name="Refresh inputs").click()
                self.open_route(first, "Decision")
                self.choose_option(first, "one")
                first.get_by_label("Actor").fill("Browser developer")
                first.get_by_label("Rationale").fill("Use the amended requirement")
                first.get_by_role("button", name="Resolve decision").click()
                resolved = load_published(root, "w")
                choice = next(node for node in resolved.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["lifecycle"], "resolved")
                self.assertEqual(choice["history"][-1]["option_id"], "one")
                self.assertEqual(choice["history"][-1]["actor"], "Browser developer")
                self.assertEqual(choice["history"][-1]["rationale"], "Use the amended requirement")

                fresh = browser.new_context().new_page()
                fresh.goto(url, wait_until="domcontentloaded")
                self.open_route(fresh, "Decision")
                expect(fresh.get_by_text("Browser developer", exact=False)).to_be_visible()
                expect(fresh.get_by_text("Use the amended requirement", exact=False)).to_be_visible()
                self.open_route(fresh, "Build")
                expect(fresh.get_by_text("No blockers are recorded.", exact=False)).to_be_visible()
                expect(fresh.get_by_text("no completed result is attached", exact=False)).to_be_visible()
                first.screenshot(path="/tmp/wb009-browser-current.png", full_page=True)
                browser.close()
        finally:
            self._shutdown(server)

    def test_gitless_model_root_shows_actionable_evidence_unavailable_state(self):
        with tempfile.TemporaryDirectory(prefix="ask-ui-gitless-") as temporary:
            root = Path(temporary)
            workbench_model(root)
            server, url = self._server(root)
            try:
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(
                        headless=True,
                        **({"channel": os.environ["ASK_BROWSER_CHANNEL"]}
                           if os.environ.get("ASK_BROWSER_CHANNEL") else {
                               "executable_path": os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                               or pw.chromium.executable_path}),
                        args=["--no-sandbox"],
                    )
                    page = browser.new_page()
                    page.goto(url, wait_until="domcontentloaded")
                    self.open_route(page, "Behavior assertion")
                    expect(page.get_by_text("Selected test: CASE-1 · revision-bound planned identity", exact=True)).to_be_visible()
                    self.open_route(page, "Result / evidence")
                    expect(page.get_by_text("Selected test: CASE-1 · revision-bound planned identity", exact=True)).to_be_visible()
                    debug = page.locator("summary").filter(has_text="Technical details and identifiers")
                    expect(debug).to_be_visible()
                    debug.focus()
                    page.keyboard.press("Enter")
                    expect(debug.locator("xpath=..")).to_have_attribute("open", "")
                    expect(page.get_by_text("Snapshot digest", exact=True)).to_be_visible()
                    expect(page.get_by_text("Git revision", exact=True)).to_be_visible()
                    expect(page.get_by_text(
                        "Git evidence inspection is unavailable because the configured model root is not a Git checkout.",
                        exact=True)).to_be_visible()
                    expect(page.get_by_text("git show", exact=False)).to_be_visible()
                    expect(page.get_by_text("./ask model show", exact=False)).to_be_visible()
                    self.assertNotIn("fatal: not a git repository", page.locator("body").inner_text())
                    browser.close()
            finally:
                self._shutdown(server)


if __name__ == "__main__":
    unittest.main()
