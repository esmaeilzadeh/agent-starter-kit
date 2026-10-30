from __future__ import annotations

import unittest
import json
import subprocess
import tempfile
from pathlib import Path
from copy import deepcopy

from workflow_refs.impact import assess_impact, record_decision
from workflow_refs.project import capture_project, load_project_graph
from workflow_refs.store import payload_digests


S = "a/spec/1@1"
P = "a/spec/1/plan/1/item/1@1"
P2 = "a/spec/1/plan/1/item/1@2"
T = "b/spec/1/plan/1/task/1@1"
T2 = "b/spec/1/plan/1/task/1@2"
X = "b/spec/1/plan/1/task/2/test/1@1"
Y = "b/spec/1/plan/1/task/3/test/1@1"
Q = "c/spec/1@1"
U = "c/spec/1/plan/1/item/1@1"
V = "c/spec/1/plan/1/item/2@1"
W = "c/spec/1/plan/1/item/3@1"


def graph():
    return {"nodes": {
        S: {"inputs": []}, P: {"inputs": [{"reference": S, "role": "requirement"}]},
        T: {"inputs": [{"reference": P, "role": "plan"}, {"reference": Q, "role": "shared-policy"}]},
        X: {"inputs": [{"reference": T, "role": "task"}]},
        Q: {"inputs": []}, U: {"inputs": [{"reference": Q, "role": "requirement"}]}}}


def decision(action="retain", generation="g1", **changes):
    paths = sorted([f"{P}|plan", f"{Q}|shared-policy"])
    value = {"action": action, "old_upstream": P, "new_upstream": P2,
             "dependent": T, "profile": "structured-item/1", "context_generation": generation,
             "examined_paths": {path: "resolved" for path in paths},
             "required_paths": paths, "eligible_consumers": [X],
             "new_dependent": T, "retirement_safe": False,
             "review_evidence": "review-1", "reviewer": "owner-b-reviewer",
             "coordinator": "owner-b-coordinator", "outward_equal": True,
             "satisfies_new_inputs": True, "reuse_allowed": True}
    value.update(changes)
    return value


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True,
                          capture_output=True, text=True).stdout.strip()


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q", "--initial-branch=taskfixture")
        git(self.root, "config", "user.email", "test@example.com")
        git(self.root, "config", "user.name", "Test")
        owner_items = {
            "a": [(S, "s", {"id": "s", "inputs": []}),
                  (P, "p", {"id": "p", "inputs": [{"reference": S, "role": "requirement"}]})],
            "b": [(T, "t", {"id": "t", "inputs": [{"reference": P, "role": "plan"},
                                                           {"reference": Q, "role": "shared-policy"}]}),
                  (X, "x", {"id": "x", "inputs": [{"reference": T, "role": "task"}]}),
                  (Y, "y", {"id": "y", "inputs": [{"reference": T, "role": "task"}]})],
            "c": [(Q, "q", {"id": "q", "inputs": []}),
                  (U, "u", {"id": "u", "inputs": [{"reference": Q, "role": "requirement"}]}),
                  (V, "v", {"id": "v", "active": False, "inputs": []}),
                  (W, "w", {"id": "w", "inputs": [{"reference": V, "role": "test-target"}]})],
        }
        for owner, values in owner_items.items():
            path = self.root / "work" / owner / "items.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"items": [payload for _ref, _id, payload in values]}, separators=(",", ":")) + "\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "source items")
        self.source_sha = git(self.root, "rev-parse", "HEAD")
        git(self.root, "branch", "develop")
        git(self.root, "branch", "main")
        a_path = self.root / "work/a/items.json"
        a_doc = json.loads(a_path.read_text())
        next(item for item in a_doc["items"] if item["id"] == "p")["version"] = 2
        a_path.write_text(json.dumps(a_doc, separators=(",", ":")) + "\n")
        git(self.root, "add", "work/a/items.json")
        git(self.root, "commit", "-qm", "candidate P revision")
        self.candidate_sha = git(self.root, "rev-parse", "HEAD")
        b_path = self.root / "work/b/items.json"
        b_doc = json.loads(b_path.read_text())
        next(item for item in b_doc["items"] if item["id"] == "t").update({
            "version": 2, "inputs": [{"reference": P2, "role": "plan"},
                                        {"reference": Q, "role": "shared-policy"}]})
        b_path.write_text(json.dumps(b_doc, separators=(",", ":")) + "\n")
        git(self.root, "add", "work/b/items.json")
        git(self.root, "commit", "-qm", "candidate T revision")
        self.candidate_b_sha = git(self.root, "rev-parse", "HEAD")
        catalog_items = dict(owner_items)
        catalog_items["a"] = [*owner_items["a"], (P2, "p", {"id": "p", "version": 2,
            "inputs": [{"reference": S, "role": "requirement"}]})]
        catalog_items["b"] = [*owner_items["b"], (T2, "t", {"id": "t", "version": 2,
            "inputs": [{"reference": P2, "role": "plan"}, {"reference": Q, "role": "shared-policy"}]})]
        for owner, values in catalog_items.items():
            entries, snapshots = [], {}
            source_path = f"work/{owner}/items.json"
            for index, (reference, item_id, _payload) in enumerate(values):
                source_sha = (self.candidate_sha if owner == "a" and reference == P2 else
                              self.candidate_b_sha if owner == "b" and reference == T2 else self.source_sha)
                raw = subprocess.run(["git", "show", f"{source_sha}:{source_path}"], cwd=self.root,
                    check=True, capture_output=True).stdout
                snapshot_id = f"{owner}-{index}"
                snapshots[snapshot_id] = {"commit": source_sha, "path": source_path}
                entries.append({"reference": reference, "logical_id": reference.rsplit("@", 1)[0],
                    "revision": int(reference.rsplit("@", 1)[1]), "snapshot_id": snapshot_id,
                    "item_id": item_id, "profile": "structured-item/1", "digest_algorithm": "sha256",
                    "digests": payload_digests(raw), "digest_semantics": sorted(payload_digests(raw)),
                    "generation": index + 1})
            catalog = {"schema": "ask-reference-catalog/v1", "owner": owner, "generation": 1,
                       "entries": entries, "snapshots": snapshots}
            catalog_path = self.root / "work" / owner / "references" / "integrity.json"
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            catalog_path.write_text(json.dumps(catalog, separators=(",", ":")) + "\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "registered catalogs")
        self.catalog_sha = git(self.root, "rev-parse", "HEAD")
        for owner in owner_items:
            live_sha = self.candidate_sha if owner == "a" else self.candidate_b_sha if owner == "b" else self.source_sha
            git(self.root, "update-ref", f"refs/heads/agent/{owner}", live_sha)
            git(self.root, "update-ref", f"refs/ask/references/{owner}", self.catalog_sha)
        self.capture = capture_project(self.root)
        self.loaded_graph = load_project_graph(self.root, self.capture)
        self.assertEqual(self.loaded_graph["status"], "complete", self.loaded_graph)

    def tearDown(self):
        self.temp.cleanup()

    def project_graph(self):
        return deepcopy(self.loaded_graph)

    def commit_owner_candidate(self, owner, update):
        source = self.root / "work" / owner / "items.json"
        if update is None:
            source.unlink()
            git(self.root, "add", "-u", source.relative_to(self.root).as_posix())
        else:
            document = json.loads(source.read_text())
            source.write_text(json.dumps(update(document), separators=(",", ":")) + "\n")
            git(self.root, "add", source.relative_to(self.root).as_posix())
        git(self.root, "commit", "-qm", f"candidate {owner}")
        candidate = git(self.root, "rev-parse", "HEAD")
        git(self.root, "update-ref", f"refs/heads/agent/{owner}", candidate)
        self.capture = capture_project(self.root)
        self.loaded_graph = load_project_graph(self.root, self.capture)

    def test_direct_and_potential_impact(self):
        result = assess_impact(self.project_graph(), [S], capture=self.capture, repository_root=self.root)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(set(result["items"]), {P, P2, T, T2, X, Y})
        self.assertNotIn(U, result["items"])
        self.assertEqual(result["items"][P]["status"], "incomplete")
        self.assertTrue(any(edge["role"] == "shared-policy" for edge in result["items"][T]["inputs"]))
        converged = assess_impact(self.project_graph(), [S, Q], capture=self.capture,
                                  repository_root=self.root)
        self.assertEqual(len(converged["items"][T]["paths"]), 2)
        self.assertEqual(len(converged["items"][X]["paths"]), 2)
        self.assertEqual(len(converged["items"][Y]["paths"]), 2)

    def test_reviewed_stop_old_pin_or_new_revision(self):
        capture = self.capture
        current = decision(generation=capture["generation"])
        result = record_decision(current, capture, required_paths=current["required_paths"],
                                 authority_check=lambda _decision, _capture: True)
        self.assertTrue(result["propagation_stopped"])
        self.assertEqual(result["status"], "retained")
        changed = decision(generation=capture["generation"], examined_paths={f"{P}|plan": "resolved", f"{Q}|shared-policy": "changed"})
        self.assertFalse(record_decision(changed, capture, required_paths=decision()["required_paths"],
            authority_check=lambda _decision, _capture: True)["propagation_stopped"])
        stale = decision(generation="g0")
        with self.assertRaises(Exception):
            record_decision(stale, capture, required_paths=stale["required_paths"],
                            authority_check=lambda _decision, _capture: True)
        impact = assess_impact(self.project_graph(), [P], {T: current}, capture=capture,
            repository_root=self.root, authority_check=lambda _decision, _capture: True)
        self.assertNotIn(X, impact["items"])
        self.assertIn(Y, impact["items"])
        unauthorised = assess_impact(self.project_graph(), [P], {T: current}, capture=capture,
                                     repository_root=self.root)
        self.assertIn(X, unauthorised["items"])
        omitted = decision(generation=capture["generation"],
                           required_paths=[f"{P}|plan"], examined_paths={f"{P}|plan": "resolved"})
        self.assertIn(X, assess_impact(self.project_graph(), [P], {T: omitted}, capture=capture,
            repository_root=self.root, authority_check=lambda _decision, _capture: True)["items"])
        unrelated = decision(generation=capture["generation"], new_upstream="z/spec/99@99")
        self.assertIn(X, assess_impact(self.project_graph(), [P], {T: unrelated}, capture=capture,
            repository_root=self.root, authority_check=lambda _decision, _capture: True)["items"])
        current = decision(action="revise", generation=self.capture["generation"],
                           new_dependent=T2, eligible_consumers=[])
        paths = [f"{P}|plan", f"{P2}|plan", f"{Q}|shared-policy"]
        current.update(required_paths=paths, examined_paths={path: "resolved" for path in paths})
        result = assess_impact(self.project_graph(), [P], {T: current}, capture=self.capture,
            repository_root=self.root, authority_check=lambda _decision, _capture: True)
        self.assertEqual(result["items"][T]["status"], "revised")
        self.assertIn(X, result["items"])

        # A candidate-only binding is traversed while its historical pin stays intact.
        source = self.root / "work/a/items.json"
        document = json.loads(source.read_text())
        next(item for item in document["items"] if item["id"] == "p")["inputs"] = [
            {"reference": Q, "role": "requirement"}]
        source.write_text(json.dumps(document, separators=(",", ":")) + "\n")
        git(self.root, "add", "work/a/items.json")
        git(self.root, "commit", "-qm", "candidate changes P2 input")
        candidate = git(self.root, "rev-parse", "HEAD")
        git(self.root, "update-ref", "refs/heads/agent/a", candidate)
        self.capture = capture_project(self.root)
        self.loaded_graph = load_project_graph(self.root, self.capture)
        self.assertEqual(self.loaded_graph["nodes"][P2]["inputs"][0]["reference"], S)
        candidate_impact = assess_impact(self.project_graph(), [Q], capture=self.capture,
                                         repository_root=self.root)
        self.assertEqual(candidate_impact["status"], "incomplete")
        self.assertIn(P2, candidate_impact["items"])
        self.assertTrue(candidate_impact["unregistered_candidates"])

    def test_retirement_preserves_shared_obligations(self):
        graph_value = self.project_graph()
        self.assertFalse(graph_value["nodes"][V]["active"])
        self.assertTrue(graph_value["nodes"][W]["active"])
        retired_pin = assess_impact(graph_value, [V], capture=self.capture, repository_root=self.root)
        self.assertEqual(retired_pin["status"], "incomplete")
        self.assertIn(W, retired_pin["items"])
        retirement = {"action": "retire", "old_upstream": Q, "new_upstream": Q,
            "dependent": U, "new_dependent": None, "profile": "structured-item/1",
            "context_generation": self.capture["generation"], "examined_paths": {f"{Q}|requirement": "resolved"},
            "required_paths": [f"{Q}|requirement"], "eligible_consumers": [],
            "review_evidence": "review-u", "reviewer": "owner-c-reviewer",
            "coordinator": "owner-c-coordinator", "outward_equal": False,
            "satisfies_new_inputs": False, "reuse_allowed": False, "retirement_safe": True}
        result = assess_impact(graph_value, [Q], {U: retirement}, capture=self.capture,
            repository_root=self.root, authority_check=lambda _decision, _capture: True)
        self.assertEqual(result["items"][U]["status"], "retired")
        self.assertIn(T, result["items"])
        self.assertIn(X, result["items"])
        self.assertEqual(graph_value["nodes"][T]["inputs"][1]["reference"], Q)

    def test_attributed_multiple_input_revalidation(self):
        capture = self.capture
        incomplete = decision(generation=capture["generation"],
            examined_paths={f"{P}|plan": "resolved", f"{Q}|shared-policy": "unknown"})
        self.assertEqual(assess_impact(self.project_graph(), [P], {T: incomplete},
            capture=capture, repository_root=self.root)["status"], "incomplete")
        missing_authority = decision(coordinator="")
        with self.assertRaises(Exception):
            record_decision(missing_authority)
        malformed = decision(generation=capture["generation"], required_paths=[[]])
        with self.assertRaises(Exception):
            record_decision(malformed, capture, required_paths=[[]],
                            authority_check=lambda _decision, _capture: True)

    def test_deletion_vs_unavailability_and_history(self):
        self.commit_owner_candidate("a", lambda value: {"items": [item for item in value["items"] if item["id"] != "s"]})
        self.assertEqual(self.loaded_graph["status"], "complete", self.loaded_graph)
        self.assertIn(S, self.loaded_graph["deletions"])
        result = assess_impact(self.project_graph(), [S], capture=self.capture, repository_root=self.root)
        self.assertEqual(result["status"], "incomplete")
        self.assertTrue(result["items"][P]["inputs"][0]["deleted"])
        self.assertIn(S, self.loaded_graph["nodes"])
        self.commit_owner_candidate("b", None)
        self.assertEqual(self.loaded_graph["status"], "incomplete")
        result = assess_impact(self.project_graph(), [P], capture=self.capture, repository_root=self.root)
        self.assertEqual(result["status"], "incomplete")

        # A catalog pin to a lost Git object is unavailable, not an ordinary deletion.
        catalog_path = self.root / "work/b/references/integrity.json"
        catalog = json.loads(catalog_path.read_text())
        snapshot_id = catalog["entries"][0]["snapshot_id"]
        catalog["snapshots"][snapshot_id]["commit"] = "f" * 40
        catalog_path.write_text(json.dumps(catalog, separators=(",", ":")) + "\n")
        git(self.root, "add", "work/b/references/integrity.json")
        git(self.root, "commit", "-qm", "authority names unavailable source object")
        git(self.root, "update-ref", "refs/ask/references/b", git(self.root, "rev-parse", "HEAD"))
        try:
            unavailable_object = load_project_graph(self.root, capture_project(self.root))
        except Exception as exc:
            unavailable_object = {"status": "error", "detail": str(exc)}
        self.assertEqual(unavailable_object["status"], "incomplete", unavailable_object)
        self.assertTrue(any(entry["reason"] == "discovery_incomplete"
                            for entry in unavailable_object.get("unresolved", [])))
