"""Real-browser two-session workbench journey against disposable model data."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

from engineering_fixture import evidence_workbench, workbench_model

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
from engineering_model.actions import edit
from engineering_model.admission import load_published, validate_current


class WorkbenchBrowserJourney(unittest.TestCase):
    @staticmethod
    def _table_below(page, heading):
        heading_box = page.get_by_text(heading, exact=True).bounding_box()
        tables = page.locator('[data-testid="stDataFrame"]')
        candidates = []
        for index in range(tables.count()):
            box = tables.nth(index).bounding_box()
            if box and heading_box and box["y"] >= heading_box["y"]:
                candidates.append((box["y"], tables.nth(index)))
        if not candidates:
            raise AssertionError(f"no rendered table follows {heading}")
        return min(candidates, key=lambda candidate: candidate[0])[1]

    @staticmethod
    def _click_row(page, table, row_index):
        table.scroll_into_view_if_needed()
        canvas = table.locator("canvas").first.bounding_box()
        if not canvas:
            raise AssertionError("table has no visible selection surface")
        page.mouse.click(canvas["x"] + 16, canvas["y"] + 54 + row_index * 36)

    @staticmethod
    def select_object(page, value):
        row_index = ["build", "case", "choice", "purpose", "requirement", "scenario"].index(value)
        table = WorkbenchBrowserJourney._table_below(page, "Engineering objects")
        WorkbenchBrowserJourney._click_row(page, table, row_index)

    @staticmethod
    def select_task_status(page, status):
        page.get_by_text(f"Status: {status}", exact=True).wait_for()

    @staticmethod
    def select_evidence_status(page, status):
        page.get_by_text(f"{status} evidence", exact=False).wait_for()

    @staticmethod
    def choose(page, label, value):
        if label == "Engineering object":
            WorkbenchBrowserJourney.select_object(page, value)
            return
        control = page.get_by_role("combobox", name=label)
        control.click()
        control.fill(value)
        control.press("Enter")

    def test_stale_spec_then_refresh_and_persist_in_new_browser_session(self):
        with tempfile.TemporaryDirectory(prefix="ask-ui-browser-") as temporary:
            root = Path(temporary)
            consumer, historical_sha = evidence_workbench()
            self.addCleanup(consumer.close)
            root = consumer.root
            current_sha = consumer.git("rev-parse", "HEAD")
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            environment = dict(os.environ)
            environment["ASK_MODEL_ROOT"] = str(root)
            environment["ASK_PYTHON"] = sys.executable
            environment["PYTHONPATH"] = str(ROOT / "_ask/scripts")
            server = subprocess.Popen(
                [str(ROOT / "ask"), "ui", "--server.headless=true",
                 f"--server.port={port}", "--server.address=127.0.0.1"],
                cwd=ROOT, env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            try:
                url = f"http://127.0.0.1:{port}"
                for _ in range(100):
                    if server.poll() is not None:
                        self.fail(f"Streamlit exited before startup with code {server.returncode}")
                    try:
                        with urlopen(url, timeout=1):
                            break
                    except (URLError, TimeoutError):
                        time.sleep(0.1)
                else:
                    self.fail("Streamlit did not become ready")

                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(
                        headless=True,
                        executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                        or playwright.chromium.executable_path,
                        args=["--no-sandbox"],
                    )
                    try:
                        first_context = browser.new_context()
                        first = first_context.new_page()
                        first.goto(url, wait_until="domcontentloaded")
                        self.select_task_status(first, "blocked")
                        self.select_evidence_status(first, "unavailable")
                        first.get_by_label("Evidence candidate").fill(current_sha)
                        first.get_by_role("button", name="Inspect evidence candidate").click()
                        self.select_evidence_status(first, "unavailable")
                        first.get_by_label("Evidence candidate").fill(historical_sha)
                        first.get_by_role("button", name="Inspect evidence candidate").click()
                        self.select_evidence_status(first, "historical")
                        second_context = browser.new_context()
                        second = second_context.new_page()
                        second.goto(url, wait_until="domcontentloaded")
                        self.select_task_status(second, "blocked")
                        self.select_object(first, "build")
                        expect(first.get_by_role("button", name="Resolve decision")).to_have_count(0)
                        self.select_object(first, "choice")
                        expect(first.get_by_role("button", name="Resolve decision")).to_be_visible()
                        first.screenshot(path="/tmp/structured-agentic-workbench.png", full_page=True)

                        before, diagnostics = validate_current(root, "w")
                        self.assertEqual(diagnostics, [], diagnostics)
                        spec = dict(consumer.spec)
                        spec["criteria"][0]["then"] = ["Reject invalid input"]
                        plan_path = root / "work/w/test-plan.json"
                        plan = json.loads(plan_path.read_text(encoding="utf-8"))
                        plan["spec_digest"] = hashlib.sha256(
                            json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
                        ).hexdigest()
                        changed = edit(root, "w", before.identity["digest"], {
                            "commands": [{"op": "revise_node", "id": "purpose",
                                          "changes": {"title": "Concurrent spec amendment"}}],
                            "files": {"specs/current/w.json": json.dumps(spec),
                                      "work/w/test-plan.json": json.dumps(plan)},
                        })
                        self.assertTrue(changed["valid"], changed)

                        self.choose(first, "Engineering object", "choice")
                        self.choose(first, "Option", "one")
                        first.get_by_label("Actor").fill("Browser developer")
                        first.get_by_label("Rationale").fill("Use the amended requirement")
                        first.get_by_role("button", name="Resolve decision").click()
                        first.get_by_text("did not succeed").wait_for()
                        unchanged = load_published(root, "w")
                        choice = next(node for node in unchanged.document["nodes"] if node["id"] == "choice")
                        self.assertEqual(choice["lifecycle"], "open")

                        first.get_by_role("button", name="Refresh inputs").click()
                        first.get_by_text(f"Snapshot: {unchanged.identity['digest']}").wait_for()
                        self.choose(first, "Engineering object", "choice")
                        self.choose(first, "Option", "one")
                        first.get_by_label("Actor").fill("Browser developer")
                        first.get_by_label("Rationale").fill("Use the amended requirement")
                        first.get_by_role("button", name="Resolve decision").click()
                        self.select_task_status(first, "ready")

                        fresh_context = browser.new_context()
                        fresh = fresh_context.new_page()
                        fresh.goto(url, wait_until="domcontentloaded")
                        self.select_task_status(fresh, "ready")
                        fresh.get_by_text(
                            "resolved: Browser developer — Use the amended requirement", exact=True
                        ).first.wait_for()
                        second.get_by_role("button", name="Refresh inputs").click()
                        self.select_task_status(second, "ready")
                    finally:
                        browser.close()
            finally:
                server.terminate()
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)

    def test_gitless_model_root_shows_actionable_evidence_unavailable_state(self):
        with tempfile.TemporaryDirectory(prefix="ask-ui-gitless-") as temporary:
            root = Path(temporary)
            workbench_model(root)
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            environment = dict(os.environ, ASK_MODEL_ROOT=str(root), ASK_PYTHON=sys.executable)
            server = subprocess.Popen(
                [str(ROOT / "ask"), "ui", "--server.headless=true",
                 f"--server.port={port}", "--server.address=127.0.0.1"],
                cwd=ROOT, env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            try:
                url = f"http://127.0.0.1:{port}"
                for _ in range(100):
                    if server.poll() is not None:
                        self.fail(f"Streamlit exited before startup with code {server.returncode}")
                    try:
                        with urlopen(url, timeout=1):
                            break
                    except (URLError, TimeoutError):
                        time.sleep(0.1)
                else:
                    self.fail("Streamlit did not become ready")

                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(
                        headless=True,
                        executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                        or playwright.chromium.executable_path,
                        args=["--no-sandbox"],
                    )
                    try:
                        page = browser.new_page()
                        page.goto(url, wait_until="domcontentloaded")
                        self.select_evidence_status(page, "unavailable")
                        page.get_by_text("Completion · 10", exact=True).click()
                        body = page.locator("body").inner_text()
                        self.assertIn("Git evidence inspection is unavailable", body)
                        self.assertNotIn("fatal: not a git repository", body)
                    finally:
                        browser.close()
            finally:
                server.terminate()
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
