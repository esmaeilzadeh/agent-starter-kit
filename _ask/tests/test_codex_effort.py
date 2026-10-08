"""Public generator journeys in isolated consumers; never mutate this checkout."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "_ask/scripts/sync-runtime-agents.py"


class CodexEffortTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ask-codex-effort-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / ".agents/ask/bindings", self.root / ".agents/ask/bindings")
        (self.root / ".agents/ask/stages").mkdir()
        (self.root / "_ask/bindings").mkdir(parents=True)
        (self.root / "work/example").mkdir(parents=True)

    def generate(self, **extra):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("ASK_",))}
        env.update(ASK_ROOT=str(self.root), **extra)
        return subprocess.run(["python3", str(SCRIPT)], env=env, text=True,
                              capture_output=True, check=False)

    def agent(self, stage):
        return (self.root / f".codex/agents/kit-{stage}.toml").read_text()

    def test_default_journey(self):
        result = self.generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        agents = list((self.root / ".codex/agents").glob("*.toml"))
        self.assertEqual(len(agents), 11)
        self.assertIn('model = "gpt-6-luna"', self.agent("06-implement"))
        self.assertIn('model_reasoning_effort = "medium"', self.agent("06-implement"))
        self.assertIn('model_reasoning_effort = "medium"', self.agent("02-spec"))
        self.assertIn('model_reasoning_effort = "high"', self.agent("03-spec-challenge"))
        self.assertIn('model_reasoning_effort = "low"', self.agent("09-verify"))
        for runtime in (".cursor", ".claude", ".opencode"):
            outputs = list((self.root / runtime / "agents").glob("*.md"))
            self.assertEqual(len(outputs), 11)
            self.assertTrue(all("reasoning_effort" not in path.read_text() for path in outputs))

    def test_high_risk_review(self):
        (self.root / "work/example/models.yaml").write_text("risk: HIGH\n")
        result = self.generate(ASK_WORK_ID="example")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('model = "gpt-6-astra"', self.agent("07-review"))
        self.assertIn('model_reasoning_effort = "high"', self.agent("07-review"))
        self.assertIn('model_reasoning_effort = "medium"', self.agent("06-implement"))

    def test_effort_precedence(self):
        (self.root / "_ask/bindings/models.yaml").write_text(
            "reasoning_effort:\n  codex:\n    06-implement: low\n")
        work = self.root / "work/example/models.yaml"
        work.write_text("codex:\n  06-implement: gpt-6.1-sol\n"
                        "reasoning_effort:\n  codex:\n    06-implement: high\n")
        result = self.generate(ASK_WORK_ID="example", ASK_EFFORT_06_IMPLEMENT="medium",
                               ASK_EFFORT_06_IMPLEMENT_CODEX="low")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('model_reasoning_effort = "low"', self.agent("06-implement"))
        result = self.generate(ASK_WORK_ID="example", ASK_EFFORT_06_IMPLEMENT="medium")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('model_reasoning_effort = "medium"', self.agent("06-implement"))
        result = self.generate(ASK_WORK_ID="example")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('model_reasoning_effort = "high"', self.agent("06-implement"))
        self.assertIn('model = "gpt-6.1-sol"', self.agent("06-implement"))
        result = self.generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('model_reasoning_effort = "low"', self.agent("06-implement"))

    def test_inherit_and_unknown_model(self):
        result = self.generate(ASK_EFFORT_06_IMPLEMENT="inherit",
                               ASK_MODEL_09_VERIFY_CODEX="future-model")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("model_reasoning_effort", self.agent("06-implement"))
        self.assertIn('model = "future-model"', self.agent("09-verify"))
        self.assertNotIn("model_reasoning_effort", self.agent("09-verify"))

    def test_invalid_effort_preserves_outputs(self):
        result = self.generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        outputs = {path: path.read_bytes() for runtime in (".cursor", ".claude", ".codex", ".opencode")
                   for path in (self.root / runtime / "agents").iterdir()}
        result = self.generate(ASK_EFFORT_09_VERIFY_CODEX="unlimited",
                               ASK_MODEL_06_IMPLEMENT_CODEX="different-model")
        self.assertNotEqual(result.returncode, 0, "Invalid effort must reject generation")
        self.assertIn("invalid reasoning effort", result.stderr)
        self.assertEqual(outputs, {path: path.read_bytes() for path in outputs})


if __name__ == "__main__":
    unittest.main()
