"""Read-only evidence projection against actual disposable coordinator records."""
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.agents/ask'))
sys.path.insert(0, str(ROOT / '_ask/scripts'))

from traceability_fixture import Consumer
from verification.traceability.contracts import digest
from verification.traceability.service import check_completion


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.consumer = Consumer()
        self.addCleanup(self.consumer.close)
        self.root = self.consumer.root
        self.runtime = self.root / 'work/w/traceability'

    def snapshot(self):
        # Include Git objects/refs and mtimes: rewriting identical bytes is a write.
        return {str(path.relative_to(self.root)):
                (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
                for path in self.root.rglob('*') if path.is_file()}

    def inspect(self, candidate_sha=None):
        before = self.snapshot()
        run = subprocess.run

        def read_command(argv, *arguments, **options):
            self.assertIsInstance(argv, (list, tuple))
            self.assertEqual(argv[0], 'git', 'Inspection must not execute tests or commands')
            self.assertIn(argv[1], {'rev-parse', 'show', 'cat-file', 'merge-base',
                                    'diff', 'ls-files'})
            return run(argv, *arguments, **options)

        with patch('subprocess.run', side_effect=read_command):
            if importlib.util.find_spec('engineering_model.evidence') is None:
                # The existing completion seam supplies a behavioral red until the
                # read-only extraction exists; no missing-import/attribute red.
                result = {'completion': check_completion(self.root, 'w', candidate_sha)}
            else:
                result = importlib.import_module('engineering_model.evidence').inspect(
                    self.root, 'w', candidate_sha)
        after = self.snapshot()
        changed = sorted(name for name in before.keys() | after.keys()
                         if before.get(name) != after.get(name))
        self.assertEqual(changed, [], 'Inspection changed repository artifacts or refs')
        return result

    def verified(self):
        process = self.consumer.command('verify')
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        receipt = self.runtime / ('static-' + self.consumer.sha + '.json')
        self.assertEqual(json.loads(receipt.read_text())['result'], 'pass')
        return receipt

    def assert_invalid(self, result, error):
        self.assertEqual(result['status'], 'invalid', result)
        self.assertFalse(result['current_completion'])
        self.assertEqual(result['completion']['status'], 'fail')
        self.assertIn(error, ' '.join(result['completion']['errors']))

    def test_real_evidence_and_tamper_is_read_only(self):
        receipt_path = self.verified()
        result = self.inspect()
        self.assertEqual(result['status'], 'valid', result)
        self.assertTrue(result['current_completion'])
        self.assertFalse(result['historical'])
        self.assertEqual(result['candidate_sha'], self.consumer.sha)
        self.assertEqual(result['completion']['status'], 'pass')
        scenario = result['scenarios'][0]
        self.assertEqual((scenario['criterion_id'], scenario['given'], scenario['when'], scenario['then']),
                         ('C1', 'lowercase text', 'rendered through domain or CLI',
                          ['uppercase text is returned']))
        self.assertEqual(scenario['required_types'], ['unit', 'e2e'])
        tests = {test['id']: test for test in scenario['tests']}
        self.assertEqual(set(tests), {'U', 'E'})
        self.assertEqual(tests['U']['expected_assertions'],
                         [{'criterion_id': 'C1', 'checks': ['Exact HELLO output']}])
        self.assertEqual(tests['U']['case_id'], 'test_app.Cases.test_unit')
        self.assertEqual(tests['U']['source_paths'], ['test_app.py'])
        rows = result['completion']['criterion_evidence'][0]['tests']
        self.assertEqual({row['tdd'] for row in rows}, {'red_green'})
        self.assertEqual({row['final_execution']['outcome'] for row in rows}, {'passed'})
        self.assertEqual({row['final_execution']['source_sha'] for row in rows},
                         {self.consumer.sha})
        self.assertTrue(all(row['red'][0]['failure_kind'] == 'behavior_assertion' for row in rows))
        self.assertTrue(all(row['final_execution']['output_digest'] for row in rows))

        # A cached pass is deliberately retained throughout all these mutations.
        receipt = json.loads(receipt_path.read_text())
        behavior_log = self.root / rows[0]['final_execution']['output_artifact']
        static_log = self.root / receipt['checks'][0]['evidence']
        for path, error in [(behavior_log, 'execution log'), (static_log, 'static execution log')]:
            original = path.read_bytes()
            try:
                path.write_bytes(original + b'\nforged retained output\n')
                self.assert_invalid(self.inspect(), error)
            finally:
                path.write_bytes(original)

        for mutate, error in [
            (lambda doc: doc.update(checkplan_digest='forged'), 'CheckPlan'),
            (lambda doc: doc.update(runner_digest='forged'), 'pinned runner/CheckPlan'),
            (lambda doc: doc['checks'][0].update(exit_code=1), 'pinned runner/CheckPlan'),
            (lambda doc: doc.update(candidate_sha=self.consumer.red_sha), 'static verification'),
        ]:
            modified = copy.deepcopy(receipt)
            mutate(modified)
            try:
                self.consumer.write(str(receipt_path.relative_to(self.root)), modified)
                self.assert_invalid(self.inspect(), error)
            finally:
                self.consumer.write(str(receipt_path.relative_to(self.root)), receipt)

        ledger_path = self.runtime / 'executions.json'
        ledger = json.loads(ledger_path.read_text())
        latest = next(entry for entry in reversed(ledger) if entry['phase'] == 'final_green')
        report_path = self.runtime / 'runs' / latest['run_id'] / 'results.json'
        report = json.loads(report_path.read_text())
        modified = copy.deepcopy(report)
        modified['runner_identity']['adapter_digest'] = 'forged'
        altered_ledger = copy.deepcopy(ledger)
        next(entry for entry in altered_ledger if entry['run_id'] == latest['run_id'])['digest'] = digest(modified)
        try:
            self.consumer.write(str(report_path.relative_to(self.root)), modified)
            ledger_path.write_text(json.dumps(altered_ledger))
            self.assert_invalid(self.inspect(), 'stale contracts or runner')
        finally:
            self.consumer.write(str(report_path.relative_to(self.root)), report)
            ledger_path.write_text(json.dumps(ledger))

        review_path = self.runtime / 'reviews' / (self.consumer.sha + '.json')
        review = json.loads(review_path.read_text())
        modified = copy.deepcopy(review)
        modified['review']['tests'][0]['counterexample'] = ''
        modified['review_digest'] = digest(modified['review'])
        try:
            self.consumer.write(str(review_path.relative_to(self.root)), modified)
            self.assert_invalid(self.inspect(), 'assertion review')
        finally:
            self.consumer.write(str(review_path.relative_to(self.root)), review)

        test_path = self.root / 'test_app.py'
        original = test_path.read_bytes()
        try:
            test_path.write_bytes(original + b'\n# uncommitted source change\n')
            self.assert_invalid(self.inspect(), 'candidate source')
        finally:
            test_path.write_bytes(original)

        self.consumer.git('update-ref', '-d', 'refs/ask/accepted-tests/w')
        missing = self.inspect()
        self.assertEqual(missing['status'], 'unavailable', missing)
        self.assertFalse(missing['current_completion'])
        self.assertIn('accepted-tests ref', ' '.join(missing['completion']['errors']))

    def test_missing_and_historical_evidence(self):
        receipt_path = self.verified()
        ledger_path = self.runtime / 'executions.json'
        ledger = ledger_path.read_bytes()
        ledger_path.unlink()
        missing = self.inspect()
        self.assertEqual(missing['status'], 'unavailable', missing)
        self.assertFalse(missing['current_completion'])
        self.assertIn('case evidence', ' '.join(missing['completion']['errors']))
        ledger_path.write_bytes(ledger)
        for path in [ledger_path, receipt_path]:
            original = path.read_bytes()
            try:
                path.write_text('{malformed')
                malformed = self.inspect()
                self.assertEqual(malformed['status'], 'invalid', malformed)
                self.assertFalse(malformed['current_completion'])
            finally:
                path.write_bytes(original)

        # Every candidate-bound input changes on the current branch. Inspection
        # must still use the old revision's plan, policy, adapter and runner.
        self.consumer.write('.agents/verification.yaml',
                            "checks:\n  - command: false\n    tier: mandatory\n")
        for name in ['_ask/policies/delegation.md', '.agents/ask/verification/run.py',
                     '.agents/ask/verification/traceability/unittest_runner.py', 'test_app.py']:
            path = self.root / name
            path.write_text(path.read_text() + '\n# later unrelated revision\n')
        spec = copy.deepcopy(self.consumer.spec)
        spec['criteria'][0]['given'] = 'later changed canonical scenario'
        self.consumer.write('specs/current/w.json', spec)
        current_sha = self.consumer.commit('later scenario, policy, CheckPlan and runners')
        historical = self.inspect(self.consumer.sha)
        self.assertEqual(historical['status'], 'historical', historical)
        self.assertTrue(historical['historical'])
        self.assertFalse(historical['current_completion'])
        self.assertEqual(historical['current_sha'], current_sha)
        self.assertEqual(historical['candidate_sha'], self.consumer.sha)
        self.assertEqual(historical['completion']['status'], 'pass', historical)
        self.assertEqual(historical['scenarios'][0]['given'], 'lowercase text')
        self.assertEqual(historical['completion']['input_digests']['spec'], digest(self.consumer.spec))
        self.assertEqual(historical['completion']['criterion_evidence'][0]['tests'][0]
                         ['final_execution']['source_sha'], self.consumer.sha)

        # Historical evidence is still validated, not accepted because it is old.
        receipt = json.loads(receipt_path.read_text())
        artifact = self.root / receipt['checks'][0]['evidence']
        artifact.write_bytes(artifact.read_bytes() + b'\nchanged historical output\n')
        tampered = self.inspect(self.consumer.sha)
        self.assert_invalid(tampered, 'static execution log')
        self.assertTrue(tampered['historical'])


if __name__ == '__main__':
    unittest.main()
