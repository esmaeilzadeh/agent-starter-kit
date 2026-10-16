"""Qualified workbench projections and immutable source inspection."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from _ask.scripts.engineering_model.admission import validate_current
from _ask.scripts.engineering_model.projection import project
from _ask.scripts.engineering_model.snapshot import capture
from _ask.scripts.engineering_model.workbench_sources import discover_work, read_snapshot
from _ask.tests.revising_fixture import digest
from _ask.tests.test_revising_context import _put, _repo
from _ask.tests.engineering_fixture import model_command


def _projection_repo(root):
    _repo(root)
    model_path = root / "work/product/engineering-model.json"
    model = json.loads(model_path.read_text())
    model["nodes"].extend([
        {"id": "scenario-stale", "type": "scenario", "title": "Stale case", "lifecycle": "active",
         "reference": {"path": "specs/current/product.json", "id": "EM-007"},
         "case": {"work_id": "product", "plan_digest": "pending", "case_id": "WB-stale"}},
        {"id": "test-stale", "type": "test", "title": "Stale assertion", "lifecycle": "active",
         "reference": {"path": "work/product/test-plan.json", "id": "WB-stale"}},
        {"id": "standalone", "type": "task", "title": "Standalone support", "lifecycle": "planned",
         "execution": {"work_id": "delivery", "task_id": "shared-17"}},
        {"id": "story-two", "type": "story", "title": "Second outcome", "lifecycle": "active"},
    ])
    model["nodes"][2]["case"]["plan_digest"] = "pending"
    model["nodes"].append({"id": "choice", "type": "decision", "title": "Publish decision",
                          "lifecycle": "open", "options": [{"id": "yes", "label": "Yes"},
                                                               {"id": "no", "label": "No"}],
                          "history": []})
    model["edges"].append({"type": "depends_on", "source": "task", "target": "choice"})
    model["edges"].extend([
        {"type": "covers", "source": "test-stale", "target": "scenario-stale"},
        {"type": "contributes_to", "source": "standalone", "target": "story"},
        {"type": "contributes_to", "source": "standalone", "target": "story-two"},
    ])
    spec = json.loads((root / "specs/current/product.json").read_text())
    plan = json.loads((root / "work/product/test-plan.json").read_text())
    plan["task_scopes"] = [
        {"task_id": "WB-003", "test_ids": ["WB-publish"]},
        {"task_id": "WB-004", "test_ids": ["WB-stale"]},
    ]
    plan["tests"][0]["criterion_ids"] = ["EM-007"]
    stale_case = next((row for row in plan["tests"] if row.get("id") == "WB-stale"), None)
    if stale_case is None:
        plan["tests"].append({"id": "WB-stale", "criterion_ids": ["EM-007"], "type": "unit",
                              "change_kind": "new", "runner_id": "fixture", "case_id": "test_fixture.Cases.test_stale",
                              "source_paths": ["test_fixture.py"],
                              "scenario": {"given": "Same obligation", "when": "Stale route", "then": ["Refuse"]},
                              "expected_assertions": [{"criterion_id": "EM-007", "checks": ["Refuse stale route"]}]})
    else:
        stale_case["criterion_ids"] = ["EM-007"]
    model["nodes"][2]["case"]["plan_digest"] = digest(plan)
    model["nodes"][5]["case"]["plan_digest"] = digest(plan)
    _put(root, "specs/current/product.json", spec)
    _put(root, "work/product/test-plan.json", plan)
    _put(root, "work/product/engineering-model.json", model)
    graph_path = root / "work/product/inner-loop/tasks.yaml"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(
        "schema: ask-inner-loop-tasks/v1\nwork_id: product\ntasks:\n"
        "  - id: WB-003\n    title: Publish safely\n    outcome: Publish the selected case\n"
        "    depends_on: []\n    owned_paths: [src/publish.py]\n"
        "  - id: WB-004\n    title: Refuse stale input\n    outcome: Reject stale routes\n"
        "    depends_on: [WB-003]\n    owned_paths: [src/stale.py]\n", encoding="utf-8")
    return model, plan


class ProjectionTests(unittest.TestCase):
    def test_qualified_tasks_context_scopes_and_separate_status_authorities(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _projection_repo(root)
            snapshot, errors = validate_current(root, "product")
            self.assertFalse(errors, str(errors))
            view = project(snapshot, root, include_evidence=False)
            tasks = {item["id"]: item for item in view["workbench"]["tasks"]}
            tests = {item["id"]: item for item in view["workbench"]["tests"]}
            self.assertEqual(tasks["WB-003"].get("product_identity"), {"work_id": "product", "node_id": "task"})
            self.assertEqual(tasks["WB-003"].get("execution_identity"), {"work_id": "product", "task_id": "WB-003"})
            self.assertEqual(tasks["standalone"].get("product_identity"), {"work_id": "product", "node_id": "standalone"})
            self.assertEqual(tasks["standalone"].get("execution_identity"), {"work_id": "delivery", "task_id": "shared-17"})
            self.assertEqual(len([row for row in tasks.values() if row["product_identity"] ==
                                  {"work_id": "product", "node_id": "standalone"}]), 1,
                             "shared work is represented by one product identity")
            self.assertIn("story-two", [item["id"] for item in tasks["standalone"].get("related_stories", [])])
            self.assertEqual(tasks["WB-003"]["outcome"], "Publish the selected case")
            self.assertEqual(tasks["WB-003"]["dependencies"], [])
            self.assertEqual(tasks["WB-003"]["owned_paths"], ["src/publish.py"])
            self.assertEqual(tasks["WB-003"]["owned_test_ids"], ["WB-publish"])
            self.assertEqual(tests["WB-publish"]["scenario_ids"], ["scenario"],
                             "shared criterion membership must not join the distinct WB-stale flow")
            self.assertEqual(tests["WB-stale"]["scenario_ids"], ["scenario-stale"])
            task_detail = next(row for row in view["tasks"] if row["id"] == "task")
            context = task_detail.get("context", {})
            spec_passages = context.get("spec", [])
            plan_passages = context.get("plan", [])
            self.assertEqual(len(spec_passages), 1)
            self.assertEqual(len(plan_passages), 1)
            spec_passage, plan_passage = spec_passages[0], plan_passages[0]
            self.assertEqual(spec_passage.get("state"), "available")
            self.assertEqual(spec_passage.get("text"), "# Scope\nCurrent contract.\n")
            self.assertEqual(plan_passage.get("state"), "available")
            self.assertIn("WB-003", plan_passage.get("text", ""))
            self.assertNotIn("WB-004", plan_passage.get("text", ""))
            self.assertEqual(tasks["WB-003"]["status"], "planned")
            self.assertEqual(tasks["WB-003"].get("model_status"), "blocked")
            self.assertEqual(tasks["WB-003"].get("readiness_source"), "engineering-model")
            self.assertEqual({item["id"] for item in view["attention"]}, {"choice", "task"})
            self.assertEqual(tasks["WB-003"].get("status_source"), "no-runtime-record")
            self.assertIsNone(tasks["WB-003"].get("verification_status"))
            self.assertEqual(tasks["WB-003"].get("verification_source"), "no-verification-record")
            runtime = {"work_id": "product", "tasks": {"WB-003": {"status": "integrated"}}}
            _put(root, "work/product/inner-loop/state.json", runtime)
            refreshed = project(capture(root, "product"), root, include_evidence=False)
            updated = next(row for row in refreshed["workbench"]["tasks"] if row["id"] == "WB-003")
            self.assertEqual(updated["status"], "completed")
            self.assertEqual(updated["runtime_status"], "integrated")
            self.assertIsNone(updated.get("verification_status"), "runtime state must not imply verified completion")

    def test_live_archive_foreign_and_historical_revisions_are_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(["git", *args], cwd=root, check=True,
                                      capture_output=True, text=True).stdout.strip()
            git("init", "-b", "main")
            git("config", "user.email", "projection@example.invalid")
            git("config", "user.name", "Projection Fixture")
            _put(root, "work/archive/engineering-model.json", {"schema": "fixture", "revision": 1})
            _put(root, "work/product/engineering-model.json", {"schema": "fixture", "work_id": "product", "revision": 1})
            (root / "work/product/inner-loop").mkdir(parents=True)
            (root / "work/product/inner-loop/tasks.yaml").write_bytes(b"revision: 1\n")
            _put(root, "work/product/test-plan.json", {"work_id": "product", "revision": 1})
            (root / "src").mkdir()
            (root / "src/harness.py").write_text("VALUE = 'historical'\n", encoding="utf-8")
            git("add", "-A")
            git("commit", "-m", "initial archive and product")
            old_product = git("rev-parse", "HEAD")
            git("checkout", "-b", "agent/product")
            _put(root, "work/product/engineering-model.json", {"schema": "fixture", "work_id": "product", "revision": 2})
            (root / "work/product/inner-loop").mkdir(parents=True, exist_ok=True)
            (root / "work/product/inner-loop/tasks.yaml").write_bytes(b"revision: 2\n")
            _put(root, "work/product/test-plan.json", {"work_id": "product", "revision": 2})
            git("add", "-A")
            git("commit", "-m", "current product")
            _put(root, "work/other/engineering-model.json", {"schema": "fixture", "work_id": "other", "revision": 1})
            git("add", "-A")
            git("commit", "-m", "foreign model")
            other_revision = git("rev-parse", "HEAD")
            before_head = git("rev-parse", "HEAD")
            before_refs = git("show-ref")
            before_files = {path: (root / path).read_bytes() for path in (
                "work/product/engineering-model.json", "work/product/inner-loop/tasks.yaml",
                "work/product/test-plan.json", "work/other/engineering-model.json", "src/harness.py")}
            inventory = discover_work(root)
            self.assertEqual(inventory["current_work_id"], "product")
            rows = {row["work_id"]: row for row in inventory["workstreams"]}
            self.assertEqual(rows["product"]["source"], "git-ref")
            selected = read_snapshot(root, old_product, "product", paths=["src/harness.py"])
            foreign = read_snapshot(root, other_revision, "other")
            self.assertEqual(selected.commit, old_product)
            self.assertEqual(json.loads(selected.files["work/product/engineering-model.json"]),
                             {"schema": "fixture", "work_id": "product", "revision": 1})
            self.assertEqual(selected.files["src/harness.py"], b"VALUE = 'historical'\n")
            self.assertFalse(selected.editable)
            self.assertEqual(foreign.commit, other_revision)
            self.assertEqual(json.loads(foreign.files["work/other/engineering-model.json"])["work_id"], "other")
            self.assertEqual(git("rev-parse", "HEAD"), before_head)
            self.assertEqual(git("show-ref"), before_refs)
            self.assertEqual({path: (root / path).read_bytes() for path in before_files}, before_files)
            self.assertEqual(selected.files["work/product/inner-loop/tasks.yaml"], b"revision: 1\n")
            self.assertEqual(json.loads(selected.files["work/product/test-plan.json"])["revision"], 1)

    def test_v2_json_markdown_ids_and_state_match(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _projection_repo(root)
            json_result = model_command(root, "show", "--work-id", "product", "--format", "json")
            self.assertEqual(json_result.returncode, 0, json_result.stderr)
            json_view = json.loads(json_result.stdout)
            markdown_result = model_command(root, "show", "--work-id", "product", "--format", "markdown")
            self.assertEqual(markdown_result.returncode, 0, markdown_result.stderr)
            self.assertIn(json_view["snapshot"]["digest"], markdown_result.stdout)
            self.assertEqual(json_view["work_id"], "product")
            planned = next(row for row in json_view["workbench"]["tasks"] if row["id"] == "WB-003")
            self.assertEqual(planned["status"], "planned")
            self.assertEqual(planned.get("model_status"), "blocked")
            self.assertEqual({item["id"] for item in json_view["attention"]}, {"choice", "task"})
            self.assertIn("WB-003", markdown_result.stdout)
            self.assertIn("choice", markdown_result.stdout)
            before = (root / "work/product/engineering-model.json").read_bytes()
            (root / "work/product/inner-loop/tasks.yaml").write_text("schema: broken\n", encoding="utf-8")
            refused = model_command(root, "show", "--work-id", "product", "--format", "json")
            self.assertNotEqual(refused.returncode, 0)
            refused_view = json.loads(refused.stdout)
            self.assertTrue(refused_view["diagnostics"])
            self.assertFalse(refused_view["editable"])
            self.assertTrue(refused_view["last_validated"])
            self.assertEqual(refused_view["snapshot"]["digest"], json_view["snapshot"]["digest"])
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
