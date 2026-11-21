"""Build caller environments for trusted, account-local verification commands."""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


BASE = {'PATH', 'HOME', 'USER', 'LOGNAME', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ', 'TMPDIR'}
NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\Z')
FORBIDDEN = re.compile(r'(^BASH_FUNC_|^LD_|^DYLD_|PYTHON|TOKEN|SECRET|PASSWORD|CREDENTIAL|API_KEY|ACCESS_KEY|^ASK_|^(BASH_ENV|ENV|CDPATH|SHELLOPTS|BASHOPTS)$)', re.I)


def build_environment(caller=None, env_allow=(), owned=None):
    caller = caller if caller is not None else os.environ
    if (not isinstance(env_allow, (list, tuple))
            or any(not isinstance(name, str) for name in env_allow)
            or len(env_allow) != len(set(env_allow))):
        raise ValueError('env_allow must be a list of unique environment names')
    names = set(BASE)
    for name in env_allow:
        if not isinstance(name, str) or not NAME.fullmatch(name) or FORBIDDEN.search(name):
            raise ValueError('env_allow contains an invalid or protected environment name')
        names.add(name)
    owned = owned or {}
    if any(not isinstance(name, str) or not NAME.fullmatch(name) for name in owned):
        raise ValueError('runner metadata contains an invalid environment name')
    if set(owned) & set(env_allow):
        raise ValueError('env_allow cannot override runner-owned metadata')
    result = {name: caller[name] for name in names if name in caller}
    result.update(owned)
    return result


def private_directory(path, root=None):
    path = Path(path)
    if root is not None:
        root = Path(root).resolve()
        if not path.is_absolute():path = root / path
        path = Path(os.path.abspath(path))
        try:parts = path.relative_to(root).parts
        except ValueError as exc:raise ValueError('raw output directory escapes runtime root') from exc
        current = root
        for part in parts:
            current /= part
            if current.is_symlink():raise ValueError('raw output path contains a symlink')
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or not path.is_dir():
        raise ValueError('raw output directory is not a real directory')
    path.chmod(0o700)
    return path


def private_open(path, mode='wb'):
    path = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    os.fchmod(fd, 0o600)
    return os.fdopen(fd, mode)


def warn_tracked_logs(root):
    result = subprocess.run(['git', 'ls-files', '-z', '--', 'work'], cwd=root,
                            capture_output=True, check=True)
    if any(b'traceability/' in path and path.endswith(b'.log')
           for path in result.stdout.split(b'\0') if path):
        import sys
        print('verify: tracked legacy traceability logs need explicit cleanup; ignore rules do not untrack them.', file=sys.stderr)
