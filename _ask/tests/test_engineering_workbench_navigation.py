"""App-level journeys through the one connected work hierarchy."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/tests"))
from engineering_fixture import workbench_model, write_json


def _init_repo(root: Path, branch: str = "agent/pilot") -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", branch], check=True)


def _add_story(model):
    model["nodes"].append({"id": "story", "type": "story", "title": "Pilot story",
                           "lifecycle": "active"})
    model["edges"].append({"type": "contains", "source": "purpose", "target": "story"})
    return model


def _run(root: Path):
    return AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=20)


def _text(app) -> str:
    return "\n".join(str(item.value) for collection in (
        app.title, app.header, app.subheader, app.markdown, app.caption,
        app.info, app.warning, app.error, app.success, app.button,
    ) for item in collection)


class WorkbenchNavigationTests(unittest.TestCase):
    def test_work_default_routes_and_context_reset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _init_repo(root, "agent/pilot")
            model, _ = workbench_model(root)
            _add_story(model)
            write_json(root, "work/pilot/engineering-model.json", model)
            # The selector lists both local models, but the branch-matched work opens first.
            other_model, _ = workbench_model(root)
            other_model["work_id"] = "archive"
            write_json(root, "work/archive/engineering-model.json", other_model)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = _run(root)
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(app.selectbox(key="work_id").value, "pilot")
                self.assertIn("Epic", _text(app))
                self.assertIn("Pilot story", _text(app))
                self.assertNotIn("Workbench section", _text(app))
                self.assertFalse(app.tabs)

                # Selecting a canonical descendant updates one breadcrumbed route.
                app.button(key="route:scenario").click().run(timeout=20)
                self.assertFalse(app.exception, app.exception)
                rendered = _text(app)
                for crumb in ("Purpose", "Pilot story", "Canonical behavior"):
                    self.assertIn(crumb, rendered)
                self.assertTrue(app.button(key="route:back"))

                app.selectbox(key="work_id").select("archive").run(timeout=20)
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(app.selectbox(key="work_id").value, "archive")
                self.assertNotIn("Canonical behavior", _text(app))
                self.assertEqual(app.session_state["_engineering_route"], "purpose")
                self.assertEqual(subprocess.check_output(
                    ["git", "-C", str(root), "branch", "--show-current"], text=True).strip(),
                    "agent/pilot")

    def test_navigation_does_not_refresh_stale_form_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _init_repo(root)
            model, _ = workbench_model(root)
            _add_story(model)
            write_json(root, "work/pilot/engineering-model.json", model)
            with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
                app = _run(root)
                self.assertFalse(app.exception, app.exception)
                captured = app.session_state["_engineering_form_identity"]
                digest = captured["digest"]
                app.button(key="route:scenario").click().run(timeout=20)
                self.assertEqual(app.session_state["_engineering_form_identity"]["digest"], digest)

                # A linked spec change makes the captured edit stale. Navigation cannot
                # replace its identity or write the form; Refresh is the explicit recapture.
                spec_path = root / "specs/current/pilot.json"
                spec = __import__("json").loads(spec_path.read_text(encoding="utf-8"))
                spec["revision"] += 1
                write_json(root, "specs/current/pilot.json", spec)
                app.button(key="route:decision").click().run(timeout=20)
                self.assertEqual(app.session_state["_engineering_form_identity"]["digest"], digest)
                self.assertIn("stale", _text(app).lower())
                self.assertFalse(app.button(key="decision:submit").disabled)
                self.assertTrue(app.button(key="refresh"))
                self.assertEqual(app.session_state["_engineering_candidate_projection"], None)


if __name__ == "__main__":
    unittest.main()
