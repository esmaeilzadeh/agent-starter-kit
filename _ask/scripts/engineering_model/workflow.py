"""Document admission around cooperating workflow actions, without long locks.

Canonical document changes belong to actions.edit. Workflow actions may change
implementation/evidence bytes, but cannot publish raw definition edits.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .actions import Refused
from . import admission as publications
from .admission import admit, load_published, validate_current
from .validation import SLUG


_active = ContextVar('engineering_workflow_admission', default={})


def _git(root, *arguments):
    return subprocess.run(['git', *arguments], cwd=root, capture_output=True, text=True)


def branch_work_id(root):
    branch = _git(root, 'rev-parse', '--abbrev-ref', 'HEAD')
    name = branch.stdout.strip() if branch.returncode == 0 else ''
    return name.split('/')[1] if name.startswith('agent/') else None


def adopted(root, work_id):
    """Read adoption markers, including deletion-resistant HEAD/runtime markers."""
    if work_id is None:
        return False
    if not isinstance(work_id, str) or not SLUG.fullmatch(work_id):
        raise Refused('EM007_WORK_ID', 'invalid workflow work-id')
    root = Path(root).resolve()
    model = root / 'work' / work_id / 'engineering-model.json'
    pointer = root / 'work' / work_id / 'traceability/model-state/current.json'
    if model.exists() or model.is_symlink() or pointer.exists() or pointer.is_symlink():
        return True
    return _git(root, 'cat-file', '-e', f'HEAD:work/{work_id}/engineering-model.json').returncode == 0


def _refuse(diagnostics):
    if diagnostics:
        first = diagnostics[0]
        refusal = Refused(first['code'], '; '.join(
            item['code']+': '+item.get('message', 'document admission refused') for item in diagnostics),
            first.get('path', '$'))
        refusal.diagnostics = diagnostics
        raise refusal


def _canonical(snapshot):
    mutable = set()
    definitions = {snapshot.model_path}
    for node in snapshot.document['nodes']:
        reference = node.get('reference')
        if reference:
            target = reference['path']
            if node['type'] in {'implementation', 'evidence', 'test_run'}:
                mutable.add(target)
            else:
                definitions.add(target)
    # All discovered closure inputs are protected unless they are explicitly
    # source/evidence targets. A canonical path never becomes mutable by alias.
    return {path: (snapshot.statuses[path], raw) for path, raw in snapshot.files.items()
            if path not in mutable or path in definitions or path.startswith('specs/')
            or Path(path).name in {'test-plan.json', 'tasks.yaml', 'engineering-model.json'}}


def _checked(root, work_id, base, base_publication, expected=None):
    current, diagnostics = validate_current(root, work_id)
    _refuse(diagnostics)
    if expected is not None and current.identity['digest'] != expected:
        raise Refused('EM007_STALE_INPUT', 'expected workflow snapshot is no longer current')
    if _canonical(current) != _canonical(base):
        if not publications.guarded_publication_chain(
                root, work_id, base.identity['digest'], current.identity['digest'],
                base_publication=base_publication):
            raise Refused('EM007_INPUT_CHANGED', 'canonical definitions changed during workflow without a verified guarded edit chain')
    return current


@contextmanager
def workflow_admission(root, work_id, expected=None):
    """Yield captured admitted inputs; publish only a valid workflow result.

    Nested calls validate at their own boundaries and share the outer snapshot
    and exact publication event. Canonical changes need a verified guarded edit
    chain from that event. Only the outermost call publishes its result. No document writer lock
    survives entry/exit admission or is held while the action/subprocess runs.
    Unadopted work yields None and acquires no validated-state label.
    """
    root = Path(root).resolve()
    if not adopted(root, work_id):
        yield None
        if adopted(root, work_id):
            _snapshot, diagnostics = validate_current(root, work_id)
            _refuse(diagnostics)
            raise Refused('EM007_INPUT_CHANGED', 'workflow cannot implicitly adopt new canonical definitions')
        return
    key = (str(root), work_id)
    active = _active.get()
    nested = key in active
    if nested:
        base, base_publication = active[key]
        captured = _checked(root, work_id, base, base_publication, expected)
    else:
        captured, diagnostics = admit(root, work_id, expected)
        _refuse(diagnostics)
        base = captured
        published = load_published(root, work_id)
        if published is None or published.identity != captured.identity:
            raise Refused('EM007_INPUT_CHANGED', 'admitted workflow generation is no longer published')
        base_publication = publications.publication_identity(root, work_id)
        confirmed = load_published(root, work_id)
        if (base_publication is None or confirmed is None or confirmed.identity != captured.identity
                or publications.publication_identity(root, work_id) != base_publication):
            raise Refused('EM007_INPUT_CHANGED', 'admitted workflow publication changed before action')
    token = _active.set({**active, key: (base, base_publication)})
    try:
        try:
            yield captured
        except BaseException:
            _checked(root, work_id, base, base_publication)
            raise
        else:
            current = _checked(root, work_id, base, base_publication)
            if not nested:
                published, diagnostics = admit(root, work_id, current.identity['digest'])
                _refuse(diagnostics)
                retained = load_published(root, work_id)
                if retained is None or retained.identity != published.identity:
                    raise Refused('EM007_INPUT_CHANGED', 'workflow result publication changed')
    finally:
        _active.reset(token)


def guarded_workflow(function):
    """Guard direct driver helpers as well as their CLI dispatchers."""
    @wraps(function)
    def guarded(root, work_id, *arguments, **options):
        with workflow_admission(root, work_id):
            return function(root, work_id, *arguments, **options)
    return guarded


def validate_candidate(root, work_id, revision):
    """Validate candidate definitions and canonical freshness before any FF/reset."""
    root = Path(root).resolve()
    if work_id is None:
        return revision
    resolved = _git(root, 'rev-parse', '--verify', revision + '^{commit}')
    if resolved.returncode:
        raise Refused('EM007_CANDIDATE', resolved.stderr.strip())
    sha = resolved.stdout.strip()
    selected = adopted(root, work_id)
    contains = _git(root, 'cat-file', '-e', f'{sha}:work/{work_id}/engineering-model.json').returncode == 0
    if not selected and not contains:
        return revision
    base = None
    if selected:
        base, diagnostics = validate_current(root, work_id)
        _refuse(diagnostics)
    with tempfile.TemporaryDirectory(prefix='ask-document-candidate-') as directory:
        checkout = Path(directory) / 'candidate'
        added = _git(root, 'worktree', 'add', '--detach', str(checkout), sha)
        if added.returncode:
            raise Refused('EM007_CANDIDATE', added.stderr.strip())
        try:
            candidate, diagnostics = validate_current(checkout, work_id)
            _refuse(diagnostics)
            if base is None or _canonical(candidate) != _canonical(base):
                raise Refused('EM007_INPUT_CHANGED', 'candidate canonical definitions require guarded publication before integration')
        finally:
            removed = _git(root, 'worktree', 'remove', '--force', str(checkout))
            if removed.returncode:
                raise Refused('EM007_CANDIDATE', removed.stderr.strip())
    return sha


def main(argv=None):
    parser = argparse.ArgumentParser(description='Internal workstream document preflight')
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--work-id', required=True)
    args = parser.parse_args(argv)
    try:
        with workflow_admission(args.root, args.work_id):
            pass
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        diagnostic = getattr(exc, 'diagnostic', {'code': 'EM007_ADMISSION', 'message': str(exc), 'path': '$'})
        print(json.dumps({'valid': False, 'diagnostics': [diagnostic]}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
