"""Public completion journeys in a disposable consumer, including a real CLI app."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.agents/ask'))
from traceability_fixture import Consumer

class EntrypointTests(unittest.TestCase):
    def consumer(self,**kwargs):c=Consumer(**kwargs);self.addCleanup(c.close);return c
    def require_pass(self,proc):self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
    def require_fail(self,proc):self.assertNotEqual(proc.returncode,0,proc.stdout+proc.stderr)
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
