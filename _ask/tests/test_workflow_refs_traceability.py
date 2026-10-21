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
from workflow_refs.codec import EnvelopeError, encode_envelope, normalize_envelope
from verification.traceability.completion import evaluate_completion
from verification.traceability.contracts import digest
from verification.traceability.evidence import accept_plan, load_accepted, record_test_review
from workflow_refs.store import initialize_catalog, register_revision, resolve_version


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
        with self.assertRaises(EnvelopeError):
            normalize_envelope({"schema": "ask-workflow-envelope/v1",
                                "payload_schema": "example/v1", "context": context,
                                "references": {}})

        consumer = Consumer()
        self.addCleanup(consumer.close)
        log = consumer.root / consumer.green["cases"][0]["output_artifact"]
        log.write_text("forged execution output\n")
        rejected = evaluate_completion(consumer.contracts, consumer.record,
                                       [consumer.red, consumer.green], consumer.context())
        self.assertEqual(rejected["status"], "fail")

    def test_contract_run_lifetimes_and_source_identity(self):
        # Run an immutable candidate while an unrelated installed package is
        # on PYTHONPATH. The candidate package and source identity must win.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            host = root / "host"
            (host / "workflow_refs").mkdir(parents=True)
            (host / "workflow_refs/__init__.py").write_text("")
            (host / "workflow_refs/marker.py").write_text("VALUE = 99\n")
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True,
                                               stderr=subprocess.PIPE).strip()
            git("init", "-q")
            git("config", "user.email", "test@example.com")
            git("config", "user.name", "Test")
            (root / ".agents/ask/workflow_refs").mkdir(parents=True)
            (root / ".agents/ask/workflow_refs/__init__.py").write_text("")
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
            old_path = os.environ.get("PYTHONPATH")
            os.environ["PYTHONPATH"] = str(host)
            try:
                report = run_tests(root, contracts, sha)
            finally:
                if old_path is None:
                    os.environ.pop("PYTHONPATH", None)
                else:
                    os.environ["PYTHONPATH"] = old_path
            self.assertEqual(report["executions"][0]["collection_status"], "ok")
            self.assertEqual(report["cases"][0]["outcome"], "passed")
            self.assertEqual(report["cases"][0]["source_sha"], sha)

        consumer = Consumer()
        self.addCleanup(consumer.close)
        accepted_before = consumer.contracts["pin"]
        old_candidate = consumer.sha
        payload = {"id": "tracked-item", "inputs": []}
        consumer.write("work/w/items.json", {"items": [payload]})
        source_sha = consumer.commit("publish numeric reference source snapshot")
        catalog_path = consumer.root / "work/w/references/integrity.json"
        initialize_catalog(catalog_path, "w")
        source_payload = (consumer.root / "work/w/items.json").read_bytes()
        entry = register_revision(catalog_path, "w", "w/spec/1/plan/1/item/1",
                                  {"commit": source_sha, "path": "work/w/items.json"},
                                  "tracked-item", "structured-item/1", source_payload)
        reference = entry["reference"]
        resolved = resolve_version(catalog_path, reference, consumer.root)
        self.assertEqual(resolved["entry"]["reference"], "w/spec/1/plan/1/item/1@1")
        self.assertIn(b"tracked-item", resolved["payload"])
        consumer.write("work/w/binding.json", {"reference": reference})
        newer_binding = consumer.commit("candidate adds registered numeric item binding")
        accepted = load_accepted(consumer.root, "w", old_candidate, newer_binding)
        self.assertEqual(accepted["pin"], accepted_before)
        consumer.sha = newer_binding
        consumer.contracts = accepted
        review = consumer.make_review()
        consumer.write("work/w/traceability/review-input.json", review)
        current_record = record_test_review(consumer.root, "w", newer_binding, newer_binding,
                                            "work/w/traceability/review-input.json", "fixture-coordinator")
        current_green = run_tests(consumer.root, accepted, newer_binding)
        stale = evaluate_completion(accepted, current_record,
                                    [consumer.red, consumer.green],
                                    {**consumer.context(), "candidate_sha": newer_binding})
        self.assertEqual(stale["status"], "fail")
        self.assertTrue(any("stale final candidate" in error for error in stale["errors"]), stale)

        # Register a separately reviewed contract amendment and require new
        # source-bound Red/Green and semantic-review evidence under that pin.
        amended_plan = copy.deepcopy(accepted["plan"])
        amended_plan["reference_bindings"] = {
            "work/w/binding.json": reference,
        }
        consumer.plan = amended_plan
        consumer.write("work/w/test-plan.json", amended_plan)
        consumer.write("work/w/traceability/plan-review-amendment.json", {
            "decision": "APPROVED", "reviewer": "fixture-independent",
            "spec_digest": digest(consumer.spec),
            "plan_digest": digest(amended_plan),
        })
        amendment_sha = consumer.commit("reviewed reference-binding contract amendment")
        accept_plan(consumer.root, "w", amendment_sha, "fixture-independent",
                    "fixture-coordinator", "work/w/traceability/plan-review-amendment.json")
        final_sha = consumer.commit("publish coordinator accepted amendment")
        consumer.sha = final_sha
        consumer.contracts = load_accepted(consumer.root, "w", final_sha, final_sha)
        red = run_tests(consumer.root, consumer.contracts, consumer.red_sha, phase="red")
        consumer.review = consumer.make_review()
        consumer.write("work/w/traceability/review-input.json", consumer.review)
        record = record_test_review(consumer.root, "w", final_sha, final_sha,
                                    "work/w/traceability/review-input.json", "fixture-coordinator")
        green = run_tests(consumer.root, consumer.contracts, final_sha)
        completed = evaluate_completion(consumer.contracts, record, [red, green],
                                        {"root": consumer.root, "candidate_sha": final_sha,
                                         "scope": "workstream", "task_id": None,
                                         "static_checks": {"result": "pass", "candidate_sha": final_sha}})
        self.assertEqual(completed["status"], "pass", completed)


if __name__ == "__main__":
    unittest.main()
