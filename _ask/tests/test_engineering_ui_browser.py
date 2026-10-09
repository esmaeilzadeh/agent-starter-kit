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

from playwright.sync_api import sync_playwright

from engineering_fixture import workbench_model

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
from engineering_model.actions import edit
from engineering_model.admission import load_published, validate_current


class WorkbenchBrowserJourney(unittest.TestCase):
    @staticmethod
    def choose(page, label, value):
        control = page.get_by_role("combobox", name=label)
        control.click()
        control.fill(value)
        control.press("Enter")

    def test_stale_spec_then_refresh_and_persist_in_new_browser_session(self):
        with tempfile.TemporaryDirectory(prefix="ask-ui-browser-") as temporary:
            root = Path(temporary)
            _model, spec = workbench_model(root)
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            environment = dict(os.environ)
            environment["ASK_MODEL_ROOT"] = str(root)
            environment["PYTHONPATH"] = str(ROOT / "_ask/scripts")
            server = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", str(ROOT / "_ask/ui/streamlit_app.py"),
                 "--server.headless=true", f"--server.port={port}", "--server.address=127.0.0.1"],
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
                        first.get_by_text("build: blocked", exact=True).wait_for()
                        second_context = browser.new_context()
                        second = second_context.new_page()
                        second.goto(url, wait_until="domcontentloaded")
                        second.get_by_text("build: blocked", exact=True).wait_for()

                        before, diagnostics = validate_current(root, "pilot")
                        self.assertEqual(diagnostics, [], diagnostics)
                        spec["criteria"][0]["then"] = ["Reject invalid input"]
                        plan_path = root / "work/pilot/test-plan.json"
                        plan = json.loads(plan_path.read_text(encoding="utf-8"))
                        plan["spec_digest"] = hashlib.sha256(
                            json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
                        ).hexdigest()
                        changed = edit(root, "pilot", before.identity["digest"], {
                            "commands": [{"op": "revise_node", "id": "purpose",
                                          "changes": {"title": "Concurrent spec amendment"}}],
                            "files": {"specs/current/pilot.json": json.dumps(spec),
                                      "work/pilot/test-plan.json": json.dumps(plan)},
                        })
                        self.assertTrue(changed["valid"], changed)

                        self.choose(first, "Engineering object", "choice")
                        self.choose(first, "Option", "one")
                        first.get_by_label("Actor").fill("Browser developer")
                        first.get_by_label("Rationale").fill("Use the amended requirement")
                        first.get_by_role("button", name="Resolve decision").click()
                        first.get_by_text("did not succeed").wait_for()
                        unchanged = load_published(root, "pilot")
                        self.assertEqual(unchanged.document[
                            "nodes"][1]["lifecycle"], "open")

                        first.get_by_role("button", name="Refresh inputs").click()
                        self.choose(first, "Engineering object", "choice")
                        self.choose(first, "Option", "one")
                        first.get_by_label("Actor").fill("Browser developer")
                        first.get_by_label("Rationale").fill("Use the amended requirement")
                        first.get_by_role("button", name="Resolve decision").click()
                        first.get_by_text("build: ready", exact=True).wait_for()

                        fresh_context = browser.new_context()
                        fresh = fresh_context.new_page()
                        fresh.goto(url, wait_until="domcontentloaded")
                        fresh.get_by_text("build: ready", exact=True).wait_for()
                        self.choose(fresh, "Engineering object", "choice")
                        fresh.get_by_text(
                            "resolved: Browser developer — Use the amended requirement", exact=True
                        ).first.wait_for()
                        second.get_by_role("button", name="Refresh inputs").click()
                        second.get_by_text("build: ready", exact=True).wait_for()
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
