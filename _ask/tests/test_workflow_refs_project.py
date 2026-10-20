from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from workflow_refs.project import capture_project, validate_capture
from workflow_refs.impact import ImpactError, _graph


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
        (self.root / "work" / "archived" / "spec.json").write_text("{}\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "initial")
        self.sha = git(self.root, "rev-parse", "HEAD")
        git(self.root, "branch", "develop")
        git(self.root, "branch", "main")
        (self.root / "work" / "archived" / "spec.json").write_text("{\"updated\":true}\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "second")
        self.other = git(self.root, "rev-parse", "HEAD")
        git(self.root, "update-ref", "refs/heads/agent/live", self.sha)
        git(self.root, "update-ref", "refs/heads/agent/orphan/task/4", self.sha)
        git(self.root, "update-ref", "refs/ask/references/shared", self.sha)

    def tearDown(self):
        self.temp.cleanup()

    def test_authoritative_inventory_and_cycles(self):
        capture = capture_project(self.root)
        self.assertEqual(capture["status"], "complete")
        self.assertEqual(capture["owners"]["live"]["kind"], "live")
        self.assertEqual(capture["owners"]["shared"]["kind"], "shared")
        self.assertEqual(capture["owners"]["archived"]["kind"], "archive")
        self.assertNotIn("refs/heads/agent/orphan/task/4", capture["refs"])
        node_a = "live/spec/1@1"
        node_b = "other/spec/1@1"
        with self.assertRaises(ImpactError):
            _graph({"nodes": {node_a: {"inputs": [{"reference": node_b, "role": "uses"}]}}})
        with self.assertRaises(ImpactError):
            _graph({"nodes": {node_a: {"inputs": [{"reference": node_b, "role": "uses"}]},
                              node_b: {"inputs": [{"reference": node_a, "role": "uses"}]}}})
        self.assertEqual(validate_capture(self.root, capture)["status"], "complete")

    def test_coherent_capture_new_owner_and_aba(self):
        calls = []
        def move_and_return(attempt, before):
            if calls:
                return
            calls.append(True)
            git(self.root, "update-ref", "--create-reflog", "refs/heads/agent/live", self.other)
            git(self.root, "update-ref", "refs/heads/agent/live", self.sha)
        capture = capture_project(self.root, retries=1, during_scan=move_and_return)
        self.assertEqual(capture["status"], "incomplete")
        capture = capture_project(self.root)
        self.assertEqual(capture["status"], "complete")
        git(self.root, "update-ref", "refs/heads/agent/live", self.other)
        git(self.root, "update-ref", "refs/heads/agent/live", self.sha)
        self.assertEqual(validate_capture(self.root, capture)["reason"], "stale_inventory")
        capture = capture_project(self.root)
        git(self.root, "update-ref", "refs/heads/agent/new-owner", self.sha)
        self.assertEqual(validate_capture(self.root, capture)["reason"], "stale_inventory")
