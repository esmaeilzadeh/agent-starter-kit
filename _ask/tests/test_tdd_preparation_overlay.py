from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "_ask/skills").mkdir(parents=True)
        (self.root / "bin").mkdir()
        shutil.copy2(ROOT / "ask", self.root / "ask")
        shutil.copy2(ROOT / "_ask/skills/prepare-skills.sh",
                     self.root / "_ask/skills/prepare-skills.sh")
        (self.root / "_ask/skills/manifest.yaml").write_text(textwrap.dedent("""\
            skills:
              tdd:
                source: mattpocock/skills
                revision: "v1.2.3"
                skill: tdd
                role: inner-loop-red-green
                required: true
            """), encoding="utf-8")
        self.installed_views = (
            Path(".agents/skills/tdd/SKILL.md"),
            Path(".cursor/skills/tdd/SKILL.md"),
        )
        npx = self.root / "bin/npx"
        npx.write_text(textwrap.dedent("""\
            #!/usr/bin/env bash
            set -euo pipefail
            content='# TDD upstream\n\nUPSTREAM-CANARY-START\nKeep this content.\nUPSTREAM-CANARY-END\n\n## Refactoring\nRefactoring is not part of the loop.\n'
            for view in .agents/skills/tdd/SKILL.md .cursor/skills/tdd/SKILL.md; do
              mkdir -p "$(dirname "$view")"
              printf '%b' "$content" > "$view"
            done
            """), encoding="utf-8")
        npx.chmod(0o755)

    def prepare(self):
        env = dict(os.environ)
        env["PATH"] = str(self.root / "bin") + os.pathsep + env.get("PATH", "")
        return subprocess.run(["./ask", "prepare"], cwd=self.root, env=env,
                              text=True, capture_output=True)

    def test_both_views_use_canonical_tdd_override(self):
        manifest_before = (self.root / "_ask/skills/manifest.yaml").read_bytes()
        result = self.prepare()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for relative in self.installed_views:
            content = (self.root / relative).read_text(encoding="utf-8")
            self.assertIn("UPSTREAM-CANARY-START\nKeep this content.\nUPSTREAM-CANARY-END", content)
            self.assertIn("Red -> Green -> Refactor", content)
            self.assertIn(".agents/ask/task-loop.md", content)
            self.assertEqual(content.count("<!-- ASK TDD OVERRIDE START -->"), 1)
            self.assertEqual(content.count("<!-- ASK TDD OVERRIDE END -->"), 1)
        self.assertEqual((self.root / "_ask/skills/manifest.yaml").read_bytes(), manifest_before)


if __name__ == "__main__":
    unittest.main()
