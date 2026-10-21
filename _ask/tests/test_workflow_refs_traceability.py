"""Traceability authority and exact binding checks for numeric workflow references."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agents/ask"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from traceability_fixture import Consumer
from verification.traceability.contracts import Invalid
from verification.traceability.evidence import load_accepted, record_test_review
from verification.traceability.adapters import run_tests
from workflow_refs.codec import encode_envelope, normalize_envelope


class ReferenceTests(unittest.TestCase):
    def test_authority_rejects_candidate_substitution(self):
        consumer = Consumer()
        self.addCleanup(consumer.close)
        accepted = consumer.root / "work/w/traceability-accepted.json"
        original = json.loads(accepted.read_text())

        # A candidate cannot replace the coordinator-owned accepted contract pin.
        forged = copy.deepcopy(original)
        forged["contract_sha"] = consumer.sha
        accepted.write_text(json.dumps(forged, indent=2) + "\n")
        candidate = consumer.commit("candidate substitutes accepted pin")
        with self.assertRaisesRegex(Invalid, "coordinator|accepted obligations"):
            load_accepted(consumer.root, "w", candidate, candidate)

        # A copied review cannot be published by the reviewer as its own coordinator.
        review_path = "work/w/traceability/review-input.json"
        with self.assertRaisesRegex(Invalid, "independent reviewer and coordinator"):
            record_test_review(consumer.root, "w", consumer.sha, consumer.sha,
                               review_path, consumer.review["reviewer"])

    def test_exact_intent_and_canonical_contracts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            work = root / "work/example"
            work.mkdir(parents=True)
            intent = work / "intent.md"
            intent.write_bytes(b"# Approved intent\n\nUse numeric references.\n")
            record = {
                "schema": "ask-intent-confirmation/v2",
                "work_id": "example",
                "scope": "complete-intent-and-assumptions",
                "prompt": "Do you approve the complete intent and every listed assumption as written?",
                "human_choice": "approve",
                "intent_sha256": hashlib.sha256(intent.read_bytes()).hexdigest(),
            }
            (work / "intent-confirmation.json").write_text(json.dumps(record) + "\n")
            script = ROOT / "_ask/scripts/intent-confirmation.py"
            valid = subprocess.run([sys.executable, str(script), "validate", "--root", str(root),
                                    "--work-id", "example"], capture_output=True, text=True)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            intent.write_bytes(intent.read_bytes() + b"\n")
            stale = subprocess.run([sys.executable, str(script), "validate", "--root", str(root),
                                    "--work-id", "example"], capture_output=True, text=True)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("intent changed after confirmation", stale.stderr)

        context = {"owner": "team", "type": "spec"}
        encoded = encode_envelope({"items": [{"name": "n", "value": 4}]},
                                  "example/v1", context)
        reordered = json.dumps({"references": {}, "payload": {"items": [{"value": 4, "name": "n"}]},
                                "context": {"type": "spec", "owner": "team"},
                                "payload_schema": "example/v1", "schema": "ask-workflow-envelope/v1"})
        self.assertEqual(normalize_envelope(encoded), normalize_envelope(reordered))

    def test_contract_run_lifetimes_and_source_identity(self):
        # Run an immutable candidate whose test imports a module under its own
        # .agents/ask tree, independent of the caller's PYTHONPATH.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True,
                                               stderr=subprocess.PIPE).strip()
            git("init", "-q")
            git("config", "user.email", "test@example.com")
            git("config", "user.name", "Test")
            (root / ".agents/ask/workflow_refs").mkdir(parents=True)
            (root / ".agents/ask/workflow_refs/marker.py").write_text("VALUE = 42\n")
            (root / "test_app.py").write_text(
                "import unittest\nfrom workflow_refs.marker import VALUE\n"
                "class Cases(unittest.TestCase):\n"
                " def test_source_identity(self): self.assertEqual(VALUE, 42)\n")
            git("add", ".")
            git("commit", "-qm", "candidate with private package")
            sha = git("rev-parse", "HEAD")
            plan = {"tests": [{"id": "T", "runner_id": "r",
                               "case_id": "test_app.Cases.test_source_identity",
                               "source_paths": ["test_app.py", ".agents/ask/workflow_refs/marker.py"]}],
                    "runners": [{"id": "r", "adapter": "unittest",
                                 "argv": ["python3", "-m", "unittest", "test_app"]}],
                    "task_scopes": []}
            contracts = {"spec": {"work_id": "fixture"}, "plan": plan}
            old_path = os.environ.pop("PYTHONPATH", None)
            try:
                report = run_tests(root, contracts, sha)
            finally:
                if old_path is not None:
                    os.environ["PYTHONPATH"] = old_path
            self.assertEqual(report["executions"][0]["collection_status"], "ok")
            self.assertEqual(report["cases"][0]["outcome"], "passed")
            self.assertEqual(report["cases"][0]["source_sha"], sha)


if __name__ == "__main__":
    unittest.main()
