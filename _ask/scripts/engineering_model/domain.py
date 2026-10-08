"""Pure semantic command boundary; filesystem publication belongs to actions."""
from copy import deepcopy
from datetime import datetime, timezone

from .validation import LIFECYCLES


def task_states(document):
    nodes = {node["id"]: node for node in document.get("nodes", [])}
    dependencies = {}
    for edge in document.get("edges", []):
        if edge["type"] == "depends_on":
            dependencies.setdefault(edge["source"], []).append(edge["target"])
    result = []
    for identity, node in sorted(nodes.items()):
        if node["type"] != "task":
            continue
        blockers = []
        for target in sorted(dependencies.get(identity, [])):
            prerequisite = nodes[target]
            expected = {"decision": "resolved", "assumption": "confirmed", "task": "done"}[prerequisite["type"]]
            if prerequisite["lifecycle"] != expected:
                blockers.append({"id": target, "type": prerequisite["type"], "lifecycle": prerequisite["lifecycle"],
                                 "reason": f"{target} is {prerequisite['lifecycle']}; requires {expected}"})
        status = node["lifecycle"] if node["lifecycle"] in ("done", "retired") else "blocked" if blockers else "ready"
        result.append({"id": identity, "lifecycle": node["lifecycle"], "status": status, "blockers": blockers})
    return result


def _history(node, event, actor, reason, timestamp):
    node.setdefault("history", []).append({"event": event, "actor": actor, "rationale": reason,
                                          "timestamp": timestamp, "options": deepcopy(node["options"]),
                                          "resolution": deepcopy(node.get("resolution", {}))})


def _attribution(command):
    for name in ("actor", "rationale"):
        if not isinstance(command.get(name), str) or not command[name].strip():
            raise ValueError(f"{name} must be nonempty")
    return command["actor"], command["rationale"]


def apply_batch(document, commands, *, timestamp=None):
    """Apply an isolated semantic proposal, with one revision for the whole batch."""
    candidate = deepcopy(document)
    effects = []
    timestamp = timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        if not isinstance(commands, list):
            raise ValueError("commands must be an array")
        nodes = {node["id"]: node for node in candidate["nodes"]}
        for command in commands:
            if not isinstance(command, dict):
                raise ValueError("command must be an object")
            op = command.get("op")
            identity = command.get("id")
            if not isinstance(identity, str) or identity not in nodes:
                raise ValueError("command must select an existing node ID")
            node = nodes[identity]
            if op in ("resolve_decision", "reopen_decision", "retire_decision"):
                allowed = {"op", "id", "actor", "rationale"} | ({"option_id"} if op == "resolve_decision" else set())
                if set(command) - allowed:
                    raise ValueError("unexpected decision command field")
                actor, reason = _attribution(command)
                if node["type"] != "decision" or node["lifecycle"] == "retired":
                    raise ValueError("decision command requires a nonretired decision")
                if op == "resolve_decision":
                    if node["lifecycle"] != "open":
                        raise ValueError("only an open decision can be resolved")
                    selected = command.get("option_id")
                    if not isinstance(selected, str) or selected not in {o["id"] for o in node["options"]}:
                        raise ValueError("option_id must select a declared alternative")
                    node["resolution"] = {"option_id": selected, "actor": actor, "rationale": reason, "timestamp": timestamp}
                    node["lifecycle"] = "resolved"
                    _history(node, "resolved", actor, reason, timestamp)
                else:
                    if op == "reopen_decision" and node["lifecycle"] != "resolved":
                        raise ValueError("only a resolved decision can be reopened")
                    _history(node, "reopened" if op == "reopen_decision" else "retired", actor, reason, timestamp)
                    node.pop("resolution", None)
                    node["lifecycle"] = "open" if op == "reopen_decision" else "retired"
            elif op == "revise_node":
                if set(command) - {"op", "id", "changes", "actor", "rationale"}:
                    raise ValueError("unexpected revision command field")
                changes = command.get("changes")
                if not isinstance(changes, dict) or not changes or set(changes) - {"title", "description", "reference", "lifecycle", "options"}:
                    raise ValueError("revision changes must use mutable definition fields; IDs and types are immutable")
                if node["lifecycle"] == "retired":
                    raise ValueError("retired definitions cannot be revised")
                if node["type"] == "decision":
                    if "lifecycle" in changes:
                        raise ValueError("decision lifecycle changes require attributable decision operations")
                    if "options" in changes:
                        if node["lifecycle"] != "open":
                            raise ValueError("options may change only on an open decision")
                        _history(node, "options_revised", command.get("actor", "document-change"),
                                 command.get("rationale", "alternatives revised"), timestamp)
                if "lifecycle" in changes:
                    value = changes["lifecycle"]
                    if not isinstance(value, str) or value not in LIFECYCLES[node["type"]]:
                        raise ValueError("invalid lifecycle transition")
                node.update(deepcopy(changes))
            else:
                raise ValueError(f"unsupported command: {op}")
            effects.append({"op": op, "id": identity})
        candidate["revision"] += 1
        return {"valid": True, "model": candidate, "diagnostics": [], "effects": effects, "tasks": task_states(candidate)}
    except (ValueError, KeyError, TypeError) as exc:
        return {"valid": False, "model": deepcopy(document), "diagnostics": [
            {"code": "EM002_COMMAND", "path": "$.commands", "message": str(exc)}], "effects": []}
