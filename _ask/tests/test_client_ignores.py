"""Generated client ignore rules preserve portable project state."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '_ask/scripts'))
from client_ignores import update


class ClientIgnoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.target)], check=True)

    def assert_ignored(self, path, expected):
        result = subprocess.run(
            ['git', 'check-ignore', '--no-index', '-q', path], cwd=self.target,
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0 if expected else 1, path + result.stderr)

    def test_generated_rules_keep_state_and_custom_files_trackable(self):
        ignore = self.target / '.gitignore'
        ignore.write_bytes((ROOT / '.gitignore').read_bytes())
        update(self.target, ROOT)
        for path in (
            'work/demo/plan.md', 'work/demo/progress/task.json',
            'work/demo/inner-loop/state.json', 'work/demo/inner-loop/results/task.json',
            'work/demo/inner-loop/evidence/verify-task/integration.json',
            'work/demo/traceability/executions.json', 'work/demo/traceability/completion.json',
            'work/demo/traceability/static-check.json', 'work/demo/traceability/model-state/state.json',
            'work/demo/traceability/runs/run/results.json',
            '.ask/tracker-context.md', '.agents/skills/client-custom/SKILL.md',
            '.codex/hooks.json', '.agents/ask.local/bindings/models.yaml', '.agents/verification.yaml',
        ):
            self.assert_ignored(path, False)
        for path in (
            'ask', '_ask/scripts/main.py', '.agents/ask/session.md',
            '.agents/skills/kit-00-explore/SKILL.md', '.ask.env',
            'work/demo/inner-loop/state.lock', 'work/demo/traceability/runs/run/stdout.log',
            'work/demo/traceability/runs/run/raw.json',
        ):
            self.assert_ignored(path, True)

    def test_old_managed_block_is_migrated_and_consumer_rules_preserved(self):
        ignore = self.target / '.gitignore'
        ignore.write_text(
            'consumer-cache/\n'
            'work/*/inner-loop/state.json\n'
            '# BEGIN AskIt local installation\n'
            '/ask\n/.agents/skills/\n/.codex/hooks.json\n/.ask/tracker-context.md\n'
            '# END AskIt local installation\n'
        )
        update(self.target, ROOT)
        first = ignore.read_bytes()
        update(self.target, ROOT)
        self.assertEqual(ignore.read_bytes(), first)
        self.assert_ignored('consumer-cache/item', True)
        for path in ('.ask/tracker-context.md', '.codex/hooks.json',
                     '.agents/skills/custom/SKILL.md', 'work/demo/inner-loop/state.json',
                     'work/demo/traceability/runs/run/results.json'):
            self.assert_ignored(path, False)
        for path in ('work/demo/inner-loop/worker.log',
                     'work/demo/traceability/runs/run/stdout.log',
                     'work/demo/traceability/runs/run/raw.json',
                     'work/demo/traceability/static-runs/run/raw.json',
                     'work/demo/traceability/executions.lock',
                     'work/demo/inner-loop/state.lock', '.ask.env'):
            self.assert_ignored(path, True)

    def test_hooks_are_trackable_when_stock_or_custom(self):
        source = self.target / 'stock'
        for base in (source, self.target):
            (base / '.codex').mkdir(parents=True)
            (base / '.codex/hooks.json').write_text('{"hooks": {}}\n')
        update(self.target, source)
        self.assert_ignored('.codex/hooks.json', False)
        (self.target / '.codex/hooks.json').write_text('{"hooks": {}, "custom": true}\n')
        update(self.target, source)
        self.assert_ignored('.codex/hooks.json', False)

    def test_prepared_skills_and_lock_do_not_dirty_client(self):
        update(self.target, ROOT)
        subprocess.run(['git', 'add', '.gitignore'], cwd=self.target, check=True)
        skill = self.target / '.agents/skills/research/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('Prepared skill\n')
        (self.target / 'skills-lock.json').write_text('{}\n')
        status = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'],
                                         cwd=self.target, text=True)
        self.assertEqual(status, '', 'prepared runtime output must stay local')
        self.assert_ignored('.cursor/skills/research/SKILL.md', True)
        self.assert_ignored('.agents/skills/client-custom/SKILL.md', False)
        before = (self.target / '.gitignore').read_bytes()
        update(self.target, ROOT)
        self.assertEqual((self.target / '.gitignore').read_bytes(), before)

    def test_ignore_update_preserves_unprepared_client_manifest(self):
        from distribution import DistributionError, prepare

        manifest = self.target / '.agents/ask.local/skills/manifest.yaml'
        manifest.parent.mkdir(parents=True)
        manifest.write_text('client manifest\n')
        update(self.target, ROOT)
        self.assertEqual(manifest.read_text(), 'client manifest\n')
        with self.assertRaisesRegex(DistributionError, 'unsupported manifest syntax'):
            prepare(self.target, manifest, ROOT / '_ask/skills/dependency-pins.json')


if __name__ == '__main__':
    unittest.main()
