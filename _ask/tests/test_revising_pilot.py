"""Migration, comprehension, and representative-passage pilot gates."""
import copy
import hashlib
import json
import os
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.source = {"schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
                       "nodes": [{"id": "intent", "type": "intent", "title": "Intent", "lifecycle": "active"},
                                 {"id": "case", "type": "scenario", "title": "Case", "lifecycle": "active",
                                  "reference": {"path": "specs/current/pilot.json", "id": "C-1"}}],
                       "edges": [{"type": "contains", "source": "intent", "target": "case"}]}
        self.target = copy.deepcopy(self.source)
        self.target.update(schema="ask-engineering-model/v2", revision=2)

    def test_reviewed_migration_binds_both_models_and_preserves_identity_authority(self):
        from engineering_model.migration import preservation_diff, review_migration

        diff = preservation_diff(self.source, self.target)
        approved = {"schema": "ask-engineering-migration-review/v1", "decision": "APPROVED",
                    "reviewer": "independent reviewer", "rationale": "Preserve recorded identity",
                    "source_digest": digest(self.source), "target_digest": digest(self.target),
                    "diff_digest": digest(diff)}
        result = review_migration(self.source, self.target, approved, work_id="pilot")
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["preservation_diff"], {"added_ids": [], "removed_ids": [],
                                                        "changed_references": [],
                                                        "changed_edges": {"removed": [], "added": []}})
        bad = copy.deepcopy(self.target)
        bad["nodes"][1]["reference"]["id"] = "C-2"
        with self.assertRaisesRegex(ValueError, "reference"):
            review_migration(self.source, bad, approved, work_id="pilot")

    def test_unreviewed_or_digest_stale_migration_is_refused(self):
        from engineering_model.migration import review_migration, preservation_diff

        review = {"decision": "APPROVED", "reviewer": "reviewer", "rationale": "reviewed",
                  "source_digest": digest(self.source), "target_digest": digest(self.target),
                  "diff_digest": digest(preservation_diff(self.source, self.target))}
        with self.assertRaisesRegex(ValueError, "schema"):
            review_migration(self.source, self.target, review, work_id="pilot")
        review["schema"] = "ask-engineering-migration-review/v1"
        changed = copy.deepcopy(self.target)
        changed["revision"] = 3
        with self.assertRaisesRegex(ValueError, "digest"):
            review_migration(self.source, changed, review, work_id="pilot")


class ReadabilityTests(unittest.TestCase):
    def test_each_answer_and_changed_dependency_control_comprehension_validity(self):
        from engineering_model.readability import validate_record

        expected = {"candidate_sha": "a" * 40, "snapshot_digest": "b" * 64,
                    "task": {"work_id": "w", "node_id": "task"},
                    "scenario": {"work_id": "w", "node_id": "scenario"},
                    "test": {"work_id": "w", "test_id": "WB-1", "case_id": "test_case"},
                    "dependencies": {"source_sha": "c" * 40, "spec_digest": "d" * 64}}
        prompts = ["purpose", "spec_context", "plan_context", "concrete_flow", "setup",
                   "action", "expected_observation", "assertion", "actual_outcome", "applicability"]
        record = {"schema": "ask-workbench-comprehension/v1", **expected,
                  "chat_assistance": False, "participant": "returning human", "assessor": "independent assessor",
                  "timestamp": "2026-10-17T12:00:00Z",
                  "answers": [{"prompt": prompt, "answer": "Human answer", "assessment": "pass",
                               "assessor_reason": "Evidence supports answer", "evidence": "source"}
                              for prompt in prompts]}
        self.assertEqual(validate_record(record, expected)["status"], "valid")
        failed = copy.deepcopy(record)
        failed["answers"][4]["assessment"] = "fail"
        self.assertEqual(validate_record(failed, expected)["status"], "failed")
        stale = dict(expected, dependencies={"source_sha": "e" * 40, "spec_digest": "d" * 64})
        self.assertEqual(validate_record(record, stale)["status"], "stale")
        assisted = copy.deepcopy(record)
        assisted["chat_assistance"] = True
        self.assertEqual(validate_record(assisted, expected)["status"], "failed")


class PilotIntegrationTests(unittest.TestCase):
    def test_migration_passages_use_the_real_guarded_entry(self):
        from engineering_model.admission import admit
        from engineering_model.migration import _digest, migrate, preservation_diff

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / "work/pilot"
            work.mkdir(parents=True)
            (root / "specs/current").mkdir(parents=True)
            (root / "specs/current/pilot.md").write_text(
                "# Specification: Pilot\n## Behavior\nThe task has observable context.\n", encoding="utf-8")
            (work / "plan.md").write_text(
                "# Plan: Pilot\n## Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| T-1 | Inspect context |\n",
                encoding="utf-8")
            source = {"schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
                      "nodes": [{"id": "intent", "type": "intent", "title": "Pilot", "lifecycle": "active"},
                                {"id": "task", "type": "task", "title": "Inspect", "lifecycle": "planned"}],
                      "edges": [{"type": "contains", "source": "intent", "target": "task"}]}
            model_path = work / "engineering-model.json"
            model_path.write_text(json.dumps(source), encoding="utf-8")
            baseline, errors = admit(root, "pilot")
            self.assertFalse(errors, errors)
            target = copy.deepcopy(source)
            target.update(schema="ask-engineering-model/v2", revision=2)
            target["nodes"][1].update(
                execution={"work_id": "pilot", "task_id": "T-1"},
                context=[
                    {"role": "spec", "path": "specs/current/pilot.md", "revision": "snapshot",
                     "selector": {"kind": "heading", "path": ["Specification: Pilot", "Behavior"]}},
                    {"role": "plan", "path": "work/pilot/plan.md", "revision": "snapshot",
                     "selector": {"kind": "plan-task", "heading_path": ["Plan: Pilot", "Work breakdown"],
                                  "task_id": "T-1"}},
                ])
            review = {"schema": "ask-engineering-migration-review/v1", "decision": "APPROVED",
                      "reviewer": "independent reviewer", "rationale": "Preserve historical identities",
                      "source_digest": _digest(source), "target_digest": _digest(target),
                      "diff_digest": _digest(preservation_diff(source, target))}
            missing_context = copy.deepcopy(target)
            missing_context["nodes"][1]["context"][1]["selector"]["task_id"] = "absent"
            stale_review = dict(review, target_digest=_digest(missing_context),
                                diff_digest=_digest(preservation_diff(source, missing_context)))
            refused = migrate(root, "pilot", baseline.identity["digest"], missing_context, stale_review,
                              selected_task_id="task")
            self.assertFalse(refused["valid"])
            self.assertEqual(refused["diagnostics"][0]["code"], "EM015_CONTEXT_REQUIRED")
            self.assertEqual(json.loads(model_path.read_text()), source)
            accepted = migrate(root, "pilot", baseline.identity["digest"], target, review,
                               selected_task_id="task")
            self.assertTrue(accepted["valid"], accepted)
            self.assertEqual(accepted["steps"], ["pre", "action", "post", "publication"])
            self.assertEqual(json.loads(model_path.read_text())["schema"], "ask-engineering-model/v2")

    def test_new_work_requires_its_own_spec_graph_review_and_accepted_contract(self):
        root = Path(__file__).resolve().parents[2]
        model = json.loads((root / "work/revising-workbench/engineering-model.json").read_text())
        spec = json.loads((root / "work/revising-workbench/spec.json").read_text())
        tasks = (root / "work/revising-workbench/inner-loop/tasks.yaml").read_text()
        accepted = json.loads((root / "work/revising-workbench/traceability-accepted.json").read_text())
        self.assertEqual(model["work_id"], "revising-workbench")
        self.assertEqual(spec["work_id"], model["work_id"])
        self.assertIn("work_id: revising-workbench", tasks)
        self.assertEqual(accepted["work_id"], model["work_id"])
        self.assertEqual(accepted["plan_review"]["decision"], "APPROVED")
        self.assertNotEqual(accepted["contract_sha"], "70dd295aacff869857081a94870d02fcbf4d640c")

    def test_retained_WB003_observation_is_genuine_and_authority_checked(self):
        from engineering_model.workbench_evidence import execution_history

        root = Path(os.environ.get("ASK_RWB_RETAINED_ROOT", Path(__file__).resolve().parents[2])).resolve()
        work = root / "work/structured-agentic-environment"
        result_path = work / "inner-loop/results/WB-003.json"
        state_path = work / "inner-loop/state.json"
        result = json.loads(result_path.read_text())
        state = json.loads(state_path.read_text())
        task = state["tasks"]["WB-003"]
        review = task["evidence"]["review"]
        self.assertEqual(result["candidate_sha"], "70dd295aacff869857081a94870d02fcbf4d640c")
        self.assertEqual(review["candidate_sha"], result["candidate_sha"])
        self.assertEqual(review["verdict"], "APPROVED")
        self.assertEqual(task["evidence"]["verification"]["result"], "pass")
        self.assertEqual(task["evidence"]["verification"]["result_digest"], review["result_digest"])
        plan = json.loads((work / "test-plan.json").read_text())
        selected_test = next(test for test in plan["tests"] if test["id"] == "WB-evidence-identity")
        observed = execution_history(root, "structured-agentic-environment", selected_test,
                                     spec_digest="f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb",
                                     plan_digest="4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8",
                                     candidate_sha=result["candidate_sha"])
        matches = [row for row in observed["runs"]
                   if row.get("run_id") == "799924ec199b4717a3eabf4fb39a1bdc"]
        self.assertEqual(observed["status"], "available", observed)
        self.assertEqual(len(matches), 1, observed)
        self.assertEqual(matches[0]["outcome"], "passed")
        self.assertEqual(matches[0]["output_status"], "valid")
        self.assertEqual(matches[0]["source_status"], "historical")

    def test_representative_passage_dependencies_require_exact_baseline_context(self):
        from engineering_model.passages import required_task_passages
        from engineering_model.snapshot import capture

        root = Path(__file__).resolve().parents[2]
        snapshot = capture(root, "revising-workbench")
        self.assertEqual(snapshot.diagnostics(root), [])
        self.assertEqual(required_task_passages(snapshot, "inspect-genuine-wb003"), [])
        spec = snapshot.resolve_passage("inspect-genuine-wb003", "spec")
        plan = snapshot.resolve_passage("inspect-genuine-wb003", "plan")
        self.assertEqual((spec["state"], plan["state"]), ("available", "available"))
        self.assertIn("Projections and evidence", spec["text"])
        self.assertIn("WB-003", plan["text"])

    def test_public_migration_entry_is_available_without_implicit_conversion(self):
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run([str(root / "ask"), "model", "--help"], cwd=root,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("migrate", result.stdout)


if __name__ == "__main__":
    unittest.main()
