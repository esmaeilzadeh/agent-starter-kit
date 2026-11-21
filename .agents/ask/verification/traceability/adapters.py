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
from verification.environment import build_environment, private_directory, private_open, warn_tracked_logs


def git(root,*args):
    result=subprocess.run(['git',*args],cwd=root,capture_output=True,text=True)
    if result.returncode:raise Invalid(result.stderr.strip())
    return result.stdout.strip()


def run_tests(root, contracts, candidate_sha, scope='workstream', task_id=None, phase='final_green'):
    root=Path(root).resolve();plan=contracts['plan'];spec=contracts['spec']
    warn_tracked_logs(root)
    sha=git(root,'rev-parse','--verify',candidate_sha+'^{commit}')
    selected=scoped_tests(plan,scope,task_id)
    run_id=uuid.uuid4().hex
    directory=private_directory(root/'work'/spec['work_id']/'traceability'/'runs'/run_id, root)
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
                start = '.'
                if 'discover' in argv:
                    try: start = argv[argv.index('-s') + 1]
                    except (ValueError, IndexError): pass
                test_root = (checkout / start).resolve()
                if not test_root.is_relative_to(checkout):
                    raise Invalid('unittest collection root escapes candidate')
                python_path = os.pathsep.join((str(checkout/'.agents'/'ask'), str(test_root)))
                env=build_environment(os.environ, runner.get('env_allow', []), {
                    'PYTHONDONTWRITEBYTECODE':'1', 'PYTHONPATH':python_path,
                    'ASK_ROOT':str(checkout), 'ASK_TRACEABILITY_RUNTIME_ROOT':str(root),
                    'ASK_TRACEABILITY_RUN_DIR':str(directory),
                })
                # Coordinator/worker mode belongs to the outer CLI command.
                # Do not leak that one-command role into the isolated test
                # process, whose fixtures exercise both coordinator and worker
                # operations explicitly.
                env.pop('ASK_INNER_LOOP_ROLE', None)
                with private_open(log, 'w') as stream:
                    try:
                        selection=[t['case_id'] for t in expected] if scope=='task' else None
                        actual_argv=[sys.executable,str(runner_file),str(raw),json.dumps(selection),*argv[3:]]
                        proc=subprocess.run(actual_argv,cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
                        code=proc.returncode
                    except subprocess.TimeoutExpired:code=124
                try:data=json.loads(raw.read_text())
                except (OSError,ValueError):data={'cases':[],'collection_status':'error'}
                artifact=str(log.relative_to(root));log_digest=file_digest(log)
                execution={'id':eid,'runner_id':runner['id'],'argv':argv,'adapter':'unittest','actual_argv':actual_argv,'interpreter':sys.executable,'interpreter_version':sys.version,'phase':phase,'source_sha':sha,'exit_code':code,
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
    with private_open(directory/'results.json', 'w') as stream:
        stream.write(json.dumps(report,indent=2)+'\n')
    if os.environ.get('ASK_TRACEABILITY_CRASH_AT') == 'after_report_publication':
        os._exit(81)
    from .evidence import write_json
    import fcntl
    ledger=directory.parent.parent/'executions.json'
    with (directory.parent.parent/'executions.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        entries=json.loads(ledger.read_text()) if ledger.exists() else []
        entries.append({'run_id':run_id,'digest':digest(report),'phase':phase,'scope':scope,'task_id':task_id,'candidate_sha':sha,'spec_digest':digest(spec),'plan_digest':digest(plan)})
        write_json(ledger,entries)
    if os.environ.get('ASK_TRACEABILITY_CRASH_AT') == 'after_ledger_insertion':
        os._exit(82)
    return report
