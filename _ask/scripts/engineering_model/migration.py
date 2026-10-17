"""Explicit, reviewed v1-to-v2 migration through the shared guarded action."""
from __future__ import annotations

import copy
import hashlib
import json

from .actions import Refused, run_action
from .validation import SCHEMA, SCHEMA_V2

REVIEW_SCHEMA = "ask-engineering-migration-review/v1"


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=False).encode("utf-8")).hexdigest()


def _references(document):
    return {node["id"]: copy.deepcopy(node["reference"])
            for node in document.get("nodes", [])
            if isinstance(node, dict) and isinstance(node.get("id"), str)
            and "reference" in node}


def preservation_diff(source, target):
    """Describe stable historical identities, references and edge changes."""
    source_nodes = {node["id"]: node for node in source.get("nodes", [])
                    if isinstance(node, dict) and isinstance(node.get("id"), str)}
    target_nodes = {node["id"]: node for node in target.get("nodes", [])
                    if isinstance(node, dict) and isinstance(node.get("id"), str)}
    source_edges = {tuple(sorted(edge.items())) for edge in source.get("edges", []) if isinstance(edge, dict)}
    target_edges = {tuple(sorted(edge.items())) for edge in target.get("edges", []) if isinstance(edge, dict)}
    changed_references = sorted(node_id for node_id in source_nodes.keys() & target_nodes.keys()
                                if source_nodes[node_id].get("reference") != target_nodes[node_id].get("reference"))
    return {
        "added_ids": sorted(target_nodes.keys() - source_nodes.keys()),
        "removed_ids": sorted(source_nodes.keys() - target_nodes.keys()),
        "changed_references": changed_references,
        "changed_edges": {"removed": [list(edge) for edge in sorted(source_edges - target_edges)],
                          "added": [list(edge) for edge in sorted(target_edges - source_edges)]},
    }


def review_migration(source, target, review, *, work_id):
    """Validate an explicit review bound to the exact source, target and diff."""
    if not isinstance(source, dict) or source.get("schema") != SCHEMA:
        raise ValueError("migration source must be an ask-engineering-model/v1 document")
    if not isinstance(target, dict) or target.get("schema") != SCHEMA_V2:
        raise ValueError("migration target must be an ask-engineering-model/v2 document")
    if source.get("work_id") != work_id or target.get("work_id") != work_id:
        raise ValueError("migration work_id must match the selected workstream")
    if not isinstance(review, dict) or review.get("schema") != REVIEW_SCHEMA:
        raise ValueError("migration review schema is missing or invalid")
    if review.get("decision") != "APPROVED":
        raise ValueError("migration requires an explicit APPROVED review")
    for field in ("reviewer", "rationale"):
        if not isinstance(review.get(field), str) or not review[field].strip():
            raise ValueError(f"migration review {field} must be nonempty")
    diff = preservation_diff(source, target)
    if diff["removed_ids"]:
        raise ValueError("migration cannot remove historical node identities")
    if diff["changed_references"]:
        raise ValueError("migration cannot rewrite historical references")
    expected = {"source_digest": _digest(source), "target_digest": _digest(target),
                "diff_digest": _digest(diff)}
    for field, digest in expected.items():
        if review.get(field) != digest:
            raise ValueError(f"migration review {field} does not match the exact input digest")
    return {"status": "approved", **expected, "preservation_diff": diff,
            "reviewer": review["reviewer"], "rationale": review["rationale"]}


def migrate(root, work_id, expected, target, review):
    """Apply a reviewed target using pre/action/post/publication admission."""
    def precondition(snapshot):
        if snapshot.document.get("schema") != SCHEMA:
            raise Refused("EM020_MIGRATION_SOURCE", "only an admitted v1 model can be explicitly migrated")
        review_migration(snapshot.document, target, review, work_id=work_id)

    def action(snapshot):
        review_migration(snapshot.document, target, review, work_id=work_id)
        return {snapshot.model_path: json.dumps(target, ensure_ascii=False, sort_keys=True,
                                                indent=2).encode("utf-8") + b"\n"}

    return run_action(root, work_id, expected, action, precondition=precondition)
