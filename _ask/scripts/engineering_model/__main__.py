"""Standalone public Engineering Model commands."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .validation import validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ask model")
    commands = parser.add_subparsers(dest="command", required=True)
    validate_parser = commands.add_parser("validate", help="validate the workstream Engineering Model")
    validate_parser.add_argument("--work-id", required=True)
    args = parser.parse_args(argv)

    root = Path.cwd().resolve()
    path = root / "work" / args.work_id / "engineering-model.json"
    try:
        raw = path.read_bytes()
    except OSError as exc:
        result = {
            "schema": "ask-engineering-validation/v1",
            "work_id": args.work_id,
            "valid": False,
            "diagnostics": [{"code": "EM001_MODEL_READ", "path": str(path), "message": str(exc)}],
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 1
    try:
        document = json.loads(raw)
        diagnostics = validate(document, root, args.work_id)
    except (UnicodeError, json.JSONDecodeError) as exc:
        diagnostics = [{
            "code": "EM001_JSON",
            "path": str(path.relative_to(root)),
            "message": f"invalid JSON: {exc}",
        }]
    result = {
        "schema": "ask-engineering-validation/v1",
        "work_id": args.work_id,
        "valid": not diagnostics,
        "diagnostics": diagnostics,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not diagnostics else 1


if __name__ == "__main__":
    raise SystemExit(main())
