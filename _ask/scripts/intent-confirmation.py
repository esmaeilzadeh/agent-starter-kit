#!/usr/bin/env python3
"""Record and validate explicit human confirmation of a workstream intent."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata


SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SCHEMA = "ask-intent-confirmation/v1"
CHOICE_SCHEMA = "ask-intent-confirmation/v2"
PROMPT = "Do you approve the complete intent and every listed assumption as written?"


def affirmative(response: str) -> bool:
    value = " ".join(unicodedata.normalize("NFKC", response).casefold().split())
    value = value.rstrip(".! ")
    return value in {"yes", "yes, i approve", "yes, defaults ok", "approve", "approved", "confirmed", "defaults ok", "all recs",
                      "i approve these defaults are ok",
                      "i approve the complete intent and every listed assumption as written"}


def intent_paths(root: Path, work_id: str) -> tuple[Path, Path]:
    if not SLUG.fullmatch(work_id):
        raise ValueError("work-id must be a lowercase hyphenated slug")
    directory = root / "work" / work_id
    return directory / "intent.md", directory / "intent-confirmation.json"


def validate(root: Path, work_id: str) -> str | None:
    intent_path, confirmation_path = intent_paths(root, work_id)
    if not intent_path.is_file():
        return f"missing {intent_path.relative_to(root)}"
    if not confirmation_path.is_file():
        return f"missing {confirmation_path.relative_to(root)}; ask the human to confirm the complete intent and assumptions"
    try:
        confirmation = json.loads(confirmation_path.read_text(encoding="utf-8"))
        intent_digest = hashlib.sha256(intent_path.read_bytes()).hexdigest()
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return f"cannot read intent confirmation: {exc}"
    if not isinstance(confirmation, dict) or confirmation.get("schema") not in {SCHEMA, CHOICE_SCHEMA}:
        return f"{confirmation_path.relative_to(root)} has an unsupported schema"
    if confirmation.get("work_id") != work_id:
        return "intent confirmation work_id does not match"
    if confirmation.get("scope") != "complete-intent-and-assumptions":
        return "confirmation must cover the complete intent and its assumptions"
    if confirmation.get("prompt") != PROMPT:
        return "confirmation was not recorded against the complete-intent approval question"
    if confirmation["schema"] == CHOICE_SCHEMA:
        if confirmation.get("human_choice") != "approve":
            return "recorded choice is not an explicit approval"
    else:
        if not isinstance(confirmation.get("human_response"), str) or not confirmation["human_response"].strip():
            return "intent confirmation must record the human's explicit response"
        if not affirmative(confirmation["human_response"]):
            return "recorded response is not an explicit approval"
    if confirmation.get("intent_sha256") != intent_digest:
        return "intent changed after confirmation; present it again and obtain renewed confirmation"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("confirm", "validate"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--work-id", required=True)
    answer = parser.add_mutually_exclusive_group()
    answer.add_argument("--choice", choices=("approve", "revise"),
                        help="explicit human selection from the complete-intent approval choices")
    answer.add_argument("--response", help="exact human response when choice controls are unavailable")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        intent_path, confirmation_path = intent_paths(root, args.work_id)
        if args.action == "confirm":
            if args.choice == "revise":
                raise ValueError("human requested revisions; intent was not approved")
            if args.choice is None and (not args.response or not args.response.strip()):
                parser.error("confirm requires --choice or --response with the human's explicit approval")
            if args.choice is None and not affirmative(args.response):
                raise ValueError("response must explicitly approve the complete intent and assumptions")
            if not intent_path.is_file():
                raise ValueError(f"missing {intent_path.relative_to(root)}")
            record = {
                "schema": CHOICE_SCHEMA if args.choice else SCHEMA,
                "work_id": args.work_id,
                "scope": "complete-intent-and-assumptions",
                "prompt": PROMPT,
                "intent_sha256": hashlib.sha256(intent_path.read_bytes()).hexdigest(),
            }
            if args.choice:
                record["human_choice"] = args.choice
            else:
                record["human_response"] = args.response.strip()
            confirmation_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            print(f"Recorded confirmation for {intent_path.relative_to(root)}")
            return 0
        error = validate(root, args.work_id)
    except (OSError, ValueError) as exc:
        error = str(exc)
    if error:
        print(f"intent-confirmation: {error}", file=sys.stderr)
        return 1
    print(f"intent-confirmation: valid work-id={args.work_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
