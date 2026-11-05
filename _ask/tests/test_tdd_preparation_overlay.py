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
        (self.root / "_ask/scripts").mkdir(parents=True)
        (self.root / "bin").mkdir()
        shutil.copy2(ROOT / "ask", self.root / "ask")
        shutil.copy2(ROOT / "_ask/skills/prepare-skills.sh",
                     self.root / "_ask/skills/prepare-skills.sh")
        shutil.copy2(ROOT / "_ask/skills/tdd-override.md",
                     self.root / "_ask/skills/tdd-override.md")
        shutil.copy2(ROOT / "_ask/scripts/ask-complete.sh",
                     self.root / "_ask/scripts/ask-complete.sh")
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
            touch "$PWD/npx-called"
            for view in .agents/skills/tdd/SKILL.md .cursor/skills/tdd/SKILL.md; do
              mkdir -p "$(dirname "$view")"
              cat > "$view" <<'SKILL'
            # TDD upstream

            UPSTREAM-CANARY-START
            Keep this content.
            UPSTREAM-CANARY-END

            ## Refactoring
            Refactoring is not part of the loop.
            SKILL
            done
            """), encoding="utf-8")
        npx.chmod(0o755)

    def set_installer(self, body):
        npx = self.root / "bin/npx"
        npx.write_text("#!/usr/bin/env bash\nset -euo pipefail\n" + body, encoding="utf-8")
        npx.chmod(0o755)

    def prepare(self, skip_install=False):
        env = dict(os.environ)
        env["PATH"] = str(self.root / "bin") + os.pathsep + env.get("PATH", "")
        if skip_install:
            env["SKIP_INSTALL"] = "1"
        return subprocess.run(["./ask", "prepare"], cwd=self.root, env=env,
                              text=True, capture_output=True)

    def test_both_views_use_canonical_tdd_override(self):
        manifest_before = (self.root / "_ask/skills/manifest.yaml").read_bytes()
        result = self.prepare()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "npx-called").is_file(), "controlled installer was not invoked")
        for relative in self.installed_views:
            content = (self.root / relative).read_text(encoding="utf-8")
            self.assertIn("UPSTREAM-CANARY-START\nKeep this content.\nUPSTREAM-CANARY-END", content)
            self.assertIn("Red -> Green -> Refactor", content)
            self.assertIn(".agents/ask/task-loop.md", content)
            self.assertEqual(content.count("<!-- ASK TDD OVERRIDE START -->"), 1)
            self.assertEqual(content.count("<!-- ASK TDD OVERRIDE END -->"), 1)
        self.assertEqual((self.root / "_ask/skills/manifest.yaml").read_bytes(), manifest_before)

        self.set_installer('''
mkdir -p .agents/skills/tdd
cat > .agents/skills/tdd/SKILL.md <<'SKILL'
# TDD upstream
SKILL
''')
        (self.root / self.installed_views[1]).unlink()
        missing_view = self.prepare()
        self.assertNotEqual(missing_view.returncode, 0, missing_view.stdout)
        self.assertIn("missing required Cursor TDD skill output", missing_view.stderr)

    def test_repeated_prepare_replaces_managed_override(self):
        self.set_installer('''
if [[ ! -f "$PWD/first-install" ]]; then
  touch "$PWD/first-install"
  for view in .agents/skills/tdd/SKILL.md .cursor/skills/tdd/SKILL.md; do
    mkdir -p "$(dirname "$view")"
    printf '# TDD upstream\\n\\nUPSTREAM-CANARY\\n' > "$view"
  done
fi
''')
        first = self.prepare()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        for relative in self.installed_views:
            view = self.root / relative
            content = view.read_text(encoding="utf-8").replace("Red -> Green -> Refactor", "STALE OVERRIDE")
            view.write_text(content, encoding="utf-8")

        second = self.prepare()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        second_snapshots = {}
        for relative in self.installed_views:
            content = (self.root / relative).read_text(encoding="utf-8")
            self.assertIn("UPSTREAM-CANARY", content)
            self.assertEqual(content.count("<!-- ASK TDD OVERRIDE START -->"), 1)
            self.assertEqual(content.count("<!-- ASK TDD OVERRIDE END -->"), 1)
            self.assertIn("Red -> Green -> Refactor", content)
            self.assertNotIn("STALE OVERRIDE", content)
            second_snapshots[relative] = content.encode("utf-8")

        third = self.prepare()
        self.assertEqual(third.returncode, 0, third.stdout + third.stderr)
        self.assertEqual({path: (self.root / path).read_bytes() for path in self.installed_views},
                         second_snapshots)

    def test_skip_install_only_validates_pins(self):
        initial = self.prepare()
        self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
        snapshots = {path: (self.root / path).read_bytes() for path in self.installed_views}
        manifest = (self.root / "_ask/skills/manifest.yaml").read_bytes()
        result = self.prepare(skip_install=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({path: (self.root / path).read_bytes() for path in self.installed_views}, snapshots)
        self.assertEqual((self.root / "_ask/skills/manifest.yaml").read_bytes(), manifest)

    def test_failed_required_install_is_not_success(self):
        for relative in self.installed_views:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("stale output\n", encoding="utf-8")
        self.set_installer("exit 9\n")
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("installer", (result.stdout + result.stderr).lower())
        self.assertNotIn("prepare-skills: ok tdd", result.stdout)

    def test_missing_optional_skill_is_not_fabricated(self):
        manifest = self.root / "_ask/skills/manifest.yaml"
        manifest.write_text(manifest.read_text().replace("required: true", "required: false"), encoding="utf-8")
        self.set_installer("exit 9\n")
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.root / self.installed_views[0]).exists())
        self.assertFalse((self.root / self.installed_views[1]).exists())

    def test_success_exit_without_required_output_is_failure(self):
        cursor = self.root / self.installed_views[1]
        cursor.parent.mkdir(parents=True, exist_ok=True)
        cursor.write_text("old Cursor view\n", encoding="utf-8")
        self.set_installer("exit 0\n")
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("tdd", (result.stdout + result.stderr).lower())
        self.assertFalse((self.root / self.installed_views[0]).exists())
        self.assertEqual(cursor.read_text(encoding="utf-8"), "old Cursor view\n")


if __name__ == "__main__":
    unittest.main()
