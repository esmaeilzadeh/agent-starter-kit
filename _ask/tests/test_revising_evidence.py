"""Readable selected-test source and authority-bound observations."""
import subprocess
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class ReadableTestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Readable test")
        self.write("test_sample.py", """import unittest
FIXTURE = {"input": "old input"}

def raw_input():
    return FIXTURE["input"]

def make_input():
    return raw_input()

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.expected = "old expected"
        self.addCleanup(self._cleanup_projection)

    def _cleanup_projection(self):
        self.cleaned = True

    def _assert_projection(self, actual):
        self.assertEqual(actual, self.expected)

    def test_projection(self):
        actual = make_input()
        self._assert_projection(actual)
""")
        self.old_sha = self.commit("initial selected test source")
        self.write("test_sample.py", """import unittest
FIXTURE = {"input": "new input"}

def raw_input():
    return FIXTURE["input"]

def make_input():
    return raw_input()

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.expected = "new expected"
        self.addCleanup(self._cleanup_projection)

    def _cleanup_projection(self):
        self.cleaned = True

    def _assert_projection(self, actual):
        self.assertEqual(actual, self.expected)

    def test_projection(self):
        actual = make_input()
        self._assert_projection(actual)
""")
        self.current_sha = self.commit("change current fixture and helper")
        self.test = {
            "id": "T",
            "case_id": "test_sample.ProjectionTests.test_projection",
            "runner_id": "unittest",
            "source_paths": ["test_sample.py"],
            "scenario": {"given": "fixture input", "when": "project", "then": ["old expected"]},
        }

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def test_same_revision_setup_helper_globals_and_assertion_context(self):
        from engineering_model.readable_tests import read_test

        readable = read_test(self.root, self.test, self.old_sha,
                             current_sha=self.current_sha)
        self.assertEqual(readable["status"], "historical", readable)
        self.assertEqual(readable["source_sha"], self.old_sha)
        self.assertEqual(readable["current_sha"], self.current_sha)
        self.assertEqual(readable["flow"], self.test["scenario"])
        self.assertIn("self._assert_projection(actual)", readable["test_source"])
        context = {item["selector"]: item for item in readable["context"]}
        self.assertIn("import unittest", context["<imports>"]["source"])
        self.assertIn('FIXTURE = {"input": "old input"}', context["FIXTURE"]["source"])
        self.assertIn("return raw_input()", context["test_sample.make_input"]["source"])
        self.assertIn("return FIXTURE[\"input\"]", context["test_sample.raw_input"]["source"])
        self.assertIn('self.expected = "old expected"',
                      context["ProjectionTests.setUp"]["source"])
        self.assertIn("def _cleanup_projection", context["ProjectionTests._cleanup_projection"]["source"])
        self.assertIn("self.assertEqual(actual, self.expected)",
                      context["ProjectionTests._assert_projection"]["source"])
        self.assertNotIn("new input", json_context(readable))

        self.write("test_sample.py", """import unittest
FIXTURE = {"input": "old input"}

def raw_input():
    return FIXTURE["input"]

def make_input():
    return raw_input()

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.expected = "old expected"

    def test_projection(self):
        actual = make_input()
        self._missing_helper(actual)
""")
        missing_sha = self.commit("remove selected helper")
        incomplete = read_test(self.root, self.test, missing_sha,
                               current_sha=missing_sha)
        self.assertEqual(incomplete["status"], "current", incomplete)
        self.assertEqual(incomplete["context_status"], "incomplete")
        missing = [item for item in incomplete["context"]
                   if item.get("status") == "missing"]
        self.assertEqual([item["selector"] for item in missing],
                         ["ProjectionTests._missing_helper"])


class EvidenceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Evidence identity")
        self.write("test_sample.py", "def test_case():\n    assert True\n")
        self.candidate = self.commit("candidate test source")
        self.runtime = self.root / "work/w/traceability"
        self.runtime.mkdir(parents=True)
        self.test = {"id": "T", "runner_id": "pytest",
                     "case_id": "test_sample.test_case",
                     "source_paths": ["test_sample.py"]}

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def report(self, *, test_id="T", work_id="w", run_id="run-1",
               plan_digest="plan-1", candidate=None, source=None,
               outcome="failed", failure_kind="behavior_assertion",
               recorded_at="2026-10-17T12:00:00Z", duration=0.125,
               log_text="AssertionError: expected result\n"):
        candidate = candidate or self.candidate
        source = source or candidate
        artifact = f"work/{work_id}/traceability/runs/{run_id}/case.log"
        raw = log_text.encode()
        self.write(artifact, raw.decode())
        output_digest = hashlib.sha256(raw).hexdigest()
        case = {"test_id": test_id, "runner_id": "pytest",
                "case_id": "test_sample.test_case", "execution_id": "exec-1",
                "phase": "final_green", "source_sha": source,
                "source_digests": {"test_sample.py": self.blob_digest(source, "test_sample.py")},
                "outcome": outcome, "failure_kind": failure_kind,
                "output_artifact": artifact, "output_digest": output_digest,
                "recorded_at": recorded_at, "duration": duration}
        execution = {"id": "exec-1", "runner_id": "pytest", "phase": "final_green",
                     "source_sha": source, "exit_code": 0 if outcome == "passed" else 1,
                     "collection_status": "ok", "output_artifact": artifact,
                     "output_digest": output_digest}
        report = {"schema": "ask-test-results/v1", "run_id": run_id,
                  "candidate_sha": candidate, "spec_digest": "spec-1",
                  "plan_digest": plan_digest, "scope": "task", "task_id": "task-1",
                  "recorded_at": recorded_at, "executions": [execution], "cases": [case]}
        report_path = self.runtime / "runs" / run_id / "results.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")
        ledger = [{"work_id": work_id, "run_id": run_id, "phase": "final_green",
                   "candidate_sha": candidate, "spec_digest": "spec-1",
                   "plan_digest": plan_digest, "scope": "task", "task_id": "task-1",
                   "test_id": test_id,
                   "digest": hashlib.sha256(json.dumps(report, sort_keys=True,
                       separators=(",", ":")).encode()).hexdigest()}]
        (self.runtime / "executions.json").write_text(json.dumps(ledger), encoding="utf-8")
        return report, ledger

    def blob_digest(self, revision, path):
        raw = subprocess.run(["git", "show", f"{revision}:{path}"], cwd=self.root,
                             check=True, capture_output=True).stdout
        return hashlib.sha256(raw).hexdigest()

    def history(self, **kwargs):
        from engineering_model.workbench_evidence import execution_history
        return execution_history(self.root, "w", self.test, spec_digest="spec-1",
                                 plan_digest="plan-1", candidate_sha=self.candidate, **kwargs)

    def test_work_test_run_contract_candidate_and_integrity_must_all_agree(self):
        report, _ledger = self.report()
        before_head = self.git("rev-parse", "HEAD")
        from engineering_model.workbench_evidence import execution_history
        valid = execution_history(self.root, "w", self.test, spec_digest="spec-1",
                                  plan_digest="plan-1", candidate_sha=self.candidate)
        self.assertEqual(valid["status"], "available", valid)
        row = valid["runs"][0]
        self.assertEqual((row["test_id"], row["run_id"], row["candidate_sha"],
                          row["plan_digest"], row["outcome"], row["failure_kind"],
                          row["recorded_at"], row["duration"], row["output_status"]),
                         ("T", "run-1", self.candidate, "plan-1", "failed",
                          "behavior_assertion", "2026-10-17T12:00:00Z", 0.125, "valid"))
        self.assertEqual(valid["completion"], "not_evaluated")
        self.assertIn("AssertionError", (self.root / row["output_artifact"]).read_text())

        cases = [
            ("foreign test", lambda r: r["cases"][0].update(test_id="OTHER"), "not_run"),
            ("foreign contract", lambda r: r.update(plan_digest="foreign-plan"), "invalid"),
            ("candidate mismatch", lambda r: r["cases"][0].update(source_sha="0" * 40), "invalid"),
            ("source digest", lambda r: r["cases"][0].update(source_digests={"test_sample.py": "0" * 64}), "invalid"),
            ("case execution join", lambda r: r["cases"][0].update(execution_id="foreign-execution"), "not_run"),
            ("failed collection", lambda r: r["executions"][0].update(collection_status="error"), "invalid"),
        ]
        for label, mutate, expected_status in cases:
            with self.subTest(label=label):
                report, _ledger = self.report(run_id="run-1")
                mutate(report)
                report_path = self.runtime / "runs/run-1/results.json"
                report_path.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")
                ledger = [{"work_id": "w", "run_id": "run-1", "phase": "final_green",
                           "candidate_sha": report["candidate_sha"], "spec_digest": "spec-1",
                           "plan_digest": "plan-1", "scope": "task", "task_id": "task-1",
                           "test_id": "T", "digest": hashlib.sha256(json.dumps(
                               report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}]
                (self.runtime / "executions.json").write_text(json.dumps(ledger), encoding="utf-8")
                result = self.history()
                if expected_status == "invalid":
                    self.assertTrue(any(row.get("output_status") == "invalid"
                                        for row in result["runs"]), (label, result))
                else:
                    self.assertEqual(result["status"], expected_status, (label, result))

        report, ledger = self.report()
        ledger[0]["work_id"] = "other-work"
        (self.runtime / "executions.json").write_text(json.dumps(ledger), encoding="utf-8")
        false_work_join = self.history()
        self.assertEqual(false_work_join["status"], "not_run", false_work_join)

        report, ledger = self.report()
        log_path = self.root / report["cases"][0]["output_artifact"]
        log_path.write_text("forged pass\n")
        tampered = self.history()
        self.assertEqual(tampered["runs"][0]["output_status"], "invalid")
        self.assertIn("digest", tampered["runs"][0]["diagnostic"])

        report, ledger = self.report()
        ledger[0]["digest"] = "0" * 64
        (self.runtime / "executions.json").write_text(json.dumps(ledger), encoding="utf-8")
        bad_report_digest = self.history()
        self.assertTrue(any(row.get("output_status") == "invalid"
                            for row in bad_report_digest["runs"]), bad_report_digest)
        self.assertEqual(self.git("rev-parse", "HEAD"), before_head)

    def test_all_observation_states_and_helper_changes_preserve_applicability(self):
        from engineering_model.workbench_evidence import execution_history

        for outcome, failure_kind in (("passed", None), ("failed", "behavior_assertion"),
                                      ("skipped", None), ("error", "runtime_error")):
            with self.subTest(outcome=outcome):
                report, _ledger = self.report(outcome=outcome, failure_kind=failure_kind,
                                              run_id="run-1", log_text=f"{outcome} output\n")
                result = self.history()
                row = result["runs"][0]
                self.assertEqual((row["outcome"], row["failure_kind"], row["output_status"]),
                                 (outcome, failure_kind, "valid"))
                self.assertEqual(row["completion"], "not_evaluated")
                self.assertEqual(row["applicability"], "current")
                self.assertIn(f"{outcome} output", (self.root / row["output_artifact"]).read_text())

        report, _ledger = self.report(run_id="run-1", outcome="unknown-outcome",
                                      failure_kind=None, log_text="unclassified observation\n")
        unknown = self.history()
        self.assertEqual(unknown["runs"][0]["output_status"], "invalid", unknown)

        report, _ledger = self.report(run_id="run-1", outcome="passed", duration=None,
                                      recorded_at=None, log_text="passed\n")
        row = self.history()["runs"][0]
        self.assertIsNone(row["duration"])
        self.assertEqual(row["duration_status"], "unavailable")
        self.assertEqual(row["recorded_at_status"], "unavailable")

        report, _ledger = self.report(run_id="run-1", candidate=self.candidate,
                                      source=self.candidate, outcome="passed")
        self.write("test_sample.py", "def test_case():\n    assert False\n")
        stale_candidate = self.commit("change selected test source")
        stale = execution_history(self.root, "w", self.test, spec_digest="spec-1",
                                  plan_digest="plan-1", candidate_sha=stale_candidate)
        self.assertEqual((stale["runs"][0]["applicability"], stale["runs"][0]["source_status"]),
                         ("stale", "stale"))

        report, _ledger = self.report(run_id="run-2", candidate=stale_candidate,
                                      source=stale_candidate, outcome="passed")
        self.write("src/implementation.py", "VALUE = 1\n")
        historical_head = self.commit("change implementation only")
        historical = execution_history(self.root, "w", self.test, spec_digest="spec-1",
                                       plan_digest="plan-1", candidate_sha=stale_candidate)
        row = next(item for item in historical["runs"] if item["run_id"] == "run-2")
        self.assertEqual((row["applicability"], row["source_status"]), ("historical", "historical"))
        self.assertEqual(self.git("rev-parse", "HEAD"), historical_head)

        (self.runtime / "executions.json").write_text("[]", encoding="utf-8")
        self.assertEqual(self.history()["status"], "not_run")
        (self.runtime / "executions.json").unlink()
        self.assertEqual(self.history()["status"], "unavailable")


def json_context(readable):
    import json
    return json.dumps(readable, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
