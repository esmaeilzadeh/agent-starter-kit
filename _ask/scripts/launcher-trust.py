#!/usr/bin/env python3
"""Identity and explicit user trust for project code reached by askit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile


# Model selections and user-facing reference text do not load executable code.
METADATA = {
    ".agents/ask.local/bindings/models.yaml",
    ".agents/ask.local/bindings/models.json",
    "_ask/bindings/models.yaml",
    "_ask/bindings/models.json",
}
RUNTIME_DIRS = (
    "_ask/scripts", "_ask/skills", "_ask/agents", "_ask/hooks",
    ".agents/ask", ".agents/ask.local", ".agents/verification",
    ".cursor/commands", ".cursor/skills", ".cursor/rules",
    ".codex/agents", ".codex/skills", ".claude/agents", ".claude/skills",
    ".opencode/agents", ".opencode/commands",
    ".git/hooks",
)
RUNTIME_FILES = (
    "ask", "askit", "AGENTS.md", "CLAUDE.md", "GEMINI.md",
    ".agents/AGENTS.md", ".agents/CLAUDE.md", ".agents/GEMINI.md",
    ".agents/verification.yaml", ".agents/verification.yml",
)


def project_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise ValueError("selected directory is not inside a Git checkout")
    root = Path(result.stdout.strip()).resolve(strict=True)
    if not (root / "ask").is_file() or not (root / "_ask").is_dir():
        raise ValueError("selected checkout is not Ask-based")
    return root


def _entries(root: Path) -> list[tuple[str, Path]]:
    found: dict[str, Path] = {}
    for name in RUNTIME_FILES:
        path = root / name
        if path.exists() or path.is_symlink():
            found[name] = path
    for relative in RUNTIME_DIRS:
        base = root / relative
        if not base.exists() and not base.is_symlink():
            continue
        if base.is_symlink():
            found[relative] = base
            continue
        if not base.is_dir():
            found[relative] = base
            continue
        for current, directories, filenames in os.walk(base, followlinks=False):
            current_path = Path(current)
            for directory in list(directories):
                item = current_path / directory
                if item.is_symlink():
                    found[item.relative_to(root).as_posix()] = item
                    directories.remove(directory)
            for filename in filenames:
                item = current_path / filename
                relative_path = item.relative_to(root).as_posix()
                if relative_path not in METADATA:
                    found[relative_path] = item
    return sorted(found.items())


def identity(root: Path) -> dict:
    rows = []
    for relative, path in _entries(root):
        info = path.lstat()
        mode = stat.S_IMODE(info.st_mode)
        if stat.S_ISLNK(info.st_mode):
            target = (path.parent / os.readlink(path)).resolve(strict=False)
            if not target.is_relative_to(root):
                raise ValueError(f"executable trust path escapes checkout: {relative}")
            kind = "symlink"
            content = os.fsencode(os.readlink(path))
        elif stat.S_ISREG(info.st_mode):
            kind = "file"
            content = path.read_bytes()
        else:
            raise ValueError(f"unsupported trust path type: {relative}")
        rows.append({
            "path": relative,
            "kind": kind,
            "mode": mode,
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {
        "root": str(root),
        "digest": hashlib.sha256(payload).hexdigest(),
        "manifest": rows,
    }


def _record_paths(root: Path) -> tuple[Path, Path]:
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    config = config.expanduser().absolute()
    for part in reversed((config, *config.parents)):
        if part.exists() and part.is_symlink():
            raise ValueError(f"trust directory contains a symlink: {part}")
    resolved = config.resolve()
    if resolved == root or root in resolved.parents:
        raise ValueError("trust records must be stored outside the project")
    directory = resolved / "askit" / "projects"
    return directory / hashlib.sha256(str(root).encode()).hexdigest(), directory


def _read_record(path: Path, root: Path) -> dict | None:
    if not path.exists():
        return None
    info = path.lstat()
    if (stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError("trust record must be a private, user-owned regular file")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("trust record is invalid") from exc
    if record.get("schema") != "askit-project-trust/v1" or record.get("root") != str(root):
        raise ValueError("trust record is invalid for this checkout")
    return record


def _store(path: Path, record: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    for parent in (path.parent, path.parent.parent):
        if parent.is_symlink() or not parent.is_dir() or parent.stat().st_uid != os.getuid():
            raise ValueError(f"trust directory must be a user-owned directory: {parent}")
        os.chmod(parent, 0o700)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise ValueError("trust record must be a regular file")
    fd, temporary = tempfile.mkstemp(prefix=".trust-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(record, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("identity", "trust", "check"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = project_root(args.root)
        current = identity(root)
        path, _ = _record_paths(root)
        if args.action == "identity":
            print(json.dumps(current, sort_keys=True))
            return 0
        if args.action == "check":
            record = _read_record(path / "trust.json", root)
            if not record or record.get("digest") != current["digest"]:
                raise ValueError(f"checkout trust is missing or changed (SHA-256 {current['digest']}); run askit trust")
            return 0
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise ValueError("run askit trust in a terminal to approve this checkout")
        print(f"Trust executable identity SHA-256 {current['digest']} for {root}?")
        if input("Trust this checkout? [y/N] ").strip().lower() not in {"y", "yes"}:
            raise ValueError("checkout trust was not granted")
        _store(path / "trust.json", {
            "schema": "askit-project-trust/v1",
            "root": str(root),
            "digest": current["digest"],
        })
        print("askit: checkout trust recorded")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"askit: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
