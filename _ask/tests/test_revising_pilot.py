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

    def test_reviewed_adoption_preserves_v1_identity_references_and_evidence(self):
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
                                                        "changed_records": [],
                                                        "changed_edges": {"removed": [], "added": []}})
        bad = copy.deepcopy(self.target)
        bad["nodes"][1]["reference"]["id"] = "C-2"
        with self.assertRaisesRegex(ValueError, "reference"):
            review_migration(self.source, bad, approved, work_id="pilot")
        bad_field = copy.deepcopy(self.target)
        bad_field["nodes"][1]["title"] = "Rewritten historical evidence"
        approved_field = dict(approved, target_digest=digest(bad_field),
                             diff_digest=digest(preservation_diff(self.source, bad_field)))
        with self.assertRaisesRegex(ValueError, "historical node fields"):
            review_migration(self.source, bad_field, approved_field, work_id="pilot")

        root = Path(__file__).resolve().parents[2]
        historical = json.loads((root / "work/structured-agentic-environment/engineering-model.json").read_text())
        proposal = copy.deepcopy(historical)
        proposal.update(schema="ask-engineering-model/v2", revision=historical["revision"] + 1)
        documented = {"schema": "ask-engineering-migration-review/v1", "decision": "APPROVED",
                      "reviewer": "Codex implementation review",
                      "rationale": "The schema/revision-only proposal preserves all historical node fields, IDs, references, and edges; the source remains unchanged.",
                      "source_digest": "7a6f3b223df36df5202e5890d870f7db23cc5a552bce7564b383d277b619a341",
                      "target_digest": "74cf6e0bb282aaedf191bd969d86e7778a2c75213ca852a6eda4bf2b3e971bfc",
                      "diff_digest": "9fa1e5f96eaa32b5cd8918c576ea272c56580929a4437c7fdbd9bfb5c3e813a7"}
        self.assertEqual(review_migration(historical, proposal, documented,
                                          work_id="structured-agentic-environment")["status"], "approved")
        self.assertEqual(json.loads((root / "work/structured-agentic-environment/engineering-model.json").read_text()),
                         historical)

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

    def test_new_work_requires_own_spec_graph_review_and_accepted_contract(self):
        PilotIntegrationTests().test_new_work_requires_its_own_spec_graph_review_and_accepted_contract()

    def test_migration_passage_dependencies_use_real_guarded_entry(self):
        PilotIntegrationTests().test_migration_passages_use_the_real_guarded_entry()


class ReadabilityTests(unittest.TestCase):
    def test_each_answer_and_changed_dependency_control_comprehension_validity(self):
        from engineering_model.readability import validate_record

        expected = {"candidate_sha": "a" * 40, "snapshot_digest": "b" * 64,
                    "task": {"work_id": "w", "node_id": "task"},
                    "scenario": {"work_id": "w", "node_id": "scenario"},
                    "test": {"work_id": "w", "test_id": "WB-1", "case_id": "test_case"},
                    "dependencies": {"inspected_sources": {"candidate_sha": "c" * 40},
                                     "spec": {"selector_digest": "d" * 64, "bytes_digest": "e" * 64},
                                     "plan": {"selector_digest": "f" * 64, "bytes_digest": "1" * 64},
                                     "test": {"source_digest": "2" * 64},
                                     "helpers": {"source_digests": ["3" * 64]},
                                     "fixtures": {"source_digests": ["4" * 64]},
                                     "evidence": {"report_digest": "5" * 64, "log_digests": ["6" * 64],
                                                  "contract_digest": "7" * 64, "review_digest": "8" * 64}}}
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
        stale_deps = copy.deepcopy(expected["dependencies"])
        stale_deps["helpers"]["source_digests"] = ["9" * 64]
        stale = dict(expected, dependencies=stale_deps)
        self.assertEqual(validate_record(record, stale)["status"], "stale")
        incomplete_deps = copy.deepcopy(expected["dependencies"])
        del incomplete_deps["evidence"]
        incomplete = dict(expected, dependencies=incomplete_deps)
        self.assertEqual(validate_record(record, incomplete)["status"], "invalid")
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
        from engineering_model.passages import resolve
        from engineering_model.readable_tests import read_test
        from engineering_model.workbench_evidence import execution_history, qualified_source

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
        result_raw = result_path.read_bytes()
        self.assertEqual(hashlib.sha256(result_raw).hexdigest(), review["result_digest"])
        review_evidence = root / review["evidence"]
        self.assertEqual(hashlib.sha256(review_evidence.read_bytes()).hexdigest(), review["evidence_digest"])
        checks = task["evidence"]["verification"]["checks"]
        self.assertTrue(checks)
        for check in checks:
            self.assertEqual((check["status"], check["exit_code"]), ("pass", 0))
            artifact = root / check["evidence"]
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), check["output_digest"])
        test_review_path = work / "traceability/reviews/70dd295aacff869857081a94870d02fcbf4d640c.json"
        test_review_envelope = json.loads(test_review_path.read_text())
        test_review = test_review_envelope["review"]
        self.assertEqual(test_review_envelope["review_digest"], digest(test_review))
        self.assertEqual((test_review["decision"], test_review["candidate_sha"],
                          test_review["scope"], test_review["task_id"]),
                         ("APPROVED", result["candidate_sha"], "task", "WB-003"))
        self.assertEqual(test_review["spec_digest"],
                         "f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb")
        self.assertEqual(test_review["plan_digest"],
                         "4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8")
        self.assertIn("WB-evidence-identity", test_review["test_ids"])
        plan = json.loads((work / "test-plan.json").read_text())
        selected_test = next(test for test in plan["tests"] if test["id"] == "WB-evidence-identity")
        current_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                     capture_output=True, text=True).stdout.strip()
        source = qualified_source(root, selected_test, result["candidate_sha"], current_sha=current_sha)
        self.assertEqual(source["status"], "historical")
        self.assertIn("test_results_match_work_test_run_and_contract", source["source"])
        readable = read_test(root, selected_test, result["candidate_sha"], current_sha=current_sha)
        self.assertEqual(readable["status"], "historical")
        self.assertEqual(readable["context_status"], "complete")
        selectors = {entry["selector"] for entry in readable["context"]}
        self.assertTrue({"WorkbenchTests.setUp", "WorkbenchTests._report", "WorkbenchTests._ledger",
                         "WorkbenchTests._blob_digest", "WorkbenchTests.git", "WorkbenchTests.write",
                         "WorkbenchTests.commit"} <= selectors)
        second_spec = resolve("specs/current/structured-agentic-environment.md",
                              (root / "specs/current/structured-agentic-environment.md").read_bytes(),
                              {"kind": "heading", "path": [
                                  "Specification: Engineering Model and local workbench", "Interactive UI"]})
        self.assertEqual(second_spec["state"], "available")
        self.assertIn("The workbench presents", second_spec["text"])
        concrete_flow = next(test for test in plan["tests"] if test["id"] == "WB-evidence-identity")
        self.assertEqual(concrete_flow["case_id"],
                         "test_engineering_workbench_evidence.WorkbenchTests.test_results_match_work_test_run_and_contract")
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
        from engineering_model.readability import demo_gate
        from engineering_model.snapshot import capture

        root = Path(__file__).resolve().parents[2]
        snapshot = capture(root, "revising-workbench")
        self.assertEqual(snapshot.diagnostics(root), [])
        gate = demo_gate(root, snapshot, "inspect-genuine-wb003",
                         expected_snapshot_digest=snapshot.identity["digest"],
                         retained_root=os.environ.get("ASK_RWB_RETAINED_ROOT", root))
        self.assertEqual(gate["status"], "context_ready")
        self.assertFalse(gate["demo_complete"])
        self.assertEqual(gate["prerequisites"], [
            {"id": "genuine_retained_result", "status": "identity_verified_authority_not_evaluated"},
            {"id": "human_comprehension", "status": "not_recorded"}])
        self.assertEqual(gate["admission_identities"]["canonical_flow"], {
            "work_id": "structured-agentic-environment",
            "plan_digest": "f2893d132abb68dc94d735bdad8ff8d41a981e6f7a131ff865d327945876bf7b",
            "case_id": "WB-evidence-identity",
            "executable_case_id": "test_engineering_workbench_evidence.WorkbenchTests.test_results_match_work_test_run_and_contract"})
        self.assertEqual(gate["admission_identities"]["evidence_identities"]["run_id"],
                         "799924ec199b4717a3eabf4fb39a1bdc")
        with self.assertRaises(TypeError):
            demo_gate(root, snapshot, "inspect-genuine-wb003", admission={"report_digest": "f" * 64})
        spec = next(row["resolution"] for row in snapshot.passages.values()
                    if row.get("node_id") == "inspect-genuine-wb003" and row.get("role") == "spec"
                    and row["resolution"].get("selector", {}).get("path", [])[-1:] == ["Projections and evidence"])
        plan = snapshot.resolve_passage("inspect-genuine-wb003", "plan")
        self.assertEqual((spec["state"], plan["state"]), ("available", "available"))
        self.assertIn("Projections and evidence", spec["text"])
        self.assertIn("WB-003", plan["text"])

        stale = demo_gate(root, snapshot, "inspect-genuine-wb003", expected_snapshot_digest="0" * 64,
                          retained_root=os.environ.get("ASK_RWB_RETAINED_ROOT", root))
        self.assertEqual(stale["status"], "blocked_context")

        from engineering_model.snapshot import capture
        missing_model = copy.deepcopy(snapshot.document)
        missing_model["nodes"][2]["context"][0]["path"] = "specs/current/missing.md"
        missing = capture(root, "revising-workbench", overrides={
            snapshot.model_path: json.dumps(missing_model).encode("utf-8")})
        self.assertEqual(demo_gate(root, missing, "inspect-genuine-wb003")["status"], "blocked_context")

        spec_path = "specs/current/structured-agentic-environment.md"
        duplicate_spec = (root / spec_path).read_bytes() + b"\n## Projections and evidence\nDuplicate section.\n"
        ambiguous = capture(root, "revising-workbench", overrides={spec_path: duplicate_spec})
        self.assertEqual(demo_gate(root, ambiguous, "inspect-genuine-wb003")["status"], "blocked_context")

        model = copy.deepcopy(snapshot.document)
        model["nodes"][2]["context"][0]["path"] = "../outside.md"
        unsafe = capture(root, "revising-workbench", overrides={
            snapshot.model_path: json.dumps(model).encode("utf-8")})
        self.assertEqual(demo_gate(root, unsafe, "inspect-genuine-wb003")["status"], "blocked_context")

    def test_public_migration_entry_is_available_without_implicit_conversion(self):
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run([str(root / "ask"), "model", "--help"], cwd=root,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("migrate", result.stdout)


class RepresentativeTests(unittest.TestCase):
    def test_required_retained_wb003_result_is_genuine_and_historically_applicable(self):
        PilotIntegrationTests().test_retained_WB003_observation_is_genuine_and_authority_checked()

    def test_required_passages_gate_demo_without_fabricated_success(self):
        PilotIntegrationTests().test_representative_passage_dependencies_require_exact_baseline_context()


if __name__ == "__main__":
    unittest.main()
