"""Behavior checks at the shared Engineering Model validation seam."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from engineering_model.validation import validate


class ModelValidationTests(unittest.TestCase):
    def test_malformed_fields_and_lifecycle(self):
        model = {
            "schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
            "nodes": [
                {"id": "purpose", "type": "intent", "title": "Purpose", "lifecycle": "active"},
                {"id": "choice", "type": "decision", "title": "Choose", "lifecycle": "open",
                 "options": [{"id": "one", "label": "Same"}, {"id": "two", "label": "Same"}],
                 "history": []},
            ],
            "edges": [{"type": "contains", "source": "purpose", "target": "choice"}],
        }
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
