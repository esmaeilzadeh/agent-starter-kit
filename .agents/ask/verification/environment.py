"""Build caller environments for trusted, account-local verification commands."""
from pathlib import Path

BASE = {'PATH', 'HOME', 'USER', 'LOGNAME', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ', 'TMPDIR'}


def build_environment(caller=None, env_allow=(), owned=None):
    import os
    caller = caller if caller is not None else os.environ
    result = {name: caller[name] for name in BASE if name in caller}
    result.update(owned or {})
    return result


def private_directory(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def private_open(path, mode='wb'):
    return Path(path).open(mode)


def warn_tracked_logs(root):
    return None
