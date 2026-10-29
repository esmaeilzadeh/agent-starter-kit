"""Compact public projections for workflow references."""
from __future__ import annotations

import json
import fcntl
from pathlib import Path

from .identity import parse_reference
from .store import (CatalogError, _lock, _recover_pending, _repo_info,
                    _trusted_catalog, resolve_version)


def _resolve_decision(repository_root, catalog_path, parsed):
    """Resolve a decision extension from its trusted owner catalog."""
    owner = parsed["owner"]
    root, _common, relative = _repo_info(catalog_path)
    if Path(repository_root).resolve() != root:
        raise CatalogError("invalid_catalog", "decision catalog belongs to another repository")
    lock = _lock(catalog_path)
    try:
        _recover_pending(catalog_path, owner, root, relative)
        catalog, _ref_value = _trusted_catalog(catalog_path, owner, root, relative)
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()
    if catalog is None:
        raise CatalogError("missing_authority", "trusted catalog is not registered")
    decisions = catalog.get("decisions", [])
    if not isinstance(decisions, list):
        raise CatalogError("invalid_catalog", "trusted decision records are not a list")
    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        raise CatalogError("invalid_catalog", "trusted catalog entries are not a list")
    if any(isinstance(item, dict) and item.get("reference") == parsed["canonical"]
           for item in entries):
        raise CatalogError("ambiguous", "reference is present in both catalog entries and decisions")
    matches = [item for item in decisions
               if isinstance(item, dict) and item.get("reference") == parsed["canonical"]]
    if len(matches) != 1:
        raise CatalogError("missing", f"catalog has no unique decision for {parsed['canonical']}")
    decision = matches[0]
    if not isinstance(decision.get("decision"), dict) or not isinstance(decision.get("status"), str):
        raise CatalogError("invalid_catalog", "trusted decision record is malformed")
    return decision


def show_reference(repository_root, reference, *, integrity=False):
    """Resolve one exact qualified revision and omit full digests by default."""
    parsed = parse_reference(reference)
    catalog = (repository_root / "results/references/integrity.json"
               if parsed["owner"] == "repository-runs" else
               repository_root / "work" / parsed["owner"] / "references" / "integrity.json")
    try:
        resolved = resolve_version(catalog, parsed["canonical"], repository_root)
    except CatalogError as exc:
        if parsed["kind"] != "review" or exc.code != "missing":
            raise
        decision_record = _resolve_decision(repository_root, catalog, parsed)
        decision_payload = {"status": decision_record["status"],
                            "decision": decision_record["decision"]}
        return {
            "status": "resolved",
            "reference": parsed["canonical"],
            "owner": parsed["owner"],
            "type": parsed["kind"],
            "parents": {},
            "id": parsed["ids"][-1],
            "revision": parsed["revision"],
            "profile": "impact-decision/1",
            "item_id": f"review-{parsed['ids'][-1]}",
            "payload": decision_payload,
        }
    entry = resolved["entry"]
    try:
        payload = json.loads(resolved["payload"].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = resolved["payload"].decode("utf-8", errors="replace")
    result = {
        "status": "resolved",
        "reference": parsed["canonical"],
        "owner": parsed["owner"],
        "type": parsed["kind"],
        "parents": dict(zip({"part": ("spec",), "plan": ("spec",),
                             "item": ("spec", "plan"), "task": ("spec", "plan"),
                             "test": ("spec", "plan", "task")}.get(parsed["kind"], ()),
                            parsed["ids"][:-1])),
        "id": parsed["ids"][-1],
        "revision": parsed["revision"],
        "profile": entry["profile"],
        "item_id": entry["item_id"],
        "payload": payload,
    }
    if integrity:
        result["integrity"] = {
            "algorithm": entry["digest_algorithm"],
            "semantics": entry["digest_semantics"],
            "digests": resolved["digests"],
            "snapshot_id": entry["snapshot_id"],
        }
    return result


def project_status(repository_root, *, integration_ref="refs/heads/develop",
                   archive_ref="refs/heads/main", shared_owners=()):
    """Return the compact owner vector; never dump per-entry catalog digests."""
    from .project import capture_project

    capture = capture_project(repository_root, integration_ref, archive_ref,
                              shared_owners=shared_owners)
    if capture.get("status") != "complete":
        return {"status": "incomplete", "scope": "local-cooperating-repository",
                "reason": capture.get("reason", "discovery_incomplete"),
                "detail": capture.get("detail")}
    return {
        "status": "complete",
        "generation": capture["generation"],
        "scope": capture["scope"],
        "integration_ref": capture.get("integration_ref"),
        "archive_ref": capture.get("archive_ref"),
        "owners": {owner: {"kind": value["kind"], "refs": sorted(value["refs"])}
                   for owner, value in sorted(capture["owners"].items())},
    }
