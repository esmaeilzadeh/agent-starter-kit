from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from workflow_refs.store import initialize_catalog, register_revision


class ReferenceCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="refs-cli-")
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.test"], cwd=self.root, check=True)
        self.source = self.root / "work/demo/source.json"
        self.source.parent.mkdir(parents=True)
        self.source.write_text(json.dumps({"items": [{"id": "task-two", "value": 7, "inputs": []}]}))
        subprocess.run(["git", "add", "work/demo/source.json"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture source"], cwd=self.root, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        catalog = self.root / "work/demo/references/integrity.json"
        catalog.parent.mkdir(parents=True)
        initialize_catalog(catalog, "demo")
        register_revision(catalog, "demo", "demo/spec/1/plan/1/task/2",
                          {"commit": self.commit, "path": "work/demo/source.json"},
                          "task-two", "structured-item/1", self.source.read_bytes())

    def tearDown(self):
        self.temp.cleanup()

    def test_public_numeric_show_and_scoped_errors(self):
        from workflow_refs.cli import main
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["show", "demo/spec/1/plan/1/task/2@1"], root=self.root)
        value = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(value["revision"], 1)
        self.assertEqual(value["parents"], {"spec": 1, "plan": 1})
        self.assertNotIn("integrity", value)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["show", "demo/spec/1/plan/1/task/2@1", "--integrity"], root=self.root)
        detailed = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertIn("digests", detailed["integrity"])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["show", "demo/spec/1/plan/1/task/2@2"], root=self.root)
        missing = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(missing["reason"], "missing")
