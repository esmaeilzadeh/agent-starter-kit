"""Public evidence preserves provenance without publishing captured output."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from inner_loop.checkpoint import read_checkpoint
from inner_loop.clean import dirty_paths
from inner_loop.evidence import NotIntegrable
from inner_loop.milestones import publish_milestones, records, migrate_runtime
from inner_loop.state import cas_init, load_state, _publish_state


class Milestones(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q', '-b', 'agent/w')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.org')
        (self.root / 'README').write_text('source\n')
        (self.root / '.gitignore').write_text('work/*/inner-loop/state.lock\nwork/*/traceability/runs/*/*.log\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        self.state = cas_init(self.root, 'w', ['T1', 'T2'], self.git('rev-parse', 'HEAD'))
        self.guard = patch('inner_loop.recovery.require_safe')
        self.guard.start()
        self.addCleanup(self.guard.stop)
        self.graph = patch('inner_loop.graph.load_graph', return_value={'work_id': 'w', 'tasks': []})
        self.graph.start()
        self.addCleanup(self.graph.stop)

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.DEVNULL).decode().strip()

    def test_pending_backfill_noop_and_source_identity(self):
        candidate = self.state['coordinator_sha']
        commit = publish_milestones(self.root, 'w')
        state = load_state(self.root, 'w')
        self.assertNotEqual(commit, candidate)
        self.assertEqual(state['tasks']['T2']['status'], 'pending')
        record = json.loads((self.root / 'work/w/progress/T1.json').read_bytes())
        self.assertIsNone(record['source_candidate_sha'])
        self.assertEqual(state['milestone_publications'][-1]['source_sha'], candidate)
        self.assertEqual(publish_milestones(self.root, 'w'), commit)
        self.assertEqual(load_state(self.root, 'w')['revision'], state['revision'])

    def test_conflicting_staged_and_symlink_paths_preserved(self):
        path = self.root / 'unrelated'
        path.write_text('user bytes')
        self.git('add', 'unrelated')
        with self.assertRaises(NotIntegrable):
            publish_milestones(self.root, 'w')
        self.assertEqual(self.git('diff', '--cached', '--name-only'), 'unrelated')
        self.assertEqual(path.read_text(), 'user bytes')
        self.git('reset', '-q', '--', 'unrelated')
        path.unlink()
        directory = self.root / 'work/w/progress'
        directory.mkdir()
        (directory / 'T1.json').symlink_to(self.root / 'README')
        with self.assertRaises((NotIntegrable, RuntimeError)):
            publish_milestones(self.root, 'w')
        self.assertEqual((self.root / 'README').read_text(), 'source\n')

    def test_precommit_exact_staged_retry(self):
        generated = records(self.root, 'w', read_checkpoint(self.root, 'w'))
        for name, raw in generated.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            self.git('add', '--', name)
        publish_milestones(self.root, 'w')
        self.assertEqual(self.git('diff', '--cached', '--name-only'), '')

    def test_postcommit_retry_folds_once(self):
        source = self.state['coordinator_sha']
        generated = records(self.root, 'w', read_checkpoint(self.root, 'w'))
        for name, raw in generated.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.git('add', 'work/w/progress')
        self.git('commit', '-qm', 'publication before crash')
        published = self.git('rev-parse', 'HEAD')
        self.assertEqual(publish_milestones(self.root, 'w'), published)
        self.assertEqual(load_state(self.root, 'w')['milestone_publications'][0]['source_sha'], source)
        revision = load_state(self.root, 'w')['revision']
        self.assertEqual(publish_milestones(self.root, 'w'), published)
        self.assertEqual(load_state(self.root, 'w')['revision'], revision)

    def test_actual_process_crashes_retry_before_and_after_commit(self):
        script = """
from pathlib import Path
from inner_loop import recovery, graph
from inner_loop.milestones import publish_milestones
recovery.require_safe = lambda *a, **kw: None
graph.load_graph = lambda *a: {'tasks': []}
publish_milestones(Path(ROOT), 'w')
""".replace('ROOT', repr(str(self.root)))
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / 'scripts'),
                   ASK_MILESTONE_CRASH_AT='before_commit')
        crashed = subprocess.run([sys.executable, '-c', script], env=env, capture_output=True)
        self.assertEqual(crashed.returncode, 78, crashed.stderr)
        env['ASK_MILESTONE_CRASH_AT'] = 'after_commit'
        crashed = subprocess.run([sys.executable, '-c', script], env=env, capture_output=True)
        self.assertEqual(crashed.returncode, 77, crashed.stderr)
        self.assertFalse((self.root / '.git/index.lock').exists())
        published = self.git('rev-parse', 'HEAD')
        self.assertEqual(publish_milestones(self.root, 'w'), published)
        revision = load_state(self.root, 'w')['revision']
        self.assertEqual(publish_milestones(self.root, 'w'), published)
        self.assertEqual(load_state(self.root, 'w')['revision'], revision)

    def test_source_advance_and_active_writer_refuse(self):
        (self.root / 'README').write_text('changed\n')
        self.git('add', 'README')
        self.git('commit', '-qm', 'unauthorized source')
        with self.assertRaisesRegex(NotIntegrable, 'source advanced'):
            publish_milestones(self.root, 'w')
        self.state['coordinator_sha'] = self.git('rev-parse', 'HEAD')
        self.state['tasks']['T1']['status'] = 'running'
        _publish_state(self.root, 'w', self.state)
        with self.assertRaisesRegex(NotIntegrable, 'writer is active'):
            publish_milestones(self.root, 'w')

    def test_clean_gate_retained_ignored_tamper_and_staged(self):
        self.assertEqual(dirty_paths(self.root), [])
        path = self.root / 'work/w/traceability/runs/r/out.log'
        path.parent.mkdir(parents=True)
        path.write_text('private-canary')
        self.assertIn(str(path.relative_to(self.root)), dirty_paths(self.root))
        _publish_state(self.root, 'w', self.state)
        self.assertEqual(dirty_paths(self.root), [])
        path.write_text('forged')
        self.assertIn(str(path.relative_to(self.root)), dirty_paths(self.root))
        path.write_text('private-canary')
        self.git('add', '-f', str(path.relative_to(self.root)))
        self.assertIn(str(path.relative_to(self.root)), dirty_paths(self.root))

    def test_public_summary_excludes_raw_command_and_output(self):
        path = self.root / 'work/w/inner-loop/results/T1.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'schema': 'ask-task-result/v2', 'candidate_sha': self.state['coordinator_sha'],
            'notes': 'SECRET-CANARY', 'tdd': {'red': {'command': 'SECRET-CANARY', 'output': 'SECRET-CANARY', 'exit_code': 1, 'continuity_receipt': {'output': 'SECRET-CANARY'}}}}))
        _publish_state(self.root, 'w', self.state)
        generated = records(self.root, 'w', read_checkpoint(self.root, 'w'))
        self.assertNotIn(b'SECRET-CANARY', b''.join(generated.values()))
        self.assertEqual(json.loads(generated['work/w/progress/T1.json'])['submissions'][0]['tdd']['red']['exit_code'], 1)

    def test_rejected_reviews_corrections_and_unattached_red_survive(self):
        evidence = self.state['tasks']['T1']['evidence']
        evidence['review'] = {'verdict': 'REJECTED', 'candidate_sha': self.state['coordinator_sha'], 'reviewer': 'independent'}
        _publish_state(self.root, 'w', self.state)
        evidence['review'] = {'verdict': 'APPROVED', 'candidate_sha': self.state['coordinator_sha'], 'reviewer': 'independent'}
        report = {'run_id': 'historical', 'task_id': 'T2', 'candidate_sha': self.state['coordinator_sha'],
                  'cases': [{'test_id': 't', 'case_id': 'c', 'outcome': 'failed', 'failure_kind': 'behavior_assertion'}]}
        from inner_loop.evidence import canonical_digest
        run = self.root / 'work/w/traceability/runs/historical/results.json'
        run.parent.mkdir(parents=True)
        run.write_text(json.dumps(report))
        ledger = self.root / 'work/w/traceability/executions.json'
        ledger.write_text(json.dumps([{'run_id': 'historical', 'task_id': 'T2', 'phase': 'red',
            'candidate_sha': self.state['coordinator_sha'], 'digest': canonical_digest(report)}]))
        _publish_state(self.root, 'w', self.state)
        generated = records(self.root, 'w', read_checkpoint(self.root, 'w'))
        self.assertEqual({r['verdict'] for r in json.loads(generated['work/w/progress/T1.json'])['reviews']}, {'APPROVED', 'REJECTED'})
        historical = json.loads(generated['work/w/progress/T2.json'])['runs'][0]
        self.assertEqual(historical['attribution'], 'historical-unattached')
        self.assertEqual(historical['cases'][0]['outcome'], 'failed')

    def test_migration_preserves_bytes_and_history(self):
        path = self.root / 'work/w/inner-loop/results/T1.json'
        path.parent.mkdir(parents=True)
        raw = b'{"schema":"ask-task-result/v2"}\n'
        path.write_bytes(raw)
        name = str(path.relative_to(self.root))
        self.git('add', name)
        self.git('commit', '-qm', 'legacy runtime')
        self.state['coordinator_sha'] = self.git('rev-parse', 'HEAD')
        _publish_state(self.root, 'w', self.state)
        inventory = {'checkpoint_sha': read_checkpoint(self.root, 'w')[0],
                     'paths': {name: hashlib.sha256(raw).hexdigest()}}
        self.assertEqual(migrate_runtime(self.root, 'w', inventory), [name])
        self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(migrate_runtime(self.root, 'w', inventory), [])
        self.assertEqual(self.git('show', 'HEAD:' + name).encode() + b'\n', raw)


if __name__ == '__main__':
    unittest.main()
