"""Captured document inputs shared by validation, guards, and later readers.

Filesystem capture is not an atomic filesystem transaction. Admission must
validate these bytes and compare a fresh capture before publishing them.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import hashlib
import json
import re
from pathlib import Path, PureWindowsPath
import subprocess
from types import MappingProxyType
from typing import Mapping

from .validation import RULES_VERSION, SLUG, validate
from .passages import (HEADING_DISCOVERY_VERSION, PLAN_TASK_DISCOVERY_VERSION,
                       RULES_VERSION as PASSAGE_RULES_VERSION, resolve)

_COMMIT = re.compile(r"^[0-9a-f]{40,64}$")
DEPENDENCY_DISCOVERY_VERSION = "engineering-input-closure/v4"
_MISSING_REVISION = object()


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
        target = root / relative
        current = root
        for part in Path(relative).parts:
            current = current / part
            if current.is_symlink():
                return "unsafe", None
        path = target.resolve()
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
            if not isinstance(node, dict):
                continue
            for field_name in ("context", "source_context"):
                values = node.get(field_name)
                if isinstance(values, list):
                    for value in values:
                        if isinstance(value, dict) and isinstance(value.get("path"), str):
                            paths.add(value["path"])
            execution = node.get("execution")
            if isinstance(execution, dict) and isinstance(execution.get("work_id"), str):
                owner = execution["work_id"]
                if SLUG.fullmatch(owner):
                    paths.add(f"work/{owner}/engineering-model.json")
            case = node.get("case")
            if (node.get("type") == "scenario" and isinstance(case, dict)
                    and isinstance(case.get("work_id"), str) and SLUG.fullmatch(case["work_id"])):
                paths.add(f"work/{case['work_id']}/test-plan.json")
    return paths


def _revision_bytes(root, relative, revision):
    if revision == "snapshot":
        return None
    if not isinstance(revision, str) or not _COMMIT.fullmatch(revision):
        raise ValueError("context revision must be 'snapshot' or a full commit ID")
    tree = subprocess.run(["git", "ls-tree", "-r", revision, "--", relative], cwd=root,
                          capture_output=True, text=True)
    if tree.returncode:
        raise ValueError("context revision is unavailable")
    records = [line.split("\t", 1)[0].split() for line in tree.stdout.splitlines()
               if "\t" in line and line.split("\t", 1)[1] == relative]
    if not records:
        return _MISSING_REVISION
    if len(records) != 1 or len(records[0]) != 3 or records[0][1] != "blob" or records[0][0] not in {"100644", "100755"}:
        raise ValueError("context revision must identify one regular committed blob")
    blob = records[0][2]
    result = subprocess.run(["git", "cat-file", "blob", blob], cwd=root, capture_output=True)
    if result.returncode:
        raise ValueError("context revision blob is unavailable")
    return result.stdout


def _context_records(document):
    records = []
    if not isinstance(document, dict) or not isinstance(document.get("nodes"), list):
        return records
    for node in document["nodes"]:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        for index, item in enumerate(node.get("context", []) if isinstance(node.get("context"), list) else []):
            if isinstance(item, dict):
                records.append((node_id, item.get("role"), index, "context", item))
        for index, item in enumerate(node.get("source_context", []) if isinstance(node.get("source_context"), list) else []):
            if isinstance(item, dict):
                records.append((node_id, item.get("role"), index, "source_context", item))
    return records


@dataclass(frozen=True)
class Snapshot:
    work_id: str
    files: Mapping[str, bytes | None]
    statuses: Mapping[str, str]
    passages: Mapping[str, dict] = field(default_factory=lambda: MappingProxyType({}))
    documents: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))
    references: Mapping[str, dict] = field(default_factory=lambda: MappingProxyType({}))
    input_errors: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    @property
    def model_path(self):
        return f"work/{self.work_id}/engineering-model.json"

    @property
    def document(self):
        if self.model_path in self.documents:
            return self.documents[self.model_path]
        return decode(self.files[self.model_path])

    @property
    def validation_reference_bytes(self):
        """Expose normalized JSON to validators while retaining raw capture bytes."""
        result = dict(self.files)
        for path, document in self.documents.items():
            if path.endswith(".json"):
                result[path] = json.dumps(document, ensure_ascii=False, sort_keys=True,
                                          separators=(",", ":")).encode("utf-8")
        return result

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
            "dependency_discovery_version": DEPENDENCY_DISCOVERY_VERSION,
            "passage_rules_version": PASSAGE_RULES_VERSION,
            "heading_discovery_version": HEADING_DISCOVERY_VERSION,
            "plan_task_discovery_version": PLAN_TASK_DISCOVERY_VERSION,
            "model": {"path": self.model_path,
                      "sha256": hashlib.sha256(self.files[self.model_path]).hexdigest()},
            "inputs": inputs,
            "passages": [
                {"key": key, "node_id": value.get("node_id"), "role": value.get("role"),
                 "kind": value.get("kind"), "path": value.get("path"),
                 "revision": value.get("revision"), "selector": value.get("selector"),
                 "status": value.get("status"), "sha256": value.get("sha256"),
                 "state": value.get("resolution", {}).get("state"),
                 "match_count": value.get("resolution", {}).get("match_count"),
                 "start_line": value.get("resolution", {}).get("start_line"),
                 "end_line": value.get("resolution", {}).get("end_line"),
                 "resolution_sha256": hashlib.sha256(json.dumps(
                     value.get("resolution"), ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode()).hexdigest()}
                for key, value in sorted(self.passages.items())
            ],
        }
        raw = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        return {"digest": hashlib.sha256(raw).hexdigest(), **identity}

    def diagnostics(self, root):
        from .canonical import diagnostics
        errors = validate(self.document, root, self.work_id,
                          reference_bytes=self.validation_reference_bytes)
        errors.extend(diagnostics(self))
        errors.extend({"code": "EM001_COMPACT_INPUT", "path": path,
                       "message": message} for path, message in self.input_errors.items())
        for key, record in self.passages.items():
            resolution = record.get("resolution", {})
            if record.get("status") in {"unsafe", "outside-repository", "unresolvable", "unreadable"}:
                errors.append({"code": "EM001_CONTEXT_REFERENCE", "path": record.get("path", "$"),
                               "message": "context path is unsafe or unreadable"})
            elif resolution.get("error"):
                errors.append({"code": "EM001_CONTEXT_SELECTOR", "path": record.get("path", "$"),
                               "message": resolution["error"]})
        return sorted(errors, key=lambda item: (item["path"], item["code"], item.get("ids", []), item["message"]))

    def resolve_passage(self, node_id, role):
        matches = [value.get("resolution") for _key, value in sorted(self.passages.items())
                   if value.get("node_id") == node_id and value.get("role") == role]
        if len(matches) != 1:
            return {"state": "unavailable", "match_count": 0, "text": None}
        return dict(matches[0])


def capture(root, work_id, *, model_bytes=None, overrides=None):
    """Read each dependency once; all subsequent validation uses these bytes."""
    if not isinstance(work_id, str) or not SLUG.fullmatch(work_id):
        raise ValueError("work_id must be a lowercase hyphenated slug")
    root = Path(root).resolve()
    overrides = overrides or {}
    def read(relative):
        if relative in overrides:
            value = overrides[relative]
            return ("present", value) if value is not None else ("missing", None)
        return read_input(root, relative)
    model_path = f"work/{work_id}/engineering-model.json"
    if model_bytes is None:
        status, model_bytes = read(model_path)
        if status != "present":
            raise OSError(f"cannot read {model_path}: {status}")
    document, model_references = _normalize_record(model_bytes)
    files = {model_path: model_bytes}
    statuses = {model_path: "present"}
    documents = {model_path: document}
    references = {model_path: model_references} if model_references else {}
    input_errors = {}
    pending = referenced_paths(document)
    while pending:
        relative = min(pending)
        pending.remove(relative)
        if relative in files:
            continue
        status, raw = read(relative)
        files[relative], statuses[relative] = raw, status
        if status != "present" or not relative.endswith(".json"):
            continue
        try:
            linked, linked_references = _normalize_record(raw)
        except (UnicodeError, ValueError, TypeError) as exc:
            if _looks_like_envelope(raw):
                input_errors[relative] = f"compact input could not be normalized: {exc}"
            continue
        documents[relative] = linked
        if linked_references:
            references[relative] = linked_references
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
            for mapping in linked.get("flow_mappings", []) if isinstance(linked.get("flow_mappings"), list) else []:
                if not isinstance(mapping, dict):
                    continue
                for selector_name in ("scenario_case", "test_case"):
                    selector = mapping.get(selector_name)
                    if isinstance(selector, dict) and selector.get("scope") == "external":
                        foreign = selector.get("work_id")
                        if isinstance(foreign, str) and SLUG.fullmatch(foreign):
                            pending.add(f"work/{foreign}/test-plan.json")
        if pending:
            # Newly discovered plan or execution-owner dependencies are read in
            # the same deterministic closure loop.
            continue
    temporary = Snapshot(work_id, MappingProxyType(files), MappingProxyType(statuses),
                         documents=MappingProxyType(documents),
                         references=MappingProxyType(references),
                         input_errors=MappingProxyType(input_errors))
    passage_records = {}
    for node_id, role, index, kind, reference in _context_records(document):
        path, revision, selector = reference.get("path"), reference.get("revision"), reference.get("selector")
        status = statuses.get(path, "missing") if isinstance(path, str) else "unsafe"
        raw = files.get(path) if isinstance(path, str) else None
        sha = hashlib.sha256(raw).hexdigest() if raw is not None else None
        resolution = None
        if kind == "context":
            try:
                historical = _revision_bytes(root, path, revision) if revision != "snapshot" else None
                if historical is _MISSING_REVISION:
                    selected_raw = None
                    passage_status = status if status in {"unsafe", "outside-repository", "unresolvable", "unreadable"} else "missing"
                else:
                    selected_raw = historical if historical is not None else raw
                    passage_status = status
                resolution = resolve(path, selected_raw, selector, status=passage_status)
                if historical is not None and historical is not _MISSING_REVISION:
                    sha = hashlib.sha256(historical).hexdigest()
                if historical is _MISSING_REVISION:
                    sha = None
                    status = passage_status
            except (OSError, UnicodeError, ValueError, TypeError) as exc:
                resolution = {"path": path, "selector": selector, "state": "error", "match_count": 0,
                              "text": None, "start_line": None, "end_line": None, "error": str(exc)}
        else:
            try:
                historical = _revision_bytes(root, path, revision) if revision != "snapshot" else None
                if historical is _MISSING_REVISION:
                    selected_raw = None
                    passage_status = status if status in {"unsafe", "outside-repository", "unresolvable", "unreadable"} else "missing"
                else:
                    selected_raw = historical if historical is not None else raw
                    passage_status = status
                selected_text = selected_raw.decode("utf-8") if selected_raw is not None else None
                resolution = {"path": path, "state": "available" if selected_text is not None else "unavailable",
                              "text": selected_text, "qualified_name": reference.get("qualified_name"),
                              "error": None}
                if historical is not None and historical is not _MISSING_REVISION:
                    sha = hashlib.sha256(historical).hexdigest()
                if historical is _MISSING_REVISION:
                    sha = None
                    status = passage_status
            except (OSError, UnicodeError, ValueError, TypeError) as exc:
                resolution = {"path": path, "state": "error", "text": None,
                              "qualified_name": reference.get("qualified_name"), "error": str(exc)}
        key = f"{node_id}:{kind}:{role}:{index}"
        passage_records[key] = {"node_id": node_id, "role": role, "kind": kind, "path": path,
                                "revision": revision, "selector": selector, "status": status,
                                "sha256": sha, "resolution": resolution}
    return Snapshot(work_id, MappingProxyType(files), MappingProxyType(statuses),
                    MappingProxyType(passage_records), MappingProxyType(documents),
                    MappingProxyType(references), MappingProxyType(input_errors))


def _looks_like_envelope(raw):
    try:
        value = decode(raw)
    except (UnicodeError, ValueError, TypeError):
        return False
    return isinstance(value, dict) and value.get("schema") == "ask-workflow-envelope/v1"


def _normalize_record(raw):
    """Decode legacy JSON or normalize one typed compact envelope."""
    value = decode(raw)
    if not isinstance(value, dict) or value.get("schema") != "ask-workflow-envelope/v1":
        return value, {}
    import sys
    workflow_refs_root = Path(__file__).resolve().parents[3] / ".agents" / "ask"
    if (workflow_refs_root / "workflow_refs").is_dir() and str(workflow_refs_root) not in sys.path:
        sys.path.insert(0, str(workflow_refs_root))
    try:
        from workflow_refs.codec import normalize_envelope
    except ImportError as exc:
        raise ValueError("compact input codec is unavailable") from exc
    normalized = normalize_envelope(value)
    payload = normalized["payload"]
    if (not isinstance(payload, dict) or payload.get("schema") != normalized["schema"]):
        raise ValueError("compact payload schema does not match its normalized document")
    return payload, normalized["references"]


def is_current(snapshot, root):
    try:
        return capture(root, snapshot.work_id).identity == snapshot.identity
    except (OSError, UnicodeError, ValueError):
        return False
