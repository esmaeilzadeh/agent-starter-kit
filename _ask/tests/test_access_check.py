import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AccessCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.git("init", "-q", "-b", "develop")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Access Check Test")
        (self.root / "work").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True)

    def copy_script(self, source, destination):
        target = self.root / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / source, target)
        target.chmod(0o755)
        return target

    def failing_mktemp(self, marker):
        bindir = self.root.parent / (self.root.name + "-bin")
        bindir.mkdir(exist_ok=True)
        self.addCleanup(shutil.rmtree, bindir, ignore_errors=True)
        real_mktemp = shutil.which("mktemp")
        wrapper = bindir / "mktemp"
        wrapper.write_text(
            "#!/bin/sh\ncase \"$1\" in *" + marker + "*) exit 1;; esac\nexec "
            + real_mktemp + " \"$@\"\n", encoding="utf-8")
        wrapper.chmod(0o755)
        return str(bindir) + os.pathsep + os.environ["PATH"]

    def test_writable_paths_pass_and_cleanup(self):
        result = subprocess.run([str(ROOT / "ask"), "access-check"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        probe_files = [*ROOT.glob(".ask-access-check.*"),
                       *ROOT.joinpath(".git").glob(".ask-access-check.*"),
                       *ROOT.joinpath("work").glob(".ask-access-check.*")]
        self.assertEqual(probe_files, [])
        nested = subprocess.run([str(ROOT / "ask"), "access-check"],
                                cwd=ROOT / "_ask/scripts", capture_output=True, text=True)
        self.assertEqual(nested.returncode, 0, nested.stderr)
        clone = self.root / "clone"
        linked = self.root / "linked"
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(clone)], check=True)
        subprocess.run(["git", "-C", str(clone), "worktree", "add", "-q", "-b",
                        "access-check-linked", str(linked), "HEAD"], check=True)
        linked_result = subprocess.run([str(linked / "ask"), "access-check"],
                                       cwd=linked / "_ask/scripts", capture_output=True, text=True)
        self.assertEqual(linked_result.returncode, 0, linked_result.stderr)

    def test_denied_write_and_cleanup_failure_report_paths(self):
        denied = subprocess.run([str(ROOT / "ask"), "access-check"], cwd=ROOT,
                                env=dict(os.environ, PATH=self.failing_mktemp(".git/")),
                                capture_output=True, text=True)
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn(".git", denied.stderr)
        self.assertIn("access", denied.stderr.lower())
        workspace_denied = subprocess.run(
            [str(ROOT / "ask"), "access-check"], cwd=ROOT,
            env=dict(os.environ, PATH=self.failing_mktemp(ROOT.name + "/.ask-access-check.")),
            capture_output=True, text=True)
        self.assertNotEqual(workspace_denied.returncode, 0)
        self.assertIn("workspace", workspace_denied.stderr.lower())
        bindir = self.root / "bin-rm"
        bindir.mkdir()
        real_rm = shutil.which("rm")
        def cleanup_leftovers():
            probes = [*ROOT.glob(".ask-access-check.*"),
                      *ROOT.joinpath(".git").glob(".ask-access-check.*"),
                      *ROOT.joinpath("work").glob(".ask-access-check.*")]
            if real_rm and probes:
                subprocess.run([real_rm, *map(str, probes)], check=False, capture_output=True)
        self.addCleanup(cleanup_leftovers)
        (bindir / "rm").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        (bindir / "rm").chmod(0o755)
        leftover = subprocess.run([str(ROOT / "ask"), "access-check"], cwd=ROOT,
                                   env=dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ["PATH"]),
                                   capture_output=True, text=True)
        self.assertNotEqual(leftover.returncode, 0)
        self.assertIn("leftover", leftover.stderr.lower())
        self.assertIsNotNone(real_rm)

    def test_start_work_refuses_before_mutation(self):
        for source in ("_ask/scripts/start-work.sh", "_ask/scripts/check-clean-worktree.sh"):
            self.copy_script(source, source)
        denied_probe = self.root / "_ask/scripts/access-check.sh"
        denied_probe.parent.mkdir(parents=True, exist_ok=True)
        denied_probe.write_text("#!/bin/sh\necho 'write denied at .git' >&2\nexit 1\n", encoding="utf-8")
        denied_probe.chmod(0o755)
        (self.root / "ask").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (self.root / "ask").chmod(0o755)
        templates = self.root / "_ask/templates"
        templates.mkdir(parents=True)
        for name in ("intent.md", "plan.md", "review.md", "verification.json", "acceptance.md"):
            (templates / name).write_text("template\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        before = self.git("rev-parse", "HEAD").stdout.strip()
        result = subprocess.run(["bash", "_ask/scripts/start-work.sh", "access-denied"],
                                cwd=self.root,
                                env=dict(os.environ, PATH=self.failing_mktemp(".git/")),
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("write denied", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), before)
        self.assertEqual(self.git("branch", "--show-current").stdout.strip(), "develop")
        self.assertFalse((self.root / "work/access-denied").exists())

    def test_runtime_hook_surfaces_failure_as_stop_condition(self):
        hook_source = ROOT / ".cursor/hooks/access-preflight.sh"
        self.assertTrue(hook_source.is_file(), "Cursor session-start hook is missing")
        self.root.joinpath(".cursor/hooks").mkdir(parents=True)
        shutil.copy2(hook_source, self.root / ".cursor/hooks/access-preflight.sh")
        fake_ask = self.root / "ask"
        fake_ask.write_text("#!/bin/sh\necho 'write denied at .git' >&2\nexit 1\n", encoding="utf-8")
        fake_ask.chmod(0o755)
        result = subprocess.run(["bash", ".cursor/hooks/access-preflight.sh"], cwd=self.root,
                                input="{}\n", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("write denied", payload["additional_context"])
        self.assertIn("stop", payload["additional_context"].lower())

    def test_project_instructions_require_check_on_start_and_resume(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()
        self.assertTrue((ROOT / "CLAUDE.md").is_file(), "Claude project instructions are missing")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("access-check", agents)
        self.assertIn("resume", agents)
        self.assertIn("access-check", claude)


if __name__ == "__main__":
    unittest.main()
