"""Disposable client and runtime fixtures for client security journeys."""

from __future__ import annotations

import os
import json
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
        self.tmp = self.root / "tmp"
        for path in (self.home, self.config, self.cache, self.prefix, self.tmp):
            path.mkdir()
        self.env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "TZ": "UTC",
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "XDG_CONFIG_HOME": str(self.config),
            "XDG_CACHE_HOME": str(self.cache),
            "ASKIT_PREFIX": str(self.prefix),
            "ASKIT_SKIP_COMPLETION_INSTALL": "1",
            "SKIP_INSTALL": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_COUNT": "3",
            "GIT_CONFIG_KEY_0": "init.defaultBranch",
            "GIT_CONFIG_VALUE_0": "main",
            "GIT_CONFIG_KEY_1": "user.name",
            "GIT_CONFIG_VALUE_1": "Client Test",
            "GIT_CONFIG_KEY_2": "user.email",
            "GIT_CONFIG_VALUE_2": "client@example.invalid",
        }

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
        migrate = source / "_ask/scripts/copy-project-config.sh"
        migrate.write_text(
            "#!/bin/sh\nprintf executed > \"$ASKIT_TEST_MARKER\"\n", encoding="utf-8"
        )
        migrate.chmod(0o755)
        self.run(["git", "-C", str(source), "add", "askit", "_ask"])
        self.run(["git", "-C", str(source), "commit", "-qm", "untrusted source"])
        return source

    def fake_model_runtime(self, *, identity: str = "gpt-6.1-sol",
                           models: list[str] | None = None,
                           can_switch: bool = False) -> tuple[Path, Path]:
        adapter = self.root / "fake-model-runtime.py"
        log = self.root / "model-runtime.jsonl"
        adapter.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "request = json.load(sys.stdin)\n"
            "with open(os.environ['ASK_MODEL_RUNTIME_LOG'], 'a', encoding='utf-8') as f:\n"
            "    f.write(json.dumps(request) + '\\n')\n"
            "action = request['action']\n"
            f"models = {json.dumps(models or ['gpt-6.1-sol', 'gpt-6-luna', 'gpt-6-astra'])}\n"
            f"identity = {json.dumps(identity)}\n"
            f"can_switch = {json.dumps(can_switch)}\n"
            "response = {'models': models} if action == 'catalog' else "
            "({'model': identity} if action == 'identity' else "
            "({'supported': can_switch, 'model': request.get('model')} if action == 'switch' else {}))\n"
            "print(json.dumps(response))\n",
            encoding="utf-8",
        )
        adapter.chmod(0o755)
        return adapter, log
