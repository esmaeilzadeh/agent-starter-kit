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
from workflow_refs.project import capture_project, load_project_graph, validate_capture


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
        candidate = consumer.candidate

        def refused(label):
            result = consumer.command("traceability", "check-completion", "e2e",
                                      "--candidate-sha", candidate,
                                      "--anchor-sha", candidate)
            self.assertNotEqual(result.returncode, 0, label)
            self.assertIn("fail", result.stdout + result.stderr, label)
            return result

        report = json.loads(completion_path.read_text())
        log = consumer.root / report["execution_artifacts"][0]
        log_bytes = log.read_bytes()
        log.write_bytes(log_bytes + b"tampered\n")
        refused("changed execution log")
        log.write_bytes(log_bytes)

        review_path = consumer.root / "work/e2e/traceability/reviews" / f"{candidate}.json"
        review_bytes = review_path.read_bytes()
        review_path.write_text("{}\n")
        refused("invalid independent review")
        review_path.write_bytes(review_bytes)

        accepted_path = consumer.root / "work/e2e/traceability-accepted.json"
        accepted_bytes = accepted_path.read_bytes()
        accepted = json.loads(accepted_bytes)
        accepted["recorded_by"] = "forged-candidate"
        accepted_path.write_text(json.dumps(accepted) + "\n")
        refused("stale or substituted accepted contract")
        accepted_path.write_bytes(accepted_bytes)

        plan_path = consumer.root / "work/e2e/test-plan.json"
        plan_bytes = plan_path.read_bytes()
        plan = json.loads(plan_bytes)
        plan["obligations"][0]["required_types"].append("integration")
        plan_path.write_text(json.dumps(plan) + "\n")
        refused("substituted obligation manifest")
        plan_path.write_bytes(plan_bytes)

        plan = json.loads(plan_bytes)
        plan["runners"][0]["argv"] = ["python3", "-m", "unittest", "missing_runner"]
        plan_path.write_text(json.dumps(plan) + "\n")
        refused("substituted runner declaration")
        plan_path.write_bytes(plan_bytes)

        source_path = consumer.root / "app.py"
        source_bytes = source_path.read_bytes()
        source_path.write_bytes(source_bytes + b"\n# altered candidate source\n")
        refused("altered candidate source")
        source_path.write_bytes(source_bytes)

        adapter_path = consumer.root / ".agents/ask/verification/traceability/unittest_runner.py"
        adapter_bytes = adapter_path.read_bytes()
        adapter_path.write_bytes(adapter_bytes + b"\n# substituted runner object\n")
        refused("altered runner object")
        adapter_path.write_bytes(adapter_bytes)

        run_id = Path(report["execution_artifacts"][0]).parts[-2]
        run_report = consumer.root / "work/e2e/traceability/runs" / run_id / "results.json"
        report_bytes = run_report.read_bytes()
        run_report.unlink()
        refused("missing retained execution object")
        run_report.write_bytes(report_bytes)

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
            status_code, status = repo.cli("status", reference)
            self.assertEqual(status_code, 0)
            self.assertEqual(status["reference"], reference)

        # Migrate an actual legacy name from its retained source commit without
        # rewriting the original document or dropping its historical mapping.
        legacy_source = repo.root / "work/demo/items.json"
        migration = repo.root / "work/demo/references/migration.json"
        migration.write_text(json.dumps({"schema": "ask-reference-migration/v1", "owner": "demo",
            "mappings": [{"legacy_reference": "legacy-plan-42",
                          "logical_id": "demo/spec/9/plan/9/item/9",
                          "snapshot": {"commit": repo.source_sha, "path": "work/demo/items.json"},
                          "item_id": "plan-item", "profile": "structured-item/1"}]}))
        repo.git("add", "work/demo/references/migration.json")
        repo.git("commit", "-qm", "declare exact legacy mapping")
        original_bytes = legacy_source.read_bytes()
        code, migrated = repo.cli("migrate", "demo")
        self.assertEqual(code, 0, migrated)
        self.assertEqual(migrated["mappings"][0]["legacy_reference"], "legacy-plan-42")
        self.assertEqual(legacy_source.read_bytes(), original_bytes)
        code, legacy_projection = repo.cli("show", migrated["mappings"][0]["reference"])
        self.assertEqual(code, 0)
        migrated_item = next(entry for entry in legacy_projection["payload"]["items"]
                             if entry["id"] == "plan-item")
        self.assertEqual(migrated_item["value"], "old")

        # Keep an exact execution record and its log in the immutable Git closure.
        run_ref = repo.register_execution({"id": "run-17", "inputs": [],
            "candidate_sha": repo.source_sha, "result": "pass", "log": "results/runs/run-17.log"},
            logical_id="repository-runs/run/17",
            artifacts={"results/runs/run-17.log": b"run-17: pass\n"})
        code, run_projection = repo.cli("show", run_ref)
        self.assertEqual(code, 0, run_projection)
        run_record = next(entry for entry in run_projection["payload"]["items"]
                          if entry["id"] == "run-17")
        self.assertEqual(run_record["candidate_sha"], repo.source_sha)
        self.assertEqual((repo.root / "results/runs/run-17.log").read_bytes(), b"run-17: pass\n")
        run_bundle = repo.root / "runs.refs"
        self.assertEqual(repo.cli("export", "repository-runs", "--out", str(run_bundle))[0], 0)
        self.assertTrue(repo.cli("import", str(run_bundle))[1]["idempotent"])
        run_projection = repo.cli("show", run_ref)[1]
        run_record = next(entry for entry in run_projection["payload"]["items"]
                          if entry["id"] == "run-17")
        self.assertEqual(run_record["candidate_sha"], repo.source_sha)

        bundle = repo.root / "transfer.refs"
        code, exported = repo.cli("export", "demo", "--out", str(bundle))
        self.assertEqual(code, 0)
        self.assertEqual(exported["status"], "exported")
        self.assertTrue(repo.cli("import", str(bundle))[1]["idempotent"])

        clone = repo.root.parent / (repo.root.name + "-clone")
        self.addCleanup(shutil.rmtree, clone, True)
        repo.git("clone", "-q", str(repo.root), str(clone))
        self.assertNotEqual(repo.cli_at(clone, "import", str(bundle))[0], 0)

        # A clone without authority must not invent either a legacy mapping or
        # historical execution just because a bundle has been offered.
        self.assertNotEqual(repo.cli_at(clone, "show", run_ref)[0], 0)
        self.assertNotEqual(repo.cli_at(clone, "import", str(run_bundle))[0], 0)

        # Tampering with the manifest is rejected before any authority is installed.
        import zipfile
        altered = repo.root / "altered.refs"
        with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(altered, "w") as target:
            for name in source.namelist():
                data = source.read(name)
                if name == "catalog.json":
                    data += b" "
                target.writestr(name, data)
        code, refusal = repo.cli("import", str(altered))
        self.assertNotEqual(code, 0)
        self.assertIn("does not match its manifest", refusal["detail"])

    def test_partial_impact_and_retained_execution(self):
        self._assert_public_impact_uses_persisted_decisions_and_blocks_unresolved_input()

    def _assert_public_impact_uses_persisted_decisions_and_blocks_unresolved_input(self):
        s1 = item("alpha/spec/1", "requirement-one", value="old")
        p1 = item("alpha/spec/1/plan/1/item/1", "plan-one",
                  [{"reference": "alpha/spec/1@1", "role": "requirement"}], value="old")
        task = item("beta/spec/1/plan/1/task/1", "task-one", [
            {"reference": "alpha/spec/1/plan/1/item/1@1", "role": "plan"},
            {"reference": "shared/spec/1@1", "role": "policy"}])
        test = item("beta/spec/1/plan/1/task/1/test/1", "test-one", [
            {"reference": "beta/spec/1/plan/1/task/1@1", "role": "task"}])
        # A separate unchanged requirement/plan/task chain remains in the graph
        # while only alpha's selected bindings change.
        s2 = item("independent/spec/2", "requirement-two")
        p4 = item("independent/spec/2/plan/4/item/1", "plan-four",
                  [{"reference": "independent/spec/2@1", "role": "requirement"}])
        t4 = item("independent/spec/2/plan/4/task/4", "task-four", [
            {"reference": "independent/spec/2/plan/4/item/1@1", "role": "plan"}])
        policy = item("shared/spec/1", "policy", value="policy-v1")
        repo = self.make_repo({"alpha": [s1, p1], "beta": [task, test],
                               "independent": [s2, p4, t4], "shared": [policy]})
        source = capture_project(repo.root, shared_owners={"shared"})

        s1_new = item("alpha/spec/1", "requirement-one", value="new", version=2)
        p1_new = item("alpha/spec/1/plan/1/item/1", "plan-one",
                      [{"reference": "alpha/spec/1@2", "role": "requirement"}],
                      value="new", version=2)
        repo.publish_items("alpha", [s1_new, p1_new])
        candidate = capture_project(repo.root, shared_owners={"shared"})
        self.assertEqual(candidate["status"], "complete")
        source_path = repo.root / "source-capture.json"
        candidate_path = repo.root / "candidate-capture.json"
        source_path.write_text(json.dumps(source))
        candidate_path.write_text(json.dumps(candidate))

        def decision(action, old_upstream, new_upstream, dependent, required_paths,
                     examined_paths, new_dependent, eligible=(), outward=False,
                     satisfies=False, reuse=False):
            return {"action": action, "old_upstream": old_upstream,
                    "new_upstream": new_upstream, "dependent": dependent,
                    "profile": "structured-item/1", "context_generation": candidate["generation"],
                    "examined_paths": examined_paths,
                    "review_evidence": "review/independent-impact-assessment",
                    "reviewer": "independent-reviewer", "coordinator": "owner-coordinator",
                    "outward_equal": outward, "satisfies_new_inputs": satisfies,
                    "reuse_allowed": reuse, "required_paths": required_paths,
                    "eligible_consumers": list(eligible), "new_dependent": new_dependent,
                    "retirement_safe": False}

        decisions = [
            decision("revise", "alpha/spec/1@1", "alpha/spec/1@2",
                     "alpha/spec/1/plan/1/item/1@1",
                     ["alpha/spec/1@1|requirement", "alpha/spec/1@2|requirement"],
                     {"alpha/spec/1@1|requirement": "resolved",
                      "alpha/spec/1@2|requirement": "resolved"},
                     "alpha/spec/1/plan/1/item/1@2"),
            decision("retain", "alpha/spec/1/plan/1/item/1@1",
                     "alpha/spec/1/plan/1/item/1@2", "beta/spec/1/plan/1/task/1@1",
                     ["alpha/spec/1/plan/1/item/1@1|plan", "shared/spec/1@1|policy"],
                     {"alpha/spec/1/plan/1/item/1@1|plan": "unchanged",
                      "shared/spec/1@1|policy": "unchanged"},
                     "beta/spec/1/plan/1/task/1@1",
                     ["beta/spec/1/plan/1/task/1/test/1@1"], True, True, True)]
        decision_refs = []
        for index, value in enumerate(decisions):
            evidence = repo.root / f"decision-{index}.json"
            evidence.write_text(json.dumps(value))
            code, recorded = repo.cli("decide", "--evidence", str(evidence),
                                      "--recorded-by", "owner-coordinator",
                                      "--shared-owner", "shared")
            self.assertEqual(code, 0, recorded)
            decision_refs.append(recorded["reference"])
            current = capture_project(repo.root, shared_owners={"shared"})
            self.assertEqual(current["generation"], candidate["generation"])
            code, resolved = repo.cli("show", recorded["reference"])
            self.assertEqual(code, 0, resolved)
            self.assertEqual(resolved["payload"]["decision"], recorded["decision"]["decision"])

        # The decision catalog publication itself must not stale the exact graph
        # generation it names. Public impact follows trusted numeric references.
        code, impact = repo.cli("impact", "--source", str(source_path), "--candidate",
                               str(candidate_path), "--shared-owner", "shared",
                               "--decision", decision_refs[0], "--decision", decision_refs[1])
        self.assertEqual(code, 0, impact)
        self.assertEqual(impact["status"], "complete")
        self.assertEqual(impact["items"]["alpha/spec/1/plan/1/item/1@1"]["decision"]["status"], "revised")
        self.assertEqual(impact["items"]["beta/spec/1/plan/1/task/1@1"]["decision"]["status"], "retained")
        self.assertNotIn("independent/spec/2/plan/4/task/4@1", impact["items"])

        # Registered historical endpoints remain assessable after they become inactive.
        from unittest.mock import patch
        from workflow_refs.project import load_project_graph
        real_load_graph = load_project_graph
        old_endpoint = decisions[0]["dependent"]
        def with_inactive_history(root, project_capture):
            graph = real_load_graph(root, project_capture)
            graph["nodes"][old_endpoint]["active"] = False
            return graph
        with patch("workflow_refs.project.load_project_graph", side_effect=with_inactive_history), \
             patch("workflow_refs.cli.load_project_graph", side_effect=with_inactive_history):
            code, historical = repo.cli("impact", "--source", str(source_path), "--candidate",
                str(candidate_path), "--shared-owner", "shared",
                "--decision", decision_refs[0], "--decision", decision_refs[1])
        self.assertEqual(code, 0, historical)
        self.assertEqual(historical["status"], "complete")

        unresolved = decision("retain", "alpha/spec/1/plan/1/item/1@1",
            "alpha/spec/1/plan/1/item/1@2", "beta/spec/1/plan/1/task/1@1",
            ["alpha/spec/1/plan/1/item/1@1|plan", "shared/spec/1@1|policy"],
            {"alpha/spec/1/plan/1/item/1@1|plan": "unchanged",
             "shared/spec/1@1|policy": "changed"},
            "beta/spec/1/plan/1/task/1@1",
            ["beta/spec/1/plan/1/task/1/test/1@1"], True, True, True)
        evidence = repo.root / "decision-unresolved.json"
        evidence.write_text(json.dumps(unresolved))
        code, recorded = repo.cli("decide", "--evidence", str(evidence),
                                  "--recorded-by", "owner-coordinator",
                                  "--shared-owner", "shared")
        self.assertEqual(code, 0, recorded)
        code, impact = repo.cli("impact", "--source", str(source_path), "--candidate",
                               str(candidate_path), "--shared-owner", "shared",
                               "--decision", decision_refs[0], "--decision", recorded["reference"])
        self.assertEqual(code, 1, impact)
        self.assertEqual(impact["status"], "incomplete")
        self.assertIn("beta/spec/1/plan/1/task/1@1", impact["unresolved"])

        # A current completion still depends on a fresh execution of the exact
        # source candidate, even when the impact review itself is complete.
        consumer = CompletionRepository()
        self.addCleanup(consumer.close)
        old_candidate = consumer.candidate
        verified = consumer.command("verify")
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
        ledger_path = consumer.root / "work/e2e/traceability/executions.json"
        old_execution_ledger = ledger_path.read_bytes()
        (consumer.root / "verification-result.json").unlink(missing_ok=True)
        consumer.source_path = consumer.root / "app.py"
        consumer.source_path.write_text(
            consumer.source_path.read_text() + "\ndef newer_value(): return 'new'\n")
        consumer.git("add", "app.py")
        consumer.git("commit", "-qm", "publish a changed source candidate")
        new_candidate = consumer.git("rev-parse", "HEAD")
        consumer.candidate = new_candidate
        consumer.create_semantic_review()
        stale = consumer.command("traceability", "check-completion", "e2e",
                                 "--candidate-sha", new_candidate,
                                 "--anchor-sha", new_candidate)
        self.assertNotEqual(stale.returncode, 0, stale.stdout + stale.stderr)
        stale_result = json.loads(stale.stdout)
        self.assertEqual(stale_result.get("status"), "fail")
        self.assertEqual(stale_result.get("candidate_sha"), new_candidate)
        self.assertTrue(any("static-" + new_candidate in error
                            for error in stale_result.get("errors", [])))
        self.assertEqual(ledger_path.read_bytes(), old_execution_ledger)
        ledger = json.loads(old_execution_ledger)
        self.assertTrue(any(row.get("candidate_sha") == old_candidate
                            and row.get("phase") == "final_green" for row in ledger))
        self.assertFalse(any(row.get("candidate_sha") == new_candidate
                             and row.get("phase") == "final_green" for row in ledger))

    def test_shared_deletion_and_retirement(self):
        r1 = item("req-a/spec/1", "req-one")
        r2 = item("req-b/spec/1", "req-two")
        shared_test = item("tests/spec/1/plan/1/task/1/test/1", "shared-test", [
            {"reference": "req-a/spec/1@1", "role": "requirement"},
            {"reference": "req-b/spec/1@1", "role": "requirement"}])
        orphan = item("tests/spec/1/plan/2/task/2/test/2", "orphan-test", [
            {"reference": "req-a/spec/1@1", "role": "requirement"}])
        repo = self.make_repo({"req-a": [r1], "req-b": [r2], "tests": [shared_test, orphan]})
        baseline = capture_project(repo.root)
        source_path = repo.root / "source-capture.json"
        source_path.write_text(json.dumps(baseline))

        # Remove R1 from the candidate source, then assess its actual consumers
        # through the public command before publishing any consumer revision.
        repo.publish_items("req-a", [], register=False)
        candidate = capture_project(repo.root)
        candidate_path = repo.root / "candidate-capture.json"
        candidate_path.write_text(json.dumps(candidate))
        code, assessed = repo.cli("impact", "--source", str(source_path), "--candidate",
                                  str(candidate_path))
        self.assertEqual(code, 1, assessed)
        self.assertIn("req-a/spec/1@1", assessed["deletions"])
        self.assertIn("tests/spec/1/plan/1/task/1/test/1@1", assessed["items"])
        self.assertIn("tests/spec/1/plan/2/task/2/test/2@1", assessed["items"])

        def make_decision(action, dependent, paths, examined, new_dependent,
                          *, retirement_safe=False):
            return {"action": action, "old_upstream": "req-a/spec/1@1",
                    "new_upstream": "req-b/spec/1@1", "dependent": dependent,
                    "profile": "structured-item/1", "context_generation": candidate["generation"],
                    "examined_paths": examined, "review_evidence": "review/deletion-assessment",
                    "reviewer": "independent-reviewer", "coordinator": "owner-coordinator",
                    "outward_equal": False, "satisfies_new_inputs": action == "revise",
                    "reuse_allowed": False, "required_paths": paths, "eligible_consumers": [],
                    "new_dependent": new_dependent, "retirement_safe": retirement_safe}

        shared_ref = "tests/spec/1/plan/1/task/1/test/1"
        orphan_ref = "tests/spec/1/plan/2/task/2/test/2"
        shared_paths = ["req-a/spec/1@1|requirement", "req-b/spec/1@1|requirement"]
        shared_decision = make_decision("revise", shared_ref + "@1", shared_paths,
            {shared_paths[0]: "resolved", shared_paths[1]: "unchanged"}, shared_ref + "@2")
        orphan_path = "req-a/spec/1@1|requirement"
        orphan_decision = make_decision("retire", orphan_ref + "@1", [orphan_path],
            {orphan_path: "resolved"}, None, retirement_safe=True)
        decision_refs = []
        for index, decision_value in enumerate((shared_decision, orphan_decision)):
            evidence = repo.root / f"deletion-decision-{index}.json"
            evidence.write_text(json.dumps(decision_value))
            code, result = repo.cli("decide", "--evidence", str(evidence),
                                    "--recorded-by", "owner-coordinator")
            self.assertEqual(code, 0, result)
            decision_refs.append(result["reference"])
            self.assertEqual(repo.cli("show", result["reference"])[0], 0)

        # Publish the reviewed replacement and retirement as numeric history.
        shared_next = item(shared_ref, "shared-test",
            [{"reference": "req-b/spec/1@1", "role": "requirement"}], active=True, version=2)
        orphan_next = item(orphan_ref, "orphan-test", [], active=False, version=2)
        repo.publish_items("tests", [shared_next, orphan_next])
        shared_next_ref, orphan_next_ref = shared_ref + "@2", orphan_ref + "@2"
        self.assertEqual(repo.cli("show", shared_next_ref)[0], 0)
        retired_code, retired = repo.cli("show", orphan_next_ref)
        self.assertEqual(retired_code, 0, retired)
        retired_item = next(entry for entry in retired["payload"]["items"]
                            if entry["id"] == "orphan-test")
        self.assertFalse(retired_item["active"])
        # Both original revisions and the retained executable run remain readable.
        self.assertEqual(repo.cli("show", shared_ref + "@1")[0], 0)
        self.assertEqual(repo.cli("show", orphan_ref + "@1")[0], 0)
        run_ref = repo.register_execution({"id": "orphan-test-run", "inputs": [],
            "candidate_sha": repo.source_sha, "result": "pass"},
            logical_id="repository-runs/run/2")
        self.assertEqual(repo.cli("show", run_ref)[0], 0)

        latest = capture_project(repo.root)
        graph = load_project_graph(repo.root, latest)
        self.assertEqual(graph["status"], "complete", graph)
        self.assertTrue(graph["nodes"][shared_next_ref]["active"])
        self.assertFalse(graph["nodes"][orphan_next_ref]["active"])
        self.assertIn(shared_next_ref, graph["nodes"])
        self.assertIn(orphan_next_ref, graph["nodes"])
        # Public impact defaults exclude the retired item while retaining the
        # active shared executable and its exact historical dependency.
        latest_path = repo.root / "latest-capture.json"
        latest_path.write_text(json.dumps(latest))
        code, after = repo.cli("impact", "--source", str(candidate_path), "--candidate",
                              str(latest_path))
        self.assertEqual(code, 0, after)
        self.assertNotIn(orphan_next_ref, after["items"])
        self.assertEqual(len(decision_refs), 2)

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
        stale_source = repo.root / "stale-source.json"
        stale_source.write_text(json.dumps(capture))
        stale_candidate = repo.root / "stale-candidate.json"
        stale_candidate.write_text(json.dumps(capture))
        code, stale_result = repo.cli("impact", "--source", str(stale_source),
                                      "--candidate", str(stale_candidate),
                                      "--shared-owner", "policy")
        self.assertEqual(code, 1, stale_result)
        self.assertEqual(stale_result["status"], "incomplete")
        refreshed = capture_project(repo.root, shared_owners={"policy"})
        self.assertEqual(refreshed["status"], "complete")
        refreshed_graph = load_project_graph(repo.root, refreshed)
        self.assertEqual(refreshed_graph["status"], "incomplete")
        self.assertTrue(refreshed_graph.get("unresolved"))
        current = repo.root / "current-capture.json"
        current.write_text(json.dumps(refreshed))
        code, incomplete = repo.cli("impact", "--source", str(stale_source),
                                    "--candidate", str(current),
                                    "--shared-owner", "policy")
        self.assertEqual(code, 1, incomplete)
        self.assertEqual(incomplete["status"], "incomplete")
        self.assertTrue(incomplete.get("unresolved"))


if __name__ == "__main__":
    unittest.main()
