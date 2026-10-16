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
            "task_scopes": [],
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
    _put(root, "specs/current/product.md", b"# Product requirements\nCanonical specification companion.\n")
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

        table = b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n| WB-004 | Review safely |\n"
        selected = resolve("work/plan.md", table,
                           {"kind": "plan-task", "heading_path": ["Work breakdown"], "task_id": "WB-003"})
        self.assertEqual(selected["state"], "available")
        self.assertEqual(selected["text"], "| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n")
        self.assertNotIn("WB-004", selected["text"], "selection excludes adjacent plan rows")
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
            self.assertEqual(identity["dependency_discovery_version"], "engineering-input-closure/v2")
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
            self.assertEqual(missing_blob.resolve_passage("task", "spec")["state"], "error",
                             "a missing historical blob cannot fall back to current bytes")
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

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root, spec_text=None, plan_text="# Work breakdown\n")
            project = Path(__file__).resolve().parents[2]
            shutil.copytree(project / "_ask/scripts", root / "_ask/scripts")
            captured = capture(root, "product")
            from _ask.scripts.engineering_model.admission import load_published
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

    def test_missing_linked_and_ambiguous_changes_invalidate_snapshot(self):
        from _ask.scripts.engineering_model.admission import admit, load_published
        from _ask.scripts.engineering_model.observer import observe_once

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
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
