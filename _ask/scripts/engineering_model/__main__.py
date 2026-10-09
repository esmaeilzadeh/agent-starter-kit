"""Standalone public Engineering Model commands."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import subprocess

from .validation import SLUG
from .admission import admit, load_published, validate_current
from .actions import edit
from .snapshot import decode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ask model")
    commands = parser.add_subparsers(dest="command", required=True)
    validate_parser = commands.add_parser("validate", help="validate the workstream Engineering Model")
    validate_parser.add_argument("--work-id", required=True)
    validate_parser.add_argument("--full", action="store_true", help="force full validation (currently every check is full)")
    admit_parser = commands.add_parser("admit", help="admit current documents to a validated generation (not workflow authorization)")
    admit_parser.add_argument("--work-id", required=True)
    admit_parser.add_argument("--expected", help="refuse if the complete input digest has changed")
    admit_parser.add_argument("--action", help="label a cooperating implementation or review action")
    admit_parser.add_argument("action_command", nargs=argparse.REMAINDER, help="action argv after -- (no shell)")
    show_parser = commands.add_parser("show", help="read a validated generation; invalid working inputs are noneditable")
    show_parser.add_argument("--work-id", required=True)
    show_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    show_parser.add_argument("--node", help="focus the projection on one stable node ID")
    show_parser.add_argument("--candidate", help="inspect evidence for this candidate revision")
    edit_parser = commands.add_parser("edit", help="stage and validate a document change batch")
    edit_parser.add_argument("--work-id", required=True)
    edit_parser.add_argument("--expected", required=True, help="complete displayed input digest")
    edit_parser.add_argument("--batch", required=True, help="JSON proposal file")
    watch_parser = commands.add_parser("watch", help="validate external saves with native observation and freshness fallback")
    watch_parser.add_argument("--work-id", required=True)
    watch_parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)

    root = Path.cwd().resolve()
    if not SLUG.fullmatch(args.work_id):
        parser.error("--work-id must be a lowercase hyphenated slug")
    if args.command == "admit" and (args.action or args.action_command):
        if not args.action or not args.action_command:
            parser.error("--action requires an action command after --")
        action_command = args.action_command
        if action_command[0] == "--":
            action_command = action_command[1:]
        if not action_command:
            parser.error("action command cannot be empty")
        from .workflow import workflow_admission
        try:
            with workflow_admission(root, args.work_id, args.expected) as admitted:
                if admitted is None:
                    raise ValueError("action requires an adopted Engineering Model")
                process = subprocess.run(action_command, cwd=root)
            return process.returncode if process.returncode >= 0 else 1
        except (OSError, ValueError, KeyError, TypeError) as exc:
            diagnostics = getattr(exc, "diagnostics", [getattr(exc, "diagnostic", {
                "code": "EM007_ACTION", "path": "$", "message": str(exc)})])
            print(json.dumps({"valid": False, "diagnostics": diagnostics}), file=sys.stderr)
            return 1
    if args.command == "watch":
        from .observer import updates
        try:
            valid = True
            for result in updates(root, args.work_id, once=args.once):
                print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
                valid = result["valid"]
            return 0 if valid else 1
        except (RuntimeError, OSError) as exc:
            print(json.dumps({"valid": False, "diagnostics": [{"code": "EM007_OBSERVER", "path": "$", "message": str(exc)}]}))
            return 1
    if args.command == "edit":
        result = edit(root, args.work_id, args.expected, lambda: decode(Path(args.batch).read_bytes()))
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
        if captured is not None:
            try:
                from .projection import markdown as render_markdown, project
                view = project(captured, root, node_id=args.node, candidate_sha=args.candidate)
                result["schema"] = view["schema"]
                result.update({key: value for key, value in view.items()
                               if key not in {"schema", "work_id", "snapshot", "model"}})
                if args.format == "markdown":
                    if diagnostics:
                        print("Last validated snapshot — Noneditable. Working inputs failed admission.\n")
                        for diagnostic in diagnostics:
                            print(f"- {diagnostic['code']}: {diagnostic.get('message', '')}")
                        print()
                    print(render_markdown(view), end="")
                    return 0 if not diagnostics else 1
            except (ValueError, OSError, KeyError, TypeError) as exc:
                result["diagnostics"].append({"code": "EM004_PROJECTION", "path": "$",
                                              "message": str(exc)})
                result["valid"] = False
                result["editable"] = False
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not diagnostics else 1


if __name__ == "__main__":
    raise SystemExit(main())
