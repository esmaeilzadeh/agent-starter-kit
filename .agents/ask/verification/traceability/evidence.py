"""Immutable contract and coordinator review bindings for cooperative local writers."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from . import CAPABILITY
from .adapters import git
from .contracts import EXEMPTIONS, Invalid, POLICY, digest, file_digest, load, safe_path, slug, text
from .coverage import JAVASCRIPT_ADAPTERS, JEST_SUFFIXES, validate_plan
from verification.yaml_lite import parse_yaml


def read_at(root,sha,path):
    if not safe_path(path):raise Invalid('invalid repository path')
    proc=subprocess.run(['git','show',f'{sha}:{path}'],cwd=root,capture_output=True)
    if proc.returncode:raise Invalid(f'migration_required: missing {path} at {sha}')
    return proc.stdout


def json_at(root,sha,path):
    try:return json.loads(read_at(root,sha,path))
    except json.JSONDecodeError as exc:raise Invalid(f'invalid JSON {path}') from exc


def contract_paths(work_id):
    if not slug(work_id):raise Invalid('invalid work_id')
    return f'specs/current/{work_id}.json',f'work/{work_id}/test-plan.json',f'work/{work_id}/inner-loop/tasks.yaml'


def contracts_at(root,work_id,sha):
    spec_path,plan_path,graph_path=contract_paths(work_id)
    spec=json_at(root,sha,spec_path);plan=json_at(root,sha,plan_path)
    exists=subprocess.run(['git','cat-file','-e',f'{sha}:{graph_path}'],cwd=root,capture_output=True).returncode==0
    graph=parse_yaml(read_at(root,sha,graph_path).decode()) if exists else {'tasks':[]}
    violations=validate_plan(spec,plan,graph)
    if violations:raise Invalid(json.dumps([e.json() for e in violations]))
    return {'spec':spec,'plan':plan,'graph':graph}


def _accept_plan(root,work_id,revision,reviewer,recorded_by,evidence):
    if not text(reviewer) or not text(recorded_by) or reviewer==recorded_by:raise Invalid('independent reviewer and coordinator required')
    sha=git(root,'rev-parse','--verify',revision+'^{commit}')
    contracts=contracts_at(root,work_id,sha)
    path=(Path(root)/evidence).resolve()
    if not path.is_relative_to(Path(root).resolve()):raise Invalid('review artifact must be inside repository')
    decision=load(path)
    if (decision.get('decision')!='APPROVED' or decision.get('reviewer')!=reviewer
        or decision.get('spec_digest')!=digest(contracts['spec']) or decision.get('plan_digest')!=digest(contracts['plan'])):
        raise Invalid('plan review must approve the exact spec/plan digests')
    doc={'schema':'ask-accepted-tests/v1','capability':CAPABILITY,'contract_sha':sha,'work_id':work_id,
         'reviewer':reviewer,'recorded_by':recorded_by,'policy':POLICY,'policy_digest':file_digest(Path(root)/POLICY),
         'plan_review':decision,'plan_review_digest':digest(decision),
         **{k+'_digest':digest(v) for k,v in contracts.items()}}
    # Store coordinator authority outside the candidate tree. A source commit
    # cannot advance this ref; only an explicit reviewed accept-plan operation can.
    ref=f'refs/ask/accepted-tests/{work_id}'
    previous=subprocess.run(['git','rev-parse','--verify',ref],cwd=root,capture_output=True,text=True).stdout.strip()
    if previous:
        history_ref=f'refs/ask/accepted-tests-history/{work_id}/{previous}'
        existing=subprocess.run(['git','rev-parse','--verify',history_ref],cwd=root,
                                capture_output=True,text=True)
        if existing.returncode:
            git(root,'update-ref',history_ref,previous,'0'*40)
        elif existing.stdout.strip()!=previous:
            raise Invalid('retained accepted authority reference conflicts with its identity')
    def object_command(args,data):
        proc=subprocess.run(['git',*args],input=data,cwd=root,capture_output=True)
        if proc.returncode:raise Invalid(proc.stderr.decode())
        return proc.stdout.decode().strip()
    blob=object_command(['hash-object','-w','--stdin'],json.dumps(doc,sort_keys=True).encode())
    tree=object_command(['mktree'],f'100644 blob {blob}\taccepted.json\n'.encode())
    commit=object_command(['commit-tree',tree,'-p',sha],b'Coordinator accepted reviewed test obligations\n')
    git(root,'update-ref',ref,commit,previous or '0'*40)
    path=Path(root)/'work'/work_id/'traceability-accepted.json';write_json(path,doc)
    return doc


def load_accepted(root,work_id,anchor_sha,candidate_sha=None):
    if not slug(work_id):raise Invalid('invalid work_id')
    authority=subprocess.run(['git','rev-parse','--verify',f'refs/ask/accepted-tests/{work_id}'],cwd=root,capture_output=True,text=True)
    if authority.returncode:raise Invalid('migration_required: missing coordinator accepted-tests ref')
    pin=json_at(root,authority.stdout.strip(),'accepted.json')
    candidate_pin=json_at(root,anchor_sha,f'work/{work_id}/traceability-accepted.json')
    if candidate_pin!=pin:raise Invalid('candidate acceptance document differs from coordinator authority')
    if (pin.get('schema')!='ask-accepted-tests/v1' or pin.get('capability')!=CAPABILITY
        or pin.get('work_id')!=work_id or not text(pin.get('reviewer')) or not text(pin.get('recorded_by'))
        or pin['reviewer']==pin['recorded_by'] or pin.get('policy')!=POLICY):raise Invalid('migration_required: invalid accepted test contract')
    contracts=contracts_at(root,work_id,pin['contract_sha'])
    for key,value in contracts.items():
        if pin.get(key+'_digest')!=digest(value):raise Invalid('stale accepted '+key)
    if (pin.get('plan_review_digest')!=digest(pin.get('plan_review'))
        or pin['plan_review'].get('decision')!='APPROVED'
        or pin['plan_review'].get('reviewer')!=pin['reviewer']
        or pin['plan_review'].get('spec_digest')!=pin['spec_digest']
        or pin['plan_review'].get('plan_digest')!=pin['plan_digest']):raise Invalid('stale accepted plan review')
    _validate_historical_red_exception(root, work_id, pin, contracts)
    git(root,'merge-base','--is-ancestor',pin['contract_sha'],candidate_sha or anchor_sha)
    if candidate_sha:
        actual=contracts_at(root,work_id,candidate_sha)
        if any(digest(actual[k])!=pin[k+'_digest'] for k in actual):raise Invalid('candidate changed accepted obligations; reviewed amendment required')
        if file_digest_bytes(read_at(root,candidate_sha,POLICY))!=pin['policy_digest']:raise Invalid('candidate changed delegation policy')
    return dict(contracts,pin=pin)


def _validate_historical_red_exception(root, work_id, pin, contracts):
    declarations=contracts['plan'].get('historical_red_exceptions', [])
    review=pin.get('plan_review') or {}
    authorized=review.get('historical_red_exceptions', [])
    if not declarations:
        if authorized:
            raise Invalid('plan review authorizes a historical Red exception absent from its contract')
        return
    if declarations!=authorized:
        raise Invalid('historical Red exception is not bound by the accepted plan review')
    migration=review.get('coordinator_migration')
    if (not isinstance(migration,dict) or migration.get('work_id')!=work_id
        or migration.get('task_id')!='CR-3' or work_id!='continuation-recovery'
        or not text(migration.get('coordinator_sha')) or not text(migration.get('coordinator_tree'))
        or not text(migration.get('verifier_sha')) or not text(migration.get('verifier_tree'))
        or migration.get('scope_decision_digest')!=declarations[0].get('decision_digest')):
        raise Invalid('historical Red exception requires its exact P1 coordinator migration authorization')
    for item in declarations:
        if item.get('work_id')!=work_id or item.get('task_id')!='CR-3' or item.get('test_id')!='CR-T21':
            raise Invalid('historical Red exception exceeds its approved scope')
        try:
            raw=read_at(root,pin['contract_sha'],item['decision_artifact'])
        except Invalid as exc:
            raise Invalid('historical Red decision artifact is unavailable') from exc
        if file_digest_bytes(raw)!=item.get('decision_digest'):
            raise Invalid('historical Red decision artifact digest mismatch')


def load_historical_accepted(root, work_id, candidate_sha):
    """Load the immutable acceptance embedded in an original run candidate."""
    pin=json_at(root,candidate_sha,f'work/{work_id}/traceability-accepted.json')
    if (pin.get('schema')!='ask-accepted-tests/v1' or pin.get('capability')!=CAPABILITY
        or pin.get('work_id')!=work_id or not text(pin.get('reviewer'))
        or not text(pin.get('recorded_by')) or pin['reviewer']==pin['recorded_by']
        or pin.get('policy')!=POLICY):
        raise Invalid('historical run has no valid original accepted authority')
    if (pin.get('plan_review_digest')!=digest(pin.get('plan_review'))
        or pin['plan_review'].get('decision')!='APPROVED'
        or pin['plan_review'].get('reviewer')!=pin['reviewer']
        or pin['plan_review'].get('spec_digest')!=pin.get('spec_digest')
        or pin['plan_review'].get('plan_digest')!=pin.get('plan_digest')):
        raise Invalid('historical accepted plan review is stale')
    contracts=contracts_at(root,work_id,pin['contract_sha'])
    if any(pin.get(key+'_digest')!=digest(value) for key,value in contracts.items()):
        raise Invalid('historical accepted contract digest mismatch')
    git(root,'merge-base','--is-ancestor',pin['contract_sha'],candidate_sha)
    actual=contracts_at(root,work_id,candidate_sha)
    if any(digest(actual[key])!=pin[key+'_digest'] for key in actual):
        raise Invalid('historical run candidate changed its accepted contract')
    if file_digest_bytes(read_at(root,candidate_sha,POLICY))!=pin['policy_digest']:
        raise Invalid('historical run candidate changed its accepted policy')
    return dict(contracts,pin=pin)


def retained_adoption_context(root, work_id, *, state=None, checkpoint=None):
    """Return adoption authority only when the current checkpoint retains it."""
    import sys
    scripts = Path(root) / '_ask' / 'scripts'
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from inner_loop.checkpoint import read_checkpoint
    from inner_loop.recovery import retained_adoption_continuity
    from inner_loop.state import load_state

    checkpoint = checkpoint or read_checkpoint(root, work_id)
    if checkpoint is None:
        return None
    if state is None:
        state = load_state(root, work_id)
    return retained_adoption_continuity(root, work_id, state, checkpoint)


def validate_historical_continuity(root, work_id, original, current, report,
                                  ledger_row, decisions, current_candidate_sha,
                                  *, adoption_context=None):
    """Validate per-case historical Red provenance and reviewed applicability."""
    import hashlib
    from .coverage import scoped_tests

    run_id=report.get('run_id')
    original_candidate=report.get('candidate_sha')
    original_plan_digest=digest(original['plan'])
    if (report.get('schema')!='ask-test-results/v1' or report.get('work_id',work_id)!=work_id
        or report.get('task_id') is None or report.get('scope')!='task'
        or report.get('plan_digest')!=original_plan_digest
        or report.get('spec_digest')!=digest(original['spec'])):
        raise Invalid('historical report identity differs from its original accepted contract')
    calculated_report_digest=hashlib.sha256(json.dumps(
        report,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if (ledger_row.get('run_id')!=run_id or ledger_row.get('candidate_sha')!=original_candidate
        or ledger_row.get('task_id')!=report.get('task_id') or ledger_row.get('phase')!='red'
        or ledger_row.get('digest')!=calculated_report_digest):
        raise Invalid('historical report differs from its original ledger identity')
    ledger_identity=digest(ledger_row)
    authority_path=f'work/{work_id}/traceability-accepted.json'
    candidate_pin_object=git(root,'rev-parse',f'{original_candidate}:{authority_path}')
    original_authority_digest=digest(original['pin'])
    original_tests={t['id']:t for t in scoped_tests(original['plan'],'task',report['task_id'])}
    current_tests={t['id']:t for t in scoped_tests(current['plan'],'task',report['task_id'])}
    failures={case.get('test_id'):case for case in report.get('cases',[])
              if case.get('phase')=='red' and case.get('outcome')=='failed'
              and case.get('failure_kind')=='behavior_assertion'}
    continuity = (getattr(adoption_context, 'early_red_continuity', None)
                  if adoption_context is not None else None)
    if isinstance(continuity, str):
        try:
            continuity = json.loads(continuity)
        except ValueError as exc:
            raise Invalid('adopted early-Red continuity map is invalid JSON') from exc
    expected_reviewer = ((getattr(adoption_context, 'reviewer', None)
                          if adoption_context is not None else None)
                         or (current.get('pin') or {}).get('reviewer'))
    if continuity is not None:
        report_digest = hashlib.sha256(json.dumps(
            report, sort_keys=True, separators=(',', ':')
        ).encode()).hexdigest()
        if (continuity.get('report_digest') != report_digest
                or continuity.get('ledger_row_digest') != ledger_identity):
            raise Invalid('adopted early-Red report or ledger digest changed')
        authorization = continuity.get('early_authorization')
        if not isinstance(authorization, dict):
            raise Invalid('adopted early-Red authorization evidence is missing')
        if adoption_context is not None:
            authorization_raw = read_at(
                root, adoption_context.checkpoint_commit,
                'artifacts/' + authorization.get('path', ''),
            )
        else:
            authorization_raw = read_at(
                root, authorization.get('candidate_sha'), authorization.get('path'),
            )
        if hashlib.sha256(authorization_raw).hexdigest() != authorization.get('sha256'):
            raise Invalid('accepted early-Red authorization bytes changed')
        authorization_review = json.loads(authorization_raw)
        amendment = authorization_review.get('authorization_amendment_review') or {}
        baseline = amendment.get('early_baseline') or {}
        if (baseline.get('candidate_sha') != original_candidate
                or baseline.get('run_id') != run_id
                or baseline.get('cases') != ['CSH-T38', 'CSH-T39']
                or baseline.get('task_state') != 'CSH-10 remains pending; early Red does not advance it'):
            raise Invalid('accepted plan review does not authorize this early Red')
        if (authorization_review.get('schema') != 'ask-plan-review/v1'
                or authorization_review.get('work_id') != work_id
                or authorization_review.get('spec_digest') != original['pin'].get('spec_digest')
                or authorization_review.get('plan_digest') != original['pin'].get('plan_digest')
                or authorization_review.get('independent') is not True
                or not text(authorization_review.get('reviewer'))
                or authorization_review.get('reviewed_candidate_sha')
                != authorization.get('candidate_sha')
                or authorization_review.get('decision') != 'APPROVED'
                or amendment.get('candidate_sha') != authorization.get('candidate_sha')
                or amendment.get('decision') != 'APPROVED'
                or amendment.get('human_acceptance_remains_required') is not True):
            raise Invalid('early-Red authorization is not bound to the independent plan review')
        executions = report.get('executions')
        if not isinstance(executions, list) or len(executions) != 1:
            raise Invalid('adopted early-Red run must retain its single original execution')
        execution = executions[0]
        runner_path = '.agents/ask/verification/traceability/unittest_runner.py'
        original_runner_digest = file_digest_bytes(read_at(root, original_candidate, runner_path))
        output_path = execution.get('output_artifact')
        output_root = Path(root) / 'work' / work_id / 'traceability' / 'runs' / run_id
        try:
            output = Path(root) / output_path
            if (not isinstance(output_path, str) or output.is_symlink()
                    or not output.resolve().is_relative_to(output_root.resolve())):
                raise Invalid('adopted early-Red output path is unsafe')
            output_raw = (read_at(root, adoption_context.checkpoint_commit,
                                  'artifacts/' + output_path)
                          if adoption_context is not None else output.read_bytes())
        except (OSError, RuntimeError, TypeError) as exc:
            raise Invalid('adopted early-Red output is unavailable') from exc
        failure_ids = {case.get('test_id') for case in report.get('cases', [])
                       if isinstance(case, dict) and case.get('phase') == 'red'
                       and case.get('outcome') == 'failed'
                       and case.get('failure_kind') == 'behavior_assertion'}
        if (execution.get('phase') != 'red' or execution.get('exit_code') != 1
                or execution.get('collection_status') != 'ok'
                or execution.get('source_sha') != original_candidate
                or continuity.get('original_runner_digest') != original_runner_digest
                or report.get('runner_identity') != {
                    'capability': CAPABILITY, 'adapter_digest': original_runner_digest,
                }
                or execution.get('output_digest') != continuity.get('output_digest')
                or hashlib.sha256(output_raw).hexdigest() != continuity.get('output_digest')
                or failure_ids != {'CSH-T38', 'CSH-T39'}):
            raise Invalid('adopted early-Red execution is not the exact behavior-failing baseline')
        ancestry = subprocess.run(
            ['git', 'merge-base', '--is-ancestor', original_candidate, current_candidate_sha],
            cwd=root, capture_output=True,
        )
        if ancestry.returncode != 0:
            raise Invalid('early-Red candidate is outside adopted source ancestry')
        authority_commit = continuity.get('original_authority_object')
        original_pin_object = git(root, 'rev-parse', f'{original_candidate}:{authority_path}')
        generated = []
        for case in continuity.get('cases', []):
            test_id = case.get('test_id')
            generated.append({
                'work_id': work_id, 'task_id': report.get('task_id'), 'run_id': run_id,
                'test_id': test_id,
                'candidate_sha': original_candidate,
                'original_plan_digest': original_plan_digest,
                'report_digest': report_digest, 'ledger_row_digest': ledger_identity,
                'original_authority_object': authority_commit,
                'original_candidate_pin_object': original_pin_object,
                'original_authority_digest': original_authority_digest,
                'original_contract_digest': digest(original['pin']),
                'reviewer': expected_reviewer,
                'behavioral_continuity': case.get('behavioral_continuity'),
                'original_source_digests': source_digests(
                    root, original_candidate, original['plan'], [test_id],
                ),
                'current_source_digests': source_digests(
                    root, current_candidate_sha, current['plan'], [test_id],
                ),
            })
        decisions = generated
    rows={}
    for decision in decisions:
        test_id=decision.get('test_id')
        if test_id in rows:
            raise Invalid('duplicate historical continuity decision for one case')
        rows[test_id]=decision
    if not rows:
        raise Invalid('historical run has no per-case continuity decisions')
    if continuity is not None:
        _validate_early_red_semantic_map(root, work_id, original, current,
                                         current_candidate_sha, continuity, rows)
    for test_id,decision in rows.items():
        old_test=original_tests.get(test_id);new_test=current_tests.get(test_id)
        case=failures.get(test_id)
        if not old_test or not new_test or not case:
            raise Invalid(f'{test_id}: historical continuity does not identify an original failed case')
        if (decision.get('work_id')!=work_id or decision.get('task_id')!=report['task_id']
            or decision.get('run_id')!=run_id or decision.get('candidate_sha')!=original_candidate
            or decision.get('original_plan_digest')!=original_plan_digest
            or decision.get('report_digest')!=calculated_report_digest
            or decision.get('ledger_row_digest')!=ledger_identity
            or not text(decision.get('original_authority_object'))
            or decision.get('original_candidate_pin_object')!=candidate_pin_object
            or decision.get('original_authority_digest')!=original_authority_digest
            or decision.get('original_contract_digest')!=digest(original['pin'])
            or decision.get('reviewer')!=expected_reviewer
            or not text(decision.get('behavioral_continuity'))):
            raise Invalid(f'{test_id}: historical continuity provenance or reviewer binding is stale')
        authority_commit=decision['original_authority_object']
        history_ref=f'refs/ask/accepted-tests-history/{work_id}/{authority_commit}'
        retained=subprocess.run(['git','rev-parse','--verify',history_ref],cwd=root,
                                capture_output=True,text=True)
        authority_pin=json_at(root,authority_commit,'accepted.json')
        parent=git(root,'rev-parse',f'{authority_commit}^')
        if (retained.returncode or retained.stdout.strip()!=authority_commit
            or authority_pin!=original['pin'] or parent!=original['pin'].get('contract_sha')):
            raise Invalid(f'{test_id}: original coordinator authority is not exactly retained')
        if not isinstance(current_candidate_sha,str) or not current_candidate_sha:
            raise Invalid('historical continuity has no current candidate identity')
        old_sources=source_digests(root,case['source_sha'],original['plan'],[test_id])
        new_sources=source_digests(root,current_candidate_sha,current['plan'],[test_id])
        if (decision.get('original_source_digests')!=old_sources
            or decision.get('current_source_digests')!=new_sources):
            raise Invalid(f'{test_id}: historical continuity source identities are stale')
    return rows


def assertion_identity(root, candidate_sha, plan, test_id):
    """Digest one planned test method and its assertion ASTs at an exact commit."""
    tests = {item.get('id'): item for item in plan.get('tests', [])
             if isinstance(item, dict) and isinstance(item.get('id'), str)}
    test = tests.get(test_id)
    if not isinstance(test, dict):
        raise Invalid(f'{test_id}: accepted test identity is missing')
    case = test.get('case_id')
    sources = test.get('source_paths')
    if (not isinstance(case, str) or len(case.split('.')) < 3
            or not isinstance(sources, list) or len(sources) != 1
            or not isinstance(sources[0], str) or not sources[0].endswith('.py')):
        raise Invalid(f'{test_id}: accepted test source identity is ambiguous')
    raw = read_at(root, candidate_sha, sources[0])
    try:
        tree = ast.parse(raw)
    except SyntaxError as exc:
        raise Invalid(f'{test_id}: source does not parse at its retained candidate') from exc
    parts = case.split('.')
    classes = [node for node in ast.walk(tree)
               if isinstance(node, ast.ClassDef) and node.name == parts[-2]]
    methods = [node for parent in classes for node in parent.body
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
               and node.name == parts[-1]]
    if len(methods) != 1:
        raise Invalid(f'{test_id}: test method identity is missing or ambiguous')
    method = methods[0]
    assertion_nodes = [node for node in ast.walk(method)
                       if isinstance(node, ast.Assert)
                       or (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                           and node.func.attr.startswith('assert'))]
    assertion_nodes.sort(key=lambda node: (getattr(node, 'lineno', 0),
                                           getattr(node, 'col_offset', 0)))
    assertions = [hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
                  for node in assertion_nodes]
    return {
        'source_path': sources[0],
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'method_ast_sha256': hashlib.sha256(
            ast.dump(method, include_attributes=False).encode()
        ).hexdigest(),
        'assertion_ast_sha256': assertions,
    }


def _validate_early_red_semantic_map(root, work_id, original, current,
                                     current_candidate_sha, continuity, decisions):
    from .coverage import scoped_tests

    if (continuity.get('schema') != 'ask-early-red-continuity/v1'
            or continuity.get('work_id') != work_id
            or continuity.get('task_id') != 'CSH-10'
            or continuity.get('run_id') != '01ba1187a3584c9184579b9af66fdc07'
            or continuity.get('candidate_sha') != '371e4a5741f34afb0b2c37401fc847dc14309664'
            or continuity.get('original_plan_digest') != digest(original['plan'])
            or continuity.get('original_spec_digest') != digest(original['spec'])
            or continuity.get('current_plan_digest') != digest(current['plan'])
            or continuity.get('current_spec_digest') != digest(current['spec'])):
        raise Invalid('adopted early-Red continuity identity is stale')
    adaptations = continuity.get('adaptations')
    required_adaptations = {'versioned-credentials', 'planning-model',
                            'fault-injection', 'fixture-runtime'}
    if (not isinstance(adaptations, list) or len(adaptations) != len(required_adaptations)
            or {item.get('id') for item in adaptations if isinstance(item, dict)} != required_adaptations
            or any(not isinstance(item.get('assessment'), str) or not item['assessment'].strip()
                   for item in adaptations if isinstance(item, dict))):
        raise Invalid('early-Red map must account for every observed journey and fixture adaptation')
    current_ids = {test['id'] for test in scoped_tests(current['plan'], 'task', 'CSH-10')}
    original_ids = {test['id'] for test in scoped_tests(original['plan'], 'task', 'CSH-10')}
    if current_ids != {'CSH-T38', 'CSH-T39'} or original_ids != current_ids:
        raise Invalid('early-Red map does not cover the exact accepted CSH-10 scope')
    cases = continuity.get('cases')
    if (not isinstance(cases, list) or len(cases) != len(current_ids)
            or {row.get('test_id') for row in cases if isinstance(row, dict)} != current_ids):
        raise Invalid('early-Red semantic map must cover each accepted journey exactly once')
    for row in cases:
        test_id = row['test_id']
        old_identity = assertion_identity(root, continuity['candidate_sha'], original['plan'], test_id)
        new_identity = assertion_identity(root, current_candidate_sha, current['plan'], test_id)
        if row.get('original_identity') != old_identity or row.get('current_identity') != new_identity:
            raise Invalid(f'{test_id}: source or assertion AST changed after its semantic review')
        mappings = row.get('assertion_mappings')
        if not isinstance(mappings, list) or len(mappings) != len(old_identity['assertion_ast_sha256']):
            raise Invalid(f'{test_id}: semantic map omits original assertions')
        old_indexes, new_indexes = set(), set()
        for mapping in mappings:
            if not isinstance(mapping, dict):
                raise Invalid(f'{test_id}: invalid per-assertion semantic mapping')
            old_index, current_indexes = mapping.get('original_index'), mapping.get('current_indexes')
            if (type(old_index) is not int or old_index in old_indexes
                    or not isinstance(current_indexes, list) or not current_indexes
                    or not isinstance(mapping.get('assessment'), str)
                    or not mapping['assessment'].strip()):
                raise Invalid(f'{test_id}: invalid per-assertion semantic mapping')
            if (old_index < 0 or old_index >= len(old_identity['assertion_ast_sha256'])
                    or old_identity['assertion_ast_sha256'][old_index]
                    != mapping.get('original_assertion_sha256')
                    or len(current_indexes) != len(set(current_indexes))
                    or any(type(index) is not int or index < 0
                           or index >= len(new_identity['assertion_ast_sha256'])
                           for index in current_indexes)
                    or [new_identity['assertion_ast_sha256'][index] for index in current_indexes]
                       != mapping.get('current_assertion_sha256')):
                raise Invalid(f'{test_id}: assertion mapping digest does not identify its source AST')
            old_indexes.add(old_index)
            new_indexes.update(current_indexes)
        if old_indexes != set(range(len(old_identity['assertion_ast_sha256']))):
            raise Invalid(f'{test_id}: semantic map omits original assertions')
        additional = row.get('additional_current_assertions')
        expected_additional = sorted(set(range(len(new_identity['assertion_ast_sha256']))) - new_indexes)
        if (not isinstance(additional, list)
                or any(not isinstance(item, dict) for item in additional)
                or {item.get('current_index') for item in additional if isinstance(item, dict)}
                != set(expected_additional)
                or any(not isinstance(item.get('assessment'), str) or not item['assessment'].strip()
                       for item in additional)):
            raise Invalid(f'{test_id}: new assertions need separately reviewed rationale')
        required = {item['id']: set(item.get('criterion_ids') or [])
                    for item in current['plan'].get('tests', []) if item.get('id') == test_id}
        if row.get('criterion_ids') != sorted(required.get(test_id, set())):
            raise Invalid(f'{test_id}: semantic map changes its accepted criterion coverage')
        decision = decisions.get(test_id)
        if (not isinstance(decision, dict)
                or decision.get('behavioral_continuity') != row.get('behavioral_continuity')):
            raise Invalid(f'{test_id}: adopted continuity decision differs from its semantic map')


def file_digest_bytes(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()


def source_digests(root,sha,plan,test_ids=None):
    selected=None if test_ids is None else set(test_ids)
    paths={name for test in plan['tests'] if selected is None or test['id'] in selected for name in test['source_paths']}
    return {name:file_digest_bytes(read_at(root,sha,name)) for name in sorted(paths)}


def inventory(root,base,sha,plan):
    changed=git(root,'diff','--name-only',base,sha,'--','*.py').splitlines()
    cases=[];unmapped=[];behavior_changes=[]
    node_runners={runner['id'] for runner in plan.get('runners', []) if runner.get('adapter') in JAVASCRIPT_ADAPTERS}
    node_changed=[]
    if node_runners:
        patterns=['*'+suffix for suffix in sorted(JEST_SUFFIXES)]
        node_changed=git(root,'diff','--name-only',base,sha,'--',*patterns).splitlines()
        changed_paths=set(node_changed)
        # A shared Node test file may hold any of its mapped assertions.
        for test in plan['tests']:
            if test['runner_id'] in node_runners and changed_paths.intersection(test['source_paths']):
                cases.append(test['id'])
                behavior_changes.append(test['id'])
    inspected=sorted(set(changed+node_changed))
    for path in changed:
        try:tree=ast.parse(read_at(root,sha,path))
        except (Invalid,SyntaxError):continue
        try: old_tree=ast.parse(read_at(root,base,path))
        except (Invalid,SyntaxError): old_tree=ast.Module(body=[],type_ignores=[])
        old_methods={f'{c.name}.{m.name}':ast.dump(m,include_attributes=False) for c in old_tree.body if isinstance(c,ast.ClassDef) for m in c.body if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name.startswith('test')}
        for cls in tree.body:
            if not isinstance(cls,ast.ClassDef):continue
            for method in cls.body:
                if not isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)) or not method.name.startswith('test'):continue
                suffix=f'.{cls.name}.{method.name}'
                matches=[t['id'] for t in plan['tests'] if path in t['source_paths'] and t['case_id'].endswith(suffix)]
                if len(matches)==1:
                    cases.extend(matches)
                    previous=old_methods.get(f'{cls.name}.{method.name}')
                    if previous is not None and previous!=ast.dump(method,include_attributes=False):behavior_changes.extend(matches)
                else:unmapped.append(path+suffix)
    return {'inspected_sources':inspected,'changed_cases':sorted(set(cases)),'unmapped_cases':sorted(unmapped),'behavior_changes':sorted(set(behavior_changes))}


def _record_test_review(root,work_id,candidate_sha,anchor_sha,review_path,recorded_by,review_document=None):
    contracts=load_accepted(root,work_id,anchor_sha,candidate_sha)
    review=review_document if review_document is not None else load(Path(root)/review_path)
    if not text(recorded_by) or recorded_by==review.get('reviewer'):raise Invalid('independent reviewer and coordinator required')
    errors=review_errors(root,contracts,review,candidate_sha)
    if errors:raise Invalid('; '.join(errors))
    record={'schema':'ask-recorded-test-review/v1','recorded_by':recorded_by,'policy':POLICY,
            'policy_digest':contracts['pin']['policy_digest'],'contract_digest':digest(contracts['pin']),
            'review_digest':digest(review),'review':review,'candidate_sha':candidate_sha,
            'scope':review.get('scope','workstream'),'task_id':review.get('task_id')}
    write_json(Path(root)/'work'/work_id/'traceability'/'reviews'/(candidate_sha+'.json'),record)
    return record


def record_test_review(root,work_id,candidate_sha,anchor_sha,review_path,recorded_by,*,selected_execution=None,
                       delivery_task_id=None,
                       review_document=None):
    """Bind task-scoped review publication to the task named by its review body."""
    # Resolve identity, semantic checks, and persisted review from one captured
    # document. The source file can change while the workflow guard is entered.
    review = review_document if review_document is not None else load(Path(root)/review_path)
    scope = review.get('scope','workstream') if isinstance(review,dict) else None
    task_id = review.get('task_id') if isinstance(review,dict) else None
    if scope == 'task':
        if not isinstance(task_id,str) or not task_id.strip():
            raise Invalid('task-scoped review must name one task before publication')
        body_execution = {'work_id':work_id,'task_id':task_id}
        if selected_execution is not None and selected_execution != body_execution:
            raise Invalid('selected execution does not match task-scoped review body')
        if delivery_task_id is not None and delivery_task_id != task_id:
            raise Invalid('selected delivery task does not match task-scoped review body')
        delivery_task_id = task_id
    elif scope == 'workstream':
        if selected_execution is not None or delivery_task_id is not None:
            raise Invalid('workstream review cannot be bound to a task execution')
    elif scope is not None:
        raise Invalid('review body has an unknown scope')
    if selected_execution is None and delivery_task_id is None:
        return _record_test_review(root,work_id,candidate_sha,anchor_sha,review_path,recorded_by,review)
    from verification.run import workflow_context
    with workflow_context(root,work_id,selected_execution=selected_execution,
                          delivery_task_id=None if selected_execution else delivery_task_id):
        return _record_test_review(root,work_id,candidate_sha,anchor_sha,review_path,recorded_by,review)


def review_errors(root,contracts,review,sha):
    errors=[];spec=contracts['spec'];plan=contracts['plan']
    if not isinstance(review,dict):return ['missing independent semantic review']
    scope=review.get('scope','workstream');task_id=review.get('task_id')
    if scope=='workstream':
        if task_id is not None:errors.append('workstream review must not name a task')
        selected_tests=list(plan['tests'])
    elif scope=='task':
        matches=[s['test_ids'] for s in plan.get('task_scopes',[]) if s.get('task_id')==task_id]
        if len(matches)!=1:return ['task review does not identify one accepted task scope']
        selected_ids=set(matches[0]);selected_tests=[t for t in plan['tests'] if t['id'] in selected_ids]
    else:return ['semantic review scope must be workstream or task']
    selected_ids=[t['id'] for t in selected_tests]
    # Workstream review covers every accepted criterion, including review-only
    # obligations with no executable test. Task review covers the criteria
    # referenced by that task's assigned cases.
    selected_criteria=(sorted(c['id'] for c in spec['criteria']) if scope=='workstream'
                       else sorted({cid for test in selected_tests for cid in test['criterion_ids']}))
    source_ids=None if scope=='workstream' else selected_ids
    expected={'schema':'ask-test-review/v2','candidate_sha':sha,'spec_digest':digest(spec),'plan_digest':digest(plan),
              'scope':scope,'task_id':task_id,'test_ids':selected_ids,'criterion_ids':selected_criteria,
              'source_digests':source_digests(root,sha,plan,source_ids)}
    if any(review.get(k)!=v for k,v in expected.items()):errors.append('stale review candidate/spec/plan/source binding')
    if not text(review.get('reviewer')):errors.append('missing reviewer')
    if review.get('base_sha')!=contracts['pin']['contract_sha']:errors.append('review inventory base differs from accepted contract revision')
    actual=inventory(root,contracts['pin']['contract_sha'],sha,plan)
    exclusions=review.get('inventory_exclusions',{})
    if not isinstance(exclusions,dict):exclusions={}
    if (review.get('inspected_sources')!=actual['inspected_sources'] or review.get('changed_cases')!=actual['changed_cases']
        or set(exclusions)!=set(actual['unmapped_cases']) or any(not text(v) for v in exclusions.values())):
        errors.append('changed test inventory is incomplete')
    for test in plan['tests']:
        if test['id'] in actual['behavior_changes'] and test['change_kind']=='regression':errors.append(test['id']+': changed behavior cannot be classified regression')
    from .contracts import indexed
    invalid=[];criteria=indexed(review.get('criteria'),'review.criteria',invalid);tests=indexed(review.get('tests'),'review.tests',invalid)
    if invalid:errors.append('duplicate or malformed semantic review decisions')
    if set(criteria)!=set(selected_criteria) or set(tests)!=set(selected_ids):errors.append('missing per-criterion/test semantic review')
    obligations={o['criterion_id']:o['required_types'] for o in plan['obligations']}
    task_types={cid:{t['type'] for t in selected_tests if cid in t['criterion_ids']} for cid in selected_criteria}
    for cid,c in criteria.items():
        if c.get('coverage_decision')!='APPROVED' or not text(c.get('assessment')):errors.append(f'{cid}: coverage rejected/missing assessment')
        types=c.get('type_adequacy',{})
        if not isinstance(types,dict):types={}
        required=obligations.get(cid,[]) if scope=='workstream' else [kind for kind in obligations.get(cid,[]) if kind in task_types.get(cid,set())]
        for kind in required:
            item=types.get(kind,{})
            if not isinstance(item,dict) or item.get('decision')!='APPROVED' or not text(item.get('assessment')):errors.append(f'{cid}: missing/rejected {kind} review')
    classifications={t['id']:t for t in plan['tests']}
    for tid,t in tests.items():
        exemption=t.get('tdd_exemption')
        if exemption is not None:
            valid=(isinstance(exemption,dict) and exemption.get('kind') in EXEMPTIONS
                   and text(exemption.get('reason')) and exemption.get('reviewer_ack') is True
                   and exemption.get('decision')=='APPROVED')
            if not valid:errors.append(f'{tid}: unsupported behavior TDD exemption')
            case=classifications.get(tid,{})
            if isinstance(exemption,dict) and exemption.get('kind')=='baseline-regression':
                allowed=plan.get('task_scoped_baseline_regression_exemptions',{}).get(task_id,[])
                unchanged=scope=='task' and case.get('change_kind')=='new' and tid in allowed
                if unchanged:
                    for path in case.get('source_paths',[]):
                        try:unchanged=unchanged and read_at(root,contracts['pin']['contract_sha'],path)==read_at(root,sha,path)
                        except (Invalid,OSError):unchanged=False
                if not unchanged:
                    errors.append(f'{tid}: baseline regression exemption is task-scoped and requires sources unchanged from the accepted baseline')
            elif case.get('change_kind')!='changed' or tid in actual['behavior_changes']:
                errors.append(f'{tid}: unsupported behavior TDD exemption')
        if t.get('decision')!='APPROVED' or any(not text(t.get(k)) for k in ['assertion_assessment','counterexample','tdd_continuity_assessment']):errors.append(f'{tid}: incomplete/rejected assertion review')
    return errors


def write_json(path,doc):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    import os,tempfile
    fd,name=tempfile.mkstemp(prefix='.report-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as stream:json.dump(doc,stream,indent=2);stream.write('\n')
        os.replace(name,path)
    finally:
        if Path(name).exists():Path(name).unlink()


def source_changes(root,work_id):
    names=set()
    for args in [('diff','--name-only','-z'),('diff','--cached','--name-only','-z'),('ls-files','--others','--exclude-standard','-z')]:
        raw=subprocess.run(['git',*args],cwd=root,check=True,capture_output=True,text=True).stdout
        names.update(raw.split('\0'))
    prefix=f'work/{work_id}/inner-loop/'
    catalog_paths={f'work/{work_id}/references/integrity.json',
                   f'work/{work_id}/references/integrity.json.pending'}
    return sorted(n for n in names if n and not n.startswith(f'work/{work_id}/traceability/')
                  and n not in {prefix+'state.json',prefix+'state.lock',f'work/{work_id}/result.json'}
                  and n not in catalog_paths
                  and not n.startswith((prefix+'evidence/',prefix+'results/',prefix+'.state-')))


def accept_plan(root,work_id,revision,reviewer,recorded_by,evidence):
    import fcntl,os
    if not slug(work_id):raise Invalid('invalid work_id')
    if os.environ.get('ASK_INNER_LOOP_ROLE')=='worker':raise Invalid('coordinator operation cannot be performed by worker')
    directory=Path(root)/'work'/work_id/'inner-loop';directory.mkdir(parents=True,exist_ok=True)
    with (directory/'state.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        path=directory/'state.json'
        if path.exists() and any(t.get('status')=='running' for t in load(path).get('tasks',{}).values()):
            raise Invalid('cannot amend accepted obligations while a task is running')
        return _accept_plan(root,work_id,revision,reviewer,recorded_by,evidence)
