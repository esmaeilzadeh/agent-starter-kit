"""Read-only subject resolution shared by stage intake and model inspection."""
from __future__ import annotations

from pathlib import Path

from .snapshot import capture
from .validation import SLUG


def _qualified(value):
    return (isinstance(value, dict) and set(value) == {"work_id", "node_id"}
            and isinstance(value.get("work_id"), str) and bool(value["work_id"])
            and isinstance(value.get("node_id"), str) and bool(value["node_id"]))


def _valid_execution_owner(value):
    return (isinstance(value, dict) and set(value) == {"work_id", "task_id"}
            and all(isinstance(item, str) and item for item in value.values()))


def _explicit_subject(value):
    if not isinstance(value, dict) or set(value) - {
            "work_id", "node_id", "contribution", "exclusions", "execution_owner"}:
        return False
    if not _qualified({"work_id": value.get("work_id"), "node_id": value.get("node_id")}):
        return False
    if "contribution" in value and (not isinstance(value["contribution"], str) or not value["contribution"].strip()):
        return False
    if "exclusions" in value and (not isinstance(value["exclusions"], list)
                                   or any(not isinstance(item, str) or not item.strip() for item in value["exclusions"])):
        return False
    if "execution_owner" in value and value["execution_owner"] is not None and not _valid_execution_owner(value["execution_owner"]):
        return False
    return True


def _recorded_association(value):
    if (not isinstance(value, dict) or not _qualified(value.get("subject"))
            or value.get("revision") != "snapshot"
            or not isinstance(value.get("snapshot_digest"), str)
            or len(value["snapshot_digest"]) != 64
            or any(char not in "0123456789abcdef" for char in value["snapshot_digest"])
            or not isinstance(value.get("contribution"), str) or not value["contribution"].strip()
            or not isinstance(value.get("exclusions"), list)
            or any(not isinstance(item, str) or not item.strip() for item in value["exclusions"])
            or not isinstance(value.get("history"), list) or not value["history"]):
        return False
    owner = value.get("execution_owner")
    if owner is not None and (not isinstance(owner, dict) or set(owner) != {"work_id", "task_id"}
                              or any(not isinstance(item, str) or not item for item in owner.values())):
        return False
    return all(isinstance(event, dict) and all(isinstance(event.get(key), str) and event[key].strip()
               for key in ("actor", "rationale", "timestamp")) for event in value["history"])


def resolve(root, work_id, request, *, branch=None):
    """Resolve only explicit qualified subjects or a reviewed model association.

    Branches, tracker IDs and parked cards remain labeled context. They never
    establish ownership or cause writes.
    """
    root = Path(root).resolve()
    request = request if isinstance(request, dict) else {}
    snapshot = capture(root, work_id)
    diagnostics = snapshot.diagnostics(root)
    result = {"schema": "ask-engineering-context/v1", "work_id": work_id,
              "disposition": "chooser", "subject": None, "source": None,
              "snapshot": snapshot.identity, "diagnostics": diagnostics,
              "relationships": [], "contribution": None, "exclusions": [],
              "execution_owner": None, "proposal": None, "external_context": None,
              "branch": branch, "inspection_only": bool(request.get("inspection_only"))}
    if diagnostics:
        result["disposition"] = "unavailable"
        return result
    document = snapshot.document
    nodes = {node["id"]: node for node in document.get("nodes", []) if isinstance(node, dict)
             and isinstance(node.get("id"), str)}
    association = document.get("subject_association")
    explicit = request.get("explicit_subjects", [])
    if not isinstance(explicit, list):
        result["disposition"] = "needs_clarification"
        result["diagnostics"] = [{"code": "EM018_SUBJECT_REQUEST", "message": "explicit_subjects must be an array"}]
        return result
    identities = []
    explicit_details = {}
    for item in explicit:
        if not _explicit_subject(item):
            result["disposition"] = "needs_clarification"
            result["diagnostics"] = [{"code": "EM018_SUBJECT_ID", "message": "subject IDs must be qualified by work_id and node_id"}]
            return result
        identity = {"work_id": item["work_id"], "node_id": item["node_id"]}
        if identity not in identities:
            identities.append(identity)
        for key in ("contribution", "exclusions", "execution_owner"):
            if key in item:
                if key in explicit_details and explicit_details[key] != item[key]:
                    result["disposition"] = "needs_clarification"
                    result["diagnostics"] = [{"code": "EM018_SUBJECT_CONFLICT",
                                              "message": f"explicit subject {key} details conflict"}]
                    return result
                explicit_details[key] = item[key]
    if len(identities) > 1:
        result["disposition"] = "needs_clarification"
        result["diagnostics"] = [{"code": "EM018_SUBJECT_CONFLICT", "message": "explicit subject identities conflict"}]
        return result
    if identities:
        subject = identities[0]
        result["source"] = "explicit-request"
        for key in ("contribution", "exclusions", "execution_owner"):
            if key in request:
                if key in explicit_details and explicit_details[key] != request[key]:
                    result["disposition"] = "needs_clarification"
                    result["diagnostics"] = [{"code": "EM018_SUBJECT_CONFLICT",
                                              "message": f"request {key} conflicts with explicit subject details"}]
                    return result
                explicit_details[key] = request[key]
        result["contribution"] = explicit_details.get("contribution")
        result["exclusions"] = explicit_details.get("exclusions", [])
        result["execution_owner"] = explicit_details.get("execution_owner")
    elif _recorded_association(association):
        subject = association["subject"]
        result["source"] = "recorded-association"
    else:
        subject = None
    if subject is not None:
        requested_owner = explicit_details.get("execution_owner", request.get("execution_owner"))
        recorded_owner = association.get("execution_owner") if _recorded_association(association) else None
        if (requested_owner is not None and recorded_owner is not None
                and requested_owner != recorded_owner):
            result["disposition"] = "needs_clarification"
            result["diagnostics"] = [{"code": "EM018_OWNER_CONFLICT",
                                      "message": "explicit execution owner conflicts with the recorded association"}]
            return result
        if subject["work_id"] == work_id and subject["node_id"] not in nodes:
            result["disposition"] = "needs_clarification"
            result["diagnostics"] = [{"code": "EM018_SUBJECT_MISSING", "message": "subject node is absent from its owning model"}]
            return result
        result["subject"] = subject
        result["disposition"] = "resolved"
        if subject["work_id"] == work_id:
            owner_document, owner_nodes, owner_edges = document, nodes, document.get("edges", [])
        elif not SLUG.fullmatch(subject["work_id"]):
            result["disposition"] = "needs_clarification"
            result["diagnostics"] = [{"code": "EM018_SUBJECT_ID", "message": "foreign subject owner must be a work ID"}]
            return result
        else:
            try:
                owner_snapshot = capture(root, subject["work_id"])
            except (OSError, ValueError) as exc:
                result["disposition"] = "unavailable"
                result["external_context"] = {"state": "unavailable", "reference": subject,
                                              "diagnostics": [{"code": "EM018_OWNER_UNAVAILABLE",
                                                               "message": str(exc)}]}
                return result
            owner_errors = owner_snapshot.diagnostics(root)
            owner_document = owner_snapshot.document if not owner_errors else {}
            owner_nodes = {node["id"]: node for node in owner_document.get("nodes", [])
                           if isinstance(node, dict) and isinstance(node.get("id"), str)}
            if owner_errors or subject["node_id"] not in owner_nodes:
                result["disposition"] = "unavailable"
                result["external_context"] = {"state": "unavailable", "reference": subject,
                                              "diagnostics": owner_errors}
                return result
            owner_edges = owner_document.get("edges", [])
            result["external_context"] = {"state": "available", "snapshot": owner_snapshot.identity}
        node = owner_nodes[subject["node_id"]]
        result["relationships"] = [edge for edge in owner_edges
                                    if edge.get("source") == subject["node_id"] or edge.get("target") == subject["node_id"]]
        result["purpose"] = node.get("title")
        if result["source"] == "recorded-association":
            result["contribution"] = association.get("contribution")
            result["exclusions"] = association.get("exclusions", [])
            result["execution_owner"] = association.get("execution_owner")
            result["association_revision"] = association.get("snapshot_digest")
    elif request.get("later_cards"):
        cards = request["later_cards"]
        result["proposal"] = {"source": "later-card", "references": cards if isinstance(cards, list) else []}
    tracker = request.get("tracker_context")
    if isinstance(tracker, dict):
        tracker_state = "unavailable" if tracker.get("available") is False else "supplied-unverified"
        tracker_context = {"state": tracker_state, "reference": tracker.get("id")}
        if isinstance(result.get("external_context"), dict):
            result["external_context"]["tracker"] = tracker_context
        else:
            result["external_context"] = tracker_context
        if tracker_state == "unavailable" and result["disposition"] == "resolved":
            result["disposition"] = "unavailable"
    if subject is None and result["disposition"] != "needs_clarification":
        result["disposition"] = "chooser"
    return result
