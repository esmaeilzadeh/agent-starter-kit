"""Runtime model selection and implementation handoff at public CLI seams."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client_security_fixtures import ClientFixture, ROOT
from traceability_support import seed as seed_traceability, accept as accept_traceability


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.fx = ClientFixture()
        self.addCleanup(self.fx.close)
        self.root = self.fx.root / 'repo'
        clone = self.fx.run(['git', 'clone', '-q', '--shared', str(ROOT), str(self.root)])
        self.assertEqual(clone.returncode, 0, clone.stderr)
        self.fx.run(['git', '-C', str(self.root), 'checkout', '-qb', 'agent/orchestrator-test'])
        self.work_id = 'orchestrator-test'
        self.work = self.root / 'work' / self.work_id
        self.work.mkdir(parents=True)
        self.env = self.fx.env.copy()
        self.env['ASK_WORK_ID'] = self.work_id
        self.log = self.fx.root / 'runtime-events.jsonl'
        self.adapter = self.fx.root / 'runtime-adapter.py'
        self.config = self.fx.root / 'runtime-config.json'
        self.write_adapter({})

    def write_adapter(self, config):
        self.config.write_text(json.dumps(config), encoding='utf-8')
        self.log.unlink(missing_ok=True)
        self.adapter.write_text(
            '#!/usr/bin/env python3\n'
            'import json, os, sys\n'
            'request = json.load(sys.stdin)\n'
            'path = os.environ["ASK_MODEL_RUNTIME_CONFIG"]\n'
            'config = json.load(open(path, encoding="utf-8"))\n'
            'with open(os.environ["ASK_MODEL_RUNTIME_LOG"], "a", encoding="utf-8") as log:\n'
            '    log.write(json.dumps(request) + "\\n")\n'
            'action = request["action"]\n'
            'if action == "catalog": response = config.get("catalog", {})\n'
            'elif action == "identity":\n'
            '    response = dict(config.get("identity", {}))\n'
            '    if "switch_supported" in config: response["switch_supported"] = config["switch_supported"]\n'
            'elif action == "switch":\n'
            '    if config.get("switch_supported") and not config.get("switch_failure"):\n'
            '        config["identity"] = {"model": config.get("switch_result", request.get("model"))}\n'
            '        json.dump(config, open(path, "w", encoding="utf-8"))\n'
            '        response = {"supported": True}\n'
            '    else: response = {"supported": config.get("switch_supported", False)}\n'
            'else: response = {}\n'
            'print(json.dumps(response))\n',
            encoding='utf-8',
        )
        self.adapter.chmod(0o755)
        self.env['ASK_MODEL_RUNTIME_ADAPTER'] = str(self.adapter)
        self.env['ASK_MODEL_RUNTIME_CONFIG'] = str(self.config)
        self.env['ASK_MODEL_RUNTIME_LOG'] = str(self.log)

    def run_ask(self, *args, input=None):
        return self.fx.run([str(self.root / 'ask'), *args], cwd=self.root,
                           env=self.env, input=input)

    def events(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def save_plan(self, *, policy='latest-accessible', overrides=None, risk=None,
                  runtime='codex', submission='confirm'):
        decision = {
            'runtime': runtime, 'submission': submission,
            'implementation_policy': policy, 'overrides': overrides or {},
        }
        if risk is not None:
            decision['risk'] = risk
        return self.fx.run(
            ['python3', str(self.root / '_ask/scripts/model-decisions.py'),
             'save', '--work-id', self.work_id],
            cwd=self.root, env=self.env, input=json.dumps(decision),
        )

    def plan_record(self):
        return json.loads(self.run_ask('model', 'decision', 'show',
                                       '--work-id', self.work_id).stdout)

    def test_accessible_implementor(self):
        failures = []
        local_models = self.root / '.agents/ask.local/bindings/models.yaml'
        local_models.parent.mkdir(parents=True, exist_ok=True)
        local_models.write_text('risk: HIGH\n', encoding='utf-8')
        saved = self.save_plan()
        if saved.returncode:
            failures.append('confirmed model plan was not saved: ' + saved.stderr)
        else:
            record = json.loads(saved.stdout)
            if record.get('risk') != 'HIGH' or record['selections']['07-review']['model'] != 'gpt-6-astra':
                failures.append('saved table did not preserve the project HIGH-risk defaults')

        self.save_plan(policy='exact', overrides={'07-review': 'gpt-6-luna'},
                       submission='change')
        confirmed = self.save_plan(policy='exact', overrides={}, submission='confirm')
        shown = self.run_ask('model', 'decision', 'show', '--work-id', self.work_id)
        if (confirmed.returncode or json.loads(shown.stdout)['selections']['07-review']['model']
                != 'gpt-6-luna'):
            failures.append('confirmation discarded a saved exact stage override')
        self.save_plan(policy='latest-accessible', overrides={}, submission='change')

        self.write_adapter({
            'catalog': {
                'authenticated': True,
                'access_verified': True,
                'family': 'gpt',
                'models': ['gpt-6.9-luna', 'gpt-6.10-luna',
                           'gpt-6.12-sol', 'gpt-6.13-astra'],
                'order': ['gpt-6.9-luna', 'gpt-6.10-luna',
                          'gpt-6.12-sol', 'gpt-6.13-astra'],
            },
            'identity': {'model': 'gpt-6.1-sol'},
            'switch_supported': False,
        })
        selected = self.run_ask('model', 'decision', 'resolve-implementor',
                                '--work-id', self.work_id)
        if selected.returncode or selected.stdout.strip() != 'gpt-6.10-luna':
            failures.append('latest accessible model ignored runtime ordering: '
                            + (selected.stderr or selected.stdout))

        exact = self.save_plan(submission='change', overrides={'06-implement': 'gpt-6.9-luna'})
        selected_exact = self.run_ask('model', 'decision', 'resolve-implementor',
                                      '--work-id', self.work_id)
        if exact.returncode or selected_exact.returncode or selected_exact.stdout.strip() != 'gpt-6.9-luna':
            failures.append('explicit implementor override did not win: '
                            + (selected_exact.stderr or selected_exact.stdout))

        self.save_plan(submission='change')
        self.write_adapter({
            'catalog': {'authenticated': True, 'family': 'gpt',
                        'access_verified': True,
                        'models': ['gpt-6.9-luna', 'gpt-6.10-luna']},
            'identity': {'model': 'gpt-6.1-sol'},
        })
        unknown_order = self.run_ask('model', 'decision', 'resolve-implementor',
                                     '--work-id', self.work_id)
        if unknown_order.returncode == 0 or not any(
                word in (unknown_order.stderr + unknown_order.stdout).lower()
                for word in ('order', 'ordering', 'evidence')):
            failures.append('unknown version ordering guessed a model')

        self.save_plan(submission='change')
        self.write_adapter({
            'catalog': {'authenticated': True, 'family': 'gpt',
                        'models': ['gpt-6-luna'],
                        'order': ['gpt-6-luna']},
            'identity': {'model': 'gpt-6.1-sol'},
        })
        unknown_access = self.run_ask('model', 'decision', 'resolve-implementor',
                                      '--work-id', self.work_id)
        if unknown_access.returncode == 0 or not any(
                word in (unknown_access.stderr + unknown_access.stdout).lower()
                for word in ('access', 'evidence', 'verified')):
            failures.append('catalog listing without current access evidence selected a model')
        self.assertFalse(failures, '\n'.join(failures))

    def test_automatic_switch_verified(self):
        failures = []
        saved = self.save_plan(policy='exact', overrides={'06-implement': 'gpt-6-luna'},
                               submission='change')
        if saved.returncode:
            failures.append('exact model decision could not be saved')
        self.write_adapter({'identity': {'model': 'gpt-6-luna'}, 'switch_supported': True})
        matching = self.run_ask('orchestrator-handoff', 'preflight', '--work-id', self.work_id)
        if matching.returncode or 'ready' not in (matching.stdout + matching.stderr).lower():
            failures.append('matching orchestrator prompted or failed preflight')
        if any(event.get('action') == 'switch' for event in self.events()):
            failures.append('matching orchestrator was switched unnecessarily')

        self.write_adapter({'identity': {'model': 'gpt-6.1-sol'}, 'switch_supported': True,
                            'switch_result': 'gpt-6-luna'})
        switched_ok = self.run_ask('orchestrator-handoff', 'preflight', '--work-id', self.work_id)
        successful_actions = [event.get('action') for event in self.events()]
        if switched_ok.returncode or 'ready' not in switched_ok.stdout.lower() or 'switch' not in successful_actions or successful_actions.count('identity') < 2:
            failures.append('supported switch was not verified by a fresh matching identity')

        self.write_adapter({'identity': {'model': 'gpt-6.1-sol'}, 'switch_supported': True,
                            'switch_result': 'gpt-6-astra'})
        switched = self.run_ask('orchestrator-handoff', 'preflight', '--work-id', self.work_id)
        actions = [event.get('action') for event in self.events()]
        if switched.returncode == 0 or 'identity' not in actions or 'switch' not in actions:
            failures.append('mismatched post-switch identity was not blocked and re-observed')
        if any(event.get('action') == 'spawn' for event in self.events()):
            failures.append('child spawn was treated as a parent identity switch')

        self.write_adapter({'identity': {}, 'switch_supported': False})
        self.seed_writer_workstream()
        saved = self.save_plan(policy='exact', overrides={'06-implement': 'gpt-6-luna'},
                               submission='change')
        self.assertEqual(saved.returncode, 0, saved.stderr or saved.stdout)
        self.fx.run(['git', '-C', str(self.root), 'add',
                     'work/' + self.work_id + '/models.yaml'])
        self.fx.run(['git', '-C', str(self.root), 'commit', '-qm', 'save confirmed model plan'])
        initialized = self.run_ask('inner-loop', 'cas-init', self.work_id)
        self.assertEqual(initialized.returncode, 0, initialized.stderr or initialized.stdout)
        admitted = self.run_ask('inner-loop', 'spawn-writer', self.work_id, 'task')
        state = json.loads((self.work / 'inner-loop/state.json').read_text(encoding='utf-8'))
        if (admitted.returncode == 0 or state['tasks']['task']['status'] != 'pending'
                or 'gpt-6-luna' not in (admitted.stdout + admitted.stderr)):
            failures.append('public spawn-writer bypassed the confirmed parent handoff gate')
        self.assertFalse(failures, '\n'.join(failures))

    def seed_writer_workstream(self):
        inner = self.work / 'inner-loop'
        inner.mkdir(exist_ok=True)
        (inner / 'tasks.yaml').write_text(
            'schema: ask-inner-loop-tasks/v1\nwork_id: ' + self.work_id +
            '\ntasks:\n  - id: task\n    depends_on: []\n    owned_paths: [src/**]\n',
            encoding='utf-8')
        (self.root / '.agents/verification.yaml').write_text(
            'schema: ask-checkplan/v1\nno_production_datastore: true\n', encoding='utf-8')
        seed_traceability(self.root, self.work_id)
        prepared = self.fx.run(['git', '-C', str(self.root), 'add', '.agents/verification.yaml',
                                'work/' + self.work_id, 'specs/current/' + self.work_id + '.json',
                                'specs/current/' + self.work_id + '.md'])
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        committed = self.fx.run(['git', '-C', str(self.root), 'commit', '-qm',
                                 'seed writer admission fixture'])
        self.assertEqual(committed.returncode, 0, committed.stderr)
        accept_traceability(self.root, self.work_id)

    def test_manual_switch_resume(self):
        failures = []
        saved = self.save_plan(policy='exact', overrides={'06-implement': 'gpt-6-luna'})
        if saved.returncode:
            failures.append('exact model decision could not be saved')
        self.write_adapter({'identity': {}, 'switch_supported': False})
        first = self.run_ask('orchestrator-handoff', 'preflight', '--work-id', self.work_id)
        request = first.stdout + first.stderr
        if first.returncode == 0 or 'gpt-6-luna' not in request or 'Codex' not in request:
            failures.append('unsupported switch did not stop with one named Codex request')
        self.assertEqual(request.count('gpt-6-luna'), 1,
                         'manual handoff repeated or omitted the model request')

        observed = self.run_ask('orchestrator-handoff', 'resume', '--work-id', self.work_id,
                                '--observed-model', 'gpt-6-luna',
                                '--provenance', 'observed in active Codex model picker')
        if observed.returncode:
            failures.append('verified manual observation was not recorded: '
                            + (observed.stderr or observed.stdout))
        resumed = self.run_ask('orchestrator-handoff', 'preflight', '--work-id', self.work_id)
        if resumed.returncode or 'ready' not in (resumed.stdout + resumed.stderr).lower():
            failures.append('recorded matching observation did not resume implementation')

        self.write_adapter({'identity': {}, 'switch_supported': False})
        failed = self.run_ask('orchestrator-handoff', 'resume', '--work-id', self.work_id,
                              '--observed-model', 'gpt-6-astra',
                              '--provenance', 'unverified claim')
        if failed.returncode == 0:
            failures.append('mismatched manual observation was accepted')

        switched_runtime = self.save_plan(runtime='cursor', policy='exact',
                                          overrides={'06-implement': 'gpt-6-luna'},
                                          submission='change')
        self.write_adapter({'identity': {}, 'switch_supported': False})
        stale = self.run_ask('orchestrator-handoff', 'preflight', '--work-id', self.work_id)
        if (switched_runtime.returncode or stale.returncode == 0
                or 'manual_handoff' not in stale.stdout):
            failures.append('manual observation from an earlier runtime authorized this session')
        self.assertFalse(failures, '\n'.join(failures))

    def test_plan_only_endpoint(self):
        plan = self.work / 'plan.md'
        plan.write_text('# Plan\n\n## Authorized endpoint\nPlan only; implementation is not authorized.\n',
                        encoding='utf-8')
        self.save_plan()
        skipped = self.run_ask('orchestrator-handoff', 'preflight', '--work-id', self.work_id,
                               '--entry', 'continue')
        if skipped.returncode or 'skipped' not in (skipped.stdout + skipped.stderr).lower():
            self.fail('generic continue did not preserve the plan-only endpoint')
        self.assertEqual(self.events(), [], 'plan-only continuation queried runtime or dispatched work')

    def test_capability_evidence(self):
        self.save_plan()
        static_only = self.run_ask('model', 'decision', 'capability', '--work-id', self.work_id,
                                   '--runtime', 'cursor')
        if static_only.returncode:
            self.fail('capability query failed: ' + (static_only.stderr or static_only.stdout))
        report = json.loads(static_only.stdout)
        self.assertEqual(report['runtime'], 'cursor')
        self.assertEqual(report['catalog'], 'unknown')
        self.assertEqual(report['identity'], 'unknown')
        self.assertEqual(report['switch'], 'unknown')

        self.write_adapter({'catalog': {'authenticated': True, 'models': ['gpt-6-luna']},
                            'identity': {'model': 'gpt-6-luna'}, 'switch_supported': False})
        codex = self.run_ask('model', 'decision', 'capability', '--work-id', self.work_id,
                             '--runtime', 'codex')
        if codex.returncode:
            self.fail('live Codex capability query failed: ' + (codex.stderr or codex.stdout))
        live = json.loads(codex.stdout)
        self.assertEqual(live['runtime'], 'codex')
        self.assertEqual(live['catalog'], 'unknown')
        self.assertEqual(live['identity'], 'supported')
        self.assertEqual(live['switch'], 'unsupported')
        self.assertTrue(live['evidence'])

        self.write_adapter({'catalog': {'authenticated': True, 'access_verified': True,
                                        'models': ['gpt-6-luna']},
                            'identity': {'model': 'gpt-6-luna'}, 'switch_supported': True})
        supported = self.run_ask('model', 'decision', 'capability', '--work-id', self.work_id,
                                 '--runtime', 'codex')
        self.assertEqual(supported.returncode, 0, supported.stderr or supported.stdout)
        self.assertEqual(json.loads(supported.stdout)['switch'], 'supported')


if __name__ == '__main__':
    unittest.main()
