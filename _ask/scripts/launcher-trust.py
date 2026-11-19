#!/usr/bin/env python3
"""Identity and explicit user trust for project code reached by askit."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
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
    "_ask/policies", "_ask/templates", "_ask/bindings",
    "_ask/ui", "_ask/tests",
    ".agents/ask", ".agents/ask.local", ".agents/verification",
    ".cursor/commands", ".cursor/skills", ".cursor/rules", ".cursor/agents",
    ".codex/agents", ".codex/skills", ".codex/commands", ".codex/rules",
    ".claude/agents", ".claude/skills", ".claude/commands",
    ".opencode/agents", ".opencode/commands", ".opencode/skills", ".opencode/rules",
    ".git/hooks",
)
SOURCE_SUFFIXES = {
    ".py", ".sh", ".bash", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx",
    ".rb", ".go", ".rs", ".java", ".c", ".h", ".cc", ".cpp", ".hpp",
    ".php", ".pl", ".lua", ".ps1", ".bat", ".cmd", ".pyc", ".scala",
    ".kt", ".kts", ".swift", ".ex", ".exs", ".erl", ".hrl", ".r", ".sql",
    ".html", ".css", ".wasm",
}
SOURCE_EXCLUDES = {".git", "__pycache__"}
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
    plan_files = [root / ".agents/verification.yaml", root / ".agents/verification.yml"]
    plan_files.extend((root / ".agents/ask/verification/presets").glob("*.yaml"))
    plan_files.extend((root / ".agents/ask/verification/presets").glob("*.yml"))
    for plan in plan_files:
        if not plan.is_file():
            continue
        for line in plan.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*(?:-\s*)?command\s*:\s*(.*)$", line)
            if not match:
                continue
            value = match.group(1).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            try:
                tokens = shlex.split(value)
            except ValueError as exc:
                raise ValueError(f"cannot inspect verification command in {plan.relative_to(root)}") from exc
            for token in tokens:
                if token.startswith("-"):
                    continue
                has_glob = any(ch in token for ch in "*?[")
                if Path(token).is_absolute():
                    candidates = glob.glob(token) if has_glob else [token]
                else:
                    candidates = sorted(root.glob(token)) if has_glob else [root / token]
                for item in candidates:
                    item = Path(item)
                    if item.is_file() or item.is_symlink():
                        try:
                            relative_path = item.relative_to(root).as_posix()
                        except ValueError:
                            relative_path = f"@verification/{item}"
                        found[relative_path] = item
    # A CheckPlan may invoke local scripts from anywhere in the checkout.
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in list(directories):
            item = current_path / name
            if item.is_symlink():
                found[item.relative_to(root).as_posix()] = item
                directories.remove(name)
            elif name in SOURCE_EXCLUDES:
                directories.remove(name)
        for filename in filenames:
            item = current_path / filename
            relative_path = item.relative_to(root).as_posix()
            if relative_path in METADATA or relative_path in found:
                continue
            if item.suffix.lower() in SOURCE_SUFFIXES or (
                not item.is_symlink() and item.stat().st_mode & 0o111
            ):
                found[relative_path] = item
    return sorted(found.items())


def _git_runtime(root: Path) -> tuple[list[tuple[str, Path]], str]:
    config = subprocess.run(
        ["git", "-C", str(root), "config", "--show-origin", "--null", "--get-regexp",
         r"^(core\.hooksPath|core\.fsmonitor|filter\..*\.(clean|smudge|process)|diff\..*\.textconv|merge\..*\.driver)$"],
        capture_output=True,
    )
    if config.returncode not in (0, 1):
        raise ValueError("cannot inspect Git execution configuration")
    configured = subprocess.run(
        ["git", "-C", str(root), "config", "--null", "--get-regexp",
         r"^(core\.fsmonitor|filter\..*\.(clean|smudge|process)|diff\..*\.textconv|merge\..*\.driver)$"],
        capture_output=True,
    )
    if configured.returncode not in (0, 1):
        raise ValueError("cannot inspect Git executable configuration")
    for item in configured.stdout.split(b"\0"):
        if not item:
            continue
        key, _, value = item.partition(b"\n")
        key_text, value_text = key.decode(errors="replace"), value.decode(errors="replace")
        if key_text == "core.fsmonitor" and value_text.lower() in {"true", "false"}:
            continue
        raise ValueError(f"cannot safely trust configured Git executable: {key_text}")
    hooks = subprocess.run(
        ["git", "-C", str(root), "config", "--path", "--get", "core.hooksPath"],
        capture_output=True, text=True,
    )
    if hooks.returncode:
        hooks = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-path", "hooks"],
            capture_output=True, text=True, check=True,
        )
    hook_dir = Path(hooks.stdout.strip())
    if not hook_dir.is_absolute():
        hook_dir = root / hook_dir
    entries = []
    if hook_dir.is_dir() and not hook_dir.is_symlink():
        for current, directories, filenames in os.walk(hook_dir, followlinks=False):
            current_path = Path(current)
            for directory in list(directories):
                item = current_path / directory
                if item.is_symlink():
                    entries.append((f"@git-hooks/{hook_dir}/{item.relative_to(hook_dir)}", item))
                    directories.remove(directory)
            for filename in filenames:
                item = current_path / filename
                entries.append((f"@git-hooks/{hook_dir}/{item.relative_to(hook_dir)}", item))
    elif hook_dir.is_symlink():
        entries.append((f"@git-hooks/{hook_dir}", hook_dir))
    return entries, hashlib.sha256(config.stdout).hexdigest()


def _tree_entries(base: Path, prefix: str) -> list[tuple[str, Path]]:
    found = []
    for current, directories, filenames in os.walk(base, followlinks=False):
        current_path = Path(current)
        for directory in list(directories):
            path = current_path / directory
            if path.is_symlink():
                found.append((f"{prefix}/{path.relative_to(base).as_posix()}", path))
                directories.remove(directory)
        for filename in filenames:
            path = current_path / filename
            found.append((f"{prefix}/{path.relative_to(base).as_posix()}", path))
    return sorted(found)


def identity(root: Path) -> dict:
    rows = []
    git_entries, config_digest = _git_runtime(root)
    pending = _entries(root) + git_entries
    expanded: set[Path] = set()
    index = 0
    while index < len(pending):
        relative, path = pending[index]
        index += 1
        info = path.lstat()
        mode = stat.S_IMODE(info.st_mode)
        if stat.S_ISLNK(info.st_mode):
            target = (path.parent / os.readlink(path)).resolve(strict=False)
            if not target.is_relative_to(root):
                raise ValueError(f"executable trust path escapes checkout: {relative}")
            kind = "symlink"
            content = os.fsencode(os.readlink(path))
            if target.is_dir() and target not in expanded:
                expanded.add(target)
                pending.extend(_tree_entries(target, f"{relative}/@target"))
            elif target.is_file():
                pending.append((f"{relative}/@target", target))
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
    rows.sort(key=lambda row: row["path"])
    payload = json.dumps(
        {"files": rows, "git_execution_config_sha256": config_digest},
        sort_keys=True, separators=(",", ":"),
    ).encode()
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


def _checked_record_directory(path: Path, *, create: bool = False) -> None:
    parts = list(reversed((path, *path.parents)))
    private = {path, path.parent, path.parent.parent}
    for part in parts:
        if part.exists() or part.is_symlink():
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise ValueError(f"trust directory must not contain symlinks: {part}")
            if part in private:
                if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
                    raise ValueError(f"trust directory must be private and user-owned: {part}")
        elif create:
            part.mkdir(mode=0o700)
        else:
            return


def _read_record(path: Path, root: Path) -> dict | None:
    _checked_record_directory(path.parent)
    if path.resolve().is_relative_to(root):
        raise ValueError("trust records must be stored outside the project")
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
    _checked_record_directory(path.parent, create=True)
    if path.parent.resolve().is_relative_to(Path(record["root"])):
        raise ValueError("trust records must be stored outside the project")
    os.chmod(path.parent, 0o700)
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
