"""RWB-103 subject resolution and adopted initial-stage intake contracts."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from _ask.tests.test_revising_context import _repo, _put


class ContextResolverTests(unittest.TestCase):
    def test_explicit_recorded_conflicting_and_unavailable_subjects(self):
        try:
            from _ask.scripts.engineering_model.context import resolve
        except ImportError:
            resolve = None
        self.assertTrue(callable(resolve), "shared read-only subject resolver must be public")
        if not callable(resolve):
            return
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            association = {
                "subject": {"work_id": "product", "node_id": "story"},
                "revision": "snapshot", "contribution": "Implement parser",
                "exclusions": ["UI redesign"], "execution_owner": {"work_id": "product", "task_id": "WB-003"},
                "snapshot_digest": "a" * 64,
                "history": [{"actor": "human", "rationale": "Confirmed subject", "timestamp": "2026-10-16T00:00:00Z"}],
            }
            doc_path = root / "work/product/engineering-model.json"
            document = json.loads(doc_path.read_text())
            document["subject_association"] = association
            _put(root, "work/product/engineering-model.json", document)
            explicit = resolve(root, "product", {"explicit_subjects": [{"work_id": "other", "node_id": "story-x"}]})
            self.assertEqual(explicit["subject"], {"work_id": "other", "node_id": "story-x"},
                             "an explicit qualified subject overrides recorded association")
            self.assertEqual(explicit["source"], "explicit-request")
            self.assertEqual(explicit["disposition"], "unavailable",
                             "a foreign owner is not claimed resolved without its captured owning model")
            self.assertEqual(explicit["external_context"]["state"], "unavailable")
            explicit_details = resolve(root, "product", {
                "explicit_subjects": [{"work_id": "product", "node_id": "story"}],
                "contribution": "Parser only", "exclusions": ["UI"],
                "execution_owner": {"work_id": "product", "task_id": "WB-003"},
            })
            self.assertEqual(explicit_details["contribution"], "Parser only")
            self.assertEqual(explicit_details["exclusions"], ["UI"])
            self.assertEqual(explicit_details["execution_owner"], {"work_id": "product", "task_id": "WB-003"})
            malformed_bounds = [
                {"contribution": []},
                {"exclusions": None},
                {"execution_owner": "not-qualified"},
            ]
            for bad_bounds in malformed_bounds:
                malformed_request = {"explicit_subjects": [{"work_id": "product", "node_id": "story"}],
                                     **bad_bounds}
                malformed_result = resolve(root, "product", malformed_request)
                self.assertEqual(malformed_result["disposition"], "needs_clarification",
                                 f"malformed top-level bounds must refuse: {bad_bounds!r}")
            foreign_model = json.loads(doc_path.read_text())
            foreign_model.pop("subject_association", None)
            foreign_model["work_id"] = "other"
            _put(root, "work/other/engineering-model.json", foreign_model)
            foreign = resolve(root, "product", {"explicit_subjects": [{"work_id": "other", "node_id": "story"}]})
            self.assertEqual(foreign["disposition"], "resolved")
            self.assertEqual(foreign["external_context"]["state"], "available")
            from _ask.scripts.engineering_model.snapshot import capture
            self.assertEqual(foreign["external_context"]["snapshot"], capture(root, "other").identity,
                             "foreign context retains the captured owning revision")
            recorded = resolve(root, "product", {})
            self.assertEqual(recorded["subject"], association["subject"])
            self.assertEqual(recorded["contribution"], association["contribution"])
            self.assertEqual(recorded["exclusions"], association["exclusions"])
            self.assertEqual(recorded["execution_owner"], association["execution_owner"])
            owner_conflict = resolve(root, "product", {"execution_owner": {"work_id": "other", "task_id": "WB-003"}})
            self.assertEqual(owner_conflict["disposition"], "needs_clarification",
                             "a matching task label cannot override the qualified recorded execution owner")
            conflict = resolve(root, "product", {"explicit_subjects": [
                {"work_id": "product", "node_id": "story"},
                {"work_id": "other", "node_id": "story"},
            ]})
            self.assertEqual(conflict["disposition"], "needs_clarification",
                             "qualified owner conflicts cannot be joined by a matching node ID")
            explicit_unknown = resolve(root, "product", {"explicit_subjects": [
                {"work_id": "product", "node_id": "missing-parent"}]})
            self.assertEqual(explicit_unknown["disposition"], "needs_clarification",
                             "missing ancestors are not invented or silently associated")
            current_doc = json.loads(doc_path.read_text())
            current_doc.pop("subject_association")
            _put(root, "work/product/engineering-model.json", current_doc)
            later = resolve(root, "product", {"later_cards": [".later/new-parser.md"]})
            self.assertIn(later["disposition"], {"chooser", "needs_clarification"})
            self.assertEqual(later.get("proposal", {}).get("source"), "later-card")
            bounded_later = resolve(root, "product", {
                "later_cards": [".later/new-parser.md"],
                "contribution": "Prototype parser only", "exclusions": ["UI"],
            })
            self.assertEqual(bounded_later["disposition"], "chooser")
            self.assertIsNone(bounded_later["subject"])
            self.assertEqual(bounded_later["proposal"], {"source": "later-card",
                                                           "references": [".later/new-parser.md"]})
            self.assertEqual(bounded_later["contribution"], "Prototype parser only")
            self.assertEqual(bounded_later["exclusions"], ["UI"])
            chooser = resolve(root, "product", {"inspection_only": True})
            self.assertEqual(chooser["disposition"], "chooser")
            tracker = resolve(root, "product", {"tracker_context": {"id": "T-19", "available": False}})
            self.assertEqual(tracker["disposition"], "chooser")
            self.assertEqual(tracker.get("external_context", {}).get("state"), "unavailable")
            no_join_doc = json.loads(doc_path.read_text())
            no_join_doc.pop("subject_association", None)
            _put(root, "work/product/engineering-model.json", no_join_doc)
            no_join = resolve(root, "product", {"tracker_context": {"id": "T-19", "available": True}})
            self.assertEqual(no_join["disposition"], "chooser",
                             "tracker IDs do not create subject or execution ownership")
            self.assertIsNone(no_join.get("execution_owner"))
            self.assertEqual(no_join["external_context"]["state"], "supplied-unverified",
                             "request data alone does not verify external tracker availability")


class StageIntakeTests(unittest.TestCase):
    def _copy_caller(self, root):
        project = Path(__file__).resolve().parents[2]
        shutil.copy2(project / "ask", root / "ask")
        scripts = project / "_ask/scripts"
        shutil.copytree(scripts, root / "_ask/scripts", dirs_exist_ok=True)
        shutil.copytree(project / ".agents/ask/stages", root / ".agents/ask/stages", dirs_exist_ok=True)
        return root

    def test_adopted_explore_and_grill_call_resolver_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_caller(Path(directory))
            _repo(root)
            probe = root / "probe"
            probe.mkdir()
            (probe / "sitecustomize.py").write_text(
                "import os\n"
                "from engineering_model import context\n"
                "_resolve = context.resolve\n"
                "def _observed(*args, **kwargs):\n"
                "    with open(os.environ['RWB_INTAKE_EVENTS'], 'a') as stream: stream.write('resolver-enter\\n')\n"
                "    result = _resolve(*args, **kwargs)\n"
                "    with open(os.environ['RWB_INTAKE_EVENTS'], 'a') as stream: stream.write('resolver-exit\\n')\n"
                "    return result\n"
                "context.resolve = _observed\n")
            event_file = root / "probe-events.log"
            env = {**os.environ, "PYTHONPATH": f"{probe}:{root / '_ask/scripts'}",
                   "RWB_INTAKE_EVENTS": str(event_file)}
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "intake@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Intake Fixture"], cwd=root, check=True)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
            before_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True,
                                         capture_output=True, check=True).stdout
            before_refs = subprocess.run(["git", "for-each-ref", "--format=%(refname) %(objectname)"],
                                         cwd=root, text=True, capture_output=True, check=True).stdout
            before_tree = subprocess.run(["git", "write-tree"], cwd=root, text=True,
                                         capture_output=True, check=True).stdout
            before_model = (root / "work/product/engineering-model.json").read_bytes()
            from _ask.scripts.engineering_model.admission import load_published
            self.assertIsNone(load_published(root, "product"), "fixture starts without a published admission")
            for stage in ("00-explore", "01-grill"):
                request = root / "request.json"
                request.write_text(json.dumps({"inspection_only": True}))
                event_file.write_text("adopted-caller-enter\n")
                result = subprocess.run(["./ask", "stage-intake", "--stage", stage,
                                         "--work-id", "product", "--request", str(request)],
                                        cwd=root, text=True, capture_output=True, env=env)
                self.assertEqual(result.returncode, 0, f"adopted {stage} caller should resolve read-only: {result.stderr}")
                payload = json.loads(result.stdout)
                event_file.write_text(event_file.read_text() + "adopted-caller-exit\n")
                self.assertEqual(event_file.read_text().splitlines(), ["adopted-caller-enter", "resolver-enter",
                                                                       "resolver-exit", "adopted-caller-exit"],
                                 "the actual adopted caller invokes the shared resolver exactly once")
                self.assertEqual(payload["disposition"], "chooser")
                self.assertIn("snapshot", payload)
                self.assertIn("source", payload)
                self.assertIn("relationships", payload)
                self.assertIn("contribution", payload)
                self.assertIn("exclusions", payload)
                self.assertIn("execution_owner", payload)
                stage_doc = (root / ".agents/ask/stages" / (stage + ".md")).read_text()
                self.assertIn("stage-intake", stage_doc, f"canonical {stage} instructions bind the caller before writes")
                self.assertIn("Before choosing or creating execution work" if stage == "00-explore"
                              else "Before selecting/creating execution work", stage_doc)
                if stage == "01-grill":
                    self.assertIn("source revision, bounded contribution, exclusions and execution owner into",
                                  stage_doc)
                    self.assertIn("intent.md` before presenting the complete intent for approval", stage_doc)
                project = Path(__file__).resolve().parents[2]
                self.assertTrue((project / ".agents/skills" / f"kit-{stage}" / "SKILL.md").is_file())
                self.assertIn(stage_doc.strip(), (project / ".agents/skills" / f"kit-{stage}" / "SKILL.md").read_text())
                self.assertIn(stage_doc.strip(), (project / ".cursor/skills" / f"kit-{stage}" / "SKILL.md").read_text())
                projection = ".cursor/commands" if stage == "00-explore" else ".cursor/commands"
                cursor_doc = project / projection / f"{stage}.md"
                self.assertIn(stage_doc.strip(), cursor_doc.read_text())
                known = root / "known.json"
                known.write_text(json.dumps({"explicit_subjects": [{"work_id": "product", "node_id": "story"}],
                                             "contribution": "Parser only", "exclusions": ["UI"],
                                             "execution_owner": {"work_id": "product", "task_id": "WB-003"}}))
                known_result = subprocess.run(["./ask", "stage-intake", "--stage", stage,
                                                "--work-id", "product", "--request", str(known)],
                                               cwd=root, text=True, capture_output=True, env=env)
                self.assertEqual(known_result.returncode, 0, known_result.stderr)
                known_payload = json.loads(known_result.stdout)
                self.assertEqual(known_payload["disposition"], "resolved")
                self.assertEqual(known_payload["contribution"], "Parser only")
                self.assertEqual(known_payload["exclusions"], ["UI"])
                self.assertEqual(known_payload["execution_owner"], {"work_id": "product", "task_id": "WB-003"})
                later = root / "later.json"
                later.write_text(json.dumps({"later_cards": [".later/parser.md"],
                                             "contribution": "Prototype parser", "exclusions": ["UI"]}))
                later_result = subprocess.run(["./ask", "stage-intake", "--stage", stage,
                                               "--work-id", "product", "--request", str(later)],
                                              cwd=root, text=True, capture_output=True, env=env)
                self.assertEqual(later_result.returncode, 0, later_result.stderr)
                later_payload = json.loads(later_result.stdout)
                self.assertIsNone(later_payload["subject"])
                self.assertEqual(later_payload["proposal"]["source"], "later-card")
                self.assertEqual(later_payload["contribution"], "Prototype parser")
                conflict = root / "conflict.json"
                conflict.write_text(json.dumps({"explicit_subjects": [
                    {"work_id": "product", "node_id": "story-a"},
                    {"work_id": "foreign", "node_id": "story-a"}]}))
                event_file.write_text("")
                refused = subprocess.run(["./ask", "stage-intake", "--stage", stage,
                                          "--work-id", "product", "--request", str(conflict)],
                                         cwd=root, text=True, capture_output=True, env=env)
                self.assertEqual(refused.returncode, 0)
                self.assertEqual(json.loads(refused.stdout)["disposition"], "needs_clarification")
                self.assertEqual(event_file.read_text().splitlines(), ["resolver-enter", "resolver-exit"])
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), before_model)
            self.assertFalse((root / "work/product/intent.md").exists())
            self.assertFalse((root / "work/product/explore-map.md").exists())
            self.assertIsNone(load_published(root, "product"), "inspection and proposal paths do not admit a generation")
            self.assertEqual(subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True,
                                            capture_output=True, check=True).stdout, before_head)
            self.assertEqual(subprocess.run(["git", "for-each-ref", "--format=%(refname) %(objectname)"],
                                            cwd=root, text=True, capture_output=True, check=True).stdout, before_refs)
            self.assertEqual(subprocess.run(["git", "write-tree"], cwd=root, text=True,
                                            capture_output=True, check=True).stdout, before_tree)

    def test_model_context_cli_matches_caller_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_caller(Path(directory))
            _repo(root)
            request = root / "request.json"
            request.write_text(json.dumps({"explicit_subjects": [{"work_id": "product", "node_id": "story"}],
                                           "contribution": "Parser only", "exclusions": ["UI"]}))
            before = (root / "work/product/engineering-model.json").read_bytes()
            command = ["./ask", "model", "context", "--work-id", "product", "--request", str(request)]
            cli = subprocess.run(command, cwd=root, text=True, capture_output=True)
            self.assertEqual(cli.returncode, 0, f"model context inspection succeeds: {cli.stderr}")
            stage = subprocess.run(["./ask", "stage-intake", "--stage", "00-explore",
                                    "--work-id", "product", "--request", str(request)],
                                   cwd=root, text=True, capture_output=True)
            self.assertEqual(stage.returncode, 0)
            self.assertEqual(json.loads(cli.stdout), json.loads(stage.stdout),
                             "CLI and adopted stage use the same resolver and structured snapshot")
            local = json.loads(cli.stdout)
            self.assertEqual(local["disposition"], "resolved")
            self.assertEqual(local["purpose"], "Outcome")
            self.assertEqual(local["contribution"], "Parser only")
            self.assertTrue(local["snapshot"]["digest"])
            foreign_document = json.loads((root / "work/product/engineering-model.json").read_text())
            foreign_document["work_id"] = "other"
            _put(root, "work/other/engineering-model.json", foreign_document)
            request.write_text(json.dumps({"explicit_subjects": [{"work_id": "other", "node_id": "story"}]}))
            foreign_cli = subprocess.run(command, cwd=root, text=True, capture_output=True)
            self.assertEqual(foreign_cli.returncode, 0, foreign_cli.stderr)
            foreign_payload = json.loads(foreign_cli.stdout)
            self.assertEqual(foreign_payload["disposition"], "resolved")
            self.assertEqual(foreign_payload["purpose"], "Outcome")
            self.assertEqual(foreign_payload["external_context"]["state"], "available")
            self.assertEqual(foreign_payload["external_context"]["snapshot"]["model"]["path"],
                             "work/other/engineering-model.json")
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), before)
            malformed = root / "bad.json"
            malformed.write_text("{")
            bad = subprocess.run(["./ask", "model", "context", "--work-id", "product",
                                  "--request", str(malformed)], cwd=root, text=True, capture_output=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), before)

    def test_association_passage_admission_uses_existing_guard(self):
        try:
            from _ask.scripts.engineering_model.actions import associate_subject
            from _ask.scripts.engineering_model import actions as actions_module, domain as domain_module
            from _ask.scripts.engineering_model.admission import validate_current, load_published
            from _ask.scripts.engineering_model.context import resolve
            from _ask.scripts.engineering_model.domain import apply_batch
            from _ask.scripts.engineering_model.snapshot import Snapshot
        except ImportError:
            associate_subject = validate_current = load_published = resolve = apply_batch = None
        self.assertTrue(callable(associate_subject) and callable(apply_batch),
                        "subject association must be an attributable semantic operation through the real guard")
        if not callable(associate_subject):
            return
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            captured, errors = validate_current(root, "product")
            self.assertFalse(errors)
            trace = []
            real_validate = actions_module.validate_current
            real_apply = domain_module.apply_batch
            real_diagnostics = Snapshot.diagnostics
            real_publish = actions_module._publish
            def traced_validate(*args, **kwargs):
                trace.append("pre")
                return real_validate(*args, **kwargs)
            def traced_apply(*args, **kwargs):
                trace.append("action")
                return real_apply(*args, **kwargs)
            def traced_diagnostics(snapshot, *args, **kwargs):
                if "action" in trace and "post" not in trace:
                    trace.append("post")
                return real_diagnostics(snapshot, *args, **kwargs)
            def traced_publish(*args, **kwargs):
                trace.append("publication")
                return real_publish(*args, **kwargs)
            with patch.object(actions_module, "validate_current", side_effect=traced_validate), \
                 patch.object(domain_module, "apply_batch", side_effect=traced_apply), \
                 patch.object(Snapshot, "diagnostics", traced_diagnostics), \
                 patch.object(actions_module, "_publish", side_effect=traced_publish):
                result = associate_subject(root, "product", captured.identity["digest"],
                                           subject={"work_id": "product", "node_id": "story"},
                                           contribution="Implement parser", exclusions=["UI redesign"],
                                           execution_owner={"work_id": "product", "task_id": "WB-003"},
                                           actor="human", rationale="Confirmed association")
            self.assertTrue(result["valid"], str(result))
            self.assertEqual(trace, ["pre", "action", "post", "publication"],
                             "real action boundaries run exactly once in guarded order")
            self.assertEqual(result["steps"], ["pre", "action", "post", "publication"])
            current = json.loads((root / "work/product/engineering-model.json").read_text())
            self.assertEqual(current["subject_association"]["subject"], {"work_id": "product", "node_id": "story"})
            self.assertEqual(current["subject_association"]["contribution"], "Implement parser")
            self.assertEqual(current["subject_association"]["snapshot_digest"], captured.identity["digest"])
            self.assertEqual(current["subject_association"]["history"][0]["actor"], "human")
            stable = (root / "work/product/engineering-model.json").read_bytes()
            refused = associate_subject(root, "product", result["snapshot"]["digest"],
                                        subject={"work_id": "product", "node_id": "missing"},
                                        contribution="Bad required contract", exclusions=[],
                                        actor="human", rationale="Missing selected subject")
            self.assertFalse(refused["valid"])
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), stable)
            self.assertEqual(refused["steps"], ["pre"])
            malformed = associate_subject(root, "product", result["snapshot"]["digest"],
                                          subject={"work_id": "product", "node_id": "story"},
                                          contribution="  ", exclusions=[], actor="human",
                                          rationale="Reject malformed proposal")
            self.assertFalse(malformed["valid"])
            self.assertEqual(malformed["steps"], ["pre"], "invalid proposal data is rejected before semantic action")
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), stable)
            required = associate_subject(root, "product", result["snapshot"]["digest"],
                                         subject={"work_id": "product", "node_id": "story"},
                                         contribution="Required contribution", exclusions=[], actor="human",
                                         rationale="Missing required spec", required_roles=("spec",))
            self.assertFalse(required["valid"], "only an explicitly required subject context blocks publication")
            self.assertEqual(required["steps"], ["pre"])
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), stable)
            stale = associate_subject(root, "product", "0" * 64,
                                      subject={"work_id": "product", "node_id": "story"},
                                      contribution="Stale", exclusions=[], actor="human", rationale="Stale")
            self.assertFalse(stale["valid"])
            self.assertEqual(stale["diagnostics"][0]["code"], "EM007_STALE_INPUT")
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), stable)
            uncovered = []
            current_document = json.loads((root / "work/product/engineering-model.json").read_text())
            current_document["nodes"][1]["context"] = [{
                "role": "spec", "path": "docs/context.md", "revision": "snapshot",
                "selector": {"kind": "heading", "path": ["Scope"]},
            }]
            _put(root, "work/product/engineering-model.json", current_document)
            required_input, required_diagnostics = validate_current(root, "product")
            self.assertFalse(required_diagnostics)
            required_success = associate_subject(
                root, "product", required_input.identity["digest"],
                subject={"work_id": "product", "node_id": "story"},
                contribution="Contracted parser support", exclusions=["UI redesign"],
                actor="human", rationale="Confirmed from the unique spec passage",
                required_roles=("spec",))
            if not required_success["valid"]:
                uncovered.append(f"unique required passage should permit association: {required_success!r}")
            else:
                self.assertEqual(required_success["input_snapshot"], required_input.identity)
                self.assertEqual(required_success["steps"], ["pre", "action", "post", "publication"])
                self.assertEqual(required_success["snapshot"], load_published(root, "product").identity)
                required_record = json.loads((root / "work/product/engineering-model.json").read_text())["subject_association"]
                self.assertEqual(required_record["snapshot_digest"], required_input.identity["digest"])
                self.assertEqual(required_record["contribution"], "Contracted parser support")
                self.assertEqual(required_record["exclusions"], ["UI redesign"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            model_path = root / "work/product/engineering-model.json"
            document = json.loads(model_path.read_text())
            document["nodes"][1]["context"] = [
                {"role": "spec", "path": "docs/context.md", "revision": "snapshot",
                 "selector": {"kind": "heading", "path": ["Scope"]}},
                {"role": "spec", "path": "docs/context.md", "revision": "snapshot",
                 "selector": {"kind": "heading", "path": ["Scope"]}},
            ]
            _put(root, "work/product/engineering-model.json", document)
            current, diagnostics = validate_current(root, "product")
            self.assertFalse(diagnostics)
            ambiguous = associate_subject(root, "product", current.identity["digest"],
                                          subject={"work_id": "product", "node_id": "story"},
                                          contribution="Ambiguous context", exclusions=[], actor="human",
                                          rationale="Do not guess", required_roles=("spec",))
            self.assertFalse(ambiguous["valid"])
            self.assertEqual(ambiguous["steps"], ["pre"])
            self.assertIsNone(load_published(root, "product"), "refusal does not publish an association candidate")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            model_path = root / "work/product/engineering-model.json"
            document = json.loads(model_path.read_text())
            document["nodes"][1]["context"] = [
                {"role": "spec", "path": "docs/unsafe.md", "revision": "snapshot",
                 "selector": {"kind": "heading", "path": ["Scope"]}},
            ]
            _put(root, "work/product/engineering-model.json", document)
            (root / "docs/unsafe.md").symlink_to(root / "docs/context.md")
            current, diagnostics = validate_current(root, "product")
            self.assertTrue(diagnostics, "unsafe context symlinks fail the captured pre-check")
            unsafe = associate_subject(root, "product", current.identity["digest"],
                                       subject={"work_id": "product", "node_id": "story"},
                                       contribution="Unsafe context", exclusions=[], actor="human",
                                       rationale="Reject symlink", required_roles=("spec",))
            self.assertFalse(unsafe["valid"])
            self.assertNotIn("action", unsafe["steps"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            document = json.loads((root / "work/product/engineering-model.json").read_text())
            malformed_prior_values = [None, 5, {}, [None],
                                      [{"actor": "human", "rationale": "Old", "timestamp": []}]]
            for prior_history in malformed_prior_values:
                changed = json.loads(json.dumps(document))
                changed["subject_association"] = {"history": prior_history}
                _put(root, "work/product/engineering-model.json", changed)
                current, diagnostics = validate_current(root, "product")
                self.assertFalse(diagnostics)
                stable_prior = (root / "work/product/engineering-model.json").read_bytes()
                try:
                    malformed_history = associate_subject(
                        root, "product", current.identity["digest"],
                        subject={"work_id": "product", "node_id": "story"}, contribution="Parser only",
                        exclusions=[], actor="human", rationale="Defend malformed history")
                except Exception as exc:
                    self.fail(f"malformed prior history must diagnose, not raise {type(exc).__name__}: {exc}")
                if malformed_history["valid"] or malformed_history["steps"] != ["pre"]:
                    uncovered.append(f"malformed history accepted or invoked action: {prior_history!r} / {malformed_history!r}")
                self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), stable_prior)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            foreign_document = json.loads((root / "work/product/engineering-model.json").read_text())
            foreign_document["work_id"] = "other"
            _put(root, "work/other/engineering-model.json", foreign_document)
            local, local_errors = validate_current(root, "product")
            foreign, foreign_errors = validate_current(root, "other")
            self.assertFalse(local_errors)
            self.assertFalse(foreign_errors)
            linked = associate_subject(root, "product", local.identity["digest"],
                                       subject={"work_id": "other", "node_id": "story"},
                                       contribution="Shared parser support", exclusions=["other product work"],
                                       execution_owner={"work_id": "product", "task_id": "WB-003"},
                                       actor="human", rationale="Confirmed foreign subject pointer")
            self.assertTrue(linked["valid"], str(linked))
            stored = json.loads((root / "work/product/engineering-model.json").read_text())["subject_association"]
            self.assertEqual(stored["subject"], {"work_id": "other", "node_id": "story"})
            self.assertEqual(stored["subject_snapshot_digest"], foreign.identity["digest"])
            resolved = resolve(root, "product", {})
            self.assertEqual(resolved["disposition"], "resolved")
            current_foreign, current_foreign_errors = validate_current(root, "other")
            self.assertFalse(current_foreign_errors)
            self.assertEqual(resolved["external_context"]["snapshot"], current_foreign.identity)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            foreign_document = json.loads((root / "work/product/engineering-model.json").read_text())
            foreign_document["work_id"] = "other"
            _put(root, "work/other/engineering-model.json", foreign_document)
            local, local_errors = validate_current(root, "product")
            self.assertFalse(local_errors)
            stable_local = (root / "work/product/engineering-model.json").read_bytes()
            stable_generation = load_published(root, "product")
            from _ask.scripts.engineering_model import domain
            real_apply = domain.apply_batch
            def save_foreign_after_action(*args, **kwargs):
                proposal = real_apply(*args, **kwargs)
                updated = json.loads((root / "work/other/engineering-model.json").read_text())
                updated["nodes"][1]["title"] = "Changed during local association"
                _put(root, "work/other/engineering-model.json", updated)
                return proposal
            with patch.object(domain, "apply_batch", side_effect=save_foreign_after_action):
                raced = associate_subject(root, "product", local.identity["digest"],
                                          subject={"work_id": "other", "node_id": "story"},
                                          contribution="Shared parser support", exclusions=["other UI"],
                                          execution_owner={"work_id": "product", "task_id": "WB-003"},
                                          actor="human", rationale="Foreign owner must stay fresh")
            if raced["valid"] or not any(item["code"] == "EM007_INPUT_CHANGED" for item in raced["diagnostics"]):
                uncovered.append(f"foreign owner save did not stale association: {raced!r}")
            self.assertEqual((root / "work/product/engineering-model.json").read_bytes(), stable_local)
            self.assertEqual(load_published(root, "product"), stable_generation)
        self.assertFalse(uncovered, "association boundary gaps: " + " | ".join(uncovered))
