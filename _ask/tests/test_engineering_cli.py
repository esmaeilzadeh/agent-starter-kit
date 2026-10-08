"""Public CLI journeys for the Engineering Model sidecar."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask/verification"))
from engineering_fixture import model_command, referenced_model, write_json
from traceability.contracts import digest


class CliJourneyTests(unittest.TestCase):
    def test_cli_inspect_resolve_reload_and_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            model["nodes"].extend([
                {"id": "scenario", "type": "scenario", "title": "Canonical scenario", "lifecycle": "active",
                 "reference": {"path": "specs/current/pilot.json", "id": "P-001"}},
                {"id": "case", "type": "test", "title": "Canonical case", "lifecycle": "active",
                 "reference": {"path": "work/pilot/test-plan.json", "id": "CASE-1"}},
                {"id": "build", "type": "task", "title": "Build dependent work", "lifecycle": "planned"},
            ])
            model["edges"].extend([
                {"type": "contains", "source": "requirement", "target": "scenario"},
                {"type": "covers", "source": "case", "target": "scenario"},
                {"type": "contains", "source": "purpose", "target": "build"},
                {"type": "depends_on", "source": "build", "target": "choice"},
            ])
            spec["criteria"][0].update(given="A valid input", when="The scenario runs", then=["Canonical outcome"])
            write_json(root, "specs/current/pilot.json", spec)
            write_json(root, "work/pilot/engineering-model.json", model)
            write_json(root, "work/pilot/test-plan.json", {
                "schema": "ask-test-plan/v1", "work_id": "pilot",
                "spec_digest": digest(spec),
                "obligations": [{"criterion_id": "P-001", "required_types": ["unit"]}],
                "runners": [{"id": "fixture-runner", "adapter": "unittest",
                             "argv": ["python3", "-m", "unittest", "test_engineering_cli.CliJourneyTests.test_cli_inspect_resolve_reload_and_invalid"]}],
                "tests": [{"id": "CASE-1", "criterion_ids": ["P-001"], "type": "unit",
                           "change_kind": "new", "scenario": {"given": "Input", "when": "Run", "then": ["Assertion"]},
                           "expected_assertions": [{"criterion_id": "P-001", "checks": ["Assertion"]}],
                           "runner_id": "fixture-runner", "case_id": "fixture.Case.test_it",
                           "source_paths": ["_ask/tests/test_engineering_cli.py"]}],
                "task_scopes": [],
            })

            validated = model_command(root, "validate", "--work-id", "pilot")
            self.assertEqual(validated.returncode, 0, validated.stdout)
            admitted = json.loads(model_command(root, "admit", "--work-id", "pilot").stdout)
            self.assertTrue(admitted["valid"], admitted)
            shown = model_command(root, "show", "--work-id", "pilot", "--format", "json", "--node", "scenario")
            self.assertEqual(shown.returncode, 0, shown.stderr)
            view = json.loads(shown.stdout)
            self.assertEqual(view["scenarios"][0]["given"], "A valid input")
            self.assertEqual(view["scenarios"][0]["tests"][0]["id"], "CASE-1")
            self.assertFalse(view["scenarios"][0].get("current_completion", False))
            identity = view["snapshot"]["digest"]

            proposal = write_json(root, "proposal.json", {"commands": [{"op": "resolve_decision", "id": "choice",
                "option_id": "one", "actor": "Developer", "rationale": "Selected for this fixture"}]})
            edited = model_command(root, "edit", "--work-id", "pilot", "--expected", identity, "--batch", str(proposal))
            self.assertEqual(edited.returncode, 0, edited.stdout)
            reloaded = model_command(root, "show", "--work-id", "pilot", "--format", "json")
            self.assertEqual(reloaded.returncode, 0, reloaded.stderr)
            after = json.loads(reloaded.stdout)
            self.assertEqual(next(node for node in after["model"]["nodes"] if node["id"] == "choice")["lifecycle"], "resolved")
            self.assertEqual(next(task for task in after["tasks"] if task["id"] == "build")["status"], "ready")

            model_path = root / "work/pilot/engineering-model.json"
            before = model_path.read_bytes()
            invalid = write_json(root, "invalid-proposal.json", {"commands": [{"op": "resolve_decision", "id": "choice",
                "option_id": "missing", "actor": "Developer", "rationale": "Invalid option"}]})
            refused = model_command(root, "edit", "--work-id", "pilot", "--expected", after["snapshot"]["digest"],
                                    "--batch", str(invalid))
            self.assertEqual(refused.returncode, 1)
            self.assertTrue(json.loads(refused.stdout)["diagnostics"])
            self.assertEqual(model_path.read_bytes(), before)
