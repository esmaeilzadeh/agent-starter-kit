from __future__ import annotations

import subprocess
from pathlib import Path


class Forbidden(RuntimeError):
    pass


class Escalate(RuntimeError):
    pass


def _run(root: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=root, check=check, capture_output=True, text=True)


def integrate(root: Path, task_ref: str, method: str = "ff-only") -> str:
    if method != "ff-only":
        raise Forbidden(f"{method} onto coordinator is forbidden")
    _run(root, ["git", "merge", "--ff-only", task_ref])
    sha = _run(root, ["git", "rev-parse", "HEAD"]).stdout.strip()
    return sha


def resume(root: Path, coordinator_sha: str) -> str:
    porcelain = _run(root, ["git", "status", "--porcelain"]).stdout
    git_dir = Path(_run(root, ["git", "rev-parse", "--git-dir"]).stdout.strip())
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    in_progress = (git_dir / "MERGE_HEAD").exists() or (git_dir / "CHERRY_PICK_HEAD").exists()
    if not porcelain.strip() and not in_progress:
        return "continue"
    anc = _run(root, ["git", "merge-base", "--is-ancestor", coordinator_sha, "HEAD"], check=False)
    if anc.returncode != 0:
        raise Escalate("cannot abort to coordinator_sha; not an ancestor of HEAD")
    if in_progress:
        _run(root, ["git", "merge", "--abort"], check=False)
        _run(root, ["git", "cherry-pick", "--abort"], check=False)
    _run(root, ["git", "reset", "--hard", coordinator_sha])
    return "aborted"
