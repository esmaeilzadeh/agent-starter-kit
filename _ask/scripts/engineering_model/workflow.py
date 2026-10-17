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
from .validation import SCHEMA_V2, SLUG
from .passages import delivery_task_execution, required_task_passages, selected_task_node


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


def _require_task_context(snapshot, selected_task_id=None, selected_execution=None, delivery_task_id=None):
    # Nested guards use the snapshot returned by their own freshness check.
    # Preserve v1 compatibility without consulting a separate generation.
    if snapshot.document.get('schema') != SCHEMA_V2:
        selected_execution = None
    try:
        if delivery_task_id is not None:
            if selected_task_id is not None or selected_execution is not None:
                raise ValueError('delivery and product Task selectors cannot be combined')
            selected_execution = delivery_task_execution(snapshot, snapshot.work_id, delivery_task_id)
        selected = selected_task_node(snapshot, selected_task_id=selected_task_id,
                                      selected_execution=selected_execution)
    except ValueError as exc:
        raise Refused('EM015_TASK_ID', str(exc)) from exc
    if selected is not None:
        missing = required_task_passages(snapshot, selected['id'])
        if missing:
            raise Refused('EM015_CONTEXT_REQUIRED',
                          'selected Task requires unique captured spec and plan passages: '
                          + ', '.join(missing), snapshot.model_path)


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
    published = load_published(root, work_id)
    if published is None:
        raise Refused('EM007_INPUT_CHANGED', 'workflow publication is no longer available')
    if _canonical(current) != _canonical(published):
        raise Refused('EM007_INPUT_CHANGED', 'canonical definitions changed since the last guarded publication')
    publication = publications.publication_identity(root, work_id)
    if publication != base_publication:
        if not publications.guarded_publication_chain(
                root, work_id, base.identity['digest'], published.identity['digest'],
                base_publication=base_publication):
            raise Refused('EM007_INPUT_CHANGED', 'canonical definitions changed during workflow without a verified guarded edit chain')
    return current


@contextmanager
def workflow_admission(root, work_id, expected=None, *, selected_task_id=None, selected_execution=None,
                       delivery_task_id=None):
    """Yield captured admitted inputs; publish only a valid workflow result.

    Nested calls validate at their own boundaries and share the outer snapshot
    and exact publication event. Canonical changes need a verified guarded edit
    chain from that event. Only the outermost call publishes its result. No
    document writer lock survives entry/exit admission or is held while the
    action/subprocess runs.
    Unadopted work yields None and acquires no validated-state label.
    """
    root = Path(root).resolve()
    if not adopted(root, work_id):
        if selected_task_id is not None or selected_execution is not None:
            raise Refused('EM015_TASK_ID', 'selected Task requires an adopted captured Engineering Model')
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
        _require_task_context(captured, selected_task_id, selected_execution, delivery_task_id)
    else:
        captured, diagnostics = admit(root, work_id, expected, selected_task_id=selected_task_id,
                                      selected_execution=selected_execution, delivery_task_id=delivery_task_id)
        _refuse(diagnostics)
        base = captured
        published = load_published(root, work_id)
        if published is None or published.identity != captured.identity:
            raise Refused('EM007_INPUT_CHANGED', 'admitted workflow generation is no longer published')
        base_publication = publications.publication_identity(root, work_id)
        confirmed = load_published(root, work_id)
        fresh, diagnostics = validate_current(root, work_id)
        _refuse(diagnostics)
        if (base_publication is None or confirmed is None or confirmed.identity != captured.identity
                or fresh.identity != captured.identity
                or publications.publication_identity(root, work_id) != base_publication
                or not publications.guarded_publication_chain(
                    root, work_id, captured.identity['digest'], captured.identity['digest'],
                    base_publication=base_publication)):
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
        selected_task_id = options.pop('selected_task_id', None)
        selected_execution = options.pop('selected_execution', None)
        with workflow_admission(root, work_id, selected_task_id=selected_task_id,
                                selected_execution=selected_execution):
            return function(root, work_id, *arguments, **options)
    return guarded


def _validate_candidate(root, work_id, revision):
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


def validate_candidate(root, work_id, revision, *, selected_task_id=None, selected_execution=None,
                       delivery_task_id=None):
    """Run candidate checks within the same explicit selected-task guard."""
    if selected_task_id is None and selected_execution is None and delivery_task_id is None:
        if adopted(root, work_id):
            current, diagnostics = validate_current(root, work_id)
            _refuse(diagnostics)
            if current.document.get('schema') == SCHEMA_V2:
                raise Refused('EM015_TASK_ID', 'adopted v2 Task candidate validation requires explicit selected identity')
        return _validate_candidate(root, work_id, revision)
    with workflow_admission(root, work_id, selected_task_id=selected_task_id,
                            selected_execution=selected_execution, delivery_task_id=delivery_task_id):
        return _validate_candidate(root, work_id, revision)


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
