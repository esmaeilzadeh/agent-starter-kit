"""Recovery guards exercised through fresh coordinator processes."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from _ask.tests.inner_loop_recovery_fixture import (
    LEGACY_AUTHORITY_SHA,
    LEGACY_STATE_SHA256,
    write_legacy_fixture,
)

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "_ask" / "scripts"
sys.path.insert(0, str(SCRIPTS))

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
        self.commit("accepted task graph")
        self.base = self.git("rev-parse", "HEAD")
        self.write(
            "work/w/traceability-accepted.json",
            json.dumps({"schema": "ask-accepted-tests/v1", "work_id": "w", "contract_sha": self.base}) + "\n",
        )
        self.commit("accepted test anchor")
        self.anchor_commit = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/ask/accepted-tests/w", self.anchor_commit)

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

    def run_cli(self, *args):
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(SCRIPTS), env.get("PYTHONPATH", "")) if part
        )
        return subprocess.run(
            [sys.executable, "-m", "inner_loop", "--root", str(self.root), *args],
            cwd=self.root,
            env=env,
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
        with self.subTest(identity="missing contract_sha"):
            refused = self.run_cli("status", "w")
            self.assert_recovery_required(refused, "contract_sha", "work/w/inner-loop/results/a.json")
        result_path.write_bytes(result_bytes)

        state = json.loads(state_before)
        state["tasks"]["a"]["base_sha"] = ""
        state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")
        with self.subTest(identity="empty state base_sha"):
            refused = self.run_cli("status", "w")
            self.assert_recovery_required(refused, "base_sha", "work/w/inner-loop/results/a.json")
        state_path.write_bytes(state_before)

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
        repair_state["tasks"]["CR-1"]["status"] = "integrated"
        state_path.write_text(json.dumps(repair_state, indent=2) + "\n", encoding="utf-8")
        second = self.run_cli("run", "continuation-recovery")
        self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
        self.assertIn("running=CR-2", second.stdout)
        self.assertEqual({name: (self.root / name).read_bytes() for name in legacy_files}, state_before)
        self.assertEqual(self.git("rev-parse", authority_ref), authority_before)


if __name__ == "__main__":
    unittest.main()
