"""Native workbench journeys through Streamlit's public AppTest interface."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from engineering_fixture import workbench_model

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
from engineering_model.admission import validate_current


def text(app):
    return "\n".join(str(element.value) for kind in ("markdown", "caption", "info", "warning", "error", "success")
                     for element in getattr(app, kind))


class UiIntegrationTests(unittest.TestCase):
    def test_resolution_survives_new_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            _snapshot, diagnostics = validate_current(root, "pilot")
            self.assertEqual(diagnostics, [], diagnostics)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build: blocked", text(app))
                app.selectbox(key="object_id").select("choice").run()
                app.selectbox(key="option_id").select("one")
                app.text_input(key="actor").input("Developer")
                app.text_area(key="rationale").input("Measured fit for the pilot")
                app.button(key="resolve").click().run(timeout=15)
                self.assertFalse(app.exception, app.exception)
                self.assertIn("build: ready", text(app))
                self.assertIn("Developer", text(app))
                self.assertIn("Measured fit for the pilot", text(app))
                reloaded = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=15)
                self.assertFalse(reloaded.exception, reloaded.exception)
                self.assertIn("build: ready", text(reloaded))
                reloaded.selectbox(key="object_id").select("choice").run()
                self.assertIn("Measured fit for the pilot", text(reloaded))
                self.assertIn("resolved", text(reloaded))
