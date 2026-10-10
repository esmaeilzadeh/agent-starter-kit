"""Native workbench journeys through Streamlit's public AppTest interface."""
import os
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import streamlit as st
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
    visible.extend(f"{element.label}: {element.value}" for element in app.metric)
    visible.extend(str(element.value) for element in app.code)
    visible.extend(str(element.label) for element in app.button)
    return "\n".join(visible)


def open_route(app, route_id, *, timeout=15):
    """Open one node in the connected Epic-to-Result outline."""
    route = next((item for item in app.button if item.key == f"route:{route_id}"), None)
    if route is None:
        raise AssertionError(f"connected hierarchy route {route_id!r} is missing")
    route.click().run(timeout=timeout)


def required_widget(elements, predicate, description):
    widget = next((item for item in elements if predicate(item)), None)
    if widget is None:
        raise AssertionError(f"required workbench control is missing: {description}")
    return widget


class UiIntegrationTests(unittest.TestCase):
    def test_historical_evidence_candidate_is_inspectable_without_being_current(self):
        consumer, historical_sha = evidence_workbench()
        self.addCleanup(consumer.close)
        current_sha = consumer.git("rev-parse", "HEAD")
        with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(consumer.root)}):
            app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertEqual(len(app.json), 0)
            open_route(app, "result:U", timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("U", text(app))
            self.assertIn("Evidence candidate", text(app))
            required_widget(app.text_input, lambda item: item.key == "candidate_sha",
                            "evidence candidate").input(current_sha)
            required_widget(app.button, lambda item: item.key == "inspect_candidate",
                            "inspect evidence candidate").click().run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("unavailable evidence", text(app))
            self.assertNotIn(current_sha, text(app))
            required_widget(app.text_input, lambda item: item.key == "candidate_sha",
                            "evidence candidate").input(historical_sha)
            required_widget(app.button, lambda item: item.key == "inspect_candidate",
                            "inspect evidence candidate").click().run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("(historical)", text(app))
            self.assertNotIn(historical_sha, text(app))
            self.assertEqual(len(app.json), 0)

    def test_planned_test_shows_its_source_in_the_detail_panel(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                open_route(app, "test:CASE-1")
                self.assertFalse(app.exception, app.exception)
                self.assertIn("test_behavior", text(app))
                self.assertIn("test_fixture.py", text(app))
                self.assertIn("self.assertEqual(actual, 'accepted')", text(app))
                self.assertIn("Planned assertions for C1", text(app))
                self.assertIn("Test source", text(app))

    def test_overview_keeps_decision_resolution_in_the_objects_section(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertIn("Build", text(app))
                app.button(key="overview:attention:decision:choice").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("Resolve decision", text(app))
                self.assertIn("Choose", text(app))

    def test_overview_shows_epic_scenarios_tasks_and_tests_without_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                rendered = text(app)
                for label in ("Epic", "Purpose", "Stories and scenarios", "Canonical behavior",
                              "Task progress", "Build", "Scenarios: 1", "Tasks: 1",
                              "Behavior assertion"):
                    self.assertIn(label, rendered)
                self.assertTrue(any(item.key == "route:test:CASE-1" for item in app.button),
                                "overview outline includes the linked planned test")
                self.assertTrue(any(item.key == "route:result:CASE-1" for item in app.button),
                                "overview outline includes the linked result route")
                self.assertNotIn("self.assertEqual(actual, 'accepted')", rendered)
                open_route(app, "test:CASE-1")
                self.assertFalse(app.exception, app.exception)
                self.assertIn("self.assertEqual(actual, 'accepted')", text(app))
                self.assertNotIn("Snapshot:", rendered)
                self.assertNotRegex(rendered, r"\b[0-9a-f]{40}\b")

    def test_overview_loads_results_on_demand_and_explains_debug_identifiers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            evidence = {
                "schema": "ask-engineering-evidence/v1", "work_id": "pilot",
                "status": "valid", "candidate_sha": "a" * 40,
                "current_sha": "a" * 40, "historical": False,
                "current_completion": True,
                "scenarios": [{
                    "criterion_id": "P-001",
                    "reference": {"path": "specs/current/pilot.json", "id": "P-001"},
                    "evidence": {"criterion_id": "P-001", "tests": [{
                        "test_id": "CASE-1", "tdd": "red_green", "red": [],
                        "final_execution": {"outcome": "passed"},
                    }]},
                }],
                "completion": {"status": "pass", "errors": [], "criterion_evidence": []},
            }
            original_expander = st.expander

            def expand_debug(*args, **kwargs):
                if str(kwargs.get("key", "")).startswith("debug-trace:"):
                    kwargs["expanded"] = True
                return original_expander(*args, **kwargs)

            with (patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}),
                  patch.object(projection_module, "inspect_evidence", return_value=evidence) as inspect,
                  patch.object(st, "expander", expand_debug)):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                inspect.assert_not_called()
                self.assertIn("Results are not loaded", text(app))
                open_route(app, "result:CASE-1")
                self.assertFalse(app.exception, app.exception)
                self.assertIn("Load test results", text(app))
                required_widget(app.button, lambda item: item.key == "test_load_results",
                                "load selected test results").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                inspect.assert_called_once()
                rendered = text(app)
                self.assertIn("Passed", rendered)
                self.assertIn("Commit SHA identifies a Git revision", rendered)
                self.assertIn("Snapshot digest fingerprints the admitted model and referenced inputs", rendered)
                self.assertIn("git show", rendered)
                self.assertIn("./ask model show", rendered)
                self.assertIn("./ask traceability check-completion", rendered)

    def test_repeated_nested_evidence_fields_do_not_duplicate_expanders(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            nested_evidence = {
                "status": "invalid", "candidate_sha": "abc", "current_sha": "abc",
                "historical": False, "current_completion": False,
                "scenarios": [
                    {"tests": [{"references": [{"id": "one"}]}]},
                    {"tests": [{"references": [{"id": "two"}]}]},
                ],
                "completion": {"errors": ["migration_required: missing review JSON for candidate"]},
            }
            original_expander = st.expander

            def expand_all(*args, **kwargs):
                kwargs["expanded"] = True
                return original_expander(*args, **kwargs)

            with (patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}),
                  patch.object(projection_module, "inspect_evidence", return_value=nested_evidence),
                  patch.object(st, "expander", expand_all)):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                open_route(app, "result:CASE-1")
                self.assertFalse(app.exception, app.exception)
                self.assertIn("Load test results", text(app))
                required_widget(app.button, lambda item: item.key == "test_load_results",
                                "load selected test results").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertTrue(any("migration_required" in str(item.value) for item in app.warning))
                self.assertFalse(any("migration_required" in str(item.value) for item in app.error))

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
                self.assertIn("No task records are available.", text(app))
                self.assertIn("No canonical scenarios are recorded.", text(app))
                app.button(key="overview:summary:scenarios").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("No records match this summary.", text(app))

    def test_resolution_survives_new_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            _snapshot, diagnostics = validate_current(root, "pilot")
            self.assertEqual(diagnostics, [], diagnostics)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("Build", text(app))
                self.assertIn("Blocked", text(app))
                app.button(key="overview:attention:decision:choice").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                option = required_widget(app.selectbox, lambda item: item.key.startswith("decision-option:"), "decision option")
                actor = required_widget(app.text_input, lambda item: item.key.startswith("decision-actor:"), "decision actor")
                rationale = required_widget(app.text_area, lambda item: item.key.startswith("decision-rationale:"), "decision rationale")
                option.select("one")
                actor.input("Developer")
                rationale.input("Measured fit for the pilot")
                app.button(key="decision:submit").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                persisted = load_published(root, "pilot")
                choice = next(node for node in persisted.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["lifecycle"], "resolved")
                self.assertEqual(choice["history"][-1]["actor"], "Developer")
                self.assertEqual(choice["history"][-1]["rationale"], "Measured fit for the pilot")
                reloaded = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(reloaded.exception, reloaded.exception)
                self.assertIn("Ready", text(reloaded))
                decision_route = next((item for item in reloaded.button if item.key == "route:decision"), None)
                self.assertIsNotNone(decision_route, "resolved decision remains navigable in the hierarchy")
                decision_route.click().run(timeout=15)
                self.assertIn("resolved", text(reloaded))
                self.assertIn("Developer", text(reloaded))
                self.assertIn("Measured fit for the pilot", text(reloaded))

    def test_gitless_model_root_keeps_workbench_usable_without_git_fatal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("Build", text(app))
                self.assertIn("Blocked", text(app))
                self.assertEqual(len(app.json), 0)
                with patch.object(projection_module, "inspect_evidence",
                                  side_effect=AssertionError("overview must defer evidence scans")):
                    initial = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                    self.assertFalse(initial.exception, initial.exception)
                open_route(app, "result:CASE-1")
                self.assertFalse(app.exception, app.exception)
                self.assertIn("Load test results", text(app))
                app.button(key="test_load_results").click().run(timeout=15)
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
                self.assertIn("Build", text(app))
                self.assertIn("Blocked", text(app))
                app.button(key="overview:attention:decision:choice").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)

                before, diagnostics = validate_current(root, "pilot")
                self.assertEqual(diagnostics, [], diagnostics)
                model_before_spec_change = before.document
                published = load_published(root, "pilot")
                app.button(key="decision:submit").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("Actor and rationale are required", text(app))
                self.assertEqual(load_published(root, "pilot").identity, published.identity)
                choice = next(node for node in published.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["lifecycle"], "open")
                decision_before_spec_change = {
                    key: choice.get(key) for key in ("id", "options", "lifecycle", "history")
                }
                spec["criteria"][0]["then"] = ["Reject invalid input"]
                plan_path = root / "work/pilot/test-plan.json"
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                plan["spec_digest"] = hashlib.sha256(
                    json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest()
                external = edit(root, "pilot", before.identity["digest"], {
                    "commands": [],
                    "files": {"specs/current/pilot.json": json.dumps(spec),
                              "work/pilot/test-plan.json": json.dumps(plan)},
                })
                self.assertTrue(external["valid"], external)
                published = load_published(root, "pilot")
                self.assertEqual(
                    {key: published.document.get(key) for key in ("nodes", "edges")},
                    {key: model_before_spec_change.get(key) for key in ("nodes", "edges")},
                    "the linked-spec amendment leaves model nodes and relationships unchanged",
                )
                choice_after_spec_change = next(node for node in published.document["nodes"]
                                                if node["id"] == "choice")
                self.assertEqual({key: choice_after_spec_change.get(key) for key in decision_before_spec_change},
                                 decision_before_spec_change,
                                 "the linked-spec amendment leaves the decision unchanged")
                option = required_widget(app.selectbox, lambda item: item.key.startswith("decision-option:"), "decision option")
                actor = required_widget(app.text_input, lambda item: item.key.startswith("decision-actor:"), "decision actor")
                rationale = required_widget(app.text_area, lambda item: item.key.startswith("decision-rationale:"), "decision rationale")
                option.select("one")
                actor.input("Developer")
                rationale.input("Use the amended requirement")
                app.button(key="decision:submit").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("stale", text(app))
                self.assertIn("No change was saved", text(app))
                self.assertEqual(load_published(root, "pilot").identity, published.identity)
                choice = next(node for node in published.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["lifecycle"], "open")

                app.button(key="refresh").click().run(timeout=15)
                app.button(key="route:decision").click().run(timeout=15)
                option = required_widget(app.selectbox, lambda item: item.key.startswith("decision-option:"), "decision option")
                actor = required_widget(app.text_input, lambda item: item.key.startswith("decision-actor:"), "decision actor")
                rationale = required_widget(app.text_area, lambda item: item.key.startswith("decision-rationale:"), "decision rationale")
                option.select("one")
                actor.input("Developer")
                rationale.input("Use the amended requirement")
                app.button(key="decision:submit").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                resolved = load_published(root, "pilot")
                choice = next(node for node in resolved.document["nodes"] if node["id"] == "choice")
                self.assertEqual(choice["lifecycle"], "resolved")
                self.assertEqual(choice["history"][-1]["rationale"], "Use the amended requirement")
                reloaded = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(reloaded.exception, reloaded.exception)
                self.assertIn("Ready", text(reloaded))
                decision_route = next((item for item in reloaded.button if item.key == "route:decision"), None)
                self.assertIsNotNone(decision_route, "resolved decision remains navigable after refreshed resolution")
                decision_route.click().run(timeout=15)
                self.assertIn("resolved", text(reloaded))
                self.assertIn("Use the amended requirement", text(reloaded))
