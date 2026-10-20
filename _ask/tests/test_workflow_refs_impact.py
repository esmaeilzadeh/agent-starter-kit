from __future__ import annotations

import unittest

from workflow_refs.impact import assess_impact, record_decision


S = "a/spec/1@1"
P = "a/spec/1/plan/1/item/1@1"
T = "b/spec/1/plan/1/task/1@1"
X = "b/spec/1/plan/1/task/2/test/1@1"
Q = "c/spec/1@1"
U = "c/spec/1/plan/1/item/1@1"


def graph():
    return {"nodes": {
        S: {"inputs": []}, P: {"inputs": [{"reference": S, "role": "requirement"}]},
        T: {"inputs": [{"reference": P, "role": "plan"}, {"reference": Q, "role": "shared-policy"}]},
        X: {"inputs": [{"reference": T, "role": "task"}]},
        Q: {"inputs": []}, U: {"inputs": [{"reference": Q, "role": "requirement"}]}}}


def decision(action="retain", generation="g1", **changes):
    value = {"action": action, "old_upstream": P, "new_upstream": P[:-1] + "2",
             "dependent": T, "profile": "structured-item/1", "context_generation": generation,
             "examined_paths": {"plan": "resolved", "shared-policy": "resolved"},
             "required_paths": ["plan", "shared-policy"],
             "review_evidence": "review-1", "reviewer": "owner-b-reviewer",
             "coordinator": "owner-b-coordinator", "outward_equal": True,
             "satisfies_new_inputs": True, "reuse_allowed": True}
    value.update(changes)
    return value


class ReferenceTests(unittest.TestCase):
    def test_direct_and_potential_impact(self):
        result = assess_impact(graph(), [S])
        self.assertEqual(result["status"], "complete")
        self.assertEqual(set(result["items"]), {P, T, X})
        self.assertNotIn(U, result["items"])
        self.assertEqual(result["items"][P]["status"], "reassess")
        self.assertTrue(any(edge["role"] == "shared-policy" for edge in result["items"][T]["inputs"]))

    def test_reviewed_stop_old_pin_or_new_revision(self):
        capture = {"status": "complete", "generation": "g1"}
        result = record_decision(decision(), capture)
        self.assertTrue(result["propagation_stopped"])
        self.assertEqual(result["status"], "retained")
        changed = decision(examined_paths={"plan": "resolved", "shared-policy": "changed"})
        self.assertFalse(record_decision(changed, capture)["propagation_stopped"])
        stale = decision(context_generation="g0")
        with self.assertRaises(Exception):
            record_decision(stale, capture)

    def test_retirement_preserves_shared_obligations(self):
        retired = record_decision(decision("retire"))
        self.assertEqual(retired["status"], "reassess")
        result = assess_impact(graph(), [P], {T: decision("retire")})
        self.assertIn(X, result["items"])
        self.assertIn(Q, graph()["nodes"][T]["inputs"][1]["reference"])

    def test_attributed_multiple_input_revalidation(self):
        capture = {"status": "complete", "generation": "g1"}
        incomplete = decision(examined_paths={"plan": "resolved", "shared-policy": "unknown"})
        self.assertEqual(assess_impact(graph(), [P], {T: incomplete}, capture)["status"], "incomplete")
        missing_authority = decision(coordinator="")
        with self.assertRaises(Exception):
            record_decision(missing_authority)

    def test_deletion_vs_unavailability_and_history(self):
        unavailable = graph()
        unavailable["nodes"][T]["resolved"] = False
        result = assess_impact(unavailable, [P])
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["items"][T]["status"], "incomplete")
        self.assertIn(T, unavailable["nodes"])
