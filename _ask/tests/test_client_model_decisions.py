"""Model consent is saved once and reused across stages and projections."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORK_ID = 'decision-test'
DECISION = {
    'runtime': 'codex',
    'submission': 'confirm',
    'implementation_policy': 'latest-accessible',
    'overrides': {'07-review': 'gpt-6-astra'},
}


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ask-model-decisions-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for source, target in (
            (ROOT / '_ask/scripts', self.root / '_ask/scripts'),
            (ROOT / '_ask/bindings', self.root / '_ask/bindings'),
            (ROOT / '_ask/cursor-commands', self.root / '_ask/cursor-commands'),
            (ROOT / '.agents/ask', self.root / '.agents/ask'),
        ):
            shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__'))
        (self.root / f'work/{WORK_ID}').mkdir(parents=True)

    def env(self, **extra):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(('ASK_MODEL_', 'ASK_EFFORT_'))
               and key not in {'ASK_ROOT', 'ASK_WORK_ID', 'ASKIT_TRANSACTION_ACTIVE'}}
        env.update(ASK_ROOT=str(self.root), ASK_WORK_ID=WORK_ID,
                   ASKIT_TRANSACTION_ACTIVE='1')
        env.update(extra)
        return env

    def decision(self, payload=DECISION, *args, **env):
        return subprocess.run(
            [sys.executable, str(self.root / '_ask/scripts/model-decisions.py'), *args,
             '--work-id', WORK_ID],
            cwd=self.root, env=self.env(**env), input=json.dumps(payload),
            text=True, capture_output=True,
        )

    def model_record(self):
        path = self.root / f'work/{WORK_ID}/models.yaml'
        return path, yaml.safe_load(path.read_text(encoding='utf-8'))

    def test_one_grill_decision(self):
        result = self.decision(DECISION, 'submit')
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        _, record = self.model_record()
        plan = record['model_plan']
        self.assertEqual(plan['status'], 'confirmed')
        self.assertEqual(plan['source'], 'grill')
        self.assertEqual(plan['runtime'], 'codex')
        self.assertEqual(plan['implementation_policy'], 'latest-accessible')
        self.assertEqual(plan['selections']['07-review']['model'], 'gpt-6-astra')
        grill = (self.root / '.agents/ask/stages/01-grill.md').read_text(encoding='utf-8')
        self.assertEqual(grill.count('Confirm model plan'), 1)
        self.assertIn('Change selected models', grill)

    def test_reuse_and_resume(self):
        saved = self.decision(DECISION, 'submit')
        self.assertEqual(saved.returncode, 0, saved.stderr or saved.stdout)
        for stage, expected in (
            ('03-spec-challenge', 'gpt-6-astra'),
            ('05-plan', 'gpt-6-luna'),
            ('06-implement', 'gpt-6-luna'),
            ('07-review', 'gpt-6-astra'),
            ('continuation', 'gpt-6.1-sol'),
        ):
            result = self.decision(None, 'resolve', '--stage', stage,
                                   ASK_MODEL_07_REVIEW_CODEX='ambient-review')
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertEqual(result.stdout.strip(), expected, stage)

        challenge = (self.root / '.agents/ask/stages/03-spec-challenge.md').read_text()
        review = (self.root / '.agents/ask/stages/07-review.md').read_text()
        self.assertNotIn('Present its model picker', challenge)
        self.assertNotIn('Present the model picker', review)

    def test_legacy_choices(self):
        models = self.root / f'work/{WORK_ID}/models.yaml'
        legacy = 'runtime: codex\nrisk: HIGH\ncodex:\n  06-implement: legacy-exact-model\n'
        models.write_text(legacy, encoding='utf-8')
        result = self.decision(None, 'resolve', '--stage', '06-implement')
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertEqual(result.stdout.strip(), 'legacy-exact-model')
        self.assertEqual(models.read_text(encoding='utf-8'), legacy)
        self.assertNotIn('model_plan:', models.read_text(encoding='utf-8'))

    def test_portable_projections(self):
        models = self.root / f'work/{WORK_ID}/models.yaml'
        models.write_text(
            'runtime: codex\nrisk: HIGH\nmodel_plan:\n'
            '  status: confirmed\n  source: grill\n'
            '  implementation_policy: latest-accessible\n'
            'codex:\n  07-review: saved-exact-review\n',
            encoding='utf-8',
        )
        generated = subprocess.run(
            [sys.executable, str(self.root / '_ask/scripts/sync-runtime-agents.py')],
            cwd=self.root, env=self.env(ASK_MODEL_07_REVIEW_CODEX='ambient-review'),
            text=True, capture_output=True,
        )
        self.assertEqual(generated.returncode, 0, generated.stderr)
        codex_review = (self.root / '.codex/agents/kit-07-review.toml').read_text()
        self.assertIn('model = "saved-exact-review"', codex_review)
        self.assertNotIn('ambient-review', codex_review)
        for runtime, path in (
            ('cursor', '.cursor/agents/kit-07-review.md'),
            ('claude', '.claude/agents/kit-07-review.md'),
            ('opencode', '.opencode/agents/kit-07-review.md'),
        ):
            self.assertTrue((self.root / path).is_file(), runtime)

        projected = subprocess.run(
            ['bash', str(self.root / '_ask/scripts/sync-cursor-binding.sh')],
            cwd=self.root, env=self.env(ASK_MODEL_07_REVIEW_CODEX='ambient-review'),
            text=True, capture_output=True,
        )
        self.assertEqual(projected.returncode, 0, projected.stderr or projected.stdout)
        for path in (
            '.agents/skills/kit-03-spec-challenge/SKILL.md',
            '.agents/skills/kit-07-review/SKILL.md',
            '.cursor/commands/03-spec-challenge.md',
            '.cursor/commands/07-review.md',
        ):
            text = (self.root / path).read_text(encoding='utf-8')
            self.assertNotIn('Present its model picker', text, path)
            self.assertNotIn('Present the model picker', text, path)

    def test_decision_persistence(self):
        result = self.decision(DECISION, 'submit')
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        path, record = self.model_record()
        plan = record['model_plan']
        self.assertEqual(record['runtime'], 'codex')
        self.assertEqual(plan['runtime'], 'codex')
        self.assertEqual(plan['status'], 'confirmed')
        self.assertEqual(plan['source'], 'grill')
        self.assertEqual(plan['implementation_policy'], 'latest-accessible')
        self.assertEqual(plan['selections']['07-review'], {
            'role': 'review', 'model': 'gpt-6-astra', 'source': 'exact-override',
        })
        self.assertEqual(record['codex'], {'07-review': 'gpt-6-astra'})
        self.assertNotIn('05-plan', record['codex'])
        self.assertNotIn('06-implement', record['codex'])

        runtime = self.root / '.agents/ask/bindings/runtimes/codex.yaml'
        config = yaml.safe_load(runtime.read_text(encoding='utf-8'))
        config['roles']['typing'] = 'new-typing-default'
        runtime.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        resolved = self.decision(None, 'resolve', '--stage', '06-implement')
        self.assertEqual(resolved.returncode, 0, resolved.stderr or resolved.stdout)
        self.assertEqual(resolved.stdout.strip(), 'new-typing-default')
        self.assertTrue(path.is_file())


if __name__ == '__main__':
    unittest.main()
