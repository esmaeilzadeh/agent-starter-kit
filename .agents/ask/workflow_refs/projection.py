"""Compact public projections for workflow references."""
from __future__ import annotations

import json

from .identity import parse_reference
from .store import resolve_version


def show_reference(repository_root, reference, *, integrity=False):
    """Resolve one exact qualified revision and omit full digests by default."""
    parsed = parse_reference(reference)
    catalog = repository_root / "work" / parsed["owner"] / "references" / "integrity.json"
    resolved = resolve_version(catalog, parsed["canonical"], repository_root)
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
