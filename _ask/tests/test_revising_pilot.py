"""Migration, comprehension, and representative-passage pilot gates."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.source = {"schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
                       "nodes": [{"id": "intent", "type": "intent", "title": "Intent", "lifecycle": "active"},
                                 {"id": "case", "type": "scenario", "title": "Case", "lifecycle": "active",
                                  "reference": {"path": "specs/current/pilot.json", "id": "C-1"}}],
                       "edges": [{"type": "contains", "source": "intent", "target": "case"}]}
        self.target = copy.deepcopy(self.source)
        self.target.update(schema="ask-engineering-model/v2", revision=2)

    def test_reviewed_migration_binds_both_models_and_preserves_identity_authority(self):
        from engineering_model.migration import preservation_diff, review_migration

        diff = preservation_diff(self.source, self.target)
        approved = {"schema": "ask-engineering-migration-review/v1", "decision": "APPROVED",
                    "reviewer": "independent reviewer", "rationale": "Preserve recorded identity",
                    "source_digest": digest(self.source), "target_digest": digest(self.target),
                    "diff_digest": digest(diff)}
        result = review_migration(self.source, self.target, approved, work_id="pilot")
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["preservation_diff"], {"added_ids": [], "removed_ids": [],
                                                        "changed_references": [],
                                                        "changed_edges": {"removed": [], "added": []}})
        bad = copy.deepcopy(self.target)
        bad["nodes"][1]["reference"]["id"] = "C-2"
        with self.assertRaisesRegex(ValueError, "reference"):
            review_migration(self.source, bad, approved, work_id="pilot")

    def test_unreviewed_or_digest_stale_migration_is_refused(self):
        from engineering_model.migration import review_migration, preservation_diff

        review = {"decision": "APPROVED", "reviewer": "reviewer", "rationale": "reviewed",
                  "source_digest": digest(self.source), "target_digest": digest(self.target),
                  "diff_digest": digest(preservation_diff(self.source, self.target))}
        with self.assertRaisesRegex(ValueError, "schema"):
            review_migration(self.source, self.target, review, work_id="pilot")
        review["schema"] = "ask-engineering-migration-review/v1"
        changed = copy.deepcopy(self.target)
        changed["revision"] = 3
        with self.assertRaisesRegex(ValueError, "digest"):
            review_migration(self.source, changed, review, work_id="pilot")


if __name__ == "__main__":
    unittest.main()
