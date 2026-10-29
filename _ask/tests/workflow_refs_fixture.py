"""Small Git-backed fixtures for public workflow-reference end-to-end tests."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import shutil


class ReferenceRepository:
    """An isolated repository whose owner catalogs and refs are real Git objects."""

    def __init__(self, owners):
        self.temp = tempfile.TemporaryDirectory(prefix="refs-e2e-")
        self.root = Path(self.temp.name)
        self.git("init", "-q", "-b", "seed")
        self.git("config", "user.name", "E2E Fixture")
        self.git("config", "user.email", "fixture@example.test")
        self.owners = owners
        for owner, items in owners.items():
            path = self.root / "work" / owner / "items.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"items": payloads(items)}, separators=(",", ":")) + "\n")
        self.git("add", "work")
        self.git("commit", "-qm", "initial owner payloads")
        self.source_sha = self.git("rev-parse", "HEAD")
        self.git("branch", "develop", self.source_sha)
        self.git("branch", "main", self.source_sha)

        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
        from workflow_refs.store import initialize_catalog, register_revision

        for owner, items in owners.items():
            catalog = self.root / "work" / owner / "references" / "integrity.json"
            catalog.parent.mkdir(parents=True, exist_ok=True)
            initialize_catalog(catalog, owner)
            for item in items:
                register_revision(catalog, owner, item["logical_id"],
                                  {"commit": self.source_sha,
                                   "path": f"work/{owner}/items.json"},
                                  item["id"], "structured-item/1",
                                  (self.root / "work" / owner / "items.json").read_bytes())
        self.git("add", "work")
        self.git("commit", "-qm", "publish trusted owner catalogs")
        self.catalog_sha = self.git("rev-parse", "HEAD")
        for owner in owners:
            self.git("update-ref", f"refs/heads/agent/{owner}", self.source_sha)
            self.git("update-ref", f"refs/ask/references/{owner}", self.catalog_sha)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def close(self):
        self.temp.cleanup()

    def cli(self, *args):
        from workflow_refs.cli import main
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(list(args), root=self.root)
        try:
            value = json.loads(output.getvalue())
        except json.JSONDecodeError:
            value = output.getvalue()
        return code, value


class CompletionRepository:
    """Minimal accepted consumer exercising the real public Verify command."""

    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="refs-completion-e2e-")
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[2]
        self.git("init", "-q", "-b", "agent/e2e")
        self.git("config", "user.name", "E2E Fixture")
        self.git("config", "user.email", "fixture@example.test")
        shutil.copytree(source / ".agents/ask/verification", self.root / ".agents/ask/verification",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(source / "_ask/scripts", self.root / "_ask/scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(source / "ask", self.root / "ask")
        from verification.traceability.contracts import POLICY, digest
        policy = self.root / POLICY
        policy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / POLICY, policy)
        self.write(".agents/verification.yaml", "schema: ask-checkplan/v1\nchecks:\n  - id: syntax\n    tier: mandatory\n    command: python3 -c 'import ast; ast.parse(open(\"app.py\").read())'\n")
        self.write("app.py", "def value(): return 'ready'\n")
        self.write("test_app.py", "import unittest\nfrom app import value\nclass Cases(unittest.TestCase):\n def test_value(self): self.assertEqual(value(), 'ready')\n")
        self.spec = {"schema": "ask-spec/v1", "work_id": "e2e", "revision": 1,
                     "criteria": [{"id": "C1", "given": "a valid accepted consumer",
                                   "when": "Verify evaluates current evidence",
                                   "then": ["completion passes only for exact recorded evidence"],
                                   "verification_mode": "tests"}]}
        self.plan = {"schema": "ask-test-plan/v1", "work_id": "e2e",
                     "spec_digest": digest(self.spec),
                     "obligations": [{"criterion_id": "C1", "required_types": ["unit"]}],
                     "runners": [{"id": "unit", "adapter": "unittest",
                                  "argv": ["python3", "-m", "unittest", "test_app"]}],
                     "task_scopes": [],
                     "tests": [{"id": "T1", "criterion_ids": ["C1"], "type": "unit",
                                "change_kind": "regression",
                                "scenario": {"given": "ready", "when": "value() is called",
                                             "then": ["ready is returned"]},
                                "expected_assertions": [{"criterion_id": "C1",
                                                         "checks": ["Exact ready value"]}],
                                "runner_id": "unit", "case_id": "test_app.Cases.test_value",
                                "source_paths": ["app.py", "test_app.py"]}]}
        self.write("specs/current/e2e.json", self.spec)
        self.write("work/e2e/test-plan.json", self.plan)
        self.write("work/e2e/plan.md", "# E2E consumer plan\nVerify current accepted evidence.\n")
        self.commit("prepare accepted E2E consumer")
        review_path = "work/e2e/traceability/plan-review.json"
        self.write(review_path, {"decision": "APPROVED", "reviewer": "independent",
                                 "spec_digest": digest(self.spec), "plan_digest": digest(self.plan)})
        reviewed_sha = self.commit("review exact E2E contract")
        from verification.traceability.evidence import accept_plan
        accept_plan(self.root, "e2e", reviewed_sha, "independent", "coordinator", review_path)
        self.commit("pin accepted E2E contract")
        self.candidate = self.git("rev-parse", "HEAD")
        self.create_semantic_review()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n" if isinstance(value, dict) else value)

    def commit(self, message):
        self.git("add", "--all")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def create_semantic_review(self):
        from verification.traceability.contracts import digest
        from verification.traceability.evidence import inventory, record_test_review, source_digests
        base = self.git("rev-parse", f"refs/ask/accepted-tests/e2e")
        # record_test_review validates against the coordinator contract, not this ref's identity.
        accepted = json.loads(self.git("show", f"{base}:accepted.json"))
        inv = inventory(self.root, accepted["contract_sha"], self.candidate, self.plan)
        review = {"schema": "ask-test-review/v2", "reviewer": "independent",
                  "candidate_sha": self.candidate, "base_sha": accepted["contract_sha"],
                  "spec_digest": digest(self.spec), "plan_digest": digest(self.plan),
                  "scope": "workstream", "task_id": None, "test_ids": ["T1"],
                  "criterion_ids": ["C1"],
                  "source_digests": source_digests(self.root, self.candidate, self.plan),
                  "inspected_sources": inv["inspected_sources"],
                  "changed_cases": inv["changed_cases"], "inventory_exclusions": {},
                  "criteria": [{"id": "C1", "coverage_decision": "APPROVED",
                                "assessment": "The accepted assertion is exact.",
                                "type_adequacy": {"unit": {"decision": "APPROVED",
                                                              "assessment": "Unit case checks exact output."}}}],
                  "tests": [{"id": "T1", "decision": "APPROVED",
                             "assertion_assessment": "Checks the literal returned value.",
                             "counterexample": "Any other value fails.",
                             "tdd_continuity_assessment": "Regression test is retained and passes."}]}
        path = "work/e2e/traceability/review-input.json"
        self.write(path, review)
        record_test_review(self.root, "e2e", self.candidate, self.candidate, path, "coordinator")

    def command(self, *args):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([str(self.root / "ask"), *args], cwd=self.root,
                              capture_output=True, text=True, env=env)

    def close(self):
        self.temp.cleanup()


def item(logical_id, identity, inputs=(), **fields):
    value = {"id": identity, "inputs": list(inputs), **fields}
    return {"logical_id": logical_id, "id": identity, "payload": value}


def payloads(items):
    """Return source-document items, excluding fixture-only identity metadata."""
    return [entry["payload"] for entry in items]
