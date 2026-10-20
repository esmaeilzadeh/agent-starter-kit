"""Behavioral contract for profile-aware artifact comparison."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from workflow_refs.compare import compare_items, extract_git_item
from workflow_refs.profiles import get_profile


class ReferenceTests(unittest.TestCase):
    def test_complete_item_and_binding_equivalence(self):
        payload = {"id": "item-1", "constraints": {"timeout": 10}, "unknown": [1, None]}
        same = compare_items(payload, dict(payload), "structured-item/1",
                             before_inputs=[{"reference": "alpha/spec/2@1", "role": "source"}],
                             after_inputs=[{"reference": "alpha/spec/2@1", "role": "source"}])
        self.assertEqual(same["status"], "unchanged")
        rebound = compare_items(payload, dict(payload), "structured-item/1",
                                before_inputs=[{"reference": "alpha/spec/2@1", "role": "source"}],
                                after_inputs=[{"reference": "alpha/spec/2@2", "role": "source"}])
        self.assertEqual(rebound["status"], "changed", "external revision changes matter despite equal blobs")
        role_changed = compare_items(payload, dict(payload), "structured-item/1",
                                     before_inputs=[{"reference": "alpha/spec/2@1", "role": "source"}],
                                     after_inputs=[{"reference": "alpha/spec/2@1", "role": "constraint"}])
        self.assertEqual(role_changed["status"], "changed")
        unknown_changed = compare_items(payload, {**payload, "unknown": [1, 2]}, "structured-item/1",
                                        before_inputs=[], after_inputs=[])
        self.assertEqual(unknown_changed["status"], "changed", "unknown fields remain significant")

    def test_profile_exclusions_and_unavailability(self):
        self.assertEqual(get_profile("structured-item/1")["format"], "json")
        self.assertEqual(get_profile("prose-item/1")["presentation"], "exact-bytes")
        json_same = compare_items('{"id":"x","values":[1,2]}',
                                  '{\n "values": [1, 2], "id": "x"\n}',
                                  "structured-item/1")
        self.assertEqual(json_same["status"], "unchanged")
        prose_changed = compare_items(b"heading\n", b"heading \n", "prose-item/1")
        self.assertEqual(prose_changed["status"], "changed")
        obligation_changed = compare_items({"timeout": 10}, {"timeout": 20}, "structured-item/1")
        self.assertEqual(obligation_changed["status"], "changed")
        missing = compare_items({"id": "x"}, {"id": "x"}, "unknown-profile/9")
        self.assertEqual(missing["status"], "incomplete")
        changed_profile = compare_items({"id": "x"}, {"id": "x"}, "structured-item/1",
                                        before_profile="structured-item/1", after_profile="unknown-profile/9")
        self.assertEqual(changed_profile["status"], "incomplete")
        incomplete_inputs = compare_items({"id": "x"}, {"id": "x"}, "structured-item/1",
                                          before_inputs=None, after_inputs=[])
        self.assertEqual(incomplete_inputs["status"], "incomplete")

    def test_git_items_moves_and_unrelated_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            source = root / "items.json"
            first_doc = {"items": [{"id": "alpha", "value": 1}, {"id": "beta", "value": 2}],
                         "unrelated": {"format": "old"}}
            source.write_text(json.dumps(first_doc), encoding="utf-8")
            subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "first snapshot"], cwd=root, check=True)
            first = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            second_doc = {"unrelated": {"format": "new"},
                          "items": [{"value": 1, "id": "alpha"}, {"id": "beta", "value": 3},
                                    {"id": "gamma", "value": 4}]}
            source.write_text(json.dumps(second_doc, indent=2), encoding="utf-8")
            subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "second snapshot"], cwd=root, check=True)
            second = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            old_alpha = extract_git_item(root, first, "items.json", "alpha", "structured-item/1")
            new_alpha = extract_git_item(root, second, "items.json", "alpha", "structured-item/1")
            self.assertEqual(old_alpha["status"], "found")
            self.assertEqual(compare_items(old_alpha["payload"], new_alpha["payload"], "structured-item/1")["status"], "unchanged")
            old_beta = extract_git_item(root, first, "items.json", "beta", "structured-item/1")
            new_beta = extract_git_item(root, second, "items.json", "beta", "structured-item/1")
            self.assertEqual(compare_items(old_beta["payload"], new_beta["payload"], "structured-item/1")["status"], "changed")
            moved = compare_items(old_alpha["payload"], new_alpha["payload"], "structured-item/1",
                                  before_inputs=[{"reference": "alpha/spec/2/plan/1/item/1@1", "role": "owner"}],
                                  after_inputs=[{"reference": "alpha/spec/2/plan/1/item/2@1", "role": "owner"}])
            self.assertEqual(moved["status"], "changed")
            absent = extract_git_item(root, second, "items.json", "missing", "structured-item/1")
            self.assertEqual(absent["status"], "absent")
            for commit, path in (("f" * 40, "items.json"), (second, "../items.json"), (second, "missing.json")):
                result = extract_git_item(root, commit, path, "alpha", "structured-item/1")
                self.assertEqual(result["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
