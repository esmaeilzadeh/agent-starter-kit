"""Captured context selection and action-dependency behavior for the workbench."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from _ask.tests.revising_fixture import model, plan, reference_bytes
from _ask.scripts.engineering_model.snapshot import capture, is_current


def _put(root, relative, value):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True).encode()
    path.write_bytes(raw)
    return path


def _document(*, context=True, source_context=True):
    document = model()
    task = document["nodes"][3]
    if context:
        task["context"] = [
            {"role": "spec", "path": "specs/current/product.md", "revision": "spec-r1",
             "selector": {"kind": "heading", "path": ["Scope"]}},
            {"role": "plan", "path": "work/product/plan.md", "revision": "plan-r1",
             "selector": {"kind": "plan-task", "heading_path": ["Work breakdown"], "task_id": "WB-003"}},
        ]
    if source_context:
        document["nodes"][4]["source_context"] = [
            {"path": "tests/helpers.py", "revision": "helper-r1", "qualified_name": "tests.helpers.assert_publish",
             "role": "helper", "explanation": "Shared assertion helper"}
        ]
    return document


def _repo(root, *, context=True, source_context=True, spec_text="# Scope\nCurrent contract.\n",
          plan_text="# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n"):
    refs, canonical_plan = reference_bytes()
    for relative, raw in refs.items():
        _put(root, relative, raw)
    _put(root, "work/product/engineering-model.json", _document(context=context, source_context=source_context))
    if context and spec_text is not None:
        _put(root, "specs/current/product.md", spec_text.encode())
    if context and plan_text is not None:
        _put(root, "work/product/plan.md", plan_text.encode())
    if source_context:
        _put(root, "tests/helpers.py", b"def assert_publish():\n    assert True\n")
    return canonical_plan


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
        unique_heading = resolve("work/plan.md", markdown,
                                 {"kind": "heading", "path": ["Work breakdown"]})
        self.assertEqual(unique_heading["state"], "ambiguous", "different full ancestor chains must not collapse")
        unique_heading = resolve("work/plan.md", markdown,
                                 {"kind": "heading", "path": ["Work", "Work breakdown"]})
        self.assertEqual(unique_heading["state"], "available")
        self.assertEqual(unique_heading["text"], "## Work breakdown\nIntro.\n### Detail\nText.\n")
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
        self.assertIn("| WB-003 | Publish safely |", selected["text"])
        for path, selector in [
            ("../outside.md", {"kind": "heading", "path": ["Work"]}),
            ("C:\\outside.md", {"kind": "heading", "path": ["Work"]}),
            ("work/a.md", {"kind": "fuzzy", "query": "Work"}),
            ("work/a.md", {"kind": "heading", "path": []}),
            ("work/a.md", {"kind": "heading", "path": [""]}),
            ("work/a.md", {"kind": "heading", "path": ["Work"], "fallback": True}),
            ("work/a.md", {"kind": "plan-task", "heading_path": ["Work"], "task_id": []}),
        ]:
            with self.subTest(path=path, selector=selector):
                with self.assertRaises((ValueError, TypeError)):
                    resolve(path, markdown, selector)

class PassageAdmissionTests(unittest.TestCase):
    def test_required_passages_block_only_dependent_actions(self):
        from _ask.scripts.engineering_model.workflow import workflow_admission
        from _ask.scripts.engineering_model.actions import Refused

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _repo(root, spec_text=None, plan_text="# Work breakdown\n")
            captured = capture(root, "product")
            calls = []
            try:
                with self.assertRaises(Refused):
                    with workflow_admission(root, "product", task_node_id="task"):
                        calls.append("selected-task-action")
            except TypeError as exc:
                self.fail(f"selected Task contract admission must be supported, not rejected by the API: {exc}")
            self.assertEqual(calls, [], "required unresolved Task passages must block before action")
            # The same unavailable context remains an admitted limitation for an
            # unrelated action; generic workflow admission must not make it global.
            with workflow_admission(root, "product"):
                calls.append("unrelated-decision")
            self.assertEqual(calls, ["unrelated-decision"])

            _put(root, "specs/current/product.md", b"# Scope\nCurrent contract.\n")
            _put(root, "work/product/plan.md",
                 b"# Work breakdown\n\n| Task ID | Outcome |\n| --- | --- |\n| WB-003 | Publish safely |\n")
            try:
                with workflow_admission(root, "product", task_node_id="task"):
                    calls.append("selected-task-action")
            except TypeError as exc:
                self.fail(f"selected Task contract admission must be supported, not rejected by the API: {exc}")
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

            spec_path = root / "specs/current/product.md"
            old_stat = spec_path.stat()
            spec_path.write_text("# Scope\nA materially changed contract.\n", encoding="utf-8")
            os.utime(spec_path, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
            self.assertFalse(is_current(first, root), "same-mtime linked-only edits invalidate captured bytes")
            second = capture(root, "product")
            self.assertNotEqual(first_identity["digest"], second.identity["digest"])
            self.assertIn("A contract", historical_text["text"], "published passage remains historical")
            _snapshot, errors = admit(root, "product")
            self.assertEqual(errors, [])
            self.assertEqual(observe_once(root, "product")["snapshot"]["digest"], second.identity["digest"])

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
