"""Readable selected-test source and authority-bound observations."""
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class ReadableTestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Readable test")
        self.write("test_sample.py", """import unittest
FIXTURE = {"input": "old input"}

def make_input():
    return FIXTURE["input"]

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.expected = "old expected"

    def _assert_projection(self, actual):
        self.assertEqual(actual, self.expected)

    def test_projection(self):
        actual = make_input()
        self._assert_projection(actual)
""")
        self.old_sha = self.commit("initial selected test source")
        self.write("test_sample.py", """import unittest
FIXTURE = {"input": "new input"}

def make_input():
    return FIXTURE["input"]

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.expected = "new expected"

    def _assert_projection(self, actual):
        self.assertEqual(actual, self.expected)

    def test_projection(self):
        actual = make_input()
        self._assert_projection(actual)
""")
        self.current_sha = self.commit("change current fixture and helper")
        self.test = {
            "id": "T",
            "case_id": "test_sample.ProjectionTests.test_projection",
            "runner_id": "unittest",
            "source_paths": ["test_sample.py"],
            "scenario": {"given": "fixture input", "when": "project", "then": ["old expected"]},
        }

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def test_same_revision_setup_helper_globals_and_assertion_context(self):
        from engineering_model.readable_tests import read_test

        readable = read_test(self.root, self.test, self.old_sha,
                             current_sha=self.current_sha)
        self.assertEqual(readable["status"], "historical", readable)
        self.assertEqual(readable["source_sha"], self.old_sha)
        self.assertEqual(readable["current_sha"], self.current_sha)
        self.assertEqual(readable["flow"], self.test["scenario"])
        self.assertIn("self._assert_projection(actual)", readable["test_source"])
        context = {item["selector"]: item for item in readable["context"]}
        self.assertIn("import unittest", context["<imports>"]["source"])
        self.assertIn('FIXTURE = {"input": "old input"}', context["FIXTURE"]["source"])
        self.assertIn("return FIXTURE[\"input\"]", context["test_sample.make_input"]["source"])
        self.assertIn('self.expected = "old expected"',
                      context["ProjectionTests.setUp"]["source"])
        self.assertIn("self.assertEqual(actual, self.expected)",
                      context["ProjectionTests._assert_projection"]["source"])
        self.assertNotIn("new input", json_context(readable))

        self.write("test_sample.py", """import unittest
FIXTURE = {"input": "old input"}

def make_input():
    return FIXTURE["input"]

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.expected = "old expected"

    def test_projection(self):
        actual = make_input()
        self._missing_helper(actual)
""")
        missing_sha = self.commit("remove selected helper")
        incomplete = read_test(self.root, self.test, missing_sha,
                               current_sha=missing_sha)
        self.assertEqual(incomplete["status"], "current", incomplete)
        self.assertEqual(incomplete["context_status"], "incomplete")
        missing = [item for item in incomplete["context"]
                   if item.get("status") == "missing"]
        self.assertEqual([item["selector"] for item in missing],
                         ["ProjectionTests._missing_helper"])


def json_context(readable):
    import json
    return json.dumps(readable, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
