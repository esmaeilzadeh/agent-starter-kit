"""Installed launcher trust and completion behavior."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from client_security_fixtures import ClientFixture, ROOT


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = ClientFixture()

    def tearDown(self) -> None:
        self.fx.close()

    def identity(self, root: Path) -> dict:
        proc = self.fx.run([
            "python3", str(ROOT / "_ask/scripts/launcher-trust.py"),
            "identity", "--root", str(root),
        ])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_identity_scope(self) -> None:
        project = self.fx.git_project(self.fx.root / "identity-project")
        (project / "ask").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (project / "ask").chmod(0o755)
        helper = project / "_ask/scripts/helper.py"
        helper.parent.mkdir(parents=True)
        helper.write_text("print('ok')\n", encoding="utf-8")
        first = self.identity(project)

        alias = self.fx.root / "identity-alias"
        alias.symlink_to(project, target_is_directory=True)
        self.assertEqual(self.identity(alias)["digest"], first["digest"])

        metadata = project / ".agents/ask.local/bindings/models.yaml"
        metadata.parent.mkdir(parents=True)
        metadata.write_text("review: sol-medium\n", encoding="utf-8")
        self.assertEqual(self.identity(project)["digest"], first["digest"])

        helper.write_text("print('changed')\n", encoding="utf-8")
        second = self.identity(project)
        self.assertNotEqual(second["digest"], first["digest"])
        helper.chmod(0o755)
        self.assertNotEqual(self.identity(project)["digest"], second["digest"])

        moved = self.fx.root / "moved-project"
        project.rename(moved)
        moved_identity = self.identity(moved)
        self.assertNotEqual(moved_identity["root"], first["root"])

    def test_delegation_requires_trust(self) -> None:
        launcher = self.fx.install_launcher()
        project = self.fx.git_project(self.fx.root / "untrusted-project")
        (project / "_ask/scripts").mkdir(parents=True)
        (project / "_ask/scripts/helper.py").write_text("print('original')\n", encoding="utf-8")
        marker = self.fx.root / "dispatcher-ran"
        dispatcher = project / "ask"
        dispatcher.write_text(
            "#!/bin/sh\nprintf executed > \"$ASKIT_TEST_MARKER\"\n", encoding="utf-8"
        )
        dispatcher.chmod(0o755)
        env = {**self.fx.env, "ASKIT_TEST_MARKER": str(marker)}

        refused = self.fx.run([str(launcher), "verify"], cwd=project, env=env)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("trust", (refused.stdout + refused.stderr).lower())
        self.assertFalse(marker.exists())

        trusted = self.fx.run_tty([str(launcher), "trust"], cwd=project, env=env, input="y\n")
        self.assertEqual(trusted.returncode, 0, trusted.stderr)
        self.assertIn("sha256", (trusted.stdout + trusted.stderr).lower())
        allowed = self.fx.run([str(launcher), "verify"], cwd=project, env=env)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertTrue(marker.exists())

        marker.unlink()
        (project / "_ask/scripts/helper.py").write_text("print('replacement')\n", encoding="utf-8")
        stale = self.fx.run([str(launcher), "verify"], cwd=project, env=env)
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("trust", (stale.stdout + stale.stderr).lower())
        self.assertFalse(marker.exists())

    def test_completion_stays_installed(self) -> None:
        launcher = self.fx.install_launcher()
        project = self.fx.git_project(self.fx.root / "completion-project")
        (project / "_ask").mkdir()
        marker = self.fx.root / "completion-dispatcher-ran"
        dispatcher = project / "ask"
        dispatcher.write_text(
            "#!/bin/sh\nprintf executed > \"$ASKIT_TEST_MARKER\"\n", encoding="utf-8"
        )
        dispatcher.chmod(0o755)
        result = self.fx.run(
            [str(launcher), "--complete", "1", "askit"], cwd=project,
            env={**self.fx.env, "ASKIT_TEST_MARKER": str(marker)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("status", result.stdout)
        self.assertFalse(marker.exists())

    def test_completion_requires_opt_in(self) -> None:
        launcher = self.fx.install_launcher()
        project = self.fx.git_project(self.fx.root / "completion-opt-in-project")
        (project / "_ask").mkdir()
        marker = self.fx.root / "help-dispatcher-ran"
        dispatcher = project / "ask"
        dispatcher.write_text(
            "#!/bin/sh\nprintf executed > \"$ASKIT_TEST_MARKER\"\n", encoding="utf-8"
        )
        dispatcher.chmod(0o755)
        env = self.fx.env.copy()
        env.pop("ASKIT_SKIP_COMPLETION_INSTALL", None)
        env["ASKIT_TEST_MARKER"] = str(marker)
        startup = {name: (self.fx.home / name).read_bytes() if (self.fx.home / name).exists() else None
                   for name in (".bashrc", ".zshrc")}

        help_result = self.fx.run([str(launcher), "--help"], cwd=project, env=env)
        completion = self.fx.run([str(launcher), "completion", "bash"], cwd=project, env=env)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertEqual(completion.returncode, 0, completion.stderr)
        self.assertFalse(marker.exists())
        self.assertEqual(
            {name: (self.fx.home / name).read_bytes() if (self.fx.home / name).exists() else None
             for name in startup}, startup,
        )

        installed = self.fx.run([str(launcher), "completion-install"], cwd=project, env=env)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertTrue((self.fx.home / ".bashrc").exists())
        self.assertTrue((self.fx.home / ".zshrc").exists())
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
