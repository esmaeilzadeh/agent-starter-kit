"""Numeric workflow references at inner-loop persistence boundaries."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))

from inner_loop.checkpoint import publish, read_checkpoint
from inner_loop.state import load_state


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
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

        self.assertEqual(persisted.get("schema"), "ask-workflow-envelope/v1")
        self.assertEqual(persisted.get("payload_schema"), "ask-inner-loop-state/v1")
        self.assertEqual(restored, state)
        self.assertEqual(load_state(self.root, "fixture-work"), state)

    def test_evidence_projection_and_exact_runner(self):
        state = self.state()
        path = self.root / "work/fixture-work/inner-loop/state.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(state, indent=2) + "\n")
        checkpoint = publish(self.root, "fixture-work", state)

        _commit, restored, artifacts = read_checkpoint(self.root, "fixture-work", checkpoint)
        self.assertEqual(restored["tasks"]["6"]["evidence"],
                         state["tasks"]["6"]["evidence"])
        self.assertEqual(load_state(self.root, "fixture-work")["tasks"]["6"],
                         state["tasks"]["6"])
        self.assertIn("artifacts/work/fixture-work/inner-loop/state.json", artifacts)


if __name__ == "__main__":
    unittest.main()
