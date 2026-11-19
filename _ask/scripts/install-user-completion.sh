#!/usr/bin/env bash
# Install shell completion only after an explicit askit completion-install.
set -euo pipefail

if [[ -z "${HOME:-}" ]]; then
  echo "askit: HOME is not set" >&2
  exit 1
fi
ASKIT_DIR="${ASKIT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
exec python3 - "$ASKIT_DIR/ask" <<'PY'
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile


def ensure_dir(path: Path) -> None:
    path = path.absolute()
    for part in reversed((path, *path.parents)):
        if part.exists() or part.is_symlink():
            if part.is_symlink() or not part.is_dir():
                raise ValueError(f"completion directory is not a real directory: {part}")
        else:
            part.mkdir(mode=0o700)
    if path.stat().st_uid != os.getuid():
        raise ValueError(f"completion directory must be owned by the current user: {path}")
    os.chmod(path, 0o700)


def checked_file(path: Path) -> int | None:
    if not path.exists() and not path.is_symlink():
        return None
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ValueError(f"completion target must be a regular file: {path}")
    if info.st_uid != os.getuid():
        raise ValueError(f"completion target must be owned by the current user: {path}")
    return stat.S_IMODE(info.st_mode)


def atomic_write(path: Path, content: bytes, mode: int) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".askit-completion-", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


try:
    home = Path(os.environ["HOME"]).absolute()
    data_home = Path(os.environ.get("XDG_DATA_HOME") or home / ".local/share").absolute()
    bash_home = Path(os.environ.get("BASH_COMPLETION_USER_DIR") or data_home / "bash-completion").absolute()
    data = data_home / "askit"
    bash_dir = bash_home / "completions"
    for directory in (data, bash_dir):
        ensure_dir(directory)

    targets = {
        data / "complete.bash": None,
        data / "complete.zsh": None,
        bash_dir / "ask": None,
        bash_dir / "askit": None,
        home / ".bashrc": None,
        home / ".zshrc": None,
    }
    for path in targets:
        targets[path] = checked_file(path)
    ask = Path(sys.argv[1])
    if not ask.is_file() or not os.access(ask, os.X_OK):
        raise ValueError("installed completion command is unavailable")
    bash = subprocess.run([str(ask), "completion", "bash"], check=True, capture_output=True).stdout
    zsh = subprocess.run([str(ask), "completion", "zsh"], check=True, capture_output=True).stdout
    hooks = {
        home / ".bashrc": b'\n# askit-completion\nif [ -f "${XDG_DATA_HOME:-$HOME/.local/share}/askit/complete.bash" ]; then\n  . "${XDG_DATA_HOME:-$HOME/.local/share}/askit/complete.bash"\nfi\n',
        home / ".zshrc": b'\n# askit-completion\nif [ -f "${XDG_DATA_HOME:-$HOME/.local/share}/askit/complete.zsh" ]; then\n  . "${XDG_DATA_HOME:-$HOME/.local/share}/askit/complete.zsh"\nfi\n',
    }
    outputs = {
        data / "complete.bash": bash,
        data / "complete.zsh": zsh,
        bash_dir / "ask": bash,
        bash_dir / "askit": bash,
    }
    for path, content in outputs.items():
        atomic_write(path, content, targets[path] or 0o600)
    for path, hook in hooks.items():
        existing = path.read_bytes() if targets[path] is not None else b""
        if b"askit-completion" not in existing:
            atomic_write(path, existing + hook, targets[path] or 0o600)
    print("askit: user completion installed")
except (OSError, ValueError, subprocess.CalledProcessError) as exc:
    print(f"askit: cannot install user completion: {exc}", file=sys.stderr)
    raise SystemExit(1)
PY
