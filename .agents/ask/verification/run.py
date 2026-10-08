"""Pinned CheckPlan and spec-to-test runner; language commands live in presets."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import uuid

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from verification.isolation import check_isolation
from verification.plan import expand_plan,load_plan
from verification.traceability.adapters import git,run_tests
from verification.traceability.contracts import Invalid,digest,file_digest
from verification.traceability.evidence import load_accepted,source_changes,write_json
from verification.traceability.service import check_completion


def main():
    root=Path(os.environ.get('ASK_ROOT') or HERE.parents[3]).resolve()
    runtime=Path(os.environ.get('ASK_TRACEABILITY_RUNTIME_ROOT') or root).resolve()
    out_dir=Path(os.environ.get('VERIFY_OUT_DIR') or root)
    out_json=Path(os.environ.get('VERIFY_JSON') or out_dir/'verification-result.json')
    sha=git(root,'rev-parse','HEAD')
    branch=git(root,'rev-parse','--abbrev-ref','HEAD')
    work_id=os.environ.get('ASK_WORK_ID') or (branch.split('/')[1] if branch.startswith('agent/') else None)
    anchor=os.environ.get('ASK_TRACEABILITY_ANCHOR_SHA') or sha
    scope=os.environ.get('ASK_TRACEABILITY_SCOPE','workstream');task_id=os.environ.get('ASK_TRACEABILITY_TASK_ID')
    doc={'schema':'ask-verify-result/v1','commit_sha':sha,'result':'fail','checks':[]}
    receipt={'candidate_sha':sha,'result':'fail'}
    completion=None
    checkout=None;tmp=None
    try:
        plan=load_plan(root);checks=expand_plan(root,plan)
        if not checks or not any(c.get('tier','mandatory')=='mandatory' for c in checks):raise Invalid('empty CheckPlan or zero mandatory checks')
        check_isolation(root,plan,[c.get('command','') for c in checks])
        receipt['checkplan_digest']=digest({'checks':checks,'yaml_digest':file_digest(root/'.agents/verification.yaml')})
        contracts=None
        if work_id:
            contracts=load_accepted(root,work_id,anchor,sha)
            if root==runtime and source_changes(root,work_id):raise Invalid('dirty candidate source')
            # Both behavior and static checks execute committed immutable source.
            if root==runtime:
                tmp=tempfile.TemporaryDirectory(prefix='ask-static-');checkout=Path(tmp.name)/'candidate'
                git(root,'worktree','add','--detach',str(checkout),sha)
            cases=run_tests(runtime,contracts,sha,scope,task_id)
        check_root=checkout or root
        cache={}
        if contracts:
            for runner in contracts['plan']['runners']:
                runs=[r for r in cases['executions'] if r['runner_id']==runner['id']]
                if len(runs)==1 and scope=='workstream':
                    cache[tuple(runner['argv'])]=runs[0]['exit_code'] if runs[0]['collection_status']=='ok' else 1
        command_cache={}
        run_id=uuid.uuid4().hex
        static_dir=runtime/'work'/work_id/'traceability'/'static-runs'/run_id if work_id else None
        if static_dir:static_dir.mkdir(parents=True)
        for check in checks:
            command=check['command'];print(f'verify: running: {command}',flush=True)
            artifact=None
            if command in command_cache:code,artifact=command_cache[command]
            elif tuple(shlex.split(command)) in cache and command==shlex.join(shlex.split(command)):
                code=cache[tuple(shlex.split(command))]
                match=next(r for r in cases['executions'] if tuple(r['argv'])==tuple(shlex.split(command)))
                artifact=match['output_artifact']
            else:
                env=dict(os.environ,ASK_ROOT=str(check_root),PYTHONDONTWRITEBYTECODE='1')
                if static_dir:
                    logfile=static_dir/(str(len(doc['checks']))+'.log')
                    with logfile.open('w') as stream:proc=subprocess.run(['bash','-lc',command],cwd=check_root,env=env,stdout=stream,stderr=subprocess.STDOUT)
                    print(logfile.read_text(),end='',flush=True);artifact=str(logfile.relative_to(runtime))
                else:proc=subprocess.run(['bash','-lc',command],cwd=check_root,env=env)
                code=proc.returncode
            command_cache[command]=(code,artifact)
            doc['checks'].append({'id':check.get('id',command),'tier':check.get('tier','mandatory'),'command':command,'status':'pass' if code==0 else 'fail','exit_code':code,'evidence':artifact or '', 'output_digest':file_digest(runtime/artifact) if artifact else None})
        if any(c['exit_code'] for c in doc['checks']):raise Invalid('required candidate verification failed')
        if git(check_root,'rev-parse','HEAD')!=sha or (work_id and source_changes(check_root,work_id)):raise Invalid('candidate source/CheckPlan changed during verification')
        receipt.update(result='pass',checks=doc['checks'],runner_digest=file_digest(HERE/'run.py'),run_id=run_id)
        if work_id:
            write_json(runtime/'work'/work_id/'traceability'/('static-'+sha+'.json'),receipt)
            completion=check_completion(root,work_id,sha,anchor,scope,task_id,receipt,runtime)
            if completion['status']!='pass':raise Invalid('spec-to-test completion failed: '+json.dumps(completion))
        doc['result']='pass'
    except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
        doc['error']=str(exc);print('verify: '+str(exc),file=sys.stderr)
        if work_id and completion is None:
            completion={'schema':'ask-completion/v1','status':'fail','scope':scope,'task_id':task_id,'candidate_sha':sha,'input_digests':{},'criterion_evidence':[],'missing_evidence':[],'errors':[str(exc)],'execution_artifacts':[]}
            write_json(runtime/'work'/work_id/'traceability'/'completion.json',completion)
            write_json(runtime/'work'/work_id/'traceability'/('static-'+sha+'.json'),receipt)
    finally:
        if checkout:
            git(root,'worktree','remove','--force',str(checkout))
        if tmp:tmp.cleanup()
        write_json(out_json,doc)
    print(json.dumps(doc,indent=2));print('verify: commit_sha='+sha)
    return 0 if doc['result']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())
