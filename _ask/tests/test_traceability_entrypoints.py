"""Public completion journeys in a disposable consumer, including a real CLI app."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.agents/ask'))
from traceability_fixture import Consumer

class EntrypointTests(unittest.TestCase):
    def consumer(self,**kwargs):c=Consumer(**kwargs);self.addCleanup(c.close);return c
    def require_pass(self,proc):self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
    def require_fail(self,proc):self.assertNotEqual(proc.returncode,0,proc.stdout+proc.stderr)
    def test_I09_runtime_agent_sync_preserves_candidate_tree(self):
        root=Path(__file__).resolve().parents[2]
        head=subprocess.run(['git','rev-parse','HEAD'],cwd=root,text=True,
                            capture_output=True,check=True).stdout.strip()
        with tempfile.TemporaryDirectory(prefix='ask-sync-clean-') as directory:
            candidate=Path(directory)/'candidate'
            subprocess.run(['git','worktree','add','--detach',str(candidate),head],cwd=root,
                           text=True,capture_output=True,check=True)
            try:
                env=os.environ.copy()
                env['ASK_WORK_ID']='revising-workbench'
                env['ASK_ROOT']=str(candidate)
                env['GIT_CONFIG_COUNT']='1'
                env['GIT_CONFIG_KEY_0']='init.defaultBranch'
                env['GIT_CONFIG_VALUE_0']='main'
                def projection_snapshot():
                    snapshot={}
                    for directory in ('.cursor/agents','.claude/agents','.codex/agents','.opencode/agents'):
                        for path in (candidate/directory).rglob('*'):
                            if path.is_file():
                                snapshot[path.relative_to(candidate).as_posix()]=path.read_bytes()
                    return snapshot
                def require_clean():
                    status=subprocess.run(['git','status','--porcelain','--untracked-files=all'],
                                          cwd=candidate,text=True,capture_output=True,check=True)
                    self.assertEqual(status.stdout,'',f'sync test dirtied candidate:\n{status.stdout}')

                before=projection_snapshot()
                failing_env=env.copy()
                failing_env['ASK_SYNC_TEST_FORCE_FAILURE']='1'
                failed=subprocess.run(['bash','_ask/tests/test-sync-runtime-agents.sh'],cwd=candidate,
                                      env=failing_env,text=True,capture_output=True)
                self.assertEqual(failed.returncode,97,failed.stdout+failed.stderr)
                self.assertIn('forced post-sync failure',failed.stderr)
                self.assertEqual(projection_snapshot(),before,'failed sync did not restore exact agent projections')
                require_clean()

                passed=subprocess.run(['bash','_ask/tests/test-sync-runtime-agents.sh'],cwd=candidate,
                                      env=env,text=True,capture_output=True)
                self.assertEqual(passed.returncode,0,passed.stdout+passed.stderr)
                self.assertEqual(projection_snapshot(),before,'successful sync changed agent projections')
                require_clean()

                consumer_env=env.copy()
                consumer_env['ASK_ROOT']=str(candidate)
                consumer=subprocess.run(['bash','_ask/tests/test-askit-first-run.sh'],cwd=candidate,
                                        env=consumer_env,text=True,capture_output=True)
                self.assertEqual(consumer.returncode,0,consumer.stdout+consumer.stderr)
                self.assertEqual(projection_snapshot(),before,'first-run consumer changed runtime agent projections')
                require_clean()
            finally:
                subprocess.run(['git','worktree','remove','--force',str(candidate)],cwd=root,
                               text=True,capture_output=True,check=False)
    def test_I08_integration_accepts_reviewed_contract_amended_after_task_base(self):
        c=self.consumer(tasks=True)
        base=c.sha
        plan_review={'decision':'APPROVED','reviewer':'fixture-independent',
                     'spec_digest':c.contracts['pin']['spec_digest'],
                     'plan_digest':c.contracts['pin']['plan_digest']}
        c.write('work/w/traceability/plan-review-amendment.json',plan_review)
        graph=(c.root/'work/w/inner-loop/tasks.yaml').read_text()
        c.write('work/w/inner-loop/tasks.yaml',graph.replace('owned_paths: [app.py]',
                                                              'owned_paths: [app.py, test_app.py]'))
        graph_revision=c.commit('amend reviewed task ownership')
        from verification.traceability.evidence import accept_plan,load_accepted
        accept_plan(c.root,'w',graph_revision,'fixture-independent','fixture-coordinator',
                    'work/w/traceability/plan-review-amendment.json')
        candidate=c.commit('pin reviewed task amendment')
        c.sha=candidate;c.contracts=load_accepted(c.root,'w',candidate,candidate)

        self.require_pass(c.command('traceability','run','w','--candidate-sha',c.red_sha,
                                    '--anchor-sha',candidate,'--scope','task','--task-id','a',
                                    '--phase','red'))
        review=c.make_review();review.update(scope='task',task_id='a')
        c.write('work/w/traceability/review-input.json',review)
        self.require_pass(c.command('traceability','record-review','w','--candidate-sha',candidate,
                                    '--anchor-sha',candidate,'--scope','task','--task-id','a',
                                    '--evidence','work/w/traceability/review-input.json',
                                    '--recorded-by','fixture-coordinator'))
        self.require_pass(c.command('traceability','run','w','--candidate-sha',candidate,
                                    '--anchor-sha',candidate,'--scope','task','--task-id','a'))

        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
        from inner_loop.evidence import Candidate,NotIntegrable,verify_candidate
        result=Candidate({}, {'work_id':'w','task_id':'a','base_sha':base,
                              'candidate_sha':candidate},'fixture-result-digest')
        try:evidence=verify_candidate(c.root,result)
        except NotIntegrable:evidence=None
        self.assertIsNotNone(evidence,'authority-approved amended candidate must integrate')
        self.assertEqual(evidence['result'],'pass',evidence)
        self.assertEqual(evidence['runner_sha'],base)

        unamended=self.consumer(tasks=True)
        unamended_base=unamended.sha
        self.require_pass(unamended.command('traceability','run','w','--candidate-sha',unamended.red_sha,
                                            '--anchor-sha',unamended_base,'--scope','task','--task-id','a',
                                            '--phase','red'))
        unamended_review=unamended.make_review();unamended_review.update(scope='task',task_id='a')
        unamended.write('work/w/traceability/review-input.json',unamended_review)
        self.require_pass(unamended.command('traceability','record-review','w','--candidate-sha',unamended_base,
                                            '--anchor-sha',unamended_base,'--scope','task','--task-id','a',
                                            '--evidence','work/w/traceability/review-input.json',
                                            '--recorded-by','fixture-coordinator'))
        self.require_pass(unamended.command('traceability','run','w','--candidate-sha',unamended_base,
                                            '--anchor-sha',unamended_base,'--scope','task','--task-id','a'))
        unamended_result=Candidate({}, {'work_id':'w','task_id':'a','base_sha':unamended_base,
                                        'candidate_sha':unamended_base},'fixture-result-digest')
        self.assertEqual(verify_candidate(unamended.root,unamended_result)['result'],'pass')

        untrusted=self.consumer()
        untrusted_base=untrusted.sha
        pin=json.loads((untrusted.root/'work/w/traceability-accepted.json').read_text())
        pin['plan_review']['assessment']='candidate-only change'
        untrusted.write('work/w/traceability-accepted.json',pin)
        untrusted_candidate=untrusted.commit('attempt candidate-only acceptance change')
        untrusted_result=Candidate({}, {'work_id':'w','task_id':'a','base_sha':untrusted_base,
                                       'candidate_sha':untrusted_candidate},'fixture-result-digest')
        with self.assertRaisesRegex(NotIntegrable,'candidate acceptance document differs from coordinator authority'):
            verify_candidate(untrusted.root,untrusted_result)

    def test_I05_all_normal_entrypoints_reject_omitted_e2e(self):
        c=self.consumer(omit_e2e=True,tasks=True)
        self.require_fail(c.command('verify'))
        self.require_fail(c.command('record-result','--work-id','w','--commit-sha',c.sha,'--result','pass'))
        self.require_fail(c.command('check-workstream','w','--acceptance'))
        self.require_pass(c.command('inner-loop','run','w'))
        state=json.loads((c.root/'work/w/inner-loop/state.json').read_text())
        c.write('work/w/inner-loop/results/a.json',{'schema':'ask-task-result/v2','work_id':'w','task_id':'a','base_sha':state['tasks']['a']['base_sha'],'candidate_sha':c.sha,'tdd':{'seam':'public render','red':{'command':'test','exit_code':1,'output':'AssertionError'},'green':{'command':'test','exit_code':0,'output':'OK'}},'exemption':None})
        c.write('work/w/inner-loop/evidence/review.md','Fixture reviewer approves task boundary.\n')
        self.require_pass(c.command('inner-loop','record-review','w','a','--reviewer','fixture-reviewer','--evidence','work/w/inner-loop/evidence/review.md'))
        self.require_fail(c.command('inner-loop','run','w'))
        self.assertEqual(json.loads((c.root/'work/w/inner-loop/state.json').read_text())['tasks']['a']['status'],'running')
        self.require_fail(c.command('traceability','run','w','--candidate-sha',c.red_sha,'--phase','final_green'))
    def test_I06_preflight_failure_replaces_old_pass(self):
        c=self.consumer();self.require_pass(c.command('verify'))
        receipt_path=c.root/'work/w/traceability'/('static-'+c.sha+'.json')
        receipt=json.loads(receipt_path.read_text());receipt['checks']=[{'id':'syntax','tier':'mandatory','command':"python3 -c 'import app'",'status':'fail','exit_code':7}]
        receipt_path.write_text(json.dumps(receipt))
        self.require_fail(c.command('traceability','check-completion','w'))
        self.require_pass(c.command('verify'))
        c.write('app.py','broken dirty source\n');self.require_fail(c.command('verify'))
        report=json.loads((c.root/'verification-result.json').read_text());self.assertEqual(report['result'],'fail')
        self.require_fail(c.command('record-result','--work-id','w','--commit-sha',c.sha,'--result','pass'))
    def test_I07_complete_evidence_agrees_across_entrypoints(self):
        c=self.consumer(tasks=True);self.require_pass(c.command('verify'))
        self.require_pass(c.command('traceability','check-completion','w'))
        self.require_pass(c.command('check-workstream','w','--acceptance'))
        self.require_pass(c.command('record-result','--work-id','w','--commit-sha',c.sha,'--result','pass','--notes','Literal "$text" and quotes preserved'))
        result=json.loads((c.root/'work/w/result.json').read_text());self.assertEqual(result['result'],'pass')
        self.assertEqual(result['notes'],'Literal "$text" and quotes preserved')
        self.require_pass(c.command('inner-loop','run','w'))
        state=json.loads((c.root/'work/w/inner-loop/state.json').read_text())
        history={}
        for phase,report in [('red',c.red),('green',c.green)]:
            execution=report['executions'][0]
            history[phase]={'command':'python3 -m unittest test_app','exit_code':execution['exit_code'],'output':(c.root/execution['output_artifact']).read_text()}
        c.write('work/w/inner-loop/results/a.json',{'schema':'ask-task-result/v2','work_id':'w','task_id':'a','base_sha':state['tasks']['a']['base_sha'],'candidate_sha':c.sha,'tdd':dict(history,seam='public render and separate CLI process'),'exemption':None})
        c.write('work/w/inner-loop/evidence/review.md','Independent fixture reviewer approves exact task boundary.\n')
        self.require_pass(c.command('inner-loop','record-review','w','a','--reviewer','fixture-reviewer','--evidence','work/w/inner-loop/evidence/review.md'))
        self.require_pass(c.command('inner-loop','run','w'))
        state=json.loads((c.root/'work/w/inner-loop/state.json').read_text())
        self.assertEqual(state['tasks']['a']['status'],'integrated')
        self.assertEqual(state['coordinator_sha'],c.sha)
        self.assertEqual(c.git('rev-parse','HEAD'),c.sha)
        self.require_pass(c.command('check-workstream','w','--acceptance'))
    def test_E01_public_red_review_verify_record_accept_journey(self):
        c=self.consumer()
        self.require_pass(c.command('traceability','run','w','--candidate-sha',c.red_sha,'--phase','red'))
        self.require_pass(c.command('traceability','record-review','w','--candidate-sha',c.sha,'--evidence','work/w/traceability/review-input.json','--recorded-by','fixture-coordinator'))
        self.require_pass(c.command('verify'))
        self.assertTrue((c.root/'work/w/traceability/completion.json').exists(), 'Verify must produce criterion evidence')
        completion=json.loads((c.root/'work/w/traceability/completion.json').read_text())
        self.assertEqual(completion['status'],'pass');row=completion['criterion_evidence'][0]
        self.assertEqual({t['type'] for t in row['tests']},{'unit','e2e'})
        self.assertTrue(all(t['final_execution']['outcome']=='passed' for t in row['tests']))
        self.require_pass(c.command('record-result','--work-id','w','--commit-sha',c.sha,'--result','pass'))
        self.require_pass(c.command('check-workstream','w','--acceptance'))
    def test_E02_omitted_e2e_names_missing_case_and_never_records_pass(self):
        c=self.consumer(omit_e2e=True);self.require_fail(c.command('verify'))
        report=json.loads((c.root/'work/w/traceability/completion.json').read_text())
        self.assertTrue(any(x.get('criterion_id')=='C1' and x.get('test_id')=='E' for x in report['missing_evidence']))
        self.require_fail(c.command('record-result','--work-id','w','--commit-sha',c.sha,'--result','pass'))
        self.assertFalse((c.root/'work/w/result.json').exists())
        self.require_fail(c.command('check-workstream','w','--acceptance'))
if __name__=='__main__':unittest.main()
