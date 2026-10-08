"""Structured traceability commands; shell dispatchers supply arguments only."""
from __future__ import annotations
import argparse
from contextlib import nullcontext
import json
import os
from pathlib import Path
import sys
from .adapters import git,run_tests
from .contracts import Invalid,load,slug
from .evidence import (accept_plan,contracts_at,load_accepted,record_test_review,source_changes,write_json)
from .service import check_completion
from verification.run import workflow_context


def main(argv=None):
    p=argparse.ArgumentParser(description='Spec-to-test provenance and completion')
    p.add_argument('--root',type=Path,default=Path(os.environ.get('ASK_ROOT','.')))
    sub=p.add_subparsers(dest='command',required=True)
    for name in ['validate-plan','accept-plan','record-review','run','check-completion','check-acceptance','migrate','record-result']:
        q=sub.add_parser(name);q.add_argument('work_id');q.add_argument('--candidate-sha');q.add_argument('--anchor-sha');q.add_argument('--revision',default='HEAD')
        if name=='accept-plan':
            q.add_argument('--reviewer',required=True);q.add_argument('--recorded-by',required=True);q.add_argument('--evidence',required=True)
        if name=='record-review':q.add_argument('--recorded-by',required=True);q.add_argument('--evidence',required=True)
        if name in {'run','check-completion'}:
            q.add_argument('--scope',choices=['task','workstream'],default='workstream');q.add_argument('--task-id')
        if name=='run':q.add_argument('--phase',choices=['red','final_green'],default='final_green')
        if name=='record-result':q.add_argument('--result',required=True);q.add_argument('--notes',default='')
    args=p.parse_args(argv);root=args.root.resolve();document=None
    try:
        if not slug(args.work_id):raise Invalid('invalid work_id')
        managed=args.command not in {'validate-plan','record-result'} or (args.command=='record-result' and args.result=='pass')
        with workflow_context(root,args.work_id) if managed else nullcontext():
            document,status=execute(args,root)
        print(json.dumps(document,indent=2))
        return status
    except (Invalid,OSError,ValueError,KeyError,TypeError) as exc:
        diagnostic=getattr(exc,'diagnostic',None)
        failure={'status':'fail','error':str(exc)}
        if diagnostic:failure['diagnostics']=getattr(exc,'diagnostics',[diagnostic])
        if diagnostic and document is not None and args.command=='record-result' and document.get('result')=='pass':
            write_json(root/'work'/args.work_id/'result.json',
                       dict(document,result='fail',notes=diagnostic['code']+': '+str(exc)))
        print(json.dumps(failure),file=sys.stderr);return 1


def execute(args,root):
    sha=git(root,'rev-parse','--verify',(args.candidate_sha or 'HEAD')+'^{commit}')
    anchor=git(root,'rev-parse','--verify',(args.anchor_sha or 'HEAD')+'^{commit}')
    if os.environ.get('ASK_INNER_LOOP_ROLE')=='worker' and args.command in {'accept-plan','record-review','record-result'}:raise Invalid('coordinator operation cannot be performed by worker')
    if args.command=='validate-plan':doc=contracts_at(root,args.work_id,args.revision)
    elif args.command=='accept-plan':doc=accept_plan(root,args.work_id,args.revision,args.reviewer,args.recorded_by,args.evidence)
    elif args.command=='record-review':doc=record_test_review(root,args.work_id,sha,anchor,args.evidence,args.recorded_by)
    elif args.command=='run':
        contracts=load_accepted(root,args.work_id,anchor)
        if args.phase=='final_green':load_accepted(root,args.work_id,anchor,sha)
        doc=run_tests(root,contracts,sha,args.scope,args.task_id,args.phase)
        expected=[t for t in contracts['plan']['tests'] if args.scope=='workstream' or t['id'] in next(s['test_ids'] for s in contracts['plan']['task_scopes'] if s['task_id']==args.task_id)]
        if (any(r['collection_status']!='ok' for r in doc['executions'])
            or (args.phase=='final_green' and len(doc['cases'])!=len(expected))
            or (args.phase=='final_green' and (any(r['exit_code']!=0 for r in doc['executions']) or any(c['outcome']!='passed' for c in doc['cases'])))
            or (args.phase=='red' and (not any(c['outcome']=='failed' and c['failure_kind']=='behavior_assertion' for c in doc['cases']) or any(c['outcome'] in {'error','unsupported_subtest'} for c in doc['cases'])))):
            return doc,1
    elif args.command=='record-result':
        if args.result=='pass':
            doc=check_completion(root,args.work_id,sha,anchor)
            if doc['status']!='pass':return doc,1
        doc={'work_id':args.work_id,'commit_sha':sha,'result':args.result,'notes':args.notes}
        write_json(root/'work'/args.work_id/'result.json',doc)
    elif args.command=='migrate':
        spec=root/'specs/current'/f'{args.work_id}.json';plan=root/'work'/args.work_id/'test-plan.json'
        if not spec.exists():
            write_json(spec,{'schema':'ask-spec/v1','work_id':args.work_id,'revision':1,'criteria':[]})
        if not plan.exists():write_json(plan,{'schema':'ask-test-plan/v1','work_id':args.work_id,'spec_digest':'REQUIRES_REVIEW','obligations':[],'tests':[],'runners':[],'task_scopes':[]})
        doc={'status':'migration_required','reason':'Fill canonical criteria/test obligations, independently review, commit, then accept-plan. Historical reports and consumer YAML preserved.'}
    else:doc=check_completion(root,args.work_id,sha,anchor,getattr(args,'scope','workstream'),getattr(args,'task_id',None))
    return doc,1 if doc.get('status') in {'fail','migration_required'} else 0
if __name__=='__main__':raise SystemExit(main())
