"""Engineering snapshot and selective-context integration contracts."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask" / "scripts"))
sys.path.insert(0, str(ROOT / ".agents" / "ask"))

from engineering_model.snapshot import capture
from workflow_refs.codec import encode_envelope
from workflow_refs.compare import compare_items
from workflow_refs.impact import assess_impact


class ReferenceTests(unittest.TestCase):
    def test_snapshots_context_and_legacy_reads(self):
        model = {
            "schema": "ask-engineering-model/v1",
            "work_id": "pilot",
            "revision": 1,
            "nodes": [{"id": "build", "type": "task", "title": "Build",
                       "lifecycle": "planned"},
                      {"id": "case", "type": "test", "title": "Selected case",
                       "lifecycle": "active",
                       "reference": {"path": "work/pilot/test-plan.json", "id": "case-local"}}],
            "edges": [],
        }
        test_plan = {
            "schema": "ask-test-plan/v1", "work_id": "pilot",
            "task_scopes": [{"task_id": "build", "test_ids": ["case-local"]}],
            "flow_mappings": [{"test_case": {"scope": "external", "work_id": "shared"}}],
            "tests": [{"id": "case-local", "type": "unit", "criterion_ids": ["P-1"]}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model_path = root / "work/pilot/engineering-model.json"
            model_path.parent.mkdir(parents=True)
            model_path.write_text(json.dumps(model), encoding="utf-8")
            spec_path = root / "specs/current/pilot.json"
            spec_path.parent.mkdir(parents=True)
            spec_path.write_text(json.dumps({"schema": "ask-spec/v1", "work_id": "pilot",
                                             "criteria": [{"id": "P-1"}]}), encoding="utf-8")
            (root / "specs/current/pilot.md").write_text("# Pilot\n", encoding="utf-8")
            graph_path = root / "work/pilot/inner-loop/tasks.yaml"
            graph_path.parent.mkdir(parents=True, exist_ok=True)
            graph_path.write_text("schema: ask-inner-loop-tasks/v1\nwork_id: pilot\ntasks:\n  - id: build\n",
                                  encoding="utf-8")
            shared_plan = root / "work/shared/test-plan.json"
            shared_plan.parent.mkdir(parents=True)
            shared_plan.write_text(json.dumps({"schema": "ask-test-plan/v1", "work_id": "shared",
                                               "tests": []}), encoding="utf-8")
            plan_path = root / "work/pilot/test-plan.json"
            compact_plan = encode_envelope(test_plan, "ask-test-plan/v1", {
                "owner": "pilot", "type": "plan", "spec": 1,
            }, {
                "task": "pilot/spec/1/plan/1/task/2@1",
                "test": "pilot/spec/1/plan/1/task/2/test/3@1",
                "review": "pilot/review/1@1",
            })
            plan_path.write_text(json.dumps(compact_plan, separators=(",", ":")), encoding="utf-8")

            legacy = capture(root, "pilot")
            self.assertEqual(legacy.document, model)
            snapshot = capture(root, "pilot")
            self.assertIn("work/shared/test-plan.json", snapshot.files,
                          "normalized plans must keep their declared external source closure")
            self.assertEqual(getattr(snapshot, "documents", {}).get("work/pilot/test-plan.json"), test_plan,
                             "captured compact plan must expose its normalized legacy read projection")
            self.assertEqual(getattr(snapshot, "references", {}).get("work/pilot/test-plan.json"), {
                "task": "pilot/spec/1/plan/1/task/2@1",
                "test": "pilot/spec/1/plan/1/task/2/test/3@1",
                "review": "pilot/review/1@1",
            }, "selected task context must inherit numeric IDs and retain review context")

    def test_unrelated_item_and_external_constraint(self):
        payload = {"id": "consumer", "assertions": ["keeps the accepted output"]}
        reference = "shared/spec/2/plan/1/item/4@1"
        same_item_unrelated_edit = compare_items(
            payload, dict(payload), "structured-item/1",
            before_inputs=[{"reference": reference, "role": "shared-constraint"}],
            after_inputs=[{"reference": reference, "role": "shared-constraint"}],
        )
        self.assertEqual(same_item_unrelated_edit["status"], "unchanged")

        changed_binding = compare_items(
            payload, dict(payload), "structured-item/1",
            before_inputs=[{"reference": reference, "role": "shared-constraint"}],
            after_inputs=[{"reference": "shared/spec/2/plan/1/item/4@2",
                           "role": "shared-constraint"}],
        )
        self.assertEqual(changed_binding["status"], "changed",
                         "equal local payload cannot hide a changed external constraint")

        blocked = assess_impact({"nodes": {}}, [reference])
        self.assertEqual(blocked["status"], "incomplete",
                         "new-context impact cannot complete without a captured project context")


if __name__ == "__main__":
    unittest.main()
