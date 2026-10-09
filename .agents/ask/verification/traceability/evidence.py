"""Immutable contract and coordinator review bindings for cooperative local writers."""
from __future__ import annotations
import ast
import json
from pathlib import Path
import subprocess
from . import CAPABILITY
from .adapters import git
from .contracts import EXEMPTIONS, Invalid, POLICY, digest, file_digest, load, safe_path, slug, text
from .coverage import validate_plan
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
    git(root,'merge-base','--is-ancestor',pin['contract_sha'],candidate_sha or anchor_sha)
    if candidate_sha:
        actual=contracts_at(root,work_id,candidate_sha)
        if any(digest(actual[k])!=pin[k+'_digest'] for k in actual):raise Invalid('candidate changed accepted obligations; reviewed amendment required')
        if file_digest_bytes(read_at(root,candidate_sha,POLICY))!=pin['policy_digest']:raise Invalid('candidate changed delegation policy')
    return dict(contracts,pin=pin)


def file_digest_bytes(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()


def source_digests(root,sha,plan,test_ids=None):
    selected=None if test_ids is None else set(test_ids)
    paths={name for test in plan['tests'] if selected is None or test['id'] in selected for name in test['source_paths']}
    return {name:file_digest_bytes(read_at(root,sha,name)) for name in sorted(paths)}


def inventory(root,base,sha,plan):
    changed=git(root,'diff','--name-only',base,sha,'--','*.py').splitlines()
    sources={name for t in plan['tests'] for name in t['source_paths']}
    inspected=sorted(changed)
    cases=[];unmapped=[];behavior_changes=[]
    for path in inspected:
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
                    if old_methods.get(f'{cls.name}.{method.name}')!=ast.dump(method,include_attributes=False):behavior_changes.extend(matches)
                else:unmapped.append(path+suffix)
    return {'inspected_sources':inspected,'changed_cases':sorted(set(cases)),'unmapped_cases':sorted(unmapped),'behavior_changes':sorted(set(behavior_changes))}


def record_test_review(root,work_id,candidate_sha,anchor_sha,review_path,recorded_by):
    contracts=load_accepted(root,work_id,anchor_sha,candidate_sha);review=load(Path(root)/review_path)
    if not text(recorded_by) or recorded_by==review.get('reviewer'):raise Invalid('independent reviewer and coordinator required')
    errors=review_errors(root,contracts,review,candidate_sha)
    if errors:raise Invalid('; '.join(errors))
    record={'schema':'ask-recorded-test-review/v1','recorded_by':recorded_by,'policy':POLICY,
            'policy_digest':contracts['pin']['policy_digest'],'contract_digest':digest(contracts['pin']),
            'review_digest':digest(review),'review':review,'candidate_sha':candidate_sha,
            'scope':review.get('scope','workstream'),'task_id':review.get('task_id')}
    write_json(Path(root)/'work'/work_id/'traceability'/'reviews'/(candidate_sha+'.json'),record)
    return record


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
    selected_criteria=(sorted(o['criterion_id'] for o in plan['obligations']) if scope=='workstream'
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
            if (not isinstance(exemption,dict) or exemption.get('kind') not in EXEMPTIONS
                or not text(exemption.get('reason')) or exemption.get('reviewer_ack') is not True
                or exemption.get('decision')!='APPROVED' or classifications.get(tid,{}).get('change_kind')!='changed'
                or tid in actual['behavior_changes']):errors.append(f'{tid}: unsupported behavior TDD exemption')
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
    return sorted(n for n in names if n and not n.startswith(f'work/{work_id}/traceability/')
                  and n not in {prefix+'state.json',prefix+'state.lock',f'work/{work_id}/result.json'}
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
