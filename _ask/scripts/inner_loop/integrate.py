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


def resume(root: Path, coordinator_sha: str, preserve_paths: list[str] | None = None) -> str:
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
    if preserve_paths:
        # Abort protocol work without letting a global reset rewind/remove the
        # tracked runtime state currently protected by the coordinator lock.
        # --quit clears operation metadata but leaves index/worktree intact.
        if (git_dir / 'MERGE_HEAD').exists():
            _run(root, ['git', 'merge', '--quit'])
        if (git_dir / 'CHERRY_PICK_HEAD').exists():
            _run(root, ['git', 'cherry-pick', '--quit'])
        current = _run(root, ['git', 'rev-parse', 'HEAD']).stdout.strip()
        # update-ref leaves even an unmerged index untouched; reset --soft
        # refuses that index. Expected-old guards against concurrent ref drift.
        _run(root, ['git', 'update-ref', '-m', 'ask resume source repair', 'HEAD', coordinator_sha, current])
        _run(root, ['git', 'restore', f'--source={coordinator_sha}', '--staged', '--worktree',
                    '--', '.', *preserve_paths])
        return 'aborted'
    if in_progress:
        _run(root, ["git", "merge", "--abort"], check=False)
        _run(root, ["git", "cherry-pick", "--abort"], check=False)
    _run(root, ["git", "reset", "--hard", coordinator_sha])
    return "aborted"
