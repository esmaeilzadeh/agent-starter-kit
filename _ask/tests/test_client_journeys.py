"""Public-command journeys for client trust and model routing."""

from __future__ import annotations

import unittest
from pathlib import Path

from client_security_fixtures import ClientFixture, ROOT


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = ClientFixture()

    def tearDown(self) -> None:
        self.fx.close()

    def test_client_upgrade_journey(self) -> None:
        """A client install must refuse untrusted code and preserve user data."""
        client = self.fx.git_project(self.fx.root / "client")
        settings = client / ".agents/ask.local/bindings/models.yaml"
        settings.parent.mkdir(parents=True)
        settings.write_text("risk: HIGH\n", encoding="utf-8")
        legacy = client / ".ask.env"
        legacy.write_text("TRACKER_TOKEN=dummy-never-real\n", encoding="utf-8")
        readme = (client / "README.md").read_bytes()

        install = self.fx.run(
            [str(ROOT / "ask"), "install", "--skip-prepare", str(client)], cwd=client
        )
        self.assertEqual(install.returncode, 0, install.stderr)
        self.assertEqual((client / "README.md").read_bytes(), readme)
        self.assertEqual(settings.read_text(encoding="utf-8"), "risk: HIGH\n")
        self.assertEqual(legacy.read_text(encoding="utf-8"), "TRACKER_TOKEN=dummy-never-real\n")

        launcher = self.fx.install_launcher()
        startup_before = {
            name: (self.fx.home / name).read_bytes() if (self.fx.home / name).exists() else None
            for name in (".bashrc", ".zshrc")
        }
        dispatcher_marker = self.fx.root / "project-dispatcher-ran"
        dispatcher = client / "ask"
        dispatcher.write_text(
            "#!/bin/sh\nprintf executed > \"$ASKIT_TEST_MARKER\"\n", encoding="utf-8"
        )
        dispatcher.chmod(0o755)
        env = self.fx.env.copy()
        env["ASKIT_TEST_MARKER"] = str(dispatcher_marker)
        completion = self.fx.run(
            [str(launcher), "--complete", "1", "askit"], cwd=client, env=env
        )
        daily = self.fx.run([str(launcher), "verify"], cwd=client, env=env)
        self.assertFalse(dispatcher_marker.exists(), "global launcher executed project code")
        self.assertEqual(completion.returncode, 0, completion.stderr)
        self.assertNotEqual(daily.returncode, 0, "untrusted project command was not refused")

        marker = self.fx.root / "untrusted-ran"
        untrusted = self.fx.make_untrusted_source(marker)
        env = self.fx.env.copy()
        env.pop("ASKIT_SKIP_COMPLETION_INSTALL", None)
        env["ASKIT_TEST_MARKER"] = str(marker)
        fetch = self.fx.run(
            ["bash", "-s", "--", "--source", str(untrusted), "--ref", "main",
             "--prefix", str(self.fx.root / "untrusted-prefix")],
            cwd=self.fx.root,
            env=env,
            input=(ROOT / "askit").read_text(encoding="utf-8"),
        )
        self.assertNotEqual(fetch.returncode, 0, "new source ran without an approval")
        self.assertFalse(marker.exists(), "untrusted downloaded helper executed")
        self.assertEqual(
            {name: (self.fx.home / name).read_bytes() if (self.fx.home / name).exists() else None
             for name in startup_before},
            startup_before,
            "untrusted source changed shell startup",
        )

        # Force still cannot authorize a destination that escapes through a symlink.
        unsafe = self.fx.git_project(self.fx.root / "unsafe-client")
        victim = self.fx.root / "outside-kit-tree"
        victim.mkdir()
        sentinel = victim / "client-data"
        sentinel.write_text("keep\n", encoding="utf-8")
        (unsafe / "_ask").mkdir()
        (unsafe / "_ask/scripts").symlink_to(victim, target_is_directory=True)
        rejected = self.fx.run(
            [str(ROOT / "ask"), "install", "--force", "--skip-prepare", str(unsafe)],
            cwd=unsafe,
        )
        self.assertNotEqual(rejected.returncode, 0, "unsafe symlink destination was accepted")
        self.assertIn("_ask/scripts", rejected.stderr + rejected.stdout)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_model_flow_journey(self) -> None:
        """Sync projections must carry one decision and saved stage choices."""
        checkout = self.fx.root / "checkout"
        clone = self.fx.run(["git", "clone", "-q", "--shared", str(ROOT), str(checkout)])
        self.assertEqual(clone.returncode, 0, clone.stderr)
        models = checkout / "work/model-flow/models.yaml"
        models.parent.mkdir(parents=True, exist_ok=True)
        models.write_text("risk: HIGH\ncodex:\n  07-review: gpt-6-astra\n", encoding="utf-8")
        env = self.fx.env.copy()
        env["ASK_WORK_ID"] = "model-flow"
        sync = self.fx.run([str(checkout / "ask"), "sync"], cwd=checkout, env=env)
        self.assertEqual(sync.returncode, 0, sync.stderr)

        grill = (checkout / ".agents/ask/stages/01-grill.md").read_text(encoding="utf-8")
        challenge = (checkout / ".agents/ask/stages/03-spec-challenge.md").read_text(encoding="utf-8")
        review = (checkout / ".agents/ask/stages/07-review.md").read_text(encoding="utf-8")
        review_agent = (checkout / ".codex/agents/kit-07-review.toml").read_text(encoding="utf-8")
        self.assertEqual(grill.count("Confirm model plan"), 1)
        self.assertNotIn("Present its model picker", challenge)
        self.assertNotIn("Present the model picker", review)
        self.assertIn('model = "gpt-6-astra"', review_agent)
        self.assertIn("implementation orchestrator", grill.lower())


if __name__ == "__main__":
    unittest.main()
