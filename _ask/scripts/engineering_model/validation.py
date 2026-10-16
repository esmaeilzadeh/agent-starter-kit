"""Pure validation for ask-engineering-model/v1 documents.

This module deliberately has no UI, persistence, or mutation responsibilities.
The returned diagnostics are stable data so CLI and later consumers can share
one validator implementation.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path, PureWindowsPath


SCHEMA = "ask-engineering-model/v1"
SCHEMA_V2 = "ask-engineering-model/v2"
RULES_VERSION = "ask-engineering-validator-rules/v6"
NODE_TYPES = {
    "intent", "requirement", "feature", "story", "scenario", "decision",
    "assumption", "task", "implementation", "test", "test_run", "risk",
    "evidence",
}
LIFECYCLES = {
    "intent": {"draft", "active", "retired"},
    "requirement": {"draft", "active", "retired"},
    "feature": {"draft", "active", "retired"},
    "story": {"draft", "active", "retired"},
    "scenario": {"draft", "active", "retired"},
    "decision": {"open", "resolved", "retired"},
    "assumption": {"unverified", "confirmed", "rejected", "retired"},
    "task": {"planned", "active", "done", "retired"},
    "implementation": {"draft", "active", "retired"},
    "test": {"draft", "active", "retired"},
    "test_run": {"draft", "active", "retired"},
    "risk": {"open", "mitigated", "retired"},
    "evidence": {"draft", "active", "retired"},
}
CONTAINS = {
    "intent": {"feature", "requirement", "task", "decision", "assumption", "risk"},
    "feature": {"story", "requirement", "scenario", "task", "decision"},
    "story": {"scenario", "task", "decision"},
    "requirement": {"scenario"},
}
REQUIRED_PARENT = {"feature", "requirement", "story", "scenario", "task"}
DEPENDENCIES = {
    "task": {"task", "decision", "assumption"},
    "decision": {"decision", "feature", "requirement", "scenario", "assumption"},
}
EDGE_TYPES = {"contains", "depends_on", "covers", "implements", "executes", "supports"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _diagnostic(code: str, path: str, message: str, *ids: str) -> dict:
    item = {"code": code, "path": path, "message": message}
    if ids:
        item["ids"] = list(ids)
    return item


def _acyclic(edges: list[tuple[str, str]], ids: set[str]) -> list[list[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        adjacency[source].append(target)
    for targets in adjacency.values():
        targets.sort()
    colour: dict[str, int] = {}
    cycles: list[list[str]] = []
    for start in sorted(ids):
        if colour.get(start, 0):
            continue
        stack: list[tuple[str, int]] = [(start, 0)]
        active: list[str] = [start]
        active_index = {start: 0}
        colour[start] = 1
        while stack:
            node, offset = stack[-1]
            neighbours = adjacency[node]
            if offset >= len(neighbours):
                stack.pop()
                active_index.pop(node, None)
                active.pop()
                colour[node] = 2
                continue
            target = neighbours[offset]
            stack[-1] = (node, offset + 1)
            if colour.get(target, 0) == 1:
                cycles.append(active[active_index[target]:] + [target])
            elif colour.get(target, 0) == 0:
                colour[target] = 1
                active_index[target] = len(active)
                active.append(target)
                stack.append((target, 0))
    return cycles


def validate(document: object, root: str | Path, work_id: str, *, reference_bytes=None) -> list[dict]:
    """Dispatch the exact model version while retaining the original v1 rules."""
    if isinstance(document, dict) and document.get("schema") == SCHEMA_V2:
        return _validate_v2(document, root, work_id, reference_bytes=reference_bytes)
    return _validate_v1(document, root, work_id, reference_bytes=reference_bytes)


def _validate_v1(document: object, root: str | Path, work_id: str, *, reference_bytes=None) -> list[dict]:
    """Return deterministic diagnostics; never modify the document or files."""
    errors: list[dict] = []
    if not isinstance(document, dict):
        return [_diagnostic("EM001_SCHEMA", "$", "model must be a JSON object")]

    allowed_top = {"schema", "work_id", "revision", "nodes", "edges"}
    for key in sorted(set(document) - allowed_top):
        errors.append(_diagnostic("EM001_FIELD", f"$.{key}", "unexpected model field"))
    if document.get("schema") != SCHEMA:
        errors.append(_diagnostic("EM001_SCHEMA", "$.schema", f"expected {SCHEMA}"))
    if document.get("work_id") != work_id:
        errors.append(_diagnostic("EM001_WORK_ID", "$.work_id", "work_id does not match selected workstream"))
    revision = document.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append(_diagnostic("EM001_REVISION", "$.revision", "revision must be a positive integer"))

    nodes = document.get("nodes")
    edges = document.get("edges")
    if not isinstance(nodes, list):
        errors.append(_diagnostic("EM001_SCHEMA", "$.nodes", "nodes must be an array"))
        nodes = []
    if not isinstance(edges, list):
        errors.append(_diagnostic("EM001_SCHEMA", "$.edges", "edges must be an array"))
        edges = []

    by_id: dict[str, dict] = {}
    id_paths: dict[str, str] = {}
    for index, node in enumerate(nodes):
        path = f"$.nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(_diagnostic("EM001_NODE", path, "node must be an object"))
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not SLUG.fullmatch(node_id):
            errors.append(_diagnostic("EM001_ID", f"{path}.id", "id must be a lowercase hyphenated slug"))
            continue
        if node_id in by_id:
            errors.append(_diagnostic("EM001_DUPLICATE_ID", f"{path}.id", "duplicate node id", node_id))
            continue
        by_id[node_id] = node
        id_paths[node_id] = path
        node_type = node.get("type")
        if not isinstance(node_type, str) or node_type not in NODE_TYPES:
            errors.append(_diagnostic("EM001_NODE_TYPE", f"{path}.type", "unknown node type", node_id))
            continue
        allowed = {"id", "type", "title", "lifecycle", "description"}
        if node_type in {"requirement", "scenario", "test", "test_run", "evidence", "implementation"}:
            allowed.add("reference")
        if node_type == "decision":
            allowed |= {"options", "resolution", "history"}
        for key in sorted(set(node) - allowed):
            errors.append(_diagnostic("EM001_FIELD", f"{path}.{key}", "unexpected node field", node_id))
        title = node.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(_diagnostic("EM001_TITLE", f"{path}.title", "title must be nonempty", node_id))
        description = node.get("description")
        if description is not None and not isinstance(description, str):
            errors.append(_diagnostic("EM001_DESCRIPTION", f"{path}.description", "description must be text", node_id))
        lifecycle = node.get("lifecycle")
        if not isinstance(lifecycle, str) or lifecycle not in LIFECYCLES[node_type]:
            errors.append(_diagnostic("EM001_LIFECYCLE", f"{path}.lifecycle", "invalid lifecycle for node type", node_id))
        if node_type == "decision":
            self_errors = _decision_diagnostics(node, path, node_id)
            errors.extend(self_errors)
        if node_type == "implementation":
            _validate_reference(node, path, node_id, "implementation", root, work_id, errors, reference_bytes)
        elif node_type in {"requirement", "scenario", "test", "test_run", "evidence"}:
            _validate_reference(node, path, node_id, node_type, root, work_id, errors, reference_bytes)

    intent_ids = [node_id for node_id, node in by_id.items() if node.get("type") == "intent"]
    if len(intent_ids) != 1:
        errors.append(_diagnostic("EM001_INTENT_COUNT", "$.nodes", "model must contain exactly one intent", *intent_ids))

    seen_edges: set[tuple[str, str, str]] = set()
    parent_edges: dict[str, list[str]] = defaultdict(list)
    containment: list[tuple[str, str]] = []
    dependencies: list[tuple[str, str]] = []
    for index, edge in enumerate(edges):
        path = f"$.edges[{index}]"
        if not isinstance(edge, dict) or set(edge) != {"type", "source", "target"}:
            errors.append(_diagnostic("EM001_EDGE", path, "edge must contain exactly type, source, and target"))
            continue
        kind, source, target = edge["type"], edge["source"], edge["target"]
        if not all(isinstance(value, str) for value in (kind, source, target)):
            errors.append(_diagnostic("EM001_EDGE", path, "edge fields must be strings"))
            continue
        identity = (kind, source, target)
        if identity in seen_edges:
            errors.append(_diagnostic("EM001_DUPLICATE_EDGE", path, "duplicate edge", source, target))
            continue
        seen_edges.add(identity)
        source_node, target_node = by_id.get(source), by_id.get(target)
        if source_node is None or target_node is None:
            errors.append(_diagnostic("EM001_DANGLING_EDGE", path, "edge refers to a missing node", source, target))
            continue
        source_type, target_type = source_node.get("type"), target_node.get("type")
        valid = kind in EDGE_TYPES
        if kind == "contains":
            valid = isinstance(source_type, str) and isinstance(target_type, str) and target_type in CONTAINS.get(source_type, set())
            if valid:
                parent_edges[target].append(source)
            containment.append((source, target))
        elif kind == "depends_on":
            valid = isinstance(source_type, str) and isinstance(target_type, str) and target_type in DEPENDENCIES.get(source_type, set())
            dependencies.append((source, target))
        elif kind == "covers":
            valid = source_type == "test" and target_type == "scenario"
        elif kind == "implements":
            valid = source_type == "implementation" and isinstance(target_type, str) and target_type in {"scenario", "task"}
        elif kind == "executes":
            valid = source_type == "test_run" and target_type == "test"
        elif kind == "supports":
            valid = source_type == "evidence" and isinstance(target_type, str) and target_type in {"test", "test_run"}
        if not valid:
            errors.append(_diagnostic("EM001_ILLEGAL_EDGE", path, "edge is not legal for its node types", source, target))

    covered_tests = {source for kind, source, _target in seen_edges if kind == "covers"}
    for node_id, node in sorted(by_id.items()):
        if node.get("type") == "test" and node_id not in covered_tests:
            errors.append(_diagnostic("EM001_TEST_COVERAGE", id_paths[node_id], "test must cover at least one scenario", node_id))

    for node_id, node in sorted(by_id.items()):
        node_type = node.get("type")
        if isinstance(node_type, str) and node_type in REQUIRED_PARENT and node.get("lifecycle") != "draft":
            parents = parent_edges.get(node_id, [])
            if len(parents) != 1:
                errors.append(_diagnostic("EM001_PARENT_COUNT", id_paths[node_id], "active definition requires exactly one containment parent", node_id))
    for cycle in _acyclic(containment, set(by_id)):
        errors.append(_diagnostic("EM001_CONTAINS_CYCLE", "$.edges", "containment cycle", *cycle))
    for cycle in _acyclic(dependencies, set(by_id)):
        errors.append(_diagnostic("EM001_DEPENDENCY_CYCLE", "$.edges", "dependency cycle", *cycle))
    errors.sort(key=lambda item: (item["path"], item["code"], item.get("ids", []), item["message"]))
    return errors


def _validate_v2(document: object, root: str | Path, work_id: str, *, reference_bytes=None) -> list[dict]:
    """Validate the v2 relationship graph and its qualified aliases."""
    from .identities import identity_diagnostics
    from .flows import flow_diagnostics

    errors: list[dict] = []
    if document.get("work_id") != work_id:
        errors.append(_diagnostic("EM001_WORK_ID", "$.work_id", "work_id does not match selected workstream"))
    if set(document) - {"schema", "work_id", "revision", "nodes", "edges", "subject_association"}:
        for key in sorted(set(document) - {"schema", "work_id", "revision", "nodes", "edges", "subject_association"}):
            errors.append(_diagnostic("EM001_FIELD", f"$.{key}", "unexpected model field"))
    revision = document.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append(_diagnostic("EM001_REVISION", "$.revision", "revision must be a positive integer"))
    nodes, edges = document.get("nodes"), document.get("edges")
    if not isinstance(nodes, list):
        errors.append(_diagnostic("EM001_SCHEMA", "$.nodes", "nodes must be an array")); nodes = []
    if not isinstance(edges, list):
        errors.append(_diagnostic("EM001_SCHEMA", "$.edges", "edges must be an array")); edges = []
    by_id: dict[str, dict] = {}
    id_paths: dict[str, str] = {}
    for index, node in enumerate(nodes):
        path = f"$.nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(_diagnostic("EM001_NODE", path, "node must be an object")); continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not SLUG.fullmatch(node_id):
            errors.append(_diagnostic("EM001_ID", f"{path}.id", "id must be a lowercase hyphenated slug")); continue
        if node_id in by_id:
            errors.append(_diagnostic("EM001_DUPLICATE_ID", f"{path}.id", "duplicate node id", node_id)); continue
        by_id[node_id], id_paths[node_id] = node, path
        node_type = node.get("type")
        if not isinstance(node_type, str) or node_type not in NODE_TYPES:
            errors.append(_diagnostic("EM001_NODE_TYPE", f"{path}.type", "unknown node type", node_id)); continue
        allowed = {"id", "type", "title", "lifecycle", "description", "context", "source_context"}
        if node_type in {"requirement", "scenario", "test", "test_run", "evidence", "implementation"}:
            allowed.add("reference")
        if node_type == "decision": allowed |= {"options", "resolution", "history"}
        if node_type == "task": allowed.add("execution")
        if node_type == "scenario": allowed.add("case")
        if node_type == "intent": allowed.add("definition")
        for key in sorted(set(node) - allowed):
            errors.append(_diagnostic("EM001_FIELD", f"{path}.{key}", "unexpected model field", node_id))
        if not isinstance(node.get("title"), str) or not node["title"].strip():
            errors.append(_diagnostic("EM001_TITLE", f"{path}.title", "title must be nonempty", node_id))
        if node.get("description") is not None and not isinstance(node["description"], str):
            errors.append(_diagnostic("EM001_DESCRIPTION", f"{path}.description", "description must be text", node_id))
        if not isinstance(node.get("lifecycle"), str) or node.get("lifecycle") not in LIFECYCLES[node_type]:
            errors.append(_diagnostic("EM001_LIFECYCLE", f"{path}.lifecycle", "invalid lifecycle for node type", node_id))
        if node_type == "decision": errors.extend(_decision_diagnostics(node, path, node_id))
        errors.extend(_v2_metadata_diagnostics(node, path, node_id))
        if node_type == "implementation":
            _validate_reference(node, path, node_id, node_type, root, work_id, errors, reference_bytes)
        elif node_type == "test" and isinstance(node.get("reference"), dict) and (
                "work_id" in node["reference"] or "plan_digest" in node["reference"]):
            reference = node["reference"]
            if (set(reference) != {"path", "id", "work_id", "plan_digest"}
                    or not isinstance(reference.get("work_id"), str)
                    or not isinstance(reference.get("plan_digest"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", reference["plan_digest"])):
                errors.append(_diagnostic("EM001_REFERENCE", f"{path}.reference", "qualified Test reference needs path, id, work_id, and plan_digest", node_id))
            normalized = dict(node)
            normalized["reference"] = {key: reference[key] for key in ("path", "id") if key in reference}
            _validate_reference(normalized, path, node_id, node_type, root, work_id, errors, reference_bytes)
        elif node_type in {"requirement", "scenario", "test", "test_run", "evidence"}:
            # In v2 a draft Scenario can omit its canonical case/reference.
            _validate_reference(node, path, node_id, node_type, root, work_id, errors, reference_bytes)

    intents = [identity for identity, node in by_id.items() if node.get("type") == "intent"]
    if len(intents) > 1:
        errors.append(_diagnostic("EM001_INTENT_COUNT", "$.nodes", "model may contain at most one intent", *intents))
    identity_errors = identity_diagnostics(by_id, id_paths)
    errors.extend(identity_errors)

    seen: set[tuple[str, str, str]] = set()
    parents: dict[str, list[str]] = defaultdict(list)
    containment: list[tuple[str, str]] = []
    dependencies: list[tuple[str, str]] = []
    for index, edge in enumerate(edges):
        path = f"$.edges[{index}]"
        if not isinstance(edge, dict) or set(edge) != {"type", "source", "target"}:
            errors.append(_diagnostic("EM001_EDGE", path, "edge must contain exactly type, source, and target")); continue
        kind, source, target = edge["type"], edge["source"], edge["target"]
        if not all(isinstance(v, str) for v in (kind, source, target)):
            errors.append(_diagnostic("EM001_EDGE", path, "edge fields must be strings")); continue
        identity = (kind, source, target)
        if identity in seen:
            errors.append(_diagnostic("EM001_DUPLICATE_EDGE", path, "duplicate edge", source, target)); continue
        seen.add(identity)
        left, right = by_id.get(source), by_id.get(target)
        if left is None or right is None:
            errors.append(_diagnostic("EM001_DANGLING_EDGE", path, "edge refers to a missing node", source, target)); continue
        lt, rt = left.get("type"), right.get("type")
        valid = False
        if kind == "contains":
            valid = isinstance(lt, str) and isinstance(rt, str) and rt in CONTAINS.get(lt, set())
            if valid: parents[target].append(source)
            containment.append((source, target))
        elif kind == "depends_on":
            valid = isinstance(lt, str) and isinstance(rt, str) and rt in DEPENDENCIES.get(lt, set()); dependencies.append((source, target))
        elif kind == "covers": valid = lt == "test" and rt == "scenario"
        elif kind == "implements": valid = lt == "implementation" and isinstance(rt, str) and rt in {"scenario", "task"}
        elif kind == "executes": valid = lt == "test_run" and rt == "test"
        elif kind == "supports": valid = lt == "evidence" and isinstance(rt, str) and rt in {"test", "test_run"}
        elif kind == "contributes_to": valid = lt == "task" and isinstance(rt, str) and rt in {"story", "scenario"}
        elif kind == "enables": valid = lt == "feature" and rt == "story"
        if not valid:
            errors.append(_diagnostic("EM001_ILLEGAL_EDGE", path, "edge is not legal for its node types", source, target))
    for node_id, node in sorted(by_id.items()):
        if isinstance(node.get("type"), str) and node.get("type") in {"feature", "requirement", "story", "scenario", "task"}:
            if len(parents[node_id]) > 1:
                errors.append(_diagnostic("EM001_MULTIPLE_PARENTS", id_paths[node_id], "definition may have at most one containment parent", node_id))
    for cycle in _acyclic(containment, set(by_id)):
        errors.append(_diagnostic("EM001_CONTAINS_CYCLE", "$.edges", "containment cycle", *cycle))
    for cycle in _acyclic(dependencies, set(by_id)):
        errors.append(_diagnostic("EM001_DEPENDENCY_CYCLE", "$.edges", "dependency cycle", *cycle))
    errors.extend(flow_diagnostics(document, by_id, seen, root, work_id, reference_bytes))
    errors.sort(key=lambda item: (item["path"], item["code"], item.get("ids", []), item["message"]))
    return errors


def _v2_metadata_diagnostics(node, path, node_id):
    errors = []
    context = node.get("context", [])
    if not isinstance(context, list):
        errors.append(_diagnostic("EM001_CONTEXT", f"{path}.context", "context must be an array", node_id))
    else:
        for index, item in enumerate(context):
            valid = (isinstance(item, dict) and set(item) == {"role", "path", "revision", "selector"}
                     and isinstance(item.get("role"), str) and item.get("role") in {"spec", "plan"}
                     and isinstance(item.get("path"), str) and bool(item["path"])
                     and isinstance(item.get("revision"), str) and bool(item["revision"])
                     and isinstance(item.get("selector"), dict))
            if not valid:
                errors.append(_diagnostic("EM001_CONTEXT", f"{path}.context[{index}]", "context entry has an invalid basic shape", node_id))
    sources = node.get("source_context", [])
    if not isinstance(sources, list):
        errors.append(_diagnostic("EM001_SOURCE_CONTEXT", f"{path}.source_context", "source_context must be an array", node_id))
    else:
        fields = {"path", "revision", "qualified_name", "role", "explanation"}
        for index, item in enumerate(sources):
            if (not isinstance(item, dict) or set(item) != fields
                    or any(not isinstance(item.get(key), str) or not item[key].strip() for key in fields)):
                errors.append(_diagnostic("EM001_SOURCE_CONTEXT", f"{path}.source_context[{index}]", "source context entry has an invalid basic shape", node_id))
    if node.get("type") == "intent" and "definition" in node:
        definition = node["definition"]
        fields = {"user", "purpose", "outcome", "scope", "completion_conditions"}
        scalar_fields = fields - {"completion_conditions"}
        if (not isinstance(definition, dict) or set(definition) != fields
                or any(not isinstance(definition.get(key), str) or not definition[key].strip() for key in scalar_fields)
                or not isinstance(definition.get("completion_conditions"), list)
                or not definition["completion_conditions"]
                or any(not isinstance(value, str) or not value.strip()
                       for value in definition["completion_conditions"])):
            errors.append(_diagnostic("EM001_DEFINITION", f"{path}.definition", "intent definition needs user, purpose, outcome, scope, and completion conditions", node_id))
    return errors


def _decision_diagnostics(node: dict, path: str, node_id: str) -> list[dict]:
    errors: list[dict] = []
    options = node.get("options")
    if not isinstance(options, list) or len(options) < 2:
        errors.append(_diagnostic("EM001_DECISION_OPTIONS", f"{path}.options", "decision needs at least two options", node_id))
        option_ids: set[str] = set()
    else:
        option_ids = set()
        labels: set[str] = set()
        for index, option in enumerate(options):
            if not isinstance(option, dict) or set(option) != {"id", "label"}:
                errors.append(_diagnostic("EM001_DECISION_OPTION", f"{path}.options[{index}]", "option needs id and label", node_id))
                continue
            option_id, label = option.get("id"), option.get("label")
            if not isinstance(option_id, str) or not option_id or option_id in option_ids:
                errors.append(_diagnostic("EM001_DECISION_OPTION", f"{path}.options[{index}].id", "option id must be unique and nonempty", node_id))
            else:
                option_ids.add(option_id)
            if not isinstance(label, str) or not label.strip() or label in labels:
                errors.append(_diagnostic("EM001_DECISION_OPTION", f"{path}.options[{index}].label", "option label must be unique and nonempty", node_id))
            else:
                labels.add(label)
    lifecycle = node.get("lifecycle")
    resolution = node.get("resolution")
    if lifecycle == "resolved":
        if not isinstance(resolution, dict) or set(resolution) != {"option_id", "actor", "rationale", "timestamp"}:
            errors.append(_diagnostic("EM001_DECISION_RESOLUTION", f"{path}.resolution", "resolved decision needs a complete resolution", node_id))
        else:
            selected = resolution.get("option_id")
            if not isinstance(selected, str) or selected not in option_ids:
                errors.append(_diagnostic("EM001_DECISION_RESOLUTION", f"{path}.resolution.option_id", "resolution must select an existing option", node_id))
            for key in ("actor", "rationale", "timestamp"):
                value = resolution.get(key)
                if not isinstance(value, str) or not value.strip():
                    errors.append(_diagnostic("EM001_DECISION_RESOLUTION", f"{path}.resolution.{key}", f"{key} must be nonempty", node_id))
            timestamp = resolution.get("timestamp")
            if isinstance(timestamp, str) and timestamp.strip():
                try:
                    instant = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if instant.tzinfo is None or instant.utcoffset() != timezone.utc.utcoffset(instant):
                        raise ValueError("timestamp is not UTC")
                except ValueError:
                    errors.append(_diagnostic("EM001_DECISION_TIMESTAMP", f"{path}.resolution.timestamp", "timestamp must be ISO-8601 UTC", node_id))
    elif resolution is not None:
        errors.append(_diagnostic("EM001_DECISION_RESOLUTION", f"{path}.resolution", "unresolved decision cannot carry an active resolution", node_id))
    history = node.get("history", [])
    if not isinstance(history, list):
        errors.append(_diagnostic("EM001_DECISION_HISTORY", f"{path}.history", "history must be an array", node_id))
    else:
        allowed_events = {"resolved", "reopened", "retired", "options_revised", "invalidated"}
        required = {"event", "actor", "rationale", "timestamp", "options", "resolution"}
        for index, entry in enumerate(history):
            entry_path = f"{path}.history[{index}]"
            if not isinstance(entry, dict) or set(entry) != required:
                errors.append(_diagnostic("EM001_DECISION_HISTORY", entry_path,
                                          "history entry has an invalid shape", node_id))
                continue
            if (entry["event"] not in allowed_events
                    or not isinstance(entry["actor"], str) or not entry["actor"].strip()
                    or not isinstance(entry["rationale"], str) or not entry["rationale"].strip()
                    or not _utc_timestamp(entry["timestamp"])):
                errors.append(_diagnostic("EM001_DECISION_HISTORY", entry_path,
                                          "history needs a known event, attribution, rationale, and UTC timestamp", node_id))
            historical_options = entry["options"]
            if (not isinstance(historical_options, list)
                    or any(not isinstance(option, dict) or set(option) != {"id", "label"}
                           or not isinstance(option.get("id"), str) or not option["id"]
                           or not isinstance(option.get("label"), str) or not option["label"].strip()
                           for option in historical_options)
                    or len({option["id"] for option in historical_options if isinstance(option, dict)
                            and isinstance(option.get("id"), str)}) != len(historical_options)
                    or len({option["label"] for option in historical_options if isinstance(option, dict)
                            and isinstance(option.get("label"), str)}) != len(historical_options)):
                errors.append(_diagnostic("EM001_DECISION_HISTORY", f"{entry_path}.options",
                                          "historical options must have unique nonempty IDs and labels", node_id))
            resolution = entry["resolution"]
            if resolution != {}:
                if (not isinstance(resolution, dict)
                        or set(resolution) != {"option_id", "actor", "rationale", "timestamp"}
                        or resolution.get("option_id") not in {
                            option.get("id") for option in historical_options
                            if isinstance(option, dict)}
                        or not isinstance(resolution.get("actor"), str) or not resolution["actor"].strip()
                        or not isinstance(resolution.get("rationale"), str) or not resolution["rationale"].strip()
                        or not _utc_timestamp(resolution.get("timestamp"))):
                    errors.append(_diagnostic("EM001_DECISION_HISTORY", f"{entry_path}.resolution",
                                              "historical resolution must select a retained option with attribution", node_id))
    return errors


def _utc_timestamp(value) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return instant.tzinfo is not None and instant.utcoffset() == timezone.utc.utcoffset(instant)
    except ValueError:
        return False


def _validate_reference(node: dict, node_path: str, node_id: str, node_type: str,
                        root: str | Path, work_id: str, errors: list[dict], reference_bytes=None) -> None:
    reference = node.get("reference")
    required = node.get("lifecycle") != "draft" if node_type in {"requirement", "scenario"} else True
    if reference is None:
        if required:
            errors.append(_diagnostic("EM001_REFERENCE", f"{node_path}.reference", "active node requires a reference", node_id))
        return
    fields = {"path", "id"} if node_type in {"requirement", "scenario", "test"} else {"path"}
    if node_type == "implementation":
        fields = {"path", "symbol"}
    required_fields = fields - ({"symbol"} if node_type == "implementation" else set())
    if (not isinstance(reference, dict) or set(reference) - fields
            or not required_fields.issubset(reference)):
        errors.append(_diagnostic("EM001_REFERENCE", f"{node_path}.reference", "reference has an invalid shape", node_id))
        return
    raw_path = reference.get("path")
    if node_type == "implementation" and "symbol" in reference:
        symbol = reference["symbol"]
        if not isinstance(symbol, str) or not symbol.strip():
            errors.append(_diagnostic("EM001_REFERENCE", f"{node_path}.reference.symbol",
                                      "implementation symbol must be nonempty text", node_id))
    if node_type in {"test_run", "evidence"} and isinstance(raw_path, str) and not raw_path.endswith(".json"):
        errors.append(_diagnostic("EM001_REFERENCE", f"{node_path}.reference.path",
                                  "test-run and evidence references must name JSON records", node_id))
    if (not isinstance(raw_path, str) or not raw_path or "\\" in raw_path
            or Path(raw_path).is_absolute() or PureWindowsPath(raw_path).drive
            or ".." in Path(raw_path).parts):
        errors.append(_diagnostic("EM001_REFERENCE_PATH", f"{node_path}.reference.path", "reference path must remain inside the repository", node_id))
        return
    if node_type in {"requirement", "scenario"} and raw_path != f"specs/current/{work_id}.json":
        parts = Path(raw_path).parts
        canonical_spec = (len(parts) == 3 and parts[0:2] == ("specs", "current")
                          and parts[2].endswith(".json") and bool(SLUG.fullmatch(parts[2][:-5])))
        if not canonical_spec:
            errors.append(_diagnostic("EM001_CANONICAL_REFERENCE", f"{node_path}.reference.path", "requirement and scenario references must use a canonical workstream spec", node_id))
    if node_type == "test":
        parts = Path(raw_path).parts
        canonical_plan = (len(parts) == 3 and parts[0] == "work" and parts[2] == "test-plan.json"
                          and bool(SLUG.fullmatch(parts[1])))
        if not canonical_plan:
            errors.append(_diagnostic("EM001_CANONICAL_REFERENCE", f"{node_path}.reference.path", "test references must use a canonical workstream test plan", node_id))
    repository = Path(root).resolve()
    try:
        resolved = (repository / raw_path).resolve()
    except (OSError, RuntimeError):
        errors.append(_diagnostic("EM001_REFERENCE_PATH", f"{node_path}.reference.path", "reference path cannot be resolved safely", node_id))
        return
    if not resolved.is_relative_to(repository):
        errors.append(_diagnostic("EM001_REFERENCE_PATH", f"{node_path}.reference.path", "reference path escapes the repository", node_id))
        return
    if node_type == "implementation":
        if reference_bytes is not None:
            if reference_bytes.get(raw_path) is None:
                errors.append(_diagnostic("EM001_REFERENCE_MISSING", f"{node_path}.reference.path",
                                          "implementation source is unavailable", node_id))
        elif not resolved.is_file():
            errors.append(_diagnostic("EM001_REFERENCE_MISSING", f"{node_path}.reference.path",
                                      "implementation source is unavailable", node_id))
    if node_type in {"requirement", "scenario"} and "id" in reference:
        _check_id(resolved, reference["id"], "criteria", node_path, node_id, errors,
                  captured=reference_bytes, relative=raw_path)
    elif node_type == "test" and "id" in reference:
        _check_id(resolved, reference["id"], "tests", node_path, node_id, errors,
                  captured=reference_bytes, relative=raw_path)


def _check_id(path: Path, identity: object, collection: str, node_path: str,
              node_id: str, errors: list[dict], key: str = "id", *, captured=None, relative=None) -> None:
    if not isinstance(identity, str) or not identity:
        errors.append(_diagnostic("EM001_REFERENCE_ID", f"{node_path}.reference.id", "reference id must be nonempty", node_id))
        return
    try:
        from .snapshot import decode
        raw = path.read_bytes() if captured is None else captured.get(relative)
        if raw is None:
            raise ValueError("missing captured definition")
        value = decode(raw)
    except (OSError, UnicodeError, ValueError):
        errors.append(_diagnostic("EM001_REFERENCE_MISSING", f"{node_path}.reference.path", "referenced definition is unavailable", node_id))
        return
    records = value.get(collection) if isinstance(value, dict) else None
    if not isinstance(records, list) or not any(isinstance(item, dict) and item.get(key) == identity for item in records):
        errors.append(_diagnostic("EM001_REFERENCE_ID", f"{node_path}.reference.id", "canonical reference id does not exist", node_id))
