"""Captured document inputs shared by validation, guards, and later readers.

Filesystem capture is not an atomic filesystem transaction. Admission must
validate these bytes and compare a fresh capture before publishing them.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PureWindowsPath
from types import MappingProxyType
from typing import Mapping

from .validation import RULES_VERSION, SLUG, validate


def unique_objects(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_objects)


def safe_relative(relative):
    return (isinstance(relative, str) and bool(relative) and relative != "."
            and not Path(relative).is_absolute() and not PureWindowsPath(relative).drive
            and "\\" not in relative and ".." not in Path(relative).parts)


def read_input(root, relative):
    if not safe_relative(relative):
        return "unsafe", None
    try:
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            return "outside-repository", None
        return "present", path.read_bytes()
    except FileNotFoundError:
        return "missing", None
    except RuntimeError:
        return "unresolvable", None
    except OSError:
        return "unreadable", None


def referenced_paths(document):
    if not isinstance(document, dict):
        return set()
    paths = set()
    if isinstance(document.get("nodes"), list):
        for node in document["nodes"]:
            ref = node.get("reference") if isinstance(node, dict) else None
            if isinstance(ref, dict) and isinstance(ref.get("path"), str):
                paths.add(ref["path"])
    return paths


@dataclass(frozen=True)
class Snapshot:
    work_id: str
    files: Mapping[str, bytes | None]
    statuses: Mapping[str, str]

    @property
    def model_path(self):
        return f"work/{self.work_id}/engineering-model.json"

    @property
    def document(self):
        return decode(self.files[self.model_path])

    @property
    def identity(self):
        inputs = []
        for path, status in sorted(self.statuses.items()):
            if path == self.model_path:
                continue
            record = {"path": path, "status": status}
            if self.files[path] is not None:
                record["sha256"] = hashlib.sha256(self.files[path]).hexdigest()
            inputs.append(record)
        identity = {
            "rules_version": RULES_VERSION,
            "model": {"path": self.model_path,
                      "sha256": hashlib.sha256(self.files[self.model_path]).hexdigest()},
            "inputs": inputs,
        }
        raw = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        return {"digest": hashlib.sha256(raw).hexdigest(), **identity}

    def diagnostics(self, root):
        from .canonical import diagnostics
        errors = validate(self.document, root, self.work_id, reference_bytes=self.files)
        errors.extend(diagnostics(self))
        return sorted(errors, key=lambda item: (item["path"], item["code"], item.get("ids", []), item["message"]))


def capture(root, work_id, *, model_bytes=None):
    """Read each dependency once; all subsequent validation uses these bytes."""
    if not isinstance(work_id, str) or not SLUG.fullmatch(work_id):
        raise ValueError("work_id must be a lowercase hyphenated slug")
    root = Path(root).resolve()
    model_path = f"work/{work_id}/engineering-model.json"
    if model_bytes is None:
        status, model_bytes = read_input(root, model_path)
        if status != "present":
            raise OSError(f"cannot read {model_path}: {status}")
    document = decode(model_bytes)
    files = {model_path: model_bytes}
    statuses = {model_path: "present"}
    pending = referenced_paths(document)
    while pending:
        relative = min(pending)
        pending.remove(relative)
        if relative in files:
            continue
        status, raw = read_input(root, relative)
        files[relative], statuses[relative] = raw, status
        if status != "present" or not relative.endswith(".json"):
            continue
        try:
            linked = decode(raw)
        except (UnicodeError, ValueError):
            continue
        if not isinstance(linked, dict):
            continue
        if linked.get("schema") == "ask-spec/v1":
            pending.add(str(Path(relative).with_suffix(".md")))
            feature = linked.get("feature_specification")
            if isinstance(feature, str):
                pending.add(feature)
        elif linked.get("schema") == "ask-feature-spec/v1":
            extended = linked.get("extends")
            if isinstance(extended, str):
                pending.add(extended)
        elif linked.get("schema") == "ask-test-plan/v1":
            linked_id = linked.get("work_id")
            if isinstance(linked_id, str) and SLUG.fullmatch(linked_id):
                pending.add(f"specs/current/{linked_id}.json")
                if linked.get("task_scopes"):
                    pending.add(f"work/{linked_id}/inner-loop/tasks.yaml")
    return Snapshot(work_id, MappingProxyType(files), MappingProxyType(statuses))


def is_current(snapshot, root):
    try:
        return capture(root, snapshot.work_id).identity == snapshot.identity
    except (OSError, UnicodeError, ValueError):
        return False
