"""Focused distribution and dependency approval checks for disposable clients."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from client_security_fixtures import ClientFixture, ROOT


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = ClientFixture()

    def tearDown(self) -> None:
        self.fx.close()

    def test_immutable_pins(self) -> None:
        pins_path = ROOT / "_ask/skills/dependency-pins.json"
        self.assertTrue(pins_path.is_file(), "reviewed dependency pin record is missing")
        pins = json.loads(pins_path.read_text(encoding="utf-8"))
        self.assertEqual(pins["schema"], "ask-dependency-pins/v1")

        manifest = ROOT / "_ask/skills/manifest.yaml"
        entries: dict[str, dict[str, str]] = {}
        current: dict[str, str] | None = None
        for line in manifest.read_text(encoding="utf-8").splitlines():
            item = re.fullmatch(r"  ([A-Za-z0-9_-]+):", line)
            field = re.fullmatch(r"    (source|revision|skill):\s*['\"]?([^'\"]+)['\"]?", line)
            if item:
                current = entries.setdefault(item.group(1), {})
            elif field and current is not None:
                current[field.group(1)] = field.group(2)

        self.assertEqual(set(entries), set(pins["skills"]))
        for skill_id, entry in entries.items():
            identity = pins["skills"][skill_id]
            self.assertEqual(entry["source"], identity["source"])
            self.assertEqual(entry["revision"], identity["commit"])
            self.assertEqual(entry["skill"], identity["skill"])
            self.assertRegex(entry["revision"], r"^[0-9a-f]{40}$")
            self.assertRegex(identity["tree"], r"^[0-9a-f]{40}$")
            self.assertRegex(identity["skill_sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(identity["path"] == "SKILL.md" or identity["path"].endswith("/SKILL.md"))

        cli = pins["packages"]["skills"]
        self.assertEqual(cli["version"], "1.5.18")
        self.assertEqual(cli["node"], ">=18")
        self.assertEqual(
            cli["integrity"],
            "sha512-WwQuqIhmS2nrn1H3HAbE2tGe7e2npc1cwMcucMKqmkBdqzm7nxzcZBTqXiHjUKhpalQLE/nNPtEdcx3QYX4TTw==",
        )
        self.assertRegex(cli["source_commit"], r"^[0-9a-f]{40}$")

        tracker = pins["packages"]["mcp-atlassian"]
        self.assertEqual(tracker["version"], "0.24.6")
        self.assertEqual(tracker["python"], ">=3.10")
        self.assertEqual(
            tracker["wheel_sha256"],
            "d515b53b7b3f330c94ac6b675bcf2bdd244deb725f5db575575627dfe0786070",
        )
        self.assertRegex(tracker["source_commit"], r"^[0-9a-f]{40}$")

    def _source_project(self, name: str) -> tuple[Path, str]:
        source = self.fx.git_project(self.fx.root / name)
        skill = source / "skill/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: demo\n---\n", encoding="utf-8")
        self.fx.run(["git", "-C", str(source), "add", "skill/SKILL.md"])
        self.fx.run(["git", "-C", str(source), "commit", "-qm", "skill source"])
        commit = self.fx.run(["git", "-C", str(source), "rev-parse", "HEAD"]).stdout.strip()
        return source, commit

    @staticmethod
    def _skill_manifest(source: Path, commit: str, skill: str = "demo") -> str:
        return (
            "skills:\n"
            f"  {skill}:\n"
            f"    source: \"{source}\"\n"
            f"    revision: \"{commit}\"\n"
            f"    skill: {skill}\n"
            "    role: fixture\n"
            "    required: false\n"
        )

    def _install_npx_spy(self) -> tuple[Path, dict[str, str]]:
        bin_dir = self.fx.root / "bin"
        bin_dir.mkdir()
        log = self.fx.root / "npx.log"
        npx = bin_dir / "npx"
        npx.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> \"$ASKIT_TEST_NPX_LOG\"\n"
            "exit \"${ASKIT_TEST_NPX_EXIT:-0}\"\n",
            encoding="utf-8",
        )
        npx.chmod(0o755)
        env = self.fx.env | {
            "PATH": f"{bin_dir}:{self.fx.env['PATH']}",
            "ASKIT_TEST_NPX_LOG": str(log),
        }
        env.pop("SKIP_INSTALL", None)
        return log, env

    def test_reject_mismatched_source(self) -> None:
        marker = self.fx.root / "source-helper-ran"
        source = self.fx.make_untrusted_source(marker)
        wrong_commit = "0" * 40

        cache = self.fx.cache / "askit/kit"
        cache.mkdir(parents=True)
        old_launcher = cache / "askit"
        old_launcher.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        old_launcher.chmod(0o755)
        installed = self.fx.prefix / "bin/askit"
        installed.parent.mkdir(parents=True)
        installed.symlink_to(old_launcher)
        cache_sentinel = cache / "client-state"
        cache_sentinel.write_text("preserve\n", encoding="utf-8")

        self_install = self.fx.run(
            ["bash", "-s", "--", "--source", str(source), "--ref", "main",
             "--expected-commit", wrong_commit, "--prefix", str(self.fx.prefix)],
            cwd=self.fx.root,
            input=(ROOT / "askit").read_text(encoding="utf-8"),
        )
        self.assertNotEqual(self_install.returncode, 0)
        self.assertIn("mismatch", self_install.stderr.lower())
        self.assertFalse(marker.exists(), "unverified source helper ran during self-install")
        self.assertEqual(cache_sentinel.read_text(encoding="utf-8"), "preserve\n")
        self.assertEqual(installed.resolve(), old_launcher)

        client = self.fx.git_project(self.fx.root / "upgrade-client")
        installed_ask = self.fx.run(
            [str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(client)]
        )
        self.assertEqual(installed_ask.returncode, 0, installed_ask.stderr)
        before = (client / "README.md").read_bytes()
        upgrade = self.fx.run(
            [str(ROOT / "_ask/scripts/upgrade-kit.sh"), "--version", "main",
             "--source", str(source), "--expected-commit", wrong_commit],
            cwd=client,
        )
        self.assertNotEqual(upgrade.returncode, 0)
        self.assertIn("mismatch", upgrade.stderr.lower())
        self.assertFalse(marker.exists(), "unverified upgrade helper ran")
        self.assertEqual((client / "README.md").read_bytes(), before)
        self.assertTrue((client / "ask").is_file())

    def test_source_approval_before_fetch(self) -> None:
        source, commit = self._source_project("skill-source")
        other_source, _ = self._source_project("other-skill-source")
        overlay = self.fx.root / "project/.agents/ask.local/skills/manifest.yaml"
        overlay.parent.mkdir(parents=True)
        overlay.write_text(self._skill_manifest(source, commit), encoding="utf-8")
        project = overlay.parents[3]
        log, env = self._install_npx_spy()
        env["HOME"] = str(project)
        env["XDG_CONFIG_HOME"] = str(self.fx.config)

        refused = self.fx.run(["bash", str(ROOT / "_ask/skills/prepare-skills.sh")],
                              cwd=project, env=env)
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse(log.exists(), "skill installer fetched an unapproved source")

        approved = self.fx.run_tty(
            ["bash", str(ROOT / "_ask/skills/prepare-skills.sh")],
            cwd=project, env=env, input="y\n",
        )
        self.assertEqual(approved.returncode, 0, approved.stdout)
        self.assertTrue(log.is_file(), "approved source was not passed to the installer")
        approvals = self.fx.config / "askit/skill-source-approvals.json"
        self.assertTrue(approvals.is_file())
        self.assertEqual(approvals.stat().st_mode & 0o777, 0o600)
        self.assertEqual(approvals.parent.stat().st_mode & 0o777, 0o700)
        self.assertFalse((project / ".agents/ask.local/skills/skill-source-approvals.json").exists())

        original_calls = log.read_text(encoding="utf-8").splitlines()
        variations = [
            self._skill_manifest(other_source, commit),
            self._skill_manifest(source, "f" * 40),
            self._skill_manifest(source, commit, "different-skill"),
        ]
        for manifest in variations:
            overlay.write_text(manifest, encoding="utf-8")
            refused = self.fx.run(["bash", str(ROOT / "_ask/skills/prepare-skills.sh")],
                                  cwd=project, env=env)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(log.read_text(encoding="utf-8").splitlines(), original_calls)

    def test_mandatory_failure_propagates(self) -> None:
        _log, env = self._install_npx_spy()
        env["ASKIT_TEST_NPX_EXIT"] = "47"

        prepare = self.fx.run(["bash", str(ROOT / "_ask/skills/prepare-skills.sh")], env=env)
        self.assertNotEqual(prepare.returncode, 0)

        client = self.fx.git_project(self.fx.root / "install-client")
        install = self.fx.run(
            [str(ROOT / "_ask/scripts/install-kit.sh"), "--force", str(client)], env=env
        )
        self.assertNotEqual(install.returncode, 0, "install reported success after required prepare failed")

        bootstrap_client = self.fx.git_project(self.fx.root / "bootstrap-client")
        bootstrap = self.fx.run(
            ["bash", str(ROOT / "_ask/scripts/askit-bootstrap.sh")], cwd=bootstrap_client,
            env=env | {"ASKIT_KIT_ROOT": str(ROOT), "ASKIT_INSTALL_FLAGS": "--force"},
        )
        self.assertNotEqual(bootstrap.returncode, 0, "bootstrap reported success after prepare failed")

        source_commit = self.fx.run(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
        upgrade_client = self.fx.git_project(self.fx.root / "upgrade-failure-client")
        upgrade = self.fx.run(
            [str(ROOT / "_ask/scripts/upgrade-kit.sh"), "--version", source_commit,
             "--source", str(ROOT)],
            cwd=upgrade_client, env=env,
        )
        self.assertNotEqual(upgrade.returncode, 0, "upgrade reported success after prepare failed")


if __name__ == "__main__":
    unittest.main()
