"""Compact public projections for workflow references."""
from __future__ import annotations

import json
import fcntl
import re
from decimal import Decimal, DecimalException
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


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def _project_payload(payload, include, selectors, map_entries):
    if not include and not selectors and not map_entries:
        return payload
    if not isinstance(payload, dict):
        raise CatalogError("invalid_projection", "projection requires a JSON object payload")

    projected = {}
    for field in include:
        if not isinstance(field, str) or not field or field in projected or field not in payload:
            raise CatalogError("invalid_projection", f"included field is unavailable or repeated: {field!r}")
        projected[field] = payload[field]

    selections = {}
    for selector in selectors:
        target, separator, value = selector.partition("=")
        field, dot, key = target.partition(".")
        if (not separator or not value or not dot or not field or not key
                or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", field)
                or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key)):
            raise CatalogError("invalid_projection", f"invalid record selector: {selector!r}")
        group = selections.setdefault(field, {"key": key, "values": []})
        if group["key"] != key or value in group["values"]:
            raise CatalogError("invalid_projection", f"conflicting or repeated selector: {selector!r}")
        group["values"].append(value)

    for field, group in selections.items():
        if field in projected:
            raise CatalogError("invalid_projection", f"field is both included and selected: {field!r}")
        rows = payload.get(field)
        if not isinstance(rows, list):
            raise CatalogError("invalid_projection", f"selected field is not an array: {field!r}")
        key, values = group["key"], group["values"]
        for value in values:
            matches = [row for row in rows if isinstance(row, dict) and row.get(key) == value]
            if not matches:
                raise CatalogError("missing", f"no {field} record has {key}={value!r}")
            if len(matches) > 1:
                raise CatalogError("ambiguous", f"multiple {field} records have {key}={value!r}")
        projected[field] = [row for row in rows
                            if isinstance(row, dict) and row.get(key) in values]

    map_selections = {}
    for selection in map_entries:
        field, separator, key = selection.partition("=")
        if not separator or not field or not key:
            raise CatalogError("invalid_projection", f"invalid map selector: {selection!r}")
        keys = map_selections.setdefault(field, [])
        if key in keys:
            raise CatalogError("invalid_projection", f"repeated map selector: {selection!r}")
        keys.append(key)
    for field, keys in map_selections.items():
        if field in projected:
            raise CatalogError("invalid_projection", f"field is selected more than once: {field!r}")
        source = payload.get(field)
        if not isinstance(source, dict):
            raise CatalogError("invalid_projection", f"selected field is not an object: {field!r}")
        missing = [key for key in keys if key not in source]
        if missing:
            raise CatalogError("missing", f"map entries are unavailable in {field!r}: {missing}")
        wanted = set(keys)
        projected[field] = {key: value for key, value in source.items() if key in wanted}
    return projected


def _project_text(text, sections, task_rows, yaml_tasks):
    if not isinstance(text, str) or (sections or task_rows) and yaml_tasks:
        raise CatalogError("invalid_projection", "text projection options do not match the source")
    if any(any(not isinstance(value, str) or not value for value in values)
           or len(set(values)) != len(values) for values in (sections, task_rows, yaml_tasks)):
        raise CatalogError("invalid_projection", "text projection selections cannot repeat")
    if yaml_tasks:
        if sections or task_rows:
            raise CatalogError("invalid_projection", "YAML task projection cannot be combined with Markdown")
        lines = text.splitlines()
        task_fields = [index for index, line in enumerate(lines)
                       if re.fullmatch(r"tasks:\s*(?:#.*)?", line)]
        if len(task_fields) != 1:
            raise CatalogError("invalid_projection", "YAML source has no unique root tasks field")
        tasks_header = task_fields[0]
        list_end = next((index for index in range(tasks_header + 1, len(lines))
                         if re.match(r"^[^#\s][^:]*:", lines[index])), len(lines))
        task_starts = [index for index in range(tasks_header + 1, list_end)
                       if re.fullmatch(r"  - id: .+", lines[index])]
        if not task_starts:
            raise CatalogError("invalid_projection", "YAML source has no supported task list")
        selected = lines[:tasks_header + 1]
        for task_id in yaml_tasks:
            start = [index for index in task_starts if lines[index] == f"  - id: {task_id}"]
            if not start:
                raise CatalogError("missing", f"YAML task is unavailable: {task_id!r}")
            if len(start) > 1:
                raise CatalogError("ambiguous", f"YAML task is duplicated: {task_id!r}")
            end = next((index for index in range(start[0] + 1, list_end)
                        if re.fullmatch(r"  - id: .+", lines[index])), list_end)
            selected.extend(lines[start[0]:end])
        return "\n".join(selected) + "\n"

    parts = []
    for heading in sections:
        marker = "## " + heading
        starts = [match.start() for match in re.finditer(r"(?m)^" + re.escape(marker) + r"$", text)]
        if not starts:
            raise CatalogError("missing", f"Markdown section is unavailable: {heading!r}")
        if len(starts) > 1:
            raise CatalogError("ambiguous", f"Markdown section is duplicated: {heading!r}")
        start = starts[0]
        end = text.find("\n## ", start + len(marker))
        parts.append(text[start:] if end < 0 else text[start:end])
    for task_id in task_rows:
        lines = text.splitlines()
        starts = [index for index, line in enumerate(lines)
                  if line.startswith("| " + task_id + " |")]
        if not starts:
            raise CatalogError("missing", f"Markdown task row is unavailable: {task_id!r}")
        if len(starts) > 1:
            raise CatalogError("ambiguous", f"Markdown task row is duplicated: {task_id!r}")
        end = next((index for index in range(starts[0] + 1, len(lines))
                    if lines[index].startswith("|") and not lines[index].startswith("|   ")), len(lines))
        row = "\n".join(lines[starts[0]:end]) + "\n"
        parts.append("## First task row\n" + row)
    if not parts:
        raise CatalogError("invalid_projection", "no text projection was selected")
    joined = "\n\n".join(parts)
    return joined if task_rows else joined + "\n"


def show_reference(repository_root, reference, *, integrity=False, include=(),
                   selectors=(), map_entries=(), sections=(), task_rows=(),
                   yaml_tasks=(), precise=False):
    """Resolve one exact qualified revision and omit full digests by default."""
    parsed = parse_reference(reference)
    catalog = (repository_root / "results/references/integrity.json"
               if parsed["owner"] == "repository-runs" else
               repository_root / "work" / parsed["owner"] / "references" / "integrity.json")
    resolved = None
    decision_record = None
    try:
        resolved = resolve_version(catalog, parsed["canonical"], repository_root)
    except CatalogError as exc:
        if parsed["kind"] != "review" or exc.code != "missing":
            raise
        decision_record = _resolve_decision(repository_root, catalog, parsed)
    entry = resolved["entry"] if resolved is not None else {
        "profile": "impact-decision/1",
        "item_id": f"review-{parsed['ids'][-1]}",
    }
    json_projection = bool(include or selectors or map_entries)
    text_projection = bool(sections or task_rows or yaml_tasks)
    if json_projection and text_projection:
        raise CatalogError("invalid_projection", "JSON and text projections cannot be combined")
    payload_format = "json"
    if decision_record is not None:
        payload = {"status": decision_record["status"],
                   "decision": decision_record["decision"]}
        if json_projection:
            payload = _project_payload(payload, include, selectors, map_entries)
        if text_projection:
            raise CatalogError("invalid_projection", "text projection requires a text reference")
    else:
        try:
            if text_projection:
                payload = resolved["payload"].decode("utf-8")
                payload = _project_text(payload, sections, task_rows, yaml_tasks)
                payload_format = "text"
            elif json_projection or precise:
                payload = json.loads(resolved["payload"].decode("utf-8"),
                                     object_pairs_hook=_unique_pairs,
                                     parse_float=Decimal,
                                     parse_constant=_reject_json_constant)
                if json_projection:
                    payload = _project_payload(payload, include, selectors, map_entries)
            else:
                payload = json.loads(resolved["payload"].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            if json_projection or text_projection:
                raise CatalogError("invalid_projection", "selected source is not valid UTF-8 JSON") from exc
            payload = resolved["payload"].decode("utf-8", errors="replace")
            payload_format = "text"
        except CatalogError:
            raise
        except (ValueError, DecimalException, RecursionError) as exc:
            if json_projection or precise:
                raise CatalogError("invalid_projection", "selected JSON payload is invalid") from exc
            payload = resolved["payload"].decode("utf-8", errors="replace")
            payload_format = "text"
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
        "payload_format": payload_format,
        "payload": payload,
    }
    if integrity and resolved is not None:
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
