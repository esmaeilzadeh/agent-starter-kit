"""Standalone public Engineering Model commands."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .validation import SLUG
from .snapshot import capture, is_current


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ask model")
    commands = parser.add_subparsers(dest="command", required=True)
    validate_parser = commands.add_parser("validate", help="validate the workstream Engineering Model")
    validate_parser.add_argument("--work-id", required=True)
    args = parser.parse_args(argv)

    root = Path.cwd().resolve()
    if not SLUG.fullmatch(args.work_id):
        parser.error("--work-id must be a lowercase hyphenated slug")
    path = root / "work" / args.work_id / "engineering-model.json"
    try:
        raw = path.read_bytes()
    except OSError as exc:
        result = {
            "schema": "ask-engineering-validation/v1",
            "work_id": args.work_id,
            "valid": False,
            "diagnostics": [{"code": "EM001_MODEL_READ", "path": f"work/{args.work_id}/engineering-model.json", "message": str(exc)}],
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 1
    try:
        captured = capture(root, args.work_id, model_bytes=raw)
        diagnostics = captured.diagnostics(root)
        snapshot = captured.identity
    except (UnicodeError, ValueError) as exc:
        diagnostics = [{
            "code": "EM001_JSON",
            "path": str(path.relative_to(root)),
            "message": f"invalid JSON: {exc}",
        }]
        snapshot = None
    if snapshot is not None:
        if not is_current(captured, root):
            diagnostics.append({
                "code": "EM007_INPUT_CHANGED",
                "path": f"work/{args.work_id}/engineering-model.json",
                "message": "model or referenced inputs changed while validation was running",
            })
    result = {
        "schema": "ask-engineering-validation/v1",
        "work_id": args.work_id,
        "valid": not diagnostics,
        "diagnostics": diagnostics,
        "snapshot": snapshot,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not diagnostics else 1


if __name__ == "__main__":
    raise SystemExit(main())
