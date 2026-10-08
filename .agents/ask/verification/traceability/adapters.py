"""Execute instrumented cases in disposable, immutable candidate worktrees."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid
from . import CAPABILITY
from .contracts import Invalid, digest, file_digest
from .coverage import scoped_tests


def git(root,*args):
    result=subprocess.run(['git',*args],cwd=root,capture_output=True,text=True)
    if result.returncode:raise Invalid(result.stderr.strip())
    return result.stdout.strip()


def run_tests(root, contracts, candidate_sha, scope='workstream', task_id=None, phase='final_green'):
    root=Path(root).resolve();plan=contracts['plan'];spec=contracts['spec']
    sha=git(root,'rev-parse','--verify',candidate_sha+'^{commit}')
    selected=scoped_tests(plan,scope,task_id)
    run_id=uuid.uuid4().hex
    directory=root/'work'/spec['work_id']/'traceability'/'runs'/run_id
    directory.mkdir(parents=True)
    report={'schema':'ask-test-results/v1','run_id':run_id,'scope':scope,'task_id':task_id,
            'candidate_sha':sha,'spec_digest':digest(spec),'plan_digest':digest(plan),
            'runner_identity':{'capability':CAPABILITY,'adapter_digest':file_digest(Path(__file__).with_name('unittest_runner.py'))},
            'executions':[],'cases':[]}
    runner_file=Path(__file__).with_name('unittest_runner.py')
    with tempfile.TemporaryDirectory(prefix='ask-cases-') as tmp:
        checkout=Path(tmp)/'candidate';git(root,'worktree','add','--detach',str(checkout),sha)
        try:
            for runner in plan['runners']:
                expected=[t for t in selected if t['runner_id']==runner['id']]
                if not expected:continue
                argv=runner['argv']
                if runner['adapter']!='unittest' or len(argv)<4 or argv[1:3]!=['-m','unittest']:
                    raise Invalid('unsupported runner adapter/invocation')
                eid=uuid.uuid4().hex;raw=directory/(eid+'.json');log=directory/(eid+'.log')
                env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
                with log.open('w') as stream:
                    try:
                        proc=subprocess.run([sys.executable,str(runner_file),str(raw),*argv[3:]],cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
                        code=proc.returncode
                    except subprocess.TimeoutExpired:code=124
                try:data=json.loads(raw.read_text())
                except (OSError,ValueError):data={'cases':[],'collection_status':'error'}
                artifact=str(log.relative_to(root));log_digest=file_digest(log)
                execution={'id':eid,'runner_id':runner['id'],'argv':argv,'adapter':'unittest','phase':phase,'source_sha':sha,'exit_code':code,
                           'collection_status':data['collection_status'],'output_artifact':artifact,'output_digest':log_digest}
                report['executions'].append(execution)
                known={t['case_id']:t for t in plan['tests'] if t['runner_id']==runner['id']}
                for case in data['cases']:
                    test=known.get(case['case_id'])
                    sources={name:file_digest(checkout/name) for name in (test or {}).get('source_paths',[])}
                    report['cases'].append(dict(case,test_id=test['id'] if test else None,runner_id=runner['id'],execution_id=eid,phase=phase,source_sha=sha,source_digests=sources,output_artifact=artifact,output_digest=log_digest))
            if git(checkout,'rev-parse','HEAD')!=sha or git(checkout,'status','--porcelain'):
                raise Invalid('candidate source changed during test execution')
        finally:git(root,'worktree','remove','--force',str(checkout))
    (directory/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
