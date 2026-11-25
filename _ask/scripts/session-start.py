#!/usr/bin/env python3
"""Load the installed AskIt workflow for a Codex or Cursor session."""

import json
from pathlib import Path
import subprocess
import sys


def main(runtime: str) -> None:
    root = Path(__file__).resolve().parents[2]
    try:
        workflow = (root / ".agents/ask/session.md").read_text(encoding="utf-8")
        subprocess.run([str(root / "ask"), "access-check"], cwd=root,
                       capture_output=True, text=True, check=True)
        context = f"AskIt project access preflight passed.\n\n{workflow}"
    except subprocess.CalledProcessError as error:
        detail = (error.stdout + error.stderr).strip()
        context = f"STOP: AskIt project access preflight failed. Restore access before project work.\n{detail}"
    except (OSError, UnicodeError) as error:
        context = f"STOP: AskIt session setup failed. Restore the local installation before project work.\n{error}"

    if runtime == "codex":
        payload = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}
    else:
        payload = {"additional_context": context}
    print(json.dumps(payload))


if __name__ == "__main__":
    main(sys.argv[1])
