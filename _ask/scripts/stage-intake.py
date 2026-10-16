#!/usr/bin/env python3
"""Read-only shared subject resolution for the adopted initial stages."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from engineering_model.context import resolve
from engineering_model.validation import SLUG


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ask stage-intake")
    parser.add_argument("--stage", required=True, choices=("00-explore", "01-grill"))
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--request", required=True, help="structured request JSON file")
    parser.add_argument("--branch", help="execution locator only; never a subject identity")
    args = parser.parse_args(argv)
    if not SLUG.fullmatch(args.work_id):
        parser.error("--work-id must be a lowercase hyphenated slug")
    try:
        request = json.loads(Path(args.request).read_bytes())
        if not isinstance(request, dict):
            raise ValueError("request JSON must be an object")
        result = resolve(Path.cwd(), args.work_id, request, branch=args.branch)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "diagnostics": [{"code": "EM018_REQUEST", "message": str(exc)}]}),
              file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
