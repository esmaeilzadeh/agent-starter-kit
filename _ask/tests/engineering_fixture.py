"""Isolated Engineering Model fixtures; never modify a checked-in pilot."""
import json
import os
from pathlib import Path
import subprocess
import sys


def model_command(root, *arguments):
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "scripts")
    return subprocess.run([sys.executable, "-m", "engineering_model", *arguments],
                          cwd=root, env=environment, capture_output=True, text=True)


def write_json(root, relative, value):
    path = Path(root) / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def referenced_model(root):
    model = decision_model()
    model["nodes"].append({"id": "requirement", "type": "requirement", "title": "Requirement",
                           "lifecycle": "active", "reference": {"path": "specs/current/pilot.json", "id": "P-001"}})
    model["edges"].append({"type": "contains", "source": "purpose", "target": "requirement"})
    spec = {"schema": "ask-spec/v1", "work_id": "pilot", "revision": 1,
            "criteria": [{"id": "P-001", "given": "Valid input", "when": "Validate", "then": ["Accept"],
                          "verification_mode": "tests"}]}
    write_json(root, "specs/current/pilot.json", spec)
    (Path(root) / "specs/current/pilot.md").write_text("# Pilot specification\n", encoding="utf-8")
    write_json(root, "work/pilot/engineering-model.json", model)
    return model, spec


def decision_model():
    return {
        "schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
        "nodes": [
            {"id": "purpose", "type": "intent", "title": "Purpose", "lifecycle": "active"},
            {"id": "choice", "type": "decision", "title": "Choose", "lifecycle": "open",
             "options": [{"id": "one", "label": "First"}, {"id": "two", "label": "Second"}],
             "history": []},
        ],
        "edges": [{"type": "contains", "source": "purpose", "target": "choice"}],
    }


def workbench_model(root):
    """Valid canonical behavior and an open decision blocking planned work."""
    import hashlib
    model, spec = referenced_model(root)
    model["nodes"].extend([
        {"id": "build", "type": "task", "title": "Build", "lifecycle": "planned"},
        {"id": "scenario", "type": "scenario", "title": "Canonical behavior", "lifecycle": "active",
         "reference": {"path": "specs/current/pilot.json", "id": "P-001"}},
        {"id": "case", "type": "test", "title": "Behavior assertion", "lifecycle": "active",
         "reference": {"path": "work/pilot/test-plan.json", "id": "CASE-1"}},
    ])
    model["edges"].extend([
        {"type": "contains", "source": "purpose", "target": "build"},
        {"type": "depends_on", "source": "build", "target": "choice"},
        {"type": "contains", "source": "requirement", "target": "scenario"},
        {"type": "covers", "source": "case", "target": "scenario"},
    ])
    plan = {"schema": "ask-test-plan/v1", "work_id": "pilot",
        "spec_digest": hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "obligations": [{"criterion_id": "P-001", "required_types": ["unit"]}],
        "runners": [{"id": "fixture", "adapter": "unittest", "argv": ["python3", "-m", "unittest", "test_fixture"]}],
        "task_scopes": [], "tests": [{"id": "CASE-1", "criterion_ids": ["P-001"], "type": "unit",
            "change_kind": "new", "runner_id": "fixture", "case_id": "test_fixture.Cases.test_behavior",
            "source_paths": ["test_fixture.py"],
            "scenario": {"given": "Valid input", "when": "Validate", "then": ["Accept"]},
            "expected_assertions": [{"criterion_id": "P-001", "checks": ["Exact accepted behavior"]}]}]}
    write_json(root, "work/pilot/engineering-model.json", model)
    write_json(root, "work/pilot/test-plan.json", plan)
    return model, spec
