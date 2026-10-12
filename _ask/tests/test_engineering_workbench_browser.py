"""Browser journeys through the semantic workbench hierarchy."""
from __future__ import annotations

import os
import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import yaml
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

    @staticmethod
    def _tab_to(page, target):
        page.evaluate("document.activeElement && document.activeElement.blur()")
        for _ in range(100):
            page.keyboard.press("Tab")
            if target.evaluate("el => el === document.activeElement"):
                return
        raise AssertionError("keyboard tab order did not reach the requested control")

    @staticmethod
    def _contrast(page, locator):
        return locator.evaluate("""el => {
          const rgba = value => {
            const parts = value.match(/[\\d.]+/g);
            return parts ? [Number(parts[0]), Number(parts[1]), Number(parts[2]),
                            parts.length > 3 ? Number(parts[3]) : 1] : [0, 0, 0, 0];
          };
          const blend = (front, back) => front.slice(0, 3).map((value, i) =>
            value * front[3] + back[i] * (1 - front[3]));
          let background = [255, 255, 255];
          const ancestors = [];
          for (let current = el; current; current = current.parentElement) ancestors.unshift(current);
          for (const current of ancestors) {
            const color = rgba(getComputedStyle(current).backgroundColor);
            if (color[3] > 0) background = blend(color, background);
          }
          const luminance = color => {
            const rgb = color.slice(0, 3).map(value => {
              value /= 255;
              return value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4;
            });
            return .2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2];
          };
          const foreground = rgba(getComputedStyle(el).color);
          const text = blend(foreground, background);
          const a = luminance(text), b = luminance(background);
          return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
        }""")

    @staticmethod
    def _select(page, label, value):
        control = page.get_by_label(label)
        expect(control).to_be_visible()
        control.click()
        page.get_by_role("option", name=value, exact=True).click()

    @staticmethod
    def _recorded_hierarchy(consumer):
        """Create explicit story/task records and two immutable work branches."""
        root = consumer.root
        consumer.git("branch", "main")
        model = json.loads((root / "work/w/engineering-model.json").read_text())
        model["nodes"].append({"id": "feature", "type": "feature", "title": "Text rendering",
                               "lifecycle": "active"})
        model["nodes"].append({"id": "story", "type": "story", "title": "Render uppercase text",
                               "lifecycle": "active"})
        model["edges"] = [edge for edge in model["edges"]
                           if not (edge["type"] == "contains" and edge["source"] == "requirement"
                                   and edge["target"] == "scenario")
                           and not (edge["type"] == "depends_on" and edge["source"] == "build")]
        model["edges"].extend([
            {"type": "contains", "source": "purpose", "target": "feature"},
            {"type": "contains", "source": "feature", "target": "story"},
            {"type": "contains", "source": "story", "target": "scenario"},
            {"type": "depends_on", "source": "review-build", "target": "choice"},
        ])
        plan_path = root / "work/w/test-plan.json"
        plan = json.loads(plan_path.read_text())
        plan["task_scopes"] = [{"task_id": "build", "test_ids": ["U"]},
                               {"task_id": "review-build", "test_ids": ["E"]}]
        graph = {"schema": "ask-inner-loop-tasks/v1", "work_id": "w", "tasks": [
            {"id": "build", "title": "Build", "outcome": "Render the promised uppercase output",
             "depends_on": [], "owned_paths": ["app.py"]},
            {"id": "review-build", "title": "Review build", "outcome": "Review the output",
             "depends_on": ["build"], "owned_paths": ["app.py"]},
        ]}
        consumer.write("work/w/engineering-model.json", model)
        consumer.write("work/w/test-plan.json", plan)
        consumer.write("work/w/inner-loop/tasks.yaml", yaml.safe_dump(graph, sort_keys=False))
        consumer.write("work/w/inner-loop/state.json", {
            "schema": "ask-inner-loop-state/v1", "work_id": "w", "revision": 1,
            "tasks": {
                "build": {"status": "integrated", "result_path": "work/w/inner-loop/results/WB-001.json"},
                "review-build": {"status": "pending", "result_path": ""},
            },
        })
        consumer.write("work/w/inner-loop/results/WB-001.json", {
            "schema": "ask-task-result/v2", "work_id": "w", "task_id": "WB-001",
            "candidate_sha": "fixture-candidate", "result": "passed",
        })
        consumer.commit("add recorded story and task journey fixture")

        alt_model = copy.deepcopy(model)
        alt_model["work_id"] = "w-alt"
        for node in alt_model["nodes"]:
            reference = node.get("reference")
            if reference:
                reference["path"] = reference["path"].replace("work/w/", "work/w-alt/").replace(
                    "specs/current/w.json", "specs/current/w-alt.json")
        alt_plan = copy.deepcopy(plan)
        alt_plan["work_id"] = "w-alt"
        alt_plan["spec_digest"] = hashlib.sha256(json.dumps(
            {**consumer.spec, "work_id": "w-alt"}, sort_keys=True,
            separators=(",", ":")).encode()).hexdigest()
        alt_graph = copy.deepcopy(graph)
        alt_graph["work_id"] = "w-alt"
        alt_spec = {**consumer.spec, "work_id": "w-alt"}
        consumer.write("work/w-alt/engineering-model.json", alt_model)
        consumer.write("work/w-alt/test-plan.json", alt_plan)
        consumer.write("work/w-alt/inner-loop/tasks.yaml", yaml.safe_dump(alt_graph, sort_keys=False))
        consumer.write("work/w-alt/inner-loop/state.json", {
            "schema": "ask-inner-loop-state/v1", "work_id": "w-alt", "revision": 1,
            "tasks": {"build": {"status": "pending", "result_path": ""},
                      "review-build": {"status": "pending", "result_path": ""}},
        })
        consumer.write("specs/current/w-alt.json", alt_spec)
        consumer.write("specs/current/w-alt.md", "# Alternate workstream\n")
        consumer.commit("add second live workstream fixture")
        consumer.git("branch", "agent/w-alt")
        consumer.git("switch", "agent/w-alt")
        source = root / "test_app.py"
        source.write_text(source.read_text() + "\n# Source revision unique to agent/w-alt.\n")
        consumer.commit("change selected source on the alternate branch")
        consumer.git("switch", "agent/w")

    def test_work_scenario_task_test_result_and_branch_journey(self):
        consumer, historical_sha = evidence_workbench()
        self.addCleanup(consumer.close)
        self._recorded_hierarchy(consumer)
        root = consumer.root
        before_head = consumer.git("rev-parse", "HEAD")
        before_refs = consumer.git("for-each-ref", "--format=%(refname) %(objectname)")
        definition_paths = [root / "work/w/engineering-model.json", root / "work/w/test-plan.json",
                            root / "work/w-alt/engineering-model.json", root / "work/w-alt/test-plan.json"]
        before_definitions = {path: path.read_bytes() for path in definition_paths}
        server, url = self._server(root)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")
                expect(page.get_by_text("Workstream: w", exact=False)).to_be_visible()
                expect(page.get_by_role("button", name="Uppercase behavior", exact=False)).to_be_visible()
                expect(page.get_by_role("button", name="Render uppercase text", exact=False)).to_be_visible()

                # Every summary opens the exact records represented by its count.
                page.get_by_role("button", name="View scenarios", exact=True).click()
                expect(page.get_by_text("Uppercase behavior", exact=True)).to_be_visible()
                expect(page.get_by_text("Second canonical behavior", exact=True)).to_be_visible()
                self.assertEqual(page.get_by_text("Uppercase behavior", exact=True).count(), 1)
                self.assertEqual(page.get_by_text("Second canonical behavior", exact=True).count(), 1)
                self._open(page, "Purpose")
                page.get_by_role("button", name="View tasks", exact=True).click()
                expect(page.get_by_text("build · completed", exact=False)).to_be_visible()
                expect(page.get_by_text("review-build · planned", exact=False)).to_be_visible()
                self._open(page, "Purpose")
                page.get_by_role("button", name="View blocked tasks", exact=True).click()
                expect(page.get_by_text("review-build · planned", exact=False)).to_be_visible()
                expect(page.get_by_text("build · completed", exact=False)).to_have_count(0)
                self._open(page, "Purpose")
                page.get_by_role("button", name="View open decisions", exact=True).click()
                expect(page.get_by_text("choice · open", exact=False)).to_be_visible()
                expect(page.get_by_text("Choose", exact=True)).to_be_visible()

                self._open(page, "Uppercase assertion")
                expect(page.get_by_text("Exact HELLO output", exact=False)).to_be_visible()
                expect(page.get_by_text("test_app.py", exact=False)).to_be_visible()
                expect(page.get_by_text("test_behavior", exact=False)).to_be_visible()
                self._open(page, "scenario")
                expect(page.get_by_role("heading", name="Uppercase behavior")).to_be_visible()
                self._open(page, "test:U")
                expect(page.get_by_text("test_app.py", exact=False)).to_be_visible()
                self._open(page, "result:U")
                expect(page.get_by_text("Evidence candidate", exact=False)).to_be_visible()
                page.get_by_role("button", name="Load test results").click()
                expect(page.get_by_text("Passed", exact=False)).to_be_visible(timeout=10000)
                expect(page.get_by_text("test U", exact=False)).to_be_visible()
                page.get_by_label("Evidence candidate").fill(historical_sha)
                page.get_by_role("button", name="Inspect candidate").click()
                expect(page.get_by_text("(historical)", exact=False)).to_be_visible()

                # The selected alternate work is read from its other branch and remains read-only.
                self._select(page, "Workstream", "w-alt")
                expect(page.get_by_text("Workstream: w-alt", exact=False)).to_be_visible()
                expect(page.get_by_text("Committed · agent/w-alt", exact=False)).to_be_visible()
                self._open(page, "Uppercase assertion")
                expect(page.get_by_text("Source revision unique to agent/w-alt", exact=False)).to_be_visible()
                expect(page.get_by_text("test_app.py", exact=False)).to_be_visible()
                self._open(page, "Result / evidence")
                expect(page.get_by_text("w-alt", exact=False)).to_be_visible()
                expect(page.get_by_text("No recorded execution", exact=False)).to_be_visible()
                self._open(page, "Decision")
                expect(page.get_by_text("This source is read-only", exact=False)).to_be_visible()
                self.assertEqual(page.get_by_role("button", name="Resolve decision").count(), 0)

                self.assertEqual(consumer.git("rev-parse", "HEAD"), before_head)
                self.assertEqual(consumer.git("for-each-ref", "--format=%(refname) %(objectname)"), before_refs)
                self.assertEqual({path: path.read_bytes() for path in definition_paths}, before_definitions)
                fresh_context = browser.new_context()
                fresh = fresh_context.new_page()
                fresh.goto(url, wait_until="domcontentloaded")
                expect(fresh.get_by_text("Workstream: w", exact=False)).to_be_visible()
                expect(fresh.get_by_text("Working tree", exact=False)).to_be_visible()
                fresh_context.close()
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
                for width in (390, 1440):
                    page.set_viewport_size({"width": width, "height": 844})
                    route = page.get_by_role("button", name="Uppercase behavior", exact=False).first
                    expect(route).to_be_visible()
                    self._tab_to(page, route)
                    focus_style = route.evaluate("el => { const s=getComputedStyle(el); return s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) >= 1 || s.boxShadow !== 'none'; }")
                    self.assertTrue(focus_style, "keyboard-focused route exposes a visible focus indicator")
                    focus_ratio = route.evaluate("""el => {
                      const style = getComputedStyle(el);
                      const color = style.outlineStyle !== 'none' ? style.outlineColor :
                        ((style.boxShadow.match(/rgba?\\([^)]*\\)/) || [])[0] || style.color);
                      const rgb = value => value.match(/[\\d.]+/g).slice(0,3).map(Number);
                      const lum = values => values.map(value => { value /= 255; return value <= .04045 ? value/12.92 : ((value+.055)/1.055)**2.4; })
                        .reduce((sum, value, index) => sum + value * [.2126,.7152,.0722][index], 0);
                      const a=lum(rgb(color)), b=lum(rgb(style.backgroundColor));
                      return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
                    }""")
                    self.assertGreaterEqual(focus_ratio, 3, "focus indicator contrasts with its control background")
                    self.assertGreaterEqual(self._contrast(page, route), 4.5,
                                            "normal-size route label meets text contrast")
                    page.keyboard.press("Enter")
                    expect(page.get_by_role("heading", name="Uppercase behavior")).to_be_visible()
                    task = page.get_by_role("button", name="Build", exact=False).first
                    self._tab_to(page, task)
                    page.keyboard.press("Enter")
                    expect(page.get_by_text("Blockers", exact=False)).to_be_visible()
                    expect(page.get_by_text("choice", exact=False)).to_be_visible()
                    test = page.get_by_role("button", name="Uppercase assertion", exact=False).first
                    self._tab_to(page, test)
                    page.keyboard.press("Enter")
                    expect(page.get_by_text("Test source", exact=False)).to_be_visible()
                    expect(page.get_by_text("test_app.py", exact=False)).to_be_visible()
                    expect(page.get_by_text("assertEqual", exact=False)).to_be_visible()
                    debug = page.get_by_role("button", name="Technical details and identifiers")
                    expect(debug).to_have_attribute("aria-expanded", "false")
                    status = page.get_by_text("No recorded execution is attached to this selected test.", exact=False)
                    if status.count():
                        self.assertGreaterEqual(self._contrast(page, status.first), 4.5,
                                                "written execution state meets normal-text contrast")

                decision = page.get_by_role("button", name="Decision", exact=False).first
                self._tab_to(page, decision)
                page.keyboard.press("Enter")
                expect(page.get_by_role("button", name="Resolve decision")).to_be_visible()
                option = page.get_by_role("combobox", name="Option")
                expect(option).to_be_visible()
                self._tab_to(page, option)
                page.keyboard.press("ArrowDown")
                page.keyboard.press("Enter")
                page.get_by_label("Actor").fill("Keyboard developer")
                page.get_by_label("Rationale").fill("Accessible option labels persist")
                submit = page.get_by_role("button", name="Resolve decision")
                self._tab_to(page, submit)
                page.keyboard.press("Enter")
                expect(page.get_by_text("resolved", exact=False)).to_be_visible()
                resolved = load_published(root, "w")
                choice = next(node for node in resolved.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["history"][-1]["actor"], "Keyboard developer")
                self.assertEqual(choice["history"][-1]["rationale"], "Accessible option labels persist")
                page.set_viewport_size({"width": 390, "height": 844})
                self.assertLessEqual(page.locator("body").evaluate("el => el.scrollWidth"), 390,
                                     "narrow layout has no horizontal page overflow")
                fresh = browser.new_context().new_page()
                fresh.goto(url, wait_until="domcontentloaded")
                self._open(fresh, "Decision")
                expect(fresh.get_by_text("Keyboard developer", exact=False)).to_be_visible()
                expect(fresh.get_by_text("Accessible option labels persist", exact=False)).to_be_visible()
                self._open(fresh, "Build")
                expect(fresh.get_by_text("No blockers are recorded.", exact=False)).to_be_visible()
                expect(fresh.get_by_text("Blockers", exact=False)).to_be_visible()
                browser.close()
        finally:
            server.terminate()
            server.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
