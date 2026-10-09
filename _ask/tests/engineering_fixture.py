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
    source = Path(root) / "test_fixture.py"
    source.write_text(
        "class Cases:\n"
        "    def test_behavior(self):\n"
        "        actual = validate_input('valid')\n"
        "        self.assertEqual(actual, 'accepted')\n",
        encoding="utf-8",
    )
    return model, spec


def evidence_workbench():
    """Real retained successful evidence, followed by a newer adopted checkout."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
    from traceability_fixture import Consumer
    consumer = Consumer()
    try:
        verified = consumer.command("verify")
        if verified.returncode:
            raise RuntimeError("evidence fixture verification failed: " + verified.stdout + verified.stderr)
        historical = consumer.sha
        model = decision_model()
        model["work_id"] = "w"
        model["nodes"].extend([
            {"id": "build", "type": "task", "title": "Build", "lifecycle": "planned"},
            {"id": "review-build", "type": "task", "title": "Review build", "lifecycle": "planned"},
            {"id": "requirement", "type": "requirement", "title": "Uppercase requirement", "lifecycle": "active",
             "reference": {"path": "specs/current/w.json", "id": "C1"}},
            {"id": "scenario", "type": "scenario", "title": "Uppercase behavior", "lifecycle": "active",
             "reference": {"path": "specs/current/w.json", "id": "C1"}},
            {"id": "scenario-other", "type": "scenario", "title": "Second canonical behavior", "lifecycle": "active",
             "reference": {"path": "specs/current/other.json", "id": "O1"}},
            {"id": "requirement-other", "type": "requirement", "title": "Second requirement", "lifecycle": "active",
             "reference": {"path": "specs/current/other.json", "id": "O1"}},
            {"id": "case", "type": "test", "title": "Uppercase assertion", "lifecycle": "active",
             "reference": {"path": "work/w/test-plan.json", "id": "U"}},
        ])
        model["edges"].extend([
            {"type": "contains", "source": "purpose", "target": "build"},
            {"type": "contains", "source": "purpose", "target": "review-build"},
            {"type": "depends_on", "source": "build", "target": "choice"},
            {"type": "contains", "source": "purpose", "target": "requirement"},
            {"type": "contains", "source": "purpose", "target": "requirement-other"},
            {"type": "contains", "source": "requirement", "target": "scenario"},
            {"type": "contains", "source": "requirement-other", "target": "scenario-other"},
            {"type": "covers", "source": "case", "target": "scenario"},
        ])
        consumer.write("specs/current/w.md", "# Uppercase specification\n")
        consumer.write("specs/current/other.json", json.dumps({"schema": "ask-spec/v1", "work_id": "other",
            "revision": 1, "criteria": [{"id": "O1", "given": "Given another input",
            "when": "When inspected", "then": ["Show the second behavior"],
            "verification_mode": "tests"}]}))
        consumer.write("specs/current/other.md", "# Second specification\n")
        consumer.write("work/w/engineering-model.json", model)
        consumer.commit("adopt workbench without claiming completion for the new revision")
        return consumer, historical
    except BaseException:
        consumer.close()
        raise
