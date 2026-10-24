"""Recovery guards exercised through fresh coordinator processes."""
from __future__ import annotations

import json
import hashlib
import os
import copy
import shutil
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

    def _real_traceability_pair(self, runner_count=1, old_runner=False, run_reports=True):
        """Run the accepted plan on real failing and passing commits."""
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
        if not run_reports:
            self.write("src/a.py", "green\n")
            self.commit("CR-3 real assertion green fixture")
            return red_sha, self.git("rev-parse", "HEAD")
        from verification.traceability.adapters import run_tests
        contracts = {"spec": self.spec, "plan": self.old_plan}
        red = run_tests(self.root, contracts, red_sha, "task", "a", "red")
        self.write("src/a.py", "green\n")
        self.commit("CR-3 real assertion green fixture")
        green_sha = self.git("rev-parse", "HEAD")
        green = run_tests(self.root, contracts, green_sha, "task", "a", "final_green")
        return red, green

    def test_checkpoint_real_red_and_green(self):
        red_sha, green_sha = self._real_traceability_pair(runner_count=2, run_reports=False)
        runs_dir = self.root / "work/w/traceability/runs"
        runs_dir.mkdir(parents=True, exist_ok=True)

        def run_traceability(candidate_sha, phase, crash_at):
            env = dict(
                os.environ,
                ASK_TRACEABILITY_RUNTIME_ROOT=str(self.root),
                ASK_TRACEABILITY_CRASH_AT=crash_at,
                PYTHONPATH=os.pathsep.join(
                    part for part in (
                        str(self.root / ".agents/ask"),
                        str(SCRIPTS),
                        os.environ.get("PYTHONPATH", ""),
                    ) if part
                ),
            )
            return subprocess.run(
                [sys.executable, "-m", "verification.traceability.cli",
                 "--root", str(self.root), "run", "w",
                 "--candidate-sha", candidate_sha,
                 "--anchor-sha", self.anchor_commit,
                 "--scope", "task", "--task-id", "a", "--phase", phase],
                cwd=self.root, env=env, capture_output=True, text=True,
            )

        def latest_report(before):
            created = sorted(path for path in runs_dir.iterdir()
                             if path.is_dir() and path.name not in before)
            self.assertEqual(len(created), 1, f"expected one newly published run, got {created}")
            report_path = created[0] / "results.json"
            self.assertTrue(report_path.is_file(), "run report must publish before the child exits")
            return created[0].name, json.loads(report_path.read_text(encoding="utf-8"))

        ledger_path = self.root / "work/w/traceability/executions.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []
        before = {path.name for path in runs_dir.iterdir() if path.is_dir()}
        red_exit = run_traceability(red_sha, "red", "after_report_publication")
        self.assertEqual(red_exit.returncode, 81, red_exit.stdout + red_exit.stderr)
        red_id, red = latest_report(before)
        ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []
        self.assertEqual(red["candidate_sha"], red_sha)
        self.assertEqual(red["cases"][0]["outcome"], "failed")
        self.assertFalse(any(row.get("run_id") == red_id for row in ledger),
                         "the process exit must precede ledger insertion")

        interrupted_checkpoint = self.run_cli(
            "checkpoint-run", "w", "a", "--run-id", red_id,
            env={"ASK_INNER_LOOP_CRASH_AT": "before_ref_publication"},
        )
        self.assertEqual(interrupted_checkpoint.returncode, 75,
                         interrupted_checkpoint.stdout + interrupted_checkpoint.stderr)
        checkpoint = read_checkpoint(self.root, "w")
        self.assertEqual(checkpoint[1]["tasks"]["a"]["evidence"].get("traceability_runs", []), [])

        resumed_red = self.run_cli("checkpoint-run", "w", "a", "--run-id", red_id)
        self.assertEqual(resumed_red.returncode, 0, resumed_red.stdout + resumed_red.stderr)
        red_checkpoint = read_checkpoint(self.root, "w")
        self.assertEqual(red_checkpoint[1]["tasks"]["a"]["evidence"]["traceability_runs"][0]["run_id"], red_id)

        before = {path.name for path in runs_dir.iterdir() if path.is_dir()}
        green_exit = run_traceability(green_sha, "final_green", "after_ledger_insertion")
        self.assertEqual(green_exit.returncode, 82, green_exit.stdout + green_exit.stderr)
        green_id, green = latest_report(before)
        self.assertEqual(green["candidate_sha"], green_sha)
        self.assertEqual(green["cases"][0]["outcome"], "passed")
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertTrue(any(row.get("run_id") == green_id for row in ledger),
                        "the child must exit after ledger insertion")

        interrupted_green_checkpoint = self.run_cli(
            "checkpoint-run", "w", "a", "--run-id", green_id,
            env={"ASK_INNER_LOOP_CRASH_AT": "after_ref_publication"},
        )
        self.assertEqual(interrupted_green_checkpoint.returncode, 76,
                         interrupted_green_checkpoint.stdout + interrupted_green_checkpoint.stderr)
        resumed = load_state(self.root, "w")
        recorded = resumed["tasks"]["a"]["evidence"]["traceability_runs"]
        self.assertEqual([row["run_id"] for row in recorded], [red_id, green_id])
        self.assertEqual([row["phase"] for row in recorded], ["red", "final_green"])
        self.assertEqual([row["candidate_sha"] for row in recorded], [red_sha, green_sha])
        self.assertEqual([row["digest"] for row in recorded],
                         [self.json_digest(red), self.json_digest(green)])

    def test_stale_review_preserves_execution(self):
        from _ask.tests.inner_loop_reliability import IntegrationTests
        from inner_loop.evidence import (
            NotIntegrable, checkpoint_run, read_candidate, validate_review,
        )
        result = unittest.TestResult()

        class ApprovedReviewCase(RecoveryTests, IntegrationTests):
            def setUp(self):
                RecoveryTests.setUp(self)

            def review(self, **options):
                from verification.traceability.contracts import digest
                from verification.traceability.evidence import (
                    inventory, load_accepted, record_test_review, source_digests,
                    write_json,
                )
                from inner_loop.evidence import record_review

                contracts = load_accepted(
                    self.root, "w", self.result["candidate_sha"], self.result["candidate_sha"]
                )
                plan = contracts["plan"]
                actual = inventory(
                    self.root, contracts["pin"]["contract_sha"], self.result["candidate_sha"], plan
                )
                test_ids = [test["id"] for test in plan["tests"]]
                review = {
                    "schema": "ask-test-review/v2", "reviewer": "fixture-independent",
                    "candidate_sha": self.result["candidate_sha"],
                    "base_sha": contracts["pin"]["contract_sha"],
                    "spec_digest": digest(contracts["spec"]),
                    "plan_digest": digest(plan), "scope": "task", "task_id": "a",
                    "test_ids": test_ids, "criterion_ids": ["C1"],
                    "source_digests": source_digests(self.root, self.result["candidate_sha"], plan),
                    "inspected_sources": actual["inspected_sources"],
                    "changed_cases": actual["changed_cases"],
                    "inventory_exclusions": {
                        name: "Fixture source is covered by its mapped assertion."
                        for name in actual["unmapped_cases"]
                    },
                    "criteria": [{
                        "id": "C1", "coverage_decision": "APPROVED",
                        "assessment": "Both accepted cases compare source to a literal value.",
                        "type_adequacy": {"integration": {
                            "decision": "APPROVED",
                            "assessment": "The trusted runner executes the committed candidate.",
                        }},
                    }],
                    "tests": [{
                        "id": test_id, "decision": "APPROVED",
                        "assertion_assessment": "Compares the committed source to a literal value.",
                        "counterexample": "The committed red value fails the assertion.",
                        "tdd_continuity_assessment": "The same assertion is recorded for red and green.",
                    } for test_id in test_ids],
                }
                path = "work/w/traceability/review-input.json"
                write_json(self.root / path, review)
                record_test_review(
                    self.root, "w", self.result["candidate_sha"], self.result["candidate_sha"],
                    path, "fixture-coordinator", review_document=review,
                )
                self.write("work/w/inner-loop/evidence/review.md",
                           "Reviewer: independent-agent; APPROVED\n")
                return record_review(
                    self.root, "w", "a", "independent-agent", "_ask/policies/delegation.md",
                    "work/w/inner-loop/evidence/review.md", **options,
                )

            def test_approved_review_cannot_be_reused_after_result_changes(self):
                red, green = self._real_traceability_pair()
                self.candidate = green["candidate_sha"]
                self.git("branch", "task-a", green["candidate_sha"])
                self.git("reset", "--hard", self.anchor_commit)
                from inner_loop.state import cas_apply
                current = load_state(self.root, "w")
                cas_apply(self.root, "w", current["revision"],
                          lambda doc: doc["tasks"]["a"].update(task_branch="task-a"))
                for report in (red, green):
                    checkpoint_run(self.root, "w", "a", report["run_id"])
                self.base = self.anchor_commit
                from verification.traceability.evidence import load_accepted
                accepted = load_accepted(
                    self.root, "w", self.candidate, self.candidate
                )
                self.result = {
                    "schema": "ask-task-result/v2", "work_id": "w", "task_id": "a",
                    "base_sha": self.base, "candidate_sha": self.candidate,
                    "contract_sha": accepted["pin"]["contract_sha"],
                    "tdd": {"seam": "src/a.py",
                            "red": {"command": "python -m unittest fixture", "output": "FAIL", "exit_code": 1},
                            "green": {"command": "python -m unittest fixture", "output": "PASS", "exit_code": 0}},
                    "exemption": None,
                }
                self.submit()
                self.review()
                before = load_state(self.root, "w")
                task_before = before["tasks"]["a"]
                execution_before = list(task_before["evidence"].get("traceability_runs", []))
                review_before = copy.deepcopy(task_before["evidence"]["review"])

                # Change the candidate after valid Red/Green and an approved
                # review. The old approval and execution history stay
                # recorded, but cannot authorize the new candidate.
                self.git("switch", "task-a")
                self.write("src/value", "candidate\n# changed after review\n")
                self.commit("change task candidate after approved review")
                self.candidate = self.git("rev-parse", "HEAD")
                self.result["candidate_sha"] = self.candidate
                self.submit()
                self.git("switch", "agent/w")
                current = load_state(self.root, "w")
                candidate = read_candidate(self.root, "w", "a", current)
                with self.assertRaisesRegex(NotIntegrable, "stale coordinator-recorded review"):
                    validate_review(self.root, current["tasks"]["a"], candidate)

                retained = load_state(self.root, "w")["tasks"]["a"]["evidence"]
                self.assertEqual(retained["review"], review_before)
                self.assertEqual(retained.get("traceability_runs", []), execution_before)
                self.assertNotIn("verification", retained)

        ApprovedReviewCase("test_approved_review_cannot_be_reused_after_result_changes").run(result)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])

    def test_crash_after_verification_or_ff(self):
        self.test_crash_around_checkpoint_publication()
        from _ask.tests.inner_loop_reliability import IntegrationTests
        from inner_loop import driver
        result = unittest.TestResult()

        class PreFastForwardRecoveryCase(IntegrationTests):
            def test_interrupt_after_verification_before_fast_forward(self):
                self.task_branch()
                self.review()
                original_integrate = driver.git_integrate

                def interrupt_before_fast_forward(*args, **kwargs):
                    raise RuntimeError("injected interruption before fast-forward")

                driver.git_integrate = interrupt_before_fast_forward
                try:
                    with self.assertRaisesRegex(RuntimeError, "before fast-forward"):
                        driver.integrate_ready(self.root, "w", "a")
                finally:
                    driver.git_integrate = original_integrate

                retained = read_checkpoint(self.root, "w")
                self.assertIsNotNone(retained)
                task = retained[1]["tasks"]["a"]
                receipt = task["evidence"]["verification"]
                self.assertEqual(task["status"], "running")
                self.assertEqual(receipt["result"], "pass")
                self.assertEqual(receipt["candidate_sha"], self.candidate)
                self.assertEqual(retained[1]["coordinator_sha"], self.base)
                self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

                driver.integrate_ready(self.root, "w", "a")
                recovered = load_state(self.root, "w")
                self.assertEqual(recovered["tasks"]["a"]["status"], "integrated")
                self.assertEqual(recovered["coordinator_sha"], self.candidate)
                recovered_receipt = recovered["tasks"]["a"]["evidence"]["verification"]
                for key in ("candidate_sha", "completion_digest", "static_receipt_digest",
                            "traceability_run_ids", "result_digest"):
                    self.assertEqual(recovered_receipt[key], receipt[key], key)

        PreFastForwardRecoveryCase(
            "test_interrupt_after_verification_before_fast_forward"
        ).run(result)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])

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

                # Exercise the production continuation path: task B runs a
                # real failed completion check after A was integrated, then
                # its passing test run must still finalize into the coordinator
                # checkpoint. The new checkpoint must retain A's historical
                # passing receipt even though completion.json now projects B's
                # failed check.
                from inner_loop.driver import run_once
                self.assertEqual(run_once(self.root, "w"), "running=b")
                pythonpath = os.pathsep.join((str(self.root / ".agents/ask"), str(SCRIPTS),
                                              os.environ.get("PYTHONPATH", "")))
                nested_env = dict(
                    os.environ,
                    PYTHONPATH=pythonpath,
                    ASK_TRACEABILITY_RUNTIME_ROOT=str(self.root),
                )
                cli = [sys.executable, "-m", "verification.traceability.cli",
                       "--root", str(self.root)]
                failed = subprocess.run(
                    cli + ["check-completion", "w", "--candidate-sha", self.candidate,
                           "--anchor-sha", self.candidate, "--scope", "task", "--task-id", "b"],
                    cwd=self.root, env=nested_env,
                    capture_output=True, text=True,
                )
                self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
                self.assertEqual(json.loads(failed.stdout)["status"], "fail")
                failed_projection = json.loads(completion.read_text(encoding="utf-8"))
                self.assertEqual(failed_projection["status"], "fail")

                finalized = subprocess.run(
                    cli + ["run", "w", "--candidate-sha", self.candidate,
                           "--anchor-sha", self.candidate, "--scope", "task", "--task-id", "b",
                           "--phase", "final_green"],
                    cwd=self.root, env=nested_env,
                    capture_output=True, text=True,
                )
                self.assertEqual(finalized.returncode, 0, finalized.stdout + finalized.stderr)
                run_document = json.loads(finalized.stdout)
                self.assertEqual(run_document["coordinator_finalization"]["task_id"], "b")
                self.assertEqual(run_document["coordinator_finalization"]["phase"], "final_green")
                advanced = read_checkpoint(self.root, "w")
                self.assertIsNotNone(advanced)
                self.assertEqual(advanced[1]["tasks"]["a"]["status"], "integrated")
                self.assertEqual(advanced[1]["tasks"]["b"]["evidence"]["traceability_runs"][-1]["phase"],
                                 "final_green")
                self.assertEqual(
                    _checkpointed_verification(self.root, "w", advanced[1], advanced),
                    historical,
                    "advancing the checkpoint must preserve the earlier passing receipt chain",
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
        red, green = self._real_traceability_pair()
        from inner_loop import evidence
        from verification.traceability.contracts import digest
        from verification.traceability.evidence import accept_plan, write_json
        for report in (red, green):
            evidence.checkpoint_run(self.root, "w", "a", report["run_id"])
        state_path = self.root / "work/w/inner-loop/state.json"
        before = json.loads(state_path.read_text(encoding="utf-8"))
        old_plan_ref = self.git("rev-parse", "refs/ask/accepted-tests/w")
        accepted_before = json.loads(
            (self.root / "work/w/traceability-accepted.json").read_text(encoding="utf-8")
        )
        execution_rows = json.loads(
            (self.root / "work/w/traceability/executions.json").read_text(encoding="utf-8")
        )
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
        self.assertEqual(prior.get("accepted_plan_digest"), accepted_before["plan_digest"])
        self.assertEqual(prior["execution_runs"], execution_rows)
        self.assertEqual({row["run_id"] for row in prior["execution_runs"]},
                         {red["run_id"], green["run_id"]})
        self.assertEqual(prior["evidence"]["traceability_runs"],
                         before["tasks"]["a"]["evidence"]["traceability_runs"])
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

        # A commit made after interruption is deliberately not attributed to
        # attempt 1. Reopen may accept it only through a reviewed reconciliation
        # that names the exact current source postimage.
        self.write("src/a.py", "candidate = True\n# reviewed continuation\n")
        self.commit("continue source after interrupted attempt")
        post_interruption_head = self.git("rev-parse", "HEAD")
        blocked = self.run_cli("status", "w")
        self.assert_recovery_required(blocked, "src/a.py")

        amended_plan = copy.deepcopy(self.old_plan)
        amended_plan["tests"][0]["scenario"]["then"] = ["updated accepted assertion outcome"]
        self.write("work/w/test-plan.json", json.dumps(amended_plan, sort_keys=True))
        self.commit("amend accepted test obligations")
        plan_review = {
            "decision": "APPROVED", "reviewer": "fixture-plan-reviewer",
            "spec_digest": digest(self.spec), "plan_digest": digest(amended_plan),
        }
        write_json(self.root / "work/w/traceability/plan-review.json", plan_review)
        accepted_after = accept_plan(
            self.root, "w", "HEAD", "fixture-plan-reviewer", "fixture-coordinator",
            "work/w/traceability/plan-review.json",
        )
        write_json(self.root / "work/w/traceability-accepted.json", accepted_after)
        self.commit("accept reviewed amended test obligations")
        new_plan_ref = self.git("rev-parse", "refs/ask/accepted-tests/w")
        checkpoint = read_checkpoint(self.root, "w")
        self.assertIsNotNone(checkpoint)
        reconciliation_head = self.git("rev-parse", "HEAD")
        source_bytes = (self.root / "src/a.py").read_bytes()
        reconciliation = {
            "schema": "ask-inner-loop-reconciliation/v1",
            "work_id": "w",
            "task_id": "a",
            "previous_checkpoint_sha": checkpoint[0],
            "previous_revision": stopped["revision"],
            "previous_attempt_id": prior["attempt_id"],
            "interrupted_candidate_sha": prior["interrupted_candidate_sha"],
            "new_attempt_id": "a:attempt-2",
            "accepted_plan_ref": new_plan_ref,
            "accepted_plan_digest": accepted_after["plan_digest"],
            "new_attempt_base_sha": stopped["coordinator_sha"],
            "candidate_sha": reconciliation_head,
            "recorded_by": "fixture-coordinator",
            "source_postimage": {"src/a.py": hashlib.sha256(source_bytes).hexdigest()},
        }
        reconciliation_payload = json.dumps(
            reconciliation, sort_keys=True, separators=(",", ":")
        ).encode()
        reconciliation["review"] = {
            "decision": "APPROVED",
            "reviewer": "fixture-independent-reconciler",
            "candidate_sha": reconciliation_head,
            "payload_sha256": hashlib.sha256(reconciliation_payload).hexdigest(),
        }
        invalid_reconciliation = copy.deepcopy(reconciliation)
        invalid_reconciliation["source_postimage"]["src/a.py"] = "0" * 64
        invalid_payload = {
            key: value for key, value in invalid_reconciliation.items() if key != "review"
        }
        invalid_reconciliation["review"]["payload_sha256"] = hashlib.sha256(
            json.dumps(invalid_payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.write(
            "work/w/inner-loop/evidence/reconciliation-a.json",
            json.dumps(invalid_reconciliation, indent=2) + "\n",
        )
        rejected_reconciliation = self.run_cli(
            "reopen", "w", "a", "--reason", "amended plan accepted"
        )
        self.assertNotEqual(rejected_reconciliation.returncode, 0)
        self.assertIn("source postimage mismatch",
                      rejected_reconciliation.stdout + rejected_reconciliation.stderr)
        self.assertEqual(load_state(self.root, "w")["tasks"]["a"]["status"], "interrupted")
        self.write(
            "work/w/inner-loop/evidence/reconciliation-a.json",
            json.dumps(reconciliation, indent=2) + "\n",
        )
        reopened = self.run_cli("reopen", "w", "a", "--reason", "amended plan accepted")
        self.assertEqual(reopened.returncode, 0, reopened.stdout + reopened.stderr)
        resumed = json.loads(state_path.read_text(encoding="utf-8"))
        current = resumed["tasks"]["a"]
        self.assertEqual(current["status"], "running")
        self.assertNotEqual(current["attempt_id"], prior["attempt_id"])
        self.assertEqual(current["accepted_plan_ref"], new_plan_ref)
        self.assertEqual(current.get("accepted_plan_digest"), accepted_after["plan_digest"])
        self.assertEqual(current["attempt_history"], task["attempt_history"])
        self.assertEqual(current["attempt_history"][0]["reason"], "accepted plan amendment")
        self.assertEqual(current["source_reconciliation"]["candidate_sha"], reconciliation_head)
        self.assertEqual(current["source_reconciliation"]["paths"], ["src/a.py"])

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

    def test_t21_exception_requires_exact_p1_decision(self):
        from inner_loop.graph import load_graph
        from verification.traceability.coverage import validate_plan
        from verification.traceability.evidence import load_accepted, _validate_historical_red_exception

        self._real_traceability_pair(run_reports=False)
        p0_plan = copy.deepcopy(self.old_plan)
        p0_plan["historical_red_exceptions"] = [{
            "work_id": "w", "task_id": "a", "test_id": "T-A",
            "decision_digest": "1" * 64, "accepted_plan": self.anchor_commit,
        }]
        violations = validate_plan(self.spec, p0_plan, load_graph(self.root, "w"))
        self.assertTrue(
            violations,
            "P0 must refuse a historical-Red exception even when its declaration looks complete",
        )

        # The same exact scope is structurally representable in P1, but only
        # when the accepted independent decision binds the approved artifact.
        approved = json.loads((REPO / "work/continuation-recovery/test-plan.json").read_text())
        spec = json.loads((REPO / "specs/current/continuation-recovery.json").read_text())
        decision_digest = "409f38a1120f45f48d6693176e21d0cab93e0107e412614945f09b9c23e44fe8"
        declaration = {
            "work_id": "continuation-recovery", "task_id": "CR-3", "test_id": "CR-T21",
            "kind": "historical-red-unavailable",
            "decision_artifact": "work/continuation-recovery/cr3-scoped-decision-record.md",
            "decision_digest": decision_digest,
            "missing_red": "No retained behavior assertion failure exists for the expanded T21 behavior.",
        }
        approved["historical_red_exceptions"] = [declaration]
        self.assertEqual(validate_plan(spec, approved, load_graph(REPO, "continuation-recovery")), [])
        current = load_accepted(REPO, "continuation-recovery", "HEAD", "HEAD")
        pin = copy.deepcopy(current["pin"])
        pin["plan_review"]["historical_red_exceptions"] = [declaration]
        pin["plan_review"]["coordinator_migration"] = {
            "work_id": "continuation-recovery", "task_id": "CR-3",
            "coordinator_sha": "a" * 40, "coordinator_tree": "b" * 40,
            "verifier_sha": "c" * 40, "verifier_tree": "d" * 40,
            "scope_decision_digest": decision_digest,
        }
        _validate_historical_red_exception(REPO, "continuation-recovery", pin,
                                           {"plan": approved})
        pin["plan_review"]["coordinator_migration"]["task_id"] = "CR-2"
        with self.assertRaisesRegex(Exception, "exact P1 coordinator migration"):
            _validate_historical_red_exception(REPO, "continuation-recovery", pin,
                                               {"plan": approved})

    def test_historical_red_continuity_through_checkpoint_and_integration(self):
        from inner_loop import evidence
        from verification.traceability.contracts import digest
        from verification.traceability.evidence import accept_plan
        from verification.traceability.evidence import load_historical_accepted, source_digests

        red, green = self._real_traceability_pair()
        evidence.checkpoint_run(self.root, "w", "a", red["run_id"])
        evidence.checkpoint_run(self.root, "w", "a", green["run_id"])

        p1_plan = copy.deepcopy(self.old_plan)
        original = load_historical_accepted(self.root, "w", red["candidate_sha"])
        original_authority_commit = self.git("rev-parse", "refs/ask/accepted-tests/w")
        original_ledger = next(row for row in json.loads(
            (self.root / "work/w/traceability/executions.json").read_text())
            if row.get("run_id") == red["run_id"])
        report_digest = hashlib.sha256(json.dumps(
            red, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        p1_plan["historical_red_continuity"] = [{
            "work_id": "w", "task_id": "a", "test_id": case["test_id"],
            "run_id": red["run_id"], "candidate_sha": red["candidate_sha"],
            "original_plan_digest": red["plan_digest"],
            "report_digest": report_digest,
            "ledger_row_digest": digest(original_ledger),
            "original_authority_object": original_authority_commit,
            "original_candidate_pin_object": self.git(
                "rev-parse", f"{red['candidate_sha']}:work/w/traceability-accepted.json"),
            "original_authority_digest": digest(original["pin"]),
            "original_contract_digest": digest(original["pin"]),
            "original_source_digests": case["source_digests"],
            "current_source_digests": source_digests(self.root, self.git("rev-parse", "HEAD"), p1_plan, [case["test_id"]]),
            "reviewer": "fixture-p1-reviewer",
            "behavioral_continuity": "same source-value assertion remains mapped",
        } for case in red["cases"] if case.get("outcome") == "failed"]
        interrupted = self.run_cli("interrupt", "w", "a", "--reason", "accept reviewed P1 fixture")
        self.assertEqual(interrupted.returncode, 0, interrupted.stdout + interrupted.stderr)
        self.write("work/w/test-plan.json", json.dumps(p1_plan, sort_keys=True))
        self.commit("accept P1 historical Red continuity fixture")
        review_path = "work/w/traceability/plan-review.json"
        self.write(review_path, json.dumps({
            "decision": "APPROVED", "reviewer": "fixture-p1-reviewer",
            "spec_digest": digest(self.spec), "plan_digest": digest(p1_plan),
        }))
        accepted = accept_plan(
            self.root, "w", "HEAD", "fixture-p1-reviewer", "fixture-coordinator", review_path,
        )
        self.assertEqual(self.git(
            "rev-parse", f"refs/ask/accepted-tests-history/w/{original_authority_commit}"),
            original_authority_commit,
        )
        self.write("work/w/traceability-accepted.json", json.dumps(accepted, sort_keys=True) + "\n")
        self.commit("commit P1 historical Red authority")
        from verification.traceability.adapters import run_tests
        current_sha = self.git("rev-parse", "HEAD")
        current_green = run_tests(self.root, {"spec": self.spec, "plan": p1_plan},
                                  current_sha, "task", "a", "final_green")
        interrupted_preflight = self.run_cli(
            "preflight-run", "w", "a", "--run-id", current_green["run_id"])
        self.assertEqual(interrupted_preflight.returncode, 0,
                         interrupted_preflight.stdout + interrupted_preflight.stderr)
        reopened = self.run_cli("reopen", "w", "a", "--reason", "exercise P1 historical Red")
        self.assertEqual(reopened.returncode, 0, reopened.stdout + reopened.stderr)

        try:
            receipt = evidence.checkpoint_run(self.root, "w", "a", red["run_id"])
        except Exception as exc:
            self.fail(
                "the exact P1 continuity row must admit original Red through checkpoint-run "
                f"without rewriting its report or ledger identity: {exc}"
            )
        self.assertEqual(receipt["run_id"], red["run_id"])
        self.assertEqual(receipt["phase"], "red")
        self.assertEqual(receipt["candidate_sha"], red["candidate_sha"])
        self.assertEqual(receipt["plan_digest"], red["plan_digest"])
        evidence.checkpoint_run(self.root, "w", "a", current_green["run_id"])
        from verification.traceability.evidence import load_accepted
        from verification.traceability.service import reports
        current_sha = self.git("rev-parse", "HEAD")
        current_contracts = load_accepted(self.root, "w", current_sha, current_sha)
        selected, rejected = reports(self.root, "w", current_contracts, current_sha, "task", "a")
        self.assertIn(red["run_id"], {item["run_id"] for item in selected})
        self.assertEqual(sum(item["run_id"] == red["run_id"] for item in selected), 1)
        self.assertNotIn(red["run_id"], {item["run_id"] for item in rejected})
        workstream_selected, workstream_rejected = reports(
            self.root, "w", current_contracts, current_sha, "workstream", None)
        self.assertIn(red["run_id"], {item["run_id"] for item in workstream_selected})
        self.assertNotIn(red["run_id"], {item["run_id"] for item in workstream_rejected})

        self._cr3_normal_integration_fixture()

    def _cr3_normal_integration_fixture(self):
        """Run the accepted P1 C/V boundary through the normal coordinator integration."""
        import shutil
        from verification.traceability.contracts import digest

        work_id, task_id = "continuation-recovery", "CR-3"
        root = Path(self.temp.name) / "cr3-integration"
        subprocess.run(["git", "clone", "--shared", "--no-checkout", str(REPO), str(root)],
                       check=True, capture_output=True, text=True)
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=root, text=True,
                                           stderr=subprocess.PIPE).strip()
        git("config", "user.email", "cr3-integration@example.test")
        git("config", "user.name", "CR3 Integration Fixture")
        coordinator_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True,
        ).strip()
        # The enclosing traceability runner checks out an immutable candidate
        # detached, so a local clone has no named coordinator branch to copy.
        # Seed the fixture ref from that exact candidate before exercising the
        # normal integration path.
        git("update-ref", "refs/heads/agent/continuation-recovery", coordinator_sha)
        coordinator_sha = git("rev-parse", "refs/heads/agent/continuation-recovery")
        original_base = "2c508ff4248f16a3e3121d33a0fae7297c9b378e"
        self.assertEqual(git("merge-base", "--is-ancestor", original_base, coordinator_sha), "")
        p0_authority = subprocess.check_output(
            ["git", "rev-parse", "refs/ask/accepted-tests/continuation-recovery"],
            cwd=REPO, text=True,
        ).strip()
        git("update-ref", "refs/ask/accepted-tests/continuation-recovery", p0_authority)
        git("switch", "-qc", "task/CR-3", coordinator_sha)

        decision_path = "work/continuation-recovery/cr3-scoped-decision-record.md"
        decision_raw = subprocess.check_output(["git", "show", f"{coordinator_sha}:{decision_path}"], cwd=root)
        decision_digest = hashlib.sha256(decision_raw).hexdigest()
        declaration = {
            "work_id": work_id, "task_id": task_id, "test_id": "CR-T21",
            "kind": "historical-red-unavailable", "decision_artifact": decision_path,
            "decision_digest": decision_digest,
            "missing_red": "The approved P1 disposition records that no retained Red exists for this case.",
        }
        spec = json.loads(subprocess.check_output(
            ["git", "show", f"{coordinator_sha}:specs/current/continuation-recovery.json"],
            cwd=root, text=True))
        plan = json.loads(subprocess.check_output(
            ["git", "show", f"{coordinator_sha}:work/continuation-recovery/test-plan.json"],
            cwd=root, text=True))
        plan["tests"] = [test for test in plan["tests"]
                         if test.get("task_id") != task_id or test.get("id") == "CR-T21"]
        for obligation in plan.get("obligations", []):
            obligation["required_types"] = ["integration"]
        for scope in plan["task_scopes"]:
            if scope.get("task_id") == task_id:
                scope["test_ids"] = ["CR-T21"]
        plan["runners"].append({"id": "fixture", "argv": ["python3", "-m", "unittest", "t21_fixture"],
                                "adapter": "unittest"})
        t21 = next(test for test in plan["tests"] if test["id"] == "CR-T21")
        t21.update({"case_id": "t21_fixture.T21.test_behavior", "runner_id": "fixture",
                    "source_paths": ["src/t21-value"]})
        plan["historical_red_exceptions"] = [declaration]
        pin0 = json.loads(subprocess.check_output(
            ["git", "show", f"{p0_authority}:accepted.json"], cwd=root, text=True))
        def source_inventory(prefix):
            names = git("ls-tree", "-r", "--name-only", coordinator_sha, "--", prefix).splitlines()
            return {name: hashlib.sha256(subprocess.check_output(
                ["git", "show", f"{coordinator_sha}:{name}"], cwd=root)).hexdigest()
                    for name in names if name.endswith(".py")}
        migration = {
            "work_id": work_id, "task_id": task_id,
            "coordinator_sha": coordinator_sha,
            "coordinator_tree": git("rev-parse", f"{coordinator_sha}^{{tree}}"),
            "verifier_sha": coordinator_sha,
            "verifier_tree": git("rev-parse", f"{coordinator_sha}^{{tree}}"),
            "original_base_sha": original_base,
            "p1_spec_digest": digest(spec), "p1_plan_digest": digest(plan),
            "p0_plan_digest": pin0["plan_digest"],
            "p0_review_identity": pin0["reviewer"],
            "p0_review_digest": pin0["plan_review_digest"],
            "scope_decision_artifact": decision_path,
            "scope_decision_digest": decision_digest,
            "integration_output_schema": "ask-integration-evidence/v1",
            "source_review_artifact": "work/continuation-recovery/cr3-cv-review.json",
        }
        source_review = {
            "decision": "APPROVED", "reviewer": "fixture-independent-source-reviewer",
            "coordinator_sha": coordinator_sha,
            "coordinator_tree": migration["coordinator_tree"],
            "verifier_sha": coordinator_sha, "verifier_tree": migration["verifier_tree"],
            "original_base_sha": original_base, "p0_plan_digest": pin0["plan_digest"],
            "review_identity": pin0["reviewer"], "review_digest": pin0["plan_review_digest"],
            "coordinator_source_digests": source_inventory("_ask/scripts/inner_loop"),
            "verifier_source_digests": source_inventory(".agents/ask/verification"),
        }
        (root / migration["source_review_artifact"]).parent.mkdir(parents=True, exist_ok=True)
        review_raw = json.dumps(source_review, sort_keys=True, separators=(",", ":")).encode()
        (root / migration["source_review_artifact"]).write_bytes(review_raw)
        migration["source_review_digest"] = hashlib.sha256(review_raw).hexdigest()
        p1_review = {
            "decision": "APPROVED", "reviewer": "fixture-independent-plan-reviewer",
            "spec_digest": digest(spec), "plan_digest": digest(plan),
            "historical_red_exceptions": [declaration],
            "coordinator_migration": migration,
        }
        review_path = root / "work/continuation-recovery/cr3-p1-plan-review.json"
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(json.dumps(p1_review, sort_keys=True) + "\n")
        (root / "specs/current/continuation-recovery.json").write_text(json.dumps(spec, sort_keys=True) + "\n")
        (root / "work/continuation-recovery/test-plan.json").write_text(json.dumps(plan, sort_keys=True) + "\n")
        (root / "t21_fixture.py").write_text(
            "import pathlib, unittest\n"
            "class T21(unittest.TestCase):\n"
            "    def test_behavior(self): self.assertEqual(pathlib.Path('src/t21-value').read_text(), 'expected\\n')\n"
        )
        (root / ".agents/verification.yaml").write_text(
            "schema: ask-checkplan/v1\nno_production_datastore: true\n"
            "checks:\n  - id: required\n    tier: mandatory\n    command: 'true'\n")
        git("add", "specs/current/continuation-recovery.json",
            "work/continuation-recovery/test-plan.json",
            migration["source_review_artifact"],
            "work/continuation-recovery/cr3-p1-plan-review.json",
            "t21_fixture.py", ".agents/verification.yaml")
        git("commit", "-qm", "prepare disposable reviewed P1 C/V integration contract")
        contract_sha = git("rev-parse", "HEAD")
        from verification.traceability.evidence import accept_plan, write_json
        accepted = accept_plan(root, work_id, contract_sha, p1_review["reviewer"],
                               "fixture-coordinator", "work/continuation-recovery/cr3-p1-plan-review.json")
        write_json(root / "work/continuation-recovery/traceability-accepted.json", accepted)
        git("add", "work/continuation-recovery/traceability-accepted.json")
        git("commit", "-qm", "accept disposable reviewed P1 contract")
        contract_checkout_sha = git("rev-parse", "HEAD")
        (root / "src/t21-value").parent.mkdir(parents=True, exist_ok=True)
        (root / "src/t21-value").write_text("expected\n")
        git("add", "src/t21-value")
        git("commit", "-qm", "implement passing disposable CR-T21 candidate")
        candidate_sha = git("rev-parse", "HEAD")
        from verification.traceability.adapters import run_tests
        green = run_tests(root, {"spec": spec, "plan": plan}, candidate_sha,
                          "task", task_id, "final_green")

        # Keep one real historical CR-3 Red report in the disposable runtime.
        # Integration must checkpoint it byte-for-byte even though P1 no longer
        # selects that historical test as a current task milestone.
        historical_run_id = "b50dd24e0ef04a2aacff4c4a26db4dd5"
        historical_relative = f"work/{work_id}/traceability/runs/{historical_run_id}/results.json"
        runtime_root = Path(os.environ.get("ASK_TRACEABILITY_RUNTIME_ROOT") or REPO).resolve()
        historical_raw = (runtime_root / historical_relative).read_bytes()
        historical_report = json.loads(historical_raw)
        self.assertEqual(historical_report["run_id"], historical_run_id)
        historical_target = root / historical_relative
        historical_target.parent.mkdir(parents=True, exist_ok=True)
        historical_target.write_bytes(historical_raw)
        executions_path = root / f"work/{work_id}/traceability/executions.json"
        executions_raw = (runtime_root / f"work/{work_id}/traceability/executions.json").read_bytes()
        executions = json.loads(executions_raw)
        executions_path.write_text(json.dumps(executions, indent=2) + "\n")

        git("branch", "-f", "agent/continuation-recovery", contract_checkout_sha)
        git("switch", "-q", "agent/continuation-recovery")
        from inner_loop.state import _publish_state, load_state
        graph = load_graph(root, work_id)
        state_tasks = {}
        for item in graph["tasks"]:
            tid = item["id"]
            state_tasks[tid] = {
                "status": "integrated" if tid in {"CR-1", "CR-2"} else "pending",
                "base_sha": "", "task_branch": "", "result_path": "",
                "boundary_reject": None, "review_round": 0, "debug_round": 0,
                "evidence": {}, "attempt_number": 0, "attempt_id": "",
                "accepted_plan_ref": "", "accepted_plan_digest": "",
                "attempt_started_revision": None, "attempt_history": [],
            }
        state_tasks[task_id].update({
            "status": "running", "base_sha": original_base, "task_branch": "task/CR-3",
            "attempt_number": 1, "attempt_id": "CR-3:attempt-1",
            "attempt_started_revision": 1,
            "accepted_plan_ref": "refs/ask/accepted-tests/continuation-recovery",
            "accepted_plan_digest": accepted["plan_digest"],
        })
        state = {"schema": "ask-inner-loop-state/v1", "work_id": work_id, "revision": 1,
                 "coordinator_sha": contract_checkout_sha,
                 "coordinator_branch": "agent/continuation-recovery", "tasks": state_tasks}
        _publish_state(root, work_id, state)
        result = {
            "schema": "ask-task-result/v2", "work_id": work_id, "task_id": task_id,
            "base_sha": original_base, "candidate_sha": candidate_sha,
            "contract_sha": accepted["contract_sha"],
            "tdd": {"seam": "src/t21-value",
                    "red": {"status": "unavailable", "kind": "historical-red-unavailable",
                            "reason": "The accepted P1 plan records the approved unavailable-history disposition.",
                            "exit_code": None},
                    "green": {"command": "python3 -m unittest t21_fixture",
                              "output": "CR-T21 passed", "exit_code": 0}},
            "exemption": None,
        }
        result_path = root / "work/continuation-recovery/inner-loop/results/CR-3.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(result) + "\n")
        from verification.traceability.evidence import inventory, record_test_review, source_digests
        contracts = __import__("verification.traceability.evidence", fromlist=["load_accepted"]).load_accepted(
            root, work_id, candidate_sha, candidate_sha)
        actual = inventory(root, accepted["contract_sha"], candidate_sha, plan)
        test_review = {
            "schema": "ask-test-review/v2", "reviewer": "fixture-independent-test-reviewer",
            "candidate_sha": candidate_sha, "base_sha": accepted["contract_sha"],
            "spec_digest": digest(spec), "plan_digest": digest(plan),
            "scope": "task", "task_id": task_id, "test_ids": ["CR-T21"],
            "criterion_ids": t21["criterion_ids"],
            "source_digests": source_digests(root, candidate_sha, plan, ["CR-T21"]),
            "inspected_sources": actual["inspected_sources"], "changed_cases": actual["changed_cases"],
            "inventory_exclusions": {name: "Fixture assertions are covered by CR-T21."
                                     for name in actual["unmapped_cases"]},
            "criteria": [{"id": criterion, "coverage_decision": "APPROVED",
                          "assessment": "The accepted task case observes the required value.",
                          "type_adequacy": {"integration": {"decision": "APPROVED",
                              "assessment": "The trusted runner executes the committed candidate."}}}
                         for criterion in t21["criterion_ids"]],
            "tests": [{"id": "CR-T21", "decision": "APPROVED",
                       "assertion_assessment": "The committed value is checked against a literal.",
                       "counterexample": "A different value fails the assertion.",
                       "tdd_continuity_assessment": "T21 is green under its exact approved historical-Red disposition."}],
        }
        test_review_path = "work/continuation-recovery/traceability/test-review.json"
        write_json(root / test_review_path, test_review)
        record_test_review(root, work_id, candidate_sha, candidate_sha, test_review_path,
                           "fixture-coordinator", review_document=test_review)
        from inner_loop.evidence import record_review
        semantic_path = root / "work/continuation-recovery/inner-loop/evidence/review.md"
        semantic_path.parent.mkdir(parents=True, exist_ok=True)
        semantic_path.write_text("Reviewer: fixture-independent-test-reviewer; APPROVED\n")
        try:
            record_review(root, work_id, task_id, "fixture-independent-test-reviewer",
                          "_ask/policies/delegation.md",
                          "work/continuation-recovery/inner-loop/evidence/review.md")
        except Exception as exc:
            self.fail(f"normal coordinator review admission refused the fixture: "
                      f"{getattr(exc, 'report', exc)}")
        from inner_loop.driver import integrate_ready
        integrated_sha = integrate_ready(root, work_id, task_id)
        self.assertEqual(integrated_sha, candidate_sha)
        final_state = load_state(root, work_id)
        task = final_state["tasks"][task_id]
        self.assertEqual(task["status"], "integrated")
        receipt = task["evidence"]["verification"]
        self.assertEqual(receipt["base_sha"], original_base)
        self.assertEqual(receipt["candidate_sha"], candidate_sha)
        self.assertEqual(receipt["resulting_sha"], candidate_sha)
        self.assertEqual(receipt["coordinator_sha"], coordinator_sha)
        self.assertEqual(receipt["verifier_sha"], coordinator_sha)
        self.assertEqual(receipt["coordinator_tree"], git("rev-parse", f"{coordinator_sha}^{{tree}}"))
        self.assertEqual(receipt["verifier_tree"], git("rev-parse", f"{coordinator_sha}^{{tree}}"))
        self.assertEqual(receipt["p1_spec_digest"], accepted["spec_digest"])
        self.assertEqual(receipt["p1_plan_digest"], accepted["plan_digest"])
        self.assertEqual(receipt["p1_contract_sha"], accepted["contract_sha"])
        self.assertTrue(receipt["traceability_run_ids"])
        for run_id in receipt["traceability_run_ids"]:
            run = json.loads((root / f"work/{work_id}/traceability/runs/{run_id}/results.json").read_text())
            self.assertEqual(run["candidate_sha"], candidate_sha)
            self.assertEqual(run["plan_digest"], accepted["plan_digest"])
        self.assertEqual(final_state["coordinator_sha"], candidate_sha)
        from inner_loop.checkpoint import read_checkpoint
        checkpoint = read_checkpoint(root, work_id)
        self.assertIsNotNone(checkpoint)
        checkpoint_files = checkpoint[2]
        self.assertEqual(checkpoint_files[f"artifacts/{historical_relative}"], historical_raw)
        self.assertIn(f"artifacts/work/{work_id}/traceability/executions.json", checkpoint_files)

    def test_consumed_receipt_selection_is_atomic(self):
        from inner_loop.checkpoint import read_checkpoint
        from inner_loop.state import load_state
        from verification.traceability.contracts import digest
        from verification.traceability.evidence import accept_plan

        # Reuse the established attempt-1 -> attempt-2 fixture, then create a
        # distinct, reviewed attempt-2 -> attempt-3 source transition.
        self.test_interrupt_and_reopen_preserve_attempt_history()
        interrupted = self.run_cli("interrupt", "w", "a", "--reason", "preserve attempt 2")
        self.assertEqual(interrupted.returncode, 0, interrupted.stdout + interrupted.stderr)
        prior_state = load_state(self.root, "w")
        prior = prior_state["tasks"]["a"]["attempt_history"][-1]
        checkpoint = read_checkpoint(self.root, "w")
        self.assertIsNotNone(checkpoint)

        self.write("src/a.py", "candidate = True\n# attempt 3 reviewed source\n")
        p1_plan = copy.deepcopy(self.old_plan)
        p1_plan["tests"][0]["scenario"]["then"] = ["attempt 3 exact assertion"]
        self.write("work/w/test-plan.json", json.dumps(p1_plan, sort_keys=True))
        self.commit("accept attempt 3 test plan")
        review_path = "work/w/traceability/plan-review.json"
        self.write(review_path, json.dumps({
            "decision": "APPROVED", "reviewer": "fixture-attempt-3-reviewer",
            "spec_digest": digest(self.spec), "plan_digest": digest(p1_plan),
        }))
        accepted = accept_plan(
            self.root, "w", "HEAD", "fixture-attempt-3-reviewer", "fixture-coordinator", review_path,
        )
        self.write("work/w/traceability-accepted.json", json.dumps(accepted, sort_keys=True) + "\n")
        self.commit("commit attempt 3 accepted plan")
        candidate = self.git("rev-parse", "HEAD")
        source_bytes = (self.root / "src/a.py").read_bytes()
        request = {
            "schema": "ask-inner-loop-reconciliation/v1", "work_id": "w", "task_id": "a",
            "previous_checkpoint_sha": checkpoint[0], "previous_revision": prior_state["revision"],
            "previous_attempt_id": prior["attempt_id"],
            "interrupted_candidate_sha": prior["interrupted_candidate_sha"],
            "new_attempt_id": "a:attempt-3",
            "accepted_plan_ref": self.git("rev-parse", "refs/ask/accepted-tests/w"),
            "accepted_plan_digest": accepted["plan_digest"],
            "new_attempt_base_sha": prior_state["coordinator_sha"], "candidate_sha": candidate,
            "recorded_by": "fixture-coordinator",
            "source_postimage": {"src/a.py": hashlib.sha256(source_bytes).hexdigest()},
        }
        payload = json.dumps(request, sort_keys=True, separators=(",", ":")).encode()
        request["review"] = {
            "decision": "APPROVED", "reviewer": "fixture-attempt-3-reviewer",
            "candidate_sha": candidate, "payload_sha256": hashlib.sha256(payload).hexdigest(),
        }
        request_path = "work/w/inner-loop/evidence/reconciliation-a-attempt-2-to-3.json"
        self.write(request_path, json.dumps(request, indent=2) + "\n")
        state_before = (self.root / "work/w/inner-loop/state.json").read_bytes()
        checkpoint_before = read_checkpoint(self.root, "w")[0]
        receipt_before = (self.root / "work/w/inner-loop/evidence/reconciliation-a.json").read_bytes()
        new_receipt_path = self.root / request_path
        new_receipt_before = new_receipt_path.read_bytes()
        altered = copy.deepcopy(request)
        altered["candidate_sha"] = self.anchor_commit
        new_receipt_path.write_text(json.dumps(altered, indent=2) + "\n")
        refused = self.run_cli("reopen", "w", "a", "--reason", "reject altered attempt transition")
        self.assertNotEqual(refused.returncode, 0, refused.stdout + refused.stderr)
        self.assertEqual((self.root / "work/w/inner-loop/state.json").read_bytes(), state_before)
        self.assertEqual(read_checkpoint(self.root, "w")[0], checkpoint_before)
        self.assertEqual((self.root / "work/w/inner-loop/evidence/reconciliation-a.json").read_bytes(), receipt_before)
        self.assertEqual(new_receipt_path.read_text(), json.dumps(altered, indent=2) + "\n")
        new_receipt_path.write_bytes(new_receipt_before)

        reopened = self.run_cli("reopen", "w", "a", "--reason", "approved attempt 2 to 3 request")
        self.assertEqual(reopened.returncode, 0, reopened.stdout + reopened.stderr)
        state_after = load_state(self.root, "w")
        self.assertEqual(state_after["tasks"]["a"]["attempt_id"], "a:attempt-3")
        self.assertEqual((self.root / "work/w/inner-loop/evidence/reconciliation-a.json").read_bytes(), receipt_before)
        self.assertNotEqual((self.root / "work/w/inner-loop/state.json").read_bytes(), state_before)
        self.assertNotEqual(read_checkpoint(self.root, "w")[0], checkpoint_before)

    def test_interrupted_preflight_is_read_only_and_derived(self):
        from inner_loop.checkpoint import read_checkpoint
        red, _green = self._real_traceability_pair()
        state_path = self.root / "work/w/inner-loop/state.json"
        retained_older_cache = state_path.read_bytes()
        interrupted = self.run_cli("interrupt", "w", "a", "--reason", "preflight before reopen")
        self.assertEqual(interrupted.returncode, 0, interrupted.stdout + interrupted.stderr)
        state_before = state_path.read_bytes()
        checkpoint_before = read_checkpoint(self.root, "w")[0]

        result = self.run_cli("preflight-run", "w", "a", "--run-id", red["run_id"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(state_path.read_bytes(), state_before)
        self.assertEqual(read_checkpoint(self.root, "w")[0], checkpoint_before)
        report = json.loads(result.stdout)
        self.assertEqual(report["work_id"], "w")
        self.assertEqual(report["task_id"], "a")
        self.assertTrue(report["read_only"])
        self.assertIn("assessment", report)

        # A worker run produced after interruption is registered in the
        # append-only ledger but is not part of the archived attempt yet.
        from verification.traceability.adapters import run_tests
        from verification.traceability.evidence import load_accepted
        candidate = self.git("rev-parse", "HEAD")
        contracts = load_accepted(self.root, "w", candidate, candidate)
        current = run_tests(self.root, contracts, candidate, "task", "a", "final_green")
        new_run_id = current["run_id"]
        checkpoint_sha = read_checkpoint(self.root, "w")[0]
        cache = state_path.read_bytes()
        state_path.unlink()
        missing_cache = self.run_cli("preflight-run", "w", "a", "--run-id", new_run_id)
        self.assertEqual(missing_cache.returncode, 0, missing_cache.stdout + missing_cache.stderr)
        self.assertFalse(state_path.exists(), "preflight must not restore a missing runtime cache")
        self.assertEqual(read_checkpoint(self.root, "w")[0], checkpoint_sha)

        state_path.write_bytes(retained_older_cache)
        old_cache_result = self.run_cli("preflight-run", "w", "a", "--run-id", new_run_id)
        self.assertEqual(old_cache_result.returncode, 0, old_cache_result.stdout + old_cache_result.stderr)
        self.assertEqual(state_path.read_bytes(), retained_older_cache,
                         "preflight must preserve an exact older checkpoint state")
        forged = json.loads(cache)
        forged["revision"] -= 1
        state_path.write_text(json.dumps(forged, indent=2) + "\n")
        forged_cache = state_path.read_bytes()
        refused_forgery = self.run_cli("preflight-run", "w", "a", "--run-id", new_run_id)
        self.assertNotEqual(refused_forgery.returncode, 0)
        self.assertEqual(state_path.read_bytes(), forged_cache,
                         "rejected preflight must not rewrite a divergent cache")
        self.assertEqual(read_checkpoint(self.root, "w")[0], checkpoint_sha)
        state_path.write_bytes(cache)


if __name__ == "__main__":
    unittest.main()
