from __future__ import annotations

import subprocess
from pathlib import Path

from inner_loop.graph import glob_to_re


def path_allowed(path: str, globs: list[str]) -> bool:
    rel = path.lstrip("./")
    return any(glob_to_re(g).match(rel) for g in globs)


def outside_paths(paths: list[str], globs: list[str]) -> list[str]:
    return [p for p in paths if not path_allowed(p, globs)]


def classify_paths(paths: list[str], globs: list[str], required: list[str]) -> str:
    outside = outside_paths(paths, globs)
    if not outside:
        return "ok"
    req = set(required)
    if any(p in req for p in outside):
        return "glob_too_narrow"
    return "extras"


def staged_paths(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    raw = proc.stdout.split(b"\0")
    return [p.decode() for p in raw if p]
