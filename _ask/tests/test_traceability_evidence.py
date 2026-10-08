"""Shared completion behavior, including evidence and semantic-review mutations."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.agents/ask'))
from verification.traceability.completion import evaluate_completion
from verification.traceability.contracts import digest
from verification.traceability.evidence import record_test_review,write_json
from traceability_fixture import Consumer

class EvidenceTests(unittest.TestCase):
    def setUp(self):self.c=Consumer();self.addCleanup(self.c.close)
    def evaluate(self,records=None,review=None,context=None):
        return evaluate_completion(self.c.contracts,review or self.c.record,records or [self.c.red,self.c.green],context or self.c.context())
    def persist(self,report):
        runtime=self.c.root/'work/w/traceability';write_json(runtime/'runs'/report['run_id']/'results.json',report)
        ledger=json.loads((runtime/'executions.json').read_text())
        for entry in ledger:
            if entry['run_id']==report['run_id']:entry['digest']=digest(report)
        write_json(runtime/'executions.json',ledger)
    def passing(self):self.assertEqual(self.evaluate()['status'],'pass')
    def test_U04_every_required_outcome_collection_and_case_identity_matters(self):
        self.passing()
        for outcome in ['skipped','expected_failure','unexpected_success','error','failed']:
            green=copy.deepcopy(self.c.green);green['cases'][0]['outcome']=outcome;self.persist(green)
            self.assertEqual(self.evaluate([self.c.red,green])['status'],'fail',outcome)
        for mutate in [lambda r:r.update(cases=[]),lambda r:r['cases'].append(r['cases'][0]),lambda r:r['executions'][0].update(collection_status='error')]:
            green=copy.deepcopy(self.c.green);mutate(green);self.persist(green);self.assertEqual(self.evaluate([self.c.red,green])['status'],'fail')
    def test_U05_setup_failure_and_missing_red_never_satisfy_tdd(self):
        self.passing();red=copy.deepcopy(self.c.red);red['cases'][0]['failure_kind']='setup_or_runtime_error';self.persist(red)
        self.assertEqual(self.evaluate([red,self.c.green])['status'],'fail')
        self.assertEqual(self.evaluate([self.c.green])['status'],'fail')
        c=Consumer(behavior_change=False,change_kind='changed');self.addCleanup(c.close)
        for test in c.review['tests']:
            test['tdd_exemption']={'kind':'documentation-only','reason':'Only explanatory test comment changed; assertions and application behavior are unchanged','reviewer_ack':True,'decision':'APPROVED'}
        c.write('work/w/traceability/review-input.json',c.review)
        record=record_test_review(c.root,'w',c.sha,c.sha,'work/w/traceability/review-input.json','fixture-coordinator')
        result=evaluate_completion(c.contracts,record,[c.green],c.context())
        self.assertEqual(result['status'],'pass',result)
    def test_U06_blanket_approval_missing_type_and_counterexample_are_rejected(self):
        self.passing()
        for mutate in [lambda r:r.update(criteria=[]),lambda r:r['criteria'][0].update(type_adequacy={}),lambda r:r['tests'][0].update(counterexample=''),lambda r:r['tests'][0].update(decision='REJECTED')]:
            record=copy.deepcopy(self.c.record);mutate(record['review']);record['review_digest']=digest(record['review']);write_json(self.c.root/'work/w/traceability/reviews'/(self.c.sha+'.json'),record)
            self.assertEqual(self.evaluate(review=record)['status'],'fail')
    def test_U07_mutated_log_source_run_identity_or_revision_is_rejected(self):
        self.passing()
        for field,value in [('run_id','wrong'),('candidate_sha',self.c.red_sha),('plan_digest','wrong')]:
            green=copy.deepcopy(self.c.green);green[field]=value;self.persist(green);self.assertEqual(self.evaluate([self.c.red,green])['status'],'fail')
        path=self.c.root/self.c.green['cases'][0]['output_artifact'];path.write_text('forged output')
        self.assertEqual(self.evaluate()['status'],'fail')
    def test_I03_changed_candidate_invalidates_bound_semantic_review(self):
        self.passing();self.c.write('test_app.py',(self.c.root/'test_app.py').read_text()+'\n# changed reviewed source\n');sha=self.c.commit('change source')
        context=self.c.context();context['candidate_sha']=sha
        self.assertEqual(self.evaluate(context=context)['status'],'fail')
    def test_I04_task_scope_cannot_replace_final_or_narrow_accepted_obligations(self):
        self.passing();green=copy.deepcopy(self.c.green);green.update(scope='task',task_id='partial')
        self.assertEqual(self.evaluate([self.c.red,green])['status'],'fail')
        from verification.traceability.evidence import load_accepted
        self.c.plan['tests']=self.c.plan['tests'][:1];self.c.write('work/w/test-plan.json',self.c.plan);sha=self.c.commit('remove e2e')
        with self.assertRaisesRegex(ValueError,'missing_test_type|accepted obligations'):load_accepted(self.c.root,'w',self.c.sha,sha)

if __name__=='__main__':unittest.main()
