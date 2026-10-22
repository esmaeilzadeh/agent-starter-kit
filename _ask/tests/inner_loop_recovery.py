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

from _ask.tests.inner_loop_recovery_fixture import (
    LEGACY_AUTHORITY_SHA,
    LEGACY_STATE_SHA256,
    write_legacy_fixture,
)
from inner_loop.graph import load_graph
from inner_loop.checkpoint import read_checkpoint
from inner_loop.recovery import inspect as inspect_recovery

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
            "tests": [self.case_a, self.case_b],
            "task_scopes": [{"task_id": "a", "test_ids": ["T-A", "T-B"]},
                            {"task_id": "b", "test_ids": []}],
        }
        self.write("specs/current/w.json", json.dumps(self.spec, sort_keys=True))
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
        original_result = self.result_path.read_bytes()
        state_path = self.root / "work/w/inner-loop/state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["a"]
        task.update(status="integrated", result_path="work/w/inner-loop/results/a.json")
        state["coordinator_sha"] = self.candidate
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        self.git("update-ref", "-d", "refs/ask/inner-loop/w")

        amended = copy.deepcopy(self.old_plan)
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
            json.dumps([{"run_id": "green-a", "phase": "final_green", "scope": "task",
                         "task_id": "a", "candidate_sha": self.candidate,
                         "spec_digest": self.old_spec_digest,
                         "plan_digest": self.old_plan_digest}]) + "\n",
        )
        state = json.loads(state_path.read_text(encoding="utf-8"))

        result = inspect_recovery(self.root, "w", load_graph(self.root, "w"), state)
        self.assertIsNone(result, result)
        self.assertEqual(self.result_path.read_bytes(), original_result)
        self.assertEqual(json.loads(self.result_path.read_text())["contract_sha"], self.base)

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
        checkpoint = self._checkpoint_ref()
        self.assertIsNotNone(checkpoint, "checkpoint validation requires a published baseline")
        state_path = self.root / "work/w/inner-loop/state.json"
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
            if ref != "refs/ask/inner-loop/w":
                self.git("update-ref", "-d", ref)
        self.git("reflog", "expire", "--expire=now", "--all")
        self.git("gc", "--prune=now")
        self.assertEqual(self.git("cat-file", "-t", checkpoint), "commit")

        bundle = self.root / "checkpoint.bundle"
        exported = self.run_cli("checkpoint-export", "w", "--out", str(bundle))
        self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
        self.assertTrue(bundle.is_file())

        imported = Path(self.temp.name) / "imported"
        self.git("clone", "-q", "--bare", str(self.root), str(imported))
        result = subprocess.run(
            [sys.executable, "-m", "inner_loop", "--root", str(imported),
             "checkpoint-import", "w", str(bundle)],
            cwd=imported,
            env={**os.environ, "PYTHONPATH": os.pathsep.join(
                part for part in (str(SCRIPTS), os.environ.get("PYTHONPATH", "")) if part
            )},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git("rev-parse", "refs/ask/inner-loop/w"), checkpoint)
        self.assertEqual(self.git("--git-dir", str(imported), "rev-parse",
                                  "refs/ask/inner-loop/w"), checkpoint)

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
