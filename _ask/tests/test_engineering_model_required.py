"""Workflows cannot reach implementation without their required model."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '_ask/scripts'))
from engineering_model.actions import Refused
from engineering_model.admission import validate_current
from engineering_model.projection import project
from engineering_model.snapshot import capture, is_current
from engineering_model.workflow import require_plan_links, workflow_admission
from engineering_fixture import workbench_model
from inner_loop.driver import run_until


class RequiredModelTests(unittest.TestCase):
    def test_missing_model_refuses_before_named_action_or_inner_loop_state_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for operation in (lambda: workflow_admission(root, 'pilot'),):
                with self.assertRaises(Refused) as refused:
                    with operation():
                        self.fail('missing model admitted an action')
                self.assertEqual(refused.exception.diagnostic['code'], 'EM007_MODEL_REQUIRED')
            with self.assertRaises(Refused):
                run_until(root, 'pilot')
            self.assertEqual(list(root.iterdir()), [])
            pointer = root / 'work/pilot/traceability/model-state/current.json'
            pointer.parent.mkdir(parents=True)
            pointer.write_text('{}')
            with self.assertRaises(Refused) as refused:
                with workflow_admission(root, 'pilot'):
                    self.fail('a publication pointer replaced the required model')
            self.assertEqual(refused.exception.diagnostic['code'], 'EM007_MODEL_REQUIRED')

    def test_template_is_valid_and_captures_graph_and_plan_without_incidental_node_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            work = root / 'work/pilot'
            model = json.loads((ROOT / '_ask/templates/engineering-model.json').read_text())
            model['work_id'] = 'pilot'
            (work / 'engineering-model.json').write_text(json.dumps(model))
            graph = work / 'inner-loop/tasks.yaml'
            snapshot, errors = validate_current(root, 'pilot')
            self.assertEqual(errors, [])
            self.assertIn('work/pilot/inner-loop/tasks.yaml', snapshot.files)
            view = project(snapshot, root, include_evidence=False)
            self.assertEqual(view['workbench']['tasks'][0]['id'], 'build')
            graph.write_text(graph.read_text() + '# changed task graph\n')
            self.assertFalse(is_current(snapshot, root))

    def test_implementation_preflight_rejects_unmodeled_planned_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbench_model(root)
            complete = capture(root, 'pilot')
            require_plan_links(complete)
            complete.document['nodes'] = [node for node in complete.document['nodes'] if node['type'] != 'test']
            with self.assertRaises(Refused) as refused:
                require_plan_links(complete)
            self.assertEqual(refused.exception.diagnostic['code'], 'EM016_PLAN_MODEL')
            self.assertIn('CASE-1', str(refused.exception))

    def test_missing_model_ui_explains_recovery_without_creating_project_files(self):
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / 'work/pilot'
            work.mkdir(parents=True)
            (work / 'plan.md').write_text('# Plan\nExisting implementation work.')
            before = {path.relative_to(root): path.read_bytes() for path in root.rglob('*') if path.is_file()}
            with patch.dict(os.environ, {'ASK_MODEL_ROOT': str(root)}):
                app = AppTest.from_file(str(ROOT / '_ask/ui/streamlit_app.py')).run(timeout=15)
            self.assertFalse(app.exception, app.exception)
            self.assertTrue(any('Required Engineering Model is missing' in item.value for item in app.error))
            self.assertTrue(any('./ask model validate --work-id pilot' in item.value for item in app.code))
            self.assertEqual(before, {path.relative_to(root): path.read_bytes()
                                      for path in root.rglob('*') if path.is_file()})


if __name__ == '__main__':
    unittest.main()
