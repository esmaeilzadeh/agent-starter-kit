"""Read work inventory and source blobs without changing the checkout."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess
from types import MappingProxyType


_WORK_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_BASE_PATHS = ("engineering-model.json", "inner-loop/tasks.yaml", "test-plan.json")


def _git(root, *args, check=False):
    return subprocess.run(["git", *args], cwd=root, capture_output=True)


def _text(result):
    return result.stdout.decode("utf-8", "replace")


def _default_branch(root):
    remote = _git(root, "symbolic-ref", "refs/remotes/origin/HEAD")
    if remote.returncode == 0:
        name = _text(remote).strip().split("/", 3)[-1]
        if _git(root, "show-ref", "--verify", "--quiet", f"refs/heads/{name}").returncode == 0:
            return name
    for name in ("main", "master"):
        if _git(root, "show-ref", "--verify", "--quiet", f"refs/heads/{name}").returncode == 0:
            return name
    branch = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    return _text(branch).strip() if branch.returncode == 0 else None


def _commit(root, ref):
    result = _git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
    if result.returncode:
        raise ValueError(f"cannot resolve committed source {ref!r}")
    return _text(result).strip()


def _tree_entry(root, commit, path):
    result = _git(root, "ls-tree", "-z", commit, "--", path)
    if result.returncode:
        return None
    for entry in result.stdout.split(b"\0"):
        if not entry:
            continue
        metadata, separator, raw_path = entry.partition(b"\t")
        if not separator:
            continue
        mode, kind, oid = metadata.decode("ascii", "replace").split(" ", 2)
        if os.fsdecode(raw_path) == path:
            return mode, kind, oid
    return None


def _blob(root, commit, path):
    entry = _tree_entry(root, commit, path)
    if entry is None:
        return None, "missing-blob"
    mode, kind, oid = entry
    if kind != "blob" or mode not in {"100644", "100755"}:
        return None, "unsafe-entry"
    result = _git(root, "cat-file", "blob", oid)
    if result.returncode:
        return None, "unreadable-blob"
    return result.stdout, None


def _safe_path(path):
    return (isinstance(path, str) and bool(path) and path != "."
            and not Path(path).is_absolute() and not PureWindowsPath(path).drive
            and "\\" not in path and "\0" not in path
            and ".." not in PurePosixPath(path).parts)


def _later_cards(root):
    directory = Path(root) / ".later"
    try:
        entries = sorted(directory.iterdir(), key=lambda item: os.fsencode(item.name))
    except OSError:
        return []
    cards = []
    for path in entries:
        if path.name.startswith(".") or path.name == "README.md" or path.suffix != ".md":
            continue
        try:
            if not path.is_file() or path.is_symlink():
                continue
            title = next((line[2:].strip() for line in path.read_text(
                encoding="utf-8", errors="replace").splitlines() if line.startswith("# ")), "")
        except OSError:
            title = ""
        cards.append({"slug": path.stem, "title": title, "path": f".later/{path.name}"})
    return cards


def _local_workstreams(root):
    base = Path(root) / "work"
    try:
        entries = sorted(base.iterdir(), key=lambda item: os.fsencode(item.name))
    except OSError:
        return []
    result = []
    for path in entries:
        if not _WORK_ID.fullmatch(path.name) or not path.is_dir() or path.is_symlink():
            continue
        model = path / "engineering-model.json"
        result.append({"work_id": path.name, "life": "local", "branch": None, "tip": None,
                       "model_status": "available" if model.is_file() and not model.is_symlink() else "missing",
                       "source": "working-files", "read_only": False})
    return result


def _model_status(root, commit, work_id):
    _data, error = _blob(root, commit, f"work/{work_id}/engineering-model.json")
    return "available" if error is None else "missing"


def discover_work(root):
    """Return local live/archive workstreams and checkout-local parked cards."""
    root = Path(root).resolve()
    if _git(root, "rev-parse", "--is-inside-work-tree").returncode:
        return {"git_available": False, "default_branch": None, "current_branch": None,
                "current_work_id": None, "selection_note": "Git is unavailable; local models only.",
                "workstreams": _local_workstreams(root), "later": _later_cards(root)}

    branch_result = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    current_branch = _text(branch_result).strip() if branch_result.returncode == 0 else None
    default = _default_branch(root)
    if not default:
        return {"git_available": True, "default_branch": None, "current_branch": current_branch,
                "current_work_id": None, "selection_note": "No default branch is available for archive discovery.",
                "workstreams": [], "later": _later_cards(root)}
    default_commit = _commit(root, default)

    listing = _git(root, "for-each-ref", "--format=%(refname:short)%00%(objectname)", "refs/heads/agent")
    refs = {}
    if listing.returncode == 0:
        for row in listing.stdout.splitlines():
            try:
                name, tip = row.decode("utf-8").split("\0", 1)
            except ValueError:
                continue
            parts = name.split("/")
            if len(parts) >= 2 and _WORK_ID.fullmatch(parts[1]):
                refs.setdefault(parts[1], []).append((name, tip.strip()))

    live, archived = {}, set()
    for work_id, candidates in refs.items():
        valid = []
        for name, tip in candidates:
            ancestor = _git(root, "merge-base", "--is-ancestor", name, default)
            if ancestor.returncode == 1:
                valid.append((name, tip))
        if valid:
            branch_name, tip = sorted(valid, key=lambda item: (item[0].count("/"), item[0]))[0]
            live[work_id] = (branch_name, tip)

    directories = _git(root, "ls-tree", "-d", "--name-only", f"{default_commit}:work")
    if directories.returncode == 0:
        for name in _text(directories).splitlines():
            if _WORK_ID.fullmatch(name) and name not in live:
                archived.add(name)

    rows = []
    for work_id, (branch, tip) in live.items():
        rows.append({"work_id": work_id, "life": "live", "branch": branch,
                     "tip": tip[:7], "model_status": _model_status(root, tip, work_id),
                     "source": "git-ref", "read_only": branch != current_branch})
    for work_id in sorted(archived):
        rows.append({"work_id": work_id, "life": "archived", "branch": default,
                     "tip": default_commit[:7], "model_status": _model_status(root, default_commit, work_id),
                     "source": "default-branch", "read_only": True})
    rows.sort(key=lambda item: (item["life"] != "live", item["work_id"]))

    current_work_id = None
    note = "Choose a workstream; checkout is detached or not on an agent branch."
    if current_branch and current_branch.startswith("agent/"):
        parts = current_branch.split("/")
        candidate = parts[1] if len(parts) > 1 else ""
        if candidate in refs:
            current_work_id = candidate
            note = "Selected from the checked-out agent work branch."
        else:
            note = "Checked-out agent branch has no matching local work ref."
    return {"git_available": True, "default_branch": default, "current_branch": current_branch,
            "current_work_id": current_work_id, "selection_note": note,
            "workstreams": rows, "later": _later_cards(root)}


@dataclass(frozen=True)
class SourceSnapshot:
    """Files resolved from one full commit identity; never an editable admission."""
    ref: str
    commit: str
    work_id: str
    files: object
    diagnostics: tuple
    editable: bool = False


def read_snapshot(root, ref, work_id, *, paths=()):
    """Read model, task graph, plan and requested paths from one resolved commit."""
    root = Path(root).resolve()
    if not isinstance(work_id, str) or not _WORK_ID.fullmatch(work_id):
        raise ValueError("work_id must be a lowercase hyphenated slug")
    if _git(root, "rev-parse", "--is-inside-work-tree").returncode:
        raise ValueError("cannot read committed snapshot: Git repository is unavailable")
    commit = _commit(root, ref)
    requested = [f"work/{work_id}/{name}" for name in _BASE_PATHS]
    requested.extend(paths)
    files, diagnostics = {}, []
    for path in dict.fromkeys(requested):
        if not _safe_path(path):
            diagnostics.append({"code": "unsafe-path", "path": str(path),
                                "message": "source path is unsafe and was not read"})
            continue
        data, error = _blob(root, commit, path)
        if error:
            diagnostics.append({"code": error, "path": path,
                                "message": "source is missing or is not a regular committed file"})
        else:
            files[path] = data
    model_path = f"work/{work_id}/engineering-model.json"
    if model_path not in files:
        raise ValueError(f"missing model for {work_id} at committed source {commit}")
    return SourceSnapshot(ref=str(ref), commit=commit, work_id=work_id,
                          files=MappingProxyType(files), diagnostics=tuple(diagnostics))
