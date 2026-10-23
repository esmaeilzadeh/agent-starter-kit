"""Recovery guards exercised through fresh coordinator processes."""
from __future__ import annotations

import json
import hashlib
import os
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "_ask" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(REPO / ".agents" / "ask"))

from _ask.tests.inner_loop_recovery_fixture import (
    LEGACY_AUTHORITY_SHA,
    LEGACY_STATE_SHA256,
    write_legacy_fixture,
)
from inner_loop.graph import load_graph
from inner_loop.checkpoint import CheckpointError, publish, read_checkpoint, _read_tree
from inner_loop.recovery import inspect as inspect_recovery
from inner_loop.state import load_state

TASKS = """schema: ask-inner-loop-tasks/v1
work_id: w
tasks:
  - id: a
    depends_on: []
    owned_paths:
      - src/a.py
  - id: b
    depends_on: [a]
    owned_paths:
      - src/a.py
"""

REPAIR_TASKS = """schema: ask-inner-loop-tasks/v1
work_id: continuation-recovery
tasks:
  - id: CR-1
    depends_on: []
    owned_paths:
      - _ask/scripts/inner_loop/state.py
      - _ask/scripts/inner_loop/driver.py
      - _ask/scripts/inner_loop/recovery.py
      - _ask/scripts/inner_loop/__main__.py
      - _ask/tests/inner_loop_recovery.py
      - _ask/tests/inner_loop_recovery_fixture.py
  - id: CR-2
    depends_on: [CR-1]
    owned_paths:
      - _ask/scripts/inner_loop/checkpoint.py
      - _ask/scripts/inner_loop/state.py
  - id: CR-3
    depends_on: [CR-2]
    owned_paths:
      - _ask/scripts/inner_loop/checkpoint.py
      - _ask/scripts/inner_loop/driver.py
  - id: CR-4
    depends_on: [CR-3]
    owned_paths:
      - _ask/scripts/inner_loop/recovery.py
      - work/continuation-recovery/adoption/**
"""


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q", "-b", "agent/w")
        self.git("config", "user.email", "recovery@example.test")
        self.git("config", "user.name", "Recovery Test")
        self.write(
            ".gitignore",
            "work/*/inner-loop/state.json\n"
            "work/*/inner-loop/state.lock\n"
            "work/*/inner-loop/results/\n"
            "work/*/inner-loop/evidence/\n"
            "work/*/traceability/\n",
        )
        self.write("work/w/inner-loop/tasks.yaml", TASKS)
        self.spec = {
            "schema": "ask-spec/v1",
            "work_id": "w",
            "criteria": [{"id": "C1", "given": "state", "when": "checked", "then": ["safe"]}],
        }
        self.case_a = {
            "id": "T-A", "task_id": "a", "criterion_ids": ["C1"],
            "case_id": "tests.test_a", "scenario": {"given": "a", "when": "runs", "then": ["passes"]},
            "expected_assertions": [{"criterion_id": "C1", "checks": ["passes"]}],
            "runner_id": "fixture", "source_paths": ["src/a.py"], "type": "integration",
        }
        self.case_b = {
            "id": "T-B", "task_id": "a", "criterion_ids": ["C1"],
            "case_id": "tests.test_b", "scenario": {"given": "b", "when": "runs", "then": ["passes"]},
            "expected_assertions": [{"criterion_id": "C1", "checks": ["passes"]}],
            "runner_id": "fixture", "source_paths": ["src/a.py"], "type": "integration",
        }
        self.old_plan = {
            "schema": "ask-test-plan/v1", "work_id": "w",
            "runners": [{"id": "fixture", "argv": ["python", "-m", "unittest", "fixture"],
                         "adapter": "unittest"}],
            "tests": [self.case_a, self.case_b],
            "task_scopes": [{"task_id": "a", "test_ids": ["T-A", "T-B"]},
                            {"task_id": "b", "test_ids": []}],
        }
        self.write("specs/current/w.json", json.dumps(self.spec, sort_keys=True))
        self.write(".agents/ask/verification/traceability/__init__.py",
                   "CAPABILITY = 'ask-traceability/v1'\n")
        self.write(".agents/ask/verification/traceability/unittest_runner.py",
                   "# fixture runner identity\n")
        self.write("work/w/test-plan.json", json.dumps(self.old_plan, sort_keys=True))
        self.commit("accepted task graph")
        self.base = self.git("rev-parse", "HEAD")
        self.old_spec_digest = self.json_digest(self.spec)
        self.old_plan_digest = self.json_digest(self.old_plan)
        self.old_graph_digest = self.json_digest(load_graph(self.root, "w"))
        self.write(
            "work/w/traceability-accepted.json",
            json.dumps({"schema": "ask-accepted-tests/v1", "work_id": "w", "contract_sha": self.base,
                        "spec_digest": self.old_spec_digest, "plan_digest": self.old_plan_digest,
                        "graph_digest": self.old_graph_digest}) + "\n",
        )
        self.commit("accepted test anchor")
        self.anchor_commit = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/ask/accepted-tests/w", self.anchor_commit)

    @staticmethod
    def json_digest(value):
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.PIPE).strip()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-qm", message)

    def run_cli(self, *args, env=None):
        child_env = dict(os.environ)
        if env is not None:
            child_env.update(env)
        child_env["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(SCRIPTS), child_env.get("PYTHONPATH", "")) if part
        )
        return subprocess.run(
            [sys.executable, "-m", "inner_loop", "--root", str(self.root), *args],
            cwd=self.root,
            env=child_env,
            capture_output=True,
            text=True,
        )

    def start_candidate(self):
        started = self.run_cli("run", "w")
        self.assertEqual(started.returncode, 0, started.stderr + started.stdout)
        self.assertIn("running=a", started.stdout)
        self.write("src/a.py", "candidate = True\n")
        self.commit("candidate for task a")
        self.candidate = self.git("rev-parse", "HEAD")
        self.result_path = self.root / "work/w/inner-loop/results/a.json"
        self.review_path = self.root / "work/w/inner-loop/evidence/review-a.json"
        self.result_path.parent.mkdir(parents=True, exist_ok=True)
        self.review_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_path.write_text(
            json.dumps(
                {
                    "schema": "ask-task-result/v2",
                    "work_id": "w",
                    "task_id": "a",
                    "base_sha": self.anchor_commit,
                    "candidate_sha": self.candidate,
                    "contract_sha": self.base,
                    "tdd": {
                        "seam": "src/a.py",
                        "red": {"command": "case", "output": "assertion failed", "exit_code": 1},
                        "green": {"command": "case", "output": "passed", "exit_code": 0},
                    },
                    "exemption": None,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.review_path.write_text(
            json.dumps(
                {
                    "work_id": "w",
                    "task_id": "a",
                    "base_sha": self.anchor_commit,
                    "candidate_sha": self.candidate,
                    "verdict": "APPROVED",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def _real_traceability_pair(self, runner_count=1, old_runner=False):
        """Run the accepted plan on real failing and passing commits."""
        import shutil
        from verification.traceability.contracts import digest
        from verification.traceability.evidence import accept_plan

        shutil.copytree(
            REPO / ".agents" / "ask" / "verification",
            self.root / ".agents/ask/verification",
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        if old_runner:
            # CR-2 is the supported pre-hook verifier base: it has no coordinator
            # checkpoint import, so the parent must consume its receipt.
            old_base = "2c508ff4248f16a3e3121d33a0fae7297c9b378e"
            paths = subprocess.check_output(
                ["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", old_base,
                 ".agents/ask/verification/"], text=True,
            ).splitlines()
            for name in paths:
                if name.endswith(".py"):
                    raw = subprocess.check_output(["git", "-C", str(REPO), "show", f"{old_base}:{name}"])
                    (self.root / name).parent.mkdir(parents=True, exist_ok=True)
                    (self.root / name).write_bytes(raw)
        (self.root / "_ask/policies").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / "_ask/policies/delegation.md",
                        self.root / "_ask/policies/delegation.md")
        self.spec = {
            "schema": "ask-spec/v1", "work_id": "w", "revision": 1,
            "criteria": [{"id": "C1", "given": "a task candidate", "when": "the assertion runs",
                          "then": ["the source value is green"], "verification_mode": "tests"}],
        }
        runners = ([{"id": "fixture", "argv": ["python", "-m", "unittest", "fixture"],
                     "adapter": "unittest"}]
                   if runner_count == 1 else [
                       {"id": "fixture-a", "argv": ["python", "-m", "unittest", "fixture"],
                        "adapter": "unittest"},
                       {"id": "fixture-b", "argv": ["python", "-m", "unittest", "fixture"],
                        "adapter": "unittest"},
                   ])
        self.old_plan = {
            "schema": "ask-test-plan/v1", "work_id": "w", "spec_digest": digest(self.spec),
            "obligations": [{"criterion_id": "C1", "required_types": ["integration"]}],
            "runners": runners,
            "tests": [
                {"id": "T-A", "task_id": "a", "criterion_ids": ["C1"],
                 "case_id": "tests.test_a", "scenario": {"given": "red source", "when": "test_a runs", "then": ["fails" ]},
                 "expected_assertions": [{"criterion_id": "C1", "checks": ["source is green"]}],
                 "runner_id": "fixture-a" if runner_count > 1 else "fixture",
                 "source_paths": ["src/a.py"], "type": "integration", "change_kind": "new"},
                {"id": "T-B", "task_id": "a", "criterion_ids": ["C1"],
                 "case_id": "tests.test_b", "scenario": {"given": "red source", "when": "test_b runs", "then": ["fails" ]},
                 "expected_assertions": [{"criterion_id": "C1", "checks": ["source is green"]}],
                 "runner_id": "fixture-b" if runner_count > 1 else "fixture",
                 "source_paths": ["src/a.py"], "type": "integration", "change_kind": "new"},
            ],
            "task_scopes": [{"task_id": "a", "test_ids": ["T-A", "T-B"]},
                            {"task_id": "b", "test_ids": []}],
        }
        self.write("specs/current/w.json", json.dumps(self.spec, sort_keys=True))
        self.write("work/w/test-plan.json", json.dumps(self.old_plan, sort_keys=True))
        review_path = "work/w/traceability/plan-review.json"
        self.write(review_path, json.dumps({"decision": "APPROVED", "reviewer": "fixture-reviewer",
                                             "spec_digest": digest(self.spec),
                                             "plan_digest": digest(self.old_plan)}))
        self.commit("CR-3 accepted real-run fixture contract")
        accepted = accept_plan(self.root, "w", "HEAD", "fixture-reviewer", "fixture-coordinator", review_path)
        self.write("work/w/traceability-accepted.json", json.dumps(accepted, sort_keys=True) + "\n")
        self.commit("CR-3 accepted real-run fixture authority")
        self.anchor_commit = self.git("rev-parse", "HEAD")
        started = self.run_cli("run", "w")
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        self.write(
            "fixture.py",
            """import pathlib, unittest
class test_a(unittest.TestCase):
    def runTest(self): self.assertEqual(pathlib.Path('src/a.py').read_text(), 'green\\n')
    def id(self): return 'tests.test_a'
class test_b(unittest.TestCase):
    def runTest(self): self.assertEqual(pathlib.Path('src/a.py').read_text(), 'green\\n')
    def id(self): return 'tests.test_b'
""",
        )
        self.write("src/a.py", "red\n")
        self.commit("CR-3 real assertion red fixture")
        red_sha = self.git("rev-parse", "HEAD")
        from verification.traceability.adapters import run_tests
        contracts = {"spec": self.spec, "plan": self.old_plan}
        red = run_tests(self.root, contracts, red_sha, "task", "a", "red")
        self.write("src/a.py", "green\n")
        self.commit("CR-3 real assertion green fixture")
        green_sha = self.git("rev-parse", "HEAD")
        green = run_tests(self.root, contracts, green_sha, "task", "a", "final_green")
        return red, green

    def test_checkpoint_real_red_and_green(self):
        red, green = self._real_traceability_pair(runner_count=2)
        from inner_loop import evidence
        self.assertTrue(
            callable(getattr(evidence, "checkpoint_run", None)),
            "coordinator must checkpoint validated standalone run milestones",
        )
        for report in (red, green):
            try:
                evidence.checkpoint_run(self.root, "w", "a", report["run_id"])
            except Exception as exc:
                self.fail(f"valid accepted multi-runner report must finalize: {exc}")
            self.assertEqual({item["runner_id"] for item in report["executions"]},
                             {"fixture-a", "fixture-b"})
        state = json.loads((self.root / "work/w/inner-loop/state.json").read_text())
        recorded = state["tasks"]["a"]["evidence"]["traceability_runs"]
        self.assertEqual([item["run_id"] for item in recorded], [red["run_id"], green["run_id"]])
        checkpoint = read_checkpoint(self.root, "w")
        self.assertIsNotNone(checkpoint)
        for report in (red, green):
            run_dir = self.root / "work/w/traceability/runs" / report["run_id"]
            for path in run_dir.iterdir():
                if path.is_file():
                    relative = path.relative_to(self.root).as_posix()
                    self.assertEqual(checkpoint[2]["artifacts/" + relative], path.read_bytes())
        cache = self.root / "work/w/inner-loop/state.json"
        cache.unlink()
        restored = load_state(self.root, "w")
        self.assertEqual(
            [item["run_id"] for item in restored["tasks"]["a"]["evidence"]["traceability_runs"]],
            [red["run_id"], green["run_id"]],
        )

    def test_stale_review_preserves_execution(self):
        self.test_new_candidate_preserves_stale_rejected_review_history()

    def test_crash_after_verification_or_ff(self):
        self.test_crash_around_checkpoint_publication()
        from _ask.tests.inner_loop_reliability import IntegrationTests
        from inner_loop import driver
        result = unittest.TestResult()

        class PostFastForwardRecoveryCase(IntegrationTests):
            def test_interrupt_after_real_fast_forward(self):
                original_integrate = driver.git_integrate

                def integrate_then_interrupt(*args, **kwargs):
                    sha = original_integrate(*args, **kwargs)
                    raise RuntimeError("injected interruption after fast-forward " + sha)

                driver.git_integrate = integrate_then_interrupt
                try:
                    with self.assertRaisesRegex(RuntimeError, "after fast-forward"):
                        super().test_fast_forward_matches_verified_candidate()
                finally:
                    driver.git_integrate = original_integrate

                self.assertEqual(self.git("rev-parse", "HEAD"), self.candidate)
                retained = read_checkpoint(self.root, "w")
                self.assertIsNotNone(retained)
                task = retained[1]["tasks"]["a"]
                self.assertEqual(task["status"], "running")
                self.assertEqual(task["evidence"]["verification"]["candidate_sha"], self.candidate)
                self.assertEqual(retained[1]["coordinator_sha"], self.base)

                driver.integrate_ready(self.root, "w", "a")
                recovered = load_state(self.root, "w")
                self.assertEqual(recovered["tasks"]["a"]["status"], "integrated")
                self.assertEqual(recovered["coordinator_sha"], self.candidate)

        PostFastForwardRecoveryCase("test_interrupt_after_real_fast_forward").run(result)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])

    def test_guard_rollback_and_explicit_attempts(self):
        # A real accepted Green must not be erasable through the generic CAS
        # API. The reviewed interrupt/reopen path below archives it first.
        self._real_traceability_pair()
        from inner_loop import evidence
        from inner_loop.state import (
            ProtocolViolation, _preserve_attempt_evidence, cas_apply,
        )
        state = load_state(self.root, "w")
        ledger = json.loads((self.root / "work/w/traceability/executions.json").read_text())
        green_id = next(row["run_id"] for row in reversed(ledger)
                        if row.get("phase") == "final_green")
        evidence.checkpoint_run(self.root, "w", "a", green_id)
        state = load_state(self.root, "w")
        recorded = copy.deepcopy(state["tasks"]["a"]["evidence"])
        self.assertTrue(any(item["run_id"] == green_id for item in recorded["traceability_runs"]))
        with self.assertRaisesRegex(ProtocolViolation, "evidence.*cannot be removed or rewritten"):
            cas_apply(self.root, "w", state["revision"],
                      lambda doc: doc["tasks"]["a"].update(evidence={}))
        after = load_state(self.root, "w")["tasks"]["a"]["evidence"]
        self.assertEqual(after, recorded)

        # Exercise each retained identity independently so the run-history
        # guard cannot mask review or verifier-receipt rewrites.
        baseline = load_state(self.root, "w")
        baseline["tasks"]["a"]["evidence"]["review"] = {
            "reviewer": "independent", "verdict": "APPROVED",
            "candidate_sha": self.git("rev-parse", "HEAD"),
            "result_digest": "review-result-digest",
        }
        changed_review = copy.deepcopy(baseline)
        changed_review["tasks"]["a"]["evidence"]["review"]["reviewer"] = "rewritten"
        with self.assertRaisesRegex(ProtocolViolation, "review evidence.*rewritten"):
            _preserve_attempt_evidence(baseline, changed_review, archive=False,
                                       update_review=False, finalize_verification=False)

        baseline["tasks"]["a"]["evidence"]["verification"] = {
            "result": "pass", "candidate_sha": self.git("rev-parse", "HEAD"),
            "checks": [{"id": "mandatory", "status": "pass"}],
            "completion_digest": "completion-receipt-digest",
        }
        baseline["tasks"]["a"]["evidence"]["verification_record_digest"] = "record-digest"
        changed_receipt = copy.deepcopy(baseline)
        changed_receipt["tasks"]["a"]["evidence"]["verification"]["checks"][0]["status"] = "skipped"
        with self.assertRaisesRegex(ProtocolViolation, "verification receipt.*rewritten"):
            _preserve_attempt_evidence(baseline, changed_receipt, archive=False,
                                       update_review=False, finalize_verification=False)

        # The explicit attempt API preserves the exact old evidence before it
        # clears the active attempt, then reopening requires a newly accepted
        # plan and starts a clean attempt.
        fresh = type(self)("test_interrupt_and_reopen_preserve_attempt_history")
        fresh.setUp()
        try:
            fresh.test_interrupt_and_reopen_preserve_attempt_history()
        finally:
            fresh.doCleanups()

    def test_clone_and_cli_recovery_diagnostics(self):
        self.test_retain_objects_after_gc_and_bundle_transfer()

    def test_nested_verifier_coordinator_finalization(self):
        from _ask.tests import inner_loop_reliability as reliability
        from verification.traceability.contracts import digest
        from verification.traceability.evidence import (
            inventory, load_accepted, record_test_review, source_digests, write_json,
        )

        original_seed = reliability.seed_traceability
        original_accept = reliability.accept_traceability
        original_review = reliability.review_traceability

        def seed_real_plan(root, work_id):
            original_seed(root, work_id)
            spec = {
                "schema": "ask-spec/v1", "work_id": work_id, "revision": 1,
                "criteria": [{"id": "C1", "given": "a coordinator candidate",
                              "when": "the real test runs", "then": ["candidate source passes"],
                              "verification_mode": "tests"}],
            }
            plan = {
                "schema": "ask-test-plan/v1", "work_id": work_id, "spec_digest": digest(spec),
                "obligations": [{"criterion_id": "C1", "required_types": ["integration"]}],
                "runners": [{"id": "fixture", "argv": ["python3", "-m", "unittest", "test_case"],
                             "adapter": "unittest"}],
                "tests": [{"id": "T-A", "task_id": "a", "criterion_ids": ["C1"],
                           "case_id": "test_case.TestA.test_a",
                           "scenario": {"given": "base source", "when": "the test runs", "then": ["red then green"]},
                           "expected_assertions": [{"criterion_id": "C1", "checks": ["candidate source passes"]}],
                           "runner_id": "fixture", "source_paths": ["src/value"],
                           "type": "integration", "change_kind": "new"},
                          {"id": "T-B", "task_id": "b", "criterion_ids": ["C1"],
                           "case_id": "test_case.TestB.test_b",
                           "scenario": {"given": "another task", "when": "its test runs", "then": ["fails at base"]},
                           "expected_assertions": [{"criterion_id": "C1", "checks": ["candidate source passes"]}],
                           "runner_id": "fixture", "source_paths": ["src/value"],
                           "type": "integration", "change_kind": "new"}],
                "task_scopes": [{"task_id": "a", "test_ids": ["T-A"]},
                                {"task_id": "b", "test_ids": ["T-B"]}],
            }
            write_json(root / "specs/current" / f"{work_id}.json", spec)
            write_json(root / "work" / work_id / "test-plan.json", plan)
            (root / "test_case.py").write_text(
                "import pathlib, unittest\n"
                "class TestA(unittest.TestCase):\n"
                "    def test_a(self): self.assertEqual(pathlib.Path('src/value').read_text(), 'candidate\\n')\n"
                "class TestB(unittest.TestCase):\n"
                "    def test_b(self): self.assertEqual(pathlib.Path('src/value').read_text(), 'candidate\\n')\n",
                encoding="utf-8",
            )

        def accept_and_seed_red(root, work_id):
            original_accept(root, work_id)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            contracts = load_accepted(root, work_id, base, base)
            from verification.traceability.adapters import run_tests
            run_tests(root, contracts, base, "task", "b", "red")
            run_tests(root, contracts, base, "task", "a", "red")

        def review_real_tests(root, work_id, candidate):
            contracts = load_accepted(root, work_id, candidate, candidate)
            plan = contracts["plan"]
            actual = inventory(root, contracts["pin"]["contract_sha"], candidate, plan)
            review = {
                "schema": "ask-test-review/v2", "reviewer": "fixture-independent",
                "candidate_sha": candidate, "base_sha": contracts["pin"]["contract_sha"],
                "spec_digest": digest(contracts["spec"]), "plan_digest": digest(plan),
                "scope": "task", "task_id": "a", "test_ids": ["T-A"],
                "criterion_ids": ["C1"], "source_digests": source_digests(root, candidate, plan, ["T-A"]),
                "inspected_sources": actual["inspected_sources"], "changed_cases": actual["changed_cases"],
                "inventory_exclusions": {name: "Fixture source is inspected by this enclosing test."
                                         for name in actual["unmapped_cases"]},
                "criteria": [{"id": "C1", "coverage_decision": "APPROVED",
                              "assessment": "The mapped assertion compares the committed source value.",
                              "type_adequacy": {"integration": {"decision": "APPROVED",
                                  "assessment": "The trusted runner executes the candidate in a disposable worktree."}}}],
                "tests": [{"id": "T-A", "decision": "APPROVED",
                           "assertion_assessment": "Compares the value to a literal expected string.",
                           "counterexample": "Returning the base value fails.",
                           "tdd_continuity_assessment": "The same assertion is run before and after the candidate change."}],
            }
            path = "work/w/traceability/review-input.json"
            write_json(root / path, review)
            record_test_review(root, work_id, candidate, candidate, path, "fixture-coordinator",
                               review_document=review)

        reliability.seed_traceability = seed_real_plan
        reliability.accept_traceability = accept_and_seed_red
        reliability.review_traceability = review_real_tests
        result = unittest.TestResult()
        class NestedFinalizationCase(reliability.IntegrationTests):
            def test_nested_real_reports_are_finalized_by_parent(self):
                from inner_loop import driver
                original_integrate = driver.git_integrate
                before_fast_forward = {}

                def interrupt_before_fast_forward(*args, **kwargs):
                    retained = read_checkpoint(self.root, "w")
                    before_fast_forward["state"] = retained[1] if retained else None
                    raise RuntimeError("injected interruption before fast-forward")

                driver.git_integrate = interrupt_before_fast_forward
                try:
                    with self.assertRaisesRegex(RuntimeError, "before fast-forward"):
                        super().test_successful_in_place_integration_records_executed_lineage()
                finally:
                    driver.git_integrate = original_integrate

                retained_task = ((before_fast_forward.get("state") or {}).get("tasks") or {}).get("a", {})
                verification = (retained_task.get("evidence") or {}).get("verification")
                self.assertIsInstance(verification, dict,
                                      "verified evidence must be durable before invoking fast-forward")
                self.assertEqual(verification.get("candidate_sha"), self.candidate)
                self.assertEqual(verification.get("result"), "pass")
                self.assertEqual(len((retained_task.get("evidence") or {}).get("traceability_runs", [])), 2)

                # Recovery completes the missing FF/state fold from the exact
                # retained verification checkpoint.
                driver.integrate_ready(self.root, "w", "a")
                task = load_state(self.root, "w")["tasks"]["a"]
                runs = task["evidence"].get("traceability_runs", [])
                self.assertEqual(len(runs), 2, runs)
                self.assertEqual({item["phase"] for item in runs}, {"red", "final_green"})
                self.assertEqual({item["task_id"] for item in runs}, {"a"})
                self.assertEqual({item["candidate_sha"] for item in runs}, {self.base, self.candidate})

                # A later failed verification replaces the shared completion
                # projection. It must not erase the historical passing receipt
                # retained by the integrated checkpoint.
                from inner_loop.recovery import (
                    _checkpointed_verification, _traceability_matches_checkpoint,
                )
                checkpoint = read_checkpoint(self.root, "w")
                self.assertIsNotNone(checkpoint)
                self.assertIn("artifacts/work/w/traceability/completion.json", checkpoint[2])
                retained_state = checkpoint[1]
                historical = _checkpointed_verification(self.root, "w", retained_state, checkpoint)
                self.assertIsNotNone(historical)
                retained_files = checkpoint[2]
                for relative, digest_key in (
                    ("work/w/traceability/completion.json", "completion_digest"),
                    (f"work/w/traceability/static-{historical['candidate_sha']}.json",
                     "static_receipt_digest"),
                ):
                    self.assertEqual(
                        hashlib.sha256(retained_files["artifacts/" + relative]).hexdigest(),
                        historical[digest_key],
                    )
                completion = self.root / "work/w/traceability/completion.json"
                completion.write_text('{"status":"fail","reason":"later candidate"}\n')
                traceability = self.root / "work/w/traceability"
                (traceability / "static-later.json").write_text('{"status":"fail"}\n')
                (traceability / "static-runs/later/0.log").parent.mkdir(parents=True, exist_ok=True)
                (traceability / "static-runs/later/0.log").write_text("failed verifier output\n")
                (traceability / "reviews/later.json").parent.mkdir(parents=True, exist_ok=True)
                (traceability / "reviews/later.json").write_text('{"verdict":"REJECTED"}\n')
                (traceability / "verification-later.json").write_text('{"result":"fail"}\n')
                (traceability / "plan-review-later.json").write_text('{"decision":"APPROVED"}\n')
                self.assertEqual(
                    _checkpointed_verification(self.root, "w", retained_state, checkpoint),
                    historical,
                    "a failed later verifier projection must not invalidate retained historical evidence",
                )
                self.assertTrue(
                    _traceability_matches_checkpoint(
                        self.root, "w", checkpoint, expected_verification=historical,
                    ),
                    "later derived verifier/review artifacts must coexist with exact retained evidence",
                )

        try:
            NestedFinalizationCase("test_nested_real_reports_are_finalized_by_parent").run(result)
        finally:
            reliability.seed_traceability = original_seed
            reliability.accept_traceability = original_accept
            reliability.review_traceability = original_review
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])

    def test_standalone_run_finalization_interruptions(self):
        red, green = self._real_traceability_pair()
        from inner_loop import evidence

        def interrupted_standalone(hook):
            run_root = self.root / "work/w/traceability/runs"
            before = {path.name for path in run_root.iterdir()}
            env = dict(os.environ, ASK_TRACEABILITY_RUNTIME_ROOT=str(self.root),
                       ASK_TRACEABILITY_CRASH_AT=hook,
                       PYTHONPATH=os.pathsep.join((str(self.root / ".agents/ask"), str(SCRIPTS),
                                                   os.environ.get("PYTHONPATH", ""))))
            proc = subprocess.run(
                [sys.executable, "-m", "verification.traceability.cli", "--root", str(self.root),
                 "run", "w", "--candidate-sha", self.git("rev-parse", "HEAD"),
                 "--anchor-sha", self.git("rev-parse", "HEAD"), "--scope", "task", "--task-id", "a",
                 "--phase", "final_green"], cwd=self.root, env=env, capture_output=True, text=True,
                timeout=30,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            added = {path.name for path in run_root.iterdir()} - before
            self.assertEqual(len(added), 1, f"{hook} should leave one complete report: {added}")
            return next(iter(added))

        report_only_id = interrupted_standalone("after_report_publication")
        ledger = self.root / "work/w/traceability/executions.json"
        rows = json.loads(ledger.read_text())
        self.assertNotIn(report_only_id, {row["run_id"] for row in rows})
        evidence.checkpoint_run(self.root, "w", "a", report_only_id)

        ledger_only_id = interrupted_standalone("after_ledger_insertion")
        rows = json.loads(ledger.read_text())
        self.assertIn(ledger_only_id, {row["run_id"] for row in rows})
        evidence.checkpoint_run(self.root, "w", "a", ledger_only_id)

        crash_env = dict(os.environ, PYTHONPATH=os.pathsep.join(
            part for part in (str(SCRIPTS), os.environ.get("PYTHONPATH", "")) if part
        ), ASK_INNER_LOOP_CRASH_AT="after_ref_publication")
        killed = subprocess.run(
            [sys.executable, "-m", "inner_loop", "--root", str(self.root),
             "checkpoint-run", "w", "a", "--run-id", ledger_only_id],
            cwd=self.root, env=crash_env, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(killed.returncode, 76, killed.stdout + killed.stderr)
        retained = read_checkpoint(self.root, "w")
        self.assertIn(ledger_only_id, {
            item["run_id"] for item in retained[1]["tasks"]["a"]["evidence"]["traceability_runs"]
        })
        self.assertIn(ledger_only_id, {
            item["run_id"] for item in load_state(self.root, "w")["tasks"]["a"]["evidence"]["traceability_runs"]
        })

        env = dict(os.environ)
        # This child is the fixture's standalone coordinator, even when the
        # enclosing test is running under a verifier's detached candidate.
        env["ASK_TRACEABILITY_RUNTIME_ROOT"] = str(self.root)
        env["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(self.root / ".agents/ask"), str(SCRIPTS), env.get("PYTHONPATH", "")) if part
        )
        command = subprocess.run(
            [sys.executable, "-m", "verification.traceability.cli", "--root", str(self.root),
             "run", "w", "--candidate-sha", self.git("rev-parse", "HEAD"),
             "--anchor-sha", self.git("rev-parse", "HEAD"), "--scope", "task", "--task-id", "a",
             "--phase", "final_green"],
            cwd=self.root, env=env, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(command.returncode, 0, command.stdout + command.stderr)
        self.assertIn("coordinator_finalization", command.stdout)
        ledger = self.root / "work/w/traceability/executions.json"
        rows = json.loads(ledger.read_text())

        worker_env = dict(env, ASK_INNER_LOOP_ROLE="worker")
        worker = subprocess.run(
            [sys.executable, "-m", "verification.traceability.cli", "--root", str(self.root),
             "run", "w", "--candidate-sha", self.git("rev-parse", "HEAD"),
             "--anchor-sha", self.git("rev-parse", "HEAD"), "--scope", "task", "--task-id", "a",
             "--phase", "final_green"], cwd=self.root, env=worker_env, capture_output=True,
            text=True, timeout=30,
        )
        self.assertEqual(worker.returncode, 0, worker.stdout + worker.stderr)
        self.assertNotIn("coordinator_finalization", worker.stdout)
        worker_report = json.loads(worker.stdout)
        state = load_state(self.root, "w")
        self.assertNotIn(worker_report["run_id"], {
            item["run_id"] for item in state["tasks"]["a"]["evidence"]["traceability_runs"]
        })
        evidence.checkpoint_run(self.root, "w", "a", worker_report["run_id"])
        rows = json.loads(ledger.read_text())

        # A malformed pending Green must be rejected before repairing its
        # ledger entry or publishing a new coordinator checkpoint.
        green_path = self.root / "work/w/traceability/runs" / green["run_id"] / "results.json"
        green_original = green_path.read_bytes()
        ledger_original = ledger.read_bytes()
        state_path = self.root / "work/w/inner-loop/state.json"
        state_before = state_path.read_bytes()
        malformed = json.loads(green_original)
        malformed["executions"][0]["runner_id"] = "unplanned-runner"
        malformed["executions"][0]["argv"] = ["python3", "-m", "unittest", "unplanned_suite"]
        malformed["cases"][0]["phase"] = "red"
        green_path.write_text(json.dumps(malformed, indent=2) + "\n")
        ledger.write_text(json.dumps([row for row in rows if row["run_id"] != green["run_id"]]) + "\n")
        try:
            with self.assertRaises(evidence.NotIntegrable):
                evidence.checkpoint_run(self.root, "w", "a", green["run_id"])
            self.assertEqual(state_path.read_bytes(), state_before)
            self.assertNotIn(green["run_id"], [row["run_id"] for row in json.loads(ledger.read_text())])
        finally:
            green_path.write_bytes(green_original)
            ledger.write_bytes(ledger_original)

        ledger.write_text(json.dumps([row for row in rows if row["run_id"] != red["run_id"]]) + "\n")
        self.assertTrue(
            callable(getattr(evidence, "checkpoint_run", None)),
            "coordinator must recover a complete report interrupted before ledger insertion",
        )
        evidence.checkpoint_run(self.root, "w", "a", red["run_id"])
        before = ledger.read_bytes()
        evidence.checkpoint_run(self.root, "w", "a", red["run_id"])
        self.assertEqual(ledger.read_bytes(), before, "replaying a finalized run must be idempotent")
        state = load_state(self.root, "w")
        recorded = {item["run_id"] for item in state["tasks"]["a"]["evidence"]["traceability_runs"]}
        self.assertIn(red["run_id"], recorded)

        # The task branch holds this Green candidate while coordinator HEAD is
        # still at the task base, the state immediately before fast-forward.
        self.git("branch", "task-a", green["candidate_sha"])
        self.git("reset", "--hard", self.anchor_commit)
        from inner_loop.state import cas_apply
        current = load_state(self.root, "w")
        cas_apply(self.root, "w", current["revision"],
                  lambda doc: doc["tasks"]["a"].update(task_branch="task-a"))
        try:
            evidence.checkpoint_run(self.root, "w", "a", green["run_id"])
        except Exception as exc:
            self.fail(f"selected isolated task candidate must finalize before FF: {exc}")
        state = load_state(self.root, "w")
        self.assertIn(green["run_id"], {
            item["run_id"] for item in state["tasks"]["a"]["evidence"]["traceability_runs"]
        })

    def test_old_pinned_runner_handoff(self):
        from inner_loop.evidence import snapshot_runner
        self.write(".agents/verification.yaml",
                   "schema: ask-checkplan/v1\nno_production_datastore: true\n"
                   "checks:\n  - id: fixture\n    tier: mandatory\n    command: 'true'\n")
        self.write("_ask/policies/delegation.md",
                   "Coordinator delegates review to an identified review agent.\n")
        self.commit("CR-3 old-runner integration policy")
        _red, green = self._real_traceability_pair(old_runner=True)
        old_sha = load_state(self.root, "w")["tasks"]["a"]["base_sha"]
        from verification.traceability.contracts import digest
        from verification.traceability.evidence import (
            inventory, load_accepted, record_test_review, source_digests, write_json,
        )
        contracts = load_accepted(self.root, "w", green["candidate_sha"], green["candidate_sha"])
        plan = contracts["plan"]
        actual = inventory(self.root, contracts["pin"]["contract_sha"], green["candidate_sha"], plan)
        review = {
            "schema": "ask-test-review/v2", "reviewer": "fixture-independent",
            "candidate_sha": green["candidate_sha"], "base_sha": contracts["pin"]["contract_sha"],
            "spec_digest": digest(contracts["spec"]), "plan_digest": digest(plan),
            "scope": "task", "task_id": "a", "test_ids": ["T-A", "T-B"],
            "criterion_ids": ["C1"],
            "source_digests": source_digests(self.root, green["candidate_sha"], plan, ["T-A", "T-B"]),
            "inspected_sources": actual["inspected_sources"], "changed_cases": actual["changed_cases"],
            "inventory_exclusions": {name: "Fixture source is covered by its mapped assertion."
                                     for name in actual["unmapped_cases"]},
            "criteria": [{"id": "C1", "coverage_decision": "APPROVED",
                          "assessment": "Both accepted cases compare source to a literal value.",
                          "type_adequacy": {"integration": {"decision": "APPROVED",
                              "assessment": "The trusted runner executes the committed candidate."}}}],
            "tests": [{"id": test_id, "decision": "APPROVED",
                       "assertion_assessment": "Compares source against the literal green value.",
                       "counterexample": "The committed red value fails the assertion.",
                       "tdd_continuity_assessment": "The same assertion is recorded for red and green."}
                      for test_id in ("T-A", "T-B")],
        }
        review_path = "work/w/traceability/old-runner-review.json"
        write_json(self.root / review_path, review)
        record_test_review(self.root, "w", green["candidate_sha"], green["candidate_sha"],
                           review_path, "fixture-coordinator", review_document=review)
        with tempfile.TemporaryDirectory() as tmp:
            runner, _digest = snapshot_runner(self.root, old_sha, Path(tmp) / "trusted")
            expected = subprocess.check_output(
                ["git", "show", f"{old_sha}:.agents/ask/verification/run.py"], cwd=self.root,
            )
            self.assertEqual(runner.read_bytes(), expected)
            output = self.root / "work/w/inner-loop/evidence/old-runner-verification.json"
            env = dict(os.environ, ASK_ROOT=str(self.root), ASK_WORK_ID="w",
                       ASK_TRACEABILITY_RUNTIME_ROOT=str(self.root),
                       ASK_TRACEABILITY_ANCHOR_SHA=old_sha,
                       ASK_TRACEABILITY_SCOPE="task", ASK_TRACEABILITY_TASK_ID="a",
                       VERIFY_JSON=str(output), VERIFY_OUT_DIR=str(output.parent))
            completed = subprocess.run([sys.executable, str(runner)], cwd=self.root, env=env,
                                       capture_output=True, text=True, timeout=60)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            receipt = json.loads((self.root / "work/w/traceability/completion.json").read_text())
            self.assertEqual(receipt["status"], "pass")
            report_ids = {Path(path).parts[4] for path in receipt["execution_artifacts"]
                          if "/runs/" in path and path.endswith(".log")}
            self.assertTrue(report_ids)
            from inner_loop import evidence
            self.assertFalse(report_ids & {
                item["run_id"] for item in load_state(self.root, "w")["tasks"]["a"]
                ["evidence"].get("traceability_runs", [])
            }, "the old runner is a worker; only its parent may publish milestones")

            # Incomplete historical schemas are diagnosed instead of being
            # accepted as milestones.
            run_id = sorted(report_ids)[0]
            result_path = self.root / "work/w/traceability/runs" / run_id / "results.json"
            valid = result_path.read_bytes()
            malformed = json.loads(valid)
            malformed["schema"] = "ask-test-results/v999"
            ledger = self.root / "work/w/traceability/executions.json"
            ledger_valid = ledger.read_bytes()
            result_path.write_text(json.dumps(malformed) + "\n")
            entries = json.loads(ledger.read_text())
            ledger.write_text(json.dumps([item for item in entries if item["run_id"] != run_id]) + "\n")
            try:
                with self.assertRaisesRegex(evidence.NotIntegrable, "migration_required|incomplete"):
                    evidence.checkpoint_run(self.root, "w", "a", run_id)
            finally:
                result_path.write_bytes(valid)
                ledger.write_bytes(ledger_valid)

            # A supported report schema with required structural fields
            # missing is also incomplete evidence, not a repairable Green.
            incomplete = json.loads(valid)
            incomplete.pop("cases", None)
            result_path.write_text(json.dumps(incomplete) + "\n")
            ledger.write_text(json.dumps([item for item in entries if item["run_id"] != run_id]) + "\n")
            state_before = (self.root / "work/w/inner-loop/state.json").read_bytes()
            try:
                with self.assertRaisesRegex(evidence.NotIntegrable,
                                            "migration_required/incomplete"):
                    evidence.checkpoint_run(self.root, "w", "a", run_id)
                self.assertEqual((self.root / "work/w/inner-loop/state.json").read_bytes(),
                                 state_before)
                self.assertNotIn(run_id, {item["run_id"] for item in json.loads(ledger.read_text())})
            finally:
                result_path.write_bytes(valid)
                ledger.write_bytes(ledger_valid)

            # Exercise the actual parent handoff: the coordinator pins and
            # runs the historical verifier, consumes only that completion
            # receipt, validates each report, then integrates the candidate.
            task_result = {
                "schema": "ask-task-result/v2", "work_id": "w", "task_id": "a",
                "base_sha": old_sha, "candidate_sha": green["candidate_sha"],
                "tdd": {"seam": "src/a.py",
                        "red": {"command": "fixture", "output": "assertion failed", "exit_code": 1},
                        "green": {"command": "fixture", "output": "passed", "exit_code": 0}},
                "exemption": None,
            }
            task_result_path = self.root / "work/w/inner-loop/results/a.json"
            task_result_path.parent.mkdir(parents=True, exist_ok=True)
            task_result_path.write_text(json.dumps(task_result, indent=2) + "\n")
            coordinator_review = self.root / "work/w/inner-loop/evidence/review.md"
            coordinator_review.parent.mkdir(parents=True, exist_ok=True)
            coordinator_review.write_text("Reviewer: fixture-independent; APPROVED\n")
            evidence.record_review(self.root, "w", "a", "fixture-independent",
                                   "_ask/policies/delegation.md",
                                   "work/w/inner-loop/evidence/review.md")
            from inner_loop.driver import integrate_ready
            integrate_ready(self.root, "w", "a")
            final_receipt = json.loads(
                (self.root / "work/w/traceability/completion.json").read_text()
            )
            final_ids = {Path(path).parts[4] for path in final_receipt["execution_artifacts"]
                         if "/runs/" in path and path.endswith(".log")}
            self.assertTrue(final_ids, "historical runner completion receipt must name task runs")
            state = load_state(self.root, "w")
            self.assertEqual(state["tasks"]["a"]["status"], "integrated")
            recorded = {item["run_id"] for item in state["tasks"]["a"]["evidence"]
                        ["traceability_runs"]}
            self.assertEqual(recorded, final_ids)

    def test_interrupt_and_reopen_preserve_attempt_history(self):
        self.write("accepted.json", json.dumps({"plan_review": {"plan_digest": "plan-before"}}) + "\n")
        self.commit("accepted plan review identity")
        self.git("update-ref", "refs/ask/accepted-tests/w", self.git("rev-parse", "HEAD"))
        started = self.run_cli("run", "w")
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        self.assertIn("running=a", started.stdout)

        state_path = self.root / "work/w/inner-loop/state.json"
        before = json.loads(state_path.read_text(encoding="utf-8"))
        old_plan_ref = self.git("rev-parse", "refs/ask/accepted-tests/w")
        execution_rows = [
            {
                "run_id": "old-red-1",
                "digest": "1" * 64,
                "phase": "red",
                "scope": "task",
                "task_id": "a",
                "candidate_sha": self.anchor_commit,
                "spec_digest": "spec-before",
                "plan_digest": "plan-before",
            },
            {
                "run_id": "old-red-2",
                "digest": "2" * 64,
                "phase": "red",
                "scope": "task",
                "task_id": "a",
                "candidate_sha": self.anchor_commit,
                "spec_digest": "spec-before",
                "plan_digest": "plan-before",
            },
        ]
        ledger = self.root / "work/w/traceability/executions.json"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(json.dumps(execution_rows) + "\n", encoding="utf-8")
        publish(self.root, "w", before)
        interrupted = self.run_cli("interrupt", "w", "a", "--reason", "accepted plan amendment")
        self.assertEqual(interrupted.returncode, 0, interrupted.stdout + interrupted.stderr)

        stopped = json.loads(state_path.read_text(encoding="utf-8"))
        task = stopped["tasks"]["a"]
        self.assertEqual(task["status"], "interrupted")
        self.assertEqual(len(task["attempt_history"]), 1)
        prior = task["attempt_history"][0]
        self.assertEqual(prior["status"], "interrupted")
        self.assertEqual(prior["base_sha"], before["tasks"]["a"]["base_sha"])
        self.assertEqual(prior["reason"], "accepted plan amendment")
        self.assertEqual(prior["accepted_plan_ref"], old_plan_ref)
        self.assertEqual(prior.get("accepted_plan_digest"), "plan-before")
        self.assertEqual(prior["execution_runs"], execution_rows)
        self.assertTrue(prior["attempt_id"])

        # A generic CAS cannot erase the attempt that interrupt_task archived.
        from inner_loop.state import ProtocolViolation, cas_apply
        before_rollback = load_state(self.root, "w")
        with self.assertRaisesRegex(ProtocolViolation, "attempt history cannot be removed or rewritten"):
            cas_apply(self.root, "w", before_rollback["revision"],
                      lambda doc: doc["tasks"]["a"].update(attempt_history=[]))
        self.assertEqual(load_state(self.root, "w")["tasks"]["a"]["attempt_history"],
                         before_rollback["tasks"]["a"]["attempt_history"])

        quiescent = self.run_cli("run", "w")
        self.assertEqual(quiescent.returncode, 0, quiescent.stdout + quiescent.stderr)
        self.assertEqual(quiescent.stdout.strip(), "quiescent")

        premature = self.run_cli("reopen", "w", "a", "--reason", "must wait for plan acceptance")
        self.assertNotEqual(premature.returncode, 0)
        self.assertIn("accept the reviewed plan amendment", premature.stdout + premature.stderr)
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8"))["tasks"]["a"]["attempt_history"],
            task["attempt_history"],
        )

        self.write("accepted.json", json.dumps({"plan_review": {"plan_digest": "plan-after"}}) + "\n")
        self.commit("accept amended test obligations")
        new_plan_ref = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/ask/accepted-tests/w", new_plan_ref)
        reopened = self.run_cli("reopen", "w", "a", "--reason", "amended plan accepted")
        self.assertEqual(reopened.returncode, 0, reopened.stdout + reopened.stderr)
        resumed = json.loads(state_path.read_text(encoding="utf-8"))
        current = resumed["tasks"]["a"]
        self.assertEqual(current["status"], "running")
        self.assertNotEqual(current["attempt_id"], prior["attempt_id"])
        self.assertEqual(current["accepted_plan_ref"], new_plan_ref)
        self.assertEqual(current.get("accepted_plan_digest"), "plan-after")
        self.assertEqual(current["attempt_history"], task["attempt_history"])
        self.assertEqual(current["attempt_history"][0]["reason"], "accepted plan amendment")

    def test_scope_compatible_historical_task_result_survives_plan_amendment(self):
        self.start_candidate()
        # Accept a metadata-only plan amendment after the immutable task base,
        # then make the task candidate from that amended contract. The result
        # must remain tied to this contract even when the base-time pin differs.
        self.git("reset", "--hard", self.anchor_commit)
        historical_plan = copy.deepcopy(self.old_plan)
        historical_plan["tests"][1]["change_kind"] = "regression"
        self.write("work/w/test-plan.json", json.dumps(historical_plan, sort_keys=True))
        self.commit("accept a metadata-only plan amendment during the attempt")
        historical_contract = self.git("rev-parse", "HEAD")
        historical_plan_digest = self.json_digest(historical_plan)
        historical_pin = {
            "schema": "ask-accepted-tests/v1", "work_id": "w",
            "contract_sha": historical_contract, "spec_digest": self.old_spec_digest,
            "plan_digest": historical_plan_digest, "graph_digest": self.old_graph_digest,
        }
        self.write("work/w/traceability-accepted.json", json.dumps(historical_pin) + "\n")
        self.commit("pin the amended plan")
        self.write("src/a.py", "candidate = True\n# amended contract\n")
        self.commit("candidate under amended historical contract")
        self.candidate = self.git("rev-parse", "HEAD")
        task_result = json.loads(self.result_path.read_text(encoding="utf-8"))
        task_result.update(candidate_sha=self.candidate, contract_sha=historical_contract)
        self.result_path.write_text(json.dumps(task_result, indent=2) + "\n", encoding="utf-8")
        original_result = self.result_path.read_bytes()
        state_path = self.root / "work/w/inner-loop/state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["a"]
        task.update(status="integrated", result_path="work/w/inner-loop/results/a.json")
        state["coordinator_sha"] = self.candidate
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        self.git("update-ref", "-d", "refs/ask/inner-loop/w")

        amended = copy.deepcopy(historical_plan)
        moved = next(test for test in amended["tests"] if test["id"] == "T-B")
        moved["task_id"] = "b"
        amended["task_scopes"] = [
            {"task_id": "a", "test_ids": ["T-A"]},
            {"task_id": "b", "test_ids": ["T-B"]},
        ]
        self.write("work/w/test-plan.json", json.dumps(amended, sort_keys=True))
        self.commit("move an unrelated obligation to task b")
        current_contract = self.git("rev-parse", "HEAD")
        current_plan_digest = self.json_digest(amended)
        self.write(
            "work/w/traceability-accepted.json",
            json.dumps({"schema": "ask-accepted-tests/v1", "work_id": "w",
                        "contract_sha": current_contract, "spec_digest": self.old_spec_digest,
                        "plan_digest": current_plan_digest, "graph_digest": self.old_graph_digest}) + "\n",
        )
        self.commit("record amended accepted plan")
        self.write(
            "work/w/traceability/executions.json",
            "[]\n",
        )
        runner_source = self.root / ".agents/ask/verification/traceability/unittest_runner.py"
        log_path = "work/w/traceability/runs/green-a/exec-a.log"
        log_bytes = b"fixture green execution output\n"
        self.write(log_path, log_bytes)
        source_digest = hashlib.sha256((self.root / "src/a.py").read_bytes()).hexdigest()
        report = {
            "schema": "ask-test-results/v1", "run_id": "green-a",
            "candidate_sha": self.candidate, "spec_digest": self.old_spec_digest,
            "plan_digest": historical_plan_digest, "scope": "task", "task_id": "a",
            "runner_identity": {"capability": "ask-traceability/v1",
                                "adapter_digest": hashlib.sha256(runner_source.read_bytes()).hexdigest()},
            "executions": [{"id": "exec-a", "phase": "final_green", "runner_id": "fixture",
                            "exit_code": 0, "collection_status": "ok",
                            "source_sha": self.candidate, "argv": ["python", "-m", "unittest", "fixture"],
                            "adapter": "unittest", "output_artifact": log_path,
                            "output_digest": hashlib.sha256(log_bytes).hexdigest()}],
            "cases": [{"test_id": test_id, "case_id": case_id, "runner_id": "fixture",
                       "execution_id": "exec-a", "phase": "final_green", "outcome": "passed",
                       "source_sha": self.candidate, "source_digests": {"src/a.py": source_digest},
                       "output_artifact": log_path,
                       "output_digest": hashlib.sha256(log_bytes).hexdigest()}
                      for test_id, case_id in (("T-A", "tests.test_a"), ("T-B", "tests.test_b"))],
        }
        report_raw = json.dumps(report, sort_keys=True, separators=(",", ":"))
        self.write("work/w/traceability/runs/green-a/results.json", report_raw)
        ledger_row = {"run_id": "green-a", "digest": hashlib.sha256(report_raw.encode()).hexdigest(),
                      "phase": "final_green", "scope": "task", "task_id": "a",
                      "candidate_sha": self.candidate, "spec_digest": self.old_spec_digest,
                      "plan_digest": historical_plan_digest}
        self.write("work/w/traceability/executions.json", json.dumps([ledger_row]) + "\n")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        publish(self.root, "w", state)

        result = inspect_recovery(self.root, "w", load_graph(self.root, "w"), state)
        self.assertIsNone(result, result)
        self.assertEqual(self.result_path.read_bytes(), original_result)
        self.assertEqual(json.loads(self.result_path.read_text())["contract_sha"], historical_contract)

        # Normal CR-2 execution may append new traceability evidence between
        # coordinator checkpoints; unchanged historical evidence still carries.
        active_report = {
            "schema": "ask-test-results/v1", "run_id": "green-b",
            "candidate_sha": self.candidate, "spec_digest": self.old_spec_digest,
            "plan_digest": current_plan_digest, "scope": "task", "task_id": "b",
            "runner_identity": report["runner_identity"],
            "executions": [{"id": "exec-b", "phase": "final_green", "runner_id": "fixture",
                            "exit_code": 0, "collection_status": "ok",
                            "source_sha": self.candidate, "argv": ["python", "-m", "unittest", "fixture"],
                            "adapter": "unittest",
                            "output_artifact": "work/w/traceability/runs/green-b/exec-b.log",
                            "output_digest": hashlib.sha256(b"active output\n").hexdigest()}],
            "cases": [{"test_id": "T-B", "case_id": "tests.test_b", "runner_id": "fixture",
                       "execution_id": "exec-b", "phase": "final_green", "outcome": "passed",
                       "source_sha": self.candidate, "source_digests": {"src/a.py": source_digest},
                       "output_artifact": "work/w/traceability/runs/green-b/exec-b.log",
                       "output_digest": hashlib.sha256(b"active output\n").hexdigest()}],
        }
        active_raw = json.dumps(active_report, sort_keys=True, separators=(",", ":"))
        self.write("work/w/traceability/runs/green-b/exec-b.log", b"active output\n")
        self.write("work/w/traceability/runs/green-b/results.json", active_raw)
        active_row = {"run_id": "green-b", "digest": hashlib.sha256(active_raw.encode()).hexdigest(),
                      "phase": "final_green", "scope": "task", "task_id": "b",
                      "candidate_sha": self.candidate, "spec_digest": self.old_spec_digest,
                      "plan_digest": current_plan_digest}
        self.write("work/w/traceability/executions.json", json.dumps([ledger_row, active_row]) + "\n")
        after_append = inspect_recovery(self.root, "w", load_graph(self.root, "w"), state)
        self.assertIsNone(after_append, after_append)

        # A digest-valid checkpoint cannot turn a failed run or ambiguous case
        # identity into historical Green evidence.
        malformed_failures = []
        for malformed in ("failed_execution", "failed_collection", "wrong_runner",
                          "wrong_runner_config", "split_execution", "duplicate_case",
                          "wrong_runner_identity", "missing_source_digest", "wrong_source_digest",
                          "wrong_output_digest", "case_output_binding"):
            invalid_report = copy.deepcopy(report)
            if malformed == "failed_execution":
                invalid_report["executions"][0]["exit_code"] = 1
            elif malformed == "failed_collection":
                invalid_report["executions"][0]["collection_status"] = "error"
            elif malformed == "wrong_runner":
                invalid_report["cases"][0]["runner_id"] = "unplanned-runner"
            elif malformed == "wrong_runner_config":
                invalid_report["executions"][0]["argv"] = ["python", "untrusted-runner"]
            elif malformed == "split_execution":
                first = invalid_report["executions"][0]
                first["id"] = "exec-a-1"
                second = dict(first, id="exec-a-2")
                invalid_report["executions"].append(second)
                invalid_report["cases"][0]["execution_id"] = "exec-a-1"
                invalid_report["cases"][1]["execution_id"] = "exec-a-2"
            elif malformed == "wrong_runner_identity":
                invalid_report["runner_identity"]["capability"] = "untrusted"
            elif malformed == "missing_source_digest":
                invalid_report["cases"][0].pop("source_digests")
            elif malformed == "wrong_source_digest":
                invalid_report["cases"][0]["source_digests"]["src/a.py"] = "0" * 64
            elif malformed == "wrong_output_digest":
                invalid_report["executions"][0]["output_digest"] = "0" * 64
                for case in invalid_report["cases"]:
                    case["output_digest"] = "0" * 64
            elif malformed == "case_output_binding":
                invalid_report["cases"][0]["output_artifact"] = "work/w/traceability/runs/other/exec.log"
            else:
                duplicate = copy.deepcopy(invalid_report["cases"][0])
                duplicate["outcome"] = "failed"
                invalid_report["cases"].append(duplicate)
            invalid_raw = json.dumps(invalid_report, sort_keys=True, separators=(",", ":"))
            self.write("work/w/traceability/runs/green-a/results.json", invalid_raw)
            invalid_row = dict(ledger_row, digest=hashlib.sha256(invalid_raw.encode()).hexdigest())
            self.write("work/w/traceability/executions.json", json.dumps([invalid_row, active_row]) + "\n")
            publish(self.root, "w", state)
            invalid = inspect_recovery(self.root, "w", load_graph(self.root, "w"), state)
            if (invalid is None or not any("TaskResult contract identity mismatch" in conflict
                                           for conflict in invalid["conflicts"])):
                malformed_failures.append(malformed)
        self.assertEqual(malformed_failures, [],
                         "checkpointed Green must require recovery for every malformed case")

        self.write("work/w/traceability/runs/green-a/results.json", report_raw)
        self.write("work/w/traceability/executions.json", json.dumps([ledger_row, active_row]) + "\n")
        publish(self.root, "w", state)

        # A fabricated matching row and a report edited after checkpoint publication
        # cannot authorize carry-forward.
        self.write("work/w/traceability/executions.json", json.dumps([{
            "run_id": "green-a", "phase": "final_green", "scope": "task", "task_id": "a",
            "candidate_sha": self.candidate, "spec_digest": self.old_spec_digest,
            "plan_digest": self.old_plan_digest,
        }]) + "\n")
        fabricated = inspect_recovery(self.root, "w", load_graph(self.root, "w"), state)
        self.assertIsNotNone(fabricated, "fabricated green evidence must require recovery")
        self.assertIn("runtime traceability evidence differs from the retained checkpoint",
                      fabricated["conflicts"])
        self.assertTrue(any("TaskResult contract identity mismatch" in conflict
                            for conflict in fabricated["conflicts"]))
        self.write("work/w/traceability/executions.json", json.dumps([ledger_row]) + "\n")
        publish(self.root, "w", state)

        changed = copy.deepcopy(amended)
        next(test for test in changed["tests"] if test["id"] == "T-A")["scenario"]["then"] = ["different behavior"]
        self.write("work/w/test-plan.json", json.dumps(changed, sort_keys=True))
        self.commit("change a retained task obligation")
        changed_contract = self.git("rev-parse", "HEAD")
        self.write(
            "work/w/traceability-accepted.json",
            json.dumps({"schema": "ask-accepted-tests/v1", "work_id": "w",
                        "contract_sha": changed_contract, "spec_digest": self.old_spec_digest,
                        "plan_digest": self.json_digest(changed), "graph_digest": self.old_graph_digest}) + "\n",
        )
        self.commit("record changed accepted plan")
        rejected = inspect_recovery(self.root, "w", load_graph(self.root, "w"), state)
        self.assert_recovery_required(
            subprocess.CompletedProcess([], 1, stdout=json.dumps(rejected), stderr=""),
            "TaskResult contract identity mismatch",
        )

        changed_spec = copy.deepcopy(self.spec)
        changed_spec["criteria"][0]["then"] = ["changed specification"]
        self.write("specs/current/w.json", json.dumps(changed_spec, sort_keys=True))
        self.commit("change the accepted specification")
        changed_contract = self.git("rev-parse", "HEAD")
        self.write(
            "work/w/traceability-accepted.json",
            json.dumps({"schema": "ask-accepted-tests/v1", "work_id": "w",
                        "contract_sha": changed_contract,
                        "spec_digest": self.json_digest(changed_spec),
                        "plan_digest": self.json_digest(changed),
                        "graph_digest": self.old_graph_digest}) + "\n",
        )
        self.commit("record changed accepted specification")
        rejected_spec = inspect_recovery(self.root, "w", load_graph(self.root, "w"), state)
        self.assert_recovery_required(
            subprocess.CompletedProcess([], 1, stdout=json.dumps(rejected_spec), stderr=""),
            "TaskResult contract identity mismatch",
        )

    def test_interrupted_candidate_paths_do_not_block_dependent_tasks(self):
        started = self.run_cli("run", "w")
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        state_path = self.root / "work/w/inner-loop/state.json"
        base = json.loads(state_path.read_text(encoding="utf-8"))["coordinator_sha"]
        self.write("src/a.py", "candidate = True\n")
        self.commit("candidate change owned by task a")
        candidate = self.git("rev-parse", "HEAD")

        interrupted = self.run_cli("interrupt", "w", "a", "--reason", "accepted plan amendment")
        self.assertEqual(interrupted.returncode, 0, interrupted.stdout + interrupted.stderr)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["a"]["attempt_history"][-1].get("interrupted_candidate_sha"), candidate)
        checkpoint = read_checkpoint(self.root, "w")
        self.assertIsNotNone(checkpoint)
        retained = subprocess.run(
            ["git", "merge-base", "--is-ancestor", candidate, checkpoint[0]],
            cwd=self.root, capture_output=True, text=True,
        )
        self.assertEqual(retained.returncode, 0, retained.stderr)
        quiescent = self.run_cli("run", "w")
        self.assertEqual(quiescent.returncode, 0, quiescent.stdout + quiescent.stderr)
        self.assertEqual(quiescent.stdout.strip(), "quiescent")

        self.write("src/a.py", "candidate = 'external change'\n")
        self.commit("unattributed change after interruption")
        refused = self.run_cli("run", "w")
        self.assert_recovery_required(refused, "src/a.py")
        self.assertEqual(
            subprocess.run(["git", "merge-base", "--is-ancestor", base, candidate],
                           cwd=self.root, capture_output=True).returncode,
            0,
        )

    def assert_recovery_required(self, result, *paths):
        output = result.stdout + result.stderr
        self.assertIn("recovery_required", output)
        for path in paths:
            self.assertIn(path, output)

    def test_missing_state_retained_result(self):
        self.start_candidate()
        result_bytes = self.result_path.read_bytes()
        review_bytes = self.review_path.read_bytes()
        candidate = self.git("rev-parse", "HEAD")
        state_path = self.root / "work/w/inner-loop/state.json"
        self.git("update-ref", "-d", "refs/ask/inner-loop/w")
        state_path.unlink()

        for command in (("run", "w"), ("resume", "w")):
            result = self.run_cli(*command)
            self.assert_recovery_required(
                result,
                "w",
                "work/w/inner-loop/results/a.json",
                "work/w/inner-loop/evidence/review-a.json",
            )
            self.assertFalse(state_path.exists(), "recovery must not replace the missing cache")
            self.assertEqual(self.result_path.read_bytes(), result_bytes)
            self.assertEqual(self.review_path.read_bytes(), review_bytes)
            self.assertEqual(self.git("rev-parse", "HEAD"), candidate)

    def test_pending_state_conflicts_with_execution(self):
        self.start_candidate()
        state_path = self.root / "work/w/inner-loop/state.json"
        original = json.loads(state_path.read_text())
        original["tasks"]["a"].update(status="pending", base_sha="", result_path="")
        original["coordinator_sha"] = self.anchor_commit
        raw = json.dumps(original, indent=2) + "\n"

        for command in (
            ("run", "w"),
            ("cas-init", "w"),
            ("spawn-writer", "w", "a"),
            ("status", "w"),
            ("reconcile", "w"),
        ):
            state_path.write_text(raw, encoding="utf-8")
            result = self.run_cli(*command)
            self.assert_recovery_required(result, "w", "work/w/inner-loop/results/a.json")
            self.assertEqual(state_path.read_text(encoding="utf-8"), raw)

        corrupt = "{broken cache bytes\n"
        state_path.write_text(corrupt, encoding="utf-8")
        result = self.run_cli("cas-init", "w")
        self.assert_recovery_required(result, "state.json", "work/w/inner-loop/state.json")
        self.assertEqual(state_path.read_text(encoding="utf-8"), corrupt)

    def test_fresh_initialization_and_missing_legacy_evidence(self):
        started = self.run_cli("run", "w")
        self.assertEqual(started.returncode, 0, started.stderr + started.stdout)
        self.assertIn("running=a", started.stdout)
        state = json.loads((self.root / "work/w/inner-loop/state.json").read_text())
        self.assertEqual(state["coordinator_sha"], self.anchor_commit)
        self.assertEqual(state["tasks"]["a"]["base_sha"], self.anchor_commit)

        legacy = Path(self.temp.name) / "legacy"
        subprocess.run(["git", "clone", "-q", str(self.root), str(legacy)], check=True)
        subprocess.run(["git", "config", "user.email", "recovery@example.test"], cwd=legacy, check=True)
        subprocess.run(["git", "config", "user.name", "Recovery Test"], cwd=legacy, check=True)
        (legacy / "src/a.py").parent.mkdir(parents=True, exist_ok=True)
        (legacy / "src/a.py").write_text("unrecorded implementation\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/a.py"], cwd=legacy, check=True)
        subprocess.run(["git", "commit", "-qm", "unrecorded post-anchor source"], cwd=legacy, check=True)
        run = subprocess.run(
            [sys.executable, "-m", "inner_loop", "--root", str(legacy), "run", "w"],
            cwd=legacy,
            env={
                **os.environ,
                "PYTHONPATH": os.pathsep.join(
                    part for part in (str(SCRIPTS), os.environ.get("PYTHONPATH", "")) if part
                ),
            },
            capture_output=True,
            text=True,
        )
        self.assertIn("recovery_required", run.stdout + run.stderr)
        self.assertFalse((legacy / "work/w/inner-loop/state.json").exists())

    def test_running_task_changes_may_overlap_later_task_ownership(self):
        self.start_candidate()
        status = self.run_cli("status", "w")
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertIn("a\trunning", status.stdout)
        self.assertIn("b\tpending", status.stdout)

    def test_new_candidate_preserves_stale_rejected_review_history(self):
        self.start_candidate()
        result = json.loads(self.result_path.read_text())
        from inner_loop.state import cas_apply
        state = json.loads((self.root / "work/w/inner-loop/state.json").read_text())
        cas_apply(self.root, "w", state["revision"], lambda doc: doc["tasks"]["a"]["evidence"].update(
            review={
                "work_id": "w",
                "task_id": "a",
                "base_sha": self.anchor_commit,
                "candidate_sha": self.candidate,
                "result_digest": hashlib.sha256(self.result_path.read_bytes()).hexdigest(),
                "verdict": "REJECTED",
            }
        ))

        self.write("src/a.py", "candidate = True\n# review correction\n")
        self.commit("correct rejected candidate")
        result["candidate_sha"] = self.git("rev-parse", "HEAD")
        self.result_path.write_text(json.dumps(result) + "\n", encoding="utf-8")

        status = self.run_cli("status", "w")
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertIn("a\trunning", status.stdout)

    def test_contract_and_checkout_conflict(self):
        self.start_candidate()
        state_path = self.root / "work/w/inner-loop/state.json"
        state_before = state_path.read_bytes()
        result_path = self.root / "work/w/inner-loop/results/a.json"
        review_path = self.root / "work/w/inner-loop/evidence/review-a.json"
        original_result = json.loads(result_path.read_text())
        result_bytes = result_path.read_bytes()
        review_bytes = review_path.read_bytes()

        wrong_work = dict(original_result, work_id="other-work")
        result_path.write_text(json.dumps(wrong_work) + "\n", encoding="utf-8")
        refused = self.run_cli("run", "w")
        self.assert_recovery_required(refused, "work_id", "work/w/inner-loop/results/a.json")
        result_path.write_bytes(result_bytes)
        self.assertEqual(state_path.read_bytes(), state_before)
        self.assertEqual(review_path.read_bytes(), review_bytes)

        wrong_contract = dict(original_result, contract_sha="0" * 40)
        result_path.write_text(json.dumps(wrong_contract) + "\n", encoding="utf-8")
        refused = self.run_cli("run", "w")
        self.assert_recovery_required(refused, "contract", "work/w/inner-loop/results/a.json")
        result_path.write_bytes(result_bytes)

        missing_contract = dict(original_result)
        del missing_contract["contract_sha"]
        result_path.write_text(json.dumps(missing_contract) + "\n", encoding="utf-8")
        accepted_at_same_base = self.run_cli("status", "w")
        self.assertEqual(accepted_at_same_base.returncode, 0,
                         accepted_at_same_base.stdout + accepted_at_same_base.stderr)
        self.assertIn("a\trunning", accepted_at_same_base.stdout)
        result_path.write_bytes(result_bytes)

        state = json.loads(state_before)
        state["tasks"]["a"]["base_sha"] = ""
        state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")
        refused = self.run_cli("status", "w")
        empty_base_reported = (
            refused.returncode == 2
            and "base_sha" in refused.stdout + refused.stderr
            and "work/w/inner-loop/results/a.json" in refused.stdout + refused.stderr
        )
        state_path.write_bytes(state_before)
        self.assertTrue(empty_base_reported, "empty state base_sha must require recovery")

        self.git("switch", "-qc", "side-candidate", self.anchor_commit)
        self.write("src/a.py", "candidate outside coordinator ancestry\n")
        self.commit("side candidate")
        side_candidate = self.git("rev-parse", "HEAD")
        self.git("switch", "-q", "agent/w")
        wrong_candidate = dict(original_result, candidate_sha=side_candidate)
        result_path.write_text(json.dumps(wrong_candidate) + "\n", encoding="utf-8")
        refused = self.run_cli("run", "w")
        self.assert_recovery_required(refused, "candidate", "work/w/inner-loop/results/a.json")
        self.assertEqual(state_path.read_bytes(), state_before)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.candidate)

        pin_path = self.root / "work/w/traceability-accepted.json"
        pin = json.loads(pin_path.read_text())
        pin["contract_sha"] = self.candidate
        pin_path.write_text(json.dumps(pin) + "\n", encoding="utf-8")
        self.commit("change accepted contract after task base")
        missing_contract = dict(original_result)
        del missing_contract["contract_sha"]
        missing_contract["candidate_sha"] = self.git("rev-parse", "HEAD")
        result_path.write_text(json.dumps(missing_contract) + "\n", encoding="utf-8")
        refused = self.run_cli("status", "w")
        self.assert_recovery_required(refused, "contract", "work/w/inner-loop/results/a.json")

    def _checkpoint_ref(self):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "refs/ask/inner-loop/w"],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() if result.returncode == 0 else None

    def test_restore_deleted_runtime_cache(self):
        self.start_candidate()
        state_path = self.root / "work/w/inner-loop/state.json"
        revision = json.loads(state_path.read_text(encoding="utf-8"))["revision"]
        checkpointed = self.run_cli("cas-apply", "w", "--observed", str(revision))
        self.assertEqual(checkpointed.returncode, 0, checkpointed.stdout + checkpointed.stderr)
        before = state_path.read_bytes()
        result_before = self.result_path.read_bytes()
        review_before = self.review_path.read_bytes()
        checkpoint = self._checkpoint_ref()
        self.assertIsNotNone(checkpoint, "writer transitions must publish a retained checkpoint")

        state_path.unlink()
        restored = self.run_cli("status", "w")

        self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)
        self.assertEqual(self._checkpoint_ref(), checkpoint)
        self.assertEqual(state_path.read_bytes(), before)
        self.assertEqual(self.result_path.read_bytes(), result_before)
        self.assertEqual(self.review_path.read_bytes(), review_before)
        self.assertNotIn("integrated", restored.stdout)

    def test_crash_around_checkpoint_publication(self):
        self.start_candidate()
        initial = self._checkpoint_ref()
        self.assertIsNotNone(initial, "initial state must have a checkpoint before transition")
        state_path = self.root / "work/w/inner-loop/state.json"
        cached = state_path.read_bytes()
        revision = json.loads(cached)["revision"]

        before = self.run_cli("cas-apply", "w", "--observed", str(revision),
                              env={"ASK_INNER_LOOP_CRASH_AT": "before_ref_publication"})
        self.assertEqual(before.returncode, 75, before.stdout + before.stderr)
        self.assertEqual(self._checkpoint_ref(), initial)
        self.assertEqual(state_path.read_bytes(), cached)
        prior = self.run_cli("status", "w")
        self.assertEqual(prior.returncode, 0, prior.stdout + prior.stderr)
        self.assertEqual(json.loads(state_path.read_text())["revision"], revision)

        after = self.run_cli("cas-apply", "w", "--observed", str(revision),
                             env={"ASK_INNER_LOOP_CRASH_AT": "after_ref_publication"})
        self.assertEqual(after.returncode, 76, after.stdout + after.stderr)
        published = self._checkpoint_ref()
        self.assertNotEqual(published, initial)
        self.assertEqual(state_path.read_bytes(), cached)
        replayed = self.run_cli("status", "w")
        self.assertEqual(replayed.returncode, 0, replayed.stdout + replayed.stderr)
        self.assertEqual(self._checkpoint_ref(), published)
        restored = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(restored["revision"], revision + 1)

    def test_concurrent_checkpoint_writers(self):
        self.start_candidate()
        observed = json.loads((self.root / "work/w/inner-loop/state.json").read_text())["revision"]
        command = [sys.executable, "-m", "inner_loop", "--root", str(self.root),
                   "cas-apply", "w", "--observed", str(observed)]
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(SCRIPTS), env.get("PYTHONPATH", "")) if part
        )
        first = subprocess.Popen(command, cwd=self.root, env=env, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        second = subprocess.Popen(command, cwd=self.root, env=env, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        first_out, first_err = first.communicate(timeout=10)
        second_out, second_err = second.communicate(timeout=10)
        outcomes = [(first.returncode, first_out + first_err),
                    (second.returncode, second_out + second_err)]

        self.assertEqual(sorted(code for code, _ in outcomes), [0, 2], outcomes)
        self.assertEqual(sum("revision mismatch" in output for _, output in outcomes), 1, outcomes)
        state = json.loads((self.root / "work/w/inner-loop/state.json").read_text())
        self.assertEqual(state["revision"], observed + 1)
        self.assertIsNotNone(self._checkpoint_ref(), "the winning CAS must publish its checkpoint")

    def test_reject_incomplete_or_unsafe_checkpoint(self):
        self.start_candidate()
        missing_fixture_sha = "7a7d800d3d47459780858e1b12c41493f99537b4"
        failed_static = self.root / "work/w/traceability" / f"static-{missing_fixture_sha}.json"
        failed_static.parent.mkdir(parents=True, exist_ok=True)
        failed_static_raw = json.dumps(
            {"candidate_sha": missing_fixture_sha, "result": "fail"}, indent=2
        ).encode() + b"\n"
        failed_static.write_bytes(failed_static_raw)
        state_path = self.root / "work/w/inner-loop/state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        try:
            publish(self.root, "w", state)
        except CheckpointError as exc:
            self.fail(
                "a failed static receipt must be preserved without requiring its "
                f"diagnostic candidate commit: {exc}"
            )
        checkpoint_doc = read_checkpoint(self.root, "w")
        self.assertIsNotNone(checkpoint_doc)
        checkpoint_sha, _checkpoint_state, checkpoint_files = checkpoint_doc
        manifest, _ = _read_tree(self.root, checkpoint_sha)
        self.assertEqual(
            checkpoint_files["artifacts/work/w/traceability/" + failed_static.name],
            failed_static_raw,
        )
        self.assertNotIn(missing_fixture_sha, manifest["retained_commits"])

        checkpoint = self._checkpoint_ref()
        self.assertIsNotNone(checkpoint, "checkpoint validation requires a published baseline")
        state_before = state_path.read_bytes()
        result_before = self.result_path.read_bytes()
        review_before = self.review_path.read_bytes()

        invalid_blob = self.git("hash-object", "-w", self.write("invalid-checkpoint", "not a commit"))
        self.git("update-ref", "refs/ask/inner-loop/w", invalid_blob)
        refused = self.run_cli("resume", "w")

        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("recovery_required", refused.stdout + refused.stderr)
        self.assertEqual(state_path.read_bytes(), state_before)
        self.assertEqual(self.result_path.read_bytes(), result_before)
        self.assertEqual(self.review_path.read_bytes(), review_before)
        self.git("update-ref", "refs/ask/inner-loop/w", checkpoint)

    def test_stale_and_newer_cache(self):
        self.start_candidate()
        state_path = self.root / "work/w/inner-loop/state.json"
        old_cache = state_path.read_bytes()
        old_revision = json.loads(old_cache)["revision"]
        advanced = self.run_cli("cas-apply", "w", "--observed", str(old_revision))
        self.assertEqual(advanced.returncode, 0, advanced.stdout + advanced.stderr)
        checkpoint = self._checkpoint_ref()
        self.assertIsNotNone(checkpoint, "state mutation must publish a checkpoint")
        state_path.write_bytes(old_cache)

        replayed = self.run_cli("status", "w")
        self.assertEqual(replayed.returncode, 0, replayed.stdout + replayed.stderr)
        self.assertEqual(self._checkpoint_ref(), checkpoint)
        current = json.loads(state_path.read_text())
        self.assertEqual(current["revision"], old_revision + 1)

        divergent = dict(current)
        divergent["revision"] += 1
        divergent["coordinator_sha"] = self.anchor_commit
        divergent_raw = json.dumps(divergent, indent=2) + "\n"
        state_path.write_text(divergent_raw, encoding="utf-8")
        refused = self.run_cli("status", "w")
        self.assert_recovery_required(refused, "checkpoint", "state.json")
        self.assertEqual(state_path.read_text(encoding="utf-8"), divergent_raw)

    def test_retain_objects_after_gc_and_bundle_transfer(self):
        self.start_candidate()
        checkpoint = self._checkpoint_ref()
        self.assertIsNotNone(checkpoint, "writer transitions must publish retained checkpoints")
        for ref in self.git("for-each-ref", "--format=%(refname)").splitlines():
            if ref not in {"refs/ask/inner-loop/w", "refs/heads/agent/w"}:
                self.git("update-ref", "-d", ref)
        self.git("reflog", "expire", "--expire=now", "--all")
        self.git("gc", "--prune=now")
        self.assertEqual(self.git("cat-file", "-t", checkpoint), "commit")

        bundle = self.root / "checkpoint.bundle"
        exported = self.run_cli("checkpoint-export", "w", "--out", str(bundle))
        self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
        self.assertTrue(bundle.is_file())

        imported = Path(self.temp.name) / "imported"
        self.git("clone", "-q", "--no-local", str(self.root), str(imported))
        subprocess.run(["git", "update-ref", "-d", "refs/ask/inner-loop/w"],
                       cwd=imported, check=False)
        imported_env = {**os.environ, "PYTHONPATH": os.pathsep.join(
            part for part in (str(SCRIPTS), os.environ.get("PYTHONPATH", "")) if part
        )}
        missing = subprocess.run(
            [sys.executable, "-m", "inner_loop", "--root", str(imported), "status", "w"],
            cwd=imported, env=imported_env, capture_output=True, text=True,
        )
        self.assertEqual(missing.returncode, 2, missing.stdout + missing.stderr)
        self.assertEqual(json.loads(missing.stdout)["status"], "recovery_required")
        self.assertIn("no runtime attempt record", missing.stdout)
        self.assertNotIn("integrated", missing.stdout)
        for command in ("reconcile", "run", "resume"):
            diagnosed = subprocess.run(
                [sys.executable, "-m", "inner_loop", "--root", str(imported), command, "w"],
                cwd=imported, env=imported_env, capture_output=True, text=True,
            )
            self.assertEqual(diagnosed.returncode, 2,
                             diagnosed.stdout + diagnosed.stderr)
            self.assertIn("recovery_required", diagnosed.stdout + diagnosed.stderr)
            self.assertIn("no runtime attempt record", diagnosed.stdout + diagnosed.stderr)
            self.assertFalse((imported / "work/w/inner-loop/state.json").exists(),
                             f"{command} must not fabricate state without the checkpoint")
        result = subprocess.run(
            [sys.executable, "-m", "inner_loop", "--root", str(imported),
             "checkpoint-import", "w", str(bundle)],
            cwd=imported,
            env=imported_env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git("rev-parse", "refs/ask/inner-loop/w"), checkpoint)
        self.assertEqual(self.git("-C", str(imported), "rev-parse",
                                  "refs/ask/inner-loop/w"), checkpoint)
        restored = subprocess.run(
            [sys.executable, "-m", "inner_loop", "--root", str(imported), "status", "w"],
            cwd=imported, env=imported_env, capture_output=True, text=True,
        )
        self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)
        self.assertIn("revision=", restored.stdout)
        self.assertIn("a\trunning", restored.stdout)
        retained_state = json.loads(
            (imported / "work/w/inner-loop/state.json").read_text(encoding="utf-8")
        )
        retained_milestones = {
            task_id: (task["status"], task.get("attempt_id"),
                      task.get("evidence", {}).get("traceability_runs", []))
            for task_id, task in retained_state["tasks"].items()
        }
        for command in ("status", "reconcile", "run", "resume"):
            recovered = subprocess.run(
                [sys.executable, "-m", "inner_loop", "--root", str(imported), command, "w"],
                cwd=imported, env=imported_env, capture_output=True, text=True,
            )
            self.assertEqual(recovered.returncode, 0,
                             recovered.stdout + recovered.stderr)
            after = json.loads(
                (imported / "work/w/inner-loop/state.json").read_text(encoding="utf-8")
            )
            actual_milestones = {
                task_id: (task["status"], task.get("attempt_id"),
                          task.get("evidence", {}).get("traceability_runs", []))
                for task_id, task in after["tasks"].items()
            }
            self.assertEqual(actual_milestones, retained_milestones, command)

    def test_isolated_repair_initialization_and_legacy_handoff(self):
        fixture = Path(self.temp.name) / "legacy-product"
        fixture.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "agent/continuation-recovery"], cwd=fixture, check=True)
        subprocess.run(["git", "config", "user.email", "recovery@example.test"], cwd=fixture, check=True)
        subprocess.run(["git", "config", "user.name", "Recovery Test"], cwd=fixture, check=True)
        self.root = fixture
        self.write(
            ".gitignore",
            "work/continuation-recovery/inner-loop/state.json\n"
            "work/continuation-recovery/inner-loop/state.lock\n",
        )
        legacy_files = write_legacy_fixture(self.root)
        self.write("work/continuation-recovery/inner-loop/tasks.yaml", REPAIR_TASKS)
        self.commit("immutable blocked product fixture and isolated repair graph")
        contract_sha = self.git("rev-parse", "HEAD")
        self.write(
            "work/continuation-recovery/traceability-accepted.json",
            json.dumps({
                "schema": "ask-accepted-tests/v1",
                "work_id": "continuation-recovery",
                "contract_sha": contract_sha,
            }) + "\n",
        )
        self.commit("repair contract anchor")
        self.git("update-ref", "refs/ask/accepted-tests/continuation-recovery", self.git("rev-parse", "HEAD"))
        authority_ref = "refs/ask/accepted-tests/shorter-hashes"
        self.git("update-ref", authority_ref, self.git("rev-parse", "HEAD"))

        state_before = {name: (self.root / name).read_bytes() for name in legacy_files}
        authority_before = self.git("rev-parse", authority_ref)
        legacy = json.loads(state_before["work/shorter-hashes/inner-loop/state.json"])
        self.assertEqual(legacy["revision"], 11)
        self.assertEqual(legacy["tasks"]["1"]["status"], "integrated")
        self.assertEqual(legacy["tasks"]["2"]["status"], "blocked")
        self.assertTrue(all(legacy["tasks"][str(i)]["status"] == "pending" for i in range(3, 11)))
        self.assertEqual(LEGACY_AUTHORITY_SHA, "e1ca2a523c5417687479c09ffc1bf6c1cc337763")
        self.assertEqual(len(LEGACY_STATE_SHA256), 64)

        first = self.run_cli("run", "continuation-recovery")
        self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
        self.assertIn("running=CR-1", first.stdout)
        state_path = self.root / "work/continuation-recovery/inner-loop/state.json"
        repair_state = json.loads(state_path.read_text())
        self.assertEqual(set(repair_state["tasks"]), {"CR-1", "CR-2", "CR-3", "CR-4"})
        from inner_loop.state import cas_apply
        cas_apply(self.root, "continuation-recovery", repair_state["revision"],
                  lambda doc: doc["tasks"]["CR-1"].update(status="integrated"))
        second = self.run_cli("run", "continuation-recovery")
        self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
        self.assertIn("running=CR-2", second.stdout)
        self.assertEqual({name: (self.root / name).read_bytes() for name in legacy_files}, state_before)
        self.assertEqual(self.git("rev-parse", authority_ref), authority_before)


if __name__ == "__main__":
    unittest.main()
