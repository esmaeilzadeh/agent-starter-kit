"""Integrity-aware result and qualified-source inspection for the workbench."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from engineering_model.workbench_evidence import execution_history, qualified_source


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Workbench test")
        self.write("test_sample.py", "class First:\n    def test_same(self):\n        return 'first-v1'\n\nclass Second:\n    def test_same(self):\n        return 'second-v1'\n")
        self.write("src/app.py", "VALUE = 'old'\n")
        self.source_sha = self.commit("initial qualified source")
        self.write("test_sample.py", "class First:\n    def test_same(self):\n        return 'first-v2'\n\nclass Second:\n    def test_same(self):\n        return 'second-v2'\n")
        self.write("src/app.py", "VALUE = 'new'\n")
        self.candidate_sha = self.commit("updated current sources")
        self.runtime = self.root / "work/w/traceability"
        self.runtime.mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def test_qualified_source_matches_selected_revision(self):
        test = {"id": "T", "runner_id": "python", "case_id": "test_sample.Second.test_same",
                "source_paths": ["test_sample.py"]}
        historical = qualified_source(self.root, test, self.source_sha,
                                      current_sha=self.candidate_sha)
        self.assertEqual(historical["status"], "historical", historical)
        self.assertEqual(historical["selector"], "test_sample.Second.test_same")
        self.assertIn("return 'second-v1'", historical["source"])
        self.assertNotIn("first-v1", historical["source"])
        self.assertEqual(historical["source_sha"], self.source_sha)
        self.assertEqual(historical["current_sha"], self.candidate_sha)
        current = qualified_source(self.root, test, self.candidate_sha,
                                   current_sha=self.candidate_sha)
        self.assertEqual(current["status"], "current", current)
        self.assertIn("return 'second-v2'", current["source"])
        self.assertEqual(qualified_source(self.root, test, "0" * 40)["status"], "unavailable")
        unsafe = dict(test, source_paths=["../outside.py"])
        self.assertEqual(qualified_source(self.root, unsafe, self.source_sha)["status"], "unavailable")

    def _report(self, *, test_id="T", work_id="w", run_id="run-1", contract="contract-1",
                outcome="passed", log=b"assertion succeeded\n", source_sha=None,
                candidate_sha=None):
        source_sha = source_sha or self.candidate_sha
        candidate_sha = candidate_sha or self.candidate_sha
        artifact = f"work/{work_id}/traceability/runs/{run_id}/execution.log"
        log_path = self.root / artifact
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_bytes(log)
        output_digest = hashlib.sha256(log).hexdigest()
        execution = {"id": "exec-1", "runner_id": "python", "phase": "final_green",
                     "source_sha": source_sha, "exit_code": 0 if outcome == "passed" else 1,
                     "collection_status": "ok", "output_artifact": artifact,
                     "output_digest": output_digest}
        case = {"test_id": test_id, "runner_id": "python",
                "case_id": "test_sample.First.test_same", "execution_id": "exec-1",
                "phase": "final_green", "source_sha": source_sha,
                "source_digests": {"test_sample.py": self._blob_digest(source_sha, "test_sample.py")},
                "outcome": outcome, "failure_kind": None, "output_artifact": artifact,
                "output_digest": output_digest}
        report = {"schema": "ask-test-results/v1", "run_id": run_id,
                  "candidate_sha": candidate_sha, "spec_digest": "spec-1",
                  "scope": "task", "task_id": "WB-003",
                  "plan_digest": contract, "runner_identity": {"capability": "ask-traceability/v1"},
                  "executions": [execution], "cases": [case]}
        run_dir = self.runtime / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "results.json").write_text(json.dumps(report, sort_keys=True), encoding="utf-8")
        return report

    def _blob_digest(self, sha, path):
        blob = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=self.root,
                              check=True, capture_output=True).stdout
        return hashlib.sha256(blob).hexdigest()

    def _ledger(self, report, *, work_id="w", test_id="T", contract="contract-1"):
        path = self.runtime / "executions.json"
        ledger = json.loads(path.read_text()) if path.exists() else []
        ledger.append({"work_id": work_id, "run_id": report["run_id"], "phase": "final_green",
                       "candidate_sha": report["candidate_sha"], "spec_digest": "spec-1",
                       "plan_digest": contract, "scope": "task", "task_id": "WB-003",
                       "digest": hashlib.sha256(json.dumps(report, sort_keys=True,
                           separators=(",", ":")).encode()).hexdigest(), "test_id": test_id})
        path.write_text(json.dumps(ledger), encoding="utf-8")

    def test_results_match_work_test_run_and_contract(self):
        expected = {"id": "T", "runner_id": "python", "case_id": "test_sample.First.test_same",
                    "source_paths": ["test_sample.py"]}
        report = self._report()
        self._ledger(report)
        rows = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                 plan_digest="contract-1", candidate_sha=self.candidate_sha)
        self.assertEqual(rows["status"], "available", rows)
        self.assertEqual(len(rows["runs"]), 1)
        self.assertEqual(rows["runs"][0]["test_id"], "T")
        self.assertEqual(rows["runs"][0]["run_id"], "run-1")
        self.assertEqual(rows["runs"][0]["outcome"], "passed")
        self.assertEqual(rows["completion"], "not_evaluated",
                         "a case pass is not a workstream completion verdict")
        output = self.root / rows["runs"][0]["output_artifact"]
        self.assertEqual(output.read_text(), "assertion succeeded\n")

        # Same test ID in a different work or contract cannot attach.
        foreign = self._report(run_id="run-foreign", work_id="other", contract="contract-2")
        self._ledger(foreign, work_id="other", contract="contract-2")
        filtered = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                    plan_digest="contract-1", candidate_sha=self.candidate_sha)
        self.assertEqual([row["run_id"] for row in filtered["runs"]], ["run-1"])
        mismatch = self._report(run_id="mismatched-case")
        mismatch["cases"][0]["test_id"] = "OTHER"
        run_dir = self.runtime / "runs" / "mismatched-case"
        (run_dir / "results.json").write_text(json.dumps(mismatch, sort_keys=True), encoding="utf-8")
        self._ledger(mismatch)
        exact = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                  plan_digest="contract-1", candidate_sha=self.candidate_sha)
        self.assertNotIn("mismatched-case", [row["run_id"] for row in exact["runs"]])

        # A digest-consistent report cannot attribute an older source to a newer run.
        contradiction = self._report(run_id="contradictory-source", source_sha=self.source_sha,
                                     candidate_sha=self.candidate_sha)
        self._ledger(contradiction)
        inspected = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                      plan_digest="contract-1", candidate_sha=self.candidate_sha)
        row = next(item for item in inspected["runs"] if item["run_id"] == "contradictory-source")
        self.assertEqual(row["outcome"], "passed")
        self.assertEqual(row["output_status"], "invalid")
        self.assertIn("candidate", row["diagnostic"])

    def test_missing_stale_tampered_and_refreshed_evidence(self):
        expected = {"id": "T", "runner_id": "python", "case_id": "test_sample.First.test_same",
                    "source_paths": ["test_sample.py"]}
        missing = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                    plan_digest="contract-1", candidate_sha=self.candidate_sha)
        self.assertEqual(missing["status"], "unavailable", missing)
        report = self._report(outcome="failed", log=b"AssertionError: expected true\n")
        self._ledger(report)
        valid = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                  plan_digest="contract-1", candidate_sha=self.candidate_sha)
        self.assertEqual(len(valid["runs"]), 1, valid)
        self.assertEqual(valid["runs"][0]["outcome"], "failed")
        self.assertEqual(valid["runs"][0]["output_status"], "valid")
        log = self.root / valid["runs"][0]["output_artifact"]
        log.write_bytes(log.read_bytes() + b"forged\n")
        tampered = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                     plan_digest="contract-1", candidate_sha=self.candidate_sha)
        self.assertEqual(tampered["runs"][0]["output_status"], "invalid")
        self.assertIn("digest", tampered["runs"][0]["diagnostic"])
        report = self._report(run_id="run-2", outcome="skipped", log=b"skipped by runner\n")
        self._ledger(report)
        refreshed = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                      plan_digest="contract-1", candidate_sha=self.candidate_sha)
        latest = next(row for row in refreshed["runs"] if row["run_id"] == "run-2")
        self.assertEqual(latest["outcome"], "skipped")
        self.assertEqual(latest["output_status"], "valid")
        older = self._report(run_id="run-3", source_sha=self.source_sha,
                             candidate_sha=self.source_sha, outcome="passed")
        self._ledger(older)
        stale = execution_history(self.root, "w", expected, spec_digest="spec-1",
                                  plan_digest="contract-1", candidate_sha=self.candidate_sha)
        old_run = next(row for row in stale["runs"] if row["run_id"] == "run-3")
        self.assertEqual(old_run["outcome"], "passed")
        self.assertEqual(old_run["output_status"], "valid")
        self.assertEqual(old_run["applicability"], "stale")

        # A production-only commit makes an earlier run historical even when
        # its test source bytes are unchanged.
        recent = self._report(run_id="run-4", source_sha=self.candidate_sha,
                              candidate_sha=self.candidate_sha, outcome="passed")
        self._ledger(recent)
        self.write("src/app.py", "VALUE = 'production-only change'\n")
        production_candidate = self.commit("production-only change")
        after_production_change = execution_history(
            self.root, "w", expected, spec_digest="spec-1", plan_digest="contract-1",
            candidate_sha=production_candidate)
        old_implementation = next(row for row in after_production_change["runs"]
                                  if row["run_id"] == "run-4")
        self.assertEqual(old_implementation["source_status"], "historical")
        self.assertEqual(old_implementation["applicability"], "historical")
        self.assertEqual(old_implementation["duration_status"], "unavailable")
        self.assertEqual(old_implementation["recorded_at_status"], "unavailable")

        # A valid external copy must not be accepted through work/<id> symlink.
        external = self.root.parent / (self.root.name + "-external")
        external_work = external / "work/w"
        shutil.copytree(self.root / "work/w", external_work)
        local_work = self.root / "work/w"
        saved_work = self.root / "work/w-saved"
        local_work.rename(saved_work)
        local_work.symlink_to(external_work, target_is_directory=True)
        try:
            outside = execution_history(
                self.root, "w", expected, spec_digest="spec-1", plan_digest="contract-1",
                candidate_sha=production_candidate)
            self.assertEqual(outside["status"], "invalid", outside)
            self.assertEqual(outside["runs"], [])
            self.assertIn("symlink", outside["diagnostic"])
        finally:
            local_work.unlink()
            saved_work.rename(local_work)
            shutil.rmtree(external)

if __name__ == "__main__":
    unittest.main()
