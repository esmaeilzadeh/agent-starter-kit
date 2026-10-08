"""Document admission through the public model commands."""
import json
from pathlib import Path
import tempfile
import unittest

from engineering_fixture import model_command, referenced_model, write_json


class DocumentGuardTests(unittest.TestCase):
    def test_bootstrap_admits_only_validated_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            admitted = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(admitted.returncode, 0, admitted.stderr)
            receipt = json.loads(admitted.stdout)
            self.assertTrue(receipt["valid"])
            identity = receipt["snapshot"]["digest"]
            shown = model_command(root, "show", "--work-id", "pilot")
            self.assertEqual(shown.returncode, 0, shown.stderr)
            projection = json.loads(shown.stdout)
            self.assertEqual(projection["snapshot"]["digest"], identity)
            self.assertEqual(projection["model"], model)
            self.assertTrue(projection["editable"])

            spec["criteria"] = []
            write_json(root, "specs/current/pilot.json", spec)
            blocked = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(blocked.returncode, 1, blocked.stderr)
            self.assertFalse(json.loads(blocked.stdout)["valid"])
            # An invalid external save cannot replace the last stable snapshot.
            shown = model_command(root, "show", "--work-id", "pilot")
            self.assertEqual(shown.returncode, 1, shown.stderr)
            projection = json.loads(shown.stdout)
            self.assertEqual(projection["snapshot"]["digest"], identity)
            self.assertEqual(projection["model"], model)
            self.assertFalse(projection["editable"])
            self.assertTrue(projection["last_validated"])

            # A current workspace does not make altered generation bytes trusted.
            _model, original_spec = referenced_model(root)
            generation = root / "work/pilot/traceability/model-state/generations" / identity
            blob = generation / "blobs" / receipt["snapshot"]["model"]["sha256"]
            blob.write_bytes(b"{}")
            corrupted = model_command(root, "show", "--work-id", "pilot")
            self.assertEqual(corrupted.returncode, 1, "a corrupt stored generation must not be reused as valid")
            self.assertFalse(json.loads(corrupted.stdout)["editable"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            model["nodes"] = []
            write_json(root, "work/pilot/engineering-model.json", model)
            blocked = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(blocked.returncode, 1, blocked.stderr)
            shown = model_command(root, "show", "--work-id", "pilot")
            self.assertEqual(shown.returncode, 1, shown.stderr)
            self.assertIsNone(json.loads(shown.stdout)["snapshot"])
