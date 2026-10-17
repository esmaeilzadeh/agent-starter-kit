"""Metadata for preexisting orchestration fixtures; no fabricated behavior evidence."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.agents/ask'))
from verification.traceability.contracts import POLICY,digest
from verification.traceability.evidence import accept_plan,inventory,load_accepted,record_test_review,write_json
from verification.yaml_lite import parse_yaml


def seed(root,work_id):
    graph_path=root/'work'/work_id/'inner-loop/tasks.yaml'
    graph=parse_yaml(graph_path.read_text()) if graph_path.exists() else {'tasks':[]}
    spec={'schema':'ask-spec/v1','work_id':work_id,'revision':1,'criteria':[{'id':'FIXTURE-CONFIG','given':'Disposable orchestration fixture','when':'Fixture CheckPlan and ownership are inspected','then':['Fixture configuration is isolated from production'],'verification_mode':'review','reason':'Nonbehavioral fixture metadata; behavior assertions belong to the enclosing real integration suite.','review_decision':{'decision':'APPROVED','reviewer':'fixture-reviewer','recorded_by':'fixture-coordinator','policy':POLICY}}]}
    plan={'schema':'ask-test-plan/v1','work_id':work_id,'spec_digest':digest(spec),'obligations':[],'tests':[],'runners':[],'task_scopes':[{'task_id':t['id'],'test_ids':[]} for t in graph['tasks']]}
    write_json(root/'specs/current'/f'{work_id}.json',spec);write_json(root/'work'/work_id/'test-plan.json',plan)
    with (root/'.gitignore').open('a') as stream:stream.write(f'\nwork/{work_id}/traceability/\n__pycache__/\n')


def accept(root,work_id):
    spec=json.loads((root/'specs/current'/f'{work_id}.json').read_text());plan=json.loads((root/'work'/work_id/'test-plan.json').read_text())
    path=f'work/{work_id}/traceability/plan-review.json'
    write_json(root/path,{'decision':'APPROVED','reviewer':'fixture-reviewer','spec_digest':digest(spec),'plan_digest':digest(plan)})
    accept_plan(root,work_id,'HEAD','fixture-reviewer','fixture-coordinator',path)
    subprocess.run(['git','add',f'work/{work_id}/traceability-accepted.json'],cwd=root,check=True)
    subprocess.run(['git','commit','-qm','pin fixture configuration contracts'],cwd=root,check=True)


def review(root,work_id,sha):
    contracts=load_accepted(root,work_id,'HEAD',sha);pin=contracts['pin'];inv=inventory(root,pin['contract_sha'],sha,contracts['plan'])
    doc={'schema':'ask-test-review/v2','reviewer':'fixture-reviewer','candidate_sha':sha,'base_sha':pin['contract_sha'],'spec_digest':pin['spec_digest'],'plan_digest':pin['plan_digest'],'scope':'workstream','task_id':None,'test_ids':[],'criterion_ids':['FIXTURE-CONFIG'],'source_digests':{},'inspected_sources':inv['inspected_sources'],'changed_cases':inv['changed_cases'],'inventory_exclusions':{n:'Existing harness fixture changes; reviewed by enclosing reliability suite' for n in inv['unmapped_cases']},'criteria':[{'id':'FIXTURE-CONFIG','coverage_decision':'APPROVED','assessment':'Disposable repository uses local isolated files; no production datastore','type_adequacy':{}}],'tests':[]}
    path=f'work/{work_id}/traceability/review-input.json';write_json(root/path,doc)
    record_test_review(root,work_id,sha,'HEAD',path,'fixture-coordinator')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['seed','accept','review']);p.add_argument('root',type=Path);p.add_argument('work_id');a=p.parse_args()
    if a.operation=='seed':seed(a.root,a.work_id)
    elif a.operation=='accept':accept(a.root,a.work_id)
    else:review(a.root,a.work_id,subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.root,text=True).strip())
