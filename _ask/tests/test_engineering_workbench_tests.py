"""Selected test/result and debug detail journeys."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "_ask/ui"
sys.path[:0] = [str(UI)]
from workbench_tests import render_test


PROJECTION = {"work_id": "pilot", "snapshot": {"digest": "snapshot-123"},
              "workbench": {"tests": [{"id": "CASE-1", "title": "Shared test",
                                          "case_id": "fixture.Case.test_shared",
                                          "runner_id": "fixture", "scenario_ids": ["scenario"],
                                          "source_paths": ["test_fixture.py"],
                                          "expected_assertions": [{"criterion_id": "P-001", "checks": ["Accept input"]}],
                                          "evidence": {"outcome": "failed", "failure": "expected output", "timestamp": "unavailable", "duration": "unavailable"}}]}}


class WorkbenchTests(unittest.TestCase):
    def test_selected_test_shows_source_results_and_related_work(self):
        script = """
import sys
sys.path.insert(0, %r)
from workbench_tests import render_test
render_test(%r, 'CASE-1')
""" % (str(UI), PROJECTION)
        app = AppTest.from_string(script).run(timeout=30)
        self.assertFalse(app.exception, app.exception)
        text = "\n".join(str(item.value) for group in (app.subheader, app.markdown, app.caption, app.info, app.error, app.text)
                           for item in group)
        for phrase in ("Shared test", "Test source", "test_fixture.py", "Recorded execution", "failed", "unavailable"):
            self.assertIn(phrase, text)

    def test_identifiers_have_explanations_and_copy_actions(self):
        script = """
import sys
sys.path.insert(0, %r)
from workbench_tests import render_test
render_test(%r, 'CASE-1')
""" % (str(UI), PROJECTION)
        app = AppTest.from_string(script).run(timeout=30)
        self.assertFalse(app.exception, app.exception)
        self.assertTrue(any(item.label == "Technical details and identifiers" for item in app.expander))
        self.assertNotIn("snapshot-123", "\n".join(str(item.value) for item in app.code))


if __name__ == "__main__":
    unittest.main()
