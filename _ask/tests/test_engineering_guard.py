"""Document admission through the public model commands."""
import json
from pathlib import Path
import tempfile
import unittest

from engineering_fixture import model_command, referenced_model, write_json


class DocumentGuardTests(unittest.TestCase):
    def test_linked_spec_change_invalidates_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            admitted = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(admitted.returncode, 0, admitted.stderr)
            old_digest = json.loads(admitted.stdout)["snapshot"]["digest"]
            raw_model = (root / "work/pilot/engineering-model.json").read_bytes()

            # A valid linked-Markdown-only edit invalidates a displayed identity.
            (root / "specs/current/pilot.md").write_text("# Amended pilot\n", encoding="utf-8")
            stale = model_command(root, "admit", "--work-id", "pilot", "--expected", old_digest)
            self.assertEqual(stale.returncode, 1, stale.stderr)
            self.assertIn("EM007_STALE_INPUT", {e["code"] for e in json.loads(stale.stdout)["diagnostics"]})
            refreshed = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(refreshed.returncode, 0, refreshed.stderr)
            self.assertNotEqual(json.loads(refreshed.stdout)["snapshot"]["digest"], old_digest)
            self.assertEqual((root / "work/pilot/engineering-model.json").read_bytes(), raw_model)

            # Finding an ID in arbitrary JSON is not canonical definition validity.
            spec["schema"] = "not-a-spec"
            write_json(root, "specs/current/pilot.json", spec)
            malformed = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(malformed.returncode, 1, "canonical schema must be checked, not just selected ID existence")
            self.assertTrue(any(e["path"] == "specs/current/pilot.json" for e in json.loads(malformed.stdout)["diagnostics"]))

            target = root / "specs/current/pilot.json"
            target.unlink()
            deleted = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(deleted.returncode, 1, deleted.stderr)
            spec["schema"] = "ask-spec/v1"
            write_json(root, "specs/current/pilot.json", spec)
            created = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(created.returncode, 0, created.stderr)

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
