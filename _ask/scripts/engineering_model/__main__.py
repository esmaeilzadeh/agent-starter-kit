"""Standalone public Engineering Model commands."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .validation import SLUG
from .admission import admit, load_published, validate_current
from .actions import run_action
from .snapshot import decode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ask model")
    commands = parser.add_subparsers(dest="command", required=True)
    validate_parser = commands.add_parser("validate", help="validate the workstream Engineering Model")
    validate_parser.add_argument("--work-id", required=True)
    admit_parser = commands.add_parser("admit", help="admit current documents to a validated generation (not workflow authorization)")
    admit_parser.add_argument("--work-id", required=True)
    admit_parser.add_argument("--expected", help="refuse if the complete input digest has changed")
    show_parser = commands.add_parser("show", help="read a validated generation; invalid working inputs are noneditable")
    show_parser.add_argument("--work-id", required=True)
    edit_parser = commands.add_parser("edit", help="stage and validate a document change batch")
    edit_parser.add_argument("--work-id", required=True)
    edit_parser.add_argument("--expected", required=True, help="complete displayed input digest")
    edit_parser.add_argument("--batch", required=True, help="JSON proposal file")
    args = parser.parse_args(argv)

    root = Path.cwd().resolve()
    if not SLUG.fullmatch(args.work_id):
        parser.error("--work-id must be a lowercase hyphenated slug")
    if args.command == "edit":
        def action(snapshot):
            batch = decode(Path(args.batch).read_bytes())
            files = batch.get("files") if isinstance(batch, dict) else None
            if not isinstance(files, dict):
                raise ValueError("batch requires a files map")
            allowed = {f"specs/current/{args.work_id}.json", f"specs/current/{args.work_id}.md",
                       f"work/{args.work_id}/test-plan.json"}
            if not set(files) <= allowed:
                raise ValueError("file batches may edit only the selected workstream's canonical documents")
            return {path: text.encode("utf-8") if isinstance(text, str) else None if text is None
                    else (_ for _ in ()).throw(ValueError("file payload must be text or null"))
                    for path, text in files.items()}
        result = run_action(root, args.work_id, args.expected, action)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["valid"] else 1
    if args.command == "validate":
        captured, diagnostics = validate_current(root, args.work_id)
    else:
        captured, diagnostics = admit(root, args.work_id, getattr(args, "expected", None))
    if args.command == "show" and diagnostics:
        try:
            captured = load_published(root, args.work_id)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            captured = None
            diagnostics.append({"code": "EM007_GENERATION", "path": "model-state/current.json", "message": str(exc)})
    result = {
        "schema": "ask-engineering-validation/v1",
        "work_id": args.work_id,
        "valid": not diagnostics,
        "diagnostics": diagnostics,
        "snapshot": captured.identity if captured is not None else None,
    }
    if args.command == "show":
        result.update(model=captured.document if captured is not None else None,
                      editable=not diagnostics, last_validated=bool(diagnostics and captured is not None))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not diagnostics else 1


if __name__ == "__main__":
    raise SystemExit(main())
