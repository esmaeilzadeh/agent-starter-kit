from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys
import shutil

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from workflow_refs.store import initialize_catalog, register_revision


class ReferenceCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="refs-cli-")
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.test"], cwd=self.root, check=True)
        self.source = self.root / "work/demo/source.json"
        self.source.parent.mkdir(parents=True)
        self.source.write_text(json.dumps({"items": [{"id": "task-two", "value": 7, "inputs": []}]}))
        subprocess.run(["git", "add", "work/demo/source.json"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture source"], cwd=self.root, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        catalog = self.root / "work/demo/references/integrity.json"
        catalog.parent.mkdir(parents=True)
        initialize_catalog(catalog, "demo")
        register_revision(catalog, "demo", "demo/spec/1/plan/1/task/2",
                          {"commit": self.commit, "path": "work/demo/source.json"},
                          "task-two", "structured-item/1", self.source.read_bytes())

    def tearDown(self):
        self.temp.cleanup()

    def test_public_numeric_show_and_scoped_errors(self):
        from workflow_refs.cli import main
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["show", "demo/spec/1/plan/1/task/2@1"], root=self.root)
        value = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(value["revision"], 1)
        self.assertEqual(value["parents"], {"spec": 1, "plan": 1})
        self.assertNotIn("integrity", value)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["show", "demo/spec/1/plan/1/task/2@1", "--integrity"], root=self.root)
        detailed = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertIn("digests", detailed["integrity"])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["show", "demo/spec/1/plan/1/task/2@2"], root=self.root)
        missing = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(missing["reason"], "missing")

    def test_record_run_numeric_provenance(self):
        repo = self.root / "run-fixture"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.test"], cwd=repo, check=True)
        kit_root = Path(__file__).resolve().parents[2]
        (repo / "_ask/scripts").mkdir(parents=True)
        shutil.copy(kit_root / "_ask/scripts/check-clean-worktree.sh", repo / "_ask/scripts/")
        shutil.copy(kit_root / "_ask/scripts/record-run.sh", repo / "_ask/scripts/")
        package = repo / ".agents/ask/workflow_refs"
        package.mkdir(parents=True)
        for module in (kit_root / ".agents/ask/workflow_refs").glob("*.py"):
            shutil.copy(module, package / module.name)
        (repo / "results/demo").mkdir(parents=True)
        (repo / "results/demo/config.yaml").write_text("lr: 0.1\n")
        subprocess.run(["git", "add", "_ask", ".agents", "results/demo/config.yaml"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "record-run fixture"], cwd=repo, check=True)
        source_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        command = ["bash", "_ask/scripts/record-run.sh", "--run-id", "demo",
                   "--commit-sha", source_sha, "--metric", "0.91", "--notes", "kept"]
        subprocess.run(command, cwd=repo, check=True, capture_output=True, text=True)
        manifest = json.loads((repo / "results/demo/run_manifest.json").read_text())
        summary = json.loads((repo / "results/demo/summary.json").read_text())
        integrity = json.loads((repo / "results/references/integrity.json").read_text())
        self.assertEqual(manifest["schema"], "eval-run-meta/v2")
        self.assertEqual(manifest["run_reference"], "repository-runs/run/1@1")
        self.assertEqual(manifest["notes"], "kept")
        self.assertNotIn(source_sha, json.dumps(manifest))
        self.assertEqual(summary["metric"], "0.91")
        self.assertEqual(integrity["source_bindings"][manifest["run_reference"]]["commit"], source_sha)

        dirty = subprocess.run(["bash", "_ask/scripts/record-run.sh", "--run-id", "dirty",
                                "--commit-sha", source_sha, "--metric", "0.2"], cwd=repo,
                               capture_output=True, text=True)
        self.assertNotEqual(dirty.returncode, 0)
        self.assertIn("dirty", dirty.stderr.lower())
        subprocess.run(["git", "add", "results"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "persist recorded run"], cwd=repo, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        wrong = subprocess.run(["bash", "_ask/scripts/record-run.sh", "--run-id", "wrong",
                                "--commit-sha", "deadbeef", "--metric", "0.1"], cwd=repo,
                               capture_output=True, text=True)
        missing_config = subprocess.run(["bash", "_ask/scripts/record-run.sh", "--run-id", "absent",
                                         "--commit-sha", head, "--metric", "0.1"], cwd=repo,
                                        capture_output=True, text=True)
        missing_sha = subprocess.run(["bash", "_ask/scripts/record-run.sh", "--run-id", "absent",
                                      "--metric", "0.1"], cwd=repo, capture_output=True, text=True)
        self.assertNotEqual(wrong.returncode, 0)
        self.assertNotEqual(missing_config.returncode, 0)
        self.assertNotEqual(missing_sha.returncode, 0)

    def test_start_work_cooperating_inventory_publication(self):
        repo = self.root / "start-fixture"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.test"], cwd=repo, check=True)
        kit_root = Path(__file__).resolve().parents[2]
        (repo / "_ask/scripts").mkdir(parents=True)
        shutil.copy(kit_root / "_ask/scripts/check-clean-worktree.sh", repo / "_ask/scripts/")
        shutil.copy(kit_root / "_ask/scripts/access-check.sh", repo / "_ask/scripts/")
        shutil.copy(kit_root / "_ask/scripts/start-work.sh", repo / "_ask/scripts/")
        shutil.copytree(kit_root / "_ask/templates", repo / "_ask/templates")
        subprocess.run(["git", "add", "_ask"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture kit"], cwd=repo, check=True)
        subprocess.run(["git", "branch", "develop"], cwd=repo, check=True)
        subprocess.run(["bash", "_ask/scripts/start-work.sh", "fresh-owner"], cwd=repo,
                       check=True, capture_output=True, text=True)
        from workflow_refs.project import capture_project
        capture = capture_project(repo)
        self.assertEqual(capture["status"], "complete")
        self.assertIn("fresh-owner", capture["owners"])
        self.assertFalse((repo / "work/fresh-owner/explore-map.md").exists())
        common = Path(subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=repo,
                                              text=True).strip())
        if not common.is_absolute():
            common = repo / common
        self.assertTrue((common / "ask-locks/references.lock").is_file())
