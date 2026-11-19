"""Write preflight and recoverable client update transactions."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
import unittest
from pathlib import Path

from client_security_fixtures import ClientFixture, ROOT


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = ClientFixture()

    def tearDown(self) -> None:
        self.fx.close()

    def _install(self, project: Path, *flags: str) -> subprocess.CompletedProcess[str]:
        return self.fx.run([
            "bash", str(ROOT / "_ask/scripts/install-kit.sh"), *flags, str(project),
        ])

    def test_classify_paths(self) -> None:
        project = self.fx.git_project(self.fx.root / "unsafe-tree")
        outside = self.fx.root / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel"
        sentinel.write_text("keep\n", encoding="utf-8")
        (project / ".cursor").symlink_to(outside, target_is_directory=True)

        result = self._install(project, "--skip-prepare", "--force")

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(".cursor", result.stderr + result.stdout)
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ["sentinel"])
        self.assertFalse((project / "_ask/agents/00-explore.md").exists())

    def test_late_conflict_no_writes(self) -> None:
        project = self.fx.git_project(self.fx.root / "late-conflict")
        prior = project / "_ask/agents/00-explore.md"
        prior.parent.mkdir(parents=True)
        prior.write_text("client bytes\n", encoding="utf-8")
        outside = self.fx.root / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel"
        sentinel.write_text("keep\n", encoding="utf-8")
        (project / ".cursor").symlink_to(outside, target_is_directory=True)

        result = self._install(project, "--skip-prepare")

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(".cursor", result.stderr + result.stdout)
        self.assertEqual(prior.read_text(encoding="utf-8"), "client bytes\n")
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ["sentinel"])

    def test_preserve_client_settings(self) -> None:
        project = self.fx.git_project(self.fx.root / "preserve-client")
        settings = project / ".agents/ask.local/stages/01-grill.md"
        settings.parent.mkdir(parents=True)
        settings.write_text("client stage\n", encoding="utf-8")
        manifest = project / "_ask/skills/manifest.yaml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("client manifest\n", encoding="utf-8")
        self.fx.run(["git", "-C", str(project), "add", ".agents/ask.local/stages/01-grill.md"])
        self.fx.run(["git", "-C", str(project), "commit", "-qm", "custom stage"])

        result = self._install(project, "--skip-prepare")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(settings.read_text(encoding="utf-8"), "client stage\n")
        self.assertEqual(manifest.read_text(encoding="utf-8"), "client manifest\n")
        self.assertEqual(self.fx.run(["git", "-C", str(project), "status", "--porcelain"]).returncode, 0)
        self.assertNotIn(".agents/ask.local/stages/01-grill.md", self.fx.run(
            ["git", "-C", str(project), "status", "--porcelain"]
        ).stdout)

    def _rsync_fault(self, marker: Path, *, sleep: bool) -> Path:
        real_rsync = shutil.which("rsync")
        self.assertIsNotNone(real_rsync, "rsync is required by install-kit")
        bin_dir = self.fx.root / "fault-bin"
        bin_dir.mkdir(exist_ok=True)
        wrapper = bin_dir / "rsync"
        wrapper.write_text(
            "#!/bin/sh\n"
            + f"{real_rsync} \"$@\" || exit $?\n"
            + f"printf hit > {marker}\n"
            + ("while :; do sleep 1; done\n" if sleep else "exit 55\n"),
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        return bin_dir

    def _recover(self, project: Path) -> subprocess.CompletedProcess[str]:
        helper = project / "_ask/scripts/write-transaction.py"
        return self.fx.run(["python3", str(helper), "recover", "--root", str(project)])

    def test_caught_failure_restores(self) -> None:
        project = self.fx.git_project(self.fx.root / "caught-failure")
        old = project / "_ask/agents/00-explore.md"
        old.parent.mkdir(parents=True)
        old.write_text("client bytes\n", encoding="utf-8")
        marker = self.fx.root / "rsync-hit"
        env = dict(self.fx.env, PATH=f"{self._rsync_fault(marker, sleep=False)}:{self.fx.env['PATH']}")

        result = self.fx.run(["bash", str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(project)], env=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(old.read_text(encoding="utf-8"), "client bytes\n")
        self.assertFalse((project / "ask").exists())
        self.assertTrue(marker.exists(), "injected failure did not run")

    def test_kill_restart_recovers(self) -> None:
        project = self.fx.git_project(self.fx.root / "killed-install")
        old = project / "_ask/agents/00-explore.md"
        old.parent.mkdir(parents=True)
        old.write_text("client bytes\n", encoding="utf-8")
        marker = self.fx.root / "rsync-hit"
        env = dict(self.fx.env, PATH=f"{self._rsync_fault(marker, sleep=True)}:{self.fx.env['PATH']}")
        process = subprocess.Popen(
            ["bash", str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(project)],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True,
        )
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
            time.sleep(0.02)
        self.assertTrue(marker.exists(), "install did not reach its first staged copy")
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate(timeout=5)

        first = self._recover(project)
        second = self._recover(project)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(old.read_text(encoding="utf-8"), "client bytes\n")
        self.assertFalse((project / "ask").exists())

    def test_recovery_preserves_intervening_edits(self) -> None:
        project = self.fx.git_project(self.fx.root / "edited-during-recovery")
        old = project / "_ask/agents/00-explore.md"
        old.parent.mkdir(parents=True)
        old.write_text("client bytes\n", encoding="utf-8")
        marker = self.fx.root / "rsync-hit"
        env = dict(self.fx.env, PATH=f"{self._rsync_fault(marker, sleep=True)}:{self.fx.env['PATH']}")
        process = subprocess.Popen(
            ["bash", str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(project)],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True,
        )
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
            time.sleep(0.02)
        self.assertTrue(marker.exists(), "install did not reach its first staged copy")
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate(timeout=5)
        old.write_text("intervening client edit\n", encoding="utf-8")

        result = self._recover(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(old), result.stderr + result.stdout)
        self.assertEqual(old.read_text(encoding="utf-8"), "intervening client edit\n")


if __name__ == "__main__":
    unittest.main()
