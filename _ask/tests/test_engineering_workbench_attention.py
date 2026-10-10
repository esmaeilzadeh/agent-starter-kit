"""Attention and guarded decision journeys for the workbench."""
from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "_ask/ui"
sys.path[:0] = [str(UI), str(ROOT / "_ask/scripts")]
from workbench_attention import attention_rows


class WorkbenchTests(unittest.TestCase):
    def test_attention_links_blockers_decisions_and_evidence(self):
        projection = {"model": {"nodes": [{"id": "choice", "type": "decision",
                                               "title": "Choose", "options": [{"id": "fast", "label": "Fast"}]}]},
                      "attention": [{"id": "choice", "type": "decision",
                                      "reason": "A choice is open", "dependents": ["task-b"]},
                                     {"id": "task-b", "type": "task",
                                      "title": "Blocked task", "reason": "choice is open"}]}
        rows = attention_rows(projection)
        self.assertEqual({row["id"] for row in rows}, {"choice", "task-b"})
        self.assertEqual(rows[0]["options"][0]["id"], "fast")
        self.assertIn("choice is open", rows[1]["reason"])
        self.assertIn("Missing attention record", rows[0]["title"])

    def test_reasoned_choice_persists_and_read_only_rejects(self):
        script = """
import sys
sys.path.insert(0, %r)
from workbench_attention import render_attention
import streamlit as st
projection = {"model": {"nodes": [{"id": "choice", "type": "decision", "title": "Choose", "options": [{"id": "fast", "label": "Fast"}]}]}, "attention": [{"id": "choice", "type": "decision", "reason": "A choice is open", "dependents": ["task-b"]}]}
render_attention(projection)
st.info("Incomplete input preserves the captured snapshot; guarded mutation belongs to the existing decision form.")
""" % str(UI)
        app = AppTest.from_string(script).run(timeout=30)
        self.assertFalse(app.exception, app.exception)
        text = "\n".join(str(item.value) for group in (app.subheader, app.markdown, app.caption, app.info, app.text)
                           for item in group)
        for phrase in ("Needs attention", "A choice is open", "Declared options", "Dependents",
                       "Incomplete input preserves"):
            self.assertIn(phrase, text)
        self.assertTrue(app.dataframe)


if __name__ == "__main__":
    unittest.main()
