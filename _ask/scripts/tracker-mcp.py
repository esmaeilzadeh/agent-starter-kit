#!/usr/bin/env python3
"""Launch the pinned Jira MCP with only its private tracker credentials."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def main() -> int:
    parser_path = Path(__file__).with_name("tracker-config.py")
    spec = importlib.util.spec_from_file_location("askit_tracker_config", parser_path)
    if spec is None or spec.loader is None:
        print("tracker-mcp: tracker configuration is unavailable", file=sys.stderr)
        return 1
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    try:
        root = config.canonical_root(args.root)
        credentials = config.read_credentials(root)
        if credentials.get("tracker") != "jira" or not credentials.get("url"):
            raise config.ConfigError("Jira tracker is not configured")
        token = credentials["credentials"].get("JIRA_PERSONAL_TOKEN")
        if not isinstance(token, str) or not token:
            raise config.ConfigError("Jira credentials are not configured")
        environment = {key: value for key, value in os.environ.items() if key in config.BASE_ENV}
        environment.update(JIRA_URL=credentials["url"], JIRA_PERSONAL_TOKEN=token)
        os.execvpe("uvx", ["uvx", "mcp-atlassian==0.24.6"], environment)
    except (config.ConfigError, OSError) as error:
        print(f"tracker-mcp: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
