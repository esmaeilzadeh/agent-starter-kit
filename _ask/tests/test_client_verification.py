"""Client security boundaries for static and instrumented verification."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ASK = Path(__file__).resolve().parents[2] / '.agents' / 'ask'
sys.path.insert(0, str(ASK))
from verification.environment import build_environment
from verification.plan import expand_plan
from verification.traceability.adapters import run_tests
from verification.environment import warn_tracked_logs, private_directory, private_open
from contextlib import redirect_stderr
from io import StringIO
from traceability_fixture import Consumer


class ClientTests(unittest.TestCase):
    def test_allowlist_and_owned_metadata(self):
        caller = {
            'PATH': '/trusted/bin', 'HOME': '/home/test', 'JIRA_PERSONAL_TOKEN': 'dummy-token',
            'BASH_ENV': '/tmp/poison', 'PYTHONPATH': '/tmp/poison', 'EXTRA_OK': 'visible',
            'ASK_ROOT': '/tmp/poison', 'ASK_TRACEABILITY_RUNTIME_ROOT': '/tmp/poison',
        }
        env = build_environment(caller, ['EXTRA_OK'], {
            'ASK_ROOT': '/candidate', 'PYTHONDONTWRITEBYTECODE': '1',
            'ASK_TRACEABILITY_RUNTIME_ROOT': '/private/run',
        })
        self.assertEqual(env['PATH'], '/trusted/bin')
        self.assertEqual(env.get('EXTRA_OK'), 'visible')
        self.assertEqual(env['ASK_ROOT'], '/candidate')
        self.assertEqual(env['ASK_TRACEABILITY_RUNTIME_ROOT'], '/private/run')
        for name in ('JIRA_PERSONAL_TOKEN', 'BASH_ENV', 'PYTHONPATH'):
            self.assertNotIn(name, env)
        with self.assertRaises(ValueError):
            build_environment(caller, ['PYTHONPATH'], {})
        with self.assertRaises(ValueError):
            build_environment(caller, ['BASH_ENV'], {})
        with self.assertRaises(ValueError):
            build_environment(caller, ['ASK_ROOT'], {'ASK_ROOT': '/candidate'})
        with self.assertRaises(ValueError):
            build_environment(caller, ['bad-name'], {})

    def test_checkplan_environment(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            preset = root / '.agents/ask/verification/presets'
            preset.mkdir(parents=True)
            check = root / 'checks/run.sh'
            check.parent.mkdir(); check.write_text('#!/bin/sh\nexit 0\n'); check.chmod(0o755)
            (preset / 'sample.yaml').write_text('checks:\n  - id: scripts\n    glob: checks/*.sh\n    env_allow: [EXTRA_OK]\n')
            expanded = expand_plan(root, {'presets': ['sample']})
            self.assertEqual(expanded[0].get('env_allow'), ['EXTRA_OK'])
            (preset / 'sample.yaml').write_text("checks:\n  - id: direct\n    command: 'true'\n    env_allow: [EXTRA_OK]\n")
            self.assertEqual(expand_plan(root, {'presets': ['sample']})[0]['env_allow'], ['EXTRA_OK'])

    def test_instrumented_environment(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, text=True, stderr=subprocess.PIPE).strip()
            git('init', '-q'); git('config', 'user.email', 'test@example.com'); git('config', 'user.name', 'Test')
            (root / '.gitignore').write_text('work/\n__pycache__/\n')
            source = root / 'test_env.py'
            source.write_text('''import os, sys, unittest\nfrom pathlib import Path\nclass Env(unittest.TestCase):\n def test_environment(self):\n  self.assertEqual(os.environ.get("EXTRA_OK"), "visible")\n  self.assertNotIn("JIRA_PERSONAL_TOKEN", os.environ)\n  self.assertNotIn("BASH_ENV", os.environ)\n  self.assertNotIn("/poison", os.environ.get("PYTHONPATH", ""))\n  self.assertEqual(os.environ.get("ASK_ROOT"), str(Path.cwd()))\n  self.assertIn(str(Path.cwd() / ".agents" / "ask"), os.environ["PYTHONPATH"].split(os.pathsep))\n''')
            package = root / '.agents/ask/verification'
            package.mkdir(parents=True)
            (package / '__init__.py').write_text('')
            (package / 'environment.py').write_text((ASK / 'verification/environment.py').read_text())
            git('add', '.'); git('commit', '-qm', 'fixture'); sha = git('rev-parse', 'HEAD')
            contract = {'spec': {'work_id': 'w'}, 'plan': {
                'tests': [{'id': 'T', 'runner_id': 'r', 'case_id': 'test_env.Env.test_environment', 'source_paths': ['test_env.py']}],
                'runners': [{'id': 'r', 'adapter': 'unittest', 'argv': ['python3', '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_env.py'], 'env_allow': ['EXTRA_OK']}],
                'task_scopes': [{'task_id': 'task', 'test_ids': ['T']}],
            }}
            old_umask = os.umask(0)
            try:
                previous = {key: os.environ.get(key) for key in ('EXTRA_OK', 'JIRA_PERSONAL_TOKEN', 'BASH_ENV', 'PYTHONPATH')}
                os.environ.update(EXTRA_OK='visible', JIRA_PERSONAL_TOKEN='dummy-token', BASH_ENV='/tmp/poison', PYTHONPATH='/tmp/poison')
                try:
                    report = run_tests(root, contract, sha, scope='task', task_id='task')
                finally:
                    for key, value in previous.items():
                        if value is None: os.environ.pop(key, None)
                        else: os.environ[key] = value
            finally:
                os.umask(old_umask)
            self.assertEqual(report['executions'][0]['exit_code'], 0, (root / report['executions'][0]['output_artifact']).read_text())
            directory = root / 'work/w/traceability/runs' / report['run_id']
            self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
            self.assertEqual((directory / (report['executions'][0]['id'] + '.log')).stat().st_mode & 0o777, 0o600)
            self.assertEqual((directory / (report['executions'][0]['id'] + '.json')).stat().st_mode & 0o777, 0o600)
            self.assertEqual((directory / 'results.json').stat().st_mode & 0o777, 0o600)

    def test_private_retained_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            previous_umask = os.umask(0)
            try:
                raw = private_directory(root / 'private/raw')
                with private_open(raw / 'capture.log', 'w') as stream: stream.write('raw')
            finally: os.umask(previous_umask)
            self.assertEqual(raw.stat().st_mode & 0o777, 0o700)
            self.assertEqual((raw / 'capture.log').stat().st_mode & 0o777, 0o600)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=root, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=root, check=True)
            legacy = root / 'work/w/traceability/old.log'
            legacy.parent.mkdir(parents=True); legacy.write_text('dummy legacy output\n')
            subprocess.run(['git', 'add', '-f', str(legacy.relative_to(root))], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'legacy log'], cwd=root, check=True)
            before = subprocess.check_output(['git', 'ls-files', '-s'], cwd=root)
            warning = StringIO()
            with redirect_stderr(warning): warn_tracked_logs(root)
            self.assertIn('explicit cleanup', warning.getvalue())
            self.assertEqual(subprocess.check_output(['git', 'ls-files', '-s'], cwd=root), before)
        repo = ASK.parents[1]
        raw = subprocess.run(['git', 'check-ignore', '--no-index', 'work/client-security-hardening/traceability/runs/run/raw.log'], cwd=repo, capture_output=True)
        summary = subprocess.run(['git', 'check-ignore', '--no-index', 'work/client-security-hardening/traceability/runs/run/results.json'], cwd=repo, capture_output=True)
        self.assertEqual(raw.returncode, 0, raw.stdout + raw.stderr)
        self.assertNotEqual(summary.returncode, 0)

    def test_trusted_verify_journey(self):
        c = Consumer()
        self.addCleanup(c.close)
        c.git('checkout', '-b', 'main')
        c.write('.agents/verification.yaml', "schema: ask-checkplan/v1\nno_production_datastore: true\nchecks:\n  - id: environment\n    tier: mandatory\n    command: python3 -c \"import os; assert os.environ.get('SAFE_EXTRA') == 'visible'; assert 'JIRA_PERSONAL_TOKEN' not in os.environ; assert 'BASH_ENV' not in os.environ\"\n    env_allow: [SAFE_EXTRA]\n")
        c.commit('configure safe verifier extras')
        env = {k:v for k,v in os.environ.items() if k not in {'ASK_ROOT','ASK_WORK_ID','SAFE_EXTRA','JIRA_PERSONAL_TOKEN','BASH_ENV','PYTHONPATH'}}
        env.update(SAFE_EXTRA='visible', JIRA_PERSONAL_TOKEN='dummy-token', BASH_ENV='/tmp/no-such-startup-file', PYTHONPATH='/tmp/poison')
        run = subprocess.run([str(c.root/'ask'), 'verify'], cwd=c.root, env=env, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        help_run = subprocess.run([str(c.root/'ask'), 'verify', '--help'], cwd=c.root, env=env, text=True, capture_output=True)
        self.assertEqual(help_run.returncode, 0, help_run.stdout + help_run.stderr)
        self.assertIn('filesystem and network access', help_run.stdout)
        self.assertIn('isolated CI', help_run.stdout)


if __name__ == '__main__':
    unittest.main()
