"""Canonical qualified numeric workflow references.

References are stable logical identities plus a positive numeric revision. A
short form is accepted only when its owner, type and parent chain are explicit.
"""
from __future__ import annotations

import re


_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_NUMBER = re.compile(r"[1-9][0-9]*\Z")
_GIT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


class ReferenceError(ValueError):
    """A reference is malformed, ambiguous, or lacks declared context."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _number(value, label="numeric identity") -> int:
    if type(value) is not int or value <= 0:
        raise ReferenceError("malformed", f"{label} must be a positive integer")
    return value


def _segment(value: str, label: str) -> int:
    if not isinstance(value, str) or not _NUMBER.fullmatch(value):
        raise ReferenceError("malformed", f"{label} must be an unpadded positive decimal")
    return int(value)


def _owner(value) -> str:
    if not isinstance(value, str) or not _SLUG.fullmatch(value):
        raise ReferenceError("malformed", "reference owner must be a lowercase work slug")
    return value


def _from_short(value: dict, context: dict) -> str:
    if set(value) != {"id", "revision"} or not isinstance(context, dict):
        raise ReferenceError("missing_context", "numeric shorthand requires only id/revision and explicit context")
    owner = _owner(context.get("owner"))
    kind = context.get("type")
    item = _number(value.get("id"))
    revision = _number(value.get("revision"), "revision")
    parents = {
        "spec": (),
        "part": ("spec",),
        "plan": ("spec",),
        "item": ("spec", "plan"),
        "task": ("spec", "plan"),
        "test": ("spec", "plan", "task"),
    }
    if kind not in parents:
        raise ReferenceError("missing_context", "unknown shorthand record type")
    required_context = {"owner", "type", *parents[kind]}
    if set(context) != required_context:
        raise ReferenceError("missing_context", "numeric shorthand context has missing or unrelated parent fields")
    ids = [_number(context.get(parent), f"{parent} parent") for parent in parents[kind]]
    if kind == "spec":
        prefix = f"{owner}/spec/{item}"
    elif kind == "part":
        prefix = f"{owner}/spec/{ids[0]}/part/{item}"
    elif kind == "plan":
        prefix = f"{owner}/spec/{ids[0]}/plan/{item}"
    elif kind == "item":
        prefix = f"{owner}/spec/{ids[0]}/plan/{ids[1]}/item/{item}"
    elif kind == "task":
        prefix = f"{owner}/spec/{ids[0]}/plan/{ids[1]}/task/{item}"
    else:
        prefix = f"{owner}/spec/{ids[0]}/plan/{ids[1]}/task/{ids[2]}/test/{item}"
    return f"{prefix}@{revision}"


def parse_reference(value, context=None):
    """Parse a canonical full reference or an explicitly contextual numeric form."""
    if isinstance(value, dict):
        value = _from_short(value, context)
    if not isinstance(value, str) or value.count("@") != 1:
        raise ReferenceError("malformed", "reference must include one numeric revision")
    path, revision_text = value.rsplit("@", 1)
    revision = _segment(revision_text, "revision")
    parts = path.split("/")
    if len(parts) < 3:
        raise ReferenceError("malformed", "reference path is incomplete")
    owner = _owner(parts[0])
    tail = parts[1:]
    kind = None
    ids: list[int] = []
    if tail[0] == "spec":
        if len(tail) < 2:
            raise ReferenceError("malformed", "spec identity is missing")
        ids.append(_segment(tail[1], "spec identity"))
        if len(tail) == 2:
            kind = "spec"
        elif len(tail) == 4 and tail[2] == "part":
            kind = "part"
            ids.append(_segment(tail[3], "part identity"))
        elif len(tail) >= 4 and tail[2] == "plan":
            ids.append(_segment(tail[3], "plan identity"))
            if len(tail) == 4:
                kind = "plan"
            elif len(tail) == 6 and tail[4] == "item":
                kind = "item"
                ids.append(_segment(tail[5], "item identity"))
            elif len(tail) >= 6 and tail[4] == "task":
                ids.append(_segment(tail[5], "task identity"))
                if len(tail) == 6:
                    kind = "task"
                elif len(tail) == 8 and tail[6] == "test":
                    kind = "test"
                    ids.append(_segment(tail[7], "test identity"))
        if kind is None:
            raise ReferenceError("malformed", "reference does not follow spec/plan/task ownership grammar")
    elif len(tail) == 4 and tail[0] == "run" and tail[2] == "log":
        kind = "log"
        ids = [_segment(tail[1], "run identity"), _segment(tail[3], "log identity")]
    elif len(tail) == 2 and _SLUG.fullmatch(tail[0]):
        kind = tail[0]
        ids = [_segment(tail[1], f"{kind} identity")]
    else:
        raise ReferenceError("malformed", "unsupported reference type or parent path")
    canonical_path = "/".join([owner, *tail])
    canonical = f"{canonical_path}@{revision}"
    logical_id = canonical_path
    return {
        "owner": owner,
        "kind": kind,
        "ids": tuple(ids),
        "revision": revision,
        "logical_id": logical_id,
        "canonical": canonical,
        "context": {"owner": owner, "type": kind},
    }


def normalize_references(values, context=None):
    if not isinstance(values, (list, tuple)):
        raise ReferenceError("malformed", "dependency references must be a list")
    return tuple(parse_reference(value, context)["canonical"] for value in values)


def reference_sort_key(value):
    parsed = parse_reference(value)
    return parsed["owner"], parsed["kind"], parsed["ids"], parsed["revision"]


def display_git_id(full_id, known_ids):
    if not isinstance(full_id, str) or not _GIT_ID.fullmatch(full_id):
        raise ReferenceError("malformed", "raw Git identity must be a full lowercase object ID")
    known = list(known_ids)
    if full_id not in known or any(not isinstance(item, str) or not _GIT_ID.fullmatch(item) for item in known):
        raise ReferenceError("missing", "raw Git identity is outside the declared inspection scope")
    if len(set(known)) != len(known):
        raise ReferenceError("ambiguous", "raw Git inspection scope contains duplicate object IDs")
    if sum(item.startswith(full_id[:8]) for item in known) > 1:
        return full_id
    for width in range(8, len(full_id) + 1):
        prefix = full_id[:width]
        if sum(item.startswith(prefix) for item in known) == 1:
            return prefix
    return full_id


def resolve_git_id(display, known_ids):
    if not isinstance(display, str) or not re.fullmatch(r"[0-9a-f]{8,64}", display):
        raise ReferenceError("malformed", "raw Git display must be an unambiguous hexadecimal prefix")
    known = list(known_ids)
    matches = [item for item in known if isinstance(item, str) and _GIT_ID.fullmatch(item) and item.startswith(display)]
    if not matches:
        raise ReferenceError("missing", "raw Git identity is outside the declared inspection scope")
    if len(matches) != 1:
        raise ReferenceError("ambiguous", "raw Git prefix matches multiple objects")
    return matches[0]
