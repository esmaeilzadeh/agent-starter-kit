"""Public-command journeys for client trust and model routing."""

from __future__ import annotations

import unittest
import json
import hashlib
import shutil
from pathlib import Path

from client_security_fixtures import ClientFixture, ROOT


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = ClientFixture()

    def tearDown(self) -> None:
        self.fx.close()

    def test_client_upgrade_journey(self) -> None:
        """Public install, upgrade, recovery and verify preserve client trust."""
        failures: list[str] = []
        client = self.fx.git_project(self.fx.root / "client")
        settings = client / "_ask/bindings/models.yaml"
        settings.parent.mkdir(parents=True)
        settings.write_text("risk: HIGH\ncodex:\n  07-review: gpt-6-astra\n", encoding="utf-8")
        legacy = client / ".ask.env"
        legacy.write_text(
            "ASK_TRACKER=github\nASK_TRACKER_URL=https://github.com/example/project\n"
            "TRACKER_TOKEN=dummy-never-real\n",
            encoding="utf-8",
        )
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
        ignored = self.fx.run(["git", "check-ignore", "-q", ".ask.env"], cwd=client)
        self.assertEqual(ignored.returncode, 0, "credential file is not ignored")

        migration = self.fx.run(
            [str(client / "ask"), "credentials", "migrate"], cwd=client, env=env
        )
        credential_id = hashlib.sha256(str(client.resolve()).encode()).hexdigest()
        credentials = (self.fx.config / "askit/projects" / credential_id / "credentials.json")
        if migration.returncode:
            failures.append("public credential migration failed: "
                            + (migration.stderr or migration.stdout).splitlines()[0])
        if not credentials.exists():
            failures.append("migration did not create private external credentials")
        else:
            self.assertEqual(json.loads(credentials.read_text(encoding="utf-8")),
                             {"TRACKER_TOKEN": "dummy-never-real"})
            self.assertEqual(credentials.stat().st_mode & 0o777, 0o600)
            self.assertEqual(credentials.parent.stat().st_mode & 0o777, 0o700)
        migrated_env = legacy.read_text(encoding="utf-8")
        if "dummy-never-real" in migrated_env:
            failures.append("legacy secret remained in the active worktree after migration")
        self.assertIn("ASK_TRACKER=github", migrated_env)
        self.assertIn("ASK_TRACKER_URL=https://github.com/example/project", migrated_env)
        if "rotate" not in (migration.stdout + migration.stderr).lower():
            failures.append("migration did not warn about rotating the legacy token")
        self.assertNotIn("dummy-never-real", migration.stdout + migration.stderr)

        verify = self.fx.run([str(client / "ask"), "verify"], cwd=client, env=env)
        if verify.returncode:
            details = (verify.stderr or verify.stdout).splitlines()
            failures.append("trusted verifier did not complete: " + "; ".join(details[:2]))
        self.assertNotIn("dummy-never-real", verify.stdout + verify.stderr)

        marker = self.fx.root / "untrusted-upgrade-ran"
        untrusted = self.fx.make_untrusted_source(marker)
        attack_client = self.fx.git_project(self.fx.root / "attack-client")
        attack_install = self.fx.run(
            [str(ROOT / "ask"), "install", "--skip-prepare", str(attack_client)], cwd=attack_client
        )
        self.assertEqual(attack_install.returncode, 0, attack_install.stderr)
        rejected_upgrade = self.fx.run(
            [str(attack_client / "ask"), "upgrade", "--version", "main", "--source", str(untrusted)],
            cwd=attack_client,
            env={**env, "ASKIT_TEST_MARKER": str(marker)},
        )
        if rejected_upgrade.returncode == 0:
            failures.append("untrusted upgrade was accepted")
        if marker.exists():
            failures.append("untrusted upgrade helper executed")
            marker.unlink()

        launcher = self.fx.install_launcher()

        # Kill an upgrade after it replaces the first kit tree; the installed
        # launcher must recover the transaction before project delegation.
        source = self.fx.root / "upgrade-source"
        clone = self.fx.run(["git", "clone", "-q", "--shared", str(ROOT), str(source)])
        self.assertEqual(clone.returncode, 0, clone.stderr)
        self.assertEqual(self.fx.run(["git", "-C", str(source), "checkout", "-qb", "main"]).returncode, 0)
        changed_source = source / "_ask/skills/prepare-skills.sh"
        changed_source.write_text(changed_source.read_text(encoding="utf-8") + "\n# upgrade fixture\n",
                                 encoding="utf-8")
        self.assertEqual(self.fx.run(["git", "-C", str(source), "add", "_ask/skills/prepare-skills.sh"]).returncode, 0)
        self.assertEqual(self.fx.run(["git", "-C", str(source), "commit", "-qm", "test upgrade source"]).returncode, 0)
        original_kit_file = client / "_ask/skills/prepare-skills.sh"
        original_kit_bytes = original_kit_file.read_bytes()
        kill_bin = self.fx.root / "kill-bin"
        kill_bin.mkdir()
        cp = shutil.which("cp")
        self.assertIsNotNone(cp)
        cp_shim = kill_bin / "cp"
        cp_shim.write_text(
            "#!/bin/sh\n"
            f"'{cp}' \"$@\" || exit $?\n"
            "case \" $* \" in *\"$ASKIT_TEST_KILL_TARGET\"*) "
            "if [ ! -e \"$ASKIT_TEST_KILL_MARKER\" ]; then "
            ": > \"$ASKIT_TEST_KILL_MARKER\"; kill -KILL \"$PPID\"; fi;; esac\n",
            encoding="utf-8",
        )
        cp_shim.chmod(0o755)
        kill_env = env | {
            "PATH": f"{kill_bin}:{env['PATH']}",
            "ASKIT_TEST_KILL_TARGET": str(client / "_ask/skills"),
            "ASKIT_TEST_KILL_MARKER": str(self.fx.root / "upgrade-killed"),
        }
        interrupted = self.fx.run(
            [str(client / "ask"), "upgrade", "--version", "main", "--source", str(source),
             "--skip-prepare"], cwd=client, env=kill_env,
        )
        if not (self.fx.root / "upgrade-killed").exists():
            failures.append("upgrade fault injection did not kill at publish: "
                            + interrupted.stdout + interrupted.stderr)
        elif interrupted.returncode != -9:
            failures.append(f"publish fault returned {interrupted.returncode}, expected SIGKILL")
        recovered = self.fx.run([str(launcher), "verify"], cwd=client, env=self.fx.env)
        if recovered.returncode:
            details = (recovered.stderr or recovered.stdout).splitlines()
            failures.append("installed launcher recovery failed: " + "; ".join(details[:2]))
        if original_kit_file.read_bytes() != original_kit_bytes:
            failures.append("installed launcher did not restore interrupted upgrade bytes")
        self.assertEqual(migrated.read_bytes(), settings.read_bytes())
        if credentials.exists():
            self.assertEqual(json.loads(credentials.read_text(encoding="utf-8")),
                             {"TRACKER_TOKEN": "dummy-never-real"})
        self.assertEqual((client / "README.md").read_bytes(), readme)

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
        if dispatcher_marker.exists():
            failures.append("global launcher executed untrusted project code")
            dispatcher_marker.unlink()
        self.assertEqual(completion.returncode, 0, completion.stderr)
        if daily.returncode == 0:
            failures.append("global launcher accepted an untrusted project command")

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
        if fetch.returncode == 0:
            failures.append("new source ran without an approval")
        if marker.exists():
            failures.append("untrusted downloaded helper executed")
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
        if rejected.returncode == 0:
            failures.append("unsafe symlink destination was accepted")
        if "_ask/scripts" not in rejected.stderr + rejected.stdout:
            failures.append("symlink refusal did not identify the unsafe path")
        if sentinel.read_text(encoding="utf-8") != "keep\n":
            failures.append("unsafe symlink install changed the outside sentinel")
        self.assertFalse(failures, "\n".join(failures))

    def test_model_flow_journey(self) -> None:
        """One Grill submission is reused and gates public implementation dispatch."""
        checkout = self.fx.root / "checkout"
        clone = self.fx.run(["git", "clone", "-q", "--shared", str(ROOT), str(checkout)])
        self.assertEqual(clone.returncode, 0, clone.stderr)
        models = checkout / "work/model-flow/models.yaml"
        models.parent.mkdir(parents=True, exist_ok=True)
        env = self.fx.env.copy()
        env["ASK_WORK_ID"] = "model-flow"
        adapter, adapter_log, adapter_config = self.fx.fake_model_runtime()
        env["ASK_MODEL_RUNTIME_ADAPTER"] = str(adapter)
        env["ASK_MODEL_RUNTIME_LOG"] = str(adapter_log)
        env["ASK_MODEL_RUNTIME_CONFIG"] = str(adapter_config)
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
                            + (saved.stderr or saved.stdout).splitlines()[0])
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
            ("05-plan", "gpt-6-luna"),
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
        if (checkout / "work/model-flow/acceptance.md").exists():
            failures.append("model confirmation was mistaken for final workstream acceptance")

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
        helpers = Path(__file__).resolve().with_name("traceability_support.py")
        for operation in ("seed",):
            prepared = self.fx.run(["python3", str(helpers), operation, str(loop_checkout), "model-flow"],
                                   cwd=loop_checkout, env=self.fx.env)
            self.assertEqual(prepared.returncode, 0, prepared.stderr + prepared.stdout)
        git("add", ".")
        git("commit", "-qm", "seed disposable model-flow coordinator")
        accepted = self.fx.run(["python3", str(helpers), "accept", str(loop_checkout), "model-flow"],
                               cwd=loop_checkout, env=self.fx.env)
        self.assertEqual(accepted.returncode, 0, accepted.stderr + accepted.stdout)

        handoff_env = self.fx.env.copy()
        handoff_env["ASK_MODEL_RUNTIME_ADAPTER"] = str(adapter)
        handoff_env["ASK_MODEL_RUNTIME_LOG"] = str(adapter_log)
        handoff_env["ASK_MODEL_RUNTIME_CONFIG"] = str(adapter_config)

        runtime = json.loads(adapter_config.read_text(encoding="utf-8"))
        runtime["models"] = ["gpt-6.1-sol", "gpt-6-astra"]
        adapter_config.write_text(json.dumps(runtime), encoding="utf-8")
        unavailable = self.fx.run(
            [str(loop_checkout / "ask"), "inner-loop", "run", "model-flow"],
            cwd=loop_checkout, env=handoff_env,
        )
        state_path = loop_checkout / "work/model-flow/inner-loop/state.json"
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else None
        task_status = (state or {}).get("tasks", {}).get("implementation", {}).get("status", "pending")
        if task_status in {"running", "completed"}:
            failures.append("unavailable implementor model did not escalate before task dispatch")
        if not any(word in (unavailable.stdout + unavailable.stderr).lower()
                   for word in ("unavailable", "accessible", "choose")):
            failures.append("unavailable-model escalation did not name the missing choice")

        runtime["models"] = ["gpt-6.1-sol", "gpt-6-luna", "gpt-6-astra"]
        adapter_config.write_text(json.dumps(runtime), encoding="utf-8")
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
        if task_status in {"running", "completed"}:
            failures.append("implementation task dispatched before the orchestrator handoff was verified: "
                            + dispatch.stdout + dispatch.stderr)
        if "manual" not in (dispatch.stdout + dispatch.stderr).lower():
            failures.append("unsupported orchestrator switch did not stop with a named manual handoff")
        if not any(call.get("action") == "identity" for call in runtime_calls):
            failures.append("the public coordinator did not inspect the fake parent orchestrator identity")
        runtime["identity"] = "gpt-6-luna"
        adapter_config.write_text(json.dumps(runtime), encoding="utf-8")
        resumed = self.fx.run(
            [str(loop_checkout / "ask"), "inner-loop", "resume", "model-flow"],
            cwd=loop_checkout, env=handoff_env,
        )
        resumed_state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else None
        resumed_status = ((resumed_state or {}).get("tasks", {}).get("implementation", {})
                          .get("status", "pending"))
        if resumed.returncode != 0 or resumed_status != "running":
            failures.append("matching parent identity did not resume implementation: "
                            + resumed.stdout + resumed.stderr)
        if (loop_checkout / "work/model-flow/acceptance.md").exists():
            failures.append("model confirmation/resume created final acceptance without an acceptance action")
        self.assertFalse(failures, "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
