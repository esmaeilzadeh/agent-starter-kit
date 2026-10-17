"""Overview and scenario journeys through the actual workbench entry point."""
from __future__ import annotations

import os
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "_ask/ui"
TESTS = ROOT / "_ask/tests"
sys.path[:0] = [str(UI), str(TESTS), str(ROOT / "_ask/scripts")]
from engineering_fixture import workbench_model


def _text(app) -> str:
    collections = (app.title, app.header, app.subheader, app.markdown, app.caption,
                   app.info, app.warning, app.error, app.success, app.text)
    return "\n".join(str(item.value) for group in collections for item in group) + "\n" + \
        "\n".join(str(item.label) for item in app.button) + "\n" + \
        "\n".join(f"{item.label} {item.value}" for item in app.metric)


def _app(root: Path):
    return AppTest.from_file(str(UI / "streamlit_app.py")).run(timeout=30)


def _fixture(root: Path, *, mixed_story: bool = False, no_blocked: bool = False) -> None:
    model, _ = workbench_model(root)
    purpose = next(node for node in model["nodes"] if node["id"] == "purpose")
    purpose["description"] = "Make delivery decisions and proof easy to inspect."
    if no_blocked:
        model["edges"] = [edge for edge in model["edges"]
                          if not (edge.get("type") == "depends_on" and edge.get("source") == "build")]
    if mixed_story:
        spec_path = root / "specs/current/pilot.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        spec["criteria"].append({"id": "P-002", "given": "A second input", "when": "Validate",
                                 "then": ["Accept the second case"], "verification_mode": "tests"})
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        plan_path = root / "work/pilot/test-plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["spec_digest"] = hashlib.sha256(
            json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        plan["obligations"].append({"criterion_id": "P-002", "required_types": ["unit"]})
        plan["task_scopes"][0]["test_ids"].append("CASE-2")
        plan["tests"].append({
            "id": "CASE-2", "criterion_ids": ["P-002"], "type": "unit", "change_kind": "new",
            "runner_id": "fixture", "case_id": "test_fixture.Cases.test_second_behavior",
            "source_paths": ["test_fixture.py"],
            "scenario": {"given": "A second input", "when": "Validate", "then": ["Accept"]},
            "expected_assertions": [{"criterion_id": "P-002", "checks": ["Accept second input"]}],
        })
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        model["nodes"].extend([
            {"id": "epic", "type": "feature", "title": "Pilot epic", "lifecycle": "active"},
            {"id": "story", "type": "story", "title": "Recorded delivery story", "lifecycle": "active"},
            {"id": "scenario-2", "type": "scenario", "title": "Second behavior", "lifecycle": "active",
             "reference": {"path": "specs/current/pilot.json", "id": "P-002"}},
            {"id": "case-2", "type": "test", "title": "Second assertion", "lifecycle": "active",
             "reference": {"path": "work/pilot/test-plan.json", "id": "CASE-2"}},
        ])
        model["edges"] = [edge for edge in model["edges"]
                          if not (edge.get("type") == "contains" and edge.get("target") == "scenario")]
        model["edges"].extend([
            {"type": "contains", "source": "purpose", "target": "epic"},
            {"type": "contains", "source": "epic", "target": "story"},
            {"type": "contains", "source": "story", "target": "scenario"},
            {"type": "contains", "source": "epic", "target": "scenario-2"},
            {"type": "covers", "source": "case-2", "target": "scenario-2"},
        ])
    # The accepted pilot has a scenario but no story node, and one task has no
    # explicit task-to-scenario implementation edge. Preserve those absences.
    (root / "work/pilot/engineering-model.json").write_text(
        __import__("json").dumps(model), encoding="utf-8")


class WorkbenchTests(unittest.TestCase):
    def test_overview_is_comprehensive_and_lazy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _fixture(root)
            source_reads = []
            original_read_text = Path.read_text

            def count_source_reads(path, *args, **kwargs):
                if path.resolve() == (root / "test_fixture.py").resolve():
                    source_reads.append(path)
                return original_read_text(path, *args, **kwargs)

            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}), \
                    patch("engineering_model.projection.inspect_evidence",
                          side_effect=AssertionError("overview must not inspect evidence")), \
                    patch.object(Path, "read_text", count_source_reads):
                app = _app(root)
                self.assertFalse(app.exception, app.exception)
                rendered = _text(app)
                for phrase in ("Make delivery decisions and proof easy to inspect.",
                               "No story records are present", "Scenarios without a recorded story",
                               "Canonical behavior", "Dependency readiness", "Blocked tasks", "Open decisions",
                               "Not loaded", "Choose"):
                    self.assertIn(phrase, rendered)
                self.assertNotIn("Exact accepted behavior", rendered)
                self.assertEqual(source_reads, [], "opening the epic must not read test source")
                self.assertFalse(app.tabs)

                # Navigate the actual hierarchy and inspect canonical details.
                app.button(key="route:scenario").click().run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                scenario_text = _text(app)
                for phrase in ("Valid input", "Validate", "Accept", "Behavior assertion", "Build"):
                    self.assertIn(phrase, scenario_text)
                route_controls = {item.key for item in app.button}
                self.assertIn("scenario:scenario:task:build", route_controls)
                self.assertIn("scenario:scenario:test:CASE-1", route_controls)
                self.assertEqual(source_reads, [], "scenario details must not eagerly read test source")

            # Mixed story membership must preserve the directly recorded
            # epic-to-scenario path. One task owns tests for both scenarios.
            with tempfile.TemporaryDirectory() as mixed_directory:
                mixed_root = Path(mixed_directory)
                _fixture(mixed_root, mixed_story=True)
                with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(mixed_root)}):
                    mixed_app = _app(mixed_root)
                    self.assertFalse(mixed_app.exception, mixed_app.exception)
                    self.assertIn("Scenarios without a recorded story", _text(mixed_app))
                    self.assertIn("Second behavior", _text(mixed_app))
                    overview_links = {item.key for item in mixed_app.button}
                    defects = []
                    if "overview:scenario:scenario" not in overview_links:
                        defects.append("story-linked scenario missing from overview")
                    if "overview:scenario:scenario-2" not in overview_links:
                        defects.append("unassigned scenario missing from overview summary")
                    mixed_app.button(key="route:scenario-2").click().run(timeout=30)
                    self.assertFalse(mixed_app.exception, mixed_app.exception)
                    mixed_app.button(key="scenario:scenario-2:task:build").click().run(timeout=30)
                    self.assertFalse(mixed_app.exception, mixed_app.exception)
                    if mixed_app.session_state["_engineering_route"] != "build@scenario-2":
                        defects.append("shared task navigation selected the wrong scenario alias")
                    if "Second behavior" not in _text(mixed_app):
                        defects.append("shared task breadcrumb lost the selected scenario context")
                    back = mixed_app.button(key="route:back")
                    if back.disabled:
                        defects.append("shared task navigation discarded Back history")
                    else:
                        mixed_app.button(key="route:back").click().run(timeout=30)
                        if mixed_app.session_state["_engineering_route"] != "scenario-2":
                            defects.append("Back did not restore scenario-2")
                    self.assertEqual(defects, [], "; ".join(defects))

    def test_summary_counts_open_exact_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _fixture(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = _app(root)
                self.assertFalse(app.exception, app.exception)
                self.assertTrue(app.button(key="route:back").disabled,
                                "Back is disabled at the initial epic route")
                controls = {item.key: item for item in app.button}
                self.assertIn("overview:summary:blocked", controls,
                              "blocked-task summary must open its stable-ID filtered records")
                controls["overview:summary:blocked"].click().run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(app.session_state["_engineering_overview_filter"],
                                 {"kind": "blocked", "ids": ["build"], "work_id": "pilot"})
                self.assertIn("Build", _text(app))
                self.assertIn("Blocked", _text(app))

                controls = {item.key: item for item in app.button}
                self.assertIn("overview:filter:clear", controls)
                controls["overview:filter:clear"].click().run(timeout=30)
                controls = {item.key: item for item in app.button}
                self.assertIn("overview:summary:decisions", controls)
                controls["overview:summary:decisions"].click().run(timeout=30)
                self.assertEqual(app.session_state["_engineering_overview_filter"],
                                 {"kind": "decisions", "ids": ["choice"], "work_id": "pilot"})
                self.assertIn("Choose", _text(app))
                self.assertIn("Not loaded", _text(app))
                self.assertNotIn("0 failed", _text(app).lower())

                controls = {item.key: item for item in app.button}
                controls["overview:filter:clear"].click().run(timeout=30)
                app.button(key="overview:summary:blocked").click().run(timeout=30)
                self.assertIn("overview:filter:open:blocked:build", {item.key for item in app.button})
                app.button(key="overview:filter:open:blocked:build").click().run(timeout=30)
                self.assertEqual(app.session_state["_engineering_route"], "build")
                self.assertIn("Task status", _text(app))
                defects = []
                expected_filter = {"kind": "blocked", "ids": ["build"], "work_id": "pilot"}
                if app.session_state["_engineering_overview_filter"] != expected_filter:
                    defects.append("opening a filtered record discarded its exact filter state")
                app.button(key="route:back").click().run(timeout=30)
                if app.session_state["_engineering_route"] != "purpose":
                    defects.append("Back did not restore the epic route")
                if app.session_state["_engineering_overview_filter"] != expected_filter:
                    defects.append("Back did not restore the exact stable-ID filter")
                if "overview:filter:open:blocked:build" not in {item.key for item in app.button}:
                    defects.append("restored overview did not show the filtered task")
                self.assertEqual(defects, [], "; ".join(defects))

            with tempfile.TemporaryDirectory() as empty_directory:
                empty_root = Path(empty_directory)
                _fixture(empty_root, no_blocked=True)
                with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(empty_root)}):
                    empty_app = _app(empty_root)
                    self.assertFalse(empty_app.exception, empty_app.exception)
                    self.assertTrue(empty_app.button(key="route:back").disabled)
                    empty_app.button(key="overview:summary:blocked").click().run(timeout=30)
                    empty_filter = {"kind": "blocked", "ids": [], "work_id": "pilot"}
                    self.assertEqual(empty_app.session_state["_engineering_overview_filter"], empty_filter)
                    self.assertIn("No records match this summary", _text(empty_app))
                    empty_app.button(key="route:scenario").click().run(timeout=30)
                    self.assertFalse(empty_app.exception, empty_app.exception)
                    empty_app.button(key="route:back").click().run(timeout=30)
                    self.assertEqual(empty_app.session_state["_engineering_route"], "purpose")
                    self.assertEqual(empty_app.session_state["_engineering_overview_filter"], empty_filter)
                    self.assertIn("No records match this summary", _text(empty_app))


if __name__ == "__main__":
    unittest.main()
