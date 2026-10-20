"""Behavioral contract for qualified workflow identity grammar."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from workflow_refs.identity import ReferenceError, display_git_id, normalize_references, parse_reference, reference_sort_key, resolve_git_id


class ReferenceTests(unittest.TestCase):
    def test_qualified_numeric_context(self):
        references = [
            "alpha/spec/2@1",
            "alpha/spec/2/part/10@3",
            "alpha/spec/2/plan/10@2",
            "alpha/spec/2/plan/10/item/2@1",
            "alpha/spec/2/plan/10/task/3@4",
            "alpha/spec/2/plan/10/task/3/test/10@2",
            "repository-runs/run/3/log/2@1",
        ]
        parsed = [parse_reference(value) for value in references]
        self.assertIsNotNone(parsed[0], "qualified references must parse into numeric identities")
        self.assertEqual([item["canonical"] for item in parsed], references)
        self.assertEqual(parse_reference("alpha/spec/2/plan/10/task/3/test/10@2")["revision"], 2)
        self.assertLess(reference_sort_key("alpha/spec/2@1"), reference_sort_key("alpha/spec/10@1"))
        with self.assertRaises(ReferenceError):
            parse_reference("alpha/spec/02@1")
        with self.assertRaises(ReferenceError):
            parse_reference("alpha/spec/0@1")
        for malformed in ("alpha/task/1@1", "alpha/test/1@1", "alpha/plan/1@1", "alpha/part/1@1"):
            try:
                parse_reference(malformed)
            except ReferenceError:
                pass
            else:
                self.fail(f"hierarchical reference bypassed required parents: {malformed}")
        with self.assertRaises(ReferenceError):
            parse_reference({"id": 3, "revision": 1}, {"owner": "alpha", "type": "task"})
        inherited = parse_reference({"id": 3, "revision": 4}, {
            "owner": "alpha", "type": "task", "spec": 2, "plan": 10,
        })
        self.assertEqual(inherited["canonical"], "alpha/spec/2/plan/10/task/3@4")
        for bad in (True, {"id": 0, "revision": 1}, {"id": 2, "revision": True}, {"id": 2}):
            with self.assertRaises(ReferenceError):
                parse_reference(bad, {"owner": "alpha", "type": "task", "spec": 2, "plan": 10})

    def test_parents_moves_and_multiple_inputs(self):
        context = {"owner": "alpha", "type": "task", "spec": 2, "plan": 4}
        refs = normalize_references([
            {"id": 7, "revision": 1}, "beta/spec/3/plan/1@2",
        ], context)
        self.assertEqual(len(refs), 2, "all declared input edges must be retained")
        self.assertEqual(refs, (
            "alpha/spec/2/plan/4/task/7@1", "beta/spec/3/plan/1@2",
        ))
        old = parse_reference("alpha/spec/2/plan/4/task/7@1")
        moved = parse_reference("alpha/spec/2/plan/4/task/7@1")
        self.assertEqual(old["logical_id"], moved["logical_id"])
        self.assertEqual(len(refs), 2, "independent dependency edges must not be collapsed")
        with self.assertRaises(ReferenceError):
            normalize_references([{"id": 7, "revision": 1}], {"owner": "alpha", "type": "task"})
        for malformed in ("alpha/task/1@1", "alpha/test/1@1", "alpha/plan/1@1", "alpha/part/1@1"):
            try:
                parse_reference(malformed)
            except ReferenceError:
                pass
            else:
                self.fail(f"hierarchical reference bypassed required parents: {malformed}")
        # Ancestor versions do not alter the numeric logical identity. A move
        # to a different parent creates a distinct ID while the original target
        # remains resolvable from its historical qualified reference.
        old = parse_reference("alpha/spec/2/plan/4/task/7@1")
        same_child_new_ancestor_revision = parse_reference("alpha/spec/2/plan/4/task/7@2")
        moved = parse_reference("alpha/spec/2/plan/5/task/7@1")
        self.assertEqual(old["logical_id"], same_child_new_ancestor_revision["logical_id"])
        self.assertNotEqual(old["logical_id"], moved["logical_id"])
        self.assertEqual(old["canonical"], "alpha/spec/2/plan/4/task/7@1")

    def test_raw_git_collision_resolution(self):
        first = "a1b2c3d4" + "0" * 32
        second = "a1b2c3d4" + "1" * 32
        other = "f0e1d2c3" + "2" * 32
        known = [first, second, other]
        self.assertEqual(display_git_id(first, known), first)
        self.assertEqual(display_git_id(other, known), "f0e1d2c3")
        with self.assertRaises(ReferenceError):
            resolve_git_id("a1b2c3d4", known)
        self.assertEqual(resolve_git_id(first, known), first)
        with self.assertRaises(ReferenceError):
            resolve_git_id("deadbeef", known)


if __name__ == "__main__":
    unittest.main()
