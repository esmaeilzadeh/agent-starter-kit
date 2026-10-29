"""Numeric workflow references at inner-loop persistence boundaries."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
sys.path.insert(0, str(ROOT / ".agents/ask"))

from inner_loop.checkpoint import publish, read_checkpoint
from inner_loop.state import load_state
from inner_loop.evidence import NotIntegrable, _execution_row
from verification.traceability.contracts import digest
from verification.traceability.evidence import accept_plan, load_accepted, write_json
from verification.traceability.adapters import run_tests


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        policy = self.root / "_ask/policies/delegation.md"
        policy.parent.mkdir(parents=True)
        policy.write_text("Coordinator delegates reviews to an identified independent reviewer.\n")
        (self.root / "seed.txt").write_text("seed\n")
        self.git("add", "seed.txt")
        self.git("commit", "-qm", "fixture base")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def state(self):
        return {
            "schema": "ask-inner-loop-state/v1",
            "work_id": "fixture-work",
            "revision": 4,
            "coordinator_sha": self.git("rev-parse", "HEAD"),
            "coordinator_branch": "agent/fixture-work",
            "tasks": {
                "6": {
                    "status": "pending",
                    "base_sha": "",
                    "task_branch": "",
                    "result_path": "",
                    "boundary_reject": None,
                    "review_round": 0,
                    "debug_round": 0,
                    "evidence": {
                        "traceability_runs": [{
                            "run_id": "run-6-green",
                            "digest": "a" * 64,
                            "phase": "final_green",
                            "task_id": "6",
                            "candidate_sha": "b" * 40,
                            "spec_digest": "c" * 64,
                            "plan_digest": "d" * 64,
                            "test_ids": ["6/1"],
                        }],
                    },
                    "attempt_number": 0,
                    "attempt_id": "",
                    "attempt_history": [],
                },
            },
        }

    def test_qualified_tasks_and_cas_recovery(self):
        state = self.state()
        path = self.root / "work/fixture-work/inner-loop/state.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(state, indent=2) + "\n")

        checkpoint = publish(self.root, "fixture-work", state)
        _commit, restored, artifacts = read_checkpoint(self.root, "fixture-work", checkpoint)
        persisted = json.loads(artifacts[
            "artifacts/work/fixture-work/inner-loop/state.json"
        ])

        self.assertEqual(restored, state)
        self.assertEqual(load_state(self.root, "fixture-work"), state)
        self.assertEqual(persisted.get("schema"), "ask-workflow-envelope/v1")
        self.assertEqual(persisted.get("payload_schema"), "ask-inner-loop-state/v1")
        self.assertEqual(persisted.get("references", {}).get("task:6"),
                         {"id": 6, "revision": 1})

    def test_evidence_projection_and_exact_runner(self):
        state = self.state()
        path = self.root / "work/fixture-work/inner-loop/state.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(state, indent=2) + "\n")
        checkpoint = publish(self.root, "fixture-work", state)

        _commit, restored, artifacts = read_checkpoint(self.root, "fixture-work", checkpoint)
        envelope = json.loads(artifacts[
            "artifacts/work/fixture-work/inner-loop/state.json"
        ])
        self.assertEqual(restored["tasks"]["6"]["evidence"],
                         state["tasks"]["6"]["evidence"])
        self.assertEqual(load_state(self.root, "fixture-work")["tasks"]["6"],
                         state["tasks"]["6"])
        self._assert_task_scoped_run()
        self.assertIn("test:6/1", envelope.get("references", {}))
        self.assertIn("artifacts/work/fixture-work/inner-loop/state.json", artifacts)

    def _assert_task_scoped_run(self):
        verifier = ROOT / ".agents/ask/verification"
        shutil.copytree(verifier, self.root / ".agents/ask/verification",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.root / "task_cases.py").write_text(
            "import unittest\n"
            "class Cases(unittest.TestCase):\n"
            " def test_six_one(self): self.assertEqual(2 + 2, 4)\n"
            " def test_six_two(self): self.assertEqual(3 + 3, 6)\n"
        )
        self.git("add", ".agents/ask/verification", "task_cases.py")
        graph_path = self.root / "work/fixture-work/inner-loop/tasks.yaml"
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        graph_path.write_text(
            "schema: ask-inner-loop-tasks/v1\nwork_id: fixture-work\ntasks:\n"
            "  - id: '6'\n    depends_on: []\n    owned_paths: [task_cases.py]\n"
            "  - id: '7'\n    depends_on: []\n    owned_paths: [task_cases.py]\n"
        )
        spec = {
            "schema": "ask-spec/v1", "work_id": "fixture-work", "revision": 1,
            "criteria": [{"id": "C1", "given": "A mapped case exists",
                          "when": "the selected task runs", "then": ["its accepted case runs"],
                          "verification_mode": "tests"}],
        }
        plan = {
            "schema": "ask-test-plan/v1", "work_id": "fixture-work",
            "spec_digest": digest(spec),
            "obligations": [{"criterion_id": "C1", "required_types": ["unit"]}],
            "runners": [{"id": "unit", "adapter": "unittest",
                         "argv": ["python3", "-m", "unittest", "task_cases"]}],
            "tests": [
                {"id": "6/1", "criterion_ids": ["C1"], "type": "unit", "change_kind": "new",
                 "scenario": {"given": "Mapped to task 6", "when": "selected", "then": ["runs"]},
                 "expected_assertions": [{"criterion_id": "C1", "checks": ["Exact result"]}],
                 "runner_id": "unit", "case_id": "task_cases.Cases.test_six_one",
                 "source_paths": ["task_cases.py"]},
                {"id": "6/2", "criterion_ids": ["C1"], "type": "unit", "change_kind": "new",
                 "scenario": {"given": "Mapped to task 7", "when": "selected", "then": ["runs"]},
                 "expected_assertions": [{"criterion_id": "C1", "checks": ["Exact result"]}],
                 "runner_id": "unit", "case_id": "task_cases.Cases.test_six_two",
                 "source_paths": ["task_cases.py"]},
            ],
            "task_scopes": [{"task_id": "6", "test_ids": ["6/1"]},
                            {"task_id": "7", "test_ids": ["6/2"]}],
        }
        (self.root / "specs/current/fixture-work.json").parent.mkdir(parents=True)
        write_json(self.root / "specs/current/fixture-work.json", spec)
        write_json(self.root / "work/fixture-work/test-plan.json", plan)
        self.git("add", "_ask/policies/delegation.md", "specs/current/fixture-work.json",
                 "work/fixture-work")
        self.git("commit", "-qm", "task-scoped contract fixture")
        contract_base = self.git("rev-parse", "HEAD")
        review_path = "work/fixture-work/traceability/plan-review.json"
        write_json(self.root / review_path, {
            "decision": "APPROVED", "reviewer": "fixture-reviewer",
            "spec_digest": digest(spec), "plan_digest": digest(plan),
        })
        accept_plan(self.root, "fixture-work", contract_base, "fixture-reviewer",
                    "fixture-coordinator", review_path)
        self.git("add", "work/fixture-work/traceability-accepted.json")
        self.git("commit", "-qm", "accept task-scoped contract fixture")
        candidate = self.git("rev-parse", "HEAD")
        contracts = load_accepted(self.root, "fixture-work", candidate, candidate)
        report = run_tests(self.root, contracts, candidate,
                           scope="task", task_id="6")
        self.assertEqual([case["test_id"] for case in report["cases"]], ["6/1"])
        self.assertEqual(report["cases"][0]["source_sha"], candidate)
        execution = report["executions"][0]
        self.assertEqual(execution["source_sha"], candidate)
        self.assertEqual(execution["runner_id"], "unit")
        self.assertEqual(report["runner_identity"]["adapter_digest"], hashlib.sha256(
            (self.root / ".agents/ask/verification/traceability/unittest_runner.py").read_bytes()
        ).hexdigest())
        task_state = {"status": "running", "base_sha": candidate, "task_branch": "",
                      "evidence": {}, "attempt_history": []}
        _execution_row(self.root, "fixture-work", "6", report["run_id"],
                       state={"tasks": {"6": task_state}})
        output = self.root / execution["output_artifact"]
        self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),
                         execution["output_digest"])
        output.write_bytes(output.read_bytes() + b"tampered\n")
        with self.assertRaisesRegex(NotIntegrable, "output log digest/binding is invalid"):
            _execution_row(self.root, "fixture-work", "6", report["run_id"],
                           state={"tasks": {"6": task_state}})


if __name__ == "__main__":
    unittest.main()
