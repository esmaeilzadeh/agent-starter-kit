"""Deterministic public task summaries; raw evidence stays in local checkpoints."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from inner_loop.checkpoint import (_atomic_write, _destination, _git, read_checkpoint,
                                   CheckpointError, _resolve_state)
from inner_loop.clean import dirty_paths, runtime_path
from inner_loop.evidence import NotIntegrable, canonical_digest, git
from inner_loop.state import load_state, state_lock, _publish_state


def _pick(value: dict, keys: str) -> dict:
    return {key: value[key] for key in keys.split() if key in value}


def _versions(root: Path, checkpoint: str, name: str, raw: bytes):
    seen = set()
    candidates = [raw]
    for commit in git(root, 'log', '--first-parent', '--format=%H', checkpoint,
                      '--', 'artifacts/' + name).splitlines():
        previous = subprocess.run(['git', 'show', f'{commit}:artifacts/{name}'],
                                  cwd=root, capture_output=True)
        if previous.returncode == 0:
            candidates.append(previous.stdout)
    for content in candidates:
        digest = hashlib.sha256(content).hexdigest()
        if digest not in seen:
            seen.add(digest)
            yield content, digest


def records(root: Path, work_id: str, checkpoint: tuple) -> dict[str, bytes]:
    checkpoint_sha, state, files = checkpoint
    base = f'work/{work_id}/'
    artifacts = {n[10:]: raw for n, raw in files.items() if n.startswith('artifacts/')}
    ledger = json.loads(artifacts.get(base + 'traceability/executions.json', b'[]'))
    history = []
    cursor = checkpoint_sha
    seen = set()
    while cursor:
        if cursor in seen:
            raise CheckpointError('checkpoint cycle while rendering milestones')
        seen.add(cursor)
        manifest = json.loads(_git(root, 'show', f'{cursor}:checkpoint.json'))
        raw_state = _git(root, 'show', f'{cursor}:' + manifest['state_path'])
        history.append(_resolve_state(root, work_id, raw_state, cursor, manifest))
        cursor = manifest.get('previous_checkpoint')
    result = {}
    for task_id, task in sorted(state['tasks'].items()):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', task_id):
            raise NotIntegrable('unsafe milestone task identity')
        evidence = task.get('evidence') or {}
        runs, submissions, references, reviews = [], [], [], []
        attached = {r['run_id'] for r in evidence.get('traceability_runs', [])}
        for attempt in task.get('attempt_history', []):
            attached.update(r['run_id'] for r in (attempt.get('evidence') or {}).get('traceability_runs', []))
        for row in ledger:
            if row.get('task_id') not in (task_id, None):
                continue
            name = base + f'traceability/runs/{row["run_id"]}/results.json'
            raw = artifacts.get(name)
            if raw is None:
                raise NotIntegrable('missing retained milestone report: ' + name)
            report = json.loads(raw)
            if (canonical_digest(report) != row.get('digest')
                    or report.get('run_id') != row['run_id']
                    or report.get('candidate_sha') != row.get('candidate_sha')
                    or report.get('task_id') != row.get('task_id')):
                raise NotIntegrable('retained milestone report differs from ledger')
            runs.append({**_pick(row, 'run_id digest phase scope task_id candidate_sha spec_digest plan_digest'),
                         'attribution': 'attempt-recorded' if row['run_id'] in attached else 'historical-unattached',
                         'cases': [_pick(c, 'test_id case_id outcome failure_kind source_sha')
                                   for c in report.get('cases', [])]})
        names = {base + f'inner-loop/results/{task_id}.json'}
        names.update(n for n in artifacts if n.startswith(base + f'inner-loop/evidence/{task_id}-'))
        for attempt in [*task.get('attempt_history', []), task]:
            ev = attempt.get('evidence') or {}
            review = ev.get('review') or {}
            if review:
                reviews.append(_pick(review, 'candidate_sha base_sha result_digest reviewer verdict boundary evidence evidence_digest policy_digest'))
                if review.get('evidence'):
                    names.add(review['evidence'])
        # Retain overwritten review receipts from the checkpoint history too.
        for old_state in history:
            old_task = old_state.get('tasks', {}).get(task_id, {})
            review = (old_task.get('evidence') or {}).get('review') or {}
            if review:
                item = _pick(review, 'candidate_sha base_sha result_digest reviewer verdict boundary evidence evidence_digest policy_digest')
                if item not in reviews:
                    reviews.append(item)
        for name in sorted(names):
            raw = artifacts.get(name)
            if raw is None:
                if (name == base + f'inner-loop/results/{task_id}.json'
                        and task.get('status') != 'integrated' and not task.get('result_path')):
                    continue
                raise NotIntegrable('missing retained milestone evidence: ' + name)
            for content, fingerprint in _versions(root, checkpoint_sha, name, raw):
                references.append({'path': name, 'sha256': fingerprint})
                if name.endswith('.json'):
                    doc = json.loads(content)
                    if doc.get('schema') in {'ask-task-result/v1', 'ask-task-result/v2'}:
                        tdd = doc.get('tdd') or {}
                        submissions.append({**_pick(doc, 'candidate_sha base_sha'),
                            'sha256': fingerprint,
                            'tdd': {phase: {**_pick(tdd.get(phase) or {}, 'exit_code source_sha run_id'),
                                'continuity_reference_sha256': canonical_digest(tdd[phase]['continuity_receipt'])
                                if isinstance((tdd.get(phase) or {}).get('continuity_receipt'), dict) else None}
                                    for phase in ('red', 'green')},
                            'notes_sha256': hashlib.sha256(str(doc.get('notes', '')).encode()).hexdigest()})
        verification = evidence.get('verification') or {}
        document = {
            'schema': 'ask-task-milestone/v1', 'work_id': work_id, 'task_id': task_id,
            'status': task.get('status'), 'attempt_id': task.get('attempt_id'),
            'recovery': [_pick(r, 'source_head source_tree proposal_sha256 review_sha256 previous_checkpoint')
                         for r in state.get('recovery_adoptions', [])],
            'source_base_sha': task.get('base_sha'),
            'source_candidate_sha': verification.get('candidate_sha'),
            'attempt_history': [_pick(a, 'attempt_id attempt_number status base_sha interrupted_candidate_sha')
                                for a in task.get('attempt_history', [])],
            'runs': runs, 'submissions': submissions, 'reviews': reviews,
            'integration': _pick(verification, 'result candidate_sha resulting_sha tree_sha traceability_run_ids'),
            'supporting_artifacts': references,
        }
        name = base + f'progress/{task_id}.json'
        old = subprocess.run(['git', 'show', f'HEAD:{name}'], cwd=root, capture_output=True)
        if old.returncode == 0:
            previous = json.loads(old.stdout)
            if {k: v for k, v in previous.items() if k != 'checkpoint_sha'} == document:
                result[name] = old.stdout
                continue
        document['checkpoint_sha'] = checkpoint_sha
        result[name] = (json.dumps(document, indent=2, sort_keys=True) + '\n').encode()
    return result


def publish_milestones(root: Path, work_id: str) -> str:
    """Publish under the coordinator and index locks; exact retries finish once."""
    from inner_loop.graph import load_graph
    from inner_loop.recovery import require_safe

    root = Path(root).resolve()
    if git(root, 'symbolic-ref', '--short', 'HEAD') != f'agent/{work_id}':
        raise NotIntegrable('milestone publisher requires the coordinator work branch')
    with state_lock(root, work_id):
        state = load_state(root, work_id)
        require_safe(root, work_id, load_graph(root, work_id), state)
        if any(t.get('status') == 'running' for t in state['tasks'].values()):
            raise NotIntegrable('defer publication until integration or interruption; writer is active')
        checkpoint = read_checkpoint(root, work_id)
        if checkpoint is None or checkpoint[1] != state:
            raise NotIntegrable('milestones require matching retained state')
        head = git(root, 'rev-parse', 'HEAD')
        documents = records(root, work_id, checkpoint)
        base = state['coordinator_sha']
        interrupted = [t['attempt_history'][-1] for t in state['tasks'].values()
                       if t.get('status') == 'interrupted' and t.get('attempt_history')]
        candidates = {a['interrupted_candidate_sha'] for a in interrupted
                      if a.get('base_sha') == base and a.get('interrupted_candidate_sha')
                      and subprocess.run(['git', 'merge-base', '--is-ancestor', base, a['interrupted_candidate_sha']],
                                         cwd=root, capture_output=True).returncode == 0}
        if head in candidates:
            base = head
        elif head != base:
            parent = git(root, 'rev-parse', 'HEAD^')
            if parent in candidates:
                base = parent
        if head != base:
            if (git(root, 'rev-parse', 'HEAD^') != base
                    or set(git(root, 'diff', '--name-only', base, head).splitlines()) - documents.keys()
                    or any(_git(root, 'show', f'{head}:{n}') != raw for n, raw in documents.items())):
                raise NotIntegrable('source advanced outside an exact milestone publication; recovery adoption required')
        dirty = set(dirty_paths(root))
        if dirty - documents.keys():
            raise NotIntegrable('uncommitted or unretained paths before publication: ' + ', '.join(sorted(dirty - documents.keys())))
        staged = set(git(root, 'diff', '--cached', '--name-only').splitlines())
        for name, raw in documents.items():
            path = _destination(root, name)
            if path.exists() or path.is_symlink():
                if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o111:
                    raise NotIntegrable('unsafe milestone destination: ' + name)
            if name in dirty and (not path.is_file() or path.read_bytes() != raw):
                raise NotIntegrable('conflicting generated milestone bytes: ' + name)
            if name in staged and (_git(root, 'show', ':' + name) != raw
                                   or git(root, 'ls-files', '--stage', '--', name).split()[0] != '100644'):
                raise NotIntegrable('staged milestone differs from generated bytes')
        changed = {n: raw for n, raw in documents.items()
                   if subprocess.run(['git', 'show', f'{head}:{n}'], cwd=root, capture_output=True).stdout != raw}
        receipts = state.get('milestone_publications') or []
        if not changed and head == base and receipts and receipts[-1]['publication_sha'] == head:
            return head
        git_dir = Path(git(root, 'rev-parse', '--absolute-git-dir'))
        index = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'index'))
        lock = index.with_name(index.name + '.lock')
        if lock.is_file() and not lock.is_symlink():
            try:
                owner = json.loads(lock.read_bytes())
                stale = (owner.get('schema') == 'ask-milestone-index-lock/v1'
                         and owner.get('work_id') == work_id
                         and owner.get('checkpoint_sha') == checkpoint[0]
                         and isinstance(owner.get('pid'), int) and owner['pid'] > 0)
                if stale:
                    try:
                        os.kill(owner['pid'], 0)
                        stale = False
                    except ProcessLookupError:
                        pass
                    except PermissionError:
                        stale = False
                if stale:
                    lock.unlink()
            except (OSError, ValueError, AttributeError):
                pass
        try:
            descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise NotIntegrable('Git index is locked by another writer') from exc
        with os.fdopen(descriptor, 'w') as stream:
            json.dump({'schema': 'ask-milestone-index-lock/v1', 'pid': os.getpid(),
                       'work_id': work_id, 'checkpoint_sha': checkpoint[0]}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        owns_lock = True
        try:
            with tempfile.TemporaryDirectory(prefix='milestones-', dir=git_dir) as temp:
                alternate = Path(temp) / 'index'
                env = dict(os.environ, GIT_INDEX_FILE=str(alternate))
                def isolated(*args):
                    proc = subprocess.run(['git', *args], cwd=root, env=env, capture_output=True)
                    if proc.returncode:
                        raise NotIntegrable(proc.stderr.decode(errors='replace'))
                    return proc.stdout.decode().strip()
                isolated('read-tree', head)
                for name, raw in changed.items():
                    _atomic_write(_destination(root, name), raw)
                    blob = _git(root, 'hash-object', '-w', '--stdin', input=raw).decode().strip()
                    isolated('update-index', '--add', '--cacheinfo', f'100644,{blob},{name}')
                if os.environ.get('ASK_MILESTONE_CRASH_AT') == 'before_commit':
                    os._exit(78)
                if (git(root, 'rev-parse', 'HEAD') != head
                        or git(root, 'symbolic-ref', '--short', 'HEAD') != f'agent/{work_id}'
                        or read_checkpoint(root, work_id)[0] != checkpoint[0]
                        or set(dirty_paths(root)) - documents.keys()
                        or any(_destination(root, n).read_bytes() != raw for n, raw in documents.items())):
                    raise NotIntegrable('source or evidence changed during publication')
                published = head
                if changed:
                    tree = isolated('write-tree')
                    published = _git(root, 'commit-tree', tree, '-p', head,
                                     input=f'Record {work_id} task milestones\n'.encode()).decode().strip()
                    _git(root, 'update-ref', f'refs/heads/agent/{work_id}', published, head)
                os.replace(alternate, index)
                lock.unlink()
                owns_lock = False
                if os.environ.get('ASK_MILESTONE_CRASH_AT') == 'after_commit':
                    os._exit(77)
                receipt = {'publication_sha': published, 'source_sha': base,
                           'records': {n: hashlib.sha256(raw).hexdigest() for n, raw in documents.items()}}
                if not receipts or receipts[-1] != receipt:
                    next_state = copy.deepcopy(state)
                    next_state.setdefault('milestone_publications', []).append(receipt)
                    next_state['coordinator_sha'] = published
                    next_state['revision'] += 1
                    _publish_state(root, work_id, next_state, expected_head=published,
                                   expected_branch=f'agent/{work_id}')
                return published
        finally:
            if owns_lock:
                lock.unlink(missing_ok=True)


def migrate_runtime(root: Path, work_id: str, inventory: dict) -> list[str]:
    """Untrack an explicitly reviewed path/digest inventory, preserving bytes."""
    if git(root, 'symbolic-ref', '--short', 'HEAD') != f'agent/{work_id}':
        raise NotIntegrable('migrate runtime from the coordinator work branch')
    with state_lock(root, work_id):
        checkpoint = read_checkpoint(root, work_id)
        if checkpoint is None or inventory.get('checkpoint_sha') != checkpoint[0]:
            raise NotIntegrable('migration inventory checkpoint is stale')
        staged = set(git(root, 'diff', '--cached', '--name-only').splitlines())
        inventory_paths = inventory.get('paths', {})
        if not isinstance(inventory_paths, dict):
            raise NotIntegrable('migration requires a path/digest inventory')
        if staged - inventory_paths.keys():
            raise NotIntegrable('resolve unrelated staged changes before runtime migration')
        names = []
        for name, digest in inventory_paths.items():
            path = _destination(root, name)
            raw = checkpoint[2].get('artifacts/' + name)
            if (not runtime_path(name, work_id) or path.is_symlink() or not path.is_file()
                    or raw is None or path.read_bytes() != raw
                    or hashlib.sha256(raw).hexdigest() != digest):
                raise NotIntegrable('migration inventory differs from retained bytes: ' + name)
            if name in staged:
                if (_git(root, 'show', 'HEAD:' + name) != raw
                        or git(root, 'ls-files', '--', name)):
                    raise NotIntegrable('staged migration is not the exact retained deletion')
            elif git(root, 'ls-files', '--', name):
                names.append(name)
        if names:
            git(root, 'rm', '--cached', '--', *names)
        return names
