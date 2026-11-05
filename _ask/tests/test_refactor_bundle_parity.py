"""Public install, upgrade, and generated prompt contracts for task lifecycle."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class BundleTests(unittest.TestCase):
    def test_install_and_sync_ship_task_loop_to_all_runtimes(self):
        with tempfile.TemporaryDirectory() as temp:
            consumer = Path(temp) / "consumer"
            self.init_repo(consumer)
            self.install_from(ROOT, consumer)
            self.assertIn("Review and Refactor happen inside each task", (consumer / "_ask/guide/02-workflow.md").read_text())
            self.assertTrue((consumer / ".agents/ask/task-loop.md").is_file())
            for stage in ("06-implement", "07-review", "08-refactor"):
                source = (consumer / f".agents/ask/stages/{stage}.md").read_text()
                self.assertIn(".agents/ask/task-loop.md", source)
                self.assertIn(source.strip(), (consumer / f".cursor/skills/kit-{stage}/SKILL.md").read_text())
                self.assertIn(f".agents/ask/stages/{stage}.md", (consumer / f".cursor/agents/kit-{stage}.md").read_text())
                self.assertIn(f".agents/ask/stages/{stage}.md", (consumer / f".claude/agents/kit-{stage}.md").read_text())
                self.assertIn(f".agents/ask/stages/{stage}.md", (consumer / f".codex/agents/kit-{stage}.toml").read_text())
                self.assertIn(f".agents/ask/stages/{stage}.md", (consumer / f".opencode/agents/kit-{stage}.md").read_text())
            self.run_cmd([str(consumer / "ask"), "sync"], cwd=consumer)

    def test_upgrade_preserves_consumer_overlays_and_task_loop(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            consumer = root / "consumer"
            self.init_repo(consumer)
            old_kit = root / "old-kit"
            self.run_cmd(["git", "clone", "--quiet", str(ROOT), str(old_kit)])
            self.run_cmd(["git", "-C", str(old_kit), "checkout", "--quiet", "a2ad10ee607e2c750c770aaf5afed0ec9059e16a"])
            self.install_from(old_kit, consumer)
            overlay = consumer / ".agents/ask.local/stages/06-implement.md"
            overlay.parent.mkdir(parents=True, exist_ok=True)
            overlay.write_text("Consumer implementation note.\n")
            manifest = consumer / "_ask/skills/manifest.yaml"
            manifest.write_text("skills:\n  custom:\n    source: example/custom\n    revision: abc123\n    skill: custom\n    role: helper\n    required: false\n")
            self.run_cmd(["git", "-C", str(consumer), "add", "."])
            self.run_cmd(["git", "-C", str(consumer), "commit", "-qm", "consumer setup"])

            candidate = self.run_cmd(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
            self.run_cmd([str(consumer / "ask"), "upgrade", "--version", candidate,
                      "--source", str(ROOT), "--target", str(consumer), "--skip-prepare"], cwd=consumer)

            self.assertTrue((consumer / ".agents/ask/task-loop.md").is_file())
            self.assertIn("Review and Refactor happen inside each task", (consumer / "_ask/guide/02-workflow.md").read_text())
            self.assertIn("Consumer implementation note", (consumer / ".cursor/skills/kit-06-implement/SKILL.md").read_text())
            self.assertIn("example/custom", manifest.read_text())

    def test_choice_and_stop_contracts_project_to_runtimes(self):
        with tempfile.TemporaryDirectory() as temp:
            consumer = Path(temp) / "consumer"
            self.init_repo(consumer)
            self.install_from(ROOT, consumer)
            grill = (consumer / ".agents/ask/stages/01-grill.md").read_text()
            implement = (consumer / ".agents/ask/stages/06-implement.md").read_text()
            self.assertIn("optional free-text field that can accompany a selected option", grill)
            self.assertIn("explicitly stops before implementation", implement)
            self.assertIn(".agents/ask/task-loop.md", implement)
            for stage in ("01-grill", "06-implement"):
                canonical = (consumer / f".agents/ask/stages/{stage}.md").read_text()
                for runtime, suffix in (("cursor", ".md"), ("claude", ".md"), ("codex", ".toml"), ("opencode", ".md")):
                    generated = (consumer / f".{runtime}/agents/kit-{stage}{suffix}").read_text()
                    self.assertIn(f".agents/ask/stages/{stage}.md", generated)
                cursor_projection = (consumer / f".cursor/skills/kit-{stage}/SKILL.md").read_text()
                self.assertIn(canonical.strip(), cursor_projection)

    def init_repo(self, path):
        path.mkdir(parents=True, exist_ok=True)
        self.run_cmd(["git", "init", "-q", str(path)])
        self.run_cmd(["git", "-C", str(path), "config", "user.email", "bundle@example.test"])
        self.run_cmd(["git", "-C", str(path), "config", "user.name", "Bundle Test"])
        (path / "README.md").write_text("consumer\n")
        self.run_cmd(["git", "-C", str(path), "add", "README.md"])
        self.run_cmd(["git", "-C", str(path), "commit", "-qm", "initialize consumer"])

    def install_from(self, kit, consumer):
        env = dict(os.environ, SKIP_INSTALL="1")
        self.run_cmd([str(kit / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(consumer)], env=env)

    def run_cmd(self, command, *, cwd=None, env=None):
        return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=True)


if __name__ == "__main__":
    unittest.main()
