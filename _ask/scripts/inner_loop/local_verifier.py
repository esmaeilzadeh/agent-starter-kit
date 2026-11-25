"""Pin installed verifier bytes to a task base without adding them to client history."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

from client_ignores import BEGIN, installed_ownership


PREFIX = ".agents/ask/verification/"
ENTRYPOINT = PREFIX + "run.py"
ADAPTERS = {PREFIX + "traceability/" + name for name in ("node_test_runner.cjs", "jest_runner.cjs")}


def executable_source(name: str) -> bool:
    return name.startswith(PREFIX) and (name.endswith(".py") or name in ADAPTERS)


def local_source(name: str) -> bool:
    path = Path(name)
    return (path.as_posix() == name and ".." not in path.parts
            and (executable_source(name) or (name.startswith(PREFIX + "presets/") and path.suffix == ".yaml")))


def git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def pin_path(root: Path, revision: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", revision):
        raise ValueError("invalid local verifier base revision")
    common = Path(git_output(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    return common / "askit-verifiers" / (revision + ".json")


def check_private(path: Path, *, directory: bool = False) -> None:
    info = path.lstat()
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError(f"unsafe local verifier state: {path}")


def read_pin(root: Path, revision: str) -> dict[str, bytes]:
    path = pin_path(root, revision)
    check_private(path.parent, directory=True)
    check_private(path)
    sources = json.loads(path.read_bytes())
    if (not isinstance(sources, dict) or ENTRYPOINT not in sources
            or any(not local_source(name) or not isinstance(content, str) for name, content in sources.items())):
        raise ValueError(f"invalid local verifier pin: {path}")
    return {name: content.encode() for name, content in sources.items()}


def pin_for_task(root: Path, revision: str) -> None:
    root = root.resolve()
    ignore = root / ".gitignore"
    if not ignore.is_file() or BEGIN not in ignore.read_bytes().splitlines():
        return
    if git_output(root, "ls-tree", "-r", "--name-only", revision, "--", PREFIX):
        return
    path = pin_path(root, revision)
    path.parent.mkdir(mode=0o700, exist_ok=True)
    check_private(path.parent, directory=True)
    if path.exists():
        read_pin(root, revision)
        return
    sources = {}
    for name, identity in installed_ownership(root).items():
        if local_source(name):
            file = root / name
            if file.resolve() != file:
                raise ValueError(f"installed verifier path contains a symlink: {name}")
            data = file.read_bytes()
            if hashlib.sha256(data).hexdigest() != identity.get("sha256"):
                raise ValueError(f"installed verifier changed since installation: {name}")
            sources[name] = data.decode()
    if ENTRYPOINT not in sources:
        raise ValueError("missing installed verifier ownership; reinstall AskIt before starting the task")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".verifier-", mode="w", encoding="utf-8") as stream:
        json.dump(sources, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
        try:
            os.link(stream.name, path)
        except FileExistsError:
            read_pin(root, revision)
