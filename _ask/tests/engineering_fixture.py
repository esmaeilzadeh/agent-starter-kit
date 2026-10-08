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
