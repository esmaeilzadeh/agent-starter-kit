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
        result = self.decision(DECISION, 'save')
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        _, record = self.model_record()
        plan = record['model_plan']
        self.assertEqual(plan['status'], 'confirmed')
        self.assertEqual(plan['source'], 'grill')
        self.assertEqual(plan['runtime'], 'codex')
        self.assertEqual(plan['implementation_policy'], 'latest-accessible')
        self.assertEqual(plan['selections']['07-review']['model'], 'gpt-6-astra')
        shown = self.decision(None, 'show')
        self.assertEqual(shown.returncode, 0, shown.stderr or shown.stdout)
        self.assertEqual(json.loads(shown.stdout)['selections']['07-review']['model'],
                         'gpt-6-astra')
        other_runtime = self.decision(None, 'show', '--runtime', 'cursor')
        self.assertEqual(other_runtime.returncode, 0,
                         other_runtime.stderr or other_runtime.stdout)
        other_plan = json.loads(other_runtime.stdout)
        self.assertFalse(other_plan['confirmed'])
        self.assertFalse(other_plan['policy_confirmed'])

        risk_id = 'decision-risk-test'
        risk_dir = self.root / 'work' / risk_id
        risk_dir.mkdir()
        (risk_dir / 'models.yaml').write_text('risk: HIGH\n', encoding='utf-8')
        low_risk = {
            'runtime': 'codex', 'risk': 'LOW', 'submission': 'confirm',
            'implementation_policy': 'latest-accessible', 'overrides': {},
        }
        saved_low = subprocess.run(
            [sys.executable, str(self.root / '_ask/scripts/model-decisions.py'),
             'save', '--work-id', risk_id], cwd=self.root, env=self.env(),
            input=json.dumps(low_risk), text=True, capture_output=True,
        )
        self.assertEqual(saved_low.returncode, 0, saved_low.stderr or saved_low.stdout)
        low_plan = yaml.safe_load((risk_dir / 'models.yaml').read_text())['model_plan']
        self.assertEqual(low_plan['risk'], 'LOW')
        self.assertEqual(low_plan['selections']['07-review']['model'], 'gpt-6-luna')

        grill = (self.root / '.agents/ask/stages/01-grill.md').read_text(encoding='utf-8')
        self.assertEqual(grill.count('Confirm model plan'), 1)
        self.assertIn('Change selected models', grill)

    def test_reuse_and_resume(self):
        saved = self.decision(DECISION, 'save')
        self.assertEqual(saved.returncode, 0, saved.stderr or saved.stdout)
        for stage, expected in (
            ('03-spec-challenge', 'gpt-6-astra'),
            ('05-plan', 'gpt-6.1-sol'),
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
        shown = self.decision(None, 'show')
        self.assertEqual(shown.returncode, 0, shown.stderr or shown.stdout)
        shown_plan = json.loads(shown.stdout)
        self.assertFalse(shown_plan['confirmed'])
        self.assertFalse(shown_plan['policy_confirmed'])
        self.assertEqual(shown_plan['implementation_policy'], 'legacy-configured')

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
        result = self.decision(DECISION, 'save')
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
        config = runtime.read_text(encoding='utf-8')
        self.assertIn('  typing: gpt-6-luna\n', config)
        runtime.write_text(config.replace('  typing: gpt-6-luna\n',
                                          '  typing: new-typing-default\n', 1),
                           encoding='utf-8')
        resolved = self.decision(None, 'resolve', '--stage', '06-implement')
        self.assertEqual(resolved.returncode, 0, resolved.stderr or resolved.stdout)
        self.assertEqual(resolved.stdout.strip(), 'new-typing-default')
        self.assertTrue(path.is_file())

        scalar_id = 'decision-scalar-test'
        (self.root / 'work' / scalar_id).mkdir()
        scalar_decision = dict(DECISION, overrides={'07-review': '1e3',
                                                     '06-implement': '0xabc'})
        saved_scalars = subprocess.run(
            [sys.executable, str(self.root / '_ask/scripts/model-decisions.py'),
             'save', '--work-id', scalar_id], cwd=self.root, env=self.env(),
            input=json.dumps(scalar_decision), text=True, capture_output=True,
        )
        self.assertEqual(saved_scalars.returncode, 0,
                         saved_scalars.stderr or saved_scalars.stdout)
        for stage, expected in (('07-review', '1e3'), ('06-implement', '0xabc')):
            restored = subprocess.run(
                [sys.executable, str(self.root / '_ask/scripts/model-decisions.py'),
                 'resolve', '--work-id', scalar_id, '--stage', stage],
                cwd=self.root, env=self.env(), text=True, capture_output=True,
            )
            self.assertEqual(restored.returncode, 0, restored.stderr or restored.stdout)
            self.assertEqual(restored.stdout.strip(), expected)

        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'models.yaml').write_text('keep: true\n', encoding='utf-8')
        (self.root / 'work/escape-work').symlink_to(outside, target_is_directory=True)
        (self.root / 'work/escape-file').mkdir()
        (self.root / 'work/escape-file/models.yaml').symlink_to(outside / 'models.yaml')
        for work_id in ('escape-work', 'escape-file'):
            rejected = subprocess.run(
                [sys.executable, str(self.root / '_ask/scripts/model-decisions.py'),
                 'save', '--work-id', work_id], cwd=self.root, env=self.env(),
                input=json.dumps(DECISION), text=True, capture_output=True,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual((outside / 'models.yaml').read_text(encoding='utf-8'), 'keep: true\n')


class ConfidenceDecisions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location('decision_ladder_tests', ROOT / '_ask/scripts/model-decisions.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ask-confidence-ladder-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / '.agents/ask', self.root / '.agents/ask')
        (self.root / '_ask/bindings').mkdir(parents=True)
        shutil.copy2(ROOT / '_ask/bindings/models.yaml', self.root / '_ask/bindings/models.yaml')
        (self.root / 'work/w').mkdir(parents=True)
        self.module.ROOT = self.root

    def request(self, **values):
        return {'decision_id': 'repair-cas', 'evidence_digest': 'a' * 64,
                'session_id': 'current-session', 'runtime': 'codex',
                'authority_kind': 'within-scope', 'confidence': 90,
                'decision': 'Choose the scoped CAS correction', 'scope': 'approved repair',
                'uncertainty': 'Verify transaction race reasoning',
                'evidence': [{'path': 'checkpoint.py', 'assessment': 'Exact CAS reproduction'}],
                'capability_evidence': {'session_id': 'current-session', 'runtime': 'codex',
                    'source': 'native-tool-metadata', 'authenticated': True, 'access_verified': True,
                    'models': [{'model': 'gpt-6.1-sol', 'efforts': ['high']},
                               {'model': 'gpt-6-astra', 'efforts': ['medium', 'high']}]}, **values}

    def assessment(self, request, model='gpt-6.1-sol', effort='high', confidence=85, **values):
        return {**{k: request[k] for k in ('decision_id', 'evidence_digest', 'session_id')},
                'requested_model': model, 'requested_effort': effort,
                'actual_model': model, 'actual_effort': effort, 'identity_verified': True,
                'status': 'assessed', 'assessment': 'Concrete scoped reasoning', 'confidence': confidence, **values}

    def test_strict_threshold_and_malformed_confidence(self):
        self.assertEqual(self.module.decide('w', self.request(confidence=90))['action'], 'consult')
        self.assertEqual(self.module.decide('w', self.request(confidence=90.1))['action'], 'continue')
        for value in (True, '91', None, -1, 101, float('nan'), float('inf')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.module.decide('w', self.request(confidence=value))

    def test_rungs_reuse_and_material_evidence_binding(self):
        request = self.request()
        decision = self.module.decide('w', request)
        self.assertEqual((decision['model'], decision['effort']), ('gpt-6.1-sol', 'high'))
        request['assessments'] = [self.assessment(request)]
        decision = self.module.decide('w', request)
        self.assertEqual((decision['model'], decision['effort']), ('gpt-6-astra', 'medium'))
        request['assessments'].append(self.assessment(request, 'gpt-6-astra', 'medium'))
        self.assertEqual(self.module.decide('w', request)['effort'], 'high')
        request['assessments'].append(self.assessment(request, 'gpt-6-astra', 'high', 96))
        self.assertEqual(self.module.decide('w', request)['action'], 'continue')
        request['evidence_digest'] = 'b' * 64
        self.assertEqual(self.module.decide('w', request)['model'], 'gpt-6.1-sol')
        request['session_id'] = 'another-session'
        self.assertEqual(self.module.decide('w', request)['action'], 'ask-human')

    def test_confidence_ladder_comes_from_runtime_and_user_overrides(self):
        request = self.request()
        self.assertEqual(self.module.decide('w', request)['model'], 'gpt-6.1-sol')

        project_models = self.root / '.agents/ask.local/bindings/models.yaml'
        project_models.parent.mkdir(parents=True)
        project_models.write_text(
            'confidence_escalation:\n  codex:\n    - gpt-6-astra@high\n',
            encoding='utf-8',
        )
        request['capability_evidence']['models'] = [
            {'model': 'gpt-6-astra', 'efforts': ['high']},
        ]
        self.assertEqual(self.module.decide('w', request)['model'], 'gpt-6-astra')

        work_models = self.root / 'work/w/models.yaml'
        work_models.parent.mkdir(exist_ok=True)
        work_models.write_text(
            'confidence_escalation:\n  codex:\n    - gpt-6.1-sol@medium\n',
            encoding='utf-8',
        )
        request['capability_evidence']['models'] = [
            {'model': 'gpt-6.1-sol', 'efforts': ['medium']},
        ]
        self.assertEqual(self.module.decide('w', request)['model'], 'gpt-6.1-sol')
        self.assertEqual(self.module.decide('w', request)['effort'], 'medium')
        work_models.write_text('confidence_escalation: codex\n', encoding='utf-8')
        self.assertEqual(self.module.decide('w', request)['action'], 'ask-human')

    def test_confidence_ladder_is_runtime_specific(self):
        request = self.request(runtime='claude')
        request['capability_evidence'] = {
            'session_id': 'current-session', 'runtime': 'claude',
            'source': 'native-tool-metadata', 'authenticated': True,
            'access_verified': True,
            'models': [{'model': 'claude-opus-5-5', 'efforts': []}],
        }
        decision = self.module.decide('w', request)
        self.assertEqual((decision['model'], decision['effort']), ('claude-opus-5-5', None))

    def test_unavailable_effort_catalog_and_human_authority(self):
        request = self.request()
        request['capability_evidence']['models'][0]['efforts'] = ['medium']
        self.assertEqual(self.module.decide('w', request)['model'], 'gpt-6-astra')
        self.assertEqual(self.module.decide('w', self.request(capability_evidence={}))['action'], 'ask-human')
        self.assertEqual(self.module.decide('w', self.request(allowed_models=[]))['action'], 'ask-human')
        for authority in ('scope-change', 'human-preference', 'unsafe-irreversible', None):
            self.assertEqual(self.module.decide('w', self.request(authority_kind=authority, confidence=99))['action'], 'ask-human')
        self.assertEqual(self.module.decide('w', self.request(runtime='unknown'))['action'], 'ask-human')
        self.assertEqual(self.module.decide('w', self.request(runtime='cursor'))['action'], 'ask-human')

    def test_consult_adapter_identity_failure_and_exhaustion(self):
        from unittest.mock import patch
        request = self.request()
        with patch.object(self.module, 'runtime_request', side_effect=ValueError('timeout')):
            result = self.module.consult('w', request)
        self.assertEqual(result['assessment']['status'], 'unavailable')
        self.assertEqual(result['next']['model'], 'gpt-6-astra')
        request['assessments'] = [result['assessment']]
        response = self.assessment(request, 'wrong-model', 'medium')
        with patch.object(self.module, 'runtime_request', return_value=response):
            result = self.module.consult('w', request)
        self.assertEqual(result['assessment']['status'], 'unavailable')
        self.assertEqual(result['next']['effort'], 'high')
        request['assessments'].append(result['assessment'])
        response = self.assessment(request, 'gpt-6-astra', 'high', confidence=89)
        with patch.object(self.module, 'runtime_request', return_value=response) as adapter:
            result = self.module.consult('w', request)
        self.assertEqual(adapter.call_args.args, ('codex', 'consult'))
        self.assertEqual(adapter.call_args.kwargs['effort'], 'high')
        self.assertEqual(adapter.call_args.kwargs['decision'], request['decision'])
        self.assertEqual(adapter.call_args.kwargs['evidence'], request['evidence'])
        self.assertEqual(result['next']['action'], 'ask-human')
        response['confidence'] = 95
        with patch.object(self.module, 'runtime_request', return_value=response):
            self.assertEqual(self.module.consult('w', request)['next']['action'], 'continue')

    def test_forged_identity_is_not_an_assessment(self):
        request = self.request()
        request['assessments'] = [self.assessment(request, identity_verified=False)]
        with self.assertRaises(ValueError):
            self.module.decide('w', request)

    def test_public_decision_cli(self):
        proc = subprocess.run([sys.executable, str(ROOT / '_ask/scripts/model-decisions.py'),
                               'decide', '--work-id', 'w'], input=json.dumps(self.request()),
                              text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['request']['effort'], 'high')

    def test_every_canonical_stage_uses_central_policy(self):
        for stage in (ROOT / '.agents/ask/stages').glob('[0-9][0-9]-*.md'):
            self.assertIn('_ask/policies/workflow.md#model-confidence-escalation', stage.read_text())
        self.assertIn('_ask/policies/workflow.md#model-confidence-escalation',
                      (ROOT / '.agents/ask/task-loop.md').read_text())


if __name__ == '__main__':
    unittest.main()
