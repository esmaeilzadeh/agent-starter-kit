"""Actual unittest cases on immutable revisions; setup errors cannot be TDD red."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.agents/ask'))
from verification.traceability.adapters import run_tests
from verification.traceability.contracts import digest
from traceability_support import supports_node_tests

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.git('init','-q');self.git('config','user.email','test@example.com');self.git('config','user.name','Test')
        (self.root/'.gitignore').write_text('work/\n__pycache__/\n')
        self.write("import unittest\nclass Cases(unittest.TestCase):\n def test_behavior(self): self.assertEqual(2, 1)\n def test_skip(self): self.skipTest('unavailable')\n def test_error(self): raise RuntimeError('setup')\n")
        self.red=self.commit()
        self.contract={'spec':{'work_id':'w'},'plan':{'tests':[{'id':n,'runner_id':'r','case_id':'test_app.Cases.test_'+n,'source_paths':['test_app.py']} for n in ['behavior','skip','error']], 'runners':[{'id':'r','adapter':'unittest','argv':['python3','-m','unittest','test_app']}], 'task_scopes':[]}}
    def git(self,*args):return subprocess.check_output(['git',*args],cwd=self.root,text=True,stderr=subprocess.PIPE).strip()
    def write(self,value):(self.root/'test_app.py').write_text(value)
    def commit(self):self.git('add','.');self.git('commit','-qm','fixture');return self.git('rev-parse','HEAD')
    def run_at(self,sha,phase='final_green'):return run_tests(self.root,self.contract,sha,phase=phase)

    def test_I01_actual_outcomes_and_collection_errors_are_not_exit_code_claims(self):
        report=self.run_at(self.red,'red');cases={c['test_id']:c for c in report['cases']}
        self.assertEqual(set(cases),{'behavior','skip','error'})
        self.assertEqual(cases['behavior']['outcome'],'failed');self.assertEqual(cases['behavior']['failure_kind'],'behavior_assertion')
        self.assertEqual(cases['skip']['outcome'],'skipped');self.assertEqual(cases['error']['outcome'],'error')
        self.contract['plan']['runners'][0]['argv'][-1]='missing_module'
        report=self.run_at(self.red)
        self.assertEqual(report['executions'][0]['collection_status'],'error')
        self.contract['plan']['runners'][0]['adapter']='unknown'
        with self.assertRaisesRegex(ValueError,'unsupported'):self.run_at(self.red)

    def test_I02_red_and_green_retain_real_case_revision_and_log(self):
        red=self.run_at(self.red,'red')
        self.assertTrue(red['cases'], 'Red must contain the executed behavior case')
        self.write("import unittest\nclass Cases(unittest.TestCase):\n def test_behavior(self): self.assertEqual(1, 1)\n def test_skip(self): self.skipTest('unavailable')\n def test_error(self): raise RuntimeError('setup')\n")
        green_sha=self.commit();green=self.run_at(green_sha)
        a=next(c for c in red['cases'] if c['test_id']=='behavior');b=next(c for c in green['cases'] if c['test_id']=='behavior')
        self.assertEqual((a['source_sha'],b['source_sha']),(self.red,green_sha));self.assertEqual(b['outcome'],'passed')
        self.assertNotEqual(a['source_digests'],b['source_digests'])
        self.assertIn('AssertionError',(self.root/a['output_artifact']).read_text())
        self.assertEqual(len(self.git('worktree','list','--porcelain').split('worktree '))-1,1)

    @unittest.skipUnless(supports_node_tests(), 'Node.js 22.18 or later required')
    def test_node_rejects_empty_files_import_errors_and_hooks_as_red(self):
        self.contract['plan']['runners']=[{
            'id':'r','adapter':'node-test','argv':['node','--test','test_app.cjs'],
        }]
        test_file=self.root/'test_app.cjs'
        self.contract['plan']['tests']=[{
            'id':'U','runner_id':'r','case_id':'test_app.cjs::unit','source_paths':['test_app.cjs'],
        }]
        for source in ('', "require('./unavailable.cjs')", """
const { test, beforeEach } = require('node:test')
beforeEach(() => require('node:assert/strict').fail())
test('unit', () => {})
"""):
            with self.subTest(source=source):
                test_file.write_text(source)
                report=self.run_at(self.commit(),'red')
                self.assertEqual(report['executions'][0]['collection_status'],'error')
                self.assertNotIn('behavior_assertion',[case['failure_kind'] for case in report['cases']])


    @unittest.skipUnless(shutil.which('node'), 'Node.js unavailable')
    def test_jest_environment_only_recognizes_assertions_from_test_body(self):
        runner=Path(__file__).resolve().parents[2]/'.agents/ask/verification/traceability/jest_runner.cjs'
        base=self.root/'base.cjs'
        base.write_text('module.exports = class {}')
        events=self.root/'events.json'
        script="""
const [runner, file] = process.argv.slice(1)
const Environment = require(runner)
const suite = { name: 'Controller', parent: { name: 'ROOT' } }
const assertion = { matcherResult: { pass: true } }
const test = name => ({ name, parent: suite, errors: [[assertion, new Error()]] })
async function main() {
  const env = new Environment({}, { testPath: file })
  const behavior = test('assertion')
  await env.handleTestEvent({ name: 'test_fn_failure', test: behavior, error: assertion })
  await env.handleTestEvent({ name: 'test_done', test: behavior })
  const setup = test('setup')
  await env.handleTestEvent({ name: 'hook_failure', test: setup, error: assertion })
  await env.handleTestEvent({ name: 'test_done', test: setup })
  await env.handleTestEvent({ name: 'run_finish' })
}
main().catch(error => { console.error(error); process.exitCode = 1 })
"""
        subprocess.run(['node','-e',script,str(runner),str(self.root/'app.spec.ts')],
                       cwd=self.root,check=True,
                       env=dict(os.environ,ASK_JEST_ENVIRONMENT=str(base),ASK_JEST_EVENTS=str(events)))
        result=json.loads(events.read_text())
        self.assertTrue(result['collectionFailed'])
        self.assertEqual([case['case_id'] for case in result['cases']],
                         ['app.spec.ts::Controller assertion','app.spec.ts::Controller setup'])
        self.assertEqual([case['failure_kind'] for case in result['cases']],
                         ['behavior_assertion','setup_or_runtime_error'])


if __name__=='__main__':unittest.main()
