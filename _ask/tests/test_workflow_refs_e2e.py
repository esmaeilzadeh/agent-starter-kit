"""End-to-end checks across numeric references, project scope and public commands."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agents/ask"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from workflow_refs_fixture import CompletionRepository, ReferenceRepository, item
from workflow_refs.impact import assess_impact, record_decision
from workflow_refs.migration import import_bundle
from workflow_refs.project import capture_project, load_project_graph, validate_capture
from workflow_refs.store import CatalogError


class ReferenceTests(unittest.TestCase):
    def make_repo(self, owners):
        repo = ReferenceRepository(owners)
        self.addCleanup(repo.close)
        return repo

    def test_valid_and_tampered_completion(self):
        consumer = CompletionRepository()
        self.addCleanup(consumer.close)
        verified = consumer.command("verify")
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
        completion_path = consumer.root / "work/e2e/traceability/completion.json"
        self.assertEqual(json.loads(completion_path.read_text())["status"], "pass")

        report = json.loads(completion_path.read_text())
        log = consumer.root / report["execution_artifacts"][0]
        log_bytes = log.read_bytes()
        log.write_bytes(log_bytes + b"tampered\n")
        refused = consumer.command("traceability", "check-completion", "e2e",
                                  "--candidate-sha", consumer.candidate,
                                  "--anchor-sha", consumer.candidate)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("fail", refused.stdout + refused.stderr)
        log.write_bytes(log_bytes)

        review_path = consumer.root / "work/e2e/traceability/reviews" / f"{consumer.candidate}.json"
        review_bytes = review_path.read_bytes()
        review_path.write_text("{}\n")
        refused_review = consumer.command("traceability", "check-completion", "e2e",
                                          "--candidate-sha", consumer.candidate,
                                          "--anchor-sha", consumer.candidate)
        self.assertNotEqual(refused_review.returncode, 0)
        self.assertIn("fail", refused_review.stdout + refused_review.stderr)
        review_path.write_bytes(review_bytes)

        accepted_path = consumer.root / "work/e2e/traceability-accepted.json"
        accepted_bytes = accepted_path.read_bytes()
        accepted = json.loads(accepted_bytes)
        accepted["recorded_by"] = "forged-candidate"
        accepted_path.write_text(json.dumps(accepted) + "\n")
        refused_contract = consumer.command("traceability", "check-completion", "e2e",
                                            "--candidate-sha", consumer.candidate,
                                            "--anchor-sha", consumer.candidate)
        self.assertNotEqual(refused_contract.returncode, 0)
        self.assertIn("fail", refused_contract.stdout + refused_contract.stderr)
        accepted_path.write_bytes(accepted_bytes)

    def test_resume_and_export_historical_records(self):
        first = item("demo/spec/1/plan/1/item/1", "plan-item", value="old")
        second = item("demo/spec/1/plan/1/item/2", "task-item", value="current")
        repo = self.make_repo({"demo": [first, second]})
        for reference, item_id, value in (
                ("demo/spec/1/plan/1/item/1@1", "plan-item", "old"),
                ("demo/spec/1/plan/1/item/2@1", "task-item", "current")):
            code, projection = repo.cli("show", reference)
            self.assertEqual(code, 0)
            selected = next(payload for payload in projection["payload"]["items"]
                            if payload["id"] == item_id)
            self.assertEqual(selected["value"], value)

        bundle = repo.root / "transfer.refs"
        code, exported = repo.cli("export", "demo", "--out", str(bundle))
        self.assertEqual(code, 0)
        self.assertEqual(exported["status"], "exported")
        self.assertTrue(import_bundle(repo.root, bundle)["idempotent"])

        clone = repo.root.parent / (repo.root.name + "-clone")
        self.addCleanup(shutil.rmtree, clone, True)
        repo.git("clone", "-q", str(repo.root), str(clone))
        with self.assertRaisesRegex(CatalogError, "cannot establish or replace"):
            import_bundle(clone, bundle)

        # Tampering with the manifest is rejected before any authority is installed.
        import zipfile
        altered = repo.root / "altered.refs"
        with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(altered, "w") as target:
            for name in source.namelist():
                data = source.read(name)
                if name == "catalog.json":
                    data += b" "
                target.writestr(name, data)
        with self.assertRaisesRegex(CatalogError, "does not match its manifest"):
            import_bundle(repo.root, altered)

    def test_partial_impact_and_retained_execution(self):
        s1 = item("alpha/spec/1", "requirement-one")
        s2 = item("alpha/spec/2", "requirement-two")
        p1 = item("alpha/spec/1/plan/1/item/1", "plan-one",
                  [{"reference": "alpha/spec/1@1", "role": "requirement"}])
        p4 = item("alpha/spec/2/plan/4/item/1", "plan-four",
                  [{"reference": "alpha/spec/2@1", "role": "requirement"}])
        t1 = item("beta/spec/1/plan/1/task/1", "task-one", [
            {"reference": "alpha/spec/1/plan/1/item/1@1", "role": "plan"},
            {"reference": "shared/spec/1@1", "role": "shared-policy"}])
        t4 = item("beta/spec/2/plan/4/task/4", "task-four", [
            {"reference": "alpha/spec/2/plan/4/item/1@1", "role": "plan"}])
        test = item("beta/spec/1/plan/1/task/1/test/1", "test-one", [
            {"reference": "beta/spec/1/plan/1/task/1@1", "role": "task"}])
        policy = item("shared/spec/1", "policy", value="policy-v1")
        repo = self.make_repo({"alpha": [s1, s2, p1, p4], "beta": [t1, t4, test],
                               "shared": [policy]})
        capture = capture_project(repo.root, shared_owners={"shared"})
        graph = load_project_graph(repo.root, capture)
        self.assertEqual(capture["status"], "complete")
        self.assertEqual(graph["status"], "complete", graph)
        impact = assess_impact(graph, ["alpha/spec/1@1"], capture=capture,
                               repository_root=repo.root)
        self.assertEqual(impact["status"], "complete")
        self.assertIn("beta/spec/1/plan/1/task/1@1", impact["items"])
        self.assertNotIn("beta/spec/2/plan/4/task/4@1", impact["items"])

        dependent = "beta/spec/1/plan/1/task/1@1"
        required = ["alpha/spec/1/plan/1/item/1@1|plan", "shared/spec/1@1|shared-policy"]
        retained = record_decision({
            "action": "retain", "old_upstream": "alpha/spec/1@1",
            "new_upstream": "alpha/spec/1@2", "dependent": dependent,
            "profile": "structured-item/1", "context_generation": capture["generation"],
            "examined_paths": {required[0]: "unchanged", required[1]: "unchanged"},
            "review_evidence": "review/reviewed-impact", "reviewer": "independent-reviewer",
            "coordinator": "owner-coordinator", "outward_equal": True,
            "satisfies_new_inputs": True, "reuse_allowed": True,
            "required_paths": required,
            "eligible_consumers": ["beta/spec/1/plan/1/task/1/test/1@1"],
            "new_dependent": dependent, "retirement_safe": False,
        }, capture, required_paths=required, authority_check=lambda _d, _c: True)
        self.assertEqual(retained["status"], "retained")
        self.assertTrue(retained["propagation_stopped"])

        # A second affected input not resolved by the review keeps propagation open.
        unresolved = record_decision({
            "action": "retain", "old_upstream": "alpha/spec/1@1",
            "new_upstream": "alpha/spec/1@2", "dependent": dependent,
            "profile": "structured-item/1", "context_generation": capture["generation"],
            "examined_paths": {required[0]: "unchanged", required[1]: "changed"},
            "review_evidence": "review/partial-impact", "reviewer": "independent-reviewer",
            "coordinator": "owner-coordinator", "outward_equal": True,
            "satisfies_new_inputs": True, "reuse_allowed": True,
            "required_paths": required,
            "eligible_consumers": ["beta/spec/1/plan/1/task/1/test/1@1"],
            "new_dependent": dependent, "retirement_safe": False,
        }, capture, required_paths=required, authority_check=lambda _d, _c: True)
        self.assertEqual(unresolved["status"], "reassess")
        self.assertFalse(unresolved["propagation_stopped"])
        self.assertEqual(repo.cli("show", "beta/spec/1/plan/1/task/1/test/1@1")[0], 0)

    def test_shared_deletion_and_retirement(self):
        r1 = item("req-a/spec/1", "req-one")
        r2 = item("req-b/spec/1", "req-two")
        shared_test = item("tests/spec/1/plan/1/task/1/test/1", "shared-test", [
            {"reference": "req-a/spec/1@1", "role": "requirement"},
            {"reference": "req-b/spec/1@1", "role": "requirement"}])
        orphan = item("tests/spec/1/plan/2/task/2/test/2", "orphan-test", [
            {"reference": "req-a/spec/1@1", "role": "requirement"}])
        repo = self.make_repo({"req-a": [r1], "req-b": [r2], "tests": [shared_test, orphan]})
        capture = capture_project(repo.root)
        graph = load_project_graph(repo.root, capture)
        self.assertEqual(graph["status"], "complete", graph)
        shared_required = ["req-b/spec/1@1|requirement"]
        shared_revision = record_decision({
            "action": "revise", "old_upstream": "req-a/spec/1@1",
            "new_upstream": "req-b/spec/1@1",
            "dependent": "tests/spec/1/plan/1/task/1/test/1@1",
            "profile": "structured-item/1", "context_generation": capture["generation"],
            "examined_paths": {shared_required[0]: "resolved"},
            "review_evidence": "review/shared-test-revision", "reviewer": "reviewer",
            "coordinator": "coordinator", "outward_equal": False,
            "satisfies_new_inputs": True, "reuse_allowed": False,
            "required_paths": shared_required, "eligible_consumers": [],
            "new_dependent": "tests/spec/1/plan/1/task/1/test/1@2", "retirement_safe": False,
        }, capture, required_paths=shared_required, authority_check=lambda _d, _c: True)
        self.assertEqual(shared_revision["status"], "revised")
        self.assertEqual(shared_revision["active_status"], "active")

        orphan_decision = record_decision({
            "action": "retire", "old_upstream": "req-a/spec/1@1",
            "new_upstream": "req-b/spec/1@1",
            "dependent": "tests/spec/1/plan/2/task/2/test/2@1",
            "profile": "structured-item/1", "context_generation": capture["generation"],
            "examined_paths": {"req-a/spec/1@1|requirement": "resolved"},
            "review_evidence": "review/orphan-retirement", "reviewer": "reviewer",
            "coordinator": "coordinator", "outward_equal": False,
            "satisfies_new_inputs": False, "reuse_allowed": False,
            "required_paths": ["req-a/spec/1@1|requirement"], "eligible_consumers": [],
            "new_dependent": None, "retirement_safe": True,
        }, capture, required_paths=["req-a/spec/1@1|requirement"],
           authority_check=lambda _d, _c: True)
        self.assertEqual(orphan_decision["status"], "retired")
        self.assertEqual(orphan_decision["active_status"], "retired")
        self.assertEqual(repo.cli("show", "tests/spec/1/plan/1/task/1/test/1@1")[0], 0)
        self.assertEqual(repo.cli("show", "tests/spec/1/plan/2/task/2/test/2@1")[0], 0)

    def test_multi_owner_incomplete_and_scope_freshness(self):
        shared = item("policy/spec/1", "shared-policy", value="v1")
        alpha = item("alpha/spec/1/plan/1/task/1", "same-local-number", [
            {"reference": "policy/spec/1@1", "role": "shared-policy"}])
        beta = item("beta/spec/1/plan/1/task/1", "same-local-number", [
            {"reference": "policy/spec/1@1", "role": "shared-policy"}])
        repo = self.make_repo({"alpha": [alpha], "beta": [beta], "policy": [shared]})
        capture = capture_project(repo.root, shared_owners={"policy"})
        graph = load_project_graph(repo.root, capture)
        self.assertEqual(capture["status"], "complete")
        self.assertEqual(graph["status"], "complete", graph)
        self.assertIn("alpha/spec/1/plan/1/task/1@1", graph["nodes"])
        self.assertIn("beta/spec/1/plan/1/task/1@1", graph["nodes"])
        self.assertEqual(graph["nodes"]["alpha/spec/1/plan/1/task/1@1"]["owner"], "alpha")
        self.assertEqual(graph["nodes"]["beta/spec/1/plan/1/task/1@1"]["owner"], "beta")

        # Publishing another owner after capture invalidates that captured scope.
        repo.git("update-ref", "refs/heads/agent/new-owner", repo.source_sha)
        self.assertEqual(validate_capture(repo.root, capture)["reason"], "stale_inventory")
        refreshed = capture_project(repo.root, shared_owners={"policy"})
        self.assertEqual(refreshed["status"], "complete")
        refreshed_graph = load_project_graph(repo.root, refreshed)
        self.assertEqual(refreshed_graph["status"], "incomplete")
        self.assertTrue(refreshed_graph.get("unresolved"))


if __name__ == "__main__":
    unittest.main()
