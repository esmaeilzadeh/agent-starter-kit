"""Browser journeys through the semantic workbench hierarchy."""
from __future__ import annotations

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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
sys.path.insert(0, str(Path(__file__).parent))
from engineering_fixture import evidence_workbench
from engineering_model.admission import load_published


class WorkbenchTests(unittest.TestCase):
    def _server(self, root):
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        listener.close()
        env = dict(os.environ, ASK_MODEL_ROOT=str(root), ASK_PYTHON=sys.executable,
                   PYTHONPATH=str(ROOT / "_ask/scripts"))
        proc = subprocess.Popen([str(ROOT / "ask"), "ui", "--server.headless=true",
                                 f"--server.port={port}", "--server.address=127.0.0.1"],
                                cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{port}"
        for _ in range(150):
            if proc.poll() is not None:
                self.fail(f"Streamlit exited during setup: {proc.returncode}")
            try:
                with urlopen(url, timeout=1):
                    return proc, url
            except (URLError, TimeoutError):
                time.sleep(.1)
        proc.terminate()
        self.fail("Streamlit did not start")

    @staticmethod
    def _open(page, route):
        names = {"scenario": "Uppercase behavior", "test:U": "Uppercase assertion",
                 "result:U": "Result / evidence", "decision": "Decision"}
        button = page.get_by_role("button", name=names.get(route, route), exact=False).first
        expect(button).to_be_visible(timeout=5000)
        button.click()

    def test_work_scenario_task_test_result_and_branch_journey(self):
        consumer, historical_sha = evidence_workbench()
        self.addCleanup(consumer.close)
        root = consumer.root
        before_head = consumer.git("rev-parse", "HEAD")
        before_refs = consumer.git("for-each-ref", "--format=%(refname) %(objectname)")
        before_model = (root / "work/w/engineering-model.json").read_bytes()
        server, url = self._server(root)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")
                expect(page.get_by_role("button", name="Uppercase behavior", exact=False)).to_be_visible()
                self._open(page, "scenario")
                expect(page.get_by_role("heading", name="Uppercase behavior")).to_be_visible()
                self._open(page, "test:U")
                expect(page.get_by_text("test_app.py", exact=False)).to_be_visible()
                self._open(page, "result:U")
                expect(page.get_by_text("Evidence candidate", exact=False)).to_be_visible()
                page.get_by_label("Evidence candidate").fill(historical_sha)
                page.get_by_role("button", name="Inspect candidate").click()
                expect(page.get_by_text("historical", exact=False)).to_be_visible()
                self.assertEqual(consumer.git("rev-parse", "HEAD"), before_head)
                self.assertEqual(consumer.git("for-each-ref", "--format=%(refname) %(objectname)"), before_refs)
                self.assertEqual((root / "work/w/engineering-model.json").read_bytes(), before_model)
                browser.close()
        finally:
            server.terminate()
            server.wait(timeout=5)

    def test_keyboard_narrow_layout_and_decision_journey(self):
        consumer, _ = evidence_workbench()
        self.addCleanup(consumer.close)
        root = consumer.root
        server, url = self._server(root)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(url, wait_until="domcontentloaded")
                expect(page.get_by_role("button", name="Uppercase behavior", exact=False)).to_be_visible()
                route = page.get_by_role("button", name="Uppercase behavior", exact=False)
                route.focus()
                self.assertTrue(route.evaluate("el => el === document.activeElement"), "route has visible keyboard focus")
                focus_style = route.evaluate("el => { const s=getComputedStyle(el); return s.outlineStyle !== 'none' || s.boxShadow !== 'none'; }")
                self.assertTrue(focus_style, "focused route exposes a visible focus indicator")
                self._open(page, "decision")
                expect(page.get_by_role("button", name="Resolve decision")).to_be_visible()
                option = page.get_by_label("Option")
                expect(option).to_be_visible()
                option.select_option(label="First")
                page.get_by_label("Actor").fill("Keyboard developer")
                page.get_by_label("Rationale").fill("Accessible option labels persist")
                page.get_by_role("button", name="Resolve decision").click()
                expect(page.get_by_text("resolved", exact=False)).to_be_visible()
                resolved = load_published(root, "w")
                choice = next(node for node in resolved.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["history"][-1]["actor"], "Keyboard developer")
                self.assertEqual(choice["history"][-1]["rationale"], "Accessible option labels persist")
                self.assertLessEqual(page.locator("body").evaluate("el => el.scrollWidth"), 390,
                                     "narrow layout has no horizontal page overflow")
                ratios = route.evaluate("""el => {
                  const rgb = v => v.match(/[\\d.]+/g).slice(0,3).map(Number).map(x => {
                    x /= 255; return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
                  });
                  const lum = c => .2126*c[0]+.7152*c[1]+.0722*c[2];
                  const a=lum(rgb(getComputedStyle(el).color));
                  const b=lum(rgb(getComputedStyle(el).backgroundColor));
                  return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
                }""")
                self.assertGreaterEqual(ratios, 4.5, "normal-size route text meets WCAG contrast")
                browser.close()
        finally:
            server.terminate()
            server.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
