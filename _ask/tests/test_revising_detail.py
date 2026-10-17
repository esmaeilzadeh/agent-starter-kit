"""Readable test/result detail, guarded decisions and lazy refresh behavior."""
from __future__ import annotations

import os
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "_ask/tests"), str(ROOT / "_ask/ui"), str(ROOT / "_ask/scripts")]
from engineering_fixture import evidence_workbench, workbench_model
import test_engineering_ui
from engineering_model.admission import admit
from engineering_model.projection import project
from workbench_loading import load_selected_detail


def _run_existing(case: str) -> None:
    """Reuse established public-AppTest journeys without duplicating their fixture logic."""
    result = unittest.TestResult()
    test_engineering_ui.UiIntegrationTests(methodName=case).run(result)
    if result.errors or result.failures:
        details = "\n".join(message for _test, message in result.errors + result.failures)
        raise AssertionError(f"{case} failed:\n{details}")


def _open(app, route: str) -> None:
    button = next((item for item in app.button if item.key == f"route:{route}"), None)
    if button is None:
        raise AssertionError(f"missing route {route!r}")
    button.click().run(timeout=20)


class DetailAppTests(unittest.TestCase):
    def test_setup_action_assertion_helpers_observations_and_flow_specificity(self):
        self._assert_same_revision_setup_and_helper_are_loaded()
        self._assert_actual_output_is_available_only_for_valid_digests()
        _run_existing("test_planned_test_shows_its_source_in_the_detail_panel")
        _run_existing("test_historical_evidence_candidate_is_inspectable_without_being_current")
        _run_existing("test_repeated_nested_evidence_fields_do_not_duplicate_expanders")
        _run_existing("test_overview_loads_results_on_demand_and_explains_debug_identifiers")

    def _assert_same_revision_setup_and_helper_are_loaded(self):
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            source = root / "test_fixture.py"
            source.write_text(
                "def expected_output():\n    return 'accepted'\n\n"
                "class Cases:\n"
                "    def setUp(self):\n        self.expected = expected_output()\n\n"
                "    def test_behavior(self):\n"
                "        actual = self.expected\n"
                "        self.assertEqual(actual, 'accepted')\n")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Workbench Test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "workbench@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "Create selected helper fixture"], check=True)
            candidate = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            snapshot, diagnostics = admit(root, "pilot")
            self.assertFalse(diagnostics, diagnostics)
            projection = project(snapshot, root, include_evidence=False)
            test = next(row for row in projection["workbench"]["tests"] if row["id"] == "CASE-1")
            detail = load_selected_detail(
                root, snapshot, test, node_id="case",
                source_context={"kind": "git-commit", "work_id": "pilot", "commit": candidate},
                candidate_sha=candidate,
            )
            readable = detail.get("readable_test") or {}
            self.assertEqual(readable.get("status"), "current")
            self.assertTrue(any(item.get("role") == "setup" for item in readable.get("context", [])))
            helper = next(item for item in readable.get("context", [])
                          if str(item.get("selector", "")).endswith("expected_output"))
            self.assertIn("return 'accepted'", helper["source"])
            self.assertEqual(readable["flow"]["given"], "Valid input")
            self.assertEqual(readable["flow"]["when"], "Validate")
            self.assertIn("Accept", readable["flow"]["then"])
            original_expander = st.expander

            def expand_helper(*args, **kwargs):
                if "expected_output" in str(args[:1]):
                    kwargs["expanded"] = True
                return original_expander(*args, **kwargs)

            with (patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}),
                  patch.object(st, "expander", expand_helper)):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py"),
                                        default_timeout=30).run(timeout=30)
                _open(app, "test:CASE-1")
                self.assertFalse(app.exception, app.exception)
                rendered = test_engineering_ui.text(app)
                self.assertIn("Selected behavior flow", rendered)
                self.assertIn("Setup", rendered)
            self.assertIn("return 'accepted'", rendered)

    def _assert_actual_output_is_available_only_for_valid_digests(self):
        consumer, _historical = evidence_workbench()
        try:
            snapshot, diagnostics = admit(consumer.root, "w")
            self.assertFalse(diagnostics, diagnostics)
            projection = project(snapshot, consumer.root, include_evidence=False)
            test = next(row for row in projection["workbench"]["tests"] if row["id"] == "U")
            detail = load_selected_detail(
                consumer.root, snapshot, test, node_id="case",
                source_context={"kind": "git-commit", "work_id": "w", "commit": consumer.sha},
                candidate_sha=consumer.sha,
            )
            runs = detail["execution_history"]["runs"]
            self.assertTrue(runs)
            self.assertTrue(all(run.get("output_status") == "valid" for run in runs))
            self.assertTrue(all(run.get("output_text") for run in runs),
                            "only digest-verified retained logs are exposed as captured output")
            self.assertTrue(any(run.get("phase") == "red" and "FAIL" in run["output_text"]
                                for run in runs), "failed execution output remains distinct and readable")
        finally:
            consumer.close()

    def test_attributed_choice_reload_and_invalid_stale_historical_refusal(self):
        _run_existing("test_resolution_survives_new_session")
        _run_existing("test_referenced_spec_change_keeps_form_stale_until_refresh")
        self._assert_task_displays_blocking_decision_context()
        self._assert_committed_decision_form_is_read_only()

    def _assert_task_displays_blocking_decision_context(self):
        import tempfile

        from engineering_fixture import write_json

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, _spec = workbench_model(root)
            choice = next(node for node in model["nodes"] if node["id"] == "choice")
            choice["history"] = [{
                "event": "reopened", "actor": "Reviewer",
                "rationale": "The latest evidence no longer supports the earlier choice.",
                "timestamp": "2026-01-02T03:04:05Z", "options": choice["options"], "resolution": {},
            }]
            write_json(root, "work/pilot/engineering-model.json", model)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py"),
                                        default_timeout=30).run(timeout=30)
                _open(app, "build")
                self.assertFalse(app.exception, app.exception)
                rendered = test_engineering_ui.text(app)
                self.assertIn("Choose · choice is open; requires resolved", rendered)
                self.assertIn("Available choices: First (one); Second (two)", rendered)
                self.assertIn("Last decision update by Reviewer", rendered)
                self.assertIn("The latest evidence no longer supports the earlier choice.", rendered)

    def _assert_committed_decision_form_is_read_only(self):
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            subprocess.run(["git", "init", "-q", "--initial-branch=main", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Workbench Test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "workbench@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "checkout", "-qb", "agent/pilot"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "Capture read-only decision"], check=True)
            model_path = root / "work/pilot/engineering-model.json"
            before = model_path.read_bytes()
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py"),
                                        default_timeout=30).run(timeout=30)
                source = next(item for item in app.selectbox if item.key == "source_id")
                source.select("git:agent/pilot").run(timeout=30)
                _open(app, "decision")
                self.assertFalse(app.exception, app.exception)
                submit = next(item for item in app.button if item.key == "decision:submit")
                self.assertTrue(submit.disabled)
                self.assertIn("read-only", test_engineering_ui.text(app).lower())
                self.assertEqual(model_path.read_bytes(), before)

    def test_overview_has_no_source_evidence_reads_and_refresh_detects_tampering(self):
        import workbench_loading
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            original = workbench_loading._working_source
            with (patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}),
                  patch.object(workbench_loading, "_working_source", wraps=original) as load_source):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py"), default_timeout=30).run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                load_source.assert_not_called()
                _open(app, "test:CASE-1")
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(load_source.call_count, 1)
                _open(app, "purpose")
                _open(app, "test:CASE-1")
                self.assertEqual(load_source.call_count, 1,
                                 "unchanged selected details reuse their parsed source cache")

                source = root / "test_fixture.py"
                before = source.stat()
                source.write_text(source.read_text() + "\n# changed helper bytes\n")
                os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
                app.button(key="refresh").click().run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                _open(app, "test:CASE-1")
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(load_source.call_count, 2,
                                 "same-mtime source changes invalidate selected detail on refresh")

        consumer, _historical = evidence_workbench()
        try:
            original_history = workbench_loading.execution_history
            with (patch.dict(os.environ, {"ASK_MODEL_ROOT": str(consumer.root)}),
                  patch.object(workbench_loading, "execution_history", wraps=original_history) as inspect_history):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py"), default_timeout=30).run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                inspect_history.assert_not_called()
                _open(app, "result:U")
                self.assertFalse(app.exception, app.exception)
                self.assertIn("Captured execution output", test_engineering_ui.text(app))
                self.assertGreater(inspect_history.call_count, 0)
                count = inspect_history.call_count
                _open(app, "purpose")
                _open(app, "result:U")
                self.assertEqual(inspect_history.call_count, count,
                                 "revisited detail reuses its evidence cache")

                ledger = json.loads((consumer.root / "work/w/traceability/executions.json").read_text())
                final = next(item for item in reversed(ledger)
                             if item.get("candidate_sha") == consumer.sha
                             and item.get("phase") == "final_green"
                             and item.get("scope") == "workstream")
                report_path = consumer.root / "work/w/traceability/runs" / final["run_id"] / "results.json"
                report = json.loads(report_path.read_text())
                case = next(item for item in report["cases"] if item.get("test_id") == "U")
                log_path = consumer.root / case["output_artifact"]
                before = log_path.stat()
                log_path.write_bytes(log_path.read_bytes() + b"tampered")
                os.utime(log_path, ns=(before.st_atime_ns, before.st_mtime_ns))
                app.button(key="refresh").click().run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                _open(app, "result:U")
                self.assertFalse(app.exception, app.exception)
                self.assertGreater(inspect_history.call_count, count,
                                   "same-mtime log tampering invalidates the evidence cache")
                self.assertIn("Output integrity: invalid", test_engineering_ui.text(app))
        finally:
            consumer.close()

        _run_existing("test_gitless_model_root_keeps_workbench_usable_without_git_fatal")
