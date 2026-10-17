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
from engineering_model.evidence import inspect as inspect_workstream_evidence
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
                      source_file_digest=_sha(raw),
                      source="\n".join(source.splitlines()[start - 1:selected.end_lineno]),
                      diagnostic=None)
    except (OSError, UnicodeError, ValueError, TypeError, SyntaxError) as exc:
        result["diagnostic"] = str(exc)
    return result


def _accepted_source_digests(root: Path, test: dict,
                             revision: str | None = None) -> dict[str, str] | None:
    """Hash every declared source file, requiring confined regular files/blobs."""
    selector = test.get("case_id") if isinstance(test, dict) else None
    paths = test.get("source_paths") if isinstance(test, dict) else None
    if not isinstance(selector, str) or not isinstance(paths, list) or not paths:
        return None
    if any(not _safe_relative(path) for path in paths) or len(paths) != len(set(paths)):
        return None
    results = {}
    if revision is None:
        for relative in paths:
            path = _confined_file(root, relative)
            if path is None:
                return None
            try:
                if not path.is_file():
                    return None
                results[relative] = _sha(path.read_bytes())
            except OSError:
                return None
        return results
    try:
        checked = subprocess.run(["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
                                 cwd=root, capture_output=True, timeout=3, check=False)
        if checked.returncode:
            return None
        commit = checked.stdout.decode("ascii").strip()
        for relative in paths:
            listing = subprocess.run(["git", "ls-tree", "-z", commit, "--", relative],
                                     cwd=root, capture_output=True, timeout=3, check=False)
            if listing.returncode:
                return None
            entries = [item for item in listing.stdout.split(b"\0") if item]
            if len(entries) != 1 or b"\t" not in entries[0]:
                return None
            metadata, listed_path = entries[0].split(b"\t", 1)
            fields = metadata.split()
            if (listed_path.decode("utf-8", "strict") != relative or len(fields) != 3
                    or fields[0] not in {b"100644", b"100755"} or fields[1] != b"blob"):
                return None
            blob = subprocess.run(["git", "cat-file", "blob", fields[2].decode("ascii")],
                                  cwd=root, capture_output=True, timeout=3, check=False)
            if blob.returncode:
                return None
            results[relative] = _sha(blob.stdout)
        return results
    except (OSError, UnicodeError, subprocess.TimeoutExpired):
        return None


def _traceability_fingerprint(root: Path, work_id: str) -> dict:
    """Fingerprint runtime evidence, excluding generated admission and static logs."""
    base = root / "work" / work_id / "traceability"
    values = {}
    if base.is_symlink() or not base.is_dir():
        return values
    paths = [base / "completion.json", base / "executions.json"]
    for directory in (base / "runs", base / "reviews"):
        if directory.is_symlink():
            values[directory.relative_to(root).as_posix()] = "unsafe-symlink"
            continue
        if directory.is_dir():
            paths.extend(directory.rglob("*"))
    for path in sorted(paths, key=lambda item: item.as_posix()):
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
    current = _git(root, "rev-parse", "HEAD")
    current_head = current.decode("ascii", "replace") if current else None
    if candidate_sha is None:
        candidate_sha = current_head
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
        "current_head": current_head,
        "working_source_bytes": source_items if source_context.get("kind") == "working-tree" else {},
        "accepted_ref": authority.decode("ascii", "replace") if authority else None,
        "all_accepted_refs": _sha(refs) if refs else None,
        "traceability_bytes": _traceability_fingerprint(root, work_id),
    })


def historical_contract_candidates(root: Path, work_id: str) -> list[str]:
    """Return retained candidate identities without inspecting their full evidence."""
    ledger_path = _confined_file(root, f"work/{work_id}/traceability/executions.json")
    if ledger_path is None or not ledger_path.is_file():
        return []
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, TypeError):
        return []
    if not isinstance(ledger, list):
        return []
    return sorted({entry.get("candidate_sha") for entry in ledger
                   if isinstance(entry, dict) and entry.get("work_id", work_id) == work_id
                   and isinstance(entry.get("candidate_sha"), str)
                   and len(entry["candidate_sha"]) == 40})


def _historical_contract_evidence(root: Path, work_id: str, test: dict,
                                  candidate_shas: list[str] | None = None) -> list[dict]:
    """Inspect prior accepted contracts for the exact selected test identity."""
    ledger_path = _confined_file(root, f"work/{work_id}/traceability/executions.json")
    if ledger_path is None or not ledger_path.is_file():
        return []
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, TypeError):
        return []
    if not isinstance(ledger, list):
        return []
    candidates = historical_contract_candidates(root, work_id)
    if candidate_shas is not None:
        candidates = [candidate for candidate in candidates if candidate in set(candidate_shas)]
    records = {}
    for candidate in candidates:
        try:
            inspected = inspect_workstream_evidence(root, work_id, candidate)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            inspected = {"status": "unavailable", "diagnostic": str(exc), "scenarios": []}
        completion = inspected.get("completion", {})
        record = records.setdefault(candidate, {
            "candidate_sha": candidate,
            "inspection_status": inspected.get("status", "unavailable"),
            "inspection_diagnostic": inspected.get("diagnostic"),
            "criterion_id": "unavailable",
            "spec_digest": completion.get("input_digests", {}).get("spec", "unavailable"),
            "plan_digest": completion.get("input_digests", {}).get("plan", "unavailable"),
            "identity_status": "not_checked",
            "executions": [],
        })
        if inspected.get("status") != "historical":
            if not record.get("inspection_diagnostic"):
                errors = completion.get("errors") if isinstance(completion, dict) else None
                record["inspection_diagnostic"] = "; ".join(map(str, errors)) if errors else None
            continue
        record["identity_status"] = "no_match"
        for scenario in inspected.get("scenarios", []):
            evidence = scenario.get("evidence") or {}
            matching_plan_tests = [planned for planned in scenario.get("tests", [])
                                   if planned.get("id") == test.get("id")
                                   and planned.get("case_id") == test.get("case_id")
                                   and planned.get("runner_id") == test.get("runner_id")]
            if len(matching_plan_tests) != 1:
                continue
            record["identity_status"] = "matched"
            record["criterion_id"] = scenario.get("criterion_id", "unavailable")
            for historical_test in evidence.get("tests", []):
                if (historical_test.get("test_id") != test.get("id")
                        or historical_test.get("case_id") != test.get("case_id")):
                    continue
                for phase, key in (("red", "red"), ("final_green", "final_execution")):
                    outcomes = historical_test.get(key, []) if key == "red" else [historical_test.get(key)]
                    for outcome in outcomes:
                        if not isinstance(outcome, dict):
                            continue
                        record["executions"].append({
                            "phase": outcome.get("phase", phase),
                            "execution": outcome,
                        })
    for record in records.values():
        record["executions"].sort(key=lambda item: (item["phase"],
                                                    item["execution"].get("execution_id", "")))
    return [records[candidate] for candidate in sorted(records)]


def inspect_historical_contract_candidate(root: Path, work_id: str, test: dict,
                                          candidate_sha: str) -> list[dict]:
    """Inspect one explicitly selected retained candidate through the authority service."""
    return _historical_contract_evidence(root, work_id, test, [candidate_sha])


def load_selected_detail(root: Path, snapshot, test: dict, *, node_id: str,
                         source_context: dict, candidate_sha: str | None = None,
                         cache: OrderedDict | None = None) -> dict:
    """Load one test's qualified source and retained evidence after explicit selection."""
    root = Path(root).resolve()
    context_kind = source_context.get("kind", "working-tree")
    current_head = _git(root, "rev-parse", "HEAD")
    evidence_candidate = source_context.get("commit") if context_kind == "git-commit" else candidate_sha
    if evidence_candidate is None and current_head:
        evidence_candidate = current_head.decode("ascii", "replace")
    if isinstance(evidence_candidate, bytes):
        evidence_candidate = evidence_candidate.decode("ascii", "replace")
    selected_candidate = evidence_candidate
    key = detail_identity(root, snapshot, test, source_context=source_context,
                          candidate_sha=selected_candidate)
    cache = cache if cache is not None else OrderedDict()
    if key in cache:
        cache.move_to_end(key)
        return cache[key]

    if context_kind == "git-commit" and selected_candidate:
        source = qualified_source(root, test, str(selected_candidate),
                                  current_sha=current_head.decode("ascii", "replace") if current_head else None)
    else:
        source = _working_source(root, test)

    try:
        if selected_candidate is None:
            raise ValueError("Git candidate is unavailable")
        evidence_projection = project(snapshot, root, node_id=node_id,
                                      candidate_sha=selected_candidate, include_evidence=True)
        evidence_set = evidence_projection.get("evidence", {}).get("by_workstream", {}).get(
            snapshot.work_id, {"status": "unavailable", "diagnostic": "selected evidence is unavailable"})
    except (OSError, ValueError, KeyError, TypeError) as exc:
        evidence_projection = None
        evidence_set = {"status": "unavailable", "diagnostic": str(exc)}
    if evidence_projection is None:
        try:
            evidence_set = inspect_workstream_evidence(root, snapshot.work_id, selected_candidate)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            evidence_set = {"status": "unavailable", "diagnostic": str(exc)}
    if selected_candidate is None and evidence_set.get("status") == "unavailable":
        evidence_set = dict(evidence_set)
        evidence_set["diagnostic"] = "Git evidence inspection is unavailable because this model root has no resolvable Git candidate."

    plan_raw = snapshot.files.get(f"work/{snapshot.work_id}/test-plan.json")
    try:
        plan_doc = json.loads(plan_raw.decode("utf-8")) if plan_raw else {}
    except (UnicodeError, ValueError, TypeError):
        plan_doc = {}
    expected_spec_digest = plan_doc.get("spec_digest") if isinstance(plan_doc, dict) else None
    spec_doc = {}
    canonical_path = f"specs/current/{snapshot.work_id}.json"
    candidates = [canonical_path, *(path for path in sorted(snapshot.files)
                                    if path.startswith("specs/current/") and path.endswith(".json")
                                    and path != canonical_path)]
    for spec_path in candidates:
        raw = snapshot.files.get(spec_path)
        try:
            candidate = json.loads(raw.decode("utf-8")) if raw else {}
        except (UnicodeError, ValueError, TypeError):
            continue
        if (isinstance(candidate, dict) and candidate.get("schema") == "ask-spec/v1"
                and (not expected_spec_digest or _json_digest(candidate) == expected_spec_digest)):
            spec_doc = candidate
            break
    try:
        history = execution_history(root, snapshot.work_id, test,
                                   spec_digest=_json_digest(spec_doc),
                                   plan_digest=_json_digest(plan_doc),
                                   candidate_sha=selected_candidate or "")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        history = {"status": "unavailable", "completion": "not_evaluated", "runs": [],
                   "diagnostic": str(exc)}
    # Backend source currency is evaluated against the selected Git candidate.
    # Keep that verdict separate from whether the retained source bytes match
    # the exact test method currently shown in this detail panel.
    selected_source_digests = _accepted_source_digests(
        root, test, str(selected_candidate) if context_kind == "git-commit" and selected_candidate else None)
    for run in history.get("runs", []):
        applicability = "unavailable"
        retained_sha = run.get("source_sha") if isinstance(run, dict) else None
        retained_source_digests = _accepted_source_digests(root, test, retained_sha) if retained_sha else None
        if selected_source_digests and retained_source_digests:
            applicability = ("matches selected source" if retained_source_digests == selected_source_digests
                             else "differs from selected source")
        if isinstance(run, dict):
            run["working_source_applicability"] = applicability
    historical_candidates = (historical_contract_candidates(root, snapshot.work_id)
                             if not history.get("runs") else [])
    value = {"identity": key, "source": source, "evidence_projection": evidence_projection,
             "evidence": evidence_set, "execution_history": history,
             "historical_candidates": historical_candidates,
             "historical_contracts": [],
             "candidate_sha": selected_candidate, "context_kind": context_kind}
    cache[key] = value
    cache.move_to_end(key)
    while len(cache) > _CACHE_LIMIT:
        cache.popitem(last=False)
    return value


def clear_detail_cache(cache: OrderedDict | None) -> None:
    if cache is not None:
        cache.clear()
