"""Explicit metadata migration preserves YAML/history and rejects old capabilities."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.agents/ask'))
from traceability_fixture import Consumer,SOURCE

class MigrationTests(unittest.TestCase):
    def test_I08_missing_contract_migration_preserves_history_and_config(self):
        c=Consumer();self.addCleanup(c.close)
        config=(c.root/'.agents/verification.yaml').read_bytes()
        c.write('work/w/legacy-results.json',{'schema':'ask-task-result/v1','result':'pass'})
        c.git('rm','specs/current/w.json','work/w/test-plan.json','work/w/traceability-accepted.json');c.commit('simulate legacy metadata')
        result=c.command('verify');self.assertNotEqual(result.returncode,0)
        self.assertIn('migration_required',result.stdout+result.stderr)
        result=c.command('traceability','migrate','w');self.assertNotEqual(result.returncode,0)
        self.assertEqual((c.root/'.agents/verification.yaml').read_bytes(),config)
        self.assertEqual(json.loads((c.root/'work/w/legacy-results.json').read_text())['schema'],'ask-task-result/v1')
        self.assertEqual(json.loads((c.root/'specs/current/w.json').read_text())['criteria'],[])
        c.git('rm','-r','.agents/ask/verification/traceability');sha=c.commit('old pinned runner')
        sys.path.insert(0,str(SOURCE/'_ask/scripts'))
        from inner_loop.evidence import Candidate,NotIntegrable,verify_candidate
        candidate=Candidate({}, {'work_id':'w','task_id':'a','base_sha':sha,'candidate_sha':sha},'result-digest')
        with self.assertRaisesRegex(NotIntegrable,'migration_required'):verify_candidate(c.root,candidate)
        report=json.loads(next(c.root.glob('work/w/inner-loop/evidence/verify-*/integration.json')).read_text())
        self.assertIn('migration_required',report.get('error',''), 'Retained failed migration report must name missing capability')
    def test_I09_templates_and_stage_commands_share_contract_versions(self):
        from verification.traceability.coverage import validate_plan
        spec=json.loads((SOURCE/'_ask/templates/spec.json').read_text());plan=json.loads((SOURCE/'_ask/templates/test-plan.json').read_text())
        self.assertEqual(validate_plan(spec,plan),[])
        for number in ['02','03','05','06','07','09','10']:
            stage=next((SOURCE/'.agents/ask/stages').glob(number+'-*.md'))
            self.assertIn('_ask/docs/spec-test-traceability.md',stage.read_text(),str(stage))
        binding=SOURCE/'.cursor/skills/kit-09-verify/SKILL.md'
        self.assertIn('Structured test evidence',binding.read_text())
if __name__=='__main__':unittest.main()
