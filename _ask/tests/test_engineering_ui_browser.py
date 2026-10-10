"""Legacy browser journeys migrated to the connected workbench outline."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
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
        consumer, _historical = evidence_workbench()
        self.addCleanup(consumer.close)
        root = consumer.root
        server, url = self._server(root)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    headless=True,
                    executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                    or pw.chromium.executable_path,
                    args=["--no-sandbox"],
                )
                first_context = browser.new_context()
                first = first_context.new_page()
                first.goto(url, wait_until="domcontentloaded")
                expect(first.get_by_role("button", name="Uppercase behavior", exact=False)).to_be_visible()
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
                self.choose_option(first, "one")
                first.get_by_label("Actor").fill("Browser developer")
                first.get_by_label("Rationale").fill("Use the amended requirement")
                first.get_by_role("button", name="Resolve decision").click()
                expect(first.get_by_text("No change was saved", exact=False)).to_be_visible()
                unchanged = load_published(root, "w")
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
                self.assertEqual(choice["history"][-1]["actor"], "Browser developer")
                self.assertEqual(choice["history"][-1]["rationale"], "Use the amended requirement")

                fresh = browser.new_context().new_page()
                fresh.goto(url, wait_until="domcontentloaded")
                self.open_route(fresh, "Decision")
                expect(fresh.get_by_text("Browser developer", exact=False)).to_be_visible()
                expect(fresh.get_by_text("Use the amended requirement", exact=False)).to_be_visible()
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
                        executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                        or pw.chromium.executable_path,
                        args=["--no-sandbox"],
                    )
                    page = browser.new_page()
                    page.goto(url, wait_until="domcontentloaded")
                    self.open_route(page, "Result / evidence")
                    expect(page.get_by_role("button", name="Load test results")).to_be_visible()
                    page.get_by_role("button", name="Load test results").click()
                    expect(page.get_by_text("Git evidence inspection is unavailable", exact=False)).to_be_visible()
                    self.assertNotIn("fatal: not a git repository", page.locator("body").inner_text())
                    browser.close()
            finally:
                self._shutdown(server)


if __name__ == "__main__":
    unittest.main()
