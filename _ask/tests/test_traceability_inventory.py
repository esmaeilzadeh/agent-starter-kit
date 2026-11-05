import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from verification.traceability.evidence import inventory


class InventoryTests(unittest.TestCase):
    def test_new_regression_case_is_not_marked_as_changed_behavior(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.git(root, "init", "-q")
            self.git(root, "config", "user.email", "traceability@example.test")
            self.git(root, "config", "user.name", "Traceability Test")
            source = root / "cases.py"
            source.write_text(
                "class Cases:\n"
                "    def test_existing(self):\n"
                "        self.assertEqual(1, 1)\n"
            )
            self.git(root, "add", "cases.py")
            self.git(root, "commit", "-qm", "baseline")
            base = self.git(root, "rev-parse", "HEAD")

            source.write_text(
                "class Cases:\n"
                "    def test_existing(self):\n"
                "        self.assertEqual(1, 2)\n"
                "\n"
                "    def test_new_regression(self):\n"
                "        self.assertTrue(True)\n"
            )
            self.git(root, "add", "cases.py")
            self.git(root, "commit", "-qm", "candidate")
            head = self.git(root, "rev-parse", "HEAD")
            plan = {
                "tests": [
                    {
                        "id": "EXISTING",
                        "source_paths": ["cases.py"],
                        "case_id": "suite.Cases.test_existing",
                    },
                    {
                        "id": "PREP-03",
                        "source_paths": ["cases.py"],
                        "case_id": "suite.Cases.test_new_regression",
                    },
                ]
            }

            result = inventory(root, base, head, plan)

            self.assertEqual(result["changed_cases"], ["EXISTING", "PREP-03"])
            self.assertEqual(result["behavior_changes"], ["EXISTING"])

    def git(self, root, *args):
        return subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()


if __name__ == "__main__":
    unittest.main()
