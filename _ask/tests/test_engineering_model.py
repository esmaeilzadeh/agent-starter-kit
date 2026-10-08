"""Behavior checks at the shared Engineering Model validation seam."""
import copy
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from engineering_model.validation import validate
from engineering_model.__main__ import main
from engineering_fixture import decision_model, referenced_model, write_json


class ModelValidationTests(unittest.TestCase):
    def test_reference_escape_and_missing_criterion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            self.assertEqual(validate(model, root, "pilot"), [])
            requirement = model["nodes"][-1]
            requirement["reference"]["id"] = "MISSING"
            self.assertIn("EM001_REFERENCE_ID", {e["code"] for e in validate(model, root, "pilot")})
            requirement["reference"]["id"] = "P-001"
            for unsafe in ("../outside.json", "/outside.json", "C:\\outside.json"):
                requirement["reference"]["path"] = unsafe
                self.assertIn("EM001_REFERENCE_PATH", {e["code"] for e in validate(model, root, "pilot")})
            requirement["reference"]["path"] = "specs/current/pilot.json"

            # Simulate an external editor replacing a definition immediately after
            # its bytes have been read. The filesystem is the system boundary.
            target = root / "specs/current/pilot.json"
            original_read_bytes = Path.read_bytes
            original_read_text = Path.read_text
            changed = False

            def change_after_read(path, value):
                nonlocal changed
                if path == target and not changed:
                    changed = True
                    replacement = copy.deepcopy(spec)
                    replacement["criteria"] = []
                    write_json(root, "specs/current/pilot.json", replacement)
                return value

            def read_bytes(path):
                return change_after_read(path, original_read_bytes(path))

            def read_text(path, *args, **kwargs):
                return change_after_read(path, original_read_text(path, *args, **kwargs))

            output = io.StringIO()
            previous = Path.cwd()
            try:
                os.chdir(root)
                with patch.object(Path, "read_bytes", read_bytes), patch.object(Path, "read_text", read_text), contextlib.redirect_stdout(output):
                    status = main(["validate", "--work-id", "pilot"])
            finally:
                os.chdir(previous)
            result = json.loads(output.getvalue())
            self.assertEqual(status, 1, "a concurrent referenced-file edit cannot receive a valid receipt")
            self.assertFalse(result["valid"])
            self.assertIn("EM007_INPUT_CHANGED", {e["code"] for e in result["diagnostics"]})

    def test_malformed_fields_and_lifecycle(self):
        model = decision_model()
        for option in model["nodes"][1]["options"]:
            option["label"] = "Same"
        original = copy.deepcopy(model)
        with tempfile.TemporaryDirectory() as directory:
            errors = validate(model, directory, "pilot")
            self.assertTrue(any(error["code"] == "EM001_DECISION_OPTION"
                                and "label" in error["path"] for error in errors),
                            "two different option IDs must not allow the same label")
            self.assertEqual(model, original, "validation must not repair its input")

            model["nodes"][1]["options"][1]["label"] = "Different"
            self.assertEqual(validate(model, directory, "pilot"), [])
            model["nodes"][1]["lifecycle"] = "resolved"
            self.assertIn("EM001_DECISION_RESOLUTION", {e["code"] for e in validate(model, directory, "pilot")})

            malformed = copy.deepcopy(model)
            malformed["nodes"][1]["type"] = []
            malformed["nodes"].append({"id": "code", "type": "implementation", "title": "Source",
                                        "lifecycle": "active", "reference": {"path": "source.py"}})
            malformed["edges"].append({"type": "implements", "source": "code", "target": "choice"})
            errors = validate(malformed, directory, "pilot")
            self.assertIn("EM001_NODE_TYPE", {e["code"] for e in errors})
            self.assertIn("EM001_ILLEGAL_EDGE", {e["code"] for e in errors})

            malformed = copy.deepcopy(model)
            malformed["revision"] = True
            malformed["unexpected"] = "field"
            malformed["nodes"][0]["title"] = " "
            errors = validate(malformed, directory, "pilot")
            self.assertTrue({"EM001_REVISION", "EM001_FIELD", "EM001_TITLE"}.issubset({e["code"] for e in errors}))
