"""Cross-owner dependency traversal and conservative reassessment decisions."""
from __future__ import annotations

from copy import deepcopy
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
    deletions = graph.get("deletions", {})
    unavailable = graph.get("unavailable", {})
    if not isinstance(deletions, dict) or not isinstance(unavailable, dict):
        raise ImpactError("discovery_incomplete", "deletion and availability declarations must be objects")
    deletion_refs = {}
    unavailable_refs = set()
    for raw_ref, declaration in deletions.items():
        ref = _reference(raw_ref)
        if (not isinstance(declaration, dict) or declaration.get("status") != "absent"
                or declaration.get("source_available") is not True):
            raise ImpactError("discovery_incomplete", f"deletion is not proven in an available source: {ref}")
        deletion_refs[ref] = declaration
    for raw_ref, declaration in unavailable.items():
        ref = _reference(raw_ref)
        if not isinstance(declaration, dict) or declaration.get("source_available") is not False:
            raise ImpactError("discovery_incomplete", f"availability state is invalid: {ref}")
        unavailable_refs.add(ref)
    for ref, node in nodes.items():
        for edge in node["inputs"]:
            if edge["reference"] not in nodes and edge["reference"] not in deletion_refs and edge["reference"] not in unavailable_refs:
                raise ImpactError("discovery_incomplete", f"unresolved dependency {edge['reference']} from {ref}")
    visiting, visited = set(), set()
    def visit(ref):
        if ref in visiting:
            raise ImpactError("cycle", f"dependency cycle includes {ref}")
        if ref in visited:
            return
        visiting.add(ref)
        for edge in nodes[ref]["inputs"]:
            if edge["reference"] in nodes:
                visit(edge["reference"])
        visiting.remove(ref)
        visited.add(ref)
    for ref in nodes:
        visit(ref)
    return nodes


def record_decision(decision, capture=None, required_paths=None, authority_check=None):
    """Validate a reviewed retain/revise/retire decision without mutating pins."""
    if not isinstance(decision, dict):
        raise ImpactError("invalid_decision", "decision must be an object")
    required = {"action", "old_upstream", "new_upstream", "dependent", "profile",
                "context_generation", "examined_paths", "review_evidence", "reviewer",
                "coordinator", "outward_equal", "satisfies_new_inputs", "reuse_allowed",
                "required_paths", "eligible_consumers", "new_dependent", "retirement_safe"}
    if required - set(decision):
        raise ImpactError("authority_missing", "decision lacks exact context, evidence, or authority")
    if decision["action"] not in {"retain", "revise", "retire"}:
        raise ImpactError("invalid_decision", "action must be retain, revise, or retire")
    decision = deepcopy(decision)
    for key in ("old_upstream", "new_upstream", "dependent"):
        decision[key] = _reference(decision[key])
    if decision["action"] == "retain":
        decision["new_dependent"] = _reference(decision["new_dependent"])
        if decision["new_dependent"] != decision["dependent"]:
            raise ImpactError("invalid_decision", "retain must preserve the original dependent pin")
    elif decision["action"] == "retire":
        if decision["new_dependent"] is not None:
            raise ImpactError("invalid_decision", "retire has no replacement dependent revision")
    elif decision["action"] == "revise":
        decision["new_dependent"] = _reference(decision["new_dependent"])
        old = parse_reference(decision["dependent"])
        new = parse_reference(decision["new_dependent"])
        if old["logical_id"] != new["logical_id"] or new["revision"] <= old["revision"]:
            raise ImpactError("invalid_decision", "revision must publish a fresh version of the same item")
    if decision["reviewer"] == decision["coordinator"]:
        raise ImpactError("authority_missing", "reviewer and coordinator attribution must be independent")
    if not isinstance(decision["profile"], str) or get_profile(decision["profile"]) is None:
        raise ImpactError("comparison_incomplete", "comparison profile is required")
    if (not isinstance(decision["examined_paths"], dict) or not decision["examined_paths"]
            or not isinstance(decision["required_paths"], list)
            or not all(isinstance(path, str) and path for path in decision["required_paths"])
            or len(set(decision["required_paths"])) != len(decision["required_paths"])
            or set(decision["required_paths"]) != set(decision["examined_paths"])
            or not isinstance(decision["eligible_consumers"], list)
            or not all(isinstance(consumer, str) for consumer in decision["eligible_consumers"])):
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
    if required_paths is not None:
        if (not isinstance(required_paths, (list, tuple, set, frozenset))
                or not all(isinstance(path, str) and path for path in required_paths)
                or set(required_paths) != set(decision["required_paths"])):
            raise ImpactError("comparison_incomplete", "decision does not cover every declared dependent input")
    authorized = False
    if callable(authority_check):
        try:
            authorized = authority_check(decision, capture) is True
        except Exception:
            authorized = False
    stop = (decision["action"] == "retain" and bool(decision["eligible_consumers"])
            and required_paths is not None and authorized
            and all(value in {"resolved", "unchanged"}
            for value in decision["examined_paths"].values()) and decision["outward_equal"] is True
            and decision["satisfies_new_inputs"] is True and decision["reuse_allowed"] is True)
    complete = (required_paths is not None and set(required_paths) == set(decision["required_paths"])
                and all(value in {"resolved", "unchanged"} for value in decision["examined_paths"].values()))
    retired = decision["action"] == "retire" and decision["retirement_safe"] is True and authorized and complete
    revised = decision["action"] == "revise" and authorized and complete
    status = "retained" if stop else "retired" if retired else "revised" if revised else "reassess"
    return {"status": status, "active_status": "retired" if retired else "active",
            "decision": dict(decision),
            "propagation_stopped": stop}


def assess_impact(graph, changed, decisions=None, capture=None, repository_root=None,
                  authority_check=None):
    """Find direct consumers and actual descendants without clearing unresolved paths."""
    if capture is None or capture.get("status") != "complete":
        return {"status": "incomplete", "reason": "capture_unavailable", "items": {}}
    if repository_root is None:
        return {"status": "incomplete", "reason": "capture_repository_unavailable", "items": {}}
    from .project import load_project_graph, validate_capture
    validity = validate_capture(repository_root, capture)
    if validity.get("status") != "complete":
        return {"status": "incomplete", "reason": validity.get("reason", "stale_inventory"), "items": {}}
    source_graph = load_project_graph(repository_root, capture)
    if source_graph.get("status") != "complete":
        return {"status": "incomplete", "reason": "discovery_incomplete",
                "unresolved": source_graph.get("unresolved", []), "items": {}}
    if graph is not None and any(graph.get(key) != source_graph.get(key)
                                 for key in ("nodes", "deletions", "changes", "capture_generation")):
        return {"status": "incomplete", "reason": "unbound_project_graph", "items": {}}
    graph = source_graph
    try:
        nodes = _graph(graph)
        roots = {_reference(ref) for ref in changed}
    except (ImpactError, TypeError) as exc:
        return {"status": "incomplete", "reason": getattr(exc, "code", "invalid_graph"),
                "detail": str(exc), "items": {}}
    decisions = decisions or {}
    deletions = {_reference(ref): value for ref, value in graph.get("deletions", {}).items()}
    unavailable = {_reference(ref) for ref in graph.get("unavailable", {})}
    missing_roots = sorted(ref for ref in roots if ref not in nodes and ref not in deletions)
    if missing_roots:
        return {"status": "incomplete", "reason": "missing_target", "unresolved": missing_roots, "items": {}}
    reverse = {}
    for consumer, node in nodes.items():
        if node.get("active") is False:
            continue
        for edge in node["inputs"]:
            reverse.setdefault(edge["reference"], []).append((consumer, edge))
    impacted = {}
    queue = [(root, [root]) for root in sorted(roots)]
    traversed = set()
    while queue:
        upstream, path = queue.pop(0)
        for consumer, edge in reverse.get(upstream, []):
            marker = (upstream, consumer, tuple(path))
            if marker in traversed:
                continue
            traversed.add(marker)
            decision = decisions.get(consumer)
            decision_result = None
            if decision is not None:
                try:
                    parsed_upstream = _reference(decision.get("old_upstream")) if isinstance(decision, dict) else None
                    input_paths = sorted(f"{item['reference']}|{item['role']}" for item in nodes[consumer]["inputs"])
                    eligible = decision.get("eligible_consumers", []) if isinstance(decision, dict) else []
                    new_upstream = _reference(decision.get("new_upstream")) if isinstance(decision, dict) else None
                    old_upstream_identity = parse_reference(upstream)
                    new_upstream_identity = parse_reference(new_upstream)
                    valid_upstream_revision = (decision.get("action") != "retain" or
                        (old_upstream_identity["logical_id"] == new_upstream_identity["logical_id"]
                         and new_upstream_identity["revision"] > old_upstream_identity["revision"]))
                    valid_eligible = all(_reference(candidate) in nodes and any(
                        edge["reference"] == consumer for edge in nodes[_reference(candidate)]["inputs"])
                        and nodes[_reference(candidate)].get("active", True)
                        for candidate in eligible)
                    if (parsed_upstream != upstream or _reference(decision.get("dependent")) != consumer
                            or not valid_eligible or new_upstream not in nodes
                            or not nodes[new_upstream].get("active", True) or not valid_upstream_revision
                            or decision.get("profile") != nodes[consumer].get("profile")):
                        decision_result = {"status": "incomplete", "reason": "decision_scope_mismatch"}
                    else:
                        if decision.get("action") == "revise" and (
                                _reference(decision.get("new_dependent")) not in nodes
                                or not nodes[_reference(decision.get("new_dependent"))].get("active", True)):
                            decision_result = {"status": "incomplete", "reason": "new_dependent_unregistered"}
                            raise ImpactError("new_dependent_unregistered", "revised item version is not in the captured catalog")
                        decision_result = record_decision(decision, capture,
                            required_paths=input_paths, authority_check=authority_check)
                        if (decision_result.get("status") == "retired"
                                and any(nodes.get(downstream, {}).get("active", True)
                                        for downstream, _edge in reverse.get(consumer, []))):
                            decision_result = {"status": "incomplete", "reason": "active_consumers_remain"}
                except (ImpactError, AttributeError) as exc:
                    decision_result = {"status": "incomplete", "reason": getattr(exc, "code", "invalid_decision"),
                                       "detail": str(exc)}
            stopped = bool(decision_result and decision_result.get("propagation_stopped"))
            item = impacted.setdefault(consumer, {"owner": parse_reference(consumer)["owner"],
                "status": "incomplete" if nodes[consumer].get("resolved") is False else "reassess",
                "paths": [], "inputs": [{"reference": input_edge["reference"],
                    "role": input_edge["role"],
                    "resolved": input_edge["reference"] not in unavailable
                        and bool(nodes.get(input_edge["reference"], {}).get("resolved", True)),
                    "deleted": input_edge["reference"] in deletions}
                    for input_edge in nodes[consumer]["inputs"]], "decision": decision_result})
            if decision_result and decision_result.get("status") == "retired":
                item["status"] = "retired"
            elif decision_result and decision_result.get("status") == "revised":
                item["status"] = "revised"
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
            "deletions": {ref: deletions[ref] for ref in sorted(roots) if ref in deletions},
            "items": impacted, "unresolved": incomplete}
