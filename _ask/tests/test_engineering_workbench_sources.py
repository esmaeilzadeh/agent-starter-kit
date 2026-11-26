"""Behavior checks for work inventory and immutable Git source reads."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from engineering_model.workbench_sources import discover_work, read_snapshot
from engineering_model import workbench_sources


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Workbench test")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def test_current_work_and_ref_archive_inventory(self):
        self.write("work/archived/intent.md", "# archived\n")
        self.write("work/no-model/README.md", "present without model\n")
        self.write(".later/parked.md", "# Parked item\n")
        self.commit("archive inventory")
        self.git("checkout", "-b", "agent/current/tasks/WB-002")
        self.write("work/current/engineering-model.json", '{"work_id":"current"}')
        current_commit = self.commit("live task")

        inventory = discover_work(self.root)
        rows = {item["work_id"]: item for item in inventory["workstreams"]}
        self.assertEqual(inventory["current_work_id"], "current")
        self.assertEqual(rows["current"]["life"], "live")
        self.assertEqual(rows["current"]["branch"], "agent/current/tasks/WB-002")
        self.assertEqual(rows["archived"]["life"], "archived")
        self.assertEqual(rows["no-model"]["model_status"], "missing")
        self.assertNotIn("parked", rows, "later cards are not workstreams")
        self.assertEqual([card["slug"] for card in inventory["later"]], ["parked"])

        self.git("checkout", "--detach", current_commit)
        detached = discover_work(self.root)
        self.assertIsNone(detached["current_work_id"])
        self.assertIn("detached", detached["selection_note"])

        with tempfile.TemporaryDirectory() as directory:
            plain = Path(directory)
            (plain / "work/local/engineering-model.json").parent.mkdir(parents=True)
            (plain / "work/local/engineering-model.json").write_text('{"work_id":"local"}', encoding="utf-8")
            gitless = discover_work(plain)
        self.assertFalse(gitless["git_available"])
        self.assertEqual(gitless["workstreams"][0]["work_id"], "local")
        self.assertIn("Git is unavailable", gitless["selection_note"])

        later = self.root / ".later"
        (later / "parked.md").unlink()
        later.rmdir()
        with tempfile.TemporaryDirectory() as directory:
            external = Path(directory)
            (external / "private.md").write_text("# External card\n", encoding="utf-8")
            later.symlink_to(external, target_is_directory=True)
            isolated = discover_work(self.root)
        self.assertEqual(isolated["later"], [],
                         "a symlinked .later root must not expose cards outside the checkout")

    def test_cross_branch_snapshot_is_consistent_and_read_only(self):
        self.write("work/pilot/engineering-model.json", '{"revision":1}')
        self.write("work/pilot/inner-loop/tasks.yaml", "revision: 1\n")
        self.write("work/pilot/test-plan.json", '{"revision":1}')
        self.write("src/check.py", "REVISION = 1\n")
        first = self.commit("first source revision")
        self.git("branch", "snapshot", first)
        selected = read_snapshot(self.root, "snapshot", "pilot", paths=["src/check.py"])
        self.write("work/pilot/engineering-model.json", '{"revision":2}')
        self.write("work/pilot/inner-loop/tasks.yaml", "revision: 2\n")
        self.write("work/pilot/test-plan.json", '{"revision":2}')
        self.write("src/check.py", "REVISION = 2\n")
        self.commit("move current branch")
        before_head = self.git("rev-parse", "HEAD")
        before_refs = self.git("show-ref")
        before_files = {path: (self.root / path).read_bytes() for path in (
            "work/pilot/engineering-model.json", "work/pilot/inner-loop/tasks.yaml",
            "work/pilot/test-plan.json", "src/check.py")}

        self.assertEqual(selected.commit, first)
        self.assertEqual(selected.files.get("work/pilot/engineering-model.json"), b'{"revision":1}')
        self.assertEqual(selected.files["work/pilot/inner-loop/tasks.yaml"], b"revision: 1\n")
        self.assertEqual(selected.files["work/pilot/test-plan.json"], b'{"revision":1}')
        self.assertEqual(selected.files["src/check.py"], b"REVISION = 1\n")
        self.assertFalse(selected.editable)
        self.assertEqual(self.git("rev-parse", "HEAD"), before_head)
        self.assertEqual(self.git("show-ref"), before_refs)
        self.assertEqual({path: (self.root / path).read_bytes() for path in before_files}, before_files)

        self.git("branch", "-f", "snapshot", "HEAD")
        refreshed = read_snapshot(self.root, "snapshot", "pilot", paths=["src/check.py"])
        self.assertNotEqual(refreshed.commit, selected.commit)
        self.assertEqual(selected.files["src/check.py"], b"REVISION = 1\n",
                         "the already captured view remains bound to its original commit")
        self.assertEqual(refreshed.files["src/check.py"], b"REVISION = 2\n")

    def test_inventory_reuses_commit_facts_and_observes_moving_refs(self):
        self.write("README.md", "baseline\n")
        self.commit("baseline")
        self.git("checkout", "-b", "agent/pilot")
        self.write("work/pilot/engineering-model.json", '{"revision":1}')
        self.commit("model")
        with patch.object(workbench_sources, "_git", wraps=workbench_sources._git) as calls:
            first = discover_work(self.root)
            cold_calls = calls.call_count
            calls.reset_mock()
            self.assertEqual(discover_work(self.root), first)
            self.assertLess(calls.call_count, cold_calls)
        (self.root / "work/pilot/engineering-model.json").unlink()
        self.commit("remove model")
        self.assertEqual(discover_work(self.root)["workstreams"][0]["model_status"], "missing")
        self.write("work/pilot/engineering-model.json", '{"revision":2}')
        self.commit("restore model")
        self.assertEqual(discover_work(self.root)["workstreams"][0]["model_status"], "available")
        self.git("checkout", "main")
        self.git("merge", "--ff-only", "agent/pilot")
        self.assertEqual(discover_work(self.root)["workstreams"][0]["life"], "archived")

    def test_standalone_maintenance_is_live_current_and_archived_without_feature_artifacts(self):
        self.write("README.md", "baseline\n")
        self.commit("baseline")
        self.git("checkout", "-b", "maintenance/cleanup")
        self.write("work/cleanup/scope.md", "Preserve behavior while simplifying structure.\n")
        self.write("app.py", "VALUE = 1\n")
        candidate = self.commit("maintenance scope and implementation")
        refs = self.git("show-ref")

        inventory = discover_work(self.root)
        self.assertEqual(inventory["current_work_id"], "cleanup")
        row = next(item for item in inventory["workstreams"] if item["work_id"] == "cleanup")
        self.assertEqual(row["branch"], "maintenance/cleanup")
        self.assertEqual(row["life"], "live")
        self.assertEqual(row["model_status"], "missing")
        status_script = Path(__file__).resolve().parents[1] / "scripts/status.sh"

        def status():
            result = subprocess.run(["bash", str(status_script), "--json", "--work-id", "cleanup"],
                                    cwd=self.root, check=True, capture_output=True, text=True)
            return json.loads(result.stdout)["workstreams"]

        self.assertEqual(status()[0]["warnings"], [])
        self.assertEqual(self.git("rev-parse", "HEAD"), candidate)
        self.assertEqual(self.git("show-ref"), refs)
        self.git("checkout", "main")
        self.git("merge", "--ff-only", "maintenance/cleanup")
        self.assertEqual(status()[0]["life"], "archived")
        archived = discover_work(self.root)
        self.assertEqual(archived["workstreams"][0]["life"], "archived")

    def test_maintenance_with_existing_task_graph_retains_missing_plan_warning(self):
        self.write("README.md", "baseline\n")
        self.commit("baseline")
        self.git("checkout", "-b", "maintenance/governed")
        self.write("work/governed/inner-loop/tasks.yaml", "tasks: []\n")
        self.write("app.py", "VALUE = 1\n")
        self.commit("existing task graph still governs work")
        status_script = Path(__file__).resolve().parents[1] / "scripts/status.sh"
        result = subprocess.run(["bash", str(status_script), "--json", "--work-id", "governed"],
                                cwd=self.root, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)["workstreams"][0]["warnings"], ["code-without-plan"])

    def test_missing_blobs_and_unsafe_paths_are_explained(self):
        self.write("work/pilot/engineering-model.json", '{"revision":1}')
        (self.root / "src").mkdir()
        (self.root / "src/outside-link.py").symlink_to("/etc/passwd")
        self.commit("model without optional blobs")
        selected = read_snapshot(self.root, "HEAD", "pilot",
                                 paths=["src/missing.py", "../outside.py", "src/outside-link.py"])
        self.assertEqual(selected.files.get("work/pilot/engineering-model.json"), b'{"revision":1}')
        diagnostics = {item["path"]: item for item in selected.diagnostics}
        self.assertEqual(diagnostics["src/missing.py"]["code"], "missing-blob")
        self.assertEqual(diagnostics["../outside.py"]["code"], "unsafe-path")
        self.assertEqual(diagnostics["src/outside-link.py"]["code"], "unsafe-entry")
        self.assertNotIn("../outside.py", selected.files)
        self.assertNotIn("src/outside-link.py", selected.files)
        with self.assertRaisesRegex(ValueError, "missing model"):
            read_snapshot(self.root, "HEAD", "absent")


if __name__ == "__main__":
    unittest.main()
