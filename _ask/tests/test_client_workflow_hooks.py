"""Client journeys for installing and updating AskIt session hooks."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from client_security_fixtures import ROOT


class ClientWorkflowHooksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="askit-client-hooks-")
        self.root = Path(self.temporary.name)
        self.kit = ROOT

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd or self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def client(self, name: str) -> Path:
        target = self.root / name
        target.mkdir()
        self.git("init", "-q", str(target))
        self.git("config", "user.name", "AskIt test", cwd=target)
        self.git("config", "user.email", "askit-test@example.invalid", cwd=target)
        (target / "README.md").write_text("client\n", encoding="utf-8")
        self.git("add", "README.md", cwd=target)
        self.git("commit", "-qm", "client seed", cwd=target)
        return target

    def install(self, target: Path, *flags: str, source: Path | None = None) -> subprocess.CompletedProcess[str]:
        source = source or self.kit
        return subprocess.run(
            ["bash", str(source / "_ask/scripts/install-kit.sh"), *flags, str(target)],
            capture_output=True,
            text=True,
        )

    def invoke_cursor(self, target: Path) -> dict:
        handlers = json.loads((target / ".cursor/hooks.json").read_text())["hooks"]["sessionStart"]
        command = next(item["command"] for item in handlers if "access-preflight.sh" in item["command"])
        result = subprocess.run(command, shell=True, cwd=target, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def invoke_codex(self, target: Path) -> dict:
        handlers = json.loads((target / ".codex/hooks.json").read_text())["hooks"]["SessionStart"]
        hook = next(item for item in handlers if any(
            "session-start.py" in entry.get("command", "") for entry in item.get("hooks", [])))
        command = hook["hooks"][0]["command"]
        result = subprocess.run(command, shell=True, cwd=target / "nested", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def assert_loaded(self, target: Path) -> None:
        cursor = self.invoke_cursor(target)["additional_context"]
        codex = self.invoke_codex(target)["hookSpecificOutput"]["additionalContext"]
        for context in (cursor, codex):
            self.assertIn("AskIt session instructions", context)
            self.assertIn("classify each deliverable", context)
            self.assertIn("project access preflight passed", context)
        self.assertIn(".agents/ask/session.md", (target / ".cursor/rules/starter-kit-bootstrap.mdc").read_text())

    def test_fresh_install_loads_workflow_in_both_runtimes(self) -> None:
        target = self.client("fresh")
        (target / "nested").mkdir()
        self.assertEqual(self.install(target, "--skip-prepare").returncode, 0)
        self.assertFalse((target / "AGENTS.md").exists())
        self.assert_loaded(target)

        (target / "ask").write_text("#!/bin/sh\necho 'write denied at .git' >&2\nexit 1\n", encoding="utf-8")
        (target / "ask").chmod(0o755)
        failures = (
            self.invoke_cursor(target)["additional_context"],
            self.invoke_codex(target)["hookSpecificOutput"]["additionalContext"],
        )
        for failure in failures:
            self.assertIn("write denied at .git", failure)
            self.assertIn("STOP:", failure)

    def test_reinstall_preserves_client_instructions_and_hooks(self) -> None:
        target = self.client("existing")
        (target / "nested").mkdir()
        agents = "# Client instructions\n"
        (target / "AGENTS.md").write_text(agents)
        cursor_config = {
            "version": 1,
            "hooks": {"sessionStart": [{"command": "client-cursor-hook"}],
                      "afterFileEdit": [{"command": "client-format-hook"}]},
        }
        codex_config = {
            "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "client-codex-hook"}]}],
                      "PostToolUse": [{"matcher": "Write", "hooks": [{"type": "command", "command": "client-review-hook"}]}]},
        }
        (target / ".cursor").mkdir()
        (target / ".cursor/hooks.json").write_text(json.dumps(cursor_config))
        (target / ".codex").mkdir()
        (target / ".codex/hooks.json").write_text(json.dumps(codex_config))
        for flags in (("--skip-prepare",), ("--force", "--skip-prepare")):
            result = self.install(target, *flags)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((target / "AGENTS.md").read_text(), agents)
        cursor_after = json.loads((target / ".cursor/hooks.json").read_text())
        codex_after = json.loads((target / ".codex/hooks.json").read_text())
        self.assertEqual(cursor_after["hooks"]["afterFileEdit"], cursor_config["hooks"]["afterFileEdit"])
        self.assertEqual(codex_after["hooks"]["PostToolUse"], codex_config["hooks"]["PostToolUse"])
        self.assertEqual(cursor_after["hooks"]["sessionStart"][0], cursor_config["hooks"]["sessionStart"][0])
        self.assertEqual(codex_after["hooks"]["SessionStart"][0], codex_config["hooks"]["SessionStart"][0])
        self.assertEqual(sum(item["command"] != "client-cursor-hook" for item in cursor_after["hooks"]["sessionStart"]), 1)
        self.assertEqual(sum(item["hooks"][0]["command"] != "client-codex-hook" for item in codex_after["hooks"]["SessionStart"]), 1)
        self.assert_loaded(target)

    def test_malformed_hook_configuration_aborts_install(self) -> None:
        target = self.client("malformed")
        prior = b'{"hooks": {"SessionStart": "invalid"}}'
        (target / ".codex").mkdir()
        (target / ".codex/hooks.json").write_bytes(prior)
        result = self.install(target, "--skip-prepare")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hook", (result.stderr + result.stdout).lower())
        self.assertEqual((target / ".codex/hooks.json").read_bytes(), prior)
        self.assertFalse((target / "ask").exists())

    def test_upgrade_registers_hooks_for_previous_release_clients(self) -> None:
        target = self.client("upgrade")
        (target / "nested").mkdir()
        (target / "AGENTS.md").write_text("# Client-owned\n")
        cursor_config = {
            "version": 1,
            "hooks": {"sessionStart": [{"command": "client-cursor-hook"}],
                      "afterFileEdit": [{"command": "client-format-hook"}]},
        }
        codex_config = {
            "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "client-codex-hook"}]}],
                      "PostToolUse": [{"matcher": "Write", "hooks": [{"type": "command", "command": "client-review-hook"}]}]},
        }
        (target / ".cursor").mkdir()
        (target / ".cursor/hooks.json").write_text(json.dumps(cursor_config))
        (target / ".codex").mkdir()
        (target / ".codex/hooks.json").write_text(json.dumps(codex_config))
        previous = self.root / "previous"
        fetched = subprocess.run(
            ["git", "clone", "--quiet", "--shared", str(self.kit), str(previous)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(fetched.returncode, 0, fetched.stderr)
        self.git("checkout", "--quiet", "v2.0.1", cwd=previous)
        installed = self.install(target, "--skip-prepare", source=previous)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        version = self.git("rev-parse", "HEAD", cwd=self.kit)
        for _ in range(2):
            upgraded = subprocess.run(
                ["bash", str(self.kit / "_ask/scripts/upgrade-kit.sh"), "--version", version,
                 "--expected-commit", version, "--source", str(self.kit), "--target", str(target), "--skip-prepare"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(upgraded.returncode, 0, upgraded.stderr)
        self.assertEqual((target / "AGENTS.md").read_text(), "# Client-owned\n")
        cursor_after = json.loads((target / ".cursor/hooks.json").read_text())
        codex_after = json.loads((target / ".codex/hooks.json").read_text())
        self.assertEqual(cursor_after["hooks"]["afterFileEdit"], cursor_config["hooks"]["afterFileEdit"])
        self.assertEqual(codex_after["hooks"]["PostToolUse"], codex_config["hooks"]["PostToolUse"])
        self.assertEqual(cursor_after["hooks"]["sessionStart"][0], cursor_config["hooks"]["sessionStart"][0])
        self.assertEqual(codex_after["hooks"]["SessionStart"][0], codex_config["hooks"]["SessionStart"][0])
        self.assertEqual(sum("access-preflight.sh" in item["command"]
                             for item in cursor_after["hooks"]["sessionStart"]), 1)
        self.assertEqual(sum(any("session-start.py" in hook.get("command", "")
                                 for hook in item.get("hooks", []))
                             for item in codex_after["hooks"]["SessionStart"]), 1)
        self.assertTrue((target / ".codex/hooks.json").is_file(),
                        f"Codex session hook was not installed by upgrade: {upgraded.stdout} {upgraded.stderr}")
        self.assert_loaded(target)
