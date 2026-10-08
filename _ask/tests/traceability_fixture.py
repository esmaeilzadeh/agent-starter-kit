"""Disposable consumer with real domain and separate-process CLI assertions."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from verification.traceability.adapters import run_tests
from verification.traceability.contracts import POLICY,digest
from verification.traceability.evidence import accept_plan,inventory,load_accepted,record_test_review,source_digests,write_json

SOURCE=Path(__file__).resolve().parents[2]
class Consumer:
    def __init__(self,omit_e2e=False,tasks=False):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.git('init','-q','-b','agent/w');self.git('config','user.email','test@example.com');self.git('config','user.name','Test')
        self.write('.gitignore','__pycache__/\nverification-result.json\nwork/w/traceability/\nwork/w/inner-loop/state.*\nwork/w/inner-loop/results/\nwork/w/inner-loop/evidence/\n')
        shutil.copytree(SOURCE/'.agents/ask/verification',self.root/'.agents/ask/verification',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(SOURCE/'_ask/scripts',self.root/'_ask/scripts',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(SOURCE/'ask',self.root/'ask')
        self.write(POLICY,(SOURCE/POLICY).read_text())
        self.write('.agents/verification.yaml',"schema: ask-checkplan/v1\nno_production_datastore: true\nchecks:\n  - id: syntax\n    tier: mandatory\n    command: python3 -c 'import app'\n")
        self.write('app.py',"import sys\ndef render(value): return value\nif __name__=='__main__': print(render(sys.argv[1]))\n")
        self.write('test_app.py',"import subprocess,sys,unittest\nfrom app import render\nclass Cases(unittest.TestCase):\n def test_unit(self): self.assertEqual(render('hello'),'HELLO')\n def test_cli(self):\n  p=subprocess.run([sys.executable,'app.py','hello'],capture_output=True,text=True)\n  self.assertEqual(p.returncode,0)\n  self.assertEqual(p.stdout.strip(),'HELLO')\n")
        self.spec={'schema':'ask-spec/v1','work_id':'w','revision':1,'criteria':[{'id':'C1','given':'lowercase text','when':'rendered through domain or CLI','then':['uppercase text is returned'],'verification_mode':'tests'}]}
        self.plan={'schema':'ask-test-plan/v1','work_id':'w','spec_digest':digest(self.spec),'obligations':[{'criterion_id':'C1','required_types':['unit','e2e']}],
                   'runners':[{'id':'r','adapter':'unittest','argv':['python3','-m','unittest','test_app']}],'task_scopes':[],
                   'tests':[{'id':name,'criterion_ids':['C1'],'type':kind,'change_kind':'new','scenario':{'given':'hello','when':'rendered '+kind,'then':['HELLO']},'expected_assertions':[{'criterion_id':'C1','checks':['Exact HELLO output']}],'runner_id':'r','case_id':'test_app.Cases.test_'+method,'source_paths':['test_app.py']} for name,kind,method in [('U','unit','unit'),('E','e2e','cli')]]}
        if omit_e2e: self.plan['runners'][0]['argv'][-1]='test_app.Cases.test_unit'
        if tasks:
            self.write('work/w/inner-loop/tasks.yaml','schema: ask-inner-loop-tasks/v1\nwork_id: w\ntasks:\n  - id: a\n    depends_on: []\n    owned_paths: [app.py]\n')
            self.plan['task_scopes']=[{'task_id':'a','test_ids':['U','E']}]
        self.write('work/w/plan.md','# Plan\nExecute explicit unit and separate-process CLI cases.\n')
        self.write('specs/current/w.json',self.spec);self.write('work/w/test-plan.json',self.plan)
        self.red_sha=self.commit('faulty implementation with behavior assertions')
        decision={'decision':'APPROVED','reviewer':'fixture-independent','spec_digest':digest(self.spec),'plan_digest':digest(self.plan)}
        self.write('work/w/traceability/plan-review.json',decision)
        accept_plan(self.root,'w',self.red_sha,'fixture-independent','fixture-coordinator','work/w/traceability/plan-review.json')
        self.commit('pin accepted obligations')
        self.contracts=load_accepted(self.root,'w','HEAD')
        self.red=run_tests(self.root,self.contracts,self.red_sha,phase='red')
        self.write('app.py',"import sys\ndef render(value): return value.upper()\nif __name__=='__main__': print(render(sys.argv[1]))\n")
        self.sha=self.commit('implement uppercase behavior');self.contracts=load_accepted(self.root,'w',self.sha,self.sha)
        self.review=self.make_review()
        self.write('work/w/traceability/review-input.json',self.review)
        self.record=record_test_review(self.root,'w',self.sha,self.sha,'work/w/traceability/review-input.json','fixture-coordinator')
        self.green=run_tests(self.root,self.contracts,self.sha)
    def git(self,*args):return subprocess.check_output(['git',*args],cwd=self.root,text=True,stderr=subprocess.PIPE).strip()
    def write(self,name,doc):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(doc,indent=2)+'\n' if isinstance(doc,dict) else doc)
    def commit(self,msg):self.git('add','.');self.git('commit','-qm',msg);return self.git('rev-parse','HEAD')
    def close(self):self.tmp.cleanup()
    def make_review(self):
        plan=self.contracts['plan'];base=self.contracts['pin']['contract_sha']
        inv=inventory(self.root,base,self.sha,plan)
        return {'schema':'ask-test-review/v1','reviewer':'fixture-independent','candidate_sha':self.sha,'base_sha':base,'spec_digest':digest(self.spec),'plan_digest':digest(plan),'source_digests':source_digests(self.root,self.sha,plan),
                'inspected_sources':inv['inspected_sources'],'changed_cases':inv['changed_cases'],'inventory_exclusions':{},
                'criteria':[{'id':'C1','coverage_decision':'APPROVED','assessment':'Exact uppercase output checked at domain and public CLI','type_adequacy':{kind:{'decision':'APPROVED','assessment':assessment} for kind,assessment in [('unit','Calls public render with known literal result'),('e2e','Separate app process checks documented stdout and exit status')]}}],
                'tests':[{'id':t['id'],'decision':'APPROVED','assertion_assessment':'Checks literal HELLO, not output derived from render','counterexample':'Returning the input unchanged fails exact output comparison','tdd_continuity_assessment':'Same test source and exact output assertions in red and green'} for t in plan['tests']]}
    def context(self):return {'root':self.root,'candidate_sha':self.sha,'scope':'workstream','task_id':None,'static_checks':{'result':'pass','candidate_sha':self.sha}}
    def command(self,*args):
        env={k:v for k,v in os.environ.items() if not k.startswith(('ASK_TRACEABILITY_','VERIFY_')) and k not in {'ASK_ROOT','ASK_WORK_ID'}}
        return subprocess.run([str(self.root/'ask'),*args],cwd=self.root,text=True,capture_output=True,env=dict(env,PYTHONDONTWRITEBYTECODE='1'))
