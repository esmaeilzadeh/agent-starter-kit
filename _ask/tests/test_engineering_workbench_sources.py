"""Behavior checks for work inventory and immutable Git source reads."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from engineering_model.workbench_sources import discover_work, read_snapshot


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
