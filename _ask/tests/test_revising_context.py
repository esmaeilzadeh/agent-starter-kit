"""Captured context selection and action-dependency behavior for the workbench."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import shutil
from contextlib import redirect_stderr
from io import StringIO

from _ask.scripts.engineering_model.snapshot import capture, is_current
from _ask.tests.revising_fixture import digest, model


def _put(root, relative, value):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True).encode()
    path.write_bytes(raw)
    return path


def _canonical():
    spec = {"schema": "ask-spec/v1", "work_id": "product", "revision": 1,
            "criteria": [{"id": "EM-007", "given": "A valid model", "when": "Admitted",
                          "then": ["Only captured sources are used"], "verification_mode": "tests"}]}
    plan = {"schema": "ask-test-plan/v1", "work_id": "product", "spec_digest": digest(spec),
            "obligations": [{"criterion_id": "EM-007", "required_types": ["unit"]}],
            "task_scopes": [{"task_id": "WB-003", "test_ids": ["WB-publish"]}],
            "runners": [{"id": "fixture", "adapter": "unittest",
                         "argv": ["python3", "-m", "unittest", "test_fixture.Cases.test_behavior"]}],
            "tests": [{"id": "WB-publish", "criterion_ids": ["EM-007"], "type": "unit",
                       "change_kind": "new", "runner_id": "fixture", "case_id": "test_fixture.Cases.test_behavior",
                       "source_paths": ["test_fixture.py"],
                       "scenario": {"given": "A valid model", "when": "Admitted", "then": ["Only captured sources are used"]},
                       "expected_assertions": [{"criterion_id": "EM-007", "checks": ["Selected passages are exact"]}]}]}
    return spec, plan


def _document(*, context=True, source_context=True):
    document = model()
    spec, plan = _canonical()
    document["nodes"][2]["case"]["plan_digest"] = digest(plan)
    task = document["nodes"][3]
    task["execution"] = {"work_id": "product", "task_id": "WB-003"}
    if context:
        task["context"] = [
            {"role": "spec", "path": "docs/context.md", "revision": "snapshot",
             "selector": {"kind": "heading", "path": ["Scope"]}},
            {"role": "plan", "path": "work/product/plan.md", "revision": "snapshot",
             "selector": {"kind": "plan-task", "heading_path": ["Work breakdown"], "task_id": "WB-003"}},
        ]
    if source_context:
        document["nodes"][4]["source_context"] = [
            {"path": "tests/helpers.py", "revision": "snapshot", "qualified_name": "tests.helpers.assert_publish",
             "role": "helper", "explanation": "Shared assertion helper"}
        ]
    return document


def _repo(root, *, context=True, source_context=True, spec_text="# Scope\nCurrent contract.\n",
          plan_text="# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n"):
    project = Path(__file__).resolve().parents[2]
    shutil.copytree(project / ".agents/ask/verification", root / ".agents/ask/verification",
                    dirs_exist_ok=True)
    spec, plan = _canonical()
    _put(root, "specs/current/product.json", spec)
    _put(root, "work/product/test-plan.json", plan)
    _put(root, "work/product/engineering-model.json", _document(context=context, source_context=source_context))
    _put(root, "work/product/inner-loop/tasks.yaml",
         b"schema: ask-inner-loop-tasks/v1\nwork_id: product\ntasks:\n"
         b"  - id: WB-003\n    depends_on: []\n    owned_paths: [task-result.md]\n")
    _put(root, "specs/current/product.md", b"# Product requirements\nCanonical specification companion.\n")
    _put(root, "test_fixture.py", b"from pathlib import Path\nimport unittest\nclass Cases(unittest.TestCase):\n"
         b"    def test_behavior(self):\n        self.assertTrue(Path('task-result.md').is_file())\n")
    if context and spec_text is not None:
        _put(root, "docs/context.md", spec_text.encode())
    else:
        (root / "docs/context.md").unlink(missing_ok=True)
    if context and plan_text is not None:
        _put(root, "work/product/plan.md", plan_text.encode())
    if source_context:
        _put(root, "tests/helpers.py", b"def assert_publish():\n    assert True\n")
    return None


def _resolve():
    try:
        from _ask.scripts.engineering_model.passages import resolve
    except ImportError:
        return None
    return resolve


class PassageTests(unittest.TestCase):
    def test_selector_grammar_and_safe_resolution_matrix(self):
        resolve = _resolve()
        self.assertTrue(callable(resolve), "the public passage selector resolver must be available")
        if not callable(resolve):
            return

        markdown = (b"# Work\n\n## Work breakdown\nIntro.\n### Detail\nText.\n"
                    b"\n# Other\n## Work breakdown\nSecond chain.\n")
        short_heading = resolve("work/plan.md", markdown,
                                {"kind": "heading", "path": ["Work breakdown"]})
        self.assertEqual(short_heading["state"], "unavailable",
                         "a selector must name the complete ancestor heading chain")
        unique_heading = resolve("work/plan.md", markdown,
                                 {"kind": "heading", "path": ["Work", "Work breakdown"]})
        self.assertEqual(unique_heading["state"], "available")
        self.assertEqual(unique_heading["text"], "## Work breakdown\nIntro.\n### Detail\nText.\n\n")
        duplicate_chain = b"# Work\n## Work breakdown\nFirst.\n# Work\n## Work breakdown\nSecond.\n"
        ambiguous_chain = resolve("work/plan.md", duplicate_chain,
                                  {"kind": "heading", "path": ["Work", "Work breakdown"]})
        self.assertEqual(ambiguous_chain["state"], "ambiguous")
        missing = resolve("work/missing.md", None, {"kind": "heading", "path": ["Work"]})
        self.assertEqual(missing["state"], "unavailable")
        zero = resolve("work/plan.md", markdown, {"kind": "heading", "path": ["Absent"]})
        self.assertEqual(zero["state"], "unavailable")
        ambiguous = resolve("work/plan.md", markdown,
                            {"kind": "heading", "path": ["Other", "Work breakdown"]})
        self.assertEqual(ambiguous["state"], "available")
        fenced_only = resolve("work/plan.md",
                              b"# Work\n```text\n## Work breakdown\nExample contract.\n```\n",
                              {"kind": "heading", "path": ["Work", "Work breakdown"]})
        self.assertEqual(fenced_only["state"], "unavailable",
                         "fenced examples are not selectable Markdown headings")
        fenced_lookalike = resolve("work/plan.md",
                                   b"# Work\n## Work breakdown\nActual contract.\n```text\n"
                                   b"## Work breakdown\nExample contract.\n```\n",
                                   {"kind": "heading", "path": ["Work", "Work breakdown"]})
        self.assertEqual(fenced_lookalike["state"], "available",
                         "fenced lookalikes do not make a real heading ambiguous")
        self.assertEqual(fenced_lookalike["start_line"], 2)
        nested_fence_marker = resolve("work/plan.md",
                                       b"# Work\n```text\n```python\n## Work breakdown\nExample still inside.\n```\n",
                                       {"kind": "heading", "path": ["Work", "Work breakdown"]})
        self.assertEqual(nested_fence_marker["state"], "unavailable",
                         "a marker with trailing info text is content, not a closing fence")
        tilde_fence_marker = resolve("work/plan.md",
                                     b"# Work\n~~~~text\n~~~~python\n## Work breakdown\nExample still inside.\n~~~~\n",
                                     {"kind": "heading", "path": ["Work", "Work breakdown"]})
        self.assertEqual(tilde_fence_marker["state"], "unavailable",
                         "tilde fences also require whitespace-only closing lines")

        table = b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n| WB-004 | Review safely |\n"
        selected = resolve("work/plan.md", table,
                           {"kind": "plan-task", "heading_path": ["Work breakdown"], "task_id": "WB-003"})
        self.assertEqual(selected["state"], "available")
        self.assertEqual(selected["text"], "| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n")
        self.assertNotIn("WB-004", selected["text"], "selection excludes adjacent plan rows")
        fenced_table = resolve("work/plan.md",
                               b"# Work breakdown\n```markdown\n| Task ID | Outcome |\n| --- | --- |\n"
                               b"| WB-003 | Example row |\n```\n",
                               {"kind": "plan-task", "heading_path": ["Work breakdown"],
                                "task_id": "WB-003"})
        self.assertEqual(fenced_table["state"], "unavailable",
                         "fenced example tables are not plan task rows")
        fenced_row = resolve("work/plan.md",
                             b"# Work breakdown\n| Task ID | Outcome |\n| --- | --- |\n"
                             b"| WB-003 | Actual row |\n```markdown\n| Task ID | Outcome |\n| --- | --- |\n"
                             b"| WB-003 | Example row |\n```\n",
                             {"kind": "plan-task", "heading_path": ["Work breakdown"],
                              "task_id": "WB-003"})
        self.assertEqual(fenced_row["state"], "available")
        self.assertIn("Actual row", fenced_row["text"])
        self.assertNotIn("Example row", fenced_row["text"])
        for path, selector in [
            ("../outside.md", {"kind": "heading", "path": ["Work"]}),
            ("C:\\outside.md", {"kind": "heading", "path": ["Work"]}),
            ("work/a.md", {"kind": "fuzzy", "query": "Work"}),
            ("work/a.md", {"kind": "heading", "path": []}),
            ("work/a.md", {"kind": "heading", "path": [""]}),
            ("work/a.md", {"kind": "heading", "path": ["Work"], "fallback": True}),
            ("work/a.md", {"kind": "plan-task", "heading_path": ["Work"], "task_id": []}),
        ]:
            with self.assertRaises((ValueError, TypeError), msg=f"unsafe selector must reject: {path} {selector!r}"):
                resolve(path, markdown, selector)

        duplicate_rows = b"# Work breakdown\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | First |\n| WB-003 | Duplicate |\n"
        duplicate_task = resolve("work/plan.md", duplicate_rows,
                                 {"kind": "plan-task", "heading_path": ["Work breakdown"], "task_id": "WB-003"})
        self.assertEqual(duplicate_task["state"], "ambiguous")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            from _ask.scripts.engineering_model.admission import admit
            baseline, diagnostics = admit(root, "product")
            self.assertEqual(diagnostics, [])
            identity = baseline.identity
            self.assertEqual(identity["dependency_discovery_version"], "engineering-input-closure/v3")
            self.assertTrue(identity["passage_rules_version"])
            self.assertTrue(identity["heading_discovery_version"])
            self.assertTrue(identity["plan_task_discovery_version"])
            path = root / "docs/context.md"
            path.unlink()
            path.symlink_to(root / "work/product/plan.md")
            linked = capture(root, "product")
            self.assertNotEqual(linked.statuses["docs/context.md"], "present",
                                "symlink components cannot be treated as safe passage sources")
            _published, diagnostics = admit(root, "product")
            self.assertTrue(any(item["code"] == "EM001_CONTEXT_REFERENCE" for item in diagnostics),
                            "terminal symlink must refuse captured admission")
            from _ask.scripts.engineering_model.observer import observe_once
            observation = observe_once(root, "product")
            self.assertFalse(observation["valid"], "unsafe current selector state remains diagnosable")
            self.assertTrue(observation["last_validated"], "invalid current input retains last valid inspection")
            self.assertEqual(observation["snapshot"]["digest"], baseline.identity["digest"])
            path.unlink()
            (root / "docs").rename(root / "docs-real")
            (root / "docs").symlink_to(root / "docs-real", target_is_directory=True)
            ancestor = capture(root, "product")
            self.assertNotEqual(ancestor.statuses["docs/context.md"], "present",
                                "an in-repository ancestor symlink is also unsafe")
            _published, diagnostics = admit(root, "product")
            self.assertTrue(any(item["code"] == "EM001_CONTEXT_REFERENCE" for item in diagnostics),
                            "ancestor symlink must refuse captured admission")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            document = json.loads((root / "work/product/engineering-model.json").read_text())
            document["nodes"][3]["context"][0]["selector"] = {
                "kind": "heading", "path": ["Scope"], "fallback": True}
            _put(root, "work/product/engineering-model.json", document)
            from _ask.scripts.engineering_model.admission import admit
            _published, diagnostics = admit(root, "product")
            self.assertTrue(any(item["code"] == "EM001_CONTEXT_SELECTOR" for item in diagnostics),
                            "malformed selectors reject actual model admission")

        # An explicit committed revision is read from that revision even when
        # the working file now contains different bytes; no current-file fallback.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root, spec_text="# Scope\nHistorical contract.\n")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "capture source"], cwd=root, check=True)
            revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                      capture_output=True, text=True).stdout.strip()
            _put(root, "docs/context.md", b"# Scope\nCurrent but not selected.\n")
            document = json.loads((root / "work/product/engineering-model.json").read_text())
            document["nodes"][3]["context"][0]["revision"] = revision
            _put(root, "work/product/engineering-model.json", document)
            historical = capture(root, "product")
            passage_reader = getattr(historical, "resolve_passage", None)
            self.assertTrue(callable(passage_reader), "historical selectors resolve through captured commits")
            if callable(passage_reader):
                self.assertIn("Historical contract", passage_reader("task", "spec")["text"])
                self.assertNotIn("Current but not selected", passage_reader("task", "spec")["text"])
                (root / "docs/context.md").unlink()
                historical_missing = capture(root, "product")
                self.assertEqual(historical_missing.resolve_passage("task", "spec")["state"], "available",
                                 "committed revision remains readable when the working target is missing")
                self.assertIn("Historical contract", historical_missing.resolve_passage("task", "spec")["text"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root, spec_text=None)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "commit without passage"], cwd=root, check=True)
            missing_revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                              capture_output=True, text=True).stdout.strip()
            _put(root, "docs/context.md", b"# Scope\nUncommitted fallback must not appear.\n")
            document = json.loads((root / "work/product/engineering-model.json").read_text())
            document["nodes"][3]["context"][0]["revision"] = missing_revision
            _put(root, "work/product/engineering-model.json", document)
            missing_blob = capture(root, "product")
            self.assertEqual(missing_blob.resolve_passage("task", "spec")["state"], "unavailable",
                             "a safe missing historical passage remains unavailable")
            self.assertIsNone(missing_blob.resolve_passage("task", "spec")["text"],
                              "current bytes cannot substitute for an absent committed blob")
            _published, missing_diagnostics = admit(root, "product")
            self.assertEqual(missing_diagnostics, [],
                             "a safe missing optional historical context does not invalidate the model")
            from _ask.scripts.engineering_model.workflow import workflow_admission
            with workflow_admission(root, "product"):
                pass
            try:
                with workflow_admission(root, "product", selected_task_id="task"):
                    self.fail("dependent Task admission must require the missing historical passage")
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_CONTEXT_REQUIRED",
                                 f"dependent actions remain gated by the unavailable passage: {exc!r}")
            self.assertNotIn("Uncommitted fallback", str(missing_blob.resolve_passage("task", "spec")["text"]))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root)
            (root / "docs/context.md").unlink()
            (root / "docs/context.md").symlink_to(root / "work/product/plan.md")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "symlink source"], cwd=root, check=True)
            symlink_revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                              capture_output=True, text=True).stdout.strip()
            document = json.loads((root / "work/product/engineering-model.json").read_text())
            document["nodes"][3]["context"][0]["revision"] = symlink_revision
            _put(root, "work/product/engineering-model.json", document)
            committed_symlink = capture(root, "product")
            self.assertEqual(committed_symlink.resolve_passage("task", "spec")["state"], "error",
                             "a committed symlink is not an admissible historical source")

class PassageAdmissionTests(unittest.TestCase):
    def test_required_passages_block_only_dependent_actions(self):
        from _ask.scripts.engineering_model.workflow import workflow_admission
        from _ask.scripts.engineering_model.actions import edit
        from _ask.scripts.engineering_model.admission import admit, load_published

        review_failures = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root, spec_text=None, plan_text="# Work breakdown\n")
            project = Path(__file__).resolve().parents[2]
            shutil.copytree(project / "_ask/scripts", root / "_ask/scripts")
            captured = capture(root, "product")

            # The schema compatibility decision and the selected-task check
            # must apply to one captured generation. Replace a valid v1 model
            # with a valid v2 model after the real preflight capture returns.
            race_root = root / "mixed-generation-race"
            race_root.mkdir()
            _repo(race_root, spec_text=None)
            next_v2 = (race_root / "work/product/engineering-model.json").read_bytes()
            legacy_seed = root / "legacy-seed"
            legacy_seed.mkdir()
            from _ask.tests.engineering_fixture import workbench_model
            legacy_document, _legacy_spec = workbench_model(legacy_seed)
            legacy_document["work_id"] = "product"
            for legacy_node in legacy_document["nodes"]:
                reference = legacy_node.get("reference") if isinstance(legacy_node, dict) else None
                if not isinstance(reference, dict):
                    continue
                reference["path"] = reference["path"].replace("pilot", "product")
                reference["id"] = "EM-007" if reference["path"].startswith("specs/") else "WB-publish"
            _put(race_root, "work/product/engineering-model.json", legacy_document)
            from _ask.scripts.engineering_model import workflow as workflow_module
            real_validate_current = workflow_module.validate_current
            _, legacy_diagnostics = real_validate_current(race_root, "product")
            self.assertEqual(legacy_diagnostics, [], "the initial legacy generation is valid v1")
            changed_after_capture = []

            def external_save_after_real_capture(captured_root, captured_work_id):
                snapshot, diagnostics = real_validate_current(captured_root, captured_work_id)
                # This save occurs only at the old standalone preflight, before
                # admission has published anything. A single admitted-snapshot
                # flow has already published its own generation by the time it
                # performs the later freshness check.
                if not changed_after_capture and load_published(race_root, "product") is None:
                    (race_root / "work/product/engineering-model.json").write_bytes(next_v2)
                    changed_after_capture.append(True)
                return snapshot, diagnostics

            workflow_module.validate_current = external_save_after_real_capture
            race_actions = []
            race_refusal = None
            try:
                try:
                    with workflow_module.workflow_admission(
                            race_root, "product", selected_execution={"work_id": "product", "task_id": "WB-003"}):
                        race_actions.append("selected-v2-action")
                except Exception as exc:
                    race_refusal = exc
            finally:
                workflow_module.validate_current = real_validate_current
            if changed_after_capture:
                self.assertIn(getattr(race_refusal, "diagnostic", {}).get("code"),
                              {"EM015_CONTEXT_REQUIRED", "EM007_INPUT_CHANGED"},
                              f"the generation switch must refuse before selected action: {race_refusal!r}")
                self.assertEqual(race_actions, [], "mixed-generation admission refuses before the dependent action")
            else:
                self.assertIsNone(race_refusal, f"single-generation v1 admission remains valid: {race_refusal!r}")
                self.assertEqual(race_actions, ["selected-v2-action"],
                                 "one captured valid v1 generation preserves the legacy action route")

            # Persisted passage text must remain bound to captured source bytes
            # and the immutable generation identity, including on reload.
            tamper_root = root / "tampered-generation"
            tamper_root.mkdir()
            _repo(tamper_root)
            admitted, diagnostics = admit(tamper_root, "product")
            self.assertEqual(diagnostics, [], "valid captured input publishes a generation")
            generation_manifest = (tamper_root / "work/product/traceability/model-state/generations"
                                  / admitted.identity["digest"] / "manifest.json")
            manifest = json.loads(generation_manifest.read_text())
            passage = next(item for item in manifest["passages"].values()
                           if item.get("kind") == "context" and item.get("role") == "spec")
            passage["resolution"]["text"] = "Forged text outside captured source bytes."
            generation_manifest.write_text(json.dumps(manifest, sort_keys=True))
            try:
                load_published(tamper_root, "product")
            except (ValueError, OSError):
                pass
            else:
                review_failures.append("published derived passage text was accepted after tampering")

            publication_before = load_published(root, "product")
            calls = []
            bridge_path = str(project / ".agents/ask")
            sys.path.insert(0, bridge_path)
            try:
                from verification.traceability.cli import main as traceability_main
                error_output = StringIO()
                with redirect_stderr(error_output):
                    traceability_status = traceability_main([
                        "--root", str(root), "run", "product", "--scope", "task", "--task-id", "WB-003"])
                self.assertNotEqual(traceability_status, 0,
                                    "task-scoped traceability refuses a Task with missing selected passages")
                self.assertIn("EM015_CONTEXT_REQUIRED", error_output.getvalue())
            finally:
                sys.path.remove(bridge_path)
            from _ask.scripts.inner_loop.evidence import record_review
            try:
                record_review(root, "product", "WB-003", "reviewer", "_ask/policies/delegation.md",
                              "work/product/review.json", selected_task_id="task")
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_CONTEXT_REQUIRED",
                                 f"direct coordinator review helper must guard selected Task: {exc!r}")
            else:
                self.fail("direct review helper must refuse before review side effects for missing Task context")
            from _ask.scripts.inner_loop.driver import integrate_ready
            try:
                integrate_ready(root, "product", "WB-003")
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_CONTEXT_REQUIRED",
                                 f"driver integration must guard its explicit Task: {exc!r}")
            else:
                self.fail("driver integration must refuse before candidate reads for missing Task context")
            try:
                receipt = edit(root, "product", captured.identity["digest"],
                               lambda: calls.append("selected-task-action") or {"commands": [
                                   {"op": "revise_node", "id": "story", "changes": {"title": "Changed"}}]},
                               selected_task_id="task")
            except Exception as exc:
                self.fail(f"semantic edit must guard selected Task without API/runtime failure: {exc}")
            self.assertFalse(receipt["valid"], "required unresolved Task passages block the real edit entry")
            self.assertEqual(calls, [], "required unresolved Task passages must block before action")
            self.assertEqual(receipt["steps"], ["pre"], "selected Task refusal stops after one pre-check")
            self.assertEqual(receipt["validation_counts"], {"pre": 1, "post": 0})
            self.assertEqual(load_published(root, "product"), publication_before,
                             "selected Task refusal does not publish a generation")
            # The same unavailable context remains an admitted limitation for an
            # unrelated action; generic workflow admission must not make it global.
            with workflow_admission(root, "product"):
                calls.append("unrelated-decision")
            self.assertEqual(calls, ["unrelated-decision"])
            unrelated_publication = load_published(root, "product")
            try:
                with workflow_admission(root, "product", selected_task_id="task"):
                    calls.append("selected-workflow-action")
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_CONTEXT_REQUIRED",
                                 f"selected Task must refuse for its missing passages, got {exc!r}")
            else:
                self.fail("selected Task missing required passages must refuse before yielding")
            self.assertNotIn("selected-workflow-action", calls,
                             "missing required passages block only the selected Task action")
            try:
                with workflow_admission(root, "product", selected_execution={
                        "work_id": "other", "task_id": "WB-003"}):
                    calls.append("misjoined-execution")
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_TASK_ID",
                                 f"wrong qualified owner must not join by task label: {exc!r}")
            else:
                self.fail("execution task identity cannot join by an equal-looking task label alone")

            # An execution alias for another work cannot borrow this work's
            # same-named plan row. Its own qualified plan source remains valid.
            foreign = root / "foreign-execution"
            foreign.mkdir()
            _repo(foreign)
            foreign_doc = json.loads((foreign / "work/product/engineering-model.json").read_text())
            foreign_doc["nodes"][3]["execution"]["work_id"] = "other"
            foreign_doc["nodes"][3]["context"][1]["path"] = "work/product/plan.md"
            _put(foreign, "work/product/engineering-model.json", foreign_doc)
            try:
                with workflow_admission(foreign, "product", selected_execution={
                        "work_id": "other", "task_id": "WB-003"}):
                    calls.append("foreign-owner-borrowed-plan")
            except Exception as exc:
                if getattr(exc, "diagnostic", {}).get("code") != "EM015_CONTEXT_REQUIRED":
                    review_failures.append(f"foreign plan refusal had unexpected diagnostic: {exc!r}")
            if "foreign-owner-borrowed-plan" in calls:
                review_failures.append("a same-ID plan row from product satisfied other/WB-003")
            _put(foreign, "work/other/plan.md",
                 b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Other-owned contract |\n")
            foreign_doc["nodes"][3]["context"][1]["path"] = "work/other/plan.md"
            _put(foreign, "work/product/engineering-model.json", foreign_doc)
            try:
                with workflow_admission(foreign, "product", selected_execution={
                        "work_id": "other", "task_id": "WB-003"}):
                    calls.append("foreign-owner-own-plan")
            except Exception as exc:
                self.fail(f"qualified execution's own plan passage must admit: {exc}")
            self.assertEqual(calls[-1], "foreign-owner-own-plan")

            try:
                with workflow_admission(root, "product", selected_task_id="story",
                                        selected_execution={"work_id": "product", "task_id": "WB-003"}):
                    calls.append("contradictory-selection")
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_TASK_ID",
                                 f"contradictory product and execution identities refuse: {exc!r}")
            else:
                self.fail("contradictory product and execution selectors must refuse before action")
            self.assertEqual(load_published(root, "product"), unrelated_publication,
                             "contradictory selected identities cannot publish")

            # A resolvable neighboring plan row is not this Task's contract;
            # plan selector identity must match the captured execution alias.
            misbound = root / "misbound"
            misbound.mkdir()
            _repo(misbound, plan_text=("# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n"
                                       "| WB-003 | Selected |\n| WB-004 | Neighbor |\n"))
            model_doc = json.loads((misbound / "work/product/engineering-model.json").read_text())
            model_doc["nodes"][3]["context"][1]["selector"]["task_id"] = "WB-004"
            _put(misbound, "work/product/engineering-model.json", model_doc)
            try:
                with workflow_admission(misbound, "product", selected_task_id="task"):
                    calls.append("unrelated-plan-row")
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_CONTEXT_REQUIRED",
                                 f"resolved neighboring row must not satisfy selected execution: {exc!r}")
            else:
                self.fail("selected Task cannot borrow an unrelated plan-task row")

            unowned = root / "unowned"
            unowned.mkdir()
            _repo(unowned)
            unowned_doc = json.loads((unowned / "work/product/engineering-model.json").read_text())
            unowned_doc["nodes"][3].pop("execution")
            unowned_doc["nodes"][3]["context"][1]["selector"]["task_id"] = "task"
            _put(unowned, "work/product/engineering-model.json", unowned_doc)
            _put(unowned, "work/product/plan.md",
                 b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| task | Product task label |\n")
            try:
                with workflow_admission(unowned, "product", selected_task_id="task"):
                    calls.append("implicit-equal-id-join")
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_CONTEXT_REQUIRED",
                                 f"matching product label cannot invent an execution binding: {exc!r}")
            else:
                self.fail("plan row equality with product Task ID cannot invent execution ownership")

            _put(root, "docs/context.md", b"# Scope\nCurrent contract.\n")
            _put(root, "work/product/plan.md",
                 b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n")
            try:
                with workflow_admission(root, "product", selected_task_id="task"):
                    calls.append("selected-task-action")
            except Exception as exc:
                self.fail(f"selected Task contract admission must succeed after passages resolve: {exc}")
            self.assertEqual(calls[-1], "selected-task-action")
            with workflow_admission(root, "product", selected_task_id="task",
                                    selected_execution={"work_id": "product", "task_id": "WB-003"}):
                calls.append("consistent-dual-identity")
            self.assertEqual(calls[-1], "consistent-dual-identity",
                             "product and qualified execution selectors resolve to the same Task")

            # The actual coordinator review helper succeeds with a candidate
            # bound to the selected execution identity and captured passages.
            review_root = root / "review-success"
            review_root.mkdir()
            _repo(review_root)
            # Keep a second valid, empty task scope so the review-file race can
            # switch from a captured WB-003 target to a distinct WB-004 target.
            review_plan_path = review_root / "work/product/test-plan.json"
            review_plan = json.loads(review_plan_path.read_text())
            review_plan["task_scopes"].append({"task_id": "WB-004", "test_ids": []})
            _put(review_root, "work/product/test-plan.json", review_plan)
            review_model = json.loads((review_root / "work/product/engineering-model.json").read_text())
            review_model["nodes"][2]["case"]["plan_digest"] = digest(review_plan)
            _put(review_root, "work/product/engineering-model.json", review_model)
            _put(review_root, "work/product/inner-loop/tasks.yaml",
                 b"schema: ask-inner-loop-tasks/v1\nwork_id: product\ntasks:\n"
                 b"  - id: WB-003\n    depends_on: []\n    owned_paths: [task-result.md]\n"
                 b"  - id: WB-004\n    depends_on: []\n    owned_paths: [other-task-result.md]\n")
            shutil.copytree(project / "_ask/scripts", review_root / "_ask/scripts",
                            ignore=shutil.ignore_patterns("__pycache__"))
            _put(review_root, ".gitignore",
                 b"work/product/traceability/\nwork/product/inner-loop/state.*\n"
                 b"work/product/inner-loop/results/\nwork/product/inner-loop/evidence/\n"
                 b"**/__pycache__/\n*.pyc\n")
            _put(review_root, ".agents/verification.yaml",
                 b"schema: ask-checkplan/v1\nno_production_datastore: true\n"
                 b"checks:\n  - id: fixture\n    tier: mandatory\n    command: 'true'\n")
            _put(review_root, "_ask/policies/delegation.md", b"Independent coordinator review policy.\n")
            _put(review_root, "work/product/review.md", b"Reviewed candidate and its task boundary.\n")
            subprocess.run(["git", "init", "-q", "-b", "agent/product"], cwd=review_root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=review_root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=review_root, check=True)
            subprocess.run(["git", "add", "."], cwd=review_root, check=True)
            subprocess.run(["git", "commit", "-qm", "review fixture base"], cwd=review_root, check=True)
            from _ask.tests.traceability_support import accept as accept_traceability
            accept_traceability(review_root, "product")
            review_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=review_root, check=True,
                                        capture_output=True, text=True).stdout.strip()
            env = dict(os.environ, PYTHONPATH=str(review_root / ".agents/ask") + os.pathsep
                       + str(review_root / "_ask/scripts"))
            # The traceability CLI must inspect the actual review body before
            # publishing generic workstream admission. A default workstream
            # option cannot publish a task-scoped review against missing
            # required task context and only then report the scope mismatch.
            from _ask.scripts.engineering_model.admission import load_published as load_review_publication
            (review_root / "docs/context.md").unlink()
            self.assertIsNone(load_review_publication(review_root, "product"),
                              "scope-mismatch fixture starts without a publication")
            _put(review_root, "work/product/traceability/review-input-mismatch.json",
                 {"schema": "ask-test-review/v2", "scope": "task", "task_id": "WB-003"})
            mismatch_cli = subprocess.run(
                [sys.executable, "-c",
                 "from verification.traceability.cli import main; raise SystemExit(main(" + repr([
                     "--root", str(review_root), "record-review", "product", "--candidate-sha", review_sha,
                     "--anchor-sha", review_sha, "--recorded-by", "fixture-coordinator",
                     "--evidence", "work/product/traceability/review-input-mismatch.json"
                 ]) + "))"], cwd=review_root, env=env, capture_output=True, text=True)
            self.assertNotEqual(mismatch_cli.returncode, 0, "default workstream scope rejects a task review body")
            self.assertIsNone(load_review_publication(review_root, "product"),
                              "scope-mismatched task review must not publish a generic generation")
            _put(review_root, "docs/context.md", b"# Scope\nCurrent contract.\n")
            red_run = subprocess.run(
                [sys.executable, "-c",
                 "from verification.traceability.cli import main; raise SystemExit(main(" + repr([
                     "--root", str(review_root), "run", "product", "--candidate-sha", review_sha,
                     "--anchor-sha", review_sha, "--scope", "task", "--task-id", "WB-003", "--phase", "red"
                 ]) + "))"], cwd=review_root, env=env, capture_output=True, text=True)
            self.assertEqual(red_run.returncode, 0,
                             f"task-scoped red command records the genuine missing-result assertion: {red_run.stderr}")
            subprocess.run(["git", "switch", "-qc", "task/selected"], cwd=review_root, check=True)
            _put(review_root, "task-result.md", b"Candidate owned by WB-003.\n")
            subprocess.run(["git", "add", "task-result.md"], cwd=review_root, check=True)
            subprocess.run(["git", "commit", "-qm", "selected task candidate"], cwd=review_root, check=True)
            candidate_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=review_root, check=True,
                                           capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "switch", "-q", "agent/product"], cwd=review_root, check=True)
            from _ask.tests.traceability_support import digest as contract_digest
            from verification.traceability.evidence import (inventory, load_accepted, source_digests,
                                                            write_json)
            contracts = load_accepted(review_root, "product", review_sha, candidate_sha)
            selected_tests = ["WB-publish"]
            inv = inventory(review_root, contracts["pin"]["contract_sha"], candidate_sha, contracts["plan"])
            review_input = {
                "schema": "ask-test-review/v2", "reviewer": "fixture-reviewer",
                "candidate_sha": candidate_sha, "base_sha": contracts["pin"]["contract_sha"],
                "spec_digest": contract_digest(contracts["spec"]),
                "plan_digest": contract_digest(contracts["plan"]), "scope": "task",
                "task_id": "WB-003", "test_ids": selected_tests, "criterion_ids": ["EM-007"],
                "source_digests": source_digests(review_root, candidate_sha, contracts["plan"], selected_tests),
                "inspected_sources": inv["inspected_sources"], "changed_cases": inv["changed_cases"],
                "inventory_exclusions": {name: "Disposable integration fixture." for name in inv["unmapped_cases"]},
                "criteria": [{"id": "EM-007", "coverage_decision": "APPROVED",
                              "assessment": "Selected passage integration check covers the obligation.",
                              "type_adequacy": {"unit": {"decision": "APPROVED", "assessment": "The unit case checks the selection boundary."}}}],
                "tests": [{"id": "WB-publish", "decision": "APPROVED",
                           "assertion_assessment": "The fixture asserts the selected result.",
                           "counterexample": "A different selected result fails.",
                           "tdd_continuity_assessment": "Red and green execution are bound to the accepted test."}],
            }
            write_json(review_root / "work/product/traceability/review-input.json", review_input)
            race_review = dict(review_input, task_id="WB-004", test_ids=[], criterion_ids=[],
                               source_digests={}, criteria=[], tests=[])
            race_review_path = review_root / "work/product/traceability/review-input-race.json"
            write_json(race_review_path, review_input)
            env = dict(os.environ, PYTHONPATH=str(review_root / ".agents/ask") + os.pathsep
                       + str(review_root / "_ask/scripts"))
            record_review_run = subprocess.run(
                [sys.executable, "-c",
                 "from verification.traceability.cli import main; raise SystemExit(main(" + repr([
                     "--root", str(review_root), "record-review", "product", "--candidate-sha", candidate_sha,
                     "--anchor-sha", review_sha, "--recorded-by", "fixture-coordinator",
                     "--evidence", "work/product/traceability/review-input.json", "--scope", "task", "--task-id", "WB-003"
                 ]) + "))"], cwd=review_root, env=env, capture_output=True, text=True)
            self.assertEqual(record_review_run.returncode, 0,
                             f"real task-scoped traceability review wrapper accepts selected context: {record_review_run.stderr}")
            review_record = review_root / "work/product/traceability/reviews" / (candidate_sha + ".json")
            accepted_review_record = review_record.read_bytes()

            # The target, semantic validation and persisted review must all use
            # one captured review document even if the input file changes
            # between the caller's first read and publication.
            candidate_scripts = str(review_root / "_ask/scripts")
            candidate_bridge = str(review_root / ".agents/ask")
            sys.path[:0] = [candidate_scripts, candidate_bridge]
            try:
                from unittest.mock import patch
                import verification.traceability.evidence as candidate_evidence
                import verification.traceability.cli as candidate_cli
                from verification.traceability.evidence import record_test_review as candidate_record_test_review

                original_evidence_load = candidate_evidence.load
                direct_swap = {"done": False}
                def swap_after_direct_read(path):
                    result = original_evidence_load(path)
                    if Path(path).resolve() == race_review_path.resolve() and not direct_swap["done"]:
                        direct_swap["done"] = True
                        write_json(race_review_path, race_review)
                    return result
                write_json(race_review_path, review_input)
                with patch.object(candidate_evidence, "load", side_effect=swap_after_direct_read):
                    direct_race = candidate_record_test_review(
                        review_root, "product", candidate_sha, review_sha,
                        "work/product/traceability/review-input-race.json", "fixture-coordinator")
                if direct_race.get("review", {}).get("task_id") != "WB-003":
                    review_failures.append("direct review recorded the replacement WB-004 body under WB-003 admission")

                original_cli_load = candidate_cli.load
                cli_swap = {"done": False}
                def swap_after_cli_read(path):
                    result = original_cli_load(path)
                    if Path(path).resolve() == race_review_path.resolve() and not cli_swap["done"]:
                        cli_swap["done"] = True
                        write_json(race_review_path, race_review)
                    return result
                write_json(race_review_path, review_input)
                with patch.object(candidate_cli, "load", side_effect=swap_after_cli_read):
                    cli_race_status = candidate_cli.main([
                        "--root", str(review_root), "record-review", "product",
                        "--candidate-sha", candidate_sha, "--anchor-sha", review_sha,
                        "--recorded-by", "fixture-coordinator", "--evidence",
                        "work/product/traceability/review-input-race.json", "--scope", "task", "--task-id", "WB-003"])
                if cli_race_status != 0:
                    review_failures.append("CLI changed-body race refused instead of using its captured WB-003 review")
                recorded_race = json.loads(review_record.read_text())
                if recorded_race.get("review", {}).get("task_id") != "WB-003":
                    review_failures.append("CLI persisted replacement WB-004 review under WB-003 admission")
                review_record.write_bytes(accepted_review_record)
            finally:
                sys.path.remove(candidate_bridge)
                sys.path.remove(candidate_scripts)

            prior_review_bytes = review_record.read_bytes()
            omitted_scope = subprocess.run(
                [sys.executable, "-c",
                 "from verification.traceability.cli import main; raise SystemExit(main(" + repr([
                     "--root", str(review_root), "record-review", "product", "--candidate-sha", candidate_sha,
                     "--anchor-sha", review_sha, "--recorded-by", "fixture-coordinator",
                     "--evidence", "work/product/traceability/review-input.json"
                 ]) + "))"], cwd=review_root, env=env, capture_output=True, text=True)
            if omitted_scope.returncode == 0:
                review_failures.append("CLI workstream default accepted task-scoped review body")
            self.assertEqual(review_record.read_bytes(), prior_review_bytes,
                             "CLI/body scope mismatch refuses before review publication")

            # Direct review API derives the actual task from its body instead of
            # letting omission of the optional selector disable task context.
            sys.path[:0] = [candidate_scripts, candidate_bridge]
            try:
                from verification.traceability.evidence import record_test_review as candidate_record_test_review
                (review_root / "docs/context.md").unlink()
                try:
                    candidate_record_test_review(review_root, "product", candidate_sha, review_sha,
                                                "work/product/traceability/review-input.json",
                                                "fixture-coordinator")
                except Exception as exc:
                    if "EM015_CONTEXT_REQUIRED" not in str(exc):
                        review_failures.append(f"direct API refused with wrong diagnostic: {exc!r}")
                else:
                    review_failures.append("direct task review bypassed required context without selected_execution")
                self.assertEqual(review_record.read_bytes(), prior_review_bytes,
                                 "missing-context direct review does not replace the retained review")
                _put(review_root, "docs/context.md", b"# Scope\nCurrent contract.\n")
            finally:
                sys.path.remove(candidate_bridge)
                sys.path.remove(candidate_scripts)

            # Actual coordinator task-start paths must bind the concrete task
            # before changing writer state. Recheck both refusal and success.
            start_scripts = str(review_root / "_ask/scripts")
            sys.path.insert(0, start_scripts)
            try:
                from inner_loop.state import cas_init, load_state
                from inner_loop.driver import run_once
                from inner_loop.__main__ import main as inner_loop_main

                for route in ("driver", "cli"):
                    start_root = root / ("missing-context-start-" + route)
                    start_root.mkdir()
                    _repo(start_root, spec_text=None)
                    shutil.copytree(project / "_ask/scripts", start_root / "_ask/scripts",
                                    ignore=shutil.ignore_patterns("__pycache__"))
                    cas_init(start_root, "product", ["WB-003"])
                    state_before = load_state(start_root, "product")
                    publication_before_start = load_published(start_root, "product")
                    try:
                        if route == "driver":
                            run_once(start_root, "product")
                        else:
                            cli_error = StringIO()
                            with redirect_stderr(cli_error):
                                cli_status = inner_loop_main(["--root", str(start_root), "spawn-writer",
                                                              "product", "WB-003"])
                            if cli_status == 0:
                                review_failures.append("cli task start bypassed missing selected context")
                            elif "EM015_CONTEXT_REQUIRED" not in cli_error.getvalue():
                                review_failures.append("cli task start refused with wrong diagnostic")
                    except Exception as exc:
                        if getattr(exc, "diagnostic", {}).get("code") != "EM015_CONTEXT_REQUIRED":
                            review_failures.append(f"{route} task start refused with wrong diagnostic: {exc!r}")
                    else:
                        if route == "driver":
                            review_failures.append(f"{route} task start bypassed missing selected context")
                    if route == "driver" and load_state(start_root, "product")["tasks"]["WB-003"]["status"] == "running":
                        review_failures.append(f"{route} task start bypassed missing selected context")
                    if load_state(start_root, "product") != state_before:
                        review_failures.append(f"{route} missing-context refusal changed writer state")
                    if load_published(start_root, "product") != publication_before_start:
                        review_failures.append(f"{route} missing-context refusal published a candidate")

                    valid_root = root / ("valid-context-start-" + route)
                    valid_root.mkdir()
                    _repo(valid_root)
                    shutil.copytree(project / "_ask/scripts", valid_root / "_ask/scripts",
                                    ignore=shutil.ignore_patterns("__pycache__"))
                    cas_init(valid_root, "product", ["WB-003"])
                    if route == "driver":
                        self.assertEqual(run_once(valid_root, "product"), "running=WB-003")
                    else:
                        self.assertEqual(inner_loop_main(["--root", str(valid_root), "spawn-writer",
                                                          "product", "WB-003"]), 0)
                    self.assertEqual(load_state(valid_root, "product")["tasks"]["WB-003"]["status"],
                                     "running", f"{route} explicit owner task start remains available")
                    valid_publication = load_published(valid_root, "product")
                    self.assertIsNotNone(valid_publication, f"{route} publishes its captured valid inputs")
                    publication_files = list((valid_root / "work/product/traceability/model-state/publications").glob("*.json"))
                    self.assertEqual(len(publication_files), 1,
                                     f"{route} task start creates one admission publication")
                    event = json.loads(publication_files[0].read_text())
                    self.assertEqual(event["result_digest"], valid_publication.identity["digest"],
                                     f"{route} publication binds the captured task-start input generation")
            finally:
                sys.path.remove(start_scripts)
            sys.path.insert(0, candidate_scripts)
            try:
                from inner_loop.state import cas_init, cas_apply
                from inner_loop.evidence import record_review as candidate_record_review
                cas_init(review_root, "product", ["WB-003"], coordinator_sha=review_sha)
                cas_apply(review_root, "product", 0, lambda state: state["tasks"]["WB-003"].update(
                    status="running", base_sha=review_sha, task_branch="task/selected"))
                _put(review_root, "work/product/inner-loop/results/WB-003.json", {
                    "schema": "ask-task-result/v2", "work_id": "product", "task_id": "WB-003",
                    "base_sha": review_sha, "candidate_sha": candidate_sha,
                    "tdd": {"seam": "task", "red": {"command": "red", "output": "FAIL", "exit_code": 1},
                            "green": {"command": "green", "output": "PASS", "exit_code": 0}},
                    "exemption": None,
                })
                review = candidate_record_review(
                    review_root, "product", "WB-003", "independent-reviewer",
                    "_ask/policies/delegation.md", "work/product/review.md",
                    selected_execution={"work_id": "product", "task_id": "WB-003"})
                self.assertEqual(review["candidate_sha"], candidate_sha)
                self.assertEqual(review["task_id"], "WB-003")
                self.assertEqual(review["verdict"], "APPROVED")
                from inner_loop.driver import integrate_ready as candidate_integrate_ready
                from inner_loop.evidence import source_changes as candidate_source_changes
                self.assertEqual(candidate_source_changes(review_root, "product"), [],
                                 "fixture runtime evidence stays outside coordinator source changes")
                self.assertEqual(candidate_integrate_ready(review_root, "product", "WB-003"), candidate_sha,
                                 "actual driver validates, reviews, verifies and fast-forwards selected candidate")
                integrated = json.loads((review_root / "work/product/inner-loop/state.json").read_text())
                self.assertEqual(integrated["tasks"]["WB-003"]["status"], "integrated")
                self.assertEqual(integrated["coordinator_sha"], candidate_sha)

                # Inner-loop integration of kit TaskResults is legal for an
                # unadopted workstream; no product execution alias exists to
                # pass through the adopted-model guard.
                unadopted_root = root / "unadopted-integrate-ready"
                unadopted_root.mkdir()
                _put(unadopted_root, "work/product/inner-loop/tasks.yaml",
                     b"schema: ask-inner-loop-tasks/v1\nwork_id: product\ntasks:\n"
                     b"  - id: WB-003\n    depends_on: []\n    owned_paths: [task-result.md]\n")
                subprocess.run(["git", "init", "-q", "-b", "agent/product"], cwd=unadopted_root, check=True)
                subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=unadopted_root, check=True)
                subprocess.run(["git", "config", "user.name", "Test"], cwd=unadopted_root, check=True)
                subprocess.run(["git", "add", "."], cwd=unadopted_root, check=True)
                subprocess.run(["git", "commit", "-qm", "unadopted inner-loop fixture"], cwd=unadopted_root, check=True)
                cas_init(unadopted_root, "product", ["WB-003"])
                cas_apply(unadopted_root, "product", 0, lambda state: state["tasks"]["WB-003"].update(
                    status="running", base_sha=review_sha, task_branch="task/selected"))
                try:
                    candidate_integrate_ready(unadopted_root, "product", "WB-003")
                except Exception as exc:
                    self.assertIn("missing or invalid TaskResult", str(exc),
                                  "unadopted integration must reach task-result validation, not require a model alias")
                else:
                    self.fail("integration without the required TaskResult unexpectedly advanced")

                # Preserve the v1 direct integration API, which has no
                # execution-alias field to select.
                legacy_root = root / "legacy-v1"
                legacy_root.mkdir()
                from _ask.tests.engineering_fixture import workbench_model
                workbench_model(legacy_root)
                _put(legacy_root, "specs/current/pilot.md", b"# Pilot requirements\n")
                shutil.copytree(project / "_ask/scripts", legacy_root / "_ask/scripts",
                                ignore=shutil.ignore_patterns("__pycache__"))
                shutil.copytree(project / ".agents/ask/verification", legacy_root / ".agents/ask/verification",
                                ignore=shutil.ignore_patterns("__pycache__"))
                _put(legacy_root, ".gitignore", b"**/__pycache__/\n*.pyc\nwork/pilot/traceability/\n")
                subprocess.run(["git", "init", "-q", "-b", "agent/pilot"], cwd=legacy_root, check=True)
                subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=legacy_root, check=True)
                subprocess.run(["git", "config", "user.name", "Test"], cwd=legacy_root, check=True)
                subprocess.run(["git", "add", "."], cwd=legacy_root, check=True)
                subprocess.run(["git", "commit", "-qm", "valid v1 base"], cwd=legacy_root, check=True)
                subprocess.run(["git", "switch", "-qc", "task/legacy"], cwd=legacy_root, check=True)
                _put(legacy_root, "legacy-result.txt", b"v1 task output\n")
                subprocess.run(["git", "add", "legacy-result.txt"], cwd=legacy_root, check=True)
                subprocess.run(["git", "commit", "-qm", "v1 candidate"], cwd=legacy_root, check=True)
                legacy_candidate = subprocess.run(["git", "rev-parse", "HEAD"], cwd=legacy_root, check=True,
                                                  capture_output=True, text=True).stdout.strip()
                subprocess.run(["git", "switch", "-q", "agent/pilot"], cwd=legacy_root, check=True)
                legacy_env = dict(os.environ, PYTHONPATH=str(legacy_root / "_ask/scripts") + os.pathsep
                                  + str(legacy_root / ".agents/ask"))
                legacy_integrate = subprocess.run(
                    [sys.executable, "-c",
                     "from inner_loop.__main__ import main; raise SystemExit(main(" + repr([
                         "--root", str(legacy_root), "integrate", "--task-ref", "task/legacy"
                     ]) + "))"], cwd=legacy_root, env=legacy_env, capture_output=True, text=True)
                self.assertEqual(legacy_integrate.returncode, 0,
                                 f"valid v1 direct integration remains compatible: {legacy_integrate.stderr}")
                self.assertEqual((legacy_root / ".git/refs/heads/agent/pilot").read_text().strip(), legacy_candidate)

                # Adopted v1 documents have no execution-alias field. Shared
                # callers that know a Task ID must keep their legacy behavior.
                legacy_routes = root / "legacy-v1-routes"
                legacy_routes.mkdir()
                workbench_model(legacy_routes)
                shutil.copytree(project / "_ask/scripts", legacy_routes / "_ask/scripts",
                                ignore=shutil.ignore_patterns("__pycache__"))
                shutil.copytree(project / ".agents/ask/verification", legacy_routes / ".agents/ask/verification",
                                ignore=shutil.ignore_patterns("__pycache__"))
                shutil.copytree(project / "_ask/policies", legacy_routes / "_ask/policies",
                                ignore=shutil.ignore_patterns("__pycache__"))
                _put(legacy_routes, ".gitignore", b"**/__pycache__/\n*.pyc\nwork/pilot/traceability/\n")
                subprocess.run(["git", "init", "-q", "-b", "agent/pilot"], cwd=legacy_routes, check=True)
                subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=legacy_routes, check=True)
                subprocess.run(["git", "config", "user.name", "Test"], cwd=legacy_routes, check=True)
                subprocess.run(["git", "add", "."], cwd=legacy_routes, check=True)
                subprocess.run(["git", "commit", "-qm", "valid legacy v1 model"], cwd=legacy_routes, check=True)
                legacy_scripts = str(legacy_routes / "_ask/scripts")
                legacy_bridge = str(legacy_routes / ".agents/ask")
                sys.path[:0] = [legacy_scripts, legacy_bridge]
                try:
                    from inner_loop.driver import run_once as legacy_run_once, integrate_ready as legacy_integrate_ready
                    from inner_loop.state import load_state, cas_apply
                    from inner_loop.evidence import result_path, record_review as legacy_record_review, NotIntegrable
                    from inner_loop.__main__ import main as legacy_inner_main
                    from verification.run import workflow_context as legacy_workflow_context
                    try:
                        legacy_start = legacy_run_once(legacy_routes, "pilot")
                    except Exception as exc:
                        self.fail(f"legacy v1 driver must start its planned Task without an execution alias: {exc!r}")
                    self.assertEqual(legacy_start, "running=build",
                                     "legacy v1 driver starts its planned Task without an execution alias")
                    try:
                        legacy_integrate_ready(legacy_routes, "pilot", "build")
                    except Exception as exc:
                        self.assertIsInstance(exc, NotIntegrable,
                                              f"legacy integration proceeds past context admission: {exc!r}")
                        self.assertIn("TaskResult", str(exc),
                                      "legacy integration proceeds past context admission to result validation")
                    else:
                        self.fail("integration must require a TaskResult after legacy context admission")
                    with legacy_workflow_context(legacy_routes, "pilot", selected_execution={
                            "work_id": "pilot", "task_id": "build"}) as legacy_snapshot:
                        self.assertEqual(legacy_snapshot.document["schema"], "ask-engineering-model/v1",
                                         "verification bridge preserves selected task calls for v1")
                    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=legacy_routes, check=True,
                                          capture_output=True, text=True).stdout.strip()
                    task_state = load_state(legacy_routes, "pilot")
                    cas_apply(legacy_routes, "pilot", task_state["revision"], lambda state: state["tasks"]["build"].update(
                        base_sha=head, task_branch="agent/pilot"))
                    result_path(legacy_routes, "pilot", "build").parent.mkdir(parents=True, exist_ok=True)
                    _put(legacy_routes, "work/pilot/inner-loop/results/build.json", {
                        "schema": "ask-task-result/v2", "work_id": "pilot", "task_id": "build",
                        "base_sha": head, "candidate_sha": head,
                        "tdd": {"seam": "legacy route", "red": {"command": "red", "output": "FAIL", "exit_code": 1},
                                "green": {"command": "green", "output": "PASS", "exit_code": 0}},
                        "exemption": None})
                    _put(legacy_routes, "work/pilot/legacy-review.md", b"Legacy review evidence.\n")
                    legacy_review = legacy_record_review(
                        legacy_routes, "pilot", "build", "fixture-reviewer",
                        "_ask/policies/delegation.md", "work/pilot/legacy-review.md")
                    self.assertEqual(legacy_review["task_id"], "build",
                                     "direct coordinator review preserves the v1 task route")
                    self.assertEqual(legacy_inner_main([
                        "--root", str(legacy_routes), "record-review", "pilot", "build",
                        "--reviewer", "fixture-reviewer", "--evidence", "work/pilot/legacy-review.md"]), 0,
                        "CLI coordinator review preserves the v1 task route")
                finally:
                    sys.path.remove(legacy_bridge)
                    sys.path.remove(legacy_scripts)

                legacy_spawn = root / "legacy-v1-spawn"
                legacy_spawn.mkdir()
                workbench_model(legacy_spawn)
                shutil.copytree(project / "_ask/scripts", legacy_spawn / "_ask/scripts",
                                ignore=shutil.ignore_patterns("__pycache__"))
                legacy_sys_path = str(legacy_spawn / "_ask/scripts")
                sys.path.insert(0, legacy_sys_path)
                try:
                    from inner_loop.state import cas_init as legacy_cas_init, load_state as legacy_load_state
                    from inner_loop.__main__ import main as legacy_inner_main
                    legacy_cas_init(legacy_spawn, "pilot", ["build"])
                    try:
                        legacy_spawn_status = legacy_inner_main(["--root", str(legacy_spawn), "spawn-writer", "pilot", "build"])
                    except Exception as exc:
                        self.fail(f"legacy v1 CLI writer admission must remain available: {exc!r}")
                    self.assertEqual(legacy_spawn_status, 0,
                                     "legacy v1 CLI writer admission remains available")
                    self.assertEqual(legacy_load_state(legacy_spawn, "pilot")["tasks"]["build"]["status"], "running")
                finally:
                    sys.path.remove(legacy_sys_path)
            finally:
                sys.path.remove(candidate_scripts)
            self.assertFalse(is_current(captured, root), "newly available passages invalidate old admission")

            before = capture(root, "product")
            action_calls = []
            receipt = edit(root, "product", before.identity["digest"],
                           lambda: action_calls.append("semantic-batch") or {"commands": [
                               {"op": "revise_node", "id": "story", "changes": {"title": "Revised"}}]},
                           selected_task_id="task")
            self.assertTrue(receipt["valid"], "selected Task semantic batch succeeds with both exact passages")
            self.assertEqual(receipt["steps"], ["pre", "action", "post", "publication"])
            self.assertEqual(action_calls, ["semantic-batch"], "semantic proposal executes exactly once")
            self.assertEqual(receipt["input_snapshot"]["digest"], before.identity["digest"])
            self.assertEqual(receipt["snapshot"]["digest"], load_published(root, "product").identity["digest"])

            published_generation = load_published(root, "product")
            sys.path.insert(0, bridge_path)
            try:
                from verification.run import workflow_context
                with workflow_context(root, "product", selected_execution={
                        "work_id": "product", "task_id": "WB-003"}) as bridged:
                    self.assertEqual(bridged.identity["digest"], published_generation.identity["digest"])
            finally:
                sys.path.remove(bridge_path)

            # Exercise the shipped model admit-with-action CLI, not a mocked
            # callback. Its subprocess writes a marker only after admission.
            from _ask.scripts.engineering_model.__main__ import main as model_main
            previous = Path.cwd()
            try:
                os.chdir(root)
                exit_code = model_main(["admit", "--work-id", "product", "--task-node", "task",
                                        "--action", "selected-task", "--", sys.executable, "-c",
                                        "from pathlib import Path; Path('cli-action-ran').write_text('yes')"])
            finally:
                os.chdir(previous)
            self.assertEqual(exit_code, 0, "real model admit-with-action wrapper accepts selected context")
            self.assertEqual((root / "cli-action-ran").read_text(), "yes")

        # The actual candidate/integration boundary receives a qualified task
        # selector and refuses missing passages before moving the ref; once the
        # passages are committed, a real FF integration preserves the SHA.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root, spec_text=None)
            project = Path(__file__).resolve().parents[2]
            shutil.copytree(project / "_ask/scripts", root / "_ask/scripts")
            subprocess.run(["git", "init", "-q", "-b", "agent/product"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "canonical fixture"], cwd=root, check=True)
            original_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                          capture_output=True, text=True).stdout.strip()
            from _ask.scripts.inner_loop.integrate import integrate
            try:
                integrate(root, original_sha, work_id="product", selected_execution={
                    "work_id": "product", "task_id": "WB-003"})
            except Exception as exc:
                self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM015_CONTEXT_REQUIRED",
                                 f"candidate integration must refuse missing selected passages: {exc!r}")
            else:
                self.fail("real candidate integration must refuse missing selected passages")
            still_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                       capture_output=True, text=True).stdout.strip()
            self.assertEqual(still_sha, original_sha, "refusal leaves the integration ref unchanged")
            _put(root, "docs/context.md", b"# Scope\nCommitted context.\n")
            _put(root, "work/product/plan.md",
                 b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "selected context"], cwd=root, check=True)
            subprocess.run(["git", "switch", "-qc", "task/selected"], cwd=root, check=True)
            _put(root, "task-result.md", b"Selected task result.\n")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "task result"], cwd=root, check=True)
            candidate_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                          capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "switch", "-q", "agent/product"], cwd=root, check=True)
            result_sha = integrate(root, candidate_sha, work_id="product", selected_execution={
                "work_id": "product", "task_id": "WB-003"})
            self.assertEqual(result_sha, candidate_sha, "valid selected context passes candidate and FF integration")

        self.assertEqual(review_failures, [], "each review finding must be independently rejected")

    def test_missing_linked_and_ambiguous_changes_invalidate_snapshot(self):
        from _ask.scripts.engineering_model.admission import admit, load_published
        from _ask.scripts.engineering_model.observer import observe_once
        from _ask.scripts.engineering_model.validation import validate
        from _ask.tests.revising_fixture import digest, reviewed_mapping

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root, spec_text="# Scope\nA contract.\n")

            # A foreign Scenario source and both sides of its reviewed mapping
            # belong to the captured dependency closure, even if direct
            # filesystem validation can see them already.
            document = json.loads((root / "work/product/engineering-model.json").read_text())
            product_plan = json.loads((root / "work/product/test-plan.json").read_text())
            foreign_spec = json.loads((root / "specs/current/product.json").read_text())
            foreign_spec["work_id"] = "foreign"
            foreign_plan = dict(product_plan)
            foreign_plan["work_id"] = "foreign"
            foreign_plan["spec_digest"] = digest(foreign_spec)
            foreign_plan["task_scopes"] = []
            foreign_plan["flow_mappings"] = [reviewed_mapping(
                {"scope": "local", "case_id": "WB-publish"},
                {"scope": "external", "work_id": "product", "plan_digest": digest(product_plan),
                 "case_id": "WB-publish"})]
            document["nodes"][2]["case"] = {"work_id": "foreign", "plan_digest": digest(foreign_plan),
                                             "case_id": "WB-publish"}
            document["nodes"][4]["reference"] = {"path": "work/product/test-plan.json", "id": "WB-publish",
                                                  "work_id": "product", "plan_digest": digest(product_plan)}
            _put(root, "work/product/engineering-model.json", document)
            _put(root, "work/foreign/test-plan.json", foreign_plan)
            _put(root, "specs/current/foreign.json", foreign_spec)
            _put(root, "specs/current/foreign.md", b"# Foreign requirements\nSame validated scope.\n")
            self.assertEqual(validate(document, root, "product"), [],
                             "direct source resolution accepts the reviewed foreign-to-local relation")
            foreign_capture = capture(root, "product")
            self.assertIn("work/foreign/test-plan.json", foreign_capture.files,
                          "foreign selected Scenario plan is part of the captured dependency closure")
            self.assertEqual(foreign_capture.diagnostics(root), [],
                             "captured validation uses the same foreign-plan bytes as direct validation")

            # Restore the ordinary local fixture so the remaining freshness
            # transitions stay isolated from this foreign-flow probe.
            _repo(root, spec_text="# Scope\nA contract.\n")
            first = capture(root, "product")
            first_identity = first.identity
            passages = getattr(first, "passages", None)
            self.assertIsNotNone(passages, "snapshot exposes captured selector states")
            if passages is None:
                return
            self.assertTrue(is_current(first, root))
            published, diagnostics = admit(root, "product")
            self.assertEqual(diagnostics, [])
            read_passage = getattr(published, "resolve_passage", None)
            self.assertTrue(callable(read_passage), "admitted snapshot reads its own captured passage")
            if not callable(read_passage):
                return
            historical_text = read_passage("task", "spec")
            self.assertIn("A contract", historical_text["text"])

            spec_path = root / "docs/context.md"
            old_stat = spec_path.stat()
            spec_path.write_text("# Scope\nA materially changed contract.\n", encoding="utf-8")
            os.utime(spec_path, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
            self.assertFalse(is_current(first, root), "same-mtime linked-only edits invalidate captured bytes")
            second = capture(root, "product")
            self.assertNotEqual(first_identity["digest"], second.identity["digest"])
            self.assertIn("A contract", historical_text["text"], "published passage remains historical")

            helper_path = root / "tests/helpers.py"
            helper_stat = helper_path.stat()
            helper_path.write_bytes(b"def assert_publish():\n    assert False\n")
            os.utime(helper_path, ns=(helper_stat.st_atime_ns, helper_stat.st_mtime_ns))
            self.assertFalse(is_current(second, root), "captured source_context helper bytes are dependencies")
            after_helper = capture(root, "product")
            fresh, errors = admit(root, "product")
            self.assertEqual(errors, [])
            self.assertIsNotNone(fresh, "fresh helper-bound admission returns a snapshot")
            observation = observe_once(root, "product")
            self.assertTrue(observation["valid"], "startup/read recaptures helper changes before publication")
            self.assertEqual(observation["snapshot"]["digest"], after_helper.identity["digest"])
            self.assertEqual(observation["snapshot"]["digest"], observation["current_input"]["digest"],
                             "observer reads one current published generation")
            from _ask.scripts.engineering_model.admission import validate_current
            full, full_errors = validate_current(root, "product")
            cached, cached_errors = admit(root, "product")
            self.assertEqual(full_errors, cached_errors, "full and current validation agree")
            self.assertEqual(full.identity, cached.identity, "validation paths share captured dependency closure")

            # A helper or linked-context edit after a selected pre-check makes
            # the actual nested semantic action stale before its callback.
            from _ask.scripts.engineering_model.workflow import workflow_admission
            from _ask.scripts.engineering_model.actions import edit
            for changed_path, changed_bytes in (
                    ("docs/context.md", b"# Scope\nLate linked contract.\n"),
                    ("tests/helpers.py", b"def assert_publish():\n    assert 'late'\n")):
                stale_root = root / ("stale-action-" + Path(changed_path).stem)
                stale_root.mkdir()
                _repo(stale_root)
                baseline, baseline_errors = admit(stale_root, "product")
                self.assertEqual(baseline_errors, [])
                prior_publication = load_published(stale_root, "product")
                model_before = (stale_root / "work/product/engineering-model.json").read_bytes()
                action_calls = []
                try:
                    with workflow_admission(stale_root, "product", selected_task_id="task") as selected:
                        stale_source = stale_root / changed_path
                        source_stat = stale_source.stat()
                        stale_source.write_bytes(changed_bytes)
                        os.utime(stale_source, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
                        edit(stale_root, "product", selected.identity["digest"],
                             lambda: action_calls.append("stale-action") or {"commands": []},
                             selected_task_id="task")
                except Exception as exc:
                    self.assertEqual(getattr(exc, "diagnostic", {}).get("code"), "EM007_INPUT_CHANGED",
                                     f"stale {changed_path} refuses before selected action: {exc!r}")
                else:
                    self.fail(f"selected action must refuse a late {changed_path} change")
                self.assertEqual(action_calls, [], f"stale {changed_path} never reaches the action callback")
                self.assertEqual((stale_root / "work/product/engineering-model.json").read_bytes(), model_before)
                retained = load_published(stale_root, "product")
                self.assertEqual(retained.identity, prior_publication.identity,
                                 f"stale {changed_path} cannot publish a candidate generation")

            # A safe optional missing passage remains admitted; creating it
            # changes identity and the captured state from unavailable to unique.
            missing_root = root / "missing-target"
            missing_root.mkdir()
            _repo(missing_root, spec_text=None)
            missing = capture(missing_root, "product")
            self.assertEqual(missing.resolve_passage("task", "spec")["state"], "unavailable")
            self.assertEqual(admit(missing_root, "product")[1], [])
            _put(missing_root, "docs/context.md", b"# Scope\nCreated context.\n")
            created = capture(missing_root, "product")
            self.assertNotEqual(missing.identity["digest"], created.identity["digest"])
            self.assertEqual(created.resolve_passage("task", "spec")["state"], "available")
            self.assertFalse(is_current(missing, missing_root))

            selected_only = json.loads((missing_root / "work/product/engineering-model.json").read_text())
            selected_only["nodes"][3]["context"][0]["selector"]["path"] = ["Different"]
            _put(missing_root, "work/product/engineering-model.json", selected_only)
            selector_changed = capture(missing_root, "product")
            self.assertNotEqual(created.identity["digest"], selector_changed.identity["digest"],
                                "selector-only changes participate in snapshot identity")

            plan_path = root / "work/product/plan.md"
            _put(root, "work/product/plan.md",
                 b"# Work breakdown\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | First |\n")
            unique = capture(root, "product")
            _put(root, "work/product/plan.md",
                 b"# Work breakdown\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | First |\n\n# Work breakdown\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Duplicate |\n")
            ambiguous = capture(root, "product")
            self.assertFalse(is_current(unique, root), "unique-to-ambiguous passage transition stales the snapshot")
            self.assertNotEqual(unique.identity["digest"], ambiguous.identity["digest"])
            plan_path.unlink()
            self.assertFalse(is_current(ambiguous, root), "target deletion invalidates the captured identity")
