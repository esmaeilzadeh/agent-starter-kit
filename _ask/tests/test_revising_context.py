"""Captured context selection and action-dependency behavior for the workbench."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

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
    task["execution"] = {"work_id": "delivery", "task_id": "task"}
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
            path = root / "docs/context.md"
            path.unlink()
            path.symlink_to(root / "work/product/plan.md")
            linked = capture(root, "product")
            self.assertNotEqual(linked.statuses["docs/context.md"], "present",
                                "symlink components cannot be treated as safe passage sources")
            from _ask.scripts.engineering_model.admission import admit
            _published, diagnostics = admit(root, "product")
            self.assertTrue(any(item["code"] == "EM001_CONTEXT_REFERENCE" for item in diagnostics),
                            "terminal symlink must refuse captured admission")
            path.unlink()
            (root / "docs").rename(root / "docs-real")
            (root / "docs").symlink_to(root / "docs-real", target_is_directory=True)
            ancestor = capture(root, "product")
            self.assertNotEqual(ancestor.statuses["docs/context.md"], "present",
                                "an in-repository ancestor symlink is also unsafe")

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

class PassageAdmissionTests(unittest.TestCase):
    def test_required_passages_block_only_dependent_actions(self):
        from _ask.scripts.engineering_model.workflow import workflow_admission
        from _ask.scripts.engineering_model.actions import edit

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root, spec_text=None, plan_text="# Work breakdown\n")
            captured = capture(root, "product")
            calls = []
            try:
                receipt = edit(root, "product", captured.identity["digest"],
                               lambda: calls.append("selected-task-action") or {"commands": [
                                   {"op": "revise_node", "id": "story", "changes": {"title": "Changed"}}]},
                               task_node_id="task")
            except TypeError as exc:
                self.fail(f"the semantic edit entry must enforce selected Task context: {exc}")
            self.assertFalse(receipt["valid"], "required unresolved Task passages block the real edit entry")
            self.assertEqual(calls, [], "required unresolved Task passages must block before action")
            # The same unavailable context remains an admitted limitation for an
            # unrelated action; generic workflow admission must not make it global.
            with workflow_admission(root, "product"):
                calls.append("unrelated-decision")
            self.assertEqual(calls, ["unrelated-decision"])

            _put(root, "docs/context.md", b"# Scope\nCurrent contract.\n")
            _put(root, "work/product/plan.md",
                 b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n")
            try:
                with workflow_admission(root, "product", task_node_id="task"):
                    calls.append("selected-task-action")
            except TypeError as exc:
                self.fail(f"selected Task contract admission must be supported: {exc}")
            self.assertEqual(calls[-1], "selected-task-action")
            self.assertFalse(is_current(captured, root), "newly available passages invalidate old admission")

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
            _snapshot, errors = admit(root, "product")
            self.assertEqual(errors, [])
            self.assertEqual(observe_once(root, "product")["snapshot"]["digest"], after_helper.identity["digest"])

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
