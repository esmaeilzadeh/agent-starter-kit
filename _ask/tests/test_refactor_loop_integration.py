"""Public regressions for the accepted inner-loop lifecycle and retry behavior."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


ROOT = Path(__file__).resolve().parents[2]


class LoopTests(unittest.TestCase):
    def run_existing_scenario(self, method):
        from inner_loop_reliability import IntegrationTests
        case = IntegrationTests(methodName=method)
        result = unittest.TestResult()
        case.run(result)
        problems = result.failures + result.errors
        self.assertFalse(problems, "\n".join(detail for _, detail in problems))

    def test_rejected_review_does_not_integrate(self):
        self.run_existing_scenario("test_review_rejection_and_boundary_rejection_prevent_integration")

    def test_changed_candidate_needs_fresh_review(self):
        self.run_existing_scenario("test_changed_result_or_review_cannot_reuse_approval")

    def test_clean_candidate_integrates_after_checks(self):
        self.run_existing_scenario("test_fast_forward_matches_verified_candidate")

    def test_retry_bounds_and_vocabulary_remain_compatible(self):
        cases = [
            (0, 0, "REJECTED", "ok", "implement"),
            (2, 0, "REJECTED", "ok", "debug"),
            (2, 2, "REJECTED", "ok", "blocked"),
            (0, 0, "APPROVED", "ok", "integrate"),
            (0, 0, "REJECTED", "glob_too_narrow", "blocked"),
        ]
        for review, debug, verdict, boundary, expected in cases:
            output = subprocess.run(
                [str(ROOT / "ask"), "inner-loop", "next-action", "--review-round", str(review),
                 "--debug-round", str(debug), "--verdict", verdict, "--boundary", boundary],
                cwd=ROOT, text=True, capture_output=True, check=True,
            ).stdout.strip()
            self.assertEqual(output, expected, f"retry contract changed for {(review, debug, verdict, boundary)}")

    def test_approved_candidate_with_failed_checks_does_not_integrate(self):
        self.run_existing_scenario("test_failed_candidate_checks_prevent_fast_forward_and_state_fold")


if __name__ == "__main__":
    unittest.main()
