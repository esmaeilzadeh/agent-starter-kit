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
from engineering_fixture import workbench_model, evidence_workbench

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
from engineering_model.admission import validate_current, load_published
from engineering_model.actions import edit


def text(app):
    return "\n".join(str(element.value) for kind in ("markdown", "caption", "info", "warning", "error", "success")
                     for element in getattr(app, kind))


class UiIntegrationTests(unittest.TestCase):
    def test_historical_evidence_candidate_is_inspectable_without_being_current(self):
        consumer, historical_sha = evidence_workbench()
        self.addCleanup(consumer.close)
        current_sha = consumer.git("rev-parse", "HEAD")
        with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(consumer.root)}):
            app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            app.text_input(key="candidate_sha").input(current_sha)
            app.button(key="inspect_candidate").click().run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            unavailable = json.loads(app.json[0].value)["by_workstream"]["w"]
            self.assertEqual(unavailable["status"], "unavailable", unavailable)
            self.assertFalse(unavailable["current_completion"])
            app.text_input(key="candidate_sha").input(historical_sha)
            app.button(key="inspect_candidate").click().run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            inspection = json.loads(app.json[0].value)["by_workstream"]["w"]
            self.assertEqual(inspection["status"], "historical", inspection)
            self.assertFalse(inspection["current_completion"])
            self.assertEqual(inspection["candidate_sha"], historical_sha)

    def test_resolution_survives_new_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            _snapshot, diagnostics = validate_current(root, "pilot")
            self.assertEqual(diagnostics, [], diagnostics)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build: blocked", text(app))
                app.selectbox(key="object_id").select("choice").run()
                app.selectbox(key="option_id").select("one")
                app.text_input(key="actor").input("Developer")
                app.text_area(key="rationale").input("Measured fit for the pilot")
                app.button(key="resolve").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build: ready", text(app))
                self.assertIn("Developer", text(app))
                self.assertIn("Measured fit for the pilot", text(app))
                reloaded = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(reloaded.exception, reloaded.exception)
                self.assertIn("build: ready", text(reloaded))
                reloaded.selectbox(key="object_id").select("choice").run()
                self.assertIn("Measured fit for the pilot", text(reloaded))
                self.assertIn("resolved", text(reloaded))

    def test_gitless_model_root_keeps_workbench_usable_without_git_fatal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                rendered = text(app) + "\n" + "\n".join(str(item.value) for item in app.json)
                self.assertIn("build: blocked", rendered)
                self.assertIn("Git evidence inspection is unavailable", rendered)
                self.assertNotIn("fatal: not a git repository", rendered)

    def test_referenced_spec_change_keeps_form_stale_until_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _model, spec = workbench_model(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build: blocked", text(app))

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
                self.assertNotEqual(app.selectbox(key="object_id").value, "choice")
                app.selectbox(key="object_id").select("choice").run()
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
                app.selectbox(key="object_id").select("choice").run()
                app.selectbox(key="option_id").select("one")
                app.text_input(key="actor").input("Developer")
                app.text_area(key="rationale").input("Use the amended requirement")
                app.button(key="resolve").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build: ready", text(app))
