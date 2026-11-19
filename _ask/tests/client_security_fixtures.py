"""Disposable client and runtime fixtures for client security journeys."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ClientFixture:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="ask-client-")
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.config = self.root / "config"
        self.cache = self.root / "cache"
        self.prefix = self.root / "prefix"
        for path in (self.home, self.config, self.cache, self.prefix):
            path.mkdir()
        self.env = os.environ.copy()
        for name in ("BASH_ENV", "ENV", "PYTHONPATH", "PYTHONHOME", "ASK_WORK_ID"):
            self.env.pop(name, None)
        self.env.update({
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.config),
            "XDG_CACHE_HOME": str(self.cache),
            "ASKIT_PREFIX": str(self.prefix),
            "ASKIT_SKIP_COMPLETION_INSTALL": "",
            "SKIP_INSTALL": "1",
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "init.defaultBranch",
            "GIT_CONFIG_VALUE_0": "main",
            "GIT_CONFIG_KEY_1": "safe.directory",
            "GIT_CONFIG_VALUE_1": "*",
        })

    def close(self) -> None:
        self._tmp.cleanup()

    def run(self, argv: list[str], *, cwd: Path | None = None,
            env: dict[str, str] | None = None, input: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            argv,
            cwd=cwd or ROOT,
            env=env or self.env,
            input=input,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )

    def git_project(self, path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        self.run(["git", "init", "-q", str(path)])
        self.run(["git", "-C", str(path), "config", "user.name", "Client Test"])
        self.run(["git", "-C", str(path), "config", "user.email", "client@example.invalid"])
        (path / "README.md").write_text("client-owned\n", encoding="utf-8")
        self.run(["git", "-C", str(path), "add", "README.md"])
        self.run(["git", "-C", str(path), "commit", "-qm", "initial client"])
        return path

    def install_launcher(self) -> Path:
        revision = self.run(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
        proc = self.run(
            ["bash", "-s", "--", "--source", str(ROOT), "--ref", revision,
             "--prefix", str(self.prefix)],
            cwd=self.root,
            input=(ROOT / "askit").read_text(encoding="utf-8"),
        )
        if proc.returncode:
            raise AssertionError(f"launcher install failed: {proc.stderr}")
        return self.prefix / "bin" / "askit"

    def make_untrusted_source(self, marker: Path) -> Path:
        source = self.git_project(self.root / "untrusted-kit")
        askit = source / "askit"
        askit.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        askit.chmod(0o755)
        helper = source / "_ask/scripts/install-user-completion.sh"
        helper.parent.mkdir(parents=True, exist_ok=True)
        helper.write_text(
            "#!/bin/sh\nprintf executed > \"$ASKIT_TEST_MARKER\"\n", encoding="utf-8"
        )
        helper.chmod(0o755)
        self.run(["git", "-C", str(source), "add", "askit", "_ask"])
        self.run(["git", "-C", str(source), "commit", "-qm", "untrusted source"])
        child = self.env.copy()
        child.pop("ASKIT_SKIP_COMPLETION_INSTALL", None)
        child["ASKIT_TEST_MARKER"] = str(marker)
        return source

