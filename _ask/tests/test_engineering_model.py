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
    def test_valid_broad_model_and_external_refs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_json(root, "specs/current/pilot.json", {
                "schema": "ask-spec/v1", "work_id": "pilot", "revision": 1,
                "criteria": [
                    {"id": "REQ-1", "given": "A request", "when": "Processed", "then": ["It succeeds"]},
                    {"id": "SCN-1", "given": "A scenario", "when": "Run", "then": ["It is covered"]},
                ],
            })
            write_json(root, "work/pilot/test-plan.json", {
                "tests": [{"id": "MV-valid"}],
            })
            write_json(root, "src/example.json", {"source": "representative implementation"})
            write_json(root, "evidence/run.json", {"status": "available"})

            model = {
                "schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
                "nodes": [
                    {"id": "purpose", "type": "intent", "title": "Purpose", "lifecycle": "active"},
                    {"id": "delivery", "type": "feature", "title": "Delivery", "lifecycle": "active"},
                    {"id": "requirement", "type": "requirement", "title": "Requirement", "lifecycle": "active",
                     "reference": {"path": "specs/current/pilot.json", "id": "REQ-1"}},
                    {"id": "user-story", "type": "story", "title": "User story", "lifecycle": "active"},
                    {"id": "scenario", "type": "scenario", "title": "Scenario", "lifecycle": "active",
                     "reference": {"path": "specs/current/pilot.json", "id": "SCN-1"}},
                    {"id": "implementation-task", "type": "task", "title": "Implement", "lifecycle": "planned"},
                    {"id": "choice", "type": "decision", "title": "Choice", "lifecycle": "open",
                     "options": [{"id": "one", "label": "First"}, {"id": "two", "label": "Second"}], "history": []},
                    {"id": "assumption", "type": "assumption", "title": "Assumption", "lifecycle": "unverified"},
                    {"id": "source", "type": "implementation", "title": "Source", "lifecycle": "active",
                     "reference": {"path": "src/example.json", "symbol": "handler"}},
                    {"id": "check", "type": "test", "title": "Check", "lifecycle": "active",
                     "reference": {"path": "work/pilot/test-plan.json", "id": "MV-valid"}},
                    {"id": "test-run", "type": "test_run", "title": "Run", "lifecycle": "draft",
                     "reference": {"path": "evidence/run.json"}},
                    {"id": "risk", "type": "risk", "title": "Risk", "lifecycle": "open"},
                    {"id": "proof", "type": "evidence", "title": "Evidence", "lifecycle": "active",
                     "reference": {"path": "evidence/run.json"}},
                ],
                "edges": [
                    {"type": "contains", "source": "purpose", "target": "delivery"},
                    {"type": "contains", "source": "delivery", "target": "requirement"},
                    {"type": "contains", "source": "delivery", "target": "user-story"},
                    {"type": "contains", "source": "user-story", "target": "scenario"},
                    {"type": "contains", "source": "delivery", "target": "implementation-task"},
                    {"type": "contains", "source": "purpose", "target": "choice"},
                    {"type": "contains", "source": "purpose", "target": "assumption"},
                    {"type": "contains", "source": "purpose", "target": "risk"},
                    {"type": "implements", "source": "source", "target": "scenario"},
                    {"type": "covers", "source": "check", "target": "scenario"},
                    {"type": "executes", "source": "test-run", "target": "check"},
                    {"type": "supports", "source": "proof", "target": "test-run"},
                    {"type": "depends_on", "source": "implementation-task", "target": "choice"},
                ],
            }

            self.assertEqual(validate(model, root, "pilot"), [])

            no_intent = copy.deepcopy(model)
            no_intent["nodes"] = [node for node in no_intent["nodes"] if node["type"] != "intent"]
            errors = validate(no_intent, root, "pilot")
            self.assertTrue(any(error["code"] == "EM001_INTENT_COUNT"
                                and error["path"] == "$.nodes" for error in errors), errors)

            draft_test_without_coverage = copy.deepcopy(model)
            draft_test_without_coverage["nodes"][9]["lifecycle"] = "draft"
            draft_test_without_coverage["edges"] = [
                edge for edge in draft_test_without_coverage["edges"]
                if not (edge["type"] == "covers" and edge["source"] == "check")
            ]
            errors = validate(draft_test_without_coverage, root, "pilot")
            coverage_errors = [error for error in errors if error["code"] == "EM001_TEST_COVERAGE"]
            self.assertEqual(len(coverage_errors), 1, errors)
            self.assertEqual(coverage_errors[0]["path"], "$.nodes[9]")
            self.assertEqual(coverage_errors[0]["ids"], ["check"])

    def test_duplicate_missing_illegal_cardinality_and_cycles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = {
                "schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
                "nodes": [
                    {"id": "purpose", "type": "intent", "title": "Purpose", "lifecycle": "active"},
                    {"id": "delivery", "type": "feature", "title": "Delivery", "lifecycle": "active"},
                    {"id": "work-item", "type": "task", "title": "Work", "lifecycle": "planned"},
                    {"id": "work-item-two", "type": "task", "title": "More work", "lifecycle": "planned"},
                    {"id": "choice", "type": "decision", "title": "Choice", "lifecycle": "open",
                     "options": [{"id": "one", "label": "First"}, {"id": "two", "label": "Second"}], "history": []},
                    {"id": "assumption", "type": "assumption", "title": "Assumption", "lifecycle": "unverified"},
                ],
                "edges": [
                    {"type": "contains", "source": "purpose", "target": "delivery"},
                    {"type": "contains", "source": "delivery", "target": "work-item"},
                    {"type": "contains", "source": "delivery", "target": "work-item-two"},
                ],
            }

            duplicate_id = copy.deepcopy(base)
            duplicate_id["nodes"].append({"id": "delivery", "type": "feature", "title": "Duplicate", "lifecycle": "draft"})
            errors = validate(duplicate_id, root, "pilot")
            matches = [error for error in errors if error["code"] == "EM001_DUPLICATE_ID"]
            self.assertEqual([(error["path"], error["ids"]) for error in matches],
                             [("$.nodes[6].id", ["delivery"])], errors)

            duplicate_edge = copy.deepcopy(base)
            duplicate_edge["edges"].append(copy.deepcopy(duplicate_edge["edges"][0]))
            errors = validate(duplicate_edge, root, "pilot")
            matches = [error for error in errors if error["code"] == "EM001_DUPLICATE_EDGE"]
            self.assertEqual([(error["path"], error["ids"]) for error in matches],
                             [("$.edges[3]", ["purpose", "delivery"])], errors)

            dangling = copy.deepcopy(base)
            dangling["edges"].append({"type": "contains", "source": "purpose", "target": "missing"})
            errors = validate(dangling, root, "pilot")
            matches = [error for error in errors if error["code"] == "EM001_DANGLING_EDGE"]
            self.assertEqual([(error["path"], error["ids"]) for error in matches],
                             [("$.edges[3]", ["purpose", "missing"])], errors)

            illegal = copy.deepcopy(base)
            illegal["edges"].append({"type": "contains", "source": "work-item", "target": "delivery"})
            errors = validate(illegal, root, "pilot")
            matches = [error for error in errors if error["code"] == "EM001_ILLEGAL_EDGE"]
            self.assertEqual([(error["path"], error["ids"]) for error in matches],
                             [("$.edges[3]", ["work-item", "delivery"])], errors)

            no_parent = copy.deepcopy(base)
            no_parent["edges"] = [edge for edge in no_parent["edges"] if edge["target"] != "work-item"]
            errors = validate(no_parent, root, "pilot")
            matches = [error for error in errors if error["code"] == "EM001_PARENT_COUNT"]
            self.assertEqual([(error["path"], error["ids"]) for error in matches],
                             [("$.nodes[2]", ["work-item"])], errors)

            multiple_parents = copy.deepcopy(base)
            multiple_parents["edges"].append({"type": "contains", "source": "purpose", "target": "work-item"})
            errors = validate(multiple_parents, root, "pilot")
            matches = [error for error in errors if error["code"] == "EM001_PARENT_COUNT"]
            self.assertEqual([(error["path"], error["ids"]) for error in matches],
                             [("$.nodes[2]", ["work-item"])], errors)

            containment_cycle = copy.deepcopy(base)
            containment_cycle["edges"].append({"type": "contains", "source": "delivery", "target": "purpose"})
            errors = validate(containment_cycle, root, "pilot")
            matches = [error for error in errors if error["code"] == "EM001_CONTAINS_CYCLE"]
            self.assertEqual([(error["path"], error["ids"]) for error in matches],
                             [("$.edges", ["delivery", "purpose", "delivery"])], errors)

            dependency_cycle = copy.deepcopy(base)
            dependency_cycle["edges"].extend([
                {"type": "depends_on", "source": "work-item", "target": "work-item-two"},
                {"type": "depends_on", "source": "work-item-two", "target": "work-item"},
            ])
            errors = validate(dependency_cycle, root, "pilot")
            matches = [error for error in errors if error["code"] == "EM001_DEPENDENCY_CYCLE"]
            self.assertEqual([(error["path"], error["ids"]) for error in matches],
                             [("$.edges", ["work-item", "work-item-two", "work-item"])], errors)

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
