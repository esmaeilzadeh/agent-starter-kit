"""RWB-103 subject resolution and adopted initial-stage intake contracts."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

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
            for stage in ("00-explore", "01-grill"):
                request = root / "request.json"
                request.write_text(json.dumps({"inspection_only": True}))
                event_file.write_text("")
                result = subprocess.run(["./ask", "stage-intake", "--stage", stage,
                                         "--work-id", "product", "--request", str(request)],
                                        cwd=root, text=True, capture_output=True, env=env)
                self.assertEqual(result.returncode, 0, f"adopted {stage} caller should resolve read-only: {result.stderr}")
                payload = json.loads(result.stdout)
                self.assertEqual(event_file.read_text().splitlines(), ["resolver-enter", "resolver-exit"],
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
                project = Path(__file__).resolve().parents[2]
                self.assertTrue((project / ".agents/skills" / f"kit-{stage}" / "SKILL.md").is_file())
                self.assertIn("stage-intake", (project / ".agents/skills" / f"kit-{stage}" / "SKILL.md").read_text())
                projection = ".cursor/commands" if stage == "00-explore" else ".cursor/commands"
                cursor_doc = project / projection / f"{stage}.md"
                self.assertIn("stage-intake", cursor_doc.read_text())
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
            request.write_text(json.dumps({"explicit_subjects": [{"work_id": "product", "node_id": "story-a"}]}))
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
            from _ask.scripts.engineering_model.admission import validate_current, load_published
            from _ask.scripts.engineering_model.domain import apply_batch
        except ImportError:
            associate_subject = validate_current = load_published = apply_batch = None
        self.assertTrue(callable(associate_subject) and callable(apply_batch),
                        "subject association must be an attributable semantic operation through the real guard")
        if not callable(associate_subject):
            return
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            captured, errors = validate_current(root, "product")
            self.assertFalse(errors)
            result = associate_subject(root, "product", captured.identity["digest"],
                                       subject={"work_id": "product", "node_id": "story"},
                                       contribution="Implement parser", exclusions=["UI redesign"],
                                       execution_owner={"work_id": "product", "task_id": "WB-003"},
                                       actor="human", rationale="Confirmed association")
            self.assertTrue(result["valid"], str(result))
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
