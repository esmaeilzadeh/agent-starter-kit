"""Public-command journeys for client trust and model routing."""

from __future__ import annotations

import unittest
import json
from pathlib import Path

from client_security_fixtures import ClientFixture, ROOT
from traceability_support import accept as accept_traceability, seed as seed_traceability


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = ClientFixture()

    def tearDown(self) -> None:
        self.fx.close()

    def test_client_upgrade_journey(self) -> None:
        """Public install, upgrade, recovery and verify preserve client trust."""
        client = self.fx.git_project(self.fx.root / "client")
        settings = client / "_ask/bindings/models.yaml"
        settings.parent.mkdir(parents=True)
        settings.write_text("risk: HIGH\ncodex:\n  07-review: gpt-6-astra\n", encoding="utf-8")
        legacy = client / ".ask.env"
        legacy.write_text("TRACKER_TOKEN=dummy-never-real\n", encoding="utf-8")
        legacy.chmod(0o600)
        verification = client / ".agents/verification.yaml"
        verification.parent.mkdir(parents=True)
        verification.write_text(
            "schema: ask-checkplan/v1\ne2e: required\n"
            "no_production_datastore: true\nadapters: []\n"
            "checks:\n  - id: filtered-environment\n    tier: mandatory\n"
            "    command: python3 check-verify-env.py\n",
            encoding="utf-8",
        )
        (client / "check-verify-env.py").write_text(
            "import os\nassert 'TRACKER_TOKEN' not in os.environ\n", encoding="utf-8"
        )
        readme = (client / "README.md").read_bytes()
        env = self.fx.env.copy()
        env["TRACKER_TOKEN"] = "dummy-never-real"

        install = self.fx.run(
            [str(ROOT / "ask"), "install", "--skip-prepare", str(client)], cwd=client, env=env
        )
        self.assertEqual(install.returncode, 0, install.stderr)
        self.assertEqual((client / "README.md").read_bytes(), readme)
        migrated = client / ".agents/ask.local/bindings/models.yaml"
        self.assertEqual(migrated.read_bytes(), settings.read_bytes())
        self.assertEqual(legacy.read_text(encoding="utf-8"), "TRACKER_TOKEN=dummy-never-real\n")
        self.assertEqual(legacy.stat().st_mode & 0o777, 0o600)
        ignored = self.fx.run(["git", "check-ignore", "-q", ".ask.env"], cwd=client)
        self.assertEqual(ignored.returncode, 0, "credential file is not ignored")

        verify = self.fx.run([str(client / "ask"), "verify"], cwd=client, env=env)
        self.assertEqual(verify.returncode, 0, verify.stderr + verify.stdout)
        self.assertNotIn("dummy-never-real", verify.stdout + verify.stderr)

        marker = self.fx.root / "untrusted-upgrade-ran"
        untrusted = self.fx.make_untrusted_source(marker)
        rejected_upgrade = self.fx.run(
            [str(client / "ask"), "upgrade", "--version", "main", "--source", str(untrusted)],
            cwd=client,
            env={**env, "ASKIT_TEST_MARKER": str(marker)},
        )
        self.assertNotEqual(rejected_upgrade.returncode, 0, "untrusted upgrade was accepted")
        self.assertFalse(marker.exists(), "untrusted upgrade helper executed")

        recovered = self.fx.run(
            [str(ROOT / "ask"), "install", "--force", "--skip-prepare", str(client)],
            cwd=client,
            env=env,
        )
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(migrated.read_bytes(), settings.read_bytes())
        self.assertEqual((client / "README.md").read_bytes(), readme)

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
            [str(launcher), "--complete", "1", "askit"], cwd=client,
            env={**env, "ASKIT_TEST_MARKER": str(dispatcher_marker)},
        )
        daily = self.fx.run(
            [str(launcher), "verify"], cwd=client,
            env={**env, "ASKIT_TEST_MARKER": str(dispatcher_marker)},
        )
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
        """One Grill submission is reused and gates public implementation dispatch."""
        checkout = self.fx.root / "checkout"
        clone = self.fx.run(["git", "clone", "-q", "--shared", str(ROOT), str(checkout)])
        self.assertEqual(clone.returncode, 0, clone.stderr)
        models = checkout / "work/model-flow/models.yaml"
        models.parent.mkdir(parents=True, exist_ok=True)
        env = self.fx.env.copy()
        env["ASK_WORK_ID"] = "model-flow"
        adapter, adapter_log = self.fx.fake_model_runtime()
        env["ASK_MODEL_RUNTIME_ADAPTER"] = str(adapter)
        env["ASK_MODEL_RUNTIME_LOG"] = str(adapter_log)
        decision = {
            "runtime": "codex",
            "submission": "confirm",
            "implementation_policy": "latest-accessible",
            "overrides": {"07-review": "gpt-6-astra"},
        }
        failures: list[str] = []
        saved = self.fx.run(
            [str(checkout / "ask"), "model", "decision", "submit", "--work-id", "model-flow"],
            cwd=checkout,
            env=env,
            input=json.dumps(decision),
        )
        if saved.returncode:
            failures.append("Grill submission was not saved through the public model-decision command: "
                            + saved.stderr + saved.stdout)
            # Keep later transition checks independent of the missing save path.
            models.write_text(
                "runtime: codex\nrisk: HIGH\nmodel_plan:\n  status: confirmed\n"
                "  source: grill\n  implementation_policy: latest-accessible\n"
                "codex:\n  07-review: gpt-6-astra\n",
                encoding="utf-8",
            )
        saved_record = models.read_text(encoding="utf-8")
        if not all(value in saved_record for value in
                   ("status: confirmed", "source: grill", "07-review: gpt-6-astra")):
            failures.append("saved Grill decision lost its confirmation or exact stage exception")
        sync = self.fx.run([str(checkout / "ask"), "sync"], cwd=checkout, env=env)
        if sync.returncode:
            failures.append("sync failed after the saved model decision: " + sync.stderr)

        grill = (checkout / ".agents/ask/stages/01-grill.md").read_text(encoding="utf-8")
        challenge = (checkout / ".agents/ask/stages/03-spec-challenge.md").read_text(encoding="utf-8")
        review = (checkout / ".agents/ask/stages/07-review.md").read_text(encoding="utf-8")
        review_agent = (checkout / ".codex/agents/kit-07-review.toml").read_text(encoding="utf-8")
        for stage, expected in (
            ("03-spec-challenge", "gpt-6-astra"),
            ("05-plan", "gpt-6.1-sol"),
            ("06-implement", "gpt-6-luna"),
            ("07-review", "gpt-6-astra"),
            ("continuation", "gpt-6.1-sol"),
        ):
            resolved = self.fx.run(
                [str(checkout / "ask"), "model", "decision", "resolve",
                 "--work-id", "model-flow", "--stage", stage],
                cwd=checkout,
                env=env,
            )
            if resolved.returncode or resolved.stdout.strip() != expected:
                failures.append(f"{stage} did not reuse {expected}: {resolved.stderr}{resolved.stdout}")

        if grill.count("Confirm model plan") != 1:
            failures.append("Grill does not offer exactly one model-plan confirmation")
        if "Present its model picker" in challenge or "Present the model picker" in review:
            failures.append("Challenge or Review still asks for a routine model picker")
        if 'model = "gpt-6-astra"' not in review_agent:
            failures.append("the saved Review exception did not reach its generated agent")
        if "implementation orchestrator" not in grill.lower():
            failures.append("Grill omits the implementation orchestrator policy")

        loop_checkout = self.fx.root / "coordinator"
        clone = self.fx.run(["git", "clone", "-q", "--shared", str(ROOT), str(loop_checkout)])
        self.assertEqual(clone.returncode, 0, clone.stderr)

        def git(*args: str) -> None:
            proc = self.fx.run(["git", "-C", str(loop_checkout), *args], cwd=loop_checkout)
            self.assertEqual(proc.returncode, 0, proc.stderr)

        git("checkout", "-qb", "agent/model-flow")
        graph = loop_checkout / "work/model-flow/inner-loop/tasks.yaml"
        graph.parent.mkdir(parents=True, exist_ok=True)
        graph.write_text(
            "schema: ask-inner-loop-tasks/v1\nwork_id: model-flow\ntasks:\n"
            "  - id: implementation\n    depends_on: []\n    owned_paths: [src/**]\n",
            encoding="utf-8",
        )
        loop_models = loop_checkout / "work/model-flow/models.yaml"
        loop_models.write_text(saved_record, encoding="utf-8")
        seed_traceability(loop_checkout, "model-flow")
        git("add", ".")
        git("commit", "-qm", "seed disposable model-flow coordinator")
        accept_traceability(loop_checkout, "model-flow")

        handoff_env = self.fx.env.copy()
        handoff_env["ASK_MODEL_RUNTIME_ADAPTER"] = str(adapter)
        handoff_env["ASK_MODEL_RUNTIME_LOG"] = str(adapter_log)
        dispatch = self.fx.run(
            [str(loop_checkout / "ask"), "inner-loop", "run", "model-flow"],
            cwd=loop_checkout,
            env=handoff_env,
        )
        state_path = loop_checkout / "work/model-flow/inner-loop/state.json"
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else None
        task_status = (state or {}).get("tasks", {}).get("implementation", {}).get("status", "pending")
        runtime_calls = [json.loads(line) for line in adapter_log.read_text(encoding="utf-8").splitlines()] \
            if adapter_log.exists() else []
        if dispatch.returncode == 0 or task_status != "pending":
            failures.append("implementation task dispatched before the orchestrator handoff was verified: "
                            + dispatch.stdout + dispatch.stderr)
        if "manual" not in (dispatch.stdout + dispatch.stderr).lower():
            failures.append("unsupported orchestrator switch did not stop with a named manual handoff")
        if not any(call.get("action") == "identity" for call in runtime_calls):
            failures.append("the public coordinator did not inspect the fake parent orchestrator identity")
        self.assertFalse(failures, "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
