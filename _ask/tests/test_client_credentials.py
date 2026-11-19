"""Private tracker credential storage, migration, and setup journeys."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import unittest
from pathlib import Path

from client_security_fixtures import ClientFixture, ROOT


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = ClientFixture()

    def tearDown(self) -> None:
        self.fx.close()

    def _install(self, project: Path) -> None:
        result = self.fx.run([
            "bash", str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(project),
        ])
        self.assertEqual(result.returncode, 0, result.stderr)

    def _env(self, *, bin_dir: Path | None = None) -> dict[str, str]:
        env = dict(self.fx.env)
        env["TERM"] = "xterm"
        if bin_dir:
            env["PATH"] = str(bin_dir) + ":/usr/bin:/bin"
        return env

    def _run_config(self, project: Path, *args: str, input: str | None = None,
                    env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return self.fx.run(
            ["python3", str(project / "_ask/scripts/tracker-config.py"), *args],
            cwd=project, env=env or self._env(), input=input,
        )

    def test_legacy_data_and_urls(self) -> None:
        project = self.fx.git_project(self.fx.root / "credential-parser")
        self._install(project)
        marker = self.fx.root / "shell-ran"
        legacy = project / ".ask.env"
        legacy.write_text(
            "# old config\nASK_TRACKER=jira\n"
            "JIRA_PERSONAL_TOKEN='$(touch " + str(marker) + ")'\n",
            encoding="utf-8",
        )

        parsed = self._run_config(project, "validate-legacy", str(legacy))
        self.assertEqual(parsed.returncode, 0, parsed.stderr)
        self.assertFalse(marker.exists())
        good = self._run_config(project, "validate-url", "https://jira.example.test")
        self.assertEqual(good.returncode, 0, good.stderr)
        for rejected in ("http://jira.example.test", "https://user:secret@jira.example.test"):
            bad = self._run_config(project, "validate-url", rejected)
            self.assertNotEqual(bad.returncode, 0)
            self.assertNotIn("secret", bad.stderr + bad.stdout)
            self.assertNotIn("user", bad.stderr + bad.stdout)
        malformed = legacy.with_name("malformed.env")
        malformed.write_text("JIRA_PERSONAL_TOKEN=$(touch " + str(marker) + ")\n", encoding="utf-8")
        rejected = self._run_config(project, "validate-legacy", str(malformed))
        self.assertNotEqual(rejected.returncode, 0)
        self.assertNotIn(str(marker), rejected.stderr + rejected.stdout)
        self.assertFalse(marker.exists())

    def test_private_storage_and_mcp_opt_in(self) -> None:
        project = self.fx.git_project(self.fx.root / "private-credentials")
        self._install(project)
        external = json.dumps({
            "tracker": "jira", "url": "https://jira.example.test",
            "credentials": {"JIRA_PERSONAL_TOKEN": "dummy-private-token"},
        })
        store = self._run_config(project, "store", "--root", str(project), input=external)
        self.assertEqual(store.returncode, 0, store.stderr)
        key = hashlib.sha256(str(project.resolve()).encode()).hexdigest()
        private_dir = self.fx.config / "askit/projects" / key
        credentials = private_dir / "credentials.json"
        self.assertEqual(stat.S_IMODE(private_dir.parent.parent.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(private_dir.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(credentials.stat().st_mode), 0o600)
        self.assertEqual(json.loads(credentials.read_text())["credentials"]["JIRA_PERSONAL_TOKEN"],
                         "dummy-private-token")

        mcp = self.fx.root / "home/cursor/mcp.json"
        mcp.parent.mkdir(parents=True)
        before = '{"mcpServers":{"existing":{"command":"keep"}}}\n'
        mcp.write_text(before)
        denied = self._run_config(project, "mcp", "--root", str(project), "--config", str(mcp),
                                  "--opt-in", "no")
        self.assertEqual(denied.returncode, 0, denied.stderr)
        self.assertEqual(mcp.read_text(), before)
        granted = self._run_config(project, "mcp", "--root", str(project), "--config", str(mcp),
                                   "--opt-in", "yes")
        self.assertEqual(granted.returncode, 0, granted.stderr)
        saved = json.loads(mcp.read_text())
        self.assertIn("existing", saved["mcpServers"])
        self.assertIn("askit-tracker", saved["mcpServers"])
        self.assertNotIn("dummy-private-token", mcp.read_text())

        outside = self.fx.root / "credential-outside"
        outside.mkdir()
        unsafe = self.fx.root / "config/askit"
        if unsafe.exists():
            import shutil
            shutil.rmtree(unsafe)
        unsafe.symlink_to(outside, target_is_directory=True)
        refused = self._run_config(project, "store", "--root", str(project), input=external)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(list(outside.iterdir()), [])

    def test_migrate_staged_credentials(self) -> None:
        project = self.fx.git_project(self.fx.root / "credential-migration")
        self._install(project)
        marker = self.fx.root / "migration-shell-ran"
        legacy = project / ".ask.env"
        legacy.write_text(
            "# preserve this comment\nASK_TRACKER=jira\n"
            "ASK_TRACKER_URL=https://jira.example.test\n"
            "MEMORY_CHOICE=2\nJIRA_PERSONAL_TOKEN='$(touch " + str(marker) + ")'\n",
            encoding="utf-8",
        )
        self.fx.run(["git", "-C", str(project), "add", ".ask.env"])
        self.fx.run(["git", "-C", str(project), "commit", "-qm", "legacy credentials"])
        self.fx.run(["git", "-C", str(project), "add", ".ask.env"])
        result = self._run_config(project, "migrate", "--root", str(project), "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        self.assertIn("rotation", (result.stdout + result.stderr).lower())
        self.assertNotIn("$(touch", legacy.read_text())
        self.assertIn("# preserve this comment", legacy.read_text())
        self.assertIn("MEMORY_CHOICE=2", legacy.read_text())
        self.assertTrue(self.fx.run(["git", "-C", str(project), "diff", "--cached", "--quiet", "--", ".ask.env"]).returncode == 0)
        history = self.fx.run(["git", "-C", str(project), "show", "HEAD:.ask.env"]).stdout
        self.assertIn("JIRA_PERSONAL_TOKEN", history)
        key = hashlib.sha256(str(project.resolve()).encode()).hexdigest()
        credentials = self.fx.config / "askit/projects" / key / "credentials.json"
        self.assertEqual(json.loads(credentials.read_text())["credentials"]["JIRA_PERSONAL_TOKEN"],
                         "$(touch " + str(marker) + ")")

        bin_dir = self.fx.root / "fake-bin"
        bin_dir.mkdir()
        capture = self.fx.root / "mcp-child.json"
        uvx = bin_dir / "uvx"
        uvx.write_text(
            "#!/usr/bin/env python3\nimport json, os, sys\n"
            "json.dump({'argv': sys.argv[1:], 'url': os.getenv('JIRA_URL'), "
            "'token': os.getenv('JIRA_PERSONAL_TOKEN'), 'other': os.getenv('GITHUB_TOKEN')}, "
            "open(os.environ['ASK_TEST_CAPTURE'], 'w'))\n",
            encoding="utf-8",
        )
        uvx.chmod(0o755)
        called = self.fx.run(
            ["python3", str(project / "_ask/scripts/tracker-mcp.py"), "--root", str(project)],
            cwd=project, env={**self._env(bin_dir=bin_dir), "ASK_TEST_CAPTURE": str(capture),
                              "GITHUB_TOKEN": "unrelated-caller-token"},
        )
        self.assertEqual(called.returncode, 0, called.stderr)
        child = json.loads(capture.read_text())
        self.assertEqual(child["token"], "$(touch " + str(marker) + ")")
        self.assertEqual(child["url"], "https://jira.example.test")
        self.assertIsNone(child["other"])
        self.assertIn("mcp-atlassian==0.24.6", " ".join(child["argv"]))

    def test_fresh_setup_pty(self) -> None:
        project = self.fx.git_project(self.fx.root / "fresh-credential-setup")
        self._install(project)
        bin_dir = self.fx.root / "setup-bin"
        bin_dir.mkdir()
        xdg_open = bin_dir / "xdg-open"
        xdg_open.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        xdg_open.chmod(0o755)
        mcp = self.fx.root / "home/cursor/mcp.json"
        mcp.parent.mkdir(parents=True)
        mcp.write_text('{"mcpServers":{"existing":{"command":"keep"}}}\n')
        result = self.fx.run_tty(
            [str(project / "ask"), "setup"], cwd=project,
            env={**self._env(bin_dir=bin_dir), "MCP_JSON": str(mcp)},
            input="\njira\nhttps://jira.example.test\ndummy-setup-token\nn\n2\n\n\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("dummy-setup-token", result.stdout + result.stderr)
        self.assertEqual(mcp.read_text(), '{"mcpServers":{"existing":{"command":"keep"}}}\n')
        local_path = project / ".agents/ask.local/tracker.json"
        self.assertTrue(local_path.exists(), "setup did not create local public tracker settings")
        local = json.loads(local_path.read_text())
        self.assertEqual(local, {"tracker": "jira", "url": "https://jira.example.test"})
        key = hashlib.sha256(str(project.resolve()).encode()).hexdigest()
        private = self.fx.config / "askit/projects" / key / "credentials.json"
        self.assertTrue(private.exists(), "setup did not store credentials privately")
        self.assertEqual(stat.S_IMODE(private.stat().st_mode), 0o600)
        self.assertEqual(json.loads(private.read_text())["credentials"]["JIRA_PERSONAL_TOKEN"],
                         "dummy-setup-token")


if __name__ == "__main__":
    unittest.main()
