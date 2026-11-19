#!/usr/bin/env python3
"""Launch the pinned Jira MCP with only its private tracker credentials."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import stat
import sys
from pathlib import Path


def resolve_uvx(root: Path) -> str:
    for entry in os.environ.get("PATH", os.defpath).split(os.pathsep):
        candidate = Path(entry or os.curdir) / "uvx"
        try:
            path = candidate.resolve(strict=True)
            info = path.stat()
        except OSError:
            continue
        if (path == root or root in path.parents or not stat.S_ISREG(info.st_mode)
                or not os.access(path, os.X_OK) or info.st_uid not in {0, os.getuid()}
                or stat.S_IMODE(info.st_mode) & 0o022):
            continue
        return str(path)
    raise ValueError("no safe uvx launcher was found outside the checkout")


def main() -> int:
    parser_path = Path(__file__).with_name("tracker-config.py")
    spec = importlib.util.spec_from_file_location("askit_tracker_config", parser_path)
    if spec is None or spec.loader is None:
        print("tracker-mcp: tracker configuration is unavailable", file=sys.stderr)
        return 1
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    try:
        root = config.canonical_root(args.root)
        launcher = resolve_uvx(root)
        pins = json.loads((root / "_ask/skills/dependency-pins.json").read_text(encoding="utf-8"))
        package = pins["packages"]["mcp-atlassian"]
        wheel, digest = package["wheel"], package["wheel_sha256"]
        if (package.get("version") != "0.24.6" or not wheel.startswith("https://")
                or not re.fullmatch(r"[a-f0-9]{64}", digest)):
            raise config.ConfigError("reviewed Jira MCP pin is invalid")
        credentials = config.read_credentials(root)
        if credentials.get("tracker") != "jira" or not credentials.get("url"):
            raise config.ConfigError("Jira tracker is not configured")
        token = credentials["credentials"].get("JIRA_PERSONAL_TOKEN")
        if not isinstance(token, str) or not token:
            raise config.ConfigError("Jira credentials are not configured")
        environment = {key: value for key, value in os.environ.items() if key in config.BASE_ENV}
        environment["PATH"] = os.defpath
        environment.update(JIRA_URL=credentials["url"], JIRA_PERSONAL_TOKEN=token)
        requirement = f"mcp-atlassian @ {wheel}#sha256={digest}"
        os.execve(launcher, [launcher, "--from", requirement, "mcp-atlassian"], environment)
    except (config.ConfigError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"tracker-mcp: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
