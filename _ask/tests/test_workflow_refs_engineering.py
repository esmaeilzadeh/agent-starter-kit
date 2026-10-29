"""Engineering snapshot and selective-context integration contracts."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import subprocess
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask" / "scripts"))
sys.path.insert(0, str(ROOT / ".agents" / "ask"))

from engineering_model.snapshot import capture
from engineering_model.admission import admit
from engineering_model.projection import project
from engineering_model.readability import _resolve_captured_flow
from workflow_refs.codec import encode_envelope
from workflow_refs.compare import compare_items
from workflow_refs.compare import extract_git_item
from workflow_refs.impact import assess_impact
from workflow_refs import store as reference_store

from _ask.tests.engineering_fixture import workbench_model


class ReferenceTests(unittest.TestCase):
    def test_selected_projection_resolves_only_requested_compact_references(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            plan_path = root / "work/pilot/test-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            envelope = encode_envelope(plan, "ask-test-plan/v1", {
                "owner": "pilot", "type": "plan", "spec": 1,
            }, {
                "task": "pilot/spec/1/plan/1/task/1@1",
                "test": "pilot/spec/1/plan/1/task/1/test/1@1",
                "review": "pilot/review/1@1",
            })
            plan_path.write_text(json.dumps(envelope, separators=(",", ":")), encoding="utf-8")

            reference_items = {"items": [
                {"id": "task-1", "kind": "task"},
                {"id": "test-1", "kind": "test"},
                {"id": "review-1", "kind": "review"},
            ]}
            source_path = "work/pilot/reference-items.json"
            source = root / source_path
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(json.dumps(reference_items, separators=(",", ":")), encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", source_path], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "publish reference source"], cwd=root, check=True)
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                             text=True).strip()
            catalog = root / "work/pilot/references/integrity.json"
            reference_store.initialize_catalog(catalog, "pilot")
            for generation, (logical_id, item_id) in enumerate((
                ("pilot/spec/1/plan/1/task/1", "task-1"),
                ("pilot/spec/1/plan/1/task/1/test/1", "test-1"),
                ("pilot/review/1", "review-1"),
            )):
                reference_store.register_revision(
                    catalog, "pilot", logical_id, {"commit": commit, "path": source_path},
                    item_id, "structured-item/1", source.read_bytes(),
                    expected_generation=generation,
                )

            snapshot = capture(root, "pilot")
            original_resolve = reference_store.resolve_version
            with patch.object(reference_store, "resolve_version", wraps=original_resolve) as resolve:
                unselected = project(snapshot, root, include_evidence=False)
                self.assertEqual(resolve.call_count, 0,
                                 "ordinary projections do not load reference catalog entries")
                selected = project(snapshot, root, node_id="build", include_evidence=False)

            resolved = selected.get("references")
            self.assertIsInstance(resolved, dict,
                                  "selected projection exposes its compact task/test/review references")
            self.assertEqual(resolved.get("status"), "complete", resolved)
            self.assertEqual(set(resolved.get("items", {})), {"task", "test", "review"})
            self.assertTrue(all(value.get("status") == "resolved"
                                for value in resolved["items"].values()), resolved)
            self.assertEqual({name: value.get("reference")
                              for name, value in resolved["items"].items()},
                             snapshot.references["work/pilot/test-plan.json"])
            self.assertEqual({name: value.get("item_id")
                              for name, value in resolved["items"].items()},
                             {"task": "task-1", "test": "test-1", "review": "review-1"})
            self.assertEqual({call.args[1] for call in resolve.call_args_list},
                             set(snapshot.references["work/pilot/test-plan.json"].values()),
                             "selection resolves only the three requested qualified references")
            self.assertNotIn("references", unselected,
                             "unselected projections do not expose or resolve workflow references")
            selected_test = project(snapshot, root, node_id="case", include_evidence=False)
            self.assertEqual(selected_test["references"]["status"], "complete")
            self.assertEqual(set(selected_test["references"]["items"]), {"task", "test", "review"})

            original_references = dict(envelope["references"])
            for bad_reference, expected_code in (
                ("pilot/review/2@1", "missing"),
                ("other/review/1@1", "owner_mismatch"),
            ):
                broken = dict(envelope)
                broken["references"] = {**original_references, "review": bad_reference}
                plan_path.write_text(json.dumps(broken, separators=(",", ":")), encoding="utf-8")
                broken_projection = project(capture(root, "pilot"), root,
                                            node_id="build", include_evidence=False)
                reference_result = broken_projection["references"]
                self.assertEqual(reference_result["status"], "incomplete", reference_result)
                self.assertEqual(reference_result["items"]["review"]["status"], "unavailable")
                self.assertEqual(reference_result["items"]["review"]["error"]["code"], expected_code)
                self.assertEqual(reference_result["items"]["task"]["status"], "resolved",
                                 "a bad review link remains scoped to that reference")

            broken = dict(envelope)
            broken["references"] = {**original_references,
                                     "test": "pilot/spec/1/plan/1/task/2/test/1@1"}
            plan_path.write_text(json.dumps(broken, separators=(",", ":")), encoding="utf-8")
            wrong_parent = project(capture(root, "pilot"), root,
                                   node_id="build", include_evidence=False)["references"]
            self.assertEqual(wrong_parent["items"]["test"]["error"]["code"], "parent_mismatch")
            self.assertEqual(wrong_parent["items"]["task"]["status"], "resolved")

            broken = dict(envelope)
            broken["references"] = original_references
            plan_path.write_text(json.dumps(broken, separators=(",", ":")), encoding="utf-8")
            original_resolve = reference_store.resolve_version
            # The trusted store rejects duplicate catalog entries at publication;
            # inject its stable ambiguity error to verify projection scoping.
            def ambiguous_review(catalog_path, reference, repository_root=None):
                if reference == "pilot/review/1@1":
                    raise reference_store.CatalogError("ambiguous", "duplicate trusted target")
                return original_resolve(catalog_path, reference, repository_root)
            with patch.object(reference_store, "resolve_version", side_effect=ambiguous_review):
                ambiguous_projection = project(capture(root, "pilot"), root,
                                               node_id="build", include_evidence=False)
            reference_result = ambiguous_projection["references"]
            self.assertEqual(reference_result["status"], "incomplete", reference_result)
            self.assertEqual(reference_result["items"]["review"]["error"]["code"], "ambiguous")
            self.assertEqual(reference_result["items"]["task"]["status"], "resolved",
                             "an ambiguous link cannot poison unrelated selected references")

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
            with patch("engineering_model.projection.inspect_evidence",
                       side_effect=AssertionError("selected projection must not read evidence catalog")):
                compact_projection = project(snapshot, root, node_id="build", include_evidence=False)
            self.assertEqual(compact_projection["workbench"], legacy_projection["workbench"],
                             "on-demand task projection is equivalent without loading the evidence catalog")

            # A selected Task resolves its own canonical case from captured bytes;
            # another Task in the same snapshot remains independently selectable.
            case_plan = {
                "schema": "ask-test-plan/v1", "work_id": "pilot",
                "tests": [
                    {"id": "HIST-1", "scenario": {"given": "Historical input"}},
                    {"id": "CURR-1", "scenario": {"given": "Current input"}},
                ],
            }
            case_plan_raw = json.dumps(case_plan, separators=(",", ":")).encode()
            case_plan_path = root / "work/pilot/test-plan.json"
            case_plan_path.write_bytes(case_plan_raw)
            import hashlib
            case_plan_digest = hashlib.sha256(json.dumps(
                case_plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            selected_model = {
                "schema": "ask-engineering-model/v2", "work_id": "pilot", "revision": 1,
                "nodes": [
                    {"id": "historical-task", "type": "task", "title": "Historical task",
                     "lifecycle": "planned", "execution": {"work_id": "pilot", "task_id": "old"}},
                    {"id": "current-task", "type": "task", "title": "Current task",
                     "lifecycle": "planned", "execution": {"work_id": "pilot", "task_id": "current"}},
                    {"id": "historical-scenario", "type": "scenario", "title": "Historical scenario",
                     "lifecycle": "active", "case": {"work_id": "pilot", "plan_digest": case_plan_digest,
                                                           "case_id": "HIST-1"}},
                    {"id": "current-scenario", "type": "scenario", "title": "Current scenario",
                     "lifecycle": "active", "case": {"work_id": "pilot", "plan_digest": case_plan_digest,
                                                           "case_id": "CURR-1"}},
                    {"id": "historical-test", "type": "test", "title": "Historical test",
                     "lifecycle": "active", "reference": {"path": "work/pilot/test-plan.json",
                        "id": "HIST-1", "work_id": "pilot", "plan_digest": case_plan_digest}},
                    {"id": "current-test", "type": "test", "title": "Current test",
                     "lifecycle": "active", "reference": {"path": "work/pilot/test-plan.json",
                        "id": "CURR-1", "work_id": "pilot", "plan_digest": case_plan_digest}},
                ],
                "edges": [
                    {"type": "contributes_to", "source": "historical-task", "target": "historical-scenario"},
                    {"type": "contributes_to", "source": "current-task", "target": "current-scenario"},
                    {"type": "covers", "source": "historical-test", "target": "historical-scenario"},
                    {"type": "covers", "source": "current-test", "target": "current-scenario"},
                ],
            }
            selected_model_raw = json.dumps(selected_model, separators=(",", ":")).encode()
            (root / "work/pilot/engineering-model.json").write_bytes(selected_model_raw)
            captured = capture(root, "pilot")
            old_task, old_case, old_row, old_digest, old_source = _resolve_captured_flow(
                captured, "historical-task")
            current_task, current_case, current_row, current_digest, current_source = _resolve_captured_flow(
                captured, "current-task")
            self.assertEqual((old_task["id"], old_case["case_id"], old_row["id"]),
                             ("historical-task", "HIST-1", "HIST-1"))
            self.assertEqual((current_task["id"], current_case["case_id"], current_row["id"]),
                             ("current-task", "CURR-1", "CURR-1"))
            self.assertEqual(old_digest, current_digest)
            self.assertEqual(old_source, case_plan_raw)
            self.assertEqual(current_source, case_plan_raw,
                             "both selected contexts bind the exact captured plan source")

            ambiguous_plan = dict(case_plan, tests=case_plan["tests"] + [case_plan["tests"][1]])
            ambiguous_raw = json.dumps(ambiguous_plan, separators=(",", ":")).encode()
            case_plan_path.write_bytes(ambiguous_raw)
            ambiguous_digest = hashlib.sha256(json.dumps(
                ambiguous_plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            selected_model["nodes"][3]["case"]["plan_digest"] = ambiguous_digest
            selected_model["nodes"][5]["reference"]["plan_digest"] = ambiguous_digest
            (root / "work/pilot/engineering-model.json").write_text(
                json.dumps(selected_model, separators=(",", ":")), encoding="utf-8")
            ambiguous = capture(root, "pilot")
            with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
                _resolve_captured_flow(ambiguous, "current-task")

    def test_unrelated_item_and_external_constraint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            path = root / "items.json"
            first = {"items": [
                {"id": "independent", "revision": 7, "value": "unchanged", "inputs": []},
                {"id": "consumer", "revision": 3, "assertions": ["keeps the accepted output"],
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
            self.assertEqual(old_independent["payload"]["revision"], new_independent["payload"]["revision"])
            self.assertEqual(new_independent["payload"]["revision"], 7,
                             "unrelated document edits preserve the selected item's own revision")

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
                {key: value for key, value in old_consumer["payload"].items() if key != "inputs"},
                {key: value for key, value in new_consumer["payload"].items() if key != "inputs"},
                "structured-item/1",
                before_inputs=old_consumer["payload"]["inputs"],
                after_inputs=new_consumer["payload"]["inputs"],
            )
            old_local_payload = {key: value for key, value in old_consumer["payload"].items()
                                 if key != "inputs"}
            new_local_payload = {key: value for key, value in new_consumer["payload"].items()
                                 if key != "inputs"}
            self.assertEqual(old_local_payload, new_local_payload,
                             "the external binding changes while the consumer's local payload stays identical")
            self.assertEqual(changed_binding["status"], "changed",
                             "equal local payload cannot hide a changed external constraint")
            self.assertEqual(changed_binding["reason"], "input_bindings_changed")

            # Build trusted catalogs over the committed baseline, then move the
            # live candidate to the changed binding. Impact must refuse to
            # complete while that new dependency lacks a registered revision.
            shared_path = root / "specs/shared.json"
            shared_path.parent.mkdir(parents=True)
            shared_path.write_text(json.dumps({"items": [{"id": "shared-item", "inputs": []}]},
                                              separators=(",", ":")), encoding="utf-8")
            subprocess.run(["git", "add", "specs/shared.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "shared source"], cwd=root, check=True)
            shared_source = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                           capture_output=True, text=True).stdout.strip()
            for ref in ("refs/heads/develop", "refs/heads/main"):
                subprocess.run(["git", "update-ref", ref, shared_source], cwd=root, check=True)

            def catalog(owner, reference, source_commit, source_path, item_id):
                from workflow_refs.store import payload_digests
                raw = subprocess.run(["git", "show", f"{source_commit}:{source_path}"], cwd=root,
                                     check=True, capture_output=True).stdout
                entry = {"reference": reference, "logical_id": reference.rsplit("@", 1)[0],
                         "revision": 1, "snapshot_id": owner + "-snapshot", "item_id": item_id,
                         "profile": "structured-item/1", "digest_algorithm": "sha256",
                         "digests": payload_digests(raw),
                         "digest_semantics": sorted(payload_digests(raw)), "generation": 1}
                value = {"schema": "ask-reference-catalog/v1", "owner": owner,
                         "generation": 1, "entries": [entry], "snapshots": {
                             owner + "-snapshot": {"commit": source_commit, "path": source_path}}}
                target = root / "work" / owner / "references/integrity.json"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                                  encoding="utf-8")

            catalog("live", "live/spec/1@1", baseline, "items.json", "consumer")
            catalog("shared", "shared/spec/2/plan/1/item/4@1", shared_source,
                    "specs/shared.json", "shared-item")
            subprocess.run(["git", "add", "work"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "trusted reference catalogs"], cwd=root, check=True)
            catalog_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                            capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "update-ref", "refs/heads/agent/live", catalog_commit],
                           cwd=root, check=True)
            for owner in ("live", "shared"):
                subprocess.run(["git", "update-ref", f"refs/ask/references/{owner}", catalog_commit],
                               cwd=root, check=True)

            from workflow_refs.project import capture_project
            captured = capture_project(root, shared_owners={"shared"})
            self.assertEqual(captured["status"], "complete", captured)
            blocked = assess_impact(None, ["shared/spec/2/plan/1/item/4@1"],
                                    capture=captured, repository_root=root)
            self.assertEqual(blocked["status"], "incomplete", blocked)
            self.assertEqual(blocked["reason"], "discovery_incomplete", blocked)
            self.assertTrue(blocked.get("unresolved"),
                            "new-context completion stays blocked by the unregistered candidate dependency")


if __name__ == "__main__":
    unittest.main()
