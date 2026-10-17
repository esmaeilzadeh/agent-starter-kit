"""Direct subject entry and contextual Task journeys in the workbench UI."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "_ask/tests"), str(ROOT / "_ask/ui"),
                str(ROOT / "_ask/scripts")]
from revising_fixture import digest, model
from test_revising_context import _repo, _put


def _commit(root: Path, message: str) -> str:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", message], check=True)
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def _init_repository(root: Path) -> None:
    subprocess.run(["git", "init", "-q", "--initial-branch=main", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Workbench Test"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "workbench@example.invalid"], check=True)
    _repo(root)
    doc = model()
    doc["nodes"][0]["title"] = "Publication capability"
    doc["nodes"][1].update(title="Publish a useful result",
                           description="A developer can publish a verified result.")
    doc["nodes"][3]["execution"] = {"work_id": "product", "task_id": "WB-003"}
    doc["nodes"][2]["case"] = {"work_id": "product", "plan_digest": "pending",
                                "case_id": "WB-publish"}
    doc["nodes"][3]["context"] = [
        {"role": "spec", "path": "docs/context.md", "revision": "snapshot",
         "selector": {"kind": "heading", "path": ["Scope"]}},
        {"role": "plan", "path": "work/product/plan.md", "revision": "snapshot",
         "selector": {"kind": "plan-task", "heading_path": ["Work breakdown"],
                      "task_id": "WB-003"}},
    ]
    doc["nodes"].extend([
        {"id": "scenario-two", "type": "scenario", "title": "Review publication",
         "lifecycle": "active", "reference": {"path": "specs/current/product.json", "id": "EM-007"},
         "case": {"work_id": "product", "plan_digest": "pending", "case_id": "WB-review"}},
        {"id": "test-two", "type": "test", "title": "Review assertion", "lifecycle": "active",
         "reference": {"path": "work/product/test-plan.json", "id": "WB-review"}},
    ])
    doc["edges"].extend([
        {"type": "contains", "source": "story", "target": "scenario-two"},
        {"type": "contributes_to", "source": "task", "target": "scenario"},
        {"type": "contributes_to", "source": "task", "target": "scenario-two"},
        {"type": "covers", "source": "test-two", "target": "scenario-two"},
    ])
    spec = json.loads((root / "specs/current/product.json").read_text())
    plan = json.loads((root / "work/product/test-plan.json").read_text())
    plan["task_scopes"] = [{"task_id": "WB-003", "test_ids": ["WB-publish", "WB-review"]}]
    plan["task_scopes"].append({"task_id": "WB-001", "test_ids": []})
    plan["tests"].append({
        "id": "WB-review", "criterion_ids": ["EM-007"], "type": "unit", "change_kind": "new",
        "runner_id": "fixture", "case_id": "test_fixture.Cases.test_review",
        "source_paths": ["test_fixture.py"],
        "scenario": {"given": "A published result", "when": "Review", "then": ["It is accepted"]},
        "expected_assertions": [{"criterion_id": "EM-007", "checks": ["Accept the reviewed result"]}],
    })
    _put(root, "work/product/test-plan.json", plan)
    plan_digest = digest(plan)
    for node in doc["nodes"]:
        if node.get("type") == "scenario":
            node["case"]["plan_digest"] = plan_digest
    _put(root, "work/product/engineering-model.json", doc)
    _put(root, "work/product/inner-loop/tasks.yaml",
         b"schema: ask-inner-loop-tasks/v1\nwork_id: product\ntasks:\n"
         b"  - id: WB-003\n    title: Publish the selected result\n"
         b"    outcome: Publish a result only after its contract is satisfied.\n"
         b"    depends_on: [WB-001]\n    owned_paths: [src/publish.py]\n"
         b"  - id: WB-001\n    title: Prepare the contract\n"
         b"    outcome: Prepare the validated contract.\n    depends_on: []\n    owned_paths: [src/contract.py]\n")
    _put(root, "docs/context.md", b"# Scope\nA verified publication is visible to its intended readers.\n")
    _put(root, "work/product/plan.md",
         b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n"
         b"| WB-003 | Publish the selected result |\n| WB-001 | Prepare the contract |\n")
    _put(root, "work/archive/engineering-model.json", {
        "schema": "ask-engineering-model/v1", "work_id": "archive", "revision": 1,
        "nodes": [{"id": "archive-purpose", "type": "intent", "title": "Archived purpose",
                   "lifecycle": "active"}],
        "edges": [],
    })
    _commit(root, "Create admitted workbench fixture")
    subprocess.run(["git", "-C", str(root), "checkout", "-qb", "agent/product"], check=True)
    _put(root, "work/product/engineering-model.json", {**doc, "revision": 2})
    _commit(root, "Add working revision")


def _run(root: Path, subject: str | None = None):
    app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py"), default_timeout=30)
    if subject is not None:
        app.query_params["subject"] = subject
    with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
        app.run(timeout=30)
    return app


def _click(app, root: Path, key: str):
    with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
        app.button(key=key).click().run(timeout=30)
    return app


def _text(app) -> str:
    return "\n".join(str(item.value) for group in (
        app.title, app.header, app.subheader, app.markdown, app.caption,
        app.info, app.warning, app.error, app.success, app.text,
    ) for item in group)


class WorkbenchAppTests(unittest.TestCase):
    def test_direct_subject_standalone_shared_back_and_revision_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _init_repository(root)
            branch_before = subprocess.check_output(
                ["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
            app = _run(root, "story:story")
            self.assertFalse(app.exception, app.exception)
            self.assertEqual(app.session_state["_engineering_route"], "story")
            self.assertEqual(app.session_state["_engineering_route_history"], ["capability"])
            self.assertIn("A developer can publish a verified result.", _text(app))

            app = _run(root, "task:task")
            self.assertFalse(app.exception, app.exception)
            self.assertEqual(app.session_state["_engineering_route"], "WB-003")
            self.assertEqual(app.session_state["_engineering_route_history"],
                             ["capability", "story", "scenario-two"])
            self.assertIn("Publish the selected result", _text(app))
            self.assertIn("product Task product:task", _text(app))
            self.assertIn("execution owner product:WB-003", _text(app))
            _click(app, root, "route:back")
            self.assertEqual(app.session_state["_engineering_route"], "scenario-two")

            app = _run(root)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("Choose a Story or Task", _text(app))
            self.assertIn("Scenarios without a recorded story", _text(app))
            _click(app, root, "route:scenario")
            self.assertFalse(app.exception, app.exception)
            self.assertIn("A valid model", _text(app))
            self.assertIn("Only captured sources are used", _text(app))
            _click(app, root, "scenario:scenario:task:WB-003")
            self.assertEqual(app.session_state["_engineering_route"], "WB-003@scenario")
            _click(app, root, "route:back")
            self.assertEqual(app.session_state["_engineering_route"], "scenario")

            _click(app, root, "route:scenario-two")
            _click(app, root, "scenario:scenario-two:task:WB-003")
            self.assertEqual(app.session_state["_engineering_route"], "WB-003")
            _click(app, root, "route:back")
            self.assertEqual(app.session_state["_engineering_route"], "scenario-two")

            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app.selectbox(key="work_id").select("archive").run(timeout=30)
            self.assertFalse(app.exception, app.exception)
            self.assertIn("Committed · main", _text(app))
            self.assertIn("Read-only source", _text(app))
            self.assertEqual(subprocess.check_output(
                ["git", "-C", str(root), "branch", "--show-current"], text=True).strip(), branch_before)

    def test_task_purpose_passages_plan_and_exact_summary_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _init_repository(root)
            app = _run(root, "task:task")
            self.assertFalse(app.exception, app.exception)
            rendered = _text(app)
            for phrase in (
                "Publish a result only after its contract is satisfied.",
                "A verified publication is visible to its intended readers.",
                "| WB-003 | Publish the selected result |",
                "Dependencies", "WB-001", "Related Stories",
                "scenario", "WB-publish", "WB-review", "Completion is not verified",
            ):
                self.assertIn(phrase, rendered)
            self.assertTrue(any("src/publish.py" in str(table.value) for table in app.dataframe))
            overview = _run(root)
            _click(overview, root, "overview:summary:scenarios")
            self.assertEqual(overview.session_state["_engineering_overview_filter"],
                             {"kind": "scenarios", "ids": ["scenario", "scenario-two"],
                              "work_id": "product"})


if __name__ == "__main__":
    unittest.main()
