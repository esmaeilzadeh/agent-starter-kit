"""Document admission through the public model commands."""
import json
from pathlib import Path
import tempfile
import unittest

from engineering_fixture import model_command, referenced_model, write_json
import copy
import sys
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import os
import shutil
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from engineering_model.actions import run_action, edit
from engineering_model.admission import admit, load_published


class DocumentGuardTests(unittest.TestCase):
    def test_public_mutators_cannot_bypass_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = Path(__file__).resolve().parents[2]
            shutil.copytree(source / "_ask/scripts", root / "_ask/scripts", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(source / ".agents/ask/verification", root / ".agents/ask/verification", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy2(source / "ask", root / "ask")
            def git(*arguments):
                return subprocess.check_output(["git", *arguments], cwd=root, text=True, stderr=subprocess.PIPE).strip()
            git("init", "-q", "-b", "agent/pilot")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.com")
            (root / ".gitignore").write_text("__pycache__/\nwork/pilot/traceability/\nverification-result.json\n", encoding="utf-8")
            model, _spec = referenced_model(root)
            before, errors = admit(root, "pilot")
            self.assertEqual(errors, [])
            model["nodes"] = []
            write_json(root, "work/pilot/engineering-model.json", model)
            (root / "work/pilot/plan.md").write_text("# Plan\n", encoding="utf-8")
            (root / ".agents/verification.yaml").write_text("schema: ask-checkplan/v1\nno_production_datastore: true\nchecks:\n  - command: 'false'\n    tier: mandatory\n", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "invalid adopted fixture")
            sha = git("rev-parse", "HEAD")
            marker = root / "action-marker"
            commands = [
                ["verify"],
                ["record-result", "--work-id", "pilot", "--commit-sha", sha, "--result", "pass"],
                ["check-workstream", "pilot", "--acceptance"],
                ["inner-loop", "run", "pilot"], ["inner-loop", "resume", "pilot"],
                ["inner-loop", "integrate", "--task-ref", "HEAD"],
                ["traceability", "record-review", "pilot", "--candidate-sha", sha,
                 "--recorded-by", "coordinator", "--evidence", "must-not-be-read.json"],
                ["traceability", "check-acceptance", "pilot"],
                ["model", "admit", "--work-id", "pilot", "--action", "review", "--",
                 sys.executable, "-c", "from pathlib import Path; Path('action-marker').write_text('ran')"],
                ["model", "edit", "--work-id", "pilot", "--expected", before.identity["digest"],
                 "--batch", "must-not-be-read.json"],
            ]
            environment = {k: v for k, v in os.environ.items() if not k.startswith(("ASK_", "VERIFY_"))}
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            for command in commands:
                process = subprocess.run([str(root / "ask"), *command], cwd=root, env=environment,
                                         capture_output=True, text=True)
                self.assertNotEqual(process.returncode, 0, command)
                self.assertIn("EM001_INTENT_COUNT", process.stdout + process.stderr,
                              f"{command} bypassed shared document admission: {process.stdout}{process.stderr}")
                self.assertFalse(marker.exists(), command)
                self.assertEqual(load_published(root, "pilot").identity, before.identity)

    def test_successful_guard_order_and_identities(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            referenced_model(root)
            before, errors = admit(root, "pilot")
            self.assertEqual(errors, [])
            batch = write_json(root, "proposal.json", {"commands": [{"op": "resolve_decision", "id": "choice",
                "option_id": "one", "actor": "Developer", "rationale": "Measured fit"}],
                "files": {"specs/current/pilot.md": "# Coordinated choice\n"}})
            changed = model_command(root, "edit", "--work-id", "pilot", "--expected", before.identity["digest"], "--batch", str(batch))
            self.assertEqual(changed.returncode, 0, changed.stderr)
            receipt = json.loads(changed.stdout)
            self.assertEqual(receipt["steps"], ["pre", "action", "post", "publication"])
            self.assertEqual(receipt["input_snapshot"], before.identity)
            after = load_published(root, "pilot")
            self.assertEqual(receipt["snapshot"], after.identity)
            self.assertNotEqual(before.identity["digest"], after.identity["digest"])
            self.assertEqual(after.document["revision"], 2)
            self.assertEqual(after.files["specs/current/pilot.md"], b"# Coordinated choice\n")
            # The action receipt and one semantic revision do not hide a second
            # full post-check. Recovery must validate its captured candidate,
            # not recapture/validate a second independently read document set.
            self.assertEqual(receipt.get("validation_counts"), {"pre": 1, "post": 1})

    def test_cached_and_full_validation_agree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            for mutation in (None, "duplicate", "missing", "restored"):
                if mutation == "duplicate":
                    broken = copy.deepcopy(model)
                    broken["nodes"].append(copy.deepcopy(broken["nodes"][0]))
                    write_json(root, "work/pilot/engineering-model.json", broken)
                elif mutation == "missing":
                    write_json(root, "work/pilot/engineering-model.json", model)
                    (root / "specs/current/pilot.json").unlink()
                elif mutation == "restored":
                    write_json(root, "specs/current/pilot.json", spec)
                ordinary = model_command(root, "validate", "--work-id", "pilot")
                full = model_command(root, "validate", "--work-id", "pilot", "--full")
                self.assertEqual(full.returncode, ordinary.returncode, full.stderr)
                self.assertEqual(json.loads(full.stdout), json.loads(ordinary.stdout))

    def test_external_changes_and_missed_events_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            initial = model_command(root, "watch", "--work-id", "pilot", "--once")
            self.assertEqual(initial.returncode, 0, initial.stderr)
            identity = json.loads(initial.stdout)["snapshot"]["digest"]
            spec["criteria"] = []
            write_json(root, "specs/current/pilot.json", spec)
            observed = model_command(root, "watch", "--work-id", "pilot", "--once")
            self.assertEqual(observed.returncode, 1, observed.stderr)
            self.assertFalse(json.loads(observed.stdout)["valid"])
            # No observer runs for the next external save; read/action startup
            # must still refresh, never reuse a cached good receipt.
            _model, spec = referenced_model(root)
            model_command(root, "admit", "--work-id", "pilot")
            spec["criteria"] = []
            write_json(root, "specs/current/pilot.json", spec)
            shown = json.loads(model_command(root, "show", "--work-id", "pilot").stdout)
            self.assertFalse(shown["editable"])
            self.assertEqual(shown["snapshot"]["digest"], identity)
            calls = []
            result = run_action(root, "pilot", identity, lambda snapshot: calls.append(snapshot))
            self.assertFalse(result["valid"])
            self.assertEqual(calls, [])

    def test_invalid_candidate_preserves_stable_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, _spec = referenced_model(root)
            admitted = json.loads(model_command(root, "admit", "--work-id", "pilot").stdout)
            identity = admitted["snapshot"]["digest"]
            batch = write_json(root, "proposal.json", {"commands": [
                {"op": "add_node", "node": {"id": "orphan", "type": "task", "title": "Orphan", "lifecycle": "planned"}}]})
            before = {p: (root / p).read_bytes() for p in ("work/pilot/engineering-model.json", "specs/current/pilot.json", "specs/current/pilot.md")}
            refused = model_command(root, "edit", "--work-id", "pilot", "--expected", identity, "--batch", str(batch))
            self.assertEqual(refused.returncode, 1, refused.stderr)
            result = json.loads(refused.stdout)
            self.assertIn("EM001_PARENT_COUNT", {e["code"] for e in result["diagnostics"]})
            self.assertEqual(result["steps"], ["pre", "action", "post"])
            self.assertEqual({p: (root / p).read_bytes() for p in before}, before)
            shown = json.loads(model_command(root, "show", "--work-id", "pilot").stdout)
            self.assertEqual(shown["snapshot"]["digest"], identity)
            self.assertEqual(shown["model"], model)

    def test_invalid_prestate_prevents_action(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            admitted = model_command(root, "admit", "--work-id", "pilot")
            identity = json.loads(admitted.stdout)["snapshot"]["digest"]
            model["nodes"] = []
            write_json(root, "work/pilot/engineering-model.json", model)
            before = (root / "work/pilot/engineering-model.json").read_bytes()
            # A nonexistent proposal must never be opened in an invalid prestate.
            blocked = model_command(root, "edit", "--work-id", "pilot", "--expected", identity,
                                    "--batch", "must-not-be-read.json")
            self.assertEqual(blocked.returncode, 1, "invalid prestate must produce an admission refusal")
            result = json.loads(blocked.stdout)
            self.assertIn("EM001_INTENT_COUNT", {e["code"] for e in result["diagnostics"]})
            self.assertNotIn("EM002_ACTION", {e["code"] for e in result["diagnostics"]})
            self.assertEqual(result["steps"], ["pre"])
            self.assertEqual((root / "work/pilot/engineering-model.json").read_bytes(), before)

    def test_linked_spec_change_invalidates_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            admitted = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(admitted.returncode, 0, admitted.stderr)
            old_digest = json.loads(admitted.stdout)["snapshot"]["digest"]
            raw_model = (root / "work/pilot/engineering-model.json").read_bytes()

            # A valid linked-Markdown-only edit invalidates a displayed identity.
            (root / "specs/current/pilot.md").write_text("# Amended pilot\n", encoding="utf-8")
            stale = model_command(root, "admit", "--work-id", "pilot", "--expected", old_digest)
            self.assertEqual(stale.returncode, 1, stale.stderr)
            self.assertIn("EM007_STALE_INPUT", {e["code"] for e in json.loads(stale.stdout)["diagnostics"]})
            refreshed = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(refreshed.returncode, 0, refreshed.stderr)
            self.assertNotEqual(json.loads(refreshed.stdout)["snapshot"]["digest"], old_digest)
            self.assertEqual((root / "work/pilot/engineering-model.json").read_bytes(), raw_model)

            # Finding an ID in arbitrary JSON is not canonical definition validity.
            spec["schema"] = "not-a-spec"
            write_json(root, "specs/current/pilot.json", spec)
            malformed = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(malformed.returncode, 1, "canonical schema must be checked, not just selected ID existence")
            self.assertTrue(any(e["path"] == "specs/current/pilot.json" for e in json.loads(malformed.stdout)["diagnostics"]))

            target = root / "specs/current/pilot.json"
            target.unlink()
            deleted = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(deleted.returncode, 1, deleted.stderr)
            spec["schema"] = "ask-spec/v1"
            write_json(root, "specs/current/pilot.json", spec)
            created = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(created.returncode, 0, created.stderr)

    def test_bootstrap_admits_only_validated_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            admitted = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(admitted.returncode, 0, admitted.stderr)
            receipt = json.loads(admitted.stdout)
            self.assertTrue(receipt["valid"])
            identity = receipt["snapshot"]["digest"]
            shown = model_command(root, "show", "--work-id", "pilot")
            self.assertEqual(shown.returncode, 0, shown.stderr)
            projection = json.loads(shown.stdout)
            self.assertEqual(projection["snapshot"]["digest"], identity)
            self.assertEqual(projection["model"], model)
            self.assertTrue(projection["editable"])

            spec["criteria"] = []
            write_json(root, "specs/current/pilot.json", spec)
            blocked = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(blocked.returncode, 1, blocked.stderr)
            self.assertFalse(json.loads(blocked.stdout)["valid"])
            # An invalid external save cannot replace the last stable snapshot.
            shown = model_command(root, "show", "--work-id", "pilot")
            self.assertEqual(shown.returncode, 1, shown.stderr)
            projection = json.loads(shown.stdout)
            self.assertEqual(projection["snapshot"]["digest"], identity)
            self.assertEqual(projection["model"], model)
            self.assertFalse(projection["editable"])
            self.assertTrue(projection["last_validated"])

            # A current workspace does not make altered generation bytes trusted.
            _model, original_spec = referenced_model(root)
            generation = root / "work/pilot/traceability/model-state/generations" / identity
            blob = generation / "blobs" / receipt["snapshot"]["model"]["sha256"]
            blob.write_bytes(b"{}")
            corrupted = model_command(root, "show", "--work-id", "pilot")
            self.assertEqual(corrupted.returncode, 1, "a corrupt stored generation must not be reused as valid")
            self.assertFalse(json.loads(corrupted.stdout)["editable"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model, spec = referenced_model(root)
            model["nodes"] = []
            write_json(root, "work/pilot/engineering-model.json", model)
            blocked = model_command(root, "admit", "--work-id", "pilot")
            self.assertEqual(blocked.returncode, 1, blocked.stderr)
            shown = model_command(root, "show", "--work-id", "pilot")
            self.assertEqual(shown.returncode, 1, shown.stderr)
            self.assertIsNone(json.loads(shown.stdout)["snapshot"])
