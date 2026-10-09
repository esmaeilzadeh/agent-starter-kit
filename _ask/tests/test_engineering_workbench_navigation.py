"""App-level journeys through the one connected work hierarchy."""
from __future__ import annotations

import os
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/tests"))
from engineering_fixture import workbench_model, write_json


def _init_repo(root: Path, branch: str = "agent/pilot") -> None:
    subprocess.run(["git", "init", "-q", "--initial-branch=main", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Workbench Test"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "workbench@example.invalid"], check=True)


def _commit(root: Path, message: str) -> str:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", message], check=True)
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def _start_agent_branch(root: Path, branch: str = "agent/pilot") -> None:
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", branch], check=True)


def _add_story(model):
    model["nodes"].extend([
        {"id": "epic", "type": "feature", "title": "Pilot epic", "lifecycle": "active"},
        {"id": "story", "type": "story", "title": "Pilot story", "lifecycle": "active"},
    ])
    model["edges"].append({"type": "contains", "source": "purpose", "target": "epic"})
    model["edges"].append({"type": "contains", "source": "epic", "target": "story"})
    model["edges"] = [edge for edge in model["edges"]
                      if not (edge.get("type") == "contains" and edge.get("target") == "scenario")]
    model["edges"].append({"type": "contains", "source": "story", "target": "scenario"})
    return model


def _add_second_scenario(root: Path, model):
    spec_path = root / "specs/current/pilot.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["criteria"].append({"id": "P-002", "given": "A second input", "when": "Validate",
                             "then": ["Accept the second case"], "verification_mode": "tests"})
    write_json(root, "specs/current/pilot.json", spec)
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
    write_json(root, "work/pilot/test-plan.json", plan)
    model["nodes"].extend([
        {"id": "scenario-2", "type": "scenario", "title": "Second behavior", "lifecycle": "active",
         "reference": {"path": "specs/current/pilot.json", "id": "P-002"}},
        {"id": "case-2", "type": "test", "title": "Second assertion", "lifecycle": "active",
         "reference": {"path": "work/pilot/test-plan.json", "id": "CASE-2"}},
    ])
    model["edges"].extend([
        {"type": "contains", "source": "story", "target": "scenario-2"},
        {"type": "covers", "source": "case-2", "target": "scenario-2"},
    ])
    return model


def _run(root: Path):
    return AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=20)


def _text(app) -> str:
    return "\n".join(str(item.value) for collection in (
        app.title, app.header, app.subheader, app.markdown, app.caption,
        app.info, app.warning, app.error, app.success, app.text,
    ) for item in collection) + "\n" + "\n".join(str(item.label) for item in app.button)


class WorkbenchTests(unittest.TestCase):
    def test_work_default_routes_and_context_reset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _init_repo(root)
            model, _ = workbench_model(root)
            other_model = copy.deepcopy(model)
            other_model["work_id"] = "archive"
            other_spec = json.loads((root / "specs/current/pilot.json").read_text(encoding="utf-8"))
            other_spec["work_id"] = "archive"
            write_json(root, "specs/current/archive.json", other_spec)
            for node in other_model["nodes"]:
                reference = node.get("reference", {})
                if reference.get("path") == "specs/current/pilot.json":
                    reference["path"] = "specs/current/archive.json"
                elif reference.get("path") == "work/pilot/test-plan.json":
                    reference["path"] = "work/archive/test-plan.json"
            other_plan = json.loads((root / "work/pilot/test-plan.json").read_text(encoding="utf-8"))
            other_plan["work_id"] = "archive"
            other_plan["spec_digest"] = "0" * 64
            write_json(root, "work/archive/test-plan.json", other_plan)
            (root / "work/archive/inner-loop").mkdir(parents=True)
            (root / "work/archive/inner-loop/tasks.yaml").write_text(
                (root / "work/pilot/inner-loop/tasks.yaml").read_text(encoding="utf-8").replace(
                    "work_id: pilot", "work_id: archive"), encoding="utf-8")
            write_json(root, "work/archive/engineering-model.json", other_model)
            _commit(root, "Create archived baseline")
            _start_agent_branch(root)
            _add_story(model)
            _add_second_scenario(root, model)
            write_json(root, "work/pilot/engineering-model.json", model)
            _commit(root, "Connect pilot story and scenario tests")
            next(node for node in model["nodes"] if node["id"] == "story")["title"] = "Working draft story"
            write_json(root, "work/pilot/engineering-model.json", model)
            write_json(root, "work/missing/engineering-model.json", {"schema": "unrecognized"})
            committed_head = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                failures = []
                app = _run(root)
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(app.selectbox(key="work_id").value, "pilot")
                has_source_selector = any(item.key == "source_id" for item in app.selectbox)
                if not has_source_selector:
                    failures.append("a separate source selector is required")
                self.assertIn("Epic", _text(app))
                self.assertIn("Working draft story", _text(app))
                self.assertIn("Working tree", _text(app))
                self.assertIn("Validated inputs", _text(app))
                self.assertNotIn("Workbench section", _text(app))
                self.assertFalse(app.tabs)

                # Selecting a canonical descendant updates one breadcrumbed route.
                app.button(key="route:scenario").click().run(timeout=20)
                self.assertFalse(app.exception, app.exception)
                rendered = _text(app)
                for crumb in ("Purpose", "Working draft story", "Canonical behavior"):
                    self.assertIn(crumb, rendered)
                app.button(key="route:scenario-2").click().run(timeout=20)
                self.assertFalse(app.exception, app.exception)
                available_routes = {item.key for item in app.button}
                if "route:test:CASE-2" not in available_routes:
                    failures.append("second scenario must retain its task, distinct test, and result route")
                else:
                    app.button(key="route:test:CASE-2").click().run(timeout=20)
                    self.assertFalse(app.exception, app.exception)
                    self.assertEqual(app.session_state["_engineering_route"], "test:CASE-2")
                    crumbs = _text(app)
                    for crumb in ("Working draft story", "Second behavior", "Build", "Second assertion"):
                        self.assertIn(crumb, crumbs)
                    app.button(key="route:result:CASE-2").click().run(timeout=20)
                    self.assertEqual(app.session_state["_engineering_route"], "result:CASE-2")
                    self.assertIn("Selected test: CASE-2", _text(app))
                    app.button(key="route:back").click().run(timeout=20)
                    self.assertFalse(app.exception, app.exception)
                    self.assertEqual(app.session_state["_engineering_route"], "test:CASE-2")
                    self.assertEqual(app.subheader[0].value, "Second assertion",
                                     "Back should render the restored test in the same rerun")

                # A committed ref is a distinct, immutable source; selecting it must
                # reset route/form state without moving the checkout.
                if has_source_selector:
                    source_selector = app.selectbox(key="source_id")
                    self.assertIn("git:agent/pilot", source_selector.options)
                    source_selector.select("git:agent/pilot").run(timeout=20)
                    self.assertFalse(app.exception, app.exception)
                    self.assertEqual(app.session_state["_engineering_route"], "purpose")
                    self.assertFalse(app.session_state["_engineering_form_identity"]["editable"])
                    self.assertEqual(app.session_state["_engineering_source_context"]["commit"], committed_head)
                    self.assertIn("Read-only source", _text(app))
                    self.assertIn("Pilot story", _text(app))
                    self.assertNotIn("Working draft story", _text(app))
                    app.button(key="route:decision").click().run(timeout=20)
                    self.assertTrue(app.button(key="decision:submit").disabled)
                    self.assertEqual(subprocess.check_output(
                        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(), committed_head)

                app.selectbox(key="work_id").select("archive").run(timeout=20)
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(app.selectbox(key="work_id").value, "archive")
                self.assertEqual(app.session_state["_engineering_route"], "purpose")
                archived_view = _text(app)
                if "EM001_CANONICAL_DEFINITION" not in archived_view:
                    failures.append("committed snapshots must expose canonical spec-to-plan admission errors")
                if "Canonical behavior" in archived_view:
                    failures.append("a rejected committed snapshot must not render its normal hierarchy")
                self.assertEqual(subprocess.check_output(
                    ["git", "-C", str(root), "branch", "--show-current"], text=True).strip(),
                    "agent/pilot")
                app.selectbox(key="work_id").select("missing").run(timeout=20)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("could not be admitted", _text(app).lower())
                self.assertEqual(failures, [], "; ".join(failures))

    def test_navigation_does_not_refresh_stale_form_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _init_repo(root)
            model, _ = workbench_model(root)
            _add_story(model)
            write_json(root, "work/pilot/engineering-model.json", model)
            _commit(root, "Create editable pilot")
            _start_agent_branch(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = _run(root)
                self.assertFalse(app.exception, app.exception)
                digest = app.session_state["_engineering_displayed_view"]["snapshot"]["digest"]
                try:
                    form_identity = app.session_state["_engineering_form_identity"]
                except KeyError:
                    form_identity = None
                self.assertEqual(form_identity,
                                 {"work_id": "pilot", "digest": digest, "editable": True})
                app.button(key="route:scenario").click().run(timeout=20)
                self.assertEqual(app.session_state["_engineering_form_identity"]["digest"], digest)
                app.button(key="route:back").click().run(timeout=20)
                self.assertEqual(app.session_state["_engineering_route"], "purpose")
                self.assertEqual(app.subheader[0].value, "Purpose",
                                 "Back should render the restored epic in the same rerun")
                app.button(key="route:scenario").click().run(timeout=20)

                # A linked spec change makes the captured edit stale. Navigation cannot
                # replace its identity or write the form; Refresh is the explicit recapture.
                spec_path = root / "specs/current/pilot.json"
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
                spec["revision"] += 1
                write_json(root, "specs/current/pilot.json", spec)
                plan_path = root / "work/pilot/test-plan.json"
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                plan["spec_digest"] = hashlib.sha256(
                    json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                write_json(root, "work/pilot/test-plan.json", plan)
                app.button(key="route:decision").click().run(timeout=20)
                self.assertEqual(app.session_state["_engineering_form_identity"]["digest"], digest)
                actor_key = next(item.key for item in app.text_input
                                 if item.key and item.key.startswith("decision-actor:"))
                rationale_key = next(item.key for item in app.text_area
                                     if item.key and item.key.startswith("decision-rationale:"))
                app.text_input(key=actor_key).input("Developer")
                app.text_area(key=rationale_key).input("Checked against the current specification")
                app.button(key="decision:submit").click().run(timeout=20)
                self.assertIn("stale", _text(app).lower())
                self.assertFalse(app.button(key="decision:submit").disabled)
                current_model = json.loads(
                    (root / "work/pilot/engineering-model.json").read_text(encoding="utf-8"))
                decision = next(node for node in current_model["nodes"] if node["id"] == "choice")
                self.assertEqual(decision["history"], [])
                self.assertTrue(app.button(key="refresh"))
                app.button(key="refresh").click().run(timeout=20)
                self.assertNotEqual(app.session_state["_engineering_form_identity"]["digest"], digest)
                self.assertEqual(app.session_state["_engineering_route"], "purpose")


if __name__ == "__main__":
    unittest.main()
