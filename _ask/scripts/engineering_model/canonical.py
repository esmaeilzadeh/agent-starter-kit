"""Validate captured canonical definitions, reusing the traceability contract API."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / ".agents/ask/verification"))
from traceability.contracts import indexed, scenario
from traceability.coverage import validate_plan

from .snapshot import decode
from .validation import SLUG


def diagnostics(snapshot):
    errors = []
    documents = {}
    required_specs = set()
    model = snapshot.document
    if isinstance(model, dict) and isinstance(model.get("nodes"), list):
        for node in model["nodes"]:
            if not isinstance(node, dict) or node.get("type") not in ("requirement", "scenario"):
                continue
            reference = node.get("reference")
            if isinstance(reference, dict) and isinstance(reference.get("path"), str):
                required_specs.add(reference["path"])
    for path, raw in snapshot.files.items():
        if path.endswith("/test-plan.json") and raw is not None:
            try:
                plan = decode(raw)
            except (UnicodeError, ValueError):
                continue
            if isinstance(plan, dict) and isinstance(plan.get("work_id"), str):
                required_specs.add(f"specs/current/{plan['work_id']}.json")

    def error(path, message):
        errors.append({"code": "EM001_CANONICAL_DEFINITION", "path": path, "message": message})

    def require(path, target):
        if snapshot.statuses.get(target) != "present":
            error(path, f"linked definition is unavailable or unsafe: {target}")

    for path, raw in sorted(snapshot.files.items()):
        parts = Path(path).parts
        is_spec = (len(parts) == 3 and parts[:2] == ("specs", "current")
                   and path.endswith(".json") and SLUG.fullmatch(parts[-1][:-5]))
        is_plan = (len(parts) == 3 and parts[0] == "work" and parts[-1] == "test-plan.json"
                   and SLUG.fullmatch(parts[1]))
        if not is_spec and not is_plan:
            continue
        try:
            value = decode(raw) if raw is not None else None
        except (UnicodeError, ValueError):
            value = None
        if not isinstance(value, dict):
            error(path, "canonical definition must be an available JSON object")
            continue
        documents[path] = value
        if is_spec and path not in required_specs and value.get("schema") == "ask-feature-spec/v1":
            linked = value.get("extends")
            if isinstance(linked, str):
                require(path, linked)
            continue
        expected_schema = "ask-spec/v1" if is_spec else "ask-test-plan/v1"
        expected_id = parts[-1][:-5] if is_spec else parts[1]
        if value.get("schema") != expected_schema or value.get("work_id") != expected_id:
            error(path, f"expected {expected_schema} for workstream {expected_id}")
        if is_spec:
            if type(value.get("revision")) is not int or value["revision"] < 1:
                error(path, "spec revision must be a positive integer")
            violations = []
            criteria = indexed(value.get("criteria"), "criteria", violations)
            if not criteria or violations or any(not scenario(item) for item in criteria.values()):
                error(path, "criterion registry has duplicate/missing identities or malformed scenarios")
            require(path, str(Path(path).with_suffix(".md")))
            feature = value.get("feature_specification")
            if feature is not None:
                if not isinstance(feature, str):
                    error(path, "feature_specification must be a repository-relative path")
                else:
                    require(path, feature)

    for path, plan in sorted(documents.items()):
        if plan.get("schema") != "ask-test-plan/v1":
            continue
        spec_path = f"specs/current/{plan.get('work_id')}.json"
        spec = documents.get(spec_path)
        if spec is None:
            error(path, f"canonical spec is unavailable: {spec_path}")
            continue
        graph = None
        if plan.get("task_scopes"):
            import yaml
            graph_path = f"work/{plan['work_id']}/inner-loop/tasks.yaml"
            if snapshot.files.get(graph_path) is None:
                error(path, "accepted task graph is unavailable or invalid")
                continue
            try:
                graph = yaml.safe_load(snapshot.files.get(graph_path))
            except yaml.YAMLError:
                graph = None
            if not isinstance(graph, dict):
                error(path, "accepted task graph is unavailable or invalid")
                continue
        for violation in validate_plan(spec, plan, graph):
            error(path, f"{violation.code}: {violation.field or violation.test_id or violation.criterion_id or ''}")
    return errors
