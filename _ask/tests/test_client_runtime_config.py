"""Runtime model generation must preserve scalar identity and publish atomically."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import tomli
import yaml

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ('.cursor', '.agents/skills', '.codex/agents', '.claude/agents', '.opencode/agents')


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ask-runtime-config-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for source, target in (
            (ROOT / '.agents/ask', self.root / '.agents/ask'),
            (ROOT / '_ask/scripts', self.root / '_ask/scripts'),
            (ROOT / '_ask/agents', self.root / '_ask/agents'),
            (ROOT / '_ask/cursor-commands', self.root / '_ask/cursor-commands'),
        ):
            shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(ROOT / 'ask', self.root / 'ask')
        shutil.copy2(ROOT / '.gitignore', self.root / '.gitignore')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Runtime Test')
        self.git('config', 'user.email', 'runtime@example.invalid')
        self.git('add', '.')
        self.git('commit', '-qm', 'runtime fixture')
        (self.root / 'work/example').mkdir(parents=True)
        result = self.run_sync()
        if result.returncode:
            self.fail('initial runtime generation failed: ' + result.stdout + result.stderr)

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True,
                              text=True, capture_output=True).stdout.strip()

    def environment(self, **extra):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(('ASK_', 'VERIFY_'))}
        env.update(PATH=os.environ.get('PATH', '/usr/bin:/bin'), ASK_WORK_ID='example')
        env.update(extra)
        return env

    def run_generator(self, **extra):
        return subprocess.run(['python3', '_ask/scripts/sync-runtime-agents.py'],
                              cwd=self.root, env=self.environment(**extra),
                              text=True, capture_output=True)

    def run_sync(self, **extra):
        return subprocess.run(['./ask', 'sync'], cwd=self.root,
                              env=self.environment(**extra), text=True, capture_output=True)

    def snapshot(self):
        return {path.relative_to(self.root): path.read_bytes()
                for pattern in OUTPUTS for path in (self.root / pattern).rglob('*')
                if path.is_file()}

    def model(self, path):
        text = path.read_text(encoding='utf-8')
        if path.suffix == '.toml':
            return tomli.loads(text)
        frontmatter = text.split('---', 2)[1]
        return yaml.safe_load(frontmatter)

    def test_scalar_roundtrip(self):
        value = 'custom "quoted" \\ path: mapping-like {{stage}}'
        result = self.run_generator(ASK_MODEL_06_IMPLEMENT=value)
        self.assertEqual(result.returncode, 0, result.stderr)
        generated = [
            self.root / '.cursor/agents/kit-06-implement.md',
            self.root / '.claude/agents/kit-06-implement.md',
            self.root / '.opencode/agents/kit-06-implement.md',
            self.root / '.codex/agents/kit-06-implement.toml',
        ]
        for path in generated:
            try:
                actual = self.model(path)['model']
            except Exception as exc:
                self.fail(f'{path} does not parse as one model scalar: {exc}')
            self.assertEqual(actual, value, str(path))

        before = self.snapshot()
        for invalid in ('', 'first line\nsecond line', 'bad\x01value'):
            with self.subTest(invalid=repr(invalid)):
                rejected = self.run_generator(ASK_MODEL_06_IMPLEMENT=invalid)
                self.assertNotEqual(rejected.returncode, 0, repr(invalid))
                self.assertEqual(self.snapshot(), before)
        (self.root / 'work/example/models.yaml').write_text(
            'codex:\n  06-implement: true\n', encoding='utf-8')
        rejected = self.run_generator()
        self.assertNotEqual(rejected.returncode, 0, rejected.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_sync_atomic_invalid(self):
        before = self.snapshot()
        result = self.run_sync(ASK_MODEL_10_ACCEPT_CODEX='safe\ninjected = true')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_sync_valid_formats(self):
        work_value = 'work "quoted" \\ path: scalar'
        project_value = 'project "quoted" \\ path: scalar'
        env_value = 'environment "quoted" \\ path: scalar'
        (self.root / 'work/example/models.yaml').write_text(
            'cursor:\n  06-implement: ' + work_value + '\n', encoding='utf-8')
        overlay = self.root / '.agents/ask.local/bindings/models.yaml'
        overlay.parent.mkdir(parents=True, exist_ok=True)
        overlay.write_text('claude:\n  06-implement: ' + project_value + '\n', encoding='utf-8')
        result = self.run_sync(ASK_MODEL_06_IMPLEMENT_CODEX=env_value)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected = {
            '.cursor/agents/kit-06-implement.md': work_value,
            '.claude/agents/kit-06-implement.md': project_value,
            '.codex/agents/kit-06-implement.toml': env_value,
        }
        for rel, value in expected.items():
            path = self.root / rel
            try:
                doc = self.model(path)
            except Exception as exc:
                self.fail(f'{path} does not parse: {exc}')
            self.assertEqual(doc['model'], value, rel)
        cursor_review = self.model(self.root / '.cursor/agents/kit-07-review.md')
        claude_review = self.model(self.root / '.claude/agents/kit-07-review.md')
        opencode_review = self.model(self.root / '.opencode/agents/kit-07-review.md')
        codex_review = self.model(self.root / '.codex/agents/kit-07-review.toml')
        self.assertIs(cursor_review['readonly'], True)
        self.assertIs(claude_review['readonly'], True)
        self.assertEqual(opencode_review['permission']['edit'], 'deny')
        self.assertIn('developer_instructions', codex_review)


if __name__ == '__main__':
    unittest.main()
