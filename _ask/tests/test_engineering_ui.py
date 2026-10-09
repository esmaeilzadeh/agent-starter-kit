"""Native workbench journeys through Streamlit's public AppTest interface."""
import os
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from engineering_fixture import workbench_model, evidence_workbench, write_json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
from engineering_model.admission import validate_current, load_published
from engineering_model.actions import edit
from engineering_model import projection as projection_module


def text(app):
    visible = [str(element.value) for kind in ("title", "header", "subheader", "markdown", "caption",
                                               "info", "warning", "error", "success")
               for element in getattr(app, kind)]
    visible.extend(element.value.to_string(index=False)
                   for collection in (app.dataframe, app.table) for element in collection)
    return "\n".join(visible)


class UiIntegrationTests(unittest.TestCase):
    def test_historical_evidence_candidate_is_inspectable_without_being_current(self):
        consumer, historical_sha = evidence_workbench()
        self.addCleanup(consumer.close)
        current_sha = consumer.git("rev-parse", "HEAD")
        with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(consumer.root)}):
            app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertEqual(len(app.json), 0)
            app.segmented_control(key="workbench_section").select("Evidence").run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("unavailable evidence", text(app))
            self.assertIn(current_sha, text(app))
            self.assertEqual(len(app.json), 0)
            app.segmented_control(key="workbench_section").select("Objects").run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("Engineering objects", text(app))
            app.segmented_control(key="workbench_section").select("Scenarios").run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("Scenarios and planned tests", text(app))
            self.assertIn("Uppercase assertion", text(app))
            self.assertIn("Planned assertions for C1", text(app))
            app.segmented_control(key="workbench_section").select("Evidence").run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            evidence_key = next(item.key for item in app.dataframe
                                if item.key and item.key.startswith("table:Evidence:"))
            app.text_input(key="candidate_sha").input(current_sha)
            app.button(key="inspect_candidate").click().run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("unavailable evidence", text(app))
            self.assertIn(current_sha, text(app))
            current_key = next(item.key for item in app.dataframe
                               if item.key and item.key.startswith("table:Evidence:"))
            app.text_input(key="candidate_sha").input(historical_sha)
            app.button(key="inspect_candidate").click().run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("(historical)", text(app))
            self.assertIn(historical_sha, text(app))
            self.assertEqual(len(app.json), 0)
            historical_key = next(item.key for item in app.dataframe
                                  if item.key and item.key.startswith("table:Evidence:"))
            self.assertNotEqual(evidence_key, historical_key)
            self.assertNotEqual(current_key, historical_key)

    def test_empty_task_and_scenario_tables_show_clear_states(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, _spec = workbench_model(root)
            removed = {"build", "scenario", "case"}
            model["nodes"] = [node for node in model["nodes"] if node["id"] not in removed]
            model["edges"] = [edge for edge in model["edges"]
                               if edge["source"] not in removed and edge["target"] not in removed]
            write_json(root, "work/pilot/engineering-model.json", model)
            _snapshot, diagnostics = validate_current(root, "pilot")
            self.assertEqual(diagnostics, [], diagnostics)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("No tasks in this snapshot.", text(app))
                app.segmented_control(key="workbench_section").select("Scenarios").run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("No canonical scenarios are linked in this snapshot.", text(app))

    def test_resolution_survives_new_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            _snapshot, diagnostics = validate_current(root, "pilot")
            self.assertEqual(diagnostics, [], diagnostics)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build Build blocked", text(app))
                app.segmented_control(key="workbench_section").select("Objects").run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                app.selectbox(key="option_id").select("one")
                app.text_input(key="actor").input("Developer")
                app.text_area(key="rationale").input("Measured fit for the pilot")
                app.button(key="resolve").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("resolved", text(app))
                self.assertIn("Developer", text(app))
                self.assertIn("Measured fit for the pilot", text(app))
                reloaded = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(reloaded.exception, reloaded.exception)
                self.assertIn("ready", text(reloaded))
                reloaded.segmented_control(key="workbench_section").select("Objects").run(timeout=15)
                self.assertIn("Measured fit for the pilot", text(reloaded))
                self.assertIn("resolved", text(reloaded))

    def test_gitless_model_root_keeps_workbench_usable_without_git_fatal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build Build blocked", text(app))
                self.assertEqual(len(app.json), 0)
                with patch.object(projection_module, "inspect_evidence",
                                  side_effect=AssertionError("overview must defer evidence scans")):
                    initial = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                    self.assertFalse(initial.exception, initial.exception)
                app.segmented_control(key="workbench_section").select("Evidence").run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                rendered = text(app) + "\n" + "\n".join(str(item.value) for item in app.json)
                self.assertIn("Git evidence inspection is unavailable", rendered)
                self.assertNotIn("fatal: not a git repository", rendered)

    def test_referenced_spec_change_keeps_form_stale_until_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _model, spec = workbench_model(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build Build blocked", text(app))
                app.segmented_control(key="workbench_section").select("Objects").run(timeout=15)
                self.assertFalse(app.exception, app.exception)

                before, diagnostics = validate_current(root, "pilot")
                self.assertEqual(diagnostics, [], diagnostics)
                spec["criteria"][0]["then"] = ["Reject invalid input"]
                plan_path = root / "work/pilot/test-plan.json"
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                plan["spec_digest"] = hashlib.sha256(
                    json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest()
                external = edit(root, "pilot", before.identity["digest"], {
                    "commands": [{"op": "revise_node", "id": "purpose",
                                  "changes": {"title": "Concurrent spec amendment"}}],
                    "files": {"specs/current/pilot.json": json.dumps(spec),
                              "work/pilot/test-plan.json": json.dumps(plan)},
                })
                self.assertTrue(external["valid"], external)
                published = load_published(root, "pilot")
                app.selectbox(key="option_id").select("one")
                app.text_input(key="actor").input("Developer")
                app.text_area(key="rationale").input("Use the amended requirement")
                app.button(key="resolve").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("did not succeed", text(app))
                self.assertEqual(load_published(root, "pilot").identity, published.identity)
                choice = next(node for node in published.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["lifecycle"], "open")

                app.button(key="refresh").click().run(timeout=15)
                app.segmented_control(key="workbench_section").select("Objects").run(timeout=15)
                app.selectbox(key="option_id").select("one")
                app.text_input(key="actor").input("Developer")
                app.text_area(key="rationale").input("Use the amended requirement")
                app.button(key="resolve").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("resolved", text(app))
                reloaded = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(reloaded.exception, reloaded.exception)
                self.assertIn("ready", text(reloaded))
