#!/usr/bin/env python3
"""Human-only verification scaffolder. Agents use --preset in tests only."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ASK_KIT_YAML = """schema: ask-checkplan/v1
e2e: not_applicable
no_production_datastore: true
adapters: []
presets:
  - ask-kit
"""

ESLINT_NAMES = (
    "eslint.config.js",
    "eslint.config.mjs",
    "eslint.config.cjs",
    ".eslintrc",
    ".eslintrc.js",
    ".eslintrc.cjs",
    ".eslintrc.json",
    ".eslintrc.yml",
    ".eslintrc.yaml",
)
BIOME_NAMES = ("biome.json", "biome.jsonc")


def _has_any(root: Path, names: tuple[str, ...]) -> bool:
    return any((root / n).is_file() for n in names)


def mixed_lint_disagreement(root: Path) -> bool:
    return _has_any(root, ESLINT_NAMES) and _has_any(root, BIOME_NAMES)


def yaml_path(root: Path) -> Path:
    return root / ".agents" / "verification.yaml"


def candidate_path(root: Path) -> Path:
    return root / ".agents" / "verification.yaml.candidate"


def require_tty() -> None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print(
            "verify-scaffold: human-only. Agents must not run the verify wizard (needs a TTY).",
            file=sys.stderr,
        )
        print("verify-scaffold: use --help, or --preset <id> in tests.", file=sys.stderr)
        raise SystemExit(2)


def write_plan(dest: Path, body: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="verify-scaffold",
        description="Human-only verification scaffolder. Writes .agents/verification.yaml only when absent.",
    )
    p.add_argument("--root", default=".")
    p.add_argument(
        "--preset",
        help="Non-interactive preset id for tests (e.g. ask-kit). Product agent labor may not use this.",
    )
    p.add_argument(
        "--re-scaffold",
        action="store_true",
        help="Write a candidate file; do not replace existing yaml.",
    )
    args = p.parse_args(argv)
    if argv is not None and any(a in ("-h", "--help") for a in argv):
        return 0

    root = Path(args.root).resolve()
    if not args.preset:
        require_tty()
        print("verify-scaffold: interactive wizard is human-only; pick a stack in the terminal.", file=sys.stderr)
        return 2

    if args.preset != "ask-kit":
        print(f"verify-scaffold: unknown preset {args.preset}", file=sys.stderr)
        return 2

    if mixed_lint_disagreement(root):
        print(
            "verify-scaffold: eslint and biome both present; stop with a choice (eslint or biome).",
            file=sys.stderr,
        )
        return 1

    body = ASK_KIT_YAML
    existing = yaml_path(root)
    if args.re_scaffold:
        write_plan(candidate_path(root), body)
        print(f"verify-scaffold: wrote {candidate_path(root)}")
        return 0
    if existing.is_file():
        print(f"verify-scaffold: {existing} exists; left in place (use --re-scaffold for a candidate)")
        return 0
    write_plan(existing, body)
    print(f"verify-scaffold: wrote {existing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
