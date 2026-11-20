"""Allow only exact retained runtime caches through the source clean gate."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from inner_loop.checkpoint import CheckpointError, _destination, read_checkpoint


def runtime_path(name: str, work_id: str) -> bool:
    prefix = f'work/{work_id}/'
    if not name.startswith(prefix):
        return False
    tail = name[len(prefix):]
    return bool(re.fullmatch(
        r'inner-loop/(?:state\.(?:json|lock)|\.state-[\w-]+\.tmp|results/[\w.-]+\.json|'
        r'evidence/verify-[\w-]+/integration\.json)|'
        r'traceability/(?:executions\.json|completion\.json|static-[a-f0-9]+\.json|'
        r'runs/[\w-]+/[\w.-]+|static-runs/[\w-]+/[\w.-]+|'
        r'model-state/[\w./-]+)', tail))


def changed_paths(root: Path, *, ignored: bool = False) -> set[str]:
    commands = [('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                ('ls-files', '--others', '--exclude-standard', '-z')]
    if ignored:
        commands.append(('ls-files', '--others', '--ignored', '--exclude-standard', '-z', '--', 'work/'))
    return {name.decode() for args in commands for name in
            subprocess.check_output(['git', *args], cwd=root).split(b'\0') if name}


def dirty_paths(root: Path) -> list[str]:
    names = changed_paths(root, ignored=True)
    # Only known runtime paths are checked among ignored files; normal ignored
    # local settings retain Git's usual behavior.
    visible = changed_paths(root)
    branch = subprocess.run(['git', 'symbolic-ref', '--short', '-q', 'HEAD'], cwd=root,
                            capture_output=True, text=True).stdout.strip()
    if not branch.startswith('agent/'):
        return sorted(visible)
    work_id = branch[6:].split('/task/', 1)[0]
    names = visible | {n for n in names if runtime_path(n, work_id)}
    staged = set(subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'],
                                        cwd=root).decode().split('\0'))
    runtime = {n for n in names - staged if runtime_path(n, work_id)}
    dirty = names - runtime
    if not runtime:
        return sorted(dirty)
    try:
        checkpoint = read_checkpoint(root, work_id)
        if checkpoint is None:
            return sorted(names)
        _, state, files = checkpoint
        cache = _destination(root, f'work/{work_id}/inner-loop/state.json')
        if cache.is_symlink() or json.loads(cache.read_bytes()) != state:
            return sorted(names)
        for name in runtime:
            path = _destination(root, name)
            valid = path.is_file() and not path.is_symlink() and not path.stat().st_mode & 0o111
            if valid and name.endswith('/inner-loop/state.lock'):
                valid = path.read_bytes() == b''
            elif valid and (name.endswith('/inner-loop/state.json') or re.search(r'/inner-loop/\.state-[\w-]+\.tmp$', name)):
                valid = json.loads(path.read_bytes()) == state
            elif valid:
                valid = files.get('artifacts/' + name) == path.read_bytes()
            if not valid:
                dirty.add(name)
    except (CheckpointError, ValueError, OSError):
        return sorted(names)
    return sorted(dirty)


def main() -> int:
    proc = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    if proc.returncode:
        print('check-clean-worktree: not a git repository', file=sys.stderr)
        return 2
    dirty = dirty_paths(Path(proc.stdout.strip()))
    if dirty:
        print('check-clean-worktree: uncommitted source or unretained runtime:', file=sys.stderr)
        print('\n'.join(dirty), file=sys.stderr)
        return 1
    print('check-clean-worktree: clean (runtime bytes retained in checkpoint)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
