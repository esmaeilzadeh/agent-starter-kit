"""Focused distribution and dependency approval checks for disposable clients."""

from __future__ import annotations

import json
import base64
import hashlib
import io
import re
import shutil
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from client_security_fixtures import ClientFixture, ROOT
sys.path.insert(0, str(ROOT / "_ask/scripts"))
import distribution


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

        project = self.fx.root / "project"
        local_bin = project / "node_modules/.bin"
        local_bin.mkdir(parents=True)
        fake_npm = local_bin / "npm"
        fake_npm.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
        fake_npm.chmod(0o755)
        (project / ".npmrc").write_text("registry=https://bad.invalid\n", encoding="utf-8")
        local_package = project / "node_modules/skills"
        local_package.mkdir()
        (local_package / "package.json").write_text('{"name":"skills","version":"1.5.18"}')
        artifact = b"fixture skills CLI artifact"
        integrity = "sha512-" + base64.b64encode(hashlib.sha512(artifact).digest()).decode()

        class Response(io.BytesIO):
            @staticmethod
            def geturl() -> str:
                return "https://registry.npmjs.org/skills/-/skills-1.5.18.tgz"

        calls: list[tuple[list[str], Path, dict[str, str]]] = []

        def npm_install(argv, *, cwd, env, text, capture_output):
            calls.append((argv, Path(cwd), env))
            package = Path(cwd) / "node_modules/skills"
            (package / "dist").mkdir(parents=True)
            (package / "package.json").write_text(
                '{"name":"skills","version":"1.5.18","bin":{"skills":"dist/cli.js"}}',
                encoding="utf-8",
            )
            (package / "dist/cli.js").write_text("// verified fixture\n", encoding="utf-8")
            return SimpleNamespace(returncode=0)

        cli_pins = {"packages": {"skills": {
            "version": "1.5.18", "tarball": "https://registry.npmjs.org/skills/-/skills-1.5.18.tgz",
            "integrity": integrity,
        }}}
        with patch.dict("os.environ", {"PATH": f"{local_bin}:{self.fx.env['PATH']}"}), \
             patch("distribution.urllib.request.urlopen", return_value=Response(artifact)), \
             patch("distribution.subprocess.run", side_effect=npm_install):
            node, executable, env = distribution.install_skills_cli(
                cli_pins, project, self.fx.root / "verified-cli")
        self.assertEqual(len(calls), 1)
        argv, cwd, npm_env = calls[0]
        self.assertNotEqual(Path(argv[0]), fake_npm.resolve())
        self.assertNotEqual(cwd, project)
        self.assertIn("--ignore-scripts", argv)
        self.assertIn("--registry=https://registry.npmjs.org", argv)
        self.assertNotIn(str(project / "node_modules/.bin"), npm_env["PATH"])
        self.assertTrue(node.is_file())
        self.assertTrue(executable.is_file())
        self.assertNotIn(str(project), env["PATH"])
        cli_pins["packages"]["skills"]["integrity"] = "sha512-" + base64.b64encode(
            hashlib.sha512(b"different artifact").digest()).decode()
        with patch("distribution.urllib.request.urlopen", return_value=Response(artifact)), \
             patch("distribution.subprocess.run") as run:
            with self.assertRaisesRegex(distribution.DistributionError, "integrity mismatch"):
                distribution.install_skills_cli(cli_pins, project, self.fx.root / "rejected-cli")
            run.assert_not_called()

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
        self.assertEqual(list((self.fx.cache / "askit").glob("kit.*")), [])

        client = self.fx.git_project(self.fx.root / "upgrade-client")
        installed_ask = self.fx.run(
            [str(ROOT / "_ask/scripts/install-kit.sh"), "--skip-prepare", str(client)]
        )
        self.assertEqual(installed_ask.returncode, 0, installed_ask.stderr)
        before = (client / "README.md").read_bytes()
        upgrade = self.fx.run(
            [str(ROOT / "_ask/scripts/upgrade-kit.sh"), "--version", "main",
             "--source", str(source), "--expected-commit", wrong_commit,
             "--target", str(client)],
            cwd=client,
        )
        self.assertNotEqual(upgrade.returncode, 0)
        self.assertIn("mismatch", upgrade.stderr.lower())
        self.assertFalse(marker.exists(), "unverified upgrade helper ran")
        self.assertEqual((client / "README.md").read_bytes(), before)
        self.assertTrue((client / "ask").is_file())

    def test_modified_cached_release_is_not_executed(self) -> None:
        launcher = self.fx.install_launcher()
        cache = self.fx.cache / "askit/kit"
        marker = self.fx.root / "modified-cache-helper-ran"
        helper = cache / "_ask/scripts/install-user-completion.sh"
        helper.write_text(f"#!/bin/sh\nprintf executed > '{marker}'\n", encoding="utf-8")
        helper.chmod(0o755)

        client = self.fx.git_project(self.fx.root / "modified-cache-client")
        direct = self.fx.run([str(launcher)], cwd=client)
        self.assertNotEqual(direct.returncode, 0)
        self.assertIn("cached release is modified", direct.stderr)
        self.assertFalse(marker.exists())

        bootstrap = self.fx.run(
            ["bash", str(cache / "_ask/scripts/askit-bootstrap.sh")], cwd=client,
            env=self.fx.env | {"ASKIT_KIT_ROOT": str(cache)},
        )
        self.assertNotEqual(bootstrap.returncode, 0)
        self.assertIn("cached release is modified", bootstrap.stderr)
        self.assertFalse(marker.exists())

    def test_source_approval_before_fetch(self) -> None:
        source, commit = self._source_project("skill-source")
        other_source, _ = self._source_project("other-skill-source")
        overlay = self.fx.root / "project/.agents/ask.local/skills/manifest.yaml"
        overlay.parent.mkdir(parents=True)
        overlay.write_text(self._skill_manifest(source, commit), encoding="utf-8")
        project = overlay.parents[3]
        (project / "_ask/skills").mkdir(parents=True)
        (project / "_ask/scripts").mkdir(parents=True)
        for relative in (
            "_ask/skills/manifest.yaml",
            "_ask/skills/dependency-pins.json",
            "_ask/skills/prepare-skills.sh",
            "_ask/scripts/distribution.py",
        ):
            shutil.copy2(ROOT / relative, project / relative)
        calls: list[tuple[str, str, bool]] = []

        def install(entry: dict, verified: Path) -> SimpleNamespace:
            actual = self.fx.run(["git", "-C", str(verified), "rev-parse", "HEAD"]).stdout.strip()
            calls.append((entry["source"], actual, verified.is_dir()))
            return SimpleNamespace(returncode=0)

        def run_prepare() -> int:
            try:
                return distribution.prepare(
                    project, overlay, project / "_ask/skills/dependency-pins.json", installer=install)
            except distribution.DistributionError:
                return 1

        with patch.dict("os.environ", {"HOME": str(self.fx.home),
                                        "XDG_CONFIG_HOME": str(self.fx.config)}):
            refused = run_prepare()
            self.assertEqual(refused, 1)
            self.assertEqual(calls, [], "unapproved source was fetched or installed")

            class TTY:
                @staticmethod
                def isatty() -> bool:
                    return True

            with patch("distribution.sys.stdin", TTY()), patch("builtins.input", return_value="y"):
                approved = run_prepare()
        self.assertEqual(approved, 0)
        self.assertEqual(calls, [(str(source), commit, True)])
        approvals = self.fx.config / "askit/skill-source-approvals.json"
        self.assertTrue(approvals.is_file())
        self.assertEqual(approvals.stat().st_mode & 0o777, 0o600)
        self.assertEqual(approvals.parent.stat().st_mode & 0o777, 0o700)
        self.assertFalse((project / ".agents/ask.local/skills/skill-source-approvals.json").exists())

        wrong_root = self.fx.root / "wrong-root"
        (wrong_root / "_ask/skills").mkdir(parents=True)
        script_env = self.fx.env | {"ASK_ROOT": str(wrong_root), "SKIP_INSTALL": "1"}
        prepared = self.fx.run(["bash", str(project / "_ask/skills/prepare-skills.sh")],
                               cwd=project, env=script_env)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)

        original_calls = calls.copy()
        destination = project / ".agents/skills/demo"
        destination.parent.mkdir(parents=True)
        destination.symlink_to(self.fx.root / "outside-skill", target_is_directory=True)
        with patch.dict("os.environ", {"HOME": str(self.fx.home),
                                        "XDG_CONFIG_HOME": str(self.fx.config)}):
            refused = run_prepare()
        self.assertEqual(refused, 1)
        self.assertEqual(calls, original_calls)
        destination.unlink()

        variations = [
            self._skill_manifest(other_source, commit),
            self._skill_manifest(source, "f" * 40),
            self._skill_manifest(source, commit, "different-skill"),
        ]
        for manifest in variations:
            overlay.write_text(manifest, encoding="utf-8")
            with patch.dict("os.environ", {"HOME": str(self.fx.home),
                                            "XDG_CONFIG_HOME": str(self.fx.config)}):
                refused = run_prepare()
            self.assertEqual(refused, 1)
            self.assertEqual(calls, original_calls)

        original_pins = (project / "_ask/skills/dependency-pins.json").read_bytes()
        modified = json.loads(original_pins)
        modified["skills"]["research"]["source"] = str(other_source)
        modified["skills"]["research"]["commit"] = commit
        overlay.write_text(self._skill_manifest(other_source, commit, "research"), encoding="utf-8")
        (project / "_ask/skills/dependency-pins.json").write_text(json.dumps(modified), encoding="utf-8")
        with patch.dict("os.environ", {"HOME": str(self.fx.home),
                                        "XDG_CONFIG_HOME": str(self.fx.config)}):
            refused = run_prepare()
        self.assertEqual(refused, 1)
        self.assertEqual(calls, original_calls)
        (project / "_ask/skills/dependency-pins.json").write_bytes(original_pins)

    def test_mandatory_failure_propagates(self) -> None:
        kit = self.fx.root / "failing-kit"
        cloned = self.fx.run(["git", "clone", "--no-hardlinks", "--local", str(ROOT), str(kit)])
        self.assertEqual(cloned.returncode, 0, cloned.stderr)
        self.fx.run(["git", "-C", str(kit), "config", "user.name", "Client Test"])
        self.fx.run(["git", "-C", str(kit), "config", "user.email", "client@example.invalid"])
        prepare_script = kit / "_ask/skills/prepare-skills.sh"
        prepare_script.write_text("#!/bin/sh\necho fixture failure >&2\nexit 47\n", encoding="utf-8")
        prepare_script.chmod(0o755)
        self.fx.run(["git", "-C", str(kit), "add", "_ask/skills/prepare-skills.sh"])
        self.fx.run(["git", "-C", str(kit), "commit", "-qm", "failing prepare fixture"])

        client = self.fx.git_project(self.fx.root / "install-client")
        install = self.fx.run(
            [str(kit / "_ask/scripts/install-kit.sh"), "--force", str(client)]
        )
        self.assertNotEqual(install.returncode, 0, "install reported success after required prepare failed")
        self.assertNotIn("install-kit: applied", install.stdout)

        bootstrap_client = self.fx.git_project(self.fx.root / "bootstrap-client")
        bootstrap = self.fx.run(
            ["bash", str(kit / "_ask/scripts/askit-bootstrap.sh")], cwd=bootstrap_client,
            env=self.fx.env | {"ASKIT_KIT_ROOT": str(kit), "ASKIT_INSTALL_FLAGS": "--force"},
        )
        self.assertNotEqual(bootstrap.returncode, 0, "bootstrap reported success after prepare failed")
        self.assertNotIn("askit: done", bootstrap.stdout)

        source_commit = self.fx.run(["git", "rev-parse", "HEAD"], cwd=kit).stdout.strip()
        upgrade_client = self.fx.git_project(self.fx.root / "upgrade-failure-client")
        upgrade = self.fx.run(
            [str(kit / "_ask/scripts/upgrade-kit.sh"), "--version", source_commit,
             "--source", str(kit), "--target", str(upgrade_client)],
            cwd=upgrade_client,
        )
        self.assertNotEqual(upgrade.returncode, 0, "upgrade reported success after prepare failed")
        self.assertNotIn("upgrade-kit: refreshed", upgrade.stdout)


if __name__ == "__main__":
    unittest.main()
