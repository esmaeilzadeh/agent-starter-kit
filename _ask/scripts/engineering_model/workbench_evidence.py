"""Read-only test source and retained execution projections for the workbench."""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess

_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True)


def _canonical_digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _safe_path(value):
    return (isinstance(value, str) and bool(value) and value != "."
            and not Path(value).is_absolute() and not PureWindowsPath(value).drive
            and "\\" not in value and "\0" not in value
            and ".." not in PurePosixPath(value).parts)


def _confined_path(root, path, boundary=None):
    """Reject symlinks in every path component and require resolved containment."""
    root = Path(root).resolve()
    path = Path(path)
    if not path.is_absolute():
        path = root / path
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return False
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        return False
    if boundary is not None and not resolved.is_relative_to(Path(boundary).resolve()):
        return False
    return True


def _commit(root, revision):
    if not isinstance(revision, str) or not revision:
        raise ValueError("source revision is missing")
    result = _git(root, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}")
    if result.returncode:
        raise ValueError("source revision is unavailable")
    return result.stdout.decode("ascii", "replace").strip()


def _blob(root, revision, relative):
    if not _safe_path(relative):
        raise ValueError("source path is unsafe")
    tree = _git(root, "ls-tree", "-z", "--full-tree", revision, "--", relative)
    if tree.returncode:
        raise ValueError("source tree is unavailable")
    entry = next((item for item in tree.stdout.split(b"\0") if item), None)
    if entry is None:
        raise FileNotFoundError("source file is missing at selected revision")
    metadata, separator, raw_path = entry.partition(b"\t")
    if not separator or os.fsdecode(raw_path) != relative:
        raise ValueError("source path is unavailable at selected revision")
    mode, kind, oid = metadata.decode("ascii", "replace").split(" ", 2)
    if kind != "blob" or mode not in {"100644", "100755"}:
        raise ValueError("source entry is unsafe (not a regular file)")
    result = _git(root, "cat-file", "blob", oid)
    if result.returncode:
        raise ValueError("source blob is unreadable")
    return result.stdout


def _selector_node(tree, selector):
    parts = selector.split(".")
    if len(parts) < 2 or any(not part for part in parts):
        raise ValueError("test selector is not a qualified module or symbol")
    module, *symbols = parts
    body = tree.body
    selected = None
    for name in symbols:
        matches = [node for node in body
                   if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                   and node.name == name]
        if len(matches) != 1:
            raise ValueError("qualified test selector does not identify one source symbol")
        selected = matches[0]
        if name != symbols[-1]:
            if not isinstance(selected, ast.ClassDef):
                raise ValueError("qualified selector traverses a non-class symbol")
            body = selected.body
    if selected is None:
        raise ValueError("qualified selector is unavailable")
    start = min([selected.lineno, *(item.lineno for item in getattr(selected, "decorator_list", []))])
    return module, selected, start, selected.end_lineno


def qualified_source(root, test, source_sha, *, current_sha=None):
    """Resolve the accepted qualified selector from exactly one Git revision."""
    root = Path(root).resolve()
    selector = test.get("case_id") if isinstance(test, dict) else None
    result = {"status": "unavailable", "selector": selector, "source_sha": None,
              "current_sha": None, "source": "", "diagnostic": "qualified source is unavailable"}
    try:
        sha = _commit(root, source_sha)
        current = _commit(root, current_sha) if current_sha is not None else None
        paths = test.get("source_paths") if isinstance(test, dict) else None
        if not isinstance(paths, list) or not paths or not isinstance(selector, str):
            raise ValueError("accepted test source or selector is missing")
        module = selector.split(".", 1)[0]
        candidates = [path for path in paths if _safe_path(path)
                      and PurePosixPath(path).stem == module]
        if not candidates and len(paths) == 1 and _safe_path(paths[0]):
            candidates = list(paths)
        if len(candidates) != 1:
            raise ValueError("qualified test module does not select one accepted source path")
        raw = _blob(root, sha, candidates[0])
        text = raw.decode("utf-8")
        tree = ast.parse(text, filename=candidates[0])
        selected_module, _node, start, end = _selector_node(tree, selector)
        if selected_module != PurePosixPath(candidates[0]).stem:
            raise ValueError("qualified selector module differs from accepted source path")
        result.update(status="current" if current is None or sha == current else "historical",
                      source_sha=sha, current_sha=current,
                      source="\n".join(text.splitlines()[start - 1:end]),
                      source_path=candidates[0], diagnostic=None)
    except (OSError, UnicodeError, ValueError, TypeError, SyntaxError, subprocess.SubprocessError) as exc:
        result["diagnostic"] = str(exc)
    return result


def execution_history(root, work_id, test, *, spec_digest, plan_digest, candidate_sha):
    """Return actual retained case outcomes, without asserting completion."""
    root = Path(root).resolve()
    result = {"status": "unavailable", "completion": "not_evaluated", "runs": [],
              "diagnostic": "retained execution evidence is unavailable"}
    if (not isinstance(work_id, str) or not _SLUG.fullmatch(work_id)
            or not isinstance(test, dict) or not isinstance(test.get("id"), str)
            or not isinstance(test.get("case_id"), str)
            or not isinstance(test.get("runner_id"), str)
            or not isinstance(test.get("source_paths"), list)):
        result["status"] = "invalid"
        result["diagnostic"] = "selected work or test identity is invalid"
        return result
    runtime = root / "work" / work_id / "traceability"
    if not _confined_path(root, runtime):
        result["status"] = "invalid"
        result["diagnostic"] = "workstream evidence root is unsafe or traverses a symlink"
        return result
    ledger_path = runtime / "executions.json"
    try:
        if not _confined_path(root, ledger_path, runtime) or not ledger_path.is_file():
            raise FileNotFoundError("retained execution ledger is missing")
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        if not isinstance(ledger, list) or any(not isinstance(entry, dict) for entry in ledger):
            raise ValueError("retained execution ledger is malformed")
        requested_candidate = _commit(root, candidate_sha)
    except (OSError, UnicodeError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        if not isinstance(exc, FileNotFoundError):
            result["status"] = "invalid"
        result["diagnostic"] = str(exc)
        return result

    for entry in ledger:
        if (entry.get("spec_digest") != spec_digest or entry.get("plan_digest") != plan_digest
                or entry.get("work_id", work_id) != work_id):
            continue
        run_id = entry.get("run_id")
        if not isinstance(run_id, str) or not _SLUG.fullmatch(run_id):
            continue
        report_path = runtime / "runs" / run_id / "results.json"
        try:
            if not _confined_path(root, report_path, runtime) or not report_path.is_file():
                raise FileNotFoundError("retained run report is missing")
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if not isinstance(report, dict):
                raise ValueError("retained run report is malformed")
            if (entry.get("digest") != _canonical_digest(report)
                    or report.get("schema") != "ask-test-results/v1"
                    or report.get("run_id") != run_id
                    or report.get("candidate_sha") != entry.get("candidate_sha")
                    or report.get("spec_digest") != spec_digest
                    or report.get("plan_digest") != plan_digest
                    or report.get("scope") != entry.get("scope")
                    or report.get("task_id") != entry.get("task_id")
                    or {run.get("phase") for run in report.get("executions", []) if isinstance(run, dict)}
                    != {entry.get("phase")}):
                raise ValueError("retained run report identity or digest is invalid")
            cases = [case for case in report.get("cases", []) if isinstance(case, dict)
                     and case.get("test_id") == test["id"]]
            exact_cases = [case for case in cases
                           if case.get("case_id") == test["case_id"]
                           and case.get("runner_id") == test["runner_id"]]
            if len(exact_cases) > 1:
                result["runs"].append({"work_id": work_id, "test_id": test["id"], "run_id": run_id,
                                       "outcome": None, "completion": "not_evaluated",
                                       "output_status": "invalid", "diagnostic": "duplicate retained case identity"})
                continue
            for case in cases:
                if (case.get("case_id") != test["case_id"]
                        or case.get("runner_id") != test["runner_id"]
                        or case.get("phase") not in {"red", "final_green"}):
                    continue
                executions = [run for run in report.get("executions", []) if isinstance(run, dict)
                              and run.get("id") == case.get("execution_id")]
                if len(executions) != 1:
                    continue
                execution = executions[0]
                row = {"work_id": work_id, "test_id": test["id"], "case_id": test["case_id"],
                       "run_id": run_id, "candidate_sha": report["candidate_sha"],
                       "spec_digest": report.get("spec_digest"),
                       "plan_digest": report.get("plan_digest"),
                       "scope": report.get("scope"), "task_id": report.get("task_id"),
                       "source_sha": case.get("source_sha"), "phase": case["phase"],
                       "outcome": case.get("outcome"), "failure_kind": case.get("failure_kind"),
                       "recorded_at": report.get("recorded_at"),
                       "recorded_at_status": "available" if report.get("recorded_at") else "unavailable",
                       "duration": case.get("duration"), "completion": "not_evaluated",
                       "duration_status": "available" if case.get("duration") is not None else "unavailable",
                       "output_artifact": case.get("output_artifact"),
                       "output_digest": case.get("output_digest"), "output_status": "invalid",
                       "diagnostic": "retained execution detail is incomplete"}
                if (execution.get("runner_id") != test["runner_id"]
                        or execution.get("source_sha") != case.get("source_sha")
                        or execution.get("phase") != case.get("phase")
                        or execution.get("output_artifact") != case.get("output_artifact")
                        or execution.get("output_digest") != case.get("output_digest")):
                    row["diagnostic"] = "case and execution identity differ"
                    result["runs"].append(row)
                    continue
                if case.get("source_sha") != report.get("candidate_sha"):
                    row["diagnostic"] = "case source revision differs from report candidate"
                    result["runs"].append(row)
                    continue
                artifact = case.get("output_artifact")
                prefix = f"work/{work_id}/traceability/runs/{run_id}/"
                if (not isinstance(artifact, str) or not artifact.startswith(prefix)
                        or not _safe_path(artifact) or case.get("output_digest") is None):
                    row["diagnostic"] = "execution log path is missing or unsafe"
                    result["runs"].append(row)
                    continue
                log_path = root / artifact
                if not _confined_path(root, log_path, runtime) or not log_path.is_file():
                    row["diagnostic"] = "execution log is missing or outside the workstream evidence root"
                    result["runs"].append(row)
                    continue
                raw_log = log_path.read_bytes()
                if hashlib.sha256(raw_log).hexdigest() != case.get("output_digest"):
                    row["diagnostic"] = "execution log digest does not match retained bytes"
                    result["runs"].append(row)
                    continue
                row.update(output_status="valid", diagnostic=None)
                source_sha = case.get("source_sha")
                source_digests = case.get("source_digests")
                if not isinstance(source_sha, str) or not isinstance(source_digests, dict):
                    row.update(output_status="invalid", diagnostic="execution source identity is missing")
                else:
                    try:
                        actual = {path: hashlib.sha256(_blob(root, source_sha, path)).hexdigest()
                                  for path in test["source_paths"] if _safe_path(path)}
                        if len(actual) != len(test["source_paths"]) or actual != source_digests:
                            row.update(output_status="invalid", diagnostic="qualified test source digest is stale")
                    except (OSError, UnicodeError, ValueError, TypeError, subprocess.SubprocessError) as exc:
                        row.update(output_status="invalid", diagnostic=str(exc))
                try:
                    selected_sources = {path: hashlib.sha256(_blob(root, requested_candidate, path)).hexdigest()
                                        for path in test["source_paths"] if _safe_path(path)}
                    head = _commit(root, "HEAD")
                    if len(selected_sources) != len(test["source_paths"]):
                        source_status = "unavailable"
                    elif selected_sources != source_digests:
                        source_status = "stale"
                    elif report.get("candidate_sha") != requested_candidate:
                        source_status = "historical"
                    elif requested_candidate != head:
                        source_status = "historical"
                    else:
                        source_status = "current"
                except (OSError, UnicodeError, ValueError, TypeError, subprocess.SubprocessError):
                    source_status = "unavailable"
                row["source_status"] = source_status
                row["applicability"] = source_status
                result["runs"].append(row)
        except (OSError, UnicodeError, ValueError, TypeError, subprocess.SubprocessError) as exc:
            result["runs"].append({"work_id": work_id, "test_id": test["id"], "run_id": run_id,
                                   "outcome": None, "completion": "not_evaluated",
                                   "output_status": "invalid", "diagnostic": str(exc)})
    result["runs"].sort(key=lambda row: (row.get("candidate_sha", ""), row["run_id"]))
    result["status"] = "available" if result["runs"] else "not_run"
    result["diagnostic"] = None if result["runs"] else "no retained execution matches this test and contract"
    return result
