"""Validate the whole accepted obligation registry before selecting task scope."""
from __future__ import annotations
from .contracts import TYPES, POLICY, Violation, digest, indexed, safe_path, scenario, slug, string_list, text


def _validate_plan(spec: dict, plan: dict, accepted_task_graph: dict | None = None) -> list[Violation]:
    errors=[]
    if not isinstance(spec,dict) or not isinstance(plan,dict):
        return [Violation('invalid_contract',field='spec/plan')]
    for doc,name,version in [(spec,'spec','ask-spec/v1'),(plan,'plan','ask-test-plan/v1')]:
        if doc.get('schema')!=version: errors.append(Violation('unsupported_schema',field=name))
        if not slug(doc.get('work_id')): errors.append(Violation('invalid_work_id',field=name))
    if spec.get('work_id')!=plan.get('work_id'): errors.append(Violation('work_id_mismatch'))
    if type(spec.get('revision')) is not int or spec['revision']<1: errors.append(Violation('invalid_revision'))
    if plan.get('spec_digest')!=digest(spec): errors.append(Violation('spec_digest_mismatch'))
    criteria=indexed(spec.get('criteria'),'criteria',errors)
    tests=indexed(plan.get('tests'),'tests',errors)
    obligations=indexed(plan.get('obligations'),'obligations',errors,'criterion_id')
    runners=indexed(plan.get('runners'),'runners',errors)
    scopes=indexed(plan.get('task_scopes'),'task_scopes',errors,'task_id')
    if not criteria: errors.append(Violation('empty_criteria'))
    for cid,c in criteria.items():
        if not scenario(c): errors.append(Violation('empty_behavior',cid,field=f'criteria.{cid}'))
        mode=c.get('verification_mode')
        if mode=='tests':
            if cid not in obligations: errors.append(Violation('missing_obligation',cid))
        elif mode=='review':
            decision=c.get('review_decision',{})
            if (not text(c.get('reason')) or not isinstance(decision,dict)
                or decision.get('decision')!='APPROVED' or decision.get('policy')!=POLICY
                or not text(decision.get('reviewer')) or not text(decision.get('recorded_by'))):
                errors.append(Violation('unauthorized_review_only',cid))
        else: errors.append(Violation('invalid_verification_mode',cid))
    for cid,o in obligations.items():
        if cid not in criteria or criteria[cid].get('verification_mode')!='tests': errors.append(Violation('invalid_obligation',cid))
        types=o.get('required_types')
        if not string_list(types) or not set(types)<=TYPES:
            errors.append(Violation('invalid_required_types',cid));continue
        for kind in types:
            if not any(t.get('type')==kind and cid in (t.get('criterion_ids') or []) for t in tests.values()):
                errors.append(Violation('missing_test_type',cid,required_type=kind))
    seen=set()
    for tid,t in tests.items():
        links=t.get('criterion_ids')
        if not string_list(links): errors.append(Violation('orphan_test',test_id=tid));links=[]
        for cid in links:
            if cid not in criteria or criteria[cid].get('verification_mode')!='tests':
                errors.append(Violation('unknown_criterion',cid,tid))
        if t.get('type') not in TYPES: errors.append(Violation('invalid_test_type',test_id=tid))
        if t.get('change_kind') not in {'new','changed','regression'}: errors.append(Violation('invalid_change_kind',test_id=tid))
        if not scenario(t.get('scenario')): errors.append(Violation('empty_behavior',test_id=tid))
        assertions=indexed(t.get('expected_assertions'),'expected_assertions',errors,'criterion_id')
        if set(assertions)!=set(links) or any(not string_list(a.get('checks')) for a in assertions.values()):
            errors.append(Violation('missing_expected_assertions',test_id=tid))
        if not string_list(t.get('source_paths')) or not all(safe_path(p) for p in t.get('source_paths',[])):
            errors.append(Violation('invalid_source_paths',test_id=tid))
        if t.get('runner_id') not in runners or not text(t.get('case_id')):
            errors.append(Violation('invalid_runner_case',test_id=tid));continue
        identity=(t['runner_id'],t['case_id'])
        if identity in seen: errors.append(Violation('duplicate_case',test_id=tid))
        seen.add(identity)
    for rid,r in runners.items():
        argv=r.get('argv')
        if (not string_list(argv) or len(argv)<4 or argv[1:3]!=['-m','unittest']
            or r.get('adapter')!='unittest' or argv[0] not in {'python','python3'}):
            errors.append(Violation('unsupported_runner',field=rid))
    graph_ids={t['id'] for t in (accepted_task_graph or {}).get('tasks',[])}
    if set(scopes)!=graph_ids: errors.append(Violation('task_graph_mismatch'))
    assigned=set()
    for task_id,s in scopes.items():
        ids=s.get('test_ids')
        if not string_list(ids) or not set(ids)<=tests.keys(): errors.append(Violation('invalid_task_scope',field=task_id));continue
        assigned.update(ids)
    if graph_ids and assigned!=set(tests): errors.append(Violation('unassigned_tests'))
    return errors


def PathName(value):
    from pathlib import Path
    return Path(value).name


def scoped_tests(plan,scope='workstream',task_id=None):
    if scope=='workstream' and task_id is None: return plan['tests']
    if scope=='task' and task_id:
        matches=[s['test_ids'] for s in plan['task_scopes'] if s['task_id']==task_id]
        if len(matches)==1: return [t for t in plan['tests'] if t['id'] in matches[0]]
    raise ValueError('invalid accepted task/workstream scope')


def validate_plan(spec,plan,accepted_task_graph=None):
    try:return _validate_plan(spec,plan,accepted_task_graph)
    except (TypeError,KeyError,AttributeError) as exc:return [Violation('invalid_field_type',field=str(exc))]
