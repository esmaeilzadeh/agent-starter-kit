"""Complete, profile-aware artifact item comparison and pinned extraction."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import subprocess
from decimal import Decimal, DecimalException

from .identity import ReferenceError, parse_reference
from .profiles import get_profile

_UNSET = object()

class ComparisonError(ValueError):
    """A source cannot be completely or safely compared."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def compare_items(before, after, profile_id, before_inputs=None, after_inputs=None,
                  before_profile=_UNSET, after_profile=_UNSET):
    """Compare payloads and their complete exact dependency bindings."""
    profile = get_profile(profile_id)
    if profile is None:
        return {"status": "incomplete", "reason": "profile_unavailable"}
    if ((before_profile is not _UNSET and before_profile != profile_id)
            or (after_profile is not _UNSET and after_profile != profile_id)):
        return {"status": "incomplete", "reason": "profile_mismatch"}
    try:
        before_value = _normalize_payload(before, profile["format"])
        after_value = _normalize_payload(after, profile["format"])
        normalized_before_inputs = _normalize_inputs(before_inputs)
        normalized_after_inputs = _normalize_inputs(after_inputs)
    except (TypeError, ValueError, UnicodeError, ReferenceError, DecimalException, RecursionError) as exc:
        return {"status": "incomplete", "reason": "comparison_input_invalid", "detail": str(exc)}
    if before_value != after_value:
        return {"status": "changed", "reason": "payload_changed"}
    if normalized_before_inputs != normalized_after_inputs:
        return {"status": "changed", "reason": "input_bindings_changed"}
    return {"status": "unchanged", "reason": "payload_and_bindings_equal"}


def _unique_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError(f"non-finite JSON value: {value}")


def _normalize_payload(value, format_name):
    if format_name == "bytes":
        if isinstance(value, str):
            return value.encode("utf-8")
        if isinstance(value, bytes):
            return value
        raise TypeError("exact-byte profile requires bytes or UTF-8 text")
    if format_name != "json":
        raise ValueError(f"unsupported comparison format: {format_name}")
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    if isinstance(value, str):
        value = json.loads(value, object_pairs_hook=_unique_pairs,
                           parse_constant=_reject_constant, parse_float=Decimal,
                           parse_int=Decimal)
    return _canonical_value(value)


def _canonical_value(value):
    """Build a typed, order-independent tree without lossy float conversion."""
    if value is None:
        return ("null",)
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, str):
        return ("string", value)
    if isinstance(value, (int, Decimal)):
        number = Decimal(value)
        if not number.is_finite():
            raise ValueError("non-finite JSON number")
        sign, digits, exponent = number.as_tuple()
        digits = list(digits)
        if not any(digits):
            return ("number", 0, "0", 0)
        while len(digits) > 1 and digits[-1] == 0:
            digits.pop()
            exponent += 1
        return ("number", sign, "".join(str(digit) for digit in digits), exponent)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite JSON number")
        return _canonical_value(Decimal(repr(value)))
    if isinstance(value, list):
        return ("array", tuple(_canonical_value(item) for item in value))
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("JSON object keys must be strings")
        return ("object", tuple((key, _canonical_value(value[key])) for key in sorted(value)))
    raise ValueError(f"unsupported JSON value type: {type(value).__name__}")


def _normalize_inputs(inputs):
    if not isinstance(inputs, (list, tuple)):
        raise ValueError("complete dependency inputs must be a list")
    result = []
    for edge in inputs:
        if not isinstance(edge, dict) or set(edge) != {"reference", "role"}:
            raise ValueError("each dependency input requires exactly reference and role")
        role = edge["role"]
        if not isinstance(role, str) or not role.strip():
            raise ValueError("dependency input role must be non-empty text")
        reference = parse_reference(edge["reference"])["canonical"]
        result.append((reference, role))
    return tuple(sorted(result))


def extract_git_item(repository_root, commit, source_path, item_id, profile_id):
    """Extract one stable item from an exact immutable Git snapshot."""
    profile = get_profile(profile_id)
    if profile is None:
        return {"status": "incomplete", "reason": "profile_unavailable"}
    if not isinstance(source_path, str) or not source_path or "\\" in source_path:
        return {"status": "incomplete", "reason": "unsafe_path"}
    relative = PurePosixPath(source_path)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        return {"status": "incomplete", "reason": "unsafe_path"}
    if relative.as_posix() != source_path:
        return {"status": "incomplete", "reason": "unsafe_path"}
    if not isinstance(commit, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
        return {"status": "incomplete", "reason": "invalid_commit_id"}
    if not isinstance(item_id, str) or not item_id:
        return {"status": "incomplete", "reason": "invalid_item_id"}
    root = Path(repository_root).resolve()
    try:
        object_format = subprocess.run(["git", "rev-parse", "--show-object-format"], cwd=root,
                                       capture_output=True, text=True, check=True).stdout.strip()
        resolved = subprocess.run(["git", "rev-parse", "--verify", f"{commit}^{{commit}}"], cwd=root,
                                  capture_output=True, text=True, check=True).stdout.strip()
        expected_length = {"sha1": 40, "sha256": 64}.get(object_format)
        if expected_length is None or len(commit) != expected_length or resolved != commit:
            return {"status": "incomplete", "reason": "commit_not_full"}
        entry = subprocess.run(["git", "ls-tree", "-z", commit, "--", relative.as_posix()], cwd=root,
                               capture_output=True, check=True).stdout
        prefix = f"{commit}:{relative.as_posix()}"
        object_type = subprocess.run(["git", "cat-file", "-t", prefix], cwd=root,
                                     capture_output=True, text=True, check=True).stdout.strip()
        if object_type != "blob" or not entry:
            return {"status": "incomplete", "reason": "source_is_not_a_file"}
        mode = entry.split(b"\t", 1)[0].split(b" ", 1)[0]
        if mode not in (b"100644", b"100755"):
            return {"status": "incomplete", "reason": "source_is_not_a_regular_file"}
        raw = subprocess.run(["git", "show", f"{commit}:{relative.as_posix()}"], cwd=root,
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {"status": "incomplete", "reason": "source_unavailable"}
    if profile["format"] == "bytes":
        if item_id != "whole-file":
            return {"status": "incomplete", "reason": "item_id_unavailable"}
        return {"status": "found", "item_id": item_id, "payload": raw,
                "canonical_digest": hashlib.sha256(raw).hexdigest(),
                "source": {"commit": commit, "path": source_path}, "profile": profile_id}
    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
                              parse_constant=_reject_constant, parse_float=Decimal,
                              parse_int=Decimal)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, DecimalException, RecursionError) as exc:
        return {"status": "incomplete", "reason": "document_invalid", "detail": str(exc)}
    if not isinstance(document, dict) or not isinstance(document.get("items"), list):
        return {"status": "incomplete", "reason": "item_collection_unavailable"}
    matches = [item for item in document["items"]
               if isinstance(item, dict) and item.get("id") == item_id]
    if len(matches) > 1:
        return {"status": "incomplete", "reason": "ambiguous_item_id"}
    if not matches:
        return {"status": "absent", "item_id": item_id,
                "source": {"commit": commit, "path": relative.as_posix()}, "profile": profile_id}
    payload = matches[0]
    try:
        canonical = _normalize_payload(payload, profile["format"])
        canonical_bytes = json.dumps(canonical, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, DecimalException, RecursionError) as exc:
        return {"status": "incomplete", "reason": "item_invalid", "detail": str(exc)}
    return {"status": "found", "item_id": item_id, "payload": payload,
            "canonical_digest": hashlib.sha256(canonical_bytes).hexdigest(),
            "source": {"commit": commit, "path": relative.as_posix()}, "profile": profile_id}
