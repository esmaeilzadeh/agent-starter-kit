"""Overview and scenario journeys through the actual workbench entry point."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "_ask/ui"
TESTS = ROOT / "_ask/tests"
sys.path[:0] = [str(UI), str(TESTS)]
from engineering_fixture import workbench_model


def _text(app) -> str:
    collections = (app.title, app.header, app.subheader, app.markdown, app.caption,
                   app.info, app.warning, app.error, app.success, app.text)
    return "\n".join(str(item.value) for group in collections for item in group) + "\n" + \
        "\n".join(str(item.label) for item in app.button)


def _app(root: Path):
    return AppTest.from_file(str(UI / "streamlit_app.py")).run(timeout=30)


def _fixture(root: Path) -> None:
    model, _ = workbench_model(root)
    purpose = next(node for node in model["nodes"] if node["id"] == "purpose")
    purpose["description"] = "Make delivery decisions and proof easy to inspect."
    # The accepted pilot has a scenario but no story node, and one task has no
    # explicit task-to-scenario implementation edge. Preserve those absences.
    (root / "work/pilot/engineering-model.json").write_text(
        __import__("json").dumps(model), encoding="utf-8")


class WorkbenchTests(unittest.TestCase):
    def test_overview_is_comprehensive_and_lazy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _fixture(root)
            source_reads = []
            original_read_text = Path.read_text

            def count_source_reads(path, *args, **kwargs):
                if path.resolve() == (root / "test_fixture.py").resolve():
                    source_reads.append(path)
                return original_read_text(path, *args, **kwargs)

            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}), \
                    patch("engineering_model.projection.inspect_evidence",
                          side_effect=AssertionError("overview must not inspect evidence")), \
                    patch.object(Path, "read_text", count_source_reads):
                app = _app(root)
                self.assertFalse(app.exception, app.exception)
                rendered = _text(app)
                for phrase in ("Make delivery decisions and proof easy to inspect.",
                               "No story records are present", "Scenarios without a recorded story",
                               "Canonical behavior", "Blocked tasks", "Open decisions",
                               "Not loaded", "Choose"):
                    self.assertIn(phrase, rendered)
                self.assertNotIn("Exact accepted behavior", rendered)
                self.assertEqual(source_reads, [], "opening the epic must not read test source")
                self.assertFalse(app.tabs)

                # Navigate the actual hierarchy and inspect canonical details.
                app.button(key="route:scenario").click().run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                scenario_text = _text(app)
                for phrase in ("Valid input", "Validate", "Accept", "Behavior assertion", "Build"):
                    self.assertIn(phrase, scenario_text)
                self.assertEqual(source_reads, [], "scenario details must not eagerly read test source")

    def test_summary_counts_open_exact_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _fixture(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = _app(root)
                self.assertFalse(app.exception, app.exception)
                controls = {item.key: item for item in app.button}
                self.assertIn("overview:summary:blocked", controls,
                              "blocked-task summary must open its stable-ID filtered records")
                controls["overview:summary:blocked"].click().run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(app.session_state["_engineering_overview_filter"],
                                 {"kind": "blocked", "ids": ["build"]})
                self.assertIn("Build", _text(app))
                self.assertIn("Blocked", _text(app))

                controls = {item.key: item for item in app.button}
                self.assertIn("overview:filter:clear", controls)
                controls["overview:filter:clear"].click().run(timeout=30)
                controls = {item.key: item for item in app.button}
                self.assertIn("overview:summary:decisions", controls)
                controls["overview:summary:decisions"].click().run(timeout=30)
                self.assertEqual(app.session_state["_engineering_overview_filter"],
                                 {"kind": "decisions", "ids": ["choice"]})
                self.assertIn("Choose", _text(app))
                self.assertIn("Not loaded", _text(app))
                self.assertNotIn("0 failed", _text(app).lower())


if __name__ == "__main__":
    unittest.main()
