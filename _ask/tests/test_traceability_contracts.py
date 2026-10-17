"""Public contract validation: explicit obligations, scenarios and task scopes."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.agents/ask'))


def contracts():
    root=Path(__file__).resolve().parents[2]
    spec=json.loads((root/'_ask/templates/spec.json').read_text())
    plan=json.loads((root/'_ask/templates/test-plan.json').read_text())
    return spec,plan


class ContractTests(unittest.TestCase):
    def validate(self,spec,plan,graph=None):
        from verification.traceability.coverage import validate_plan
        return validate_plan(spec,plan,graph)

    def test_U01_rejects_malformed_contract_fields_and_duplicate_ids(self):
        spec,plan=contracts()
        self.assertEqual(self.validate(spec,plan),[])
        for mutate in [lambda s,p:s['criteria'].append(copy.deepcopy(s['criteria'][0])),
                       lambda s,p:s['criteria'][0].update(then=[]),
                       lambda s,p:p['tests'][0].update(criterion_ids=['UNKNOWN']),
                       lambda s,p:p['tests'][0].update(source_paths='bad'),
                       lambda s,p:p.update(schema='unsupported')]:
            s,p=copy.deepcopy(spec),copy.deepcopy(plan);mutate(s,p)
            self.assertTrue(self.validate(s,p))

    def test_U02_unit_does_not_cover_required_e2e_or_orphan_assertions(self):
        spec,plan=contracts();plan['tests']=plan['tests'][:1]
        errors=self.validate(spec,plan)
        self.assertTrue(any(e.code=='missing_test_type' and e.required_type=='e2e' for e in errors))
        spec,plan=contracts();plan['tests'][0]['expected_assertions']=[]
        self.assertTrue(self.validate(spec,plan))

    def test_U03_task_scopes_must_match_accepted_graph_and_cover_all_tests(self):
        spec,plan=contracts();plan['task_scopes']=[{'task_id':'a','test_ids':['INV-U01']}]
        self.assertTrue(self.validate(spec,plan,{'tasks':[{'id':'a'}]}))
        plan['task_scopes'][0]['test_ids'].append('INV-E01')
        self.assertEqual(self.validate(spec,plan,{'tasks':[{'id':'a'}]}),[])
        self.assertTrue(self.validate(spec,plan,{'tasks':[{'id':'b'}]}))
    def test_I04_baseline_regression_exemptions_are_task_scoped_and_assigned(self):
        spec,plan=contracts();plan['task_scopes']=[{'task_id':'a','test_ids':['INV-U01','INV-E01']}]
        graph={'tasks':[{'id':'a'}]}
        plan['task_scoped_baseline_regression_exemptions']={'a':['INV-U01']}
        self.assertEqual(self.validate(spec,plan,graph),[])
        plan['task_scoped_baseline_regression_exemptions']={'a':['MISSING']}
        self.assertTrue(self.validate(spec,plan,graph))
        plan['task_scoped_baseline_regression_exemptions']={'unknown':['INV-U01']}
        self.assertTrue(self.validate(spec,plan,graph))

if __name__=='__main__': unittest.main()
