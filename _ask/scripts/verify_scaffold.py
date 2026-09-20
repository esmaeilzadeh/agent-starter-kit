#!/usr/bin/env python3
"""Human-only verification scaffolder. Agents use --preset in tests only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ASK_KIT_YAML = """schema: ask-checkplan/v1
e2e: not_applicable
no_production_datastore: true
adapters: []
presets:
  - ask-kit
"""

PRESETS = ("ask-kit", "typescript", "python")

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


def _lint_tool(path: Path) -> str | None:
    e, b = _has_any(path, ESLINT_NAMES), _has_any(path, BIOME_NAMES)
    if e and b:
        return "both"
    if e:
        return "eslint"
    if b:
        return "biome"
    return None


def discover_workspaces(root: Path) -> list[dict]:
    found: list[dict] = [{"id": "root", "path": "."}]
    seen = {"."}

    def add(rel: str) -> None:
        rel = rel.rstrip("/") or "."
        if rel in seen:
            return
        seen.add(rel)
        found.append({"id": Path(rel).name, "path": rel})

    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        ws = data.get("workspaces")
        if isinstance(ws, dict):
            ws = ws.get("packages") or []
        for pattern in ws or []:
            for p in root.glob(str(pattern)):
                if p.is_dir() and (
                    (p / "package.json").is_file() or (p / "pyproject.toml").is_file()
                ):
                    add(str(p.relative_to(root)))

    pnpm = root / "pnpm-workspace.yaml"
    if pnpm.is_file():
        for line in pnpm.read_text(encoding="utf-8").splitlines():
            s = line.strip().lstrip("- ").strip("'\"")
            if not s or s.startswith("packages:") or s.startswith("#"):
                continue
            for p in root.glob(s):
                if p.is_dir():
                    add(str(p.relative_to(root)))

    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name in ("node_modules", ".git", ".agents"):
            continue
        if (child / "package.json").is_file() or (child / "pyproject.toml").is_file():
            add(child.name)
    return found


def mixed_lint_disagreement(root: Path) -> bool:
    tools: set[str] = set()
    for w in discover_workspaces(root):
        tool = _lint_tool(root / w["path"])
        if tool == "both":
            return True
        if tool:
            tools.add(tool)
    return len(tools) > 1


def preview_plan(root: Path, preset: str) -> str:
    lines = [ASK_KIT_YAML.rstrip() if preset == "ask-kit" else f"presets:\n  - {preset}"]
    if preset != "ask-kit":
        lines = [
            "schema: ask-checkplan/v1",
            "e2e: not_applicable",
            f"presets:",
            f"  - {preset}",
        ]
    lines.append("workspaces:")
    for w in discover_workspaces(root):
        lines.append(f"  - id: {w['id']}")
        lines.append(f"    path: {w['path']}")
    return "\n".join(lines) + "\n"


def apply_with_rollback(dest: Path, body: str, after_write=None) -> None:
    existed = dest.is_file()
    backup = dest.read_text(encoding="utf-8") if existed else None
    try:
        write_plan(dest, body)
        if after_write:
            after_write()
    except Exception:
        if backup is None:
            if dest.is_file():
                dest.unlink()
        else:
            dest.write_text(backup, encoding="utf-8")
        raise


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
    p.add_argument(
        "--wizard-preview",
        action="store_true",
        help="Print the plan that would be written (preview). Does not write.",
    )
    p.add_argument(
        "--confirm",
        action="store_true",
        help="Required with a write in the interactive wizard. Tests use --preset.",
    )
    args = p.parse_args(argv)
    if argv is not None and any(a in ("-h", "--help") for a in argv):
        return 0

    root = Path(args.root).resolve()
    if args.wizard_preview:
        preset = args.preset or "ask-kit"
        print(preview_plan(root, preset), end="")
        return 0

    if not args.preset:
        require_tty()
        body = preview_plan(root, "ask-kit")
        if not args.confirm:
            print(body, file=sys.stderr)
            print(
                "verify-scaffold: interactive wizard is human-only; re-run with --confirm to apply.",
                file=sys.stderr,
            )
            return 2
        dest = yaml_path(root)
        if dest.is_file() and not args.re_scaffold:
            print(f"verify-scaffold: {dest} exists; left in place (use --re-scaffold for a candidate)")
            return 0
        apply_with_rollback(dest, body)
        print(f"verify-scaffold: wrote {dest}")
        return 0

    if args.preset not in PRESETS:
        print(f"verify-scaffold: unknown preset {args.preset}", file=sys.stderr)
        return 2

    if mixed_lint_disagreement(root):
        print(
            "verify-scaffold: eslint and biome both present; stop with a choice (eslint or biome).",
            file=sys.stderr,
        )
        return 1

    body = preview_plan(root, args.preset)
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
