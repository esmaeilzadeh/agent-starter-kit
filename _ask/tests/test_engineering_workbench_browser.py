"""Browser journeys through the semantic workbench hierarchy."""
from __future__ import annotations

import os
import copy
import hashlib
import json
from pathlib import Path
import re
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
from engineering_model.admission import admit, load_published
from engineering_model.projection import project


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
    def _key_class(key):
        # Streamlit 1.59 normalizes widget-key punctuation in its wrapper class.
        return "st-key-" + re.sub(r"[^A-Za-z0-9_-]", "-", key)

    @staticmethod
    def _open(page, route):
        routes = {"Purpose": "purpose", "Render uppercase text": "story",
                  "Uppercase behavior": "scenario", "Uppercase assertion": "test:U",
                  "scenario": "scenario", "test:U": "test:U", "result:U": "result:U",
                  "Build": "build", "Review build": "review-build", "Decision": "decision"}
        route_id = routes.get(route, route)
        wrapper = page.locator(f'[class~="{WorkbenchTests._key_class(f"route:{route_id}")}"]')
        button = wrapper.get_by_role("button")
        expect(button).to_be_visible(timeout=5000)
        button.click()

    @staticmethod
    def _assert_filter_ids(page, kind, expected, metric_label, metric_count):
        prefix = WorkbenchTests._key_class(f"overview:filter:open:{kind}:")
        row_wrappers = page.locator(f"[class*='st-key-overview-filter-open-{kind}-']")
        expect(row_wrappers).to_have_count(len(expected))
        actual = page.locator("[class*='st-key-overview-filter-open-']").evaluate_all(
            "(els, prefix) => [...new Set(els.flatMap(el => [...el.classList]"
            ".filter(name => name.startsWith(prefix)).map(name => name.slice(prefix.length))))]",
            prefix)
        assert set(actual) == set(expected), f"{kind} summary opened {actual}, expected {sorted(expected)}"
        expect(page.get_by_role("button", name="Clear filter", exact=True)).to_be_visible()
        metric = page.locator("[data-testid='stMetric']").filter(
            has=page.get_by_text(metric_label, exact=True))
        expect(metric).to_have_count(1)
        assert metric.inner_text().splitlines()[-1].strip() == str(metric_count), (
            f"{metric_label} metric must match its opened records")
        for identity in expected:
            expect(page.locator(f'[class~="{WorkbenchTests._key_class(f"overview:filter:open:{kind}:{identity}")}"]')
                   .get_by_role("button", name="Open record", exact=True)).to_be_visible()
        expect(page.get_by_role("button", name="Open record", exact=True)).to_have_count(len(expected))

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
    def _assert_focus(page, target, label):
        measurement = target.evaluate("""el => {
          const parse = value => { const values=value.match(/[\\d.]+/g)||[0,0,0,1];
            return [Number(values[0]),Number(values[1]),Number(values[2]),values.length>3?Number(values[3]):1]; };
          const blend = (front, back) => front.slice(0,3).map((v,i)=>v*front[3]+back[i]*(1-front[3]));
          const chain = element => { const values=[]; for(let n=element;n;n=n.parentElement) values.unshift(n); return values; };
          const background = element => { let value=[255,255,255]; for(const n of chain(element)) {
            const color=parse(getComputedStyle(n).backgroundColor); if(color[3]>0) value=blend(color,value); } return value; };
          const style=getComputedStyle(el);
          const outline=parseFloat(style.outlineWidth)>0 && style.outlineStyle!=='none';
          const shadow=style.boxShadow.match(/rgba?\\([^)]*\\)/g)||[];
          const indicator=outline ? parse(style.outlineColor) : shadow.map(parse).find(color=>color[3]>0);
          if(!indicator) return {visible:false};
          const luminance=color=>color.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;})
            .reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
          const ratio=(a,b)=>(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
          const inside=background(el);
          const outside=background(el.parentElement?.parentElement||el.parentElement||el);
          const colorInside=blend(indicator,inside), colorOutside=blend(indicator,outside);
          return {visible:true, contrast:Math.min(ratio(luminance(colorInside),luminance(inside)),
            ratio(luminance(colorOutside),luminance(outside)))};
        }""")
        assert measurement["visible"], f"{label} exposes a visible keyboard focus indicator"
        assert measurement["contrast"] >= 3, (
            f"{label} focus indicator contrasts at least 3:1 with both adjacent backgrounds; "
            f"got {measurement['contrast']:.3f}:1")

    @staticmethod
    def _select(page, label, value):
        control = page.get_by_label(label)
        expect(control).to_be_visible()
        control.click()
        page.get_by_role("option", name=value, exact=True).click()

    @staticmethod
    def _recorded_hierarchy(consumer):
        """Create explicit story/task records and two immutable work branches."""
        def task_graph_yaml(document):
            rows = []
            for task in document["tasks"]:
                dependencies = ", ".join(task.get("depends_on", []))
                paths = ", ".join(task.get("owned_paths", []))
                rows.extend((f"  - id: {task['id']}", f"    title: {task['title']}",
                             f"    outcome: {task['outcome']}",
                             f"    depends_on: [{dependencies}]", f"    owned_paths: [{paths}]"))
            return (f"schema: {document['schema']}\nwork_id: {document['work_id']}\ntasks:\n"
                    + "\n".join(rows) + "\n")

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
        consumer.write("work/w/inner-loop/tasks.yaml", task_graph_yaml(graph))
        consumer.write("work/w/inner-loop/state.json", {
            "schema": "ask-inner-loop-state/v1", "work_id": "w", "revision": 1,
            "tasks": {
                "build": {"status": "integrated", "result_path": "work/w/inner-loop/results/build.json"},
                "review-build": {"status": "pending", "result_path": ""},
            },
        })
        consumer.write("work/w/inner-loop/results/build.json", {
            "schema": "ask-task-result/v2", "work_id": "w", "task_id": "build",
            "candidate_sha": consumer.sha, "result": "passed",
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
        consumer.write("work/w-alt/inner-loop/tasks.yaml", task_graph_yaml(alt_graph))
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
        admitted, diagnostics = admit(root, "w")
        self.assertEqual(diagnostics, [], diagnostics)
        self.assertIsNotNone(admitted)
        projection = project(admitted, root, include_evidence=False)
        tests_by_id = {item["id"]: item for item in projection["workbench"]["tests"]}
        self.assertEqual(len([item for item in projection["workbench"]["tests"]
                              if item["id"] == "U"]), 1)
        self.assertEqual(tests_by_id["U"]["owner_task_id"], "build")
        self.assertEqual(tests_by_id["U"]["ownership_status"], "owned")
        self.assertEqual(tests_by_id["U"]["related_tasks"],
                         [{"task_id": "review-build", "via": "scenario-coverage"}])
        before_head = consumer.git("rev-parse", "HEAD")
        before_refs = consumer.git("for-each-ref", "--format=%(refname) %(objectname)")
        definition_paths = [root / path for path in (
            "work/w/engineering-model.json", "work/w/test-plan.json",
            "work/w/inner-loop/tasks.yaml", "work/w/inner-loop/state.json",
            "work/w/inner-loop/results/build.json", "specs/current/w.json", "specs/current/w.md",
            "work/w-alt/engineering-model.json", "work/w-alt/test-plan.json",
            "work/w-alt/inner-loop/tasks.yaml", "work/w-alt/inner-loop/state.json",
            "specs/current/w-alt.json", "specs/current/w-alt.md", "test_app.py")]
        before_definitions = {path: path.read_bytes() for path in definition_paths}
        state_dir = root / "work/w/traceability/model-state"
        pointer_path = state_dir / "current.json"
        pointer_before = pointer_path.read_bytes()
        generation_id = json.loads(pointer_before)["generation"]
        generation_manifest = state_dir / "generations" / generation_id / "manifest.json"
        generation_before = generation_manifest.read_bytes()
        before_publication = load_published(root, "w").identity
        server, url = self._server(root)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    headless=True,
                    **({"channel": os.environ["ASK_BROWSER_CHANNEL"]}
                       if os.environ.get("ASK_BROWSER_CHANNEL") else {}),
                    args=["--no-sandbox"])
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")
                expect(page.get_by_text("Workstream: w", exact=False)).to_be_visible()
                expect(page.get_by_role("button", name="Uppercase behavior", exact=False)).to_be_visible()
                expect(page.get_by_role("button", name="Render uppercase text", exact=False)).to_be_visible()

                # Every summary opens the exact records represented by its count.
                page.get_by_role("button", name="View scenarios", exact=True).click()
                self._assert_filter_ids(page, "scenarios", {"scenario", "scenario-other"}, "Scenarios", 2)
                expect(page.get_by_role("heading", name="Scenarios", exact=True)).to_be_visible()
                self._open(page, "Purpose")
                page.get_by_role("button", name="View tasks", exact=True).click()
                self._assert_filter_ids(page, "tasks", {"build", "review-build"}, "Tasks", 2)
                expect(page.get_by_role("heading", name="Tasks", exact=True)).to_be_visible()
                self._open(page, "Purpose")
                page.get_by_role("button", name="View blocked tasks", exact=True).click()
                self._assert_filter_ids(page, "blocked", {"review-build"}, "Blocked tasks", 1)
                self._open(page, "Purpose")
                page.get_by_role("button", name="View open decisions", exact=True).click()
                self._assert_filter_ids(page, "decisions", {"choice"}, "Open decisions", 1)

                self._open(page, "Render uppercase text")
                expect(page.get_by_role("heading", name="Render uppercase text")).to_be_visible()
                self._open(page, "Uppercase behavior")
                expect(page.get_by_role("heading", name="Uppercase behavior")).to_be_visible()
                expect(page.get_by_text("lowercase text", exact=True)).to_be_visible()
                expect(page.get_by_text("rendered through domain or CLI", exact=True)).to_be_visible()
                expect(page.get_by_text("uppercase text is returned", exact=True)).to_be_visible()
                self._open(page, "Build")
                expect(page.get_by_role("heading", name="Build")).to_be_visible()
                expect(page.get_by_text("Render the promised uppercase output", exact=False)).to_be_visible()
                expect(page.get_by_text("Recorded result: work/w/inner-loop/results/build.json", exact=True)).to_be_visible()
                self.assertEqual(json.loads((root / "work/w/inner-loop/results/build.json").read_text())[
                    "candidate_sha"], historical_sha)
                expect(page.get_by_text("U", exact=True)).to_be_visible()
                self._open(page, "Review build")
                expect(page.get_by_role("heading", name="Review build")).to_be_visible()
                expect(page.get_by_role("button", name="E", exact=True)).to_be_visible()
                self._open(page, "Uppercase assertion")
                expect(page.get_by_text("Selected source path: test_app.py", exact=True)).to_be_visible()
                expect(page.get_by_text("test_app.Cases.test_unit", exact=False)).to_be_visible()
                self._open(page, "scenario")
                expect(page.get_by_role("heading", name="Uppercase behavior")).to_be_visible()
                self._open(page, "test:U")
                expect(page.get_by_text("test_app.py", exact=False)).to_be_visible()
                self._open(page, "result:E")
                expect(page.get_by_text("Selected test: E · revision-bound planned identity", exact=True)).to_be_visible()
                expect(page.get_by_text("Historical contract evidence", exact=True)).to_be_visible()
                page.get_by_label("Historical contract candidate").select_option(historical_sha)
                page.get_by_role("button", name="Inspect candidate", exact=True).click()
                expect(page.get_by_text("Recorded historical outcome: Passed", exact=True).first).to_be_visible()
                expect(page.get_by_text("They do not verify the current contract.", exact=True)).to_be_visible()
                self._open(page, "result:U")
                expect(page.get_by_text("Selected test: U · revision-bound planned identity", exact=True)).to_be_visible()
                expect(page.get_by_text("No retained execution matches the current test contract.", exact=True)).to_be_visible()
                expect(page.get_by_text("Historical contract evidence", exact=True)).to_be_visible()
                page.get_by_label("Historical contract candidate").select_option(historical_sha)
                page.get_by_role("button", name="Inspect candidate", exact=True).click()
                expect(page.get_by_text("Recorded historical outcome: Passed", exact=True).first).to_be_visible()
                self.assertGreater(page.get_by_text(historical_sha, exact=True).count(), 0,
                                   "historical contract inspection identifies its retained candidate")

                # The selected alternate work is read from its other branch and remains read-only.
                self._select(page, "Workstream", "w-alt")
                expect(page.get_by_text("Workstream: w-alt", exact=False)).to_be_visible()
                expect(page.get_by_text("Committed · agent/w-alt", exact=False)).to_be_visible()
                self._open(page, "Uppercase assertion")
                expect(page.get_by_text("Selected test: U · revision-bound planned identity", exact=True)).to_be_visible()
                expect(page.get_by_text("Source revision unique to agent/w-alt", exact=False)).to_be_visible()
                expect(page.get_by_text("test_app.py", exact=False)).to_be_visible()
                self._open(page, "result:U")
                expect(page.get_by_text("Selected test: U · revision-bound planned identity", exact=True)).to_be_visible()
                expect(page.get_by_text("No recorded execution is attached to this selected test.", exact=True)).to_be_visible()
                self._open(page, "Decision")
                expect(page.get_by_text("This source is read-only", exact=False)).to_be_visible()
                self.assertEqual(page.get_by_role("button", name="Resolve decision").count(), 0)

                self.assertEqual(consumer.git("rev-parse", "HEAD"), before_head)
                self.assertEqual(consumer.git("for-each-ref", "--format=%(refname) %(objectname)"), before_refs)
                self.assertEqual({path: path.read_bytes() for path in definition_paths}, before_definitions)
                self.assertEqual(load_published(root, "w").identity, before_publication)
                self.assertEqual(pointer_path.read_bytes(), pointer_before)
                self.assertEqual(json.loads(pointer_path.read_bytes())["generation"], generation_id)
                self.assertEqual(generation_manifest.read_bytes(), generation_before)
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
                browser = pw.chromium.launch(
                    headless=True,
                    **({"channel": os.environ["ASK_BROWSER_CHANNEL"]}
                       if os.environ.get("ASK_BROWSER_CHANNEL") else {}),
                    args=["--no-sandbox"])
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(url, wait_until="domcontentloaded")
                expect(page.get_by_role("heading", name="Engineering workbench", exact=True)).to_be_visible(timeout=15000)
                for width in (390, 1440):
                    page.set_viewport_size({"width": width, "height": 844})
                    route = page.get_by_role("button", name="Uppercase behavior", exact=False).first
                    expect(route).to_be_visible(timeout=15000)
                    self._tab_to(page, route)
                    self._assert_focus(page, route, "scenario route")
                    self.assertGreaterEqual(self._contrast(page, route), 4.5,
                                            "normal-size route label meets text contrast")
                    large_text = page.get_by_role("heading", name="Engineering workbench")
                    self.assertGreaterEqual(self._contrast(page, large_text), 3,
                                            "large title text meets 3:1 contrast")
                    page.keyboard.press("Enter")
                    expect(page.get_by_role("heading", name="Uppercase behavior")).to_be_visible()
                    task = page.get_by_role("button", name="Build", exact=False).first
                    self._tab_to(page, task)
                    self._assert_focus(page, task, "task route")
                    page.keyboard.press("Enter")
                    expect(page.get_by_text("Blockers", exact=False)).to_be_visible()
                    expect(page.get_by_text("choice", exact=False)).to_be_visible()
                    test = page.get_by_role("button", name="Uppercase assertion", exact=False).first
                    self._tab_to(page, test)
                    self._assert_focus(page, test, "test route")
                    page.keyboard.press("Enter")
                    expect(page.get_by_role("heading", name="Test source", exact=True)).to_be_visible()
                    expect(page.get_by_text("Selected source path: test_app.py", exact=True)).to_be_visible()
                    expect(page.get_by_text("test_app.Cases.test_unit", exact=True)).to_be_visible()
                    debug = page.locator("summary").filter(has_text="Technical details and identifiers")
                    expect(debug).to_be_visible()
                    if debug.evaluate("el => el.parentElement.open"):
                        self._tab_to(page, debug)
                        page.keyboard.press("Enter")
                        self.assertFalse(debug.evaluate("el => el.parentElement.open"))
                    self._tab_to(page, debug)
                    self._assert_focus(page, debug, "debug expander")
                    page.keyboard.press("Enter")
                    self.assertTrue(debug.evaluate("el => el.parentElement.open"),
                                    "keyboard opens debug details at each viewport")
                    expect(page.get_by_text("Snapshot digest", exact=True)).to_be_visible()
                    expect(page.get_by_text("Git revision", exact=True)).to_be_visible()
                    expect(page.get_by_text("Selected source: test_app.py", exact=False)).to_be_visible()
                    status = page.get_by_text(
                        "No current recorded execution is attached to this selected revision.", exact=True)
                    expect(status).to_be_visible()
                    self.assertGreaterEqual(self._contrast(page, status.first), 4.5,
                                            "written execution state meets normal-text contrast")
                    self.assertLessEqual(page.locator("body").evaluate("el => el.scrollWidth"), width,
                                         f"page has no horizontal overflow at {width}px")

                page.set_viewport_size({"width": 390, "height": 844})
                decision = page.get_by_role("button", name="Decision", exact=False).first
                self._tab_to(page, decision)
                self._assert_focus(page, decision, "decision route")
                page.keyboard.press("Enter")
                expect(page.get_by_role("button", name="Resolve decision")).to_be_visible()
                option = page.get_by_role("combobox", name="Option")
                self._tab_to(page, option)
                page.keyboard.press("ArrowDown")
                page.keyboard.press("Enter")
                actor = page.get_by_label("Actor")
                self._tab_to(page, actor)
                page.keyboard.type("Keyboard developer")
                rationale = page.get_by_label("Rationale")
                self._tab_to(page, rationale)
                page.keyboard.type("Accessible option labels persist")
                submit = page.get_by_role("button", name="Resolve decision")
                self._tab_to(page, submit)
                page.keyboard.press("Enter")
                expect(page.get_by_role("heading", name="Purpose", exact=True)).to_be_visible()
                expect(page.get_by_role("button", name="Resolve decision")).to_have_count(0)

                resolved = load_published(root, "w")
                choice = next(node for node in resolved.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["resolution"]["option_id"], "two")
                self.assertEqual(choice["resolution"]["actor"], "Keyboard developer")
                self.assertEqual(choice["resolution"]["rationale"], "Accessible option labels persist")
                self._open(page, "resolved-decision:choice")
                expect(page.get_by_role("heading", name="Resolved decision", exact=True)).to_be_visible()
                expect(page.get_by_text("Resolved option: two", exact=True)).to_be_visible()
                page.set_viewport_size({"width": 390, "height": 844})
                self.assertLessEqual(page.locator("body").evaluate("el => el.scrollWidth"), 390,
                                     "narrow layout has no horizontal page overflow")
                fresh = browser.new_context().new_page()
                fresh.goto(url, wait_until="domcontentloaded")
                self._open(fresh, "resolved-decision:choice")
                expect(fresh.get_by_role("heading", name="Resolved decision", exact=True)).to_be_visible()
                expect(fresh.get_by_text("Resolved option: two", exact=True)).to_be_visible()
                expect(fresh.get_by_text("Keyboard developer", exact=False)).to_be_visible()
                expect(fresh.get_by_text("Accessible option labels persist", exact=False)).to_be_visible()
                self._open(fresh, "Build")
                expect(fresh.get_by_text("No blockers are recorded.", exact=False)).to_be_visible()
                expect(fresh.get_by_text("Blockers", exact=True)).to_be_visible()
                browser.close()

            wide_consumer, _ = evidence_workbench()
            wide_server, wide_url = self._server(wide_consumer.root)
            try:
                with sync_playwright() as pw:
                    wide_browser = pw.chromium.launch(
                        headless=True,
                        **({"channel": os.environ["ASK_BROWSER_CHANNEL"]}
                           if os.environ.get("ASK_BROWSER_CHANNEL") else {}),
                        args=["--no-sandbox"])
                    wide = wide_browser.new_page(viewport={"width": 1440, "height": 900})
                    wide.goto(wide_url, wait_until="domcontentloaded")
                    decision = wide.get_by_role("button", name="Decision", exact=False).first
                    self._tab_to(wide, decision)
                    self._assert_focus(wide, decision, "wide decision route")
                    self.assertGreaterEqual(self._contrast(wide, decision), 4.5)
                    wide.keyboard.press("Enter")
                    option = wide.get_by_role("combobox", name="Option")
                    self._tab_to(wide, option)
                    self._assert_focus(wide, option, "wide decision option")
                    self.assertGreaterEqual(self._contrast(wide, option), 4.5)
                    wide.keyboard.press("ArrowDown")
                    wide.keyboard.press("Enter")
                    expect(option).to_have_value("two")
                    actor = wide.get_by_label("Actor")
                    self._tab_to(wide, actor)
                    self._assert_focus(wide, actor, "wide decision actor")
                    self.assertGreaterEqual(self._contrast(wide, actor), 4.5)
                    wide.keyboard.type("Wide keyboard developer")
                    rationale = wide.get_by_label("Rationale")
                    self._tab_to(wide, rationale)
                    self._assert_focus(wide, rationale, "wide decision rationale")
                    self.assertGreaterEqual(self._contrast(wide, rationale), 4.5)
                    wide.keyboard.type("Wide layout decision remains attributed")
                    submit = wide.get_by_role("button", name="Resolve decision")
                    self._tab_to(wide, submit)
                    self._assert_focus(wide, submit, "wide decision submit")
                    self.assertGreaterEqual(self._contrast(wide, submit), 4.5)
                    wide.keyboard.press("Enter")
                    expect(wide.get_by_role("heading", name="Purpose", exact=True)).to_be_visible()
                    resolved = load_published(wide_consumer.root, "w")
                    choice = next(node for node in resolved.document["nodes"] if node["id"] == "choice")
                    self.assertEqual(choice["resolution"]["option_id"], "two")
                    self.assertEqual(choice["resolution"]["actor"], "Wide keyboard developer")
                    self.assertEqual(choice["resolution"]["rationale"], "Wide layout decision remains attributed")
                    wide_browser.close()
            finally:
                wide_server.terminate()
                wide_server.wait(timeout=5)
                wide_consumer.close()
        finally:
            server.terminate()
            server.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
