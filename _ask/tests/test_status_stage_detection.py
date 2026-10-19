"""End-to-end stage inference checks through the public ``./ask status`` CLI."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]


class StatusStageDetection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ask-status-stage-")
        self.root = Path(self.temp.name)
        shutil.copytree(REPO / "_ask", self.root / "_ask")
        shutil.copy2(REPO / "ask", self.root / "ask")
        self.git("init", "-q", "-b", "develop")
        self.git("config", "user.name", "Status fixture")
        self.git("config", "user.email", "status@example.test")
        self.git("commit", "--allow-empty", "-qm", "default branch")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout.strip()

    def status(self, edits=None):
        self.git("checkout", "-qb", "agent/demo")
        work = self.root / "work" / "demo"
        work.mkdir(parents=True)
        for name in ("intent.md", "plan.md", "review.md"):
            shutil.copy2(REPO / "_ask" / "templates" / name, work / name)
        for name, content in (edits or {}).items():
            (work / name).write_text(content)
        self.git("add", "work/demo")
        self.git("commit", "-qm", "seed workstream artifacts")
        result = subprocess.run(
            [str(self.root / "ask"), "status", "--json", "--work-id", "demo"],
            cwd=self.root, check=True, text=True, capture_output=True,
        )
        return json.loads(result.stdout)["workstreams"][0]["stage"]

    def test_blank_templates_report_seeded(self):
        self.assertEqual("seeded", self.status())

    def test_findings_without_verdict_do_not_report_reviewed(self):
        review = (REPO / "_ask/templates/review.md").read_text().replace(
            "## Findings\n", "## Findings\n- A concrete observation.\n"
        )
        self.assertEqual("seeded", self.status({"review.md": review}))

    def test_incomplete_task_row_does_not_report_planned(self):
        plan = (REPO / "_ask/templates/plan.md").read_text().replace(
            "|  |  |  |  |  |  |", "| task-1 |  |  |  |  |  |"
        )
        self.assertEqual("seeded", self.status({"plan.md": plan}))

    def test_meaningful_approach_reports_planned(self):
        plan = (REPO / "_ask/templates/plan.md").read_text().replace(
            "## Approach\n", "## Approach\nImplement the agreed behavior.\n"
        )
        self.assertEqual("planned", self.status({"plan.md": plan}))

    def test_populated_task_row_reports_planned(self):
        plan = (REPO / "_ask/templates/plan.md").read_text().replace(
            "|  |  |  |  |  |  |", "| task-1 | Deliver behavior |  |  |  |  |"
        )
        self.assertEqual("planned", self.status({"plan.md": plan}))

    def test_substantive_verdict_reports_reviewed(self):
        review = (REPO / "_ask/templates/review.md").read_text().replace(
            "## Review verdict\n", "## Review verdict\nApproved: checks pass.\n"
        )
        self.assertEqual("reviewed", self.status({"review.md": review}))


if __name__ == "__main__":
    unittest.main()
