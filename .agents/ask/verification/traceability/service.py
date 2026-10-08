"""Coordinator operations shared by the thin CLI and the pinned Verify runner."""
from __future__ import annotations
import json
from pathlib import Path
from .adapters import git
from .completion import evaluate_completion
from .contracts import Invalid,digest,load,slug
from .evidence import load_accepted,source_changes,write_json


def reports(root,work_id,contracts,sha,scope,task_id):
    runtime=Path(root)/'work'/work_id/'traceability'
    try:ledger=json.loads((runtime/'executions.json').read_text())
    except (OSError,ValueError):raise Invalid('no coordinator-executed case evidence')
    matching=[e for e in ledger if e.get('spec_digest')==digest(contracts['spec']) and e.get('plan_digest')==digest(contracts['plan'])]
    finals=[e for e in matching if e['phase']=='final_green' and e['candidate_sha']==sha and e['scope']==scope and e['task_id']==task_id]
    selected=[e for e in matching if e['phase']=='red']+finals[-1:]
    docs=[]
    for entry in selected:
        if not slug(entry['run_id']):raise Invalid('invalid run identity')
        doc=load(runtime/'runs'/entry['run_id']/'results.json')
        if digest(doc)!=entry['digest']:raise Invalid('changed coordinator-executed report')
        docs.append(doc)
    return docs


def check_completion(root,work_id,sha=None,anchor_sha=None,scope='workstream',task_id=None,static=None,runtime_root=None):
    root=Path(root).resolve();runtime_root=Path(runtime_root or root).resolve();sha=sha or git(root,'rev-parse','HEAD');anchor_sha=anchor_sha or sha
    path=runtime_root/'work'/work_id/'traceability'/'completion.json'
    report={'schema':'ask-completion/v1','status':'fail','scope':scope,'task_id':task_id,'candidate_sha':sha,'input_digests':{},'criterion_evidence':[],'missing_evidence':[],'errors':[],'execution_artifacts':[]}
    try:
        contracts=load_accepted(root,work_id,anchor_sha,sha)
        if root==runtime_root and (git(root,'rev-parse','HEAD')!=sha or source_changes(root,work_id)):raise Invalid('dirty or non-current candidate source')
        review=load(runtime_root/'work'/work_id/'traceability'/'reviews'/(sha+'.json'))
        runs=reports(runtime_root,work_id,contracts,sha,scope,task_id)
        if static is None:
            receipt=load(runtime_root/'work'/work_id/'traceability'/('static-'+sha+'.json'))
            if receipt.get('candidate_sha')!=sha or receipt.get('result')!='pass':raise Invalid('static verification missing/failed/stale')
            from verification.plan import load_plan,expand_plan
            from .contracts import file_digest
            checks=expand_plan(root,load_plan(root))
            identity=digest({'checks':checks,'yaml_digest':file_digest(root/'.agents/verification.yaml')})
            if receipt.get('checkplan_digest')!=identity:raise Invalid('stale static CheckPlan')
            executed=receipt.get('checks',[])
            check_identity=lambda cs:[(c.get('id',c.get('command')),c.get('tier','mandatory'),c.get('command')) for c in cs]
            if (check_identity(executed)!=check_identity(checks) or any(type(c.get('exit_code')) is not int or c['exit_code']!=0 or c.get('status')!='pass' for c in executed) or receipt.get('runner_digest')!=file_digest(Path(__file__).parents[1]/'run.py')):raise Invalid('static check execution failed or differs from pinned runner/CheckPlan')
            for check in executed:
                artifact=(runtime_root/check.get('evidence','')).resolve()
                if not artifact.is_relative_to((runtime_root/'work'/work_id/'traceability').resolve()) or file_digest(artifact)!=check.get('output_digest'):raise Invalid('changed/missing static execution log')
            static=receipt
        report=evaluate_completion(contracts,review,runs,{'root':runtime_root,'candidate_sha':sha,'scope':scope,'task_id':task_id,'static_checks':static,'detached_candidate':root!=runtime_root})
    except (Invalid,OSError,ValueError,KeyError,TypeError) as exc:report['errors'].append(str(exc))
    write_json(path,report)
    return report
