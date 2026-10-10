"""Task list/detail journeys through the connected workbench."""
from __future__ import annotations

import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "_ask/ui"
TESTS = ROOT / "_ask/tests"
sys.path[:0] = [str(UI), str(TESTS), str(ROOT / "_ask/scripts")]
from engineering_fixture import workbench_model
from workbench_tasks import task_rows


def _fixture(root: Path) -> None:
    model, _ = workbench_model(root)
    (root / "work/pilot/engineering-model.json").write_text(
        __import__("json").dumps(model), encoding="utf-8")


def _text(app) -> str:
    collections = (app.title, app.header, app.subheader, app.markdown, app.caption,
                   app.info, app.warning, app.error, app.success, app.text)
    return "\n".join(str(item.value) for group in collections for item in group)


class WorkbenchTests(unittest.TestCase):
    def test_task_detail_explains_work_dependencies_and_tests(self):
        projection = {"model": {"nodes": [{"id": "planned", "type": "task",
                                               "title": "Planned task", "lifecycle": "active"}]},
                      "workbench": {"tasks": [{"id": "planned", "title": "Planned task",
                                                  "status": "planned", "owned_test_ids": [],
                                                  "owned_paths": []}]},
                      "tasks": [{"id": "planned", "status": "planned", "blockers": []}]}
        row = task_rows(projection)[0]
        self.assertEqual(row["lifecycle"], "active")
        self.assertEqual(row["status"], "planned")
        self.assertFalse(row["verified"])

    def test_completed_tasks_retain_tests_results_and_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _fixture(root)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(UI / "streamlit_app.py")).run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                app.button(key="route:build").click().run(timeout=30)
                self.assertFalse(app.exception, app.exception)
                text = _text(app)
                for phrase in ("Tasks", "Related scenarios", "Related tests",
                               "Implementation evidence", "Lifecycle status is separate"):
                    self.assertIn(phrase, text)
                self.assertTrue(app.dataframe)
                self.assertIn("Status filter", {item.label for item in app.selectbox})
                self.assertIn("Search tasks", {item.label for item in app.text_input})
                self.assertIn("Unrecorded implementation gap", text)
                self.assertTrue(any(item.key.startswith("tasks:selected:") for item in app.selectbox))


if __name__ == "__main__":
    unittest.main()
