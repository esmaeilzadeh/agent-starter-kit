"""Merge AskIt session handlers into Cursor and Codex project hook files."""

import json
from pathlib import Path
import sys


def update(path: Path, event: str, handler: dict) -> None:
    try:
        config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot safely update hook configuration {path}: {error}") from error
    if not isinstance(config, dict):
        raise ValueError(f"hook configuration must be an object: {path}")
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"hooks must be an object: {path}")
    entries = hooks.setdefault(event, [])
    if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
        raise ValueError(f"{event} must be an array of objects: {path}")
    if handler not in entries:
        entries.append(handler)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(root: Path) -> None:
    update(root / ".cursor/hooks.json", "sessionStart", {
        "command": ".cursor/hooks/access-preflight.sh",
    })
    update(root / ".codex/hooks.json", "SessionStart", {
        "hooks": [{
            "type": "command",
            "command": 'python3 "$(git rev-parse --show-toplevel)/_ask/scripts/session-start.py" codex',
            "statusMessage": "Loading AskIt workflow",
        }],
    })


if __name__ == "__main__":
    try:
        main(Path(sys.argv[1]).resolve())
    except (OSError, ValueError) as error:
        sys.exit(f"askit: {error}")
