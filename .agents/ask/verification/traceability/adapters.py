"""Execute instrumented cases in disposable, immutable candidate worktrees."""
from __future__ import annotations
import json
import os
import shutil
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid
from . import CAPABILITY
from .contracts import Invalid, digest, file_digest
from .coverage import scoped_tests, supported_runner
from verification.environment import build_environment, private_directory, private_open, warn_tracked_logs


RUNNER_FILES = {
    'unittest': 'unittest_runner.py',
    'node-test': 'node_test_runner.cjs',
    'jest': 'jest_runner.cjs',
}


def adapter_digest(adapters, hash_file):
    # Preserve the identity of previously published Python-only evidence.
    if not adapters or adapters == {'unittest'}:
        return hash_file(RUNNER_FILES['unittest'])
    return digest({adapter: hash_file(RUNNER_FILES[adapter]) for adapter in adapters})


def git(root,*args):
    result=subprocess.run(['git',*args],cwd=root,capture_output=True,text=True)
    if result.returncode:raise Invalid(result.stderr.strip())
    return result.stdout.strip()


def run_isolated(command, cwd, env, log, timeout):
    with subprocess.Popen(command, cwd=cwd, env=env, stdout=log,
                          stderr=subprocess.STDOUT, start_new_session=True) as process:
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            return 124


def prepare_jest(checkout, env, log):
    npm = shutil.which('npm', path=env.get('PATH'))
    if npm is None:
        raise Invalid('jest adapter requires npm on PATH')
    for name in ('package.json', 'package-lock.json'):
        path = checkout / name
        if not path.is_file() or path.is_symlink():
            raise Invalid('jest adapter requires a committed regular ' + name)
    modules = checkout / 'node_modules'
    if modules.is_symlink() or git(checkout, 'ls-files', '--', 'node_modules'):
        raise Invalid('jest dependency install requires untracked node_modules/')
    if subprocess.run(['git', 'check-ignore', '-q', 'node_modules/'], cwd=checkout).returncode:
        raise Invalid('jest dependency install requires node_modules/ in .gitignore')
    command = [npm, 'ci', '--ignore-scripts', '--include=dev', '--no-audit', '--no-fund']
    if run_isolated(command, checkout, env, log, timeout=300):
        raise Invalid('npm ci failed for the Jest candidate; see the private verification log')
    return npm



def run_tests(root, contracts, candidate_sha, scope='workstream', task_id=None, phase='final_green'):
    root=Path(root).resolve();plan=contracts['plan'];spec=contracts['spec']
    warn_tracked_logs(root)
    sha=git(root,'rev-parse','--verify',candidate_sha+'^{commit}')
    selected=scoped_tests(plan,scope,task_id)
    run_id=uuid.uuid4().hex
    directory=private_directory(root/'work'/spec['work_id']/'traceability'/'runs'/run_id, root)
    report={'schema':'ask-test-results/v1','run_id':run_id,'scope':scope,'task_id':task_id,
            'candidate_sha':sha,'spec_digest':digest(spec),'plan_digest':digest(plan),
            'executions':[],'cases':[]}
    with tempfile.TemporaryDirectory(prefix='ask-cases-') as tmp:
        checkout=Path(tmp)/'candidate';git(root,'worktree','add','--detach',str(checkout),sha)
        npm=None
        try:
            for runner in plan['runners']:
                expected=[t for t in selected if t['runner_id']==runner['id']]
                if not expected:continue
                argv=runner['argv']
                adapter=runner['adapter']
                if not supported_runner(runner):
                    raise Invalid('unsupported runner adapter/invocation')
                eid=uuid.uuid4().hex;raw=directory/(eid+'.json');log=directory/(eid+'.log')
                start = '.'
                if adapter=='unittest' and argv[3]=='discover':
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
                runner_file=Path(__file__).with_name(RUNNER_FILES[adapter])
                selection=[t['case_id'] for t in expected] if scope=='task' else None
                if adapter in {'node-test', 'jest'}:
                    interpreter=shutil.which('node', path=env.get('PATH'))
                    if interpreter is None:
                        raise Invalid(f'{adapter} adapter requires Node.js on PATH')
                    try:
                        version=subprocess.run([interpreter,'--version'],env=env,cwd=checkout,
                                               capture_output=True,text=True,timeout=10,check=True).stdout.strip()
                        release=tuple(map(int,version.removeprefix('v').split('.')[:2]))
                    except (subprocess.SubprocessError,ValueError) as exc:
                        raise Invalid(f'could not determine the Node.js version for {adapter}') from exc
                    if adapter=='node-test' and release < (22,18):
                        raise Invalid('node-test adapter requires Node.js 22.18 or later')
                    selectors=argv[2:]
                else:
                    interpreter,version,selectors=sys.executable,sys.version,argv[3:]
                with private_open(log, 'w') as stream:
                    if adapter=='jest':
                        if npm is None:
                            npm=prepare_jest(checkout,env,stream)
                        selectors=[npm,argv[2],*argv[4:]]
                    actual_argv=[interpreter,str(runner_file),str(raw),json.dumps(selection),*selectors]
                    code=run_isolated(actual_argv,checkout,env,stream,timeout=300)
                data={'cases':[],'collection_status':'error'}
                if code in (0,1):
                    try: data=json.loads(raw.read_text())
                    except (OSError,ValueError): pass
                artifact=str(log.relative_to(root));log_digest=file_digest(log)
                execution={'id':eid,'runner_id':runner['id'],'argv':argv,'adapter':adapter,'actual_argv':actual_argv,'interpreter':interpreter,'interpreter_version':version,'phase':phase,'source_sha':sha,'exit_code':code,
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
    report['runner_identity']={
        'capability':CAPABILITY,
        'adapter_digest':adapter_digest({run['adapter'] for run in report['executions']},
                                        lambda name:file_digest(Path(__file__).with_name(name))),
    }
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
