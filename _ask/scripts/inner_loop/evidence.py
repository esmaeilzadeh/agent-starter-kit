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


def _commit_is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ['git', 'merge-base', '--is-ancestor', ancestor, descendant], cwd=root,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def _candidate_in_task_lineage(root: Path, task: dict, candidate: str) -> bool:
    """Accept current in-place work or the selected task branch before its FF."""
    if _commit_is_ancestor(root, candidate, git(root, 'rev-parse', 'HEAD')):
        return True
    branch = task.get('task_branch')
    if not isinstance(branch, str) or not branch or branch.startswith('-'):
        return False
    tip = subprocess.run(['git', 'rev-parse', '--verify', f'refs/heads/{branch}^{{commit}}'],
                         cwd=root, capture_output=True, text=True)
    return (tip.returncode == 0
            and _commit_is_ancestor(root, candidate, tip.stdout.strip()))


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
                or (name.startswith(prefix + '.state-') and name.endswith('.tmp'))
                or name.startswith(f'work/{work_id}/traceability/')
                or name == f'work/{work_id}/result.json')
    return sorted(n for n in names if n and not operational(n))


def runtime_exclusions(work_id: str) -> list[str]:
    prefix = f'work/{work_id}/inner-loop/'
    return ([f':(literal,exclude){prefix}{f}' for f in RUNTIME_FILES]
            + [f':(glob,exclude){prefix}{d}**' for d in RUNTIME_DIRS]
            + [f':(glob,exclude){prefix}.state-*.tmp']
            + [f':(glob,exclude)work/{work_id}/traceability/**',f':(literal,exclude)work/{work_id}/result.json'])


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


def _execution_row(root: Path, work_id: str, task_id: str, run_id: str) -> tuple[dict, dict]:
    """Validate one complete task run and return its report and canonical ledger row."""
    import re
    if not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', run_id):
        raise NotIntegrable('invalid traceability run ID')
    sys.path.insert(0, str(root / '.agents' / 'ask'))
    from verification.traceability.evidence import load_accepted
    from verification.traceability.coverage import scoped_tests
    from verification.traceability.contracts import digest as contract_digest
    from verification.traceability.contracts import file_digest

    state = None
    from inner_loop.state import load_state
    state = load_state(root, work_id)
    task = (state.get('tasks') or {}).get(task_id) or {}
    base = task.get('base_sha') or ''
    if not base or not _commit_is_ancestor(root, base, git(root, 'rev-parse', 'HEAD')):
        raise NotIntegrable('run finalization has no valid active task base')

    run_dir = root / 'work' / work_id / 'traceability' / 'runs' / run_id
    try:
        report_raw = (run_dir / 'results.json').read_bytes()
        report = json.loads(report_raw)
    except (OSError, ValueError) as exc:
        raise NotIntegrable(f'complete traceability report is unavailable: {exc}') from exc
    if (not isinstance(report, dict) or report.get('schema') != 'ask-test-results/v1'
            or report.get('run_id') != run_id or report.get('scope') != 'task'
            or report.get('task_id') != task_id):
        raise NotIntegrable('migration_required/incomplete: traceability report identity/schema does not match the selected task/run')
    candidate = report.get('candidate_sha')
    if (not isinstance(candidate, str) or not candidate
            or not _commit_is_ancestor(root, base, candidate)
            or not _candidate_in_task_lineage(root, task, candidate)):
        raise NotIntegrable('traceability candidate is outside the active task ancestry')

    contracts = load_accepted(root, work_id, candidate, candidate)
    plan, spec = contracts['plan'], contracts['spec']
    if (report.get('plan_digest') != contract_digest(plan)
            or report.get('spec_digest') != contract_digest(spec)):
        raise NotIntegrable('traceability report uses a stale accepted contract')
    expected = scoped_tests(plan, 'task', task_id)
    expected_by_id = {item['id']: item for item in expected}
    if not expected_by_id:
        raise NotIntegrable('accepted task scope has no mapped tests')

    runner_path = '.agents/ask/verification/traceability/unittest_runner.py'
    base_runner = subprocess.run(['git', 'show', f'{base}:{runner_path}'], cwd=root,
                                 capture_output=True)
    if base_runner.returncode:
        raise NotIntegrable('active task base has no pinned traceability runner')
    runner_identity = report.get('runner_identity')
    if (not isinstance(runner_identity, dict)
            or runner_identity.get('capability') != 'ask-traceability/v1'
            or runner_identity.get('adapter_digest') != hashlib.sha256(base_runner.stdout).hexdigest()):
        raise NotIntegrable('traceability runner differs from the task-base pinned runner')

    executions = report.get('executions')
    cases = report.get('cases')
    if (not isinstance(executions, list) or not executions
            or not isinstance(cases, list)):
        raise NotIntegrable('traceability report has unsupported execution/case shape')
    runners = {item.get('id'): item for item in plan.get('runners', []) if isinstance(item, dict)}
    tests_by_runner: dict[str, dict] = {}
    for test_id, test in expected_by_id.items():
        tests_by_runner.setdefault(test['runner_id'], {})[test_id] = test
    execution_by_id = {}
    execution_by_runner = {}
    phases = set()
    prefix = f'work/{work_id}/traceability/runs/{run_id}/'
    for execution in executions:
        if not isinstance(execution, dict):
            raise NotIntegrable('malformed traceability execution')
        execution_id = execution.get('id')
        runner_id = execution.get('runner_id')
        runner = runners.get(runner_id) if isinstance(runner_id, str) else None
        phase = execution.get('phase')
        if (not isinstance(execution_id, str) or not execution_id
                or execution_id in execution_by_id or runner is None
                or runner_id not in tests_by_runner or runner_id in execution_by_runner):
            raise NotIntegrable('traceability execution is outside the accepted runner scope')
        if (execution.get('argv') != runner.get('argv')
                or execution.get('adapter') != runner.get('adapter')):
            raise NotIntegrable('traceability execution runner/argv differs from the accepted plan')
        if phase not in {'red', 'final_green'}:
            raise NotIntegrable('traceability run phase is unsupported')
        if (execution.get('source_sha') != candidate or execution.get('collection_status') != 'ok'
                or type(execution.get('exit_code')) is not int):
            raise NotIntegrable('traceability execution is incomplete or collected from another source')
        relative = execution.get('output_artifact')
        if (not isinstance(relative, str) or not relative.startswith(prefix)
                or Path(relative).is_absolute() or '..' in Path(relative).parts):
            raise NotIntegrable('traceability output path is outside the selected run')
        output = root / relative
        try:
            output_raw = output.read_bytes()
        except OSError as exc:
            raise NotIntegrable('traceability output log is missing') from exc
        output_digest = hashlib.sha256(output_raw).hexdigest()
        if output.is_symlink() or output_digest != execution.get('output_digest'):
            raise NotIntegrable('traceability output log digest/binding is invalid')
        execution_by_id[execution_id] = execution
        execution_by_runner[runner_id] = execution
        phases.add(phase)
    if set(execution_by_runner) != set(tests_by_runner) or len(phases) != 1:
        raise NotIntegrable('traceability executions do not cover accepted runners in one phase')
    phase = next(iter(phases))

    seen = set()
    seen_by_runner: dict[str, set[str]] = {runner_id: set() for runner_id in tests_by_runner}
    behavior_red = False
    behavior_red_executions = set()
    for case in cases:
        if not isinstance(case, dict):
            raise NotIntegrable('malformed traceability case')
        test_id = case.get('test_id')
        test = expected_by_id.get(test_id) if isinstance(test_id, str) else None
        execution_id = case.get('execution_id')
        execution = execution_by_id.get(execution_id) if isinstance(execution_id, str) else None
        if (test is None or test_id in seen
                or (case.get('runner_id'), case.get('case_id')) !=
                   (test.get('runner_id'), test.get('case_id'))
                or execution is None or case.get('runner_id') != execution.get('runner_id')
                or case.get('phase') != execution.get('phase')
                or case.get('source_sha') != candidate):
            raise NotIntegrable('traceability case is outside its accepted execution/phase binding')
        seen.add(test_id)
        seen_by_runner[test.get('runner_id')].add(test_id)
        expected_sources = {
            name: hashlib.sha256(subprocess.run(
                ['git', 'show', f'{candidate}:{name}'], cwd=root,
                check=True, capture_output=True,
            ).stdout).hexdigest()
            for name in test.get('source_paths', [])
        }
        if case.get('source_digests') != expected_sources:
            raise NotIntegrable('traceability case source digest does not match its candidate')
        outcome = case.get('outcome')
        if outcome == 'failed' and case.get('failure_kind') == 'behavior_assertion':
            if execution['phase'] != 'red' or execution['exit_code'] == 0:
                raise NotIntegrable('behavior assertion failure is not bound to a failing Red execution')
            behavior_red = True
            behavior_red_executions.add(execution['id'])
        elif outcome != 'passed':
            raise NotIntegrable('traceability case contains an error or unsupported outcome')
        if execution['phase'] == 'final_green' and outcome != 'passed':
            raise NotIntegrable('final Green requires every mapped case to pass')
    if seen != set(expected_by_id):
        raise NotIntegrable('traceability run does not cover the complete accepted task scope')
    if any(seen_by_runner[runner_id] != set(expected)
           for runner_id, expected in tests_by_runner.items()):
        raise NotIntegrable('traceability execution does not cover its accepted runner cases')
    if phase == 'red' and (not behavior_red or not any(e['exit_code'] != 0 for e in executions)):
        raise NotIntegrable('Red requires a collected behavior assertion failure')
    if phase == 'red' and any(e['exit_code'] != 0 and e['id'] not in behavior_red_executions
                              for e in executions):
        raise NotIntegrable('failing Red execution has no mapped behavior assertion')
    if phase == 'final_green' and (behavior_red or any(e['exit_code'] != 0 for e in executions)):
        raise NotIntegrable('final Green requires all mapped cases to pass')
    for case in cases:
        execution = execution_by_id[case['execution_id']]
        if (case.get('output_artifact') != execution.get('output_artifact')
                or case.get('output_digest') != execution.get('output_digest')):
            raise NotIntegrable('traceability case output binding differs from its execution')

    ledger_row = {
        'run_id': run_id,
        'digest': hashlib.sha256(json.dumps(report, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        'phase': phase,
        'scope': 'task',
        'task_id': task_id,
        'candidate_sha': candidate,
        'spec_digest': report['spec_digest'],
        'plan_digest': report['plan_digest'],
    }
    return report, ledger_row


def _checkpoint_run_locked(root: Path, work_id: str, task_id: str, run_id: str,
                           state: dict) -> dict:
    """Finalize a validated report under an already-held coordinator state lock."""
    task = (state.get('tasks') or {}).get(task_id) or {}
    if task.get('status') != 'running':
        raise NotIntegrable('traceability run can only finalize for the active task attempt')
    report, row = _execution_row(root, work_id, task_id, run_id)
    traceability = root / 'work' / work_id / 'traceability'
    ledger_path = traceability / 'executions.json'
    ledger_lock = traceability / 'executions.lock'
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    import fcntl
    with ledger_lock.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            try:
                entries = json.loads(ledger_path.read_text(encoding='utf-8'))
            except FileNotFoundError:
                entries = []
            except (OSError, ValueError) as exc:
                raise NotIntegrable(f'cannot read execution ledger: {exc}') from exc
            if not isinstance(entries, list) or any(not isinstance(item, dict) for item in entries):
                raise NotIntegrable('execution ledger has an unsupported shape')
            matches = [item for item in entries if item.get('run_id') == run_id]
            if matches and (len(matches) != 1 or matches[0] != row):
                raise NotIntegrable('execution ledger contains a conflicting run identity')
            if not matches:
                entries.append(row)
                from verification.traceability.evidence import write_json
                write_json(ledger_path, entries)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
    recorded = task.setdefault('evidence', {}).setdefault('traceability_runs', [])
    prior = [item for item in recorded if isinstance(item, dict) and item.get('run_id') == run_id]
    summary = {key: row[key] for key in ('run_id', 'digest', 'phase', 'task_id',
                                         'candidate_sha', 'spec_digest', 'plan_digest')}
    if prior and (len(prior) != 1 or prior[0] != summary):
        raise NotIntegrable('coordinator state contains a conflicting run identity')
    if not prior:
        recorded.append(summary)
    return summary


def checkpoint_run(root: Path, work_id: str, task_id: str, run_id: str) -> dict:
    """Validate, idempotently ledger and checkpoint one standalone task run."""
    from inner_loop.checkpoint import read_checkpoint, publish
    from inner_loop.state import load_state, state_lock, _write_state, state_path
    with state_lock(root, work_id):
        state = load_state(root, work_id)
        current = read_checkpoint(root, work_id)
        if current is None or current[1] != state:
            raise NotIntegrable('coordinator state differs from its retained checkpoint')
        from inner_loop.graph import load_graph
        from inner_loop.recovery import require_safe
        require_safe(root, work_id, load_graph(root, work_id), state)
        summary = _checkpoint_run_locked(root, work_id, task_id, run_id, state)
        state['revision'] = int(state['revision']) + 1
        publish(root, work_id, state)
        _write_state(state_path(root, work_id), state)
    return summary


def artifact(root: Path, name: str) -> tuple[str, str]:
    path = (root / name).resolve()
    try:
        relative = str(path.relative_to(root.resolve()))
        return relative, digest(path.read_bytes())
    except (OSError, ValueError) as exc:
        raise NotIntegrable(f'review/policy artifact must exist inside repository: {name}') from exc


def _record_review(root: Path, work_id: str, task_id: str, reviewer: str, policy: str,
                   evidence: str, verdict: str = 'APPROVED', boundary: str = 'ok') -> dict:
    """Coordinator records an attributable delegated decision, bound to result bytes."""
    if not reviewer.strip() or policy != POLICY:
        raise NotIntegrable(f'reviewer identity and canonical policy {POLICY} required')
    if verdict not in {'APPROVED', 'REJECTED'} or boundary not in {'ok', 'extras', 'glob_too_narrow'}:
        raise NotIntegrable('invalid review verdict/boundary')
    with state_transaction(root, work_id, update_review=True) as doc:
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


def record_review(root: Path, work_id: str, task_id: str, reviewer: str, policy: str,
                  evidence: str, verdict: str = 'APPROVED', boundary: str = 'ok', *,
                  selected_task_id=None, selected_execution=None, delivery_task_id=None) -> dict:
    """Bind adopted task review to its explicit captured Task identity."""
    try:
        from engineering_model.workflow import adopted, workflow_admission
    except ModuleNotFoundError:
        from _ask.scripts.engineering_model.workflow import adopted, workflow_admission
    if (selected_task_id is None and selected_execution is None
            and delivery_task_id is None and adopted(root, work_id)):
        delivery_task_id = task_id
    if selected_task_id is None and selected_execution is None and delivery_task_id is None:
        return _record_review(root, work_id, task_id, reviewer, policy, evidence, verdict, boundary)
    with workflow_admission(root, work_id, selected_task_id=selected_task_id,
                            selected_execution=selected_execution, delivery_task_id=delivery_task_id):
        return _record_review(root, work_id, task_id, reviewer, policy, evidence, verdict, boundary)


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
                  result_digest=candidate.result_digest, checks=[], traceability_run_ids=[],
                  evidence_path=str((out / 'verification.json').relative_to(root)),
                  log_path=str((out / 'output.log').relative_to(root)))
    try:
        with tempfile.TemporaryDirectory(prefix='ask-candidate-') as tmp:
            runner, report['runner_digest'] = snapshot_runner(root, identity['base_sha'], Path(tmp) / 'trusted')
            report['runner_sha'] = identity['base_sha']
            capability_file=runner.parent/'traceability/__init__.py'
            import ast
            capability=None
            if capability_file.is_file():
                try:
                    for statement in ast.parse(capability_file.read_text()).body:
                        if isinstance(statement,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CAPABILITY' for t in statement.targets):
                            capability=ast.literal_eval(statement.value)
                except (SyntaxError,ValueError):
                    capability=None
            if capability!='ask-traceability/v1':
                raise NotIntegrable('migration_required: pinned runner has no supported traceability capability')
            checkout = Path(tmp) / 'checkout'
            git(root, 'worktree', 'add', '--detach', str(checkout), identity['candidate_sha'])
            try:
                report['tree_sha'] = git(checkout, 'rev-parse', 'HEAD^{tree}')
                report['checkplan_digest'], expected = plan_identity(checkout, runner)
                env = dict(os.environ, ASK_ROOT=str(checkout), VERIFY_JSON=str(out / 'verification.json'),
                           VERIFY_OUT_DIR=str(out), ASK_WORK_ID=identity['work_id'],
                           # Keep verifier code pinned to base, but load accepted
                           # obligations from the candidate. A reviewed amendment
                           # may be accepted after this task's original base.
                           ASK_TRACEABILITY_ANCHOR_SHA=identity['candidate_sha'],
                           ASK_TRACEABILITY_RUNTIME_ROOT=str(root), ASK_TRACEABILITY_SCOPE='task',
                           ASK_TRACEABILITY_TASK_ID=identity['task_id'])
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
                    raise NotIntegrable('required candidate verification failed or mismatched its CheckPlan: ' + str(executed.get('error', '')))
                completion_path = (root / 'work' / identity['work_id'] / 'traceability' / 'completion.json')
                try:
                    completion_raw = completion_path.read_bytes()
                    completion = json.loads(completion_raw)
                except (OSError, ValueError) as exc:
                    raise NotIntegrable('trusted verification produced no valid completion receipt') from exc
                if (not isinstance(completion, dict) or completion.get('status') != 'pass'
                        or completion.get('candidate_sha') != identity['candidate_sha']
                        or completion.get('scope') != 'task'
                        or completion.get('task_id') != identity['task_id']):
                    raise NotIntegrable('completion receipt is not bound to this verified task candidate')
                static_path = root / 'work' / identity['work_id'] / 'traceability' / (
                    f"static-{identity['candidate_sha']}.json")
                try:
                    static_raw = static_path.read_bytes()
                    static_receipt = json.loads(static_raw)
                except (OSError, ValueError) as exc:
                    raise NotIntegrable('trusted verification produced no valid static receipt') from exc
                if (not isinstance(static_receipt, dict)
                        or static_receipt.get('candidate_sha') != identity['candidate_sha']
                        or static_receipt.get('result') != 'pass'):
                    raise NotIntegrable('static receipt is not bound to this verified task candidate')
                report['static_receipt_digest'] = hashlib.sha256(static_raw).hexdigest()
                prefix = f"work/{identity['work_id']}/traceability/runs/"
                selected_runs = set()
                artifacts = completion.get('execution_artifacts')
                if not isinstance(artifacts, list):
                    raise NotIntegrable('completion receipt has no execution artifact inventory')
                for artifact_name in artifacts:
                    if not isinstance(artifact_name, str) or not artifact_name.startswith(prefix):
                        continue
                    parts = Path(artifact_name).parts
                    if len(parts) < 5 or parts[3] != 'runs' or not parts[4]:
                        raise NotIntegrable('completion receipt contains an unsafe run artifact path')
                    run_path = root / prefix / parts[4] / 'results.json'
                    try:
                        run = json.loads(run_path.read_bytes())
                    except (OSError, ValueError) as exc:
                        raise NotIntegrable('completion receipt names an unavailable run report') from exc
                    if (not isinstance(run, dict) or run.get('schema') != 'ask-test-results/v1'
                            or run.get('run_id') != parts[4]):
                        raise NotIntegrable('completion receipt names an invalid run report')
                    # Completion retains historical proof from other tasks as
                    # well. Only this task's reports are coordinator milestones;
                    # the full checkpoint continues to retain all raw proof.
                    if run.get('scope') != 'task' or run.get('task_id') != identity['task_id']:
                        continue
                    selected_runs.add(parts[4])
                report['traceability_run_ids'] = sorted(selected_runs)
                report['completion_digest'] = hashlib.sha256(completion_raw).hexdigest()
                if (git(checkout, 'rev-parse', 'HEAD') != identity['candidate_sha']
                        or git(checkout, 'status', '--porcelain')
                        or plan_identity(checkout, runner)[0] != report['checkplan_digest']):
                    raise NotIntegrable('candidate source/CheckPlan changed during verification')
                report['result'] = 'pass'
            finally:
                git(root, 'worktree', 'remove', '--force', str(checkout))
    except NotIntegrable as exc:
        report['error'] = str(exc)
        raise
    except (OSError, ValueError) as exc:
        report['error'] = str(exc)
        raise NotIntegrable(f'candidate verification could not execute: {exc}') from exc
    finally:
        report_path = out / 'integration.json'
        report['record_path'] = str(report_path.relative_to(root))
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report


def reuse_checkpointed_verification(root: Path, work_id: str, task: dict,
                                    candidate: Candidate) -> dict | None:
    """Return an exact retained passing receipt when pre-FF recovery can reuse it."""
    evidence = (task.get('evidence') or {}).get('verification')
    expected_digest = (task.get('evidence') or {}).get('verification_record_digest')
    if not isinstance(evidence, dict) or evidence.get('result') != 'pass':
        return None
    identity = dict(candidate.identity, result_digest=candidate.result_digest)
    if any(evidence.get(key) != value for key, value in identity.items()):
        return None
    record_path = evidence.get('record_path')
    if not isinstance(record_path, str):
        return None
    unresolved_path = root / record_path
    path = unresolved_path.resolve()
    if unresolved_path.is_symlink() or not path.is_relative_to(root.resolve()):
        return None
    try:
        raw = path.read_bytes()
        recorded = json.loads(raw)
        completion_raw = (root / 'work' / work_id / 'traceability' / 'completion.json').read_bytes()
    except (OSError, ValueError):
        return None
    if (not isinstance(expected_digest, str) or digest(raw) != expected_digest
            or recorded != evidence
            or digest(completion_raw) != evidence.get('completion_digest')):
        return None
    try:
        tree_sha = git(root, 'rev-parse', f"{candidate.identity['candidate_sha']}^{{tree}}")
    except NotIntegrable:
        return None
    if tree_sha != evidence.get('tree_sha'):
        return None
    if not isinstance(evidence.get('traceability_run_ids'), list):
        return None
    return evidence
