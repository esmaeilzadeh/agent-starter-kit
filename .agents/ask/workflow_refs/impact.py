"""Cross-owner dependency traversal and conservative reassessment decisions."""
from __future__ import annotations

from .identity import ReferenceError, parse_reference
from .profiles import get_profile


class ImpactError(ValueError):
    """An impact graph or decision is malformed or incomplete."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _reference(value):
    try:
        return parse_reference(value)["canonical"]
    except ReferenceError as exc:
        raise ImpactError(exc.code, str(exc)) from exc


def _graph(graph):
    if not isinstance(graph, dict) or not isinstance(graph.get("nodes"), dict):
        raise ImpactError("discovery_incomplete", "graph must declare all nodes and dependency inputs")
    nodes = {}
    for reference, node in graph["nodes"].items():
        ref = _reference(reference)
        if not isinstance(node, dict) or not isinstance(node.get("inputs"), list):
            raise ImpactError("discovery_incomplete", f"dependency declarations unavailable for {ref}")
        edges = []
        for edge in node["inputs"]:
            if not isinstance(edge, dict) or set(edge) != {"reference", "role"}:
                raise ImpactError("discovery_incomplete", f"invalid dependency declaration for {ref}")
            target = _reference(edge["reference"])
            if not isinstance(edge["role"], str) or not edge["role"].strip():
                raise ImpactError("discovery_incomplete", f"dependency role unavailable for {ref}")
            edges.append({"reference": target, "role": edge["role"]})
        if ref in nodes:
            raise ImpactError("identity_conflict", f"duplicate graph identity: {ref}")
        nodes[ref] = {**node, "reference": ref, "inputs": edges}
    for ref, node in nodes.items():
        for edge in node["inputs"]:
            if edge["reference"] not in nodes:
                raise ImpactError("discovery_incomplete", f"unresolved dependency {edge['reference']} from {ref}")
    visiting, visited = set(), set()
    def visit(ref):
        if ref in visiting:
            raise ImpactError("cycle", f"dependency cycle includes {ref}")
        if ref in visited:
            return
        visiting.add(ref)
        for edge in nodes[ref]["inputs"]:
            visit(edge["reference"])
        visiting.remove(ref)
        visited.add(ref)
    for ref in nodes:
        visit(ref)
    return nodes


def record_decision(decision, capture=None):
    """Validate a reviewed retain/revise/retire decision without mutating pins."""
    if not isinstance(decision, dict):
        raise ImpactError("invalid_decision", "decision must be an object")
    required = {"action", "old_upstream", "new_upstream", "dependent", "profile",
                "context_generation", "examined_paths", "review_evidence", "reviewer",
                "coordinator", "outward_equal", "satisfies_new_inputs", "reuse_allowed", "required_paths"}
    if required - set(decision):
        raise ImpactError("authority_missing", "decision lacks exact context, evidence, or authority")
    if decision["action"] not in {"retain", "revise", "retire"}:
        raise ImpactError("invalid_decision", "action must be retain, revise, or retire")
    for key in ("old_upstream", "new_upstream", "dependent"):
        decision[key] = _reference(decision[key])
    if not isinstance(decision["profile"], str) or get_profile(decision["profile"]) is None:
        raise ImpactError("comparison_incomplete", "comparison profile is required")
    if (not isinstance(decision["examined_paths"], dict) or not decision["examined_paths"]
            or not isinstance(decision["required_paths"], list)
            or set(decision["required_paths"]) != set(decision["examined_paths"])):
        raise ImpactError("comparison_incomplete", "every affected input path must be resolved")
    unresolved = [path for path, value in decision["examined_paths"].items()
                  if not isinstance(path, str) or not path or value not in {"resolved", "unchanged", "changed"}]
    if unresolved:
        raise ImpactError("comparison_incomplete", "one or more affected input paths are unresolved")
    for key in ("review_evidence", "reviewer", "coordinator"):
        if not isinstance(decision[key], str) or not decision[key].strip():
            raise ImpactError("authority_missing", "review evidence and owner-scoped attribution are required")
    if capture is not None and (capture.get("status") != "complete"
                                or capture.get("generation") != decision["context_generation"]):
        raise ImpactError("stale_context", "decision does not bind the captured project generation")
    stop = (decision["action"] == "retain" and all(value in {"resolved", "unchanged"}
            for value in decision["examined_paths"].values()) and decision["outward_equal"] is True
            and decision["satisfies_new_inputs"] is True and decision["reuse_allowed"] is True)
    return {"status": "retained" if stop else "reassess", "decision": decision,
            "propagation_stopped": stop}


def assess_impact(graph, changed, decisions=None, capture=None):
    """Find direct consumers and actual descendants without clearing unresolved paths."""
    if capture is not None and capture.get("status") != "complete":
        return {"status": "incomplete", "reason": "capture_unavailable", "items": {}}
    try:
        nodes = _graph(graph)
        roots = {_reference(ref) for ref in changed}
    except (ImpactError, TypeError) as exc:
        return {"status": "incomplete", "reason": getattr(exc, "code", "invalid_graph"),
                "detail": str(exc), "items": {}}
    missing_roots = sorted(roots - nodes.keys())
    if missing_roots:
        return {"status": "incomplete", "reason": "missing_target", "unresolved": missing_roots, "items": {}}
    decisions = decisions or {}
    reverse = {}
    for consumer, node in nodes.items():
        for edge in node["inputs"]:
            reverse.setdefault(edge["reference"], []).append((consumer, edge))
    impacted = {}
    queue = [(root, [root]) for root in sorted(roots)]
    traversed = set()
    while queue:
        upstream, path = queue.pop(0)
        for consumer, edge in reverse.get(upstream, []):
            marker = (upstream, consumer)
            if marker in traversed:
                continue
            traversed.add(marker)
            decision = decisions.get(consumer)
            decision_result = None
            if decision is not None:
                try:
                    parsed_upstream = _reference(decision.get("old_upstream")) if isinstance(decision, dict) else None
                    if parsed_upstream == upstream and _reference(decision.get("dependent")) == consumer:
                        decision_result = record_decision(decision, capture)
                except (ImpactError, AttributeError) as exc:
                    decision_result = {"status": "incomplete", "reason": getattr(exc, "code", "invalid_decision"),
                                       "detail": str(exc)}
            stopped = bool(decision_result and decision_result.get("propagation_stopped"))
            item = impacted.setdefault(consumer, {"owner": parse_reference(consumer)["owner"],
                "status": "incomplete" if nodes[consumer].get("resolved") is False else "reassess",
                "paths": [], "inputs": [{"reference": input_edge["reference"],
                    "role": input_edge["role"], "resolved": bool(nodes.get(input_edge["reference"], {}).get("resolved", True))}
                    for input_edge in nodes[consumer]["inputs"]], "decision": decision_result})
            item["paths"].append(path + [consumer])
            if not stopped and consumer not in path:
                queue.append((consumer, path + [consumer]))
    incomplete = [ref for ref, item in impacted.items()
                  if item["status"] == "incomplete"
                  or any(not edge["resolved"] for edge in item["inputs"])
                  or (item["decision"] and item["decision"].get("status") == "incomplete")]
    for ref in incomplete:
        impacted[ref]["status"] = "incomplete"
    return {"status": "incomplete" if incomplete else "complete", "capture_generation":
            capture.get("generation") if capture else None, "roots": sorted(roots),
            "items": impacted, "unresolved": incomplete}
