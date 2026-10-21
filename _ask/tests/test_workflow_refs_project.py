from __future__ import annotations

import subprocess
import json
import tempfile
import unittest
from pathlib import Path

from workflow_refs.project import capture_project, load_project_graph, validate_capture
from workflow_refs.impact import ImpactError, _graph
from workflow_refs.store import payload_digests


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "test@example.com")
        git(self.root, "config", "user.name", "Test")
        (self.root / "work" / "archived").mkdir(parents=True)
        (self.root / "work" / "archived" / "spec.json").write_text('{"items":[{"id":"archive-item","inputs":[]}]}\n')
        (self.root / "work" / "live").mkdir(parents=True)
        (self.root / "specs").mkdir()
        (self.root / "work" / "live" / "spec.json").write_text(
            '{"items":[{"id":"live-item","inputs":[{"reference":"shared/spec/1@1","role":"constraint"}]}]}\n')
        (self.root / "specs" / "shared.json").write_text(
            '{"items":[{"id":"shared-item","inputs":[]}]}\n')
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "initial")
        self.sha = git(self.root, "rev-parse", "HEAD")
        git(self.root, "branch", "develop")
        git(self.root, "branch", "main")
        def catalog(owner, ref, path, item_id):
            raw = (self.root / path).read_bytes()
            entry = {"reference": ref, "logical_id": ref.rsplit("@", 1)[0], "revision": 1,
                     "snapshot_id": owner + "-snapshot", "item_id": item_id,
                     "profile": "structured-item/1", "digest_algorithm": "sha256",
                     "digests": payload_digests(raw), "digest_semantics": sorted(payload_digests(raw)),
                     "generation": 1}
            value = {"schema": "ask-reference-catalog/v1", "owner": owner, "generation": 1,
                     "entries": [entry], "snapshots": {owner + "-snapshot": {"commit": self.sha, "path": path}}}
            target = self.root / "work" / owner / "references" / "integrity.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(value, separators=(",", ":")) + "\n")
        catalog("live", "live/spec/1@1", "work/live/spec.json", "live-item")
        catalog("shared", "shared/spec/1@1", "specs/shared.json", "shared-item")
        catalog("archived", "archived/spec/1@1", "work/archived/spec.json", "archive-item")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "catalog authority")
        self.catalog_commit = git(self.root, "rev-parse", "HEAD")
        git(self.root, "update-ref", "refs/heads/agent/live", self.sha)
        git(self.root, "update-ref", "refs/heads/agent/orphan/task/4", self.sha)
        git(self.root, "update-ref", "refs/ask/references/shared", self.catalog_commit)
        git(self.root, "update-ref", "refs/ask/references/live", self.catalog_commit)
        git(self.root, "update-ref", "refs/ask/references/archived", self.catalog_commit)
        (self.root / "work" / "archived" / "unrelated.txt").write_text("new commit\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "second")
        self.other = git(self.root, "rev-parse", "HEAD")

    def tearDown(self):
        self.temp.cleanup()

    def test_authoritative_inventory_and_cycles(self):
        capture = capture_project(self.root, shared_owners={"shared"})
        self.assertEqual(capture["status"], "complete")
        self.assertEqual(capture["owners"]["live"]["kind"], "live")
        self.assertIn("refs/ask/references/live", capture["owners"]["live"]["refs"])
        self.assertEqual(capture["owners"]["shared"]["kind"], "shared")
        self.assertEqual(capture["owners"]["archived"]["kind"], "archive")
        self.assertIn("refs/ask/references/archived", capture["owners"]["archived"]["refs"])
        self.assertNotIn("refs/heads/agent/orphan/task/4", capture["refs"])
        node_a = "live/spec/1@1"
        node_b = "other/spec/1@1"
        with self.assertRaises(ImpactError):
            _graph({"nodes": {node_a: {"inputs": [{"reference": node_b, "role": "uses"}]}}})
        with self.assertRaises(ImpactError):
            _graph({"nodes": {node_a: {"inputs": [{"reference": node_b, "role": "uses"}]},
                              node_b: {"inputs": [{"reference": node_a, "role": "uses"}]}}})
        self.assertEqual(validate_capture(self.root, capture)["status"], "complete")
        graph = load_project_graph(self.root, capture)
        self.assertEqual(graph["status"], "complete", graph)
        self.assertEqual(graph["nodes"]["live/spec/1@1"]["inputs"],
                         [{"reference": "shared/spec/1@1", "role": "constraint"}])
        # Candidate-only bindings are visible without rewriting the committed pin.
        live_path = self.root / "work/live/spec.json"
        live_doc = json.loads(live_path.read_text())
        live_doc["items"][0]["inputs"] = [{"reference": "archived/spec/1@1", "role": "constraint"}]
        live_path.write_text(json.dumps(live_doc, separators=(",", ":")) + "\n")
        git(self.root, "add", "work/live/spec.json")
        git(self.root, "commit", "-qm", "candidate changes dependency")
        git(self.root, "update-ref", "refs/heads/agent/live", git(self.root, "rev-parse", "HEAD"))
        capture = capture_project(self.root, shared_owners={"shared"})
        graph = load_project_graph(self.root, capture)
        self.assertEqual(graph["nodes"]["live/spec/1@1"]["inputs"][0]["reference"], "shared/spec/1@1")
        self.assertEqual(graph.get("candidate_inputs", {}).get("live/spec/1@1", [{}])[0].get("reference"),
                         "archived/spec/1@1")
        self.assertTrue(graph.get("unregistered_candidates", []))
        from workflow_refs.impact import assess_impact
        impact = assess_impact(graph, ["archived/spec/1@1"], capture=capture, repository_root=self.root)
        self.assertEqual(impact["status"], "incomplete")
        self.assertIn("live/spec/1@1", impact["items"])

        # Restore the old input then verify a missing declaration remains incomplete.
        live_doc["items"][0]["inputs"] = []
        live_path.write_text(json.dumps(live_doc, separators=(",", ":")) + "\n")
        live_doc["items"][0].pop("inputs")
        live_path.write_text(json.dumps(live_doc, separators=(",", ":")) + "\n")
        git(self.root, "add", "work/live/spec.json")
        git(self.root, "commit", "-qm", "remove dependency declaration")
        git(self.root, "update-ref", "refs/heads/agent/live", git(self.root, "rev-parse", "HEAD"))
        changed_capture = capture_project(self.root, shared_owners={"shared"})
        self.assertEqual(load_project_graph(self.root, changed_capture)["status"], "incomplete")

        # A registered snapshot whose Git commit was lost is unavailable, not an exception.
        authority_path = self.root / "work/live/references/integrity.json"
        authority = json.loads(authority_path.read_text())
        authority["snapshots"]["live-snapshot"]["commit"] = "f" * 40
        authority_path.write_text(json.dumps(authority, separators=(",", ":")) + "\n")
        git(self.root, "add", "work/live/references/integrity.json")
        git(self.root, "commit", "-qm", "authority names unavailable source")
        git(self.root, "update-ref", "refs/ask/references/live", git(self.root, "rev-parse", "HEAD"))
        try:
            unavailable = load_project_graph(self.root, capture_project(self.root, shared_owners={"shared"}))
        except Exception as exc:
            unavailable = {"status": "error", "detail": str(exc)}
        self.assertEqual(unavailable["status"], "incomplete")
        self.assertTrue(any(entry["reason"] == "discovery_incomplete"
                            for entry in unavailable["unresolved"]))

    def test_coherent_capture_new_owner_and_aba(self):
        calls = []
        def shared_owner_aba(attempt, before):
            git(self.root, "update-ref", "refs/ask/references/transient", self.sha)
            git(self.root, "update-ref", "-d", "refs/ask/references/transient")
        transient = capture_project(self.root, retries=1, during_scan=shared_owner_aba,
                                    shared_owners={"shared"})
        self.assertEqual(transient["status"], "incomplete")
        git(self.root, "config", "core.logAllRefUpdates", "false")
        git(self.root, "update-ref", "refs/heads/develop", self.sha)
        common = Path(git(self.root, "rev-parse", "--git-common-dir"))
        if not common.is_absolute():
            common = (self.root / common).resolve()
        develop_log = common / "logs/refs/heads/develop"
        develop_log.unlink(missing_ok=True)
        def develop_move_and_return(attempt, before):
            git(self.root, "update-ref", "refs/heads/develop", self.other)
            git(self.root, "update-ref", "refs/heads/develop", self.sha)
        self.assertEqual(capture_project(self.root, retries=1, during_scan=develop_move_and_return,
                                         shared_owners={"shared"})["status"], "incomplete")
        def move_and_return(attempt, before):
            if calls:
                return
            calls.append(True)
            git(self.root, "update-ref", "--create-reflog", "refs/heads/agent/live", self.other)
            git(self.root, "update-ref", "refs/heads/agent/live", self.sha)
        capture = capture_project(self.root, retries=1, during_scan=move_and_return,
                                  shared_owners={"shared"})
        self.assertEqual(capture["status"], "incomplete")
        capture = capture_project(self.root, shared_owners={"shared"})
        self.assertEqual(capture["status"], "complete")
        git(self.root, "update-ref", "refs/heads/agent/live", self.other)
        git(self.root, "update-ref", "refs/heads/agent/live", self.sha)
        self.assertEqual(validate_capture(self.root, capture)["reason"], "stale_inventory")
        capture = capture_project(self.root, shared_owners={"shared"})
        git(self.root, "update-ref", "refs/ask/references/transient", self.sha)
        git(self.root, "update-ref", "-d", "refs/ask/references/transient")
        self.assertEqual(validate_capture(self.root, capture)["reason"], "stale_inventory")
        capture = capture_project(self.root, shared_owners={"shared"})
        git(self.root, "update-ref", "refs/heads/agent/new-owner", self.sha)
        self.assertEqual(validate_capture(self.root, capture)["reason"], "stale_inventory")
