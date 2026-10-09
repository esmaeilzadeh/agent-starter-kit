"""Behavior checks for the connected workbench projection."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from engineering_model.projection import project
from engineering_model.snapshot import capture


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        model = {
            "schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
            "nodes": [
                {"id": "epic", "type": "feature", "title": "Workbench", "lifecycle": "active"},
                {"id": "story", "type": "story", "title": "Delivery story", "lifecycle": "active"},
                {"id": "s1", "type": "scenario", "title": "First", "lifecycle": "active",
                 "reference": {"path": "specs/current/pilot.json", "id": "C1"}},
                {"id": "s2", "type": "scenario", "title": "Second", "lifecycle": "active",
                 "reference": {"path": "specs/current/pilot.json", "id": "C2"}},
                {"id": "legacy-task", "type": "task", "title": "Pilot-only task", "lifecycle": "planned"},
                {"id": "case-shared", "type": "test", "title": "Shared scenario case", "lifecycle": "active",
                 "reference": {"path": "work/pilot/test-plan.json", "id": "CASE-1"}},
                {"id": "case-second", "type": "test", "title": "Second scenario case", "lifecycle": "active",
                 "reference": {"path": "work/pilot/test-plan.json", "id": "CASE-2"}},
            ],
            "edges": [
                {"type": "contains", "source": "epic", "target": "story"},
                {"type": "contains", "source": "story", "target": "s1"},
                {"type": "contains", "source": "story", "target": "s2"},
                {"type": "contains", "source": "epic", "target": "legacy-task"},
                {"type": "covers", "source": "case-shared", "target": "s1"},
                {"type": "covers", "source": "case-shared", "target": "s2"},
                {"type": "covers", "source": "case-second", "target": "s2"},
            ],
        }
        self.write("work/pilot/engineering-model.json", model)
        self.write("specs/current/pilot.json", {
            "schema": "ask-spec/v1", "work_id": "pilot", "revision": 1,
            "criteria": [
                {"id": "C1", "given": "A", "when": "B", "then": ["C"], "verification_mode": "tests"},
                {"id": "C2", "given": "D", "when": "E", "then": ["F"], "verification_mode": "tests"},
            ],
        })
        self.write("work/pilot/test-plan.json", {
            "schema": "ask-test-plan/v1", "work_id": "pilot",
            "task_scopes": [
                {"task_id": "task-a", "test_ids": ["CASE-1"]},
                {"task_id": "task-b", "test_ids": ["CASE-2"]},
            ],
            "tests": [
                {"id": "CASE-1", "criterion_ids": ["C1", "C2"], "type": "unit",
                 "scenario": {"given": "A", "when": "B", "then": ["C"]}},
                {"id": "CASE-2", "criterion_ids": ["C2"], "type": "unit",
                 "scenario": {"given": "D", "when": "E", "then": ["F"]}},
            ],
        })
        self.write("work/pilot/inner-loop/tasks.yaml", """schema: ask-inner-loop-tasks/v1
work_id: pilot
tasks:
  - id: task-a
    title: First task
    outcome: Preserve shared ownership
    depends_on: []
    owned_paths: [src/a.py]
  - id: task-b
    title: Second task
    outcome: Deliver second scenario
    depends_on: [task-a]
    owned_paths: [src/b.py]
""")

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")

    def projection(self):
        return project(capture(self.root, "pilot"), self.root, include_evidence=False)

    def workbench(self):
        projection = self.projection()
        self.assertIn("workbench", projection, "projection joins the task graph and story relationships")
        return projection["workbench"]

    def test_many_to_many_relations_and_deduplication(self):
        workbench = self.workbench()
        tasks = {task["id"]: task for task in workbench["tasks"]}
        tests = {test["id"]: test for test in workbench["tests"]}

        self.assertEqual(tasks["task-a"]["owned_test_ids"], ["CASE-1"])
        self.assertEqual(tasks["task-b"]["owned_test_ids"], ["CASE-2"])
        self.assertEqual(tests["CASE-1"]["scenario_ids"], ["s1", "s2"])
        self.assertEqual(tests["CASE-1"]["owner_task_id"], "task-a")
        self.assertIn({"task_id": "task-b", "via": "scenario-coverage"},
                      tests["CASE-1"]["related_tasks"])
        self.assertEqual(len(tests), 2)

    def test_task_scopes_runtime_and_missing_history(self):
        workbench = self.workbench()
        tasks = {task["id"]: task for task in workbench["tasks"]}

        self.assertEqual(tasks["task-a"]["title"], "First task")
        self.assertEqual(tasks["task-a"]["outcome"], "Preserve shared ownership")
        self.assertEqual(tasks["task-a"]["owned_paths"], ["src/a.py"])
        self.assertEqual(tasks["task-a"]["dependencies"], [])
        self.assertEqual(tasks["task-a"]["status"], "planned")
        self.assertEqual(tasks["task-a"]["status_source"], "no-runtime-record")
        self.assertEqual(tasks["legacy-task"]["record_source"], "engineering-model")
        self.assertEqual(tasks["legacy-task"]["status"], "not-recorded")

    def test_story_scope_and_missing_story_are_honest(self):
        workbench = self.workbench()
        stories = {story["id"]: story for story in workbench["stories"]}

        self.assertEqual(stories["story"]["scenario_ids"], ["s1", "s2"])
        self.assertEqual(workbench["unassigned_scenario_ids"], [])
        self.assertNotIn("task-a", stories)
