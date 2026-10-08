"""Immutable contract and coordinator review bindings for cooperative local writers."""
from __future__ import annotations
import ast
import json
from pathlib import Path
import subprocess
from . import CAPABILITY
from .adapters import git
from .contracts import Invalid, POLICY, digest, file_digest, load, safe_path, slug, text
from .coverage import validate_plan
from verification.yaml_lite import parse_yaml


def read_at(root,sha,path):
    if not safe_path(path):raise Invalid('invalid repository path')
    proc=subprocess.run(['git','show',f'{sha}:{path}'],cwd=root,capture_output=True)
    if proc.returncode:raise Invalid(f'migration_required: missing {path} at {sha}')
    return proc.stdout


def json_at(root,sha,path):
    try:return json.loads(read_at(root,sha,path))
    except ValueError as exc:raise Invalid(f'invalid JSON {path}') from exc


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


def accept_plan(root,work_id,revision,reviewer,recorded_by,evidence):
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
    path=Path(root)/'work'/work_id/'traceability-accepted.json';write_json(path,doc)
    return doc


def load_accepted(root,work_id,anchor_sha,candidate_sha=None):
    pin=json_at(root,anchor_sha,f'work/{work_id}/traceability-accepted.json')
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


def source_digests(root,sha,plan):
    return {name:file_digest_bytes(read_at(root,sha,name)) for t in plan['tests'] for name in t['source_paths']}


def inventory(root,base,sha,plan):
    changed=git(root,'diff','--name-only',base,sha,'--','*.py').splitlines()
    sources={name for t in plan['tests'] for name in t['source_paths']}
    inspected=sorted(set(changed)&sources | {n for n in changed if Path(n).name.startswith('test_')})
    cases=[];unmapped=[]
    for path in inspected:
        try:tree=ast.parse(read_at(root,sha,path))
        except (Invalid,SyntaxError):continue
        for cls in tree.body:
            if not isinstance(cls,ast.ClassDef):continue
            for method in cls.body:
                if not isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)) or not method.name.startswith('test'):continue
                suffix=f'.{cls.name}.{method.name}'
                matches=[t['id'] for t in plan['tests'] if path in t['source_paths'] and t['case_id'].endswith(suffix)]
                if len(matches)==1:cases.extend(matches)
                else:unmapped.append(path+suffix)
    return {'inspected_sources':inspected,'changed_cases':sorted(set(cases)),'unmapped_cases':sorted(unmapped)}


def record_test_review(root,work_id,candidate_sha,anchor_sha,review_path,recorded_by):
    contracts=load_accepted(root,work_id,anchor_sha,candidate_sha);review=load(Path(root)/review_path)
    if not text(recorded_by) or recorded_by==review.get('reviewer'):raise Invalid('independent reviewer and coordinator required')
    errors=review_errors(root,contracts,review,candidate_sha)
    if errors:raise Invalid('; '.join(errors))
    record={'schema':'ask-recorded-test-review/v1','recorded_by':recorded_by,'policy':POLICY,
            'policy_digest':contracts['pin']['policy_digest'],'contract_digest':digest(contracts['pin']),
            'review_digest':digest(review),'review':review,'candidate_sha':candidate_sha}
    write_json(Path(root)/'work'/work_id/'traceability'/'reviews'/(candidate_sha+'.json'),record)
    return record


def review_errors(root,contracts,review,sha):
    errors=[];spec=contracts['spec'];plan=contracts['plan']
    if not isinstance(review,dict):return ['missing independent semantic review']
    expected={'schema':'ask-test-review/v1','candidate_sha':sha,'spec_digest':digest(spec),'plan_digest':digest(plan),'source_digests':source_digests(root,sha,plan)}
    if any(review.get(k)!=v for k,v in expected.items()):errors.append('stale review candidate/spec/plan/source binding')
    if not text(review.get('reviewer')):errors.append('missing reviewer')
    if review.get('base_sha')!=contracts['pin']['contract_sha']:errors.append('review inventory base differs from accepted contract revision')
    actual=inventory(root,contracts['pin']['contract_sha'],sha,plan)
    exclusions=review.get('inventory_exclusions',{})
    if not isinstance(exclusions,dict):exclusions={}
    if (review.get('inspected_sources')!=actual['inspected_sources'] or review.get('changed_cases')!=actual['changed_cases']
        or set(exclusions)!=set(actual['unmapped_cases']) or any(not text(v) for v in exclusions.values())):
        errors.append('changed test inventory is incomplete')
    from .contracts import indexed
    invalid=[];criteria=indexed(review.get('criteria'),'review.criteria',invalid);tests=indexed(review.get('tests'),'review.tests',invalid)
    if invalid:errors.append('duplicate or malformed semantic review decisions')
    if set(criteria)!={c['id'] for c in spec['criteria']} or set(tests)!={t['id'] for t in plan['tests']}:errors.append('missing per-criterion/test semantic review')
    obligations={o['criterion_id']:o['required_types'] for o in plan['obligations']}
    for cid,c in criteria.items():
        if c.get('coverage_decision')!='APPROVED' or not text(c.get('assessment')):errors.append(f'{cid}: coverage rejected/missing assessment')
        types=c.get('type_adequacy',{})
        if not isinstance(types,dict):types={}
        for kind in obligations.get(cid,[]):
            item=types.get(kind,{})
            if not isinstance(item,dict) or item.get('decision')!='APPROVED' or not text(item.get('assessment')):errors.append(f'{cid}: missing/rejected {kind} review')
    for tid,t in tests.items():
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
                  and n not in {prefix+'state.json',prefix+'state.lock'}
                  and not n.startswith((prefix+'evidence/',prefix+'results/',prefix+'.state-')))
