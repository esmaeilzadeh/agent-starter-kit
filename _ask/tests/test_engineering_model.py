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
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask/verification"))
from engineering_model.validation import validate
from engineering_model.__main__ import main
from engineering_fixture import decision_model, referenced_model, write_json, model_command
from traceability.contracts import digest
from concurrent.futures import ThreadPoolExecutor
from engineering_model.domain import apply_batch


class ModelEditTests(unittest.TestCase):
    def test_invalid_and_stale_edits_preserve_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, _spec = referenced_model(root)
            receipt = json.loads(model_command(root, "admit", "--work-id", "pilot").stdout)
            identity = receipt["snapshot"]["digest"]
            path = root / "work/pilot/engineering-model.json"
            before = path.read_bytes()
            resolved_node = {"id": "raw-choice", "type": "decision", "title": "Raw resolution", "lifecycle": "resolved",
                             "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                             "resolution": {"option_id": "a", "actor": "Developer", "rationale": "Bypass",
                                            "timestamp": "2026-10-08T12:00:00Z"}, "history": []}
            invalid = [
                {"op": "add_node", "node": resolved_node},
                {"op": "revise_node", "id": "choice", "changes": {"id": "rename"}},
                {"op": "revise_node", "id": "choice", "changes": {"type": "task"}},
                {"op": "resolve_decision", "id": "choice", "option_id": "missing", "actor": "Developer", "rationale": "Reason"},
                {"op": "resolve_decision", "id": "choice", "option_id": "one", "actor": " ", "rationale": "Reason"},
            ]
            for command in invalid:
                batch = write_json(root, "proposal.json", {"commands": [command]})
                refused = model_command(root, "edit", "--work-id", "pilot", "--expected", identity, "--batch", str(batch))
                self.assertEqual(refused.returncode, 1, f"accepted invalid command: {command}")
                self.assertTrue(json.loads(refused.stdout)["diagnostics"])
                self.assertEqual(path.read_bytes(), before)
            (root / "specs/current/pilot.md").write_text("# Concurrent amendment\n", encoding="utf-8")
            batch = write_json(root, "proposal.json", {"commands": [{"op": "resolve_decision", "id": "choice",
                                "option_id": "one", "actor": "Developer", "rationale": "Reason"}]})
            refused = model_command(root, "edit", "--work-id", "pilot", "--expected", identity, "--batch", str(batch))
            self.assertEqual(refused.returncode, 1, refused.stderr)
            self.assertIn("EM007_STALE_INPUT", {e["code"] for e in json.loads(refused.stdout)["diagnostics"]})
            self.assertEqual(path.read_bytes(), before)

    def test_concurrent_compare_and_swap(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            referenced_model(root)
            receipt = json.loads(model_command(root, "admit", "--work-id", "pilot").stdout)
            identity = receipt["snapshot"]["digest"]
            paths = [write_json(root, f"proposal-{option}.json", {"commands": [{"op": "resolve_decision", "id": "choice",
                       "option_id": option, "actor": "Developer", "rationale": "Competing proposal"}]}) for option in ("one", "two")]
            with ThreadPoolExecutor(max_workers=2) as pool:
                attempts = list(pool.map(lambda p: model_command(root, "edit", "--work-id", "pilot", "--expected", identity,
                                                                  "--batch", str(p)), paths))
            self.assertEqual(sorted(p.returncode for p in attempts), [0, 1])
            loser = next(json.loads(p.stdout) for p in attempts if p.returncode)
            self.assertIn("EM007_STALE_INPUT", {e["code"] for e in loser["diagnostics"]})
            shown = json.loads(model_command(root, "show", "--work-id", "pilot").stdout)
            self.assertEqual(shown["model"]["revision"], 2)
            self.assertEqual(next(n for n in shown["model"]["nodes"] if n["id"] == "choice")["lifecycle"], "resolved")

    def test_revise_invalidates_transitive_decisions(self):
        model = decision_model()
        model = apply_batch(model, [{"op": "resolve_decision", "id": "choice", "option_id": "one",
                                     "actor": "Developer", "rationale": "Initial choice"}])["model"]
        model["nodes"].extend([
            {"id": "feature", "type": "feature", "title": "Feature", "lifecycle": "active"},
            {"id": "assumption", "type": "assumption", "title": "Assumption", "lifecycle": "confirmed"},
            {"id": "build", "type": "task", "title": "Build", "lifecycle": "planned"},
        ])
        for identity in ("second", "third"):
            node = copy.deepcopy(model["nodes"][1])
            node["id"], node["title"] = identity, identity
            model["nodes"].append(node)
        model["edges"].extend([
            {"type": "contains", "source": "purpose", "target": "feature"},
            {"type": "contains", "source": "purpose", "target": "build"},
            {"type": "depends_on", "source": "second", "target": "feature"},
            {"type": "depends_on", "source": "second", "target": "choice"},
            {"type": "depends_on", "source": "third", "target": "second"},
            {"type": "depends_on", "source": "build", "target": "third"},
        ])
        commands = [
            {"op": "revise_node", "id": "feature", "changes": {"title": "Changed feature"}},
            {"op": "reopen_decision", "id": "choice", "actor": "Developer", "rationale": "Changed inputs"},
            {"op": "add_edge", "edge": {"type": "depends_on", "source": "second", "target": "assumption"}},
        ]
        for command in commands:
            changed = apply_batch(model, [command], timestamp="2026-10-08T12:00:00Z")
            self.assertTrue(changed["valid"], changed)
            nodes = {n["id"]: n for n in changed["model"]["nodes"]}
            for identity in ("second", "third"):
                self.assertEqual(nodes[identity]["lifecycle"], "open", f"{command}: {identity}")
                self.assertNotIn("resolution", nodes[identity])
                self.assertTrue(any(h["event"] == "invalidated" and h["resolution"]["option_id"] == "one"
                                    for h in nodes[identity]["history"]))
            self.assertEqual(next(t for t in changed["tasks"] if t["id"] == "build")["status"], "blocked")
        model["edges"].append({"type": "depends_on", "source": "second", "target": "assumption"})
        removed = apply_batch(model, [{"op": "remove_edge", "edge": {"type": "depends_on", "source": "second", "target": "assumption"}}])
        self.assertTrue(removed["valid"], removed)
        self.assertEqual({n["id"]: n["lifecycle"] for n in removed["model"]["nodes"]}["third"], "open")

    def test_decision_history_and_dependency_propagation(self):
        model = decision_model()
        model["nodes"].extend([
            {"id": "build", "type": "task", "title": "Build", "lifecycle": "planned"},
            {"id": "assumption", "type": "assumption", "title": "Assumption", "lifecycle": "unverified"},
        ])
        model["edges"].extend([
            {"type": "contains", "source": "purpose", "target": "build"},
            {"type": "contains", "source": "purpose", "target": "assumption"},
            {"type": "depends_on", "source": "build", "target": "choice"},
            {"type": "depends_on", "source": "build", "target": "assumption"},
        ])
        original = copy.deepcopy(model)
        resolved = apply_batch(model, [{"op": "resolve_decision", "id": "choice", "option_id": "two",
                                        "actor": "Developer", "rationale": "Measured fit"}],
                               timestamp="2026-10-08T12:00:00Z")
        self.assertTrue(resolved["valid"], resolved)
        self.assertEqual(model, original)
        choice = next(n for n in resolved["model"]["nodes"] if n["id"] == "choice")
        self.assertEqual(choice["lifecycle"], "resolved")
        self.assertEqual(choice["resolution"], {"option_id": "two", "actor": "Developer",
                                              "rationale": "Measured fit", "timestamp": "2026-10-08T12:00:00Z"})
        self.assertEqual(resolved["model"]["revision"], 2)
        build = next(task for task in resolved["tasks"] if task["id"] == "build")
        self.assertEqual([blocker["id"] for blocker in build["blockers"]], ["assumption"])
        confirmed = apply_batch(resolved["model"], [{"op": "revise_node", "id": "assumption",
                                                   "changes": {"lifecycle": "confirmed"}}])
        self.assertTrue(confirmed["valid"], confirmed)
        self.assertEqual(next(task for task in confirmed["tasks"] if task["id"] == "build")["status"], "ready")
        for state in ("rejected", "retired"):
            blocked = apply_batch(confirmed["model"], [{"op": "revise_node", "id": "assumption",
                                                       "changes": {"lifecycle": state}}])
            self.assertTrue(blocked["valid"], blocked)
            self.assertEqual(next(task for task in blocked["tasks"] if task["id"] == "build")["status"], "blocked")
        reopened = apply_batch(resolved["model"], [{"op": "reopen_decision", "id": "choice",
                                                   "actor": "Developer", "rationale": "New measurements"}],
                               timestamp="2026-10-08T12:01:00Z")
        self.assertTrue(reopened["valid"], reopened)
        choice = next(n for n in reopened["model"]["nodes"] if n["id"] == "choice")
        self.assertEqual(choice["lifecycle"], "open")
        self.assertNotIn("resolution", choice)
        self.assertTrue(any(h.get("resolution", {}).get("option_id") == "two" for h in choice["history"]))
        changed = apply_batch(reopened["model"], [{"op": "revise_node", "id": "choice",
                                                  "changes": {"options": [{"id": "one", "label": "First revised"},
                                                                          {"id": "two", "label": "Second revised"}]}}])
        self.assertTrue(changed["valid"], changed)
        self.assertTrue(any(h.get("options", [{}])[0].get("label") == "First"
                            for h in next(n for n in changed["model"]["nodes"] if n["id"] == "choice")["history"]))
        retired = apply_batch(resolved["model"], [{"op": "retire_decision", "id": "choice",
                                                  "actor": "Developer", "rationale": "Superseded"}])
        self.assertTrue(retired["valid"], retired)
        self.assertIn("choice", [b["id"] for b in next(t for t in retired["tasks"] if t["id"] == "build")["blockers"]])
        for state in ("planned", "active", "retired", "done"):
            dependent = decision_model()
            dependent["nodes"].extend([
                {"id": "upstream", "type": "task", "title": "Upstream", "lifecycle": state},
                {"id": "downstream", "type": "task", "title": "Downstream", "lifecycle": "planned"}])
            dependent["edges"].append({"type": "depends_on", "source": "downstream", "target": "upstream"})
            result = apply_batch(dependent, [{"op": "revise_node", "id": "downstream", "changes": {"title": "Updated"}}])
            self.assertTrue(result["valid"], result)
            expected = "ready" if state == "done" else "blocked"
            self.assertEqual(next(t for t in result["tasks"] if t["id"] == "downstream")["status"], expected)


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

            # An illegal incoming edge cannot satisfy the required legal parent.
            illegal_parent = copy.deepcopy(no_parent)
            illegal_parent["edges"].append({"type": "contains", "source": "choice", "target": "work-item"})
            errors = validate(illegal_parent, root, "pilot")
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


class ProjectionTests(unittest.TestCase):
    def test_json_markdown_same_ids_and_no_outcomes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, _spec = referenced_model(root)
            model["nodes"].extend([
                {"id": "scenario", "type": "scenario", "title": "Canonical flow", "lifecycle": "active",
                 "reference": {"path": "specs/current/pilot.json", "id": "P-001"}},
                {"id": "case", "type": "test", "title": "Canonical assertion", "lifecycle": "active",
                 "reference": {"path": "work/pilot/test-plan.json", "id": "CASE-1"}},
            ])
            model["edges"].extend([
                {"type": "contains", "source": "requirement", "target": "scenario"},
                {"type": "covers", "source": "case", "target": "scenario"},
            ])
            write_json(root, "work/pilot/engineering-model.json", model)
            write_json(root, "work/pilot/test-plan.json", {
                "schema": "ask-test-plan/v1", "work_id": "pilot",
                "spec_digest": digest(_spec),
                "obligations": [{"criterion_id": "P-001", "required_types": ["unit"]}],
                "runners": [{"id": "fixture-runner", "adapter": "unittest",
                             "argv": ["python3", "-m", "unittest", "test_engineering_model.ProjectionTests.test_json_markdown_same_ids_and_no_outcomes"]}],
                "tests": [{"id": "CASE-1", "criterion_ids": ["P-001"], "type": "unit",
                           "change_kind": "new", "scenario": {"given": "Input", "when": "Run", "then": ["Visible"]},
                           "expected_assertions": [{"criterion_id": "P-001", "checks": ["Visible"]}],
                           "runner_id": "fixture-runner", "case_id": "fixture.Case.test_it",
                           "source_paths": ["_ask/tests/test_engineering_model.py"]}],
                "task_scopes": [],
            })
            admitted = json.loads(model_command(root, "admit", "--work-id", "pilot").stdout)
            self.assertTrue(admitted["valid"], admitted)
            machine = model_command(root, "show", "--work-id", "pilot", "--format", "json")
            self.assertEqual(machine.returncode, 0, machine.stderr)
            data = json.loads(machine.stdout)
            self.assertEqual(data["snapshot"]["digest"], admitted["snapshot"]["digest"])
            expected_ids = {node["id"] for node in model["nodes"]}
            self.assertEqual({node["id"] for node in data["model"]["nodes"]}, expected_ids)
            markdown = model_command(root, "show", "--work-id", "pilot", "--format", "markdown")
            self.assertEqual(markdown.returncode, 0, markdown.stderr)
            self.assertTrue(all(f"`{identity}`" in markdown.stdout for identity in sorted(expected_ids)))
            self.assertIn(admitted["snapshot"]["digest"], markdown.stdout)
            self.assertNotIn("current_completion", data)
            self.assertNotIn("current_completion", markdown.stdout)
