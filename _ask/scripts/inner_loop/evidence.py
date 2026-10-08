"""Candidate-bound review and executed checks for cooperative coordinators.

Repository write access is not an authentication boundary. Workers submit history;
only coordinator operations record review decisions and execute integration checks.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from inner_loop.state import state_transaction

POLICY = '_ask/policies/delegation.md'
EXEMPTIONS = {'documentation-only', 'generated-projections', 'non-behavioral-config'}
RUNTIME_FILES = ('state.json', 'state.lock')
RUNTIME_DIRS = ('results/', 'evidence/')


class NotIntegrable(RuntimeError):
    pass


def result_path(root: Path, work_id: str, task_id: str) -> Path:
    return root / 'work' / work_id / 'inner-loop' / 'results' / f'{task_id}.json'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)
    if proc.returncode:
        raise NotIntegrable(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout.strip()


def source_changes(root: Path, work_id: str) -> list[str]:
    names = set()
    for args in [('diff', '--name-only', '-z'), ('diff', '--cached', '--name-only', '-z'),
                 ('ls-files', '--others', '--exclude-standard', '-z')]:
        proc = subprocess.run(['git', *args], cwd=root, check=True, capture_output=True, text=True)
        names.update(proc.stdout.split('\0'))
    prefix = f'work/{work_id}/inner-loop/'
    def operational(name):
        return (name in {prefix + f for f in RUNTIME_FILES}
                or name.startswith(tuple(prefix + d for d in RUNTIME_DIRS))
                or (name.startswith(prefix + '.state-') and name.endswith('.tmp')))
    return sorted(n for n in names if n and not operational(n))


def runtime_exclusions(work_id: str) -> list[str]:
    prefix = f'work/{work_id}/inner-loop/'
    return ([f':(literal,exclude){prefix}{f}' for f in RUNTIME_FILES]
            + [f':(glob,exclude){prefix}{d}**' for d in RUNTIME_DIRS]
            + [f':(glob,exclude){prefix}.state-*.tmp'])


@dataclass
class Candidate:
    result: dict
    identity: dict
    result_digest: str


def read_candidate(root: Path, work_id: str, task_id: str, doc: dict) -> Candidate:
    task = (doc.get('tasks') or {}).get(task_id)
    if not task or task.get('status') != 'running':
        raise NotIntegrable(f'task {task_id} is not running')
    path = result_path(root, work_id, task_id)
    try:
        raw = path.read_bytes()
        result = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise NotIntegrable(f'missing or invalid TaskResult {path}: {exc}') from exc
    if not isinstance(result, dict) or result.get('schema') != 'ask-task-result/v2':
        raise NotIntegrable('integration requires TaskResult ask-task-result/v2')
    if result.get('work_id') != work_id:
        raise NotIntegrable('TaskResult work_id mismatch')
    if result.get('task_id') != task_id:
        raise NotIntegrable('TaskResult task_id mismatch')
    base = task.get('base_sha') or ''
    if not base or result.get('base_sha') != base:
        raise NotIntegrable('TaskResult base_sha mismatch')
    ref = task.get('task_branch') or 'HEAD'
    sha = git(root, 'rev-parse', '--verify', f'{ref}^{{commit}}')
    if result.get('candidate_sha') != sha:
        raise NotIntegrable('TaskResult candidate_sha mismatch')
    git(root, 'merge-base', '--is-ancestor', base, sha)
    git(root, 'merge-base', '--is-ancestor', base, 'HEAD')
    git(root, 'merge-base', '--is-ancestor', 'HEAD', sha)
    return Candidate(result, {'work_id': work_id, 'task_id': task_id,
                             'base_sha': base, 'candidate_sha': sha}, digest(raw))


def check_integrable(result: dict) -> None:
    exemption = result.get('exemption')
    tdd = result.get('tdd')
    if exemption is not None:
        if (not isinstance(exemption, dict) or exemption.get('kind') not in EXEMPTIONS
                or not isinstance(exemption.get('reason'), str) or not exemption['reason'].strip()
                or exemption.get('reviewer_ack') is not True):
            raise NotIntegrable('unsupported exemption: kind, reason and reviewer_ack required')
        if tdd is not None:
            raise NotIntegrable('exemption and TDD history are mutually exclusive')
        return
    if not isinstance(tdd, dict) or not str(tdd.get('seam') or '').strip():
        raise NotIntegrable('missing TDD history/seam')
    for name in ('red', 'green'):
        step = tdd.get(name)
        if (not isinstance(step, dict) or type(step.get('exit_code')) is not int
                or not isinstance(step.get('command'), str) or not step['command'].strip()
                or not isinstance(step.get('output'), str) or not step['output'].strip()):
            raise NotIntegrable(f'{name} requires command, captured output and integer exit_code')
        if (name == 'red' and step['exit_code'] == 0) or (name == 'green' and step['exit_code'] != 0):
            raise NotIntegrable(f'{name} did not {"fail" if name == "red" else "pass"}')


def artifact(root: Path, name: str) -> tuple[str, str]:
    path = (root / name).resolve()
    try:
        relative = str(path.relative_to(root.resolve()))
        return relative, digest(path.read_bytes())
    except (OSError, ValueError) as exc:
        raise NotIntegrable(f'review/policy artifact must exist inside repository: {name}') from exc


def record_review(root: Path, work_id: str, task_id: str, reviewer: str, policy: str,
                  evidence: str, verdict: str = 'APPROVED', boundary: str = 'ok') -> dict:
    """Coordinator records an attributable delegated decision, bound to result bytes."""
    if not reviewer.strip() or policy != POLICY:
        raise NotIntegrable(f'reviewer identity and canonical policy {POLICY} required')
    if verdict not in {'APPROVED', 'REJECTED'} or boundary not in {'ok', 'extras', 'glob_too_narrow'}:
        raise NotIntegrable('invalid review verdict/boundary')
    with state_transaction(root, work_id) as doc:
        candidate = read_candidate(root, work_id, task_id, doc)
        if verdict == 'APPROVED':
            check_integrable(candidate.result)
        evidence_path, evidence_digest = artifact(root, evidence)
        _, policy_digest = artifact(root, policy)
        review = dict(candidate.identity, result_digest=candidate.result_digest,
                      reviewer=reviewer, policy=policy, policy_digest=policy_digest,
                      evidence=evidence_path, evidence_digest=evidence_digest,
                      verdict=verdict, boundary=boundary,
                      exemption_reason=(candidate.result['exemption'].get('reason')
                                        if isinstance(candidate.result.get('exemption'), dict) else None))
        doc['tasks'][task_id]['evidence']['review'] = review
    return review


def validate_review(root: Path, task: dict, candidate: Candidate) -> dict:
    review = (task.get('evidence') or {}).get('review') or {}
    expected = dict(candidate.identity, result_digest=candidate.result_digest)
    if any(review.get(k) != v for k, v in expected.items()):
        raise NotIntegrable('missing or stale coordinator-recorded review for candidate/result')
    if (review.get('verdict') != 'APPROVED' or review.get('boundary') != 'ok'
            or not str(review.get('reviewer') or '').strip() or review.get('policy') != POLICY):
        raise NotIntegrable('coordinator review must be APPROVED with boundary ok, reviewer and policy')
    for name in ('evidence', 'policy'):
        _, current = artifact(root, review[name])
        if current != review.get(name + '_digest'):
            raise NotIntegrable(f'stale review {name} artifact')
    if review.get('exemption_reason') != (candidate.result.get('exemption') or {}).get('reason'):
        raise NotIntegrable('exemption reason differs from coordinator review')
    return review


def snapshot_runner(root: Path, base_sha: str, destination: Path) -> tuple[Path, str]:
    """Pin verifier and imports to the accepted coordinator base, even in-place."""
    prefix = '.agents/ask/verification/'
    paths = git(root, 'ls-tree', '-r', '--name-only', base_sha, '--', prefix).splitlines()
    hashes = {}
    for name in paths:
        if not name.endswith('.py'):
            continue
        raw = subprocess.run(['git', 'show', f'{base_sha}:{name}'], cwd=root,
                             check=True, capture_output=True).stdout
        relative = Path(name).relative_to('.agents/ask')
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        hashes[str(relative)] = digest(raw)
    runner = destination / 'verification/run.py'
    if not runner.is_file():
        raise NotIntegrable('recorded coordinator base has no verification runner')
    return runner, digest(json.dumps(hashes, sort_keys=True).encode())


def plan_identity(checkout: Path, runner: Path) -> tuple[str, list[dict]]:
    # Resolve plans through pinned imports in a separate process. The current
    # coordinator checkout may already contain candidate changes to those files.
    code = '''
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from verification.plan import load_plan,expand_plan
root=Path(sys.argv[2]);plan=load_plan(root);checks=expand_plan(root,plan)
sources=[root/'.agents/verification.yaml']
sources += [root/'.agents/ask/verification/presets'/f'{n}.yaml' for n in plan.get('presets') or []]
data={'plan':plan,'expanded_checks':checks,
      'sources':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
print(json.dumps({'digest':hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest(),'checks':checks}))
'''
    proc = subprocess.run([sys.executable, '-c', code, str(runner.parent.parent), str(checkout)],
                          cwd=checkout, capture_output=True, text=True)
    if proc.returncode:
        raise NotIntegrable('candidate CheckPlan could not load: ' + proc.stderr.strip())
    data = json.loads(proc.stdout)
    checks = data['checks']
    if not checks or not any(c.get('tier', 'mandatory') == 'mandatory' for c in checks):
        raise NotIntegrable('empty CheckPlan or zero mandatory checks')
    return data['digest'], checks


def verify_candidate(root: Path, candidate: Candidate) -> dict:
    identity = candidate.identity
    directory = root / 'work' / identity['work_id'] / 'inner-loop' / 'evidence'
    directory.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='verify-', dir=directory))
    report = dict(identity, schema='ask-integration-evidence/v1', result='fail',
                  result_digest=candidate.result_digest, checks=[],
                  evidence_path=str((out / 'verification.json').relative_to(root)),
                  log_path=str((out / 'output.log').relative_to(root)))
    try:
        with tempfile.TemporaryDirectory(prefix='ask-candidate-') as tmp:
            runner, report['runner_digest'] = snapshot_runner(root, identity['base_sha'], Path(tmp) / 'trusted')
            report['runner_sha'] = identity['base_sha']
            checkout = Path(tmp) / 'checkout'
            git(root, 'worktree', 'add', '--detach', str(checkout), identity['candidate_sha'])
            try:
                report['tree_sha'] = git(checkout, 'rev-parse', 'HEAD^{tree}')
                report['checkplan_digest'], expected = plan_identity(checkout, runner)
                env = dict(os.environ, ASK_ROOT=str(checkout), VERIFY_JSON=str(out / 'verification.json'),
                           VERIFY_OUT_DIR=str(out))
                with (out / 'output.log').open('w') as log:
                    proc = subprocess.run([sys.executable, str(runner)],
                                          cwd=checkout, env=env, stdout=log, stderr=subprocess.STDOUT)
                try:
                    executed = json.loads((out / 'verification.json').read_bytes())
                except (OSError, ValueError) as exc:
                    raise NotIntegrable('candidate verification produced no valid result') from exc
                checks = executed.get('checks') if isinstance(executed, dict) else None
                if not isinstance(checks, list) or not all(isinstance(c, dict) for c in checks):
                    raise NotIntegrable('malformed candidate check results')
                report['checks'] = checks
                identities = lambda cs: [(c.get('id', c.get('command')), c.get('tier', 'mandatory'), c.get('command')) for c in cs]
                if (proc.returncode != 0 or executed.get('schema') != 'ask-verify-result/v1'
                        or executed.get('commit_sha') != identity['candidate_sha']
                        or executed.get('result') != 'pass' or identities(checks) != identities(expected)
                        or any(type(c.get('exit_code')) is not int or c['exit_code'] != 0
                               or c.get('status') != 'pass' for c in checks)):
                    raise NotIntegrable('required candidate verification failed or mismatched its CheckPlan')
                if (git(checkout, 'rev-parse', 'HEAD') != identity['candidate_sha']
                        or git(checkout, 'status', '--porcelain')
                        or plan_identity(checkout, runner)[0] != report['checkplan_digest']):
                    raise NotIntegrable('candidate source/CheckPlan changed during verification')
                report['result'] = 'pass'
            finally:
                git(root, 'worktree', 'remove', '--force', str(checkout))
    except (OSError, ValueError) as exc:
        raise NotIntegrable(f'candidate verification could not execute: {exc}') from exc
    finally:
        report_path = out / 'integration.json'
        report['record_path'] = str(report_path.relative_to(root))
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report
