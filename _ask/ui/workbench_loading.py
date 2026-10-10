"""Integrity-bound lazy detail loading for selected workbench tests."""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
from collections import OrderedDict

from engineering_model.projection import project
from engineering_model.workbench_evidence import execution_history, qualified_source


_CACHE_LIMIT = 16


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json_digest(value) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def _safe_relative(value: str) -> bool:
    return (isinstance(value, str) and bool(value) and value != "."
            and not Path(value).is_absolute() and not PureWindowsPath(value).drive
            and "\\" not in value and "\0" not in value
            and ".." not in PurePosixPath(value).parts)


def _confined_file(root: Path, relative: str) -> Path | None:
    if not _safe_relative(relative):
        return None
    root = root.resolve()
    path = root / relative
    cursor = root
    for part in PurePosixPath(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return None
    try:
        path.resolve().relative_to(root)
    except (OSError, ValueError):
        return None
    return path


def _git(root: Path, *args: str) -> bytes | None:
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True,
                                timeout=3, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _working_source(root: Path, test: dict) -> dict:
    selector = test.get("case_id")
    result = {"status": "unavailable", "selector": selector, "source_sha": None,
              "source_path": None, "source": "", "diagnostic": "qualified source is unavailable"}
    try:
        paths = test.get("source_paths")
        if not isinstance(selector, str) or not isinstance(paths, list):
            raise ValueError("accepted source path or qualified selector is missing")
        module = selector.split(".", 1)[0]
        candidates = [path for path in paths if _safe_relative(path)
                      and PurePosixPath(path).stem == module]
        if not candidates and len(paths) == 1 and _safe_relative(paths[0]):
            candidates = list(paths)
        if len(candidates) != 1:
            raise ValueError("qualified selector does not identify one accepted source path")
        source_path = _confined_file(root, candidates[0])
        if source_path is None or not source_path.is_file():
            raise FileNotFoundError("qualified source is missing or unsafe in the working tree")
        raw = source_path.read_bytes()
        source = raw.decode("utf-8")
        tree = ast.parse(source, filename=candidates[0])
        body = tree.body
        selected = None
        parts = selector.split(".")
        if len(parts) < 2:
            raise ValueError("test selector is not fully qualified")
        for index, name in enumerate(parts[1:]):
            matches = [node for node in body
                       if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                       and node.name == name]
            if len(matches) != 1:
                raise ValueError("qualified selector does not identify one source symbol")
            selected = matches[0]
            if index != len(parts[1:]) - 1:
                if not isinstance(selected, ast.ClassDef):
                    raise ValueError("qualified selector traverses a non-class symbol")
                body = selected.body
        start = min([selected.lineno, *(node.lineno for node in selected.decorator_list)])
        result.update(status="working-tree", source_sha="working-tree:" + _sha(raw),
                      source_path=candidates[0],
                      source="\n".join(source.splitlines()[start - 1:selected.end_lineno]),
                      diagnostic=None)
    except (OSError, UnicodeError, ValueError, TypeError, SyntaxError) as exc:
        result["diagnostic"] = str(exc)
    return result


def _traceability_fingerprint(root: Path, work_id: str) -> dict:
    base = root / "work" / work_id / "traceability"
    values = {}
    if base.is_symlink() or not base.is_dir():
        return values
    for path in sorted(base.rglob("*"), key=lambda item: item.as_posix()):
        try:
            if path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            values[relative] = _sha(path.read_bytes())
        except (OSError, ValueError):
            values[path.as_posix()] = "unreadable"
    return values


def detail_identity(root: Path, snapshot, test: dict, *, source_context: dict,
                    candidate_sha: str | None = None) -> str:
    """Hash selected definitions, exact source bytes, authority refs, and evidence bytes."""
    root = Path(root).resolve()
    work_id = str(snapshot.work_id)
    plan_path = f"work/{work_id}/test-plan.json"
    plan_raw = snapshot.files.get(plan_path) or b""
    plan = {}
    try:
        plan = json.loads(plan_raw.decode("utf-8"))
    except (UnicodeError, ValueError, TypeError):
        pass
    source_items = {}
    for relative in test.get("source_paths", []):
        path = _confined_file(root, relative)
        if path is None or not path.is_file():
            source_items[str(relative)] = "unavailable"
        else:
            try:
                source_items[str(relative)] = _sha(path.read_bytes())
            except OSError:
                source_items[str(relative)] = "unreadable"
    authority = _git(root, "rev-parse", "--verify", f"refs/ask/accepted-tests/{work_id}")
    refs = _git(root, "for-each-ref", "--format=%(refname)%00%(objectname)", "refs/ask/accepted-tests")
    return _json_digest({
        "work_id": work_id,
        "snapshot": snapshot.identity,
        "test": test,
        "plan_bytes": _sha(plan_raw),
        "spec_and_plan_refs": {path: _sha(raw) for path, raw in snapshot.files.items()
                                if raw is not None and (path.startswith("specs/current/")
                                                        or path == plan_path)},
        "plan_digest": _json_digest(plan),
        "source_context": source_context,
        "candidate_sha": candidate_sha,
        "working_source_bytes": source_items if source_context.get("kind") == "working-tree" else {},
        "accepted_ref": authority.decode("ascii", "replace") if authority else None,
        "all_accepted_refs": _sha(refs) if refs else None,
        "traceability_bytes": _traceability_fingerprint(root, work_id),
    })


def load_selected_detail(root: Path, snapshot, test: dict, *, node_id: str,
                         source_context: dict, candidate_sha: str | None = None,
                         cache: OrderedDict | None = None) -> dict:
    """Load one test's qualified source and retained evidence after explicit selection."""
    root = Path(root).resolve()
    key = detail_identity(root, snapshot, test, source_context=source_context,
                          candidate_sha=candidate_sha)
    cache = cache if cache is not None else OrderedDict()
    if key in cache:
        cache.move_to_end(key)
        return cache[key]

    context_kind = source_context.get("kind", "working-tree")
    chosen_commit = source_context.get("commit") if context_kind == "git-commit" else candidate_sha
    current_head = _git(root, "rev-parse", "HEAD")
    if chosen_commit:
        source = qualified_source(root, test, str(chosen_commit),
                                  current_sha=current_head.decode("ascii", "replace") if current_head else None)
    else:
        source = _working_source(root, test)

    selected_candidate = candidate_sha or (chosen_commit.decode("ascii", "replace")
                                            if isinstance(chosen_commit, bytes) else chosen_commit)
    if selected_candidate is None and current_head:
        selected_candidate = current_head.decode("ascii", "replace")
    try:
        evidence_projection = project(snapshot, root, node_id=node_id,
                                      candidate_sha=selected_candidate, include_evidence=True)
        evidence_set = evidence_projection.get("evidence", {}).get("by_workstream", {}).get(
            snapshot.work_id, {"status": "unavailable", "diagnostic": "selected evidence is unavailable"})
    except (OSError, ValueError, KeyError, TypeError) as exc:
        evidence_projection = None
        evidence_set = {"status": "unavailable", "diagnostic": str(exc)}

    spec_path = next((path for path in snapshot.files
                      if path.startswith("specs/current/") and path.endswith(".json")), None)
    spec = snapshot.files.get(spec_path) if spec_path else None
    plan_raw = snapshot.files.get(f"work/{snapshot.work_id}/test-plan.json")
    try:
        spec_doc = json.loads(spec.decode("utf-8")) if spec else {}
    except (UnicodeError, ValueError, TypeError):
        spec_doc = {}
    try:
        plan_doc = json.loads(plan_raw.decode("utf-8")) if plan_raw else {}
    except (UnicodeError, ValueError, TypeError):
        plan_doc = {}
    try:
        history = execution_history(root, snapshot.work_id, test,
                                   spec_digest=_json_digest(spec_doc),
                                   plan_digest=_json_digest(plan_doc),
                                   candidate_sha=selected_candidate or "")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        history = {"status": "unavailable", "completion": "not_evaluated", "runs": [],
                   "diagnostic": str(exc)}
    value = {"identity": key, "source": source, "evidence_projection": evidence_projection,
             "evidence": evidence_set, "execution_history": history,
             "candidate_sha": selected_candidate, "context_kind": context_kind}
    cache[key] = value
    cache.move_to_end(key)
    while len(cache) > _CACHE_LIMIT:
        cache.popitem(last=False)
    return value


def clear_detail_cache(cache: OrderedDict | None) -> None:
    if cache is not None:
        cache.clear()
