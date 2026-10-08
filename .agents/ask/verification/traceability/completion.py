"""One policy evaluator for Verify, integration, acceptance and result recording."""
from __future__ import annotations
from pathlib import Path
from . import CAPABILITY
from .contracts import Invalid, POLICY, digest, file_digest, load, slug, text
from .coverage import scoped_tests, validate_plan
from .evidence import (file_digest_bytes, git, read_at, review_errors, source_changes,
                       source_digests)


def evaluate_completion(contracts, review, executions, trusted_context):
    root=Path(trusted_context['root']).resolve();sha=trusted_context['candidate_sha']
    scope=trusted_context.get('scope','workstream');task_id=trusted_context.get('task_id')
    errors=[];missing=[];rows=[];artifacts=[]
    spec=contracts['spec'];plan=contracts['plan'];pin=contracts['pin'];work_id=spec['work_id']
    report={'schema':'ask-completion/v1','status':'fail','scope':scope,'task_id':task_id,'candidate_sha':sha,
            'input_digests':{'spec':digest(spec),'plan':digest(plan),'accepted':digest(pin),'review':digest(review),'executions':digest(executions)},
            'criterion_evidence':rows,'missing_evidence':missing,'errors':errors,'execution_artifacts':artifacts}
    try:
        selected=scoped_tests(plan,scope,task_id)
        if validate_plan(spec,plan,contracts['graph']):errors.append('invalid accepted plan')
        # Runtime evidence does not exempt changes to candidate source/contracts.
        if not trusted_context.get('detached_candidate'):
            if git(root,'rev-parse','HEAD')!=sha:errors.append('candidate is not current HEAD')
            if source_changes(root,work_id):errors.append('dirty candidate source')
        sources=source_digests(root,sha,plan)
        if (not isinstance(review,dict) or review.get('schema')!='ask-recorded-test-review/v1'
            or review.get('candidate_sha')!=sha or review.get('contract_digest')!=digest(pin)
            or review.get('policy')!=POLICY or review.get('policy_digest')!=pin['policy_digest']
            or review.get('review_digest')!=digest(review.get('review'))
            or not text(review.get('recorded_by'))
            or review.get('recorded_by')==(review.get('review') or {}).get('reviewer')):
            errors.append('missing or stale coordinator-recorded semantic review')
        semantic=(review or {}).get('review') or {}
        errors.extend(review_errors(root,contracts,semantic,sha))
        if file_digest(root/POLICY)!=pin['policy_digest']:errors.append('changed policy artifact')
        finals={};reds={};seen_runs=set()
        runners={r['id']:r for r in plan['runners']};test_map={t['id']:t for t in plan['tests']}
        expected_adapter=file_digest(Path(__file__).with_name('unittest_runner.py'))
        for execution_report in executions:
            run_id=execution_report.get('run_id')
            if not slug(run_id) or run_id in seen_runs:
                errors.append('invalid or duplicate run identity');continue
            seen_runs.add(run_id)
            retained=load(root/'work'/work_id/'traceability'/'runs'/run_id/'results.json')
            if retained!=execution_report:errors.append(f'{run_id}: report differs from coordinator execution record')
            if (execution_report.get('schema')!='ask-test-results/v1' or execution_report.get('spec_digest')!=digest(spec)
                or execution_report.get('plan_digest')!=digest(plan)
                or execution_report.get('runner_identity')!={'capability':CAPABILITY,'adapter_digest':expected_adapter}):errors.append(f'{run_id}: stale contracts or runner')
            processes={};cases_by_execution={}
            for run in execution_report.get('executions',[]):
                eid=run.get('id');runner=runners.get(run.get('runner_id'))
                if not text(eid) or eid in processes:errors.append(f'{run_id}: duplicate/missing execution identity')
                processes[eid]=run
                if not runner or run.get('argv')!=runner['argv'] or run.get('adapter')!=runner['adapter']:errors.append(f'{run_id}: runner identity mismatch')
                if type(run.get('exit_code')) is not int or run.get('collection_status')!='ok':errors.append(f'{run_id}: collection failed or zero cases')
                if run.get('source_sha')!=execution_report.get('candidate_sha'):errors.append(f'{run_id}: execution revision mismatch')
                artifact=(root/run['output_artifact']).resolve()
                if not artifact.is_relative_to((root/'work'/work_id/'traceability'/'runs'/run_id).resolve()) or file_digest(artifact)!=run.get('output_digest'):errors.append(f'{run_id}: changed/missing execution log')
                artifacts.append(run['output_artifact'])
                cases_by_execution[eid]=[]
            seen_cases=set()
            for case in execution_report.get('cases',[]):
                tid=case.get('test_id');test=test_map.get(tid);run=processes.get(case.get('execution_id'))
                identity=(case.get('runner_id'),case.get('case_id'))
                if identity in seen_cases:errors.append(f'{run_id}: duplicate case {tid}')
                seen_cases.add(identity)
                if (not test or not run or case.get('case_id')!=test['case_id']
                    or case.get('runner_id')!=test['runner_id'] or case.get('runner_id')!=run.get('runner_id')):
                    errors.append(f'{run_id}: unknown or mismatched case {tid}');continue
                cases_by_execution[run['id']].append(case['case_id'])
                if (case.get('source_sha')!=run.get('source_sha') or case.get('phase')!=run.get('phase')
                    or case.get('output_artifact')!=run.get('output_artifact') or case.get('output_digest')!=run.get('output_digest')):
                    errors.append(f'{tid}: case execution binding mismatch')
                expected_sources={name:file_digest_bytes(read_at(root,case['source_sha'],name)) for name in test['source_paths']}
                if case.get('source_digests')!=expected_sources:errors.append(f'{tid}: stale test source digests')
                if case.get('phase')=='final_green':
                    if execution_report.get('scope')!=scope or execution_report.get('task_id')!=task_id:errors.append(f'{tid}: final scope mismatch')
                    if case['source_sha']!=sha or execution_report.get('candidate_sha')!=sha:errors.append(f'{tid}: stale final candidate')
                    if tid in finals:errors.append(f'{tid}: duplicate final case')
                    finals[tid]=case
                    if case['outcome']!='passed' or run['exit_code']!=0:errors.append(f'{tid}: required case did not pass')
                    if any(case['source_digests'].get(n)!=sources[n] for n in test['source_paths']):errors.append(f'{tid}: changed final test source')
                elif case.get('phase')=='red':
                    if case['outcome']=='failed' and case.get('failure_kind')=='behavior_assertion' and run['exit_code']!=0:
                        git(root,'merge-base','--is-ancestor',case['source_sha'],sha)
                        if case['source_sha']==sha:errors.append(f'{tid}: red equals final candidate')
                        reds.setdefault(tid,[]).append(case)
                else:errors.append(f'{tid}: unknown test phase')
            for eid,run in processes.items():
                expected={t['case_id'] for t in plan['tests'] if t['runner_id']==run['runner_id']}
                if set(cases_by_execution[eid])!=expected:errors.append(f'{run_id}: missing/unplanned collected cases for {run["runner_id"]}')
        static=trusted_context.get('static_checks') or {}
        if static.get('result')!='pass' or static.get('candidate_sha')!=sha:errors.append('mandatory static checks missing/failed/stale')
        semantic_criteria={c['id']:c for c in semantic.get('criteria',[]) if isinstance(c,dict) and 'id' in c}
        obligations={o['criterion_id']:o['required_types'] for o in plan['obligations']}
        for criterion in spec['criteria']:
            cid=criterion['id'];tests=[t for t in selected if cid in t['criterion_ids']]
            if scope=='task' and not tests:continue
            evidence=[]
            for test in tests:
                tid=test['id'];green=finals.get(tid);red=reds.get(tid,[])
                tdd='regression' if test['change_kind']=='regression' else 'red_green' if red and green else 'missing'
                if not green or green.get('outcome')!='passed':missing.append({'criterion_id':cid,'required_type':test['type'],'test_id':tid,'reason':'final passing execution missing'})
                if tdd=='missing':missing.append({'criterion_id':cid,'test_id':tid,'reason':'recognized behavior red and final green required'})
                evidence.append({'test_id':tid,'case_id':test['case_id'],'type':test['type'],'tdd':tdd,'red':red,'final_execution':green})
            rows.append({'criterion_id':cid,'verification_mode':criterion['verification_mode'],'required_types':obligations.get(cid,[]),'review':semantic_criteria.get(cid),'tests':evidence})
        if not errors and not missing:report['status']='pass'
    except (Invalid,OSError,KeyError,TypeError,ValueError) as exc:
        errors.append(str(exc))
    return report
