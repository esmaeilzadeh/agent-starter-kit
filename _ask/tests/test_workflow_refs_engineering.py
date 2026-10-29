"""Engineering snapshot and selective-context integration contracts."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import subprocess

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask" / "scripts"))
sys.path.insert(0, str(ROOT / ".agents" / "ask"))

from engineering_model.snapshot import capture
from engineering_model.admission import admit
from engineering_model.projection import project
from workflow_refs.codec import encode_envelope
from workflow_refs.compare import compare_items
from workflow_refs.compare import extract_git_item
from workflow_refs.impact import assess_impact

from _ask.tests.engineering_fixture import workbench_model


class ReferenceTests(unittest.TestCase):
    def test_snapshots_context_and_legacy_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, _spec = workbench_model(root)
            plan_path = root / "work/pilot/test-plan.json"
            legacy_plan = json.loads(plan_path.read_text(encoding="utf-8"))
            legacy = capture(root, "pilot")
            legacy_errors = legacy.diagnostics(root)
            self.assertEqual(legacy_errors, [], "legacy admission remains the reference behavior")
            legacy_projection = project(legacy, root, node_id="build", include_evidence=False)

            compact_plan = encode_envelope(legacy_plan, "ask-test-plan/v1", {
                "owner": "pilot", "type": "plan", "spec": 1,
            }, {
                "task": "pilot/spec/1/plan/1/task/1@1",
                "test": "pilot/spec/1/plan/1/task/1/test/1@1",
                "review": "pilot/review/1@1",
            })
            plan_path.write_text(json.dumps(compact_plan, separators=(",", ":")), encoding="utf-8")

            snapshot = capture(root, "pilot")
            self.assertEqual(snapshot.document, model)
            self.assertEqual(snapshot.files["work/pilot/test-plan.json"], plan_path.read_bytes(),
                             "the exact compact source bytes remain bound to the capture")
            self.assertEqual(getattr(snapshot, "documents", {}).get("work/pilot/test-plan.json"), legacy_plan,
                             "captured compact plan must expose its normalized legacy read projection")
            self.assertEqual(getattr(snapshot, "references", {}).get("work/pilot/test-plan.json"), {
                "task": "pilot/spec/1/plan/1/task/1@1",
                "test": "pilot/spec/1/plan/1/task/1/test/1@1",
                "review": "pilot/review/1@1",
            }, "selected task context must inherit numeric IDs and retain review context")
            compact_errors = snapshot.diagnostics(root)
            self.assertEqual(compact_errors, legacy_errors,
                             "compact admission diagnostics must match the legacy source")
            admitted, admission_errors = admit(root, "pilot")
            self.assertEqual(admission_errors, [], admission_errors)
            self.assertEqual(getattr(admitted, "documents", {}).get("work/pilot/test-plan.json"), legacy_plan)
            compact_projection = project(snapshot, root, node_id="build", include_evidence=False)
            self.assertEqual(compact_projection["workbench"], legacy_projection["workbench"],
                             "on-demand task projection is equivalent without loading the evidence catalog")

    def test_unrelated_item_and_external_constraint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            path = root / "items.json"
            first = {"items": [
                {"id": "independent", "value": "unchanged", "inputs": []},
                {"id": "consumer", "assertions": ["keeps the accepted output"],
                 "inputs": [{"reference": "shared/spec/2/plan/1/item/4@1",
                             "role": "shared-constraint"}]},
            ], "unrelated": {"revision": 1}}
            path.write_text(json.dumps(first, separators=(",", ":")), encoding="utf-8")
            subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "baseline source"], cwd=root, check=True)
            baseline = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                      capture_output=True, text=True).stdout.strip()

            # Editing an unrelated section preserves both selected item revisions.
            first["unrelated"]["revision"] = 2
            path.write_text(json.dumps(first, separators=(",", ":")), encoding="utf-8")
            subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "unrelated document edit"], cwd=root, check=True)
            unrelated = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                       capture_output=True, text=True).stdout.strip()
            old_independent = extract_git_item(root, baseline, "items.json", "independent", "structured-item/1")
            new_independent = extract_git_item(root, unrelated, "items.json", "independent", "structured-item/1")
            self.assertEqual(old_independent["status"], "found")
            self.assertEqual(new_independent["status"], "found")
            independent = compare_items(old_independent["payload"], new_independent["payload"],
                                        "structured-item/1", before_inputs=[], after_inputs=[])
            self.assertEqual(independent["status"], "unchanged",
                             "unrelated source edits preserve independent item eligibility")
            self.assertEqual(old_independent["canonical_digest"], new_independent["canonical_digest"])

            old_consumer = extract_git_item(root, baseline, "items.json", "consumer", "structured-item/1")
            changed = json.loads(path.read_text(encoding="utf-8"))
            changed["items"][1]["inputs"][0]["reference"] = "shared/spec/2/plan/1/item/4@2"
            path.write_text(json.dumps(changed, separators=(",", ":")), encoding="utf-8")
            subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "external constraint revision"], cwd=root, check=True)
            constraint_change = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                               capture_output=True, text=True).stdout.strip()
            new_consumer = extract_git_item(root, constraint_change, "items.json", "consumer", "structured-item/1")
            changed_binding = compare_items(
                old_consumer["payload"], new_consumer["payload"], "structured-item/1",
                before_inputs=old_consumer["payload"]["inputs"],
                after_inputs=new_consumer["payload"]["inputs"],
            )
            self.assertEqual(old_consumer["payload"]["assertions"], new_consumer["payload"]["assertions"])
            self.assertEqual(changed_binding["status"], "changed",
                             "equal local payload cannot hide a changed external constraint")

        reference = "shared/spec/2/plan/1/item/4@2"
        blocked = assess_impact({"nodes": {}}, [reference])
        self.assertEqual(blocked["status"], "incomplete",
                         "new-context impact cannot complete without a captured project context")


if __name__ == "__main__":
    unittest.main()
