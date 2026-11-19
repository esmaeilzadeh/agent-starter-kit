"""Write preflight and recoverable client update transactions."""

from __future__ import annotations

import os
import hashlib
import json
import shutil
import stat
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

    def _claim_existing(self, project: Path, path: Path) -> None:
        state = project / ".git/askit-transactions"
        state.mkdir(mode=0o700)
        (state / "owned-files.json").write_text(json.dumps({
            "schema": "askit-installed-files/v1",
            "files": {path.relative_to(project).as_posix(): {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "mode": stat.S_IMODE(path.stat().st_mode),
            }},
        }), encoding="utf-8")
        (state / "owned-files.json").chmod(0o600)

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

        valid = self.fx.git_project(self.fx.root / "reinstall-conflict")
        installed = self._install(valid, "--skip-prepare")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        owned = valid / "_ask/agents/00-explore.md"
        original = owned.read_bytes()
        original_gitignore = (valid / ".gitignore").read_bytes()
        unsafe = valid / ".cursor/commands"
        shutil.rmtree(unsafe)
        unsafe.unlink(missing_ok=True)
        unsafe_outside = self.fx.root / "reinstall-outside"
        unsafe_outside.mkdir()
        unsafe_sentinel = unsafe_outside / "sentinel"
        unsafe_sentinel.write_text("keep\n", encoding="utf-8")
        unsafe.symlink_to(unsafe_outside, target_is_directory=True)

        version = self.fx.run(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
        attempts = [
            self._install(valid, "--skip-prepare"),
            self.fx.run([
                "bash", str(ROOT / "_ask/scripts/upgrade-kit.sh"), "--version", version,
                "--expected-commit", version, "--source", str(ROOT), "--target", str(valid),
                "--skip-prepare",
            ]),
            self.fx.run(["bash", str(valid / "_ask/scripts/sync-cursor-binding.sh")], cwd=valid),
        ]
        for attempt in attempts:
            self.assertNotEqual(attempt.returncode, 0, attempt.stdout)
            self.assertIn(".cursor", attempt.stderr + attempt.stdout)
            self.assertEqual(owned.read_bytes(), original)
            self.assertEqual((valid / ".gitignore").read_bytes(), original_gitignore)
            self.assertEqual(sorted(p.name for p in unsafe_outside.iterdir()), ["sentinel"])

        standalone = self.fx.git_project(self.fx.root / "standalone-sync")
        self.assertEqual(self._install(standalone, "--skip-prepare").returncode, 0)
        calls = [
            self.fx.run(["bash", str(standalone / "_ask/scripts/sync-cursor-binding.sh")], cwd=standalone),
            self.fx.run(["python3", str(standalone / "_ask/scripts/sync-codex-skills.py"), "--update-ignore"], cwd=standalone),
            self.fx.run(["bash", str(standalone / "_ask/scripts/copy-project-config.sh"),
                         str(standalone), str(standalone / "_ask/skills/manifest.yaml")], cwd=standalone),
        ]
        for call in calls:
            self.assertEqual(call.returncode, 0, call.stderr)

        empty = self.fx.git_project(self.fx.root / "empty-config-target")
        default_manifest = self.fx.root / "custom-default.yaml"
        default_manifest.write_text("version: 1\nskills: []\n", encoding="utf-8")
        seeded = self.fx.run([
            "bash", str(ROOT / "_ask/scripts/copy-project-config.sh"),
            str(empty), str(default_manifest),
        ])
        self.assertEqual(seeded.returncode, 0, seeded.stderr)
        self.assertEqual((empty / ".agents/ask.local/skills/manifest.yaml").read_text(),
                         "version: 1\nskills: []\n")

        aliased = self.fx.git_project(self.fx.root / "alias-target")
        alias = self.fx.root / "alias"
        alias.symlink_to(aliased, target_is_directory=True)
        installed = self._install(alias, "--skip-prepare")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        version = self.fx.run(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
        upgraded = self.fx.run([
            "bash", str(ROOT / "_ask/scripts/upgrade-kit.sh"), "--version", version,
            "--expected-commit", version, "--source", str(ROOT), "--target", str(alias),
            "--skip-prepare",
        ])
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr)

    def test_preserve_client_settings(self) -> None:
        project = self.fx.git_project(self.fx.root / "preserve-client")
        settings = project / ".agents/ask.local/stages/01-grill.md"
        settings.parent.mkdir(parents=True)
        settings.write_text("client stage\n", encoding="utf-8")
        manifest = project / "_ask/skills/manifest.yaml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("client manifest\n", encoding="utf-8")
        cursor_settings = project / ".cursor/settings.json"
        cursor_settings.parent.mkdir(parents=True)
        cursor_settings.write_text('{"editor": "client"}\n', encoding="utf-8")
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
        owner_path = project / ".git/askit-transactions/owned-files.json"
        owner_manifest = json.loads(owner_path.read_text())
        self.assertNotIn(".cursor/settings.json", owner_manifest["files"])
        version = self.fx.run(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
        upgraded = self.fx.run([
            "bash", str(ROOT / "_ask/scripts/upgrade-kit.sh"), "--version", version,
            "--expected-commit", version, "--source", str(ROOT), "--target", str(project),
            "--skip-prepare",
        ])
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr)
        self.assertEqual(cursor_settings.read_text(encoding="utf-8"), '{"editor": "client"}\n')
        self.assertNotIn(".cursor/settings.json", json.loads(owner_path.read_text())["files"])

    def _fault_environment(self, project: Path, marker: Path, mode: str) -> dict[str, str]:
        hooks = self.fx.root / ("python-hook-" + mode)
        hooks.mkdir()
        (hooks / "sitecustomize.py").write_text(
            "import os, pathlib, time\n"
            "_replace = os.replace\n"
            "_triggered = False\n"
            "_root = pathlib.Path(os.environ['ASK_TEST_PROJECT']).resolve()\n"
            "_marker = pathlib.Path(os.environ['ASK_TEST_MARKER'])\n"
            "_mode = os.environ['ASK_TEST_MODE']\n"
            "import json\n"
            "def replace(src, dst, *args, **kwargs):\n"
            "    global _triggered\n"
            "    target = pathlib.Path(dst)\n"
            "    if _mode == 'edit' and target.name == 'journal.json':\n"
            "        data = json.loads(pathlib.Path(src).read_text())\n"
            "        if data.get('state') != 'committed':\n"
            "            (_root / '_ask/agents/00-explore.md').write_text('concurrent client edit\\n')\n"
            "    result = _replace(src, dst, *args, **kwargs)\n"
            "    if _mode == 'finalize' and target.name == 'journal.json':\n"
            "        data = json.loads(target.read_text())\n"
            "        if data.get('state') == 'committed':\n"
            "            _marker.write_text('finalizing')\n"
            "            while True: time.sleep(1)\n"
            "    if (not _triggered and target.name == '00-explore.md' and "
            "target.parent == _root / '_ask/agents'):\n"
            "        _triggered = True\n"
            "        _marker.write_text('published')\n"
            "        if _mode == 'fail': raise OSError('injected publish failure')\n"
            "        if _mode == 'pause':\n"
            "            while True: time.sleep(1)\n"
            "    return result\n"
            "os.replace = replace\n",
            encoding="utf-8",
        )
        return dict(
            self.fx.env,
            PYTHONPATH=str(hooks),
            ASK_TEST_PROJECT=str(project),
            ASK_TEST_MARKER=str(marker),
            ASK_TEST_MODE=mode,
        )

    def _recover(self, project: Path) -> subprocess.CompletedProcess[str]:
        helper = ROOT / "_ask/scripts/write-transaction.py"
        return self.fx.run(["python3", str(helper), "recover", "--root", str(project)])

    def test_caught_failure_restores(self) -> None:
        project = self.fx.git_project(self.fx.root / "caught-failure")
        old = project / "_ask/agents/00-explore.md"
        old.parent.mkdir(parents=True)
        old.write_text("client bytes\n", encoding="utf-8")
        self._claim_existing(project, old)
        marker = self.fx.root / "publish-hit"
        env = self._fault_environment(project, marker, "fail")

        result = self.fx.run(["bash", str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(project)], env=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(old.read_text(encoding="utf-8"), "client bytes\n")
        self.assertFalse((project / "ask").exists())
        self.assertTrue(marker.exists(), "injected publish failure did not run")

        concurrent = self.fx.git_project(self.fx.root / "concurrent-write")
        old = concurrent / "_ask/agents/00-explore.md"
        old.parent.mkdir(parents=True)
        old.write_text("kit bytes\n", encoding="utf-8")
        self._claim_existing(concurrent, old)
        concurrent_result = self.fx.run(
            ["bash", str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(concurrent)],
            env=self._fault_environment(concurrent, self.fx.root / "concurrent-hit", "edit"),
        )
        self.assertNotEqual(concurrent_result.returncode, 0)
        self.assertEqual(old.read_text(encoding="utf-8"), "concurrent client edit\n")

    def test_kill_restart_recovers(self) -> None:
        project = self.fx.git_project(self.fx.root / "killed-install")
        dispatcher = project / "ask"
        dispatcher.write_text("#!/bin/sh\nprintf ran > \"$ASKIT_TEST_MARKER\"\n", encoding="utf-8")
        dispatcher.chmod(0o755)
        installed = self._install(project, "--skip-prepare")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        old = project / "_ask/agents/00-explore.md"
        original = old.read_bytes()
        marker = self.fx.root / "publish-hit"
        env = self._fault_environment(project, marker, "pause")
        helper = project / "_ask/scripts/write-transaction.py"
        process = subprocess.Popen(
            ["python3", str(helper), "run", "--root", str(project), "--path", "_ask/agents", "--",
             "python3", "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('interrupted\\n')",
             "{target}/_ask/agents/00-explore.md"],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True,
        )
        deadline = time.monotonic() + 10
        try:
            while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.02)
            self.assertTrue(marker.exists(), "install did not reach the first publish")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.communicate(timeout=5)

        self.assertNotEqual(old.read_bytes(), original)
        launcher = self.fx.install_launcher()
        trusted = self.fx.run_tty([str(launcher), "trust"], cwd=project, env=self.fx.env, input="y\n")
        self.assertEqual(trusted.returncode, 0, trusted.stderr)
        self.assertEqual(old.read_bytes(), original)
        delegated = self.fx.run(
            [str(launcher), "verify"], cwd=project,
            env={**self.fx.env, "ASKIT_TEST_MARKER": str(self.fx.root / "dispatcher-ran")},
        )
        self.assertEqual(delegated.returncode, 0, delegated.stderr)
        self.assertTrue((self.fx.root / "dispatcher-ran").exists())

        finalizing = self.fx.git_project(self.fx.root / "finalize-restart")
        installed = self._install(finalizing, "--skip-prepare")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        path = finalizing / "_ask/agents/00-explore.md"
        marker = self.fx.root / "finalize-hit"
        env = self._fault_environment(finalizing, marker, "finalize")
        process = subprocess.Popen(
            ["python3", str(finalizing / "_ask/scripts/write-transaction.py"), "run",
             "--root", str(finalizing), "--path", "_ask/agents", "--",
             "python3", "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('committed\\n')",
             "{target}/_ask/agents/00-explore.md"],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True,
        )
        deadline = time.monotonic() + 10
        try:
            while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.02)
            self.assertTrue(marker.exists(), "transaction did not persist committed state")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.communicate(timeout=5)
        self.assertEqual(path.read_text(encoding="utf-8"), "committed\n")
        recovered = self._recover(finalizing)
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(list((finalizing / ".git/askit-transactions").glob("*/journal.json")), [])

    def test_recovery_preserves_intervening_edits(self) -> None:
        project = self.fx.git_project(self.fx.root / "edited-during-recovery")
        old = project / "_ask/agents/00-explore.md"
        old.parent.mkdir(parents=True)
        old.write_text("client bytes\n", encoding="utf-8")
        self._claim_existing(project, old)
        marker = self.fx.root / "publish-hit"
        env = self._fault_environment(project, marker, "pause")
        process = subprocess.Popen(
            ["bash", str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(project)],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True,
        )
        deadline = time.monotonic() + 10
        try:
            while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.02)
            self.assertTrue(marker.exists(), "install did not reach the first publish")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.communicate(timeout=5)
        pending = old.read_text(encoding="utf-8")
        self.assertNotEqual(pending, "client bytes\n")
        state = project / ".git/askit-transactions"
        journal = next(state.glob("*/journal.json"))
        saved = journal.read_text(encoding="utf-8")
        record = json.loads(saved)
        record["files"].insert(0, {"path": "../outside/sentinel"})
        journal.write_text(json.dumps(record), encoding="utf-8")
        rejected = self._recover(project)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertTrue(journal.exists())
        self.assertEqual(old.read_text(encoding="utf-8"), pending)
        journal.write_text(saved, encoding="utf-8")
        old.write_text("intervening client edit\n", encoding="utf-8")

        result = self._recover(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(old), result.stderr + result.stdout)
        self.assertEqual(old.read_text(encoding="utf-8"), "intervening client edit\n")


if __name__ == "__main__":
    unittest.main()
