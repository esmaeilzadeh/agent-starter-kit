#!/usr/bin/env python3
"""Fail-closed OpenSpec invoke helper for kit gates.

Targeted invocations only. Never pass --all / --changes / --specs.
Measured field names: OpenSpec 1.13.0 (see _ask/openspec-pin.yaml).
Agents must not install @latest; this helper asserts the pin.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

FORBIDDEN_FLAGS = ("--all", "--changes", "--specs")
PILOT_LINE = re.compile(r"^Engine:\s*openspec\s*$", re.M)
PIN_KEYS = ("package", "revision", "schema", "profile")


def die(msg: str, code: int = 1) -> None:
    print(f"openspec-cli: {msg}", file=sys.stderr)
    raise SystemExit(code)


def repo_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    cwd = Path.cwd()
    for p in (cwd, *cwd.parents):
        if (p / ".git").exists() or (p / "_ask").is_dir():
            return p
    return cwd


def load_pin(path: Path) -> dict[str, str]:
    if not path.is_file():
        die(f"missing pin file {path}", 2)
    out: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.+?)\s*$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
        out[key] = val
    for key in PIN_KEYS:
        if not out.get(key):
            die(f"pin missing {key}", 2)
    rev = out["revision"]
    if rev.lower() == "latest":
        die("pin revision must not be latest", 2)
    return out


def find_bin() -> str:
    env = os.environ.get("OPENSPEC_BIN", "").strip()
    if env:
        if not os.path.isfile(env) or not os.access(env, os.X_OK):
            die("missing openspec executable (set OPENSPEC_BIN or install the pinned revision)")
        return env
    found = shutil.which("openspec")
    if not found:
        die("missing openspec executable (set OPENSPEC_BIN or install the pinned revision)")
    return found


def assert_version(bin_path: str, pin: dict[str, str]) -> str:
    proc = subprocess.run(
        [bin_path, "--version"],
        capture_output=True,
        text=True,
        env=_cli_env(),
    )
    got = (proc.stdout or "").strip()
    if proc.returncode != 0 or not got:
        die(f"version assertion failed (exit {proc.returncode}): {(proc.stderr or got).strip()}")
    want = pin["revision"]
    if got != want:
        die(f"version mismatch: got {got!r} want {want!r}")
    return got


def _cli_env() -> dict[str, str]:
    env = os.environ.copy()
    env["OPENSPEC_TELEMETRY"] = "0"
    return env


def _reject_forbidden(args: list[str]) -> None:
    for a in args:
        if a in FORBIDDEN_FLAGS:
            die(f"refusing bulk flag {a} as gate input")


def parse_json(raw: str, stderr: str) -> dict:
    text = (raw or "").strip()
    if not text:
        die(f"invalid JSON (empty stdout); stderr={(stderr or '').strip()!r}")
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as exc:
        die(f"invalid JSON: {exc}")
    if not isinstance(doc, dict):
        die("JSON root must be an object")
    return doc


def shape_fail(doc: dict) -> str | None:
    if "root" in doc and doc.get("root") is None:
        return "root: null"
    status = doc.get("status")
    if isinstance(status, list):
        for item in status:
            if isinstance(item, dict) and item.get("severity") == "error":
                code = item.get("code") or "error"
                return f"status[].severity=error ({code})"
    return None


def sanitize(doc: dict) -> dict:
    out = json.loads(json.dumps(doc))
    if "nextSteps" in out:
        out["nextSteps"] = [
            "Use kit stage commands (./ask). OpenSpec CLI is an internal engine."
        ]
    return out


def run_json(bin_path: str, args: list[str]) -> tuple[dict, int]:
    _reject_forbidden(args)
    argv = [bin_path, *args]
    if "--json" not in argv:
        argv.append("--json")
    proc = subprocess.run(argv, capture_output=True, text=True, env=_cli_env())
    doc = parse_json(proc.stdout, proc.stderr or "")
    reason = shape_fail(doc)
    if reason:
        die(reason)
    return doc, proc.returncode


def matching_items(doc: dict, work_id: str) -> list[dict]:
    items = doc.get("items")
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, dict) and i.get("id") == work_id]


def cmd_validate(bin_path: str, work_id: str) -> dict:
    doc, code = run_json(bin_path, ["validate", work_id, "--strict"])
    matches = matching_items(doc, work_id)
    if len(matches) == 0:
        die(f"validate returned no item for {work_id}")
    if len(matches) > 1:
        die(f"validate returned more than one item for {work_id}")
    item = matches[0]
    if code != 0 or item.get("valid") is not True:
        die(f"invalid change {work_id}")
    return sanitize(doc)


def planning_incomplete(doc: dict) -> str | None:
    if doc.get("isPlanningComplete") is not True:
        return "isPlanningComplete is not true"
    if doc.get("isComplete") is not True:
        return "isComplete is not true"
    arts = doc.get("artifacts") or []
    if isinstance(arts, list):
        for a in arts:
            if isinstance(a, dict) and a.get("status") == "blocked":
                return f"artifact {a.get('id')} status=blocked"
    return None


def cmd_status(bin_path: str, work_id: str, require_complete: bool) -> dict:
    doc, code = run_json(bin_path, ["status", "--change", work_id])
    if code != 0:
        die(f"status failed for {work_id} (exit {code})")
    if require_complete:
        reason = planning_incomplete(doc)
        if reason:
            die(f"incomplete change {work_id}: {reason}")
    return sanitize(doc)


def cmd_archive(bin_path: str, work_id: str) -> dict:
    doc, code = run_json(bin_path, ["archive", work_id, "-y"])
    if code != 0:
        die(f"openspec archive failed for {work_id} (exit {code})")
    return sanitize(doc)


def is_pilot(root: Path, work_id: str) -> bool:
    intent = root / "work" / work_id / "intent.md"
    if not intent.is_file():
        return False
    return bool(PILOT_LINE.search(intent.read_text()))


HEADING = re.compile(r"^##\s+(.*)\s*$")


def section_after(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m and m.group(1).strip().lower() == heading.lower():
            start = i + 1
            break
    if start is None:
        return ""
    body = []
    for line in lines[start:]:
        if HEADING.match(line):
            break
        body.append(line)
    return "\n".join(body)


def meaningful(text: str) -> bool:
    if not text:
        return False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("<!--") or line.startswith("-->"):
            continue
        if re.fullmatch(r"<[^>]+>", line):
            continue
        if re.fullmatch(r"[-*]\s*([.…]+|\.\.\.)?", line):
            continue
        if line.startswith("**Contract:**"):
            continue
        return True
    return False


def accept_sha(root: Path, work_id: str) -> str:
    acc = root / "work" / work_id / "acceptance.md"
    if not acc.is_file():
        return ""
    body = section_after(acc.read_text(), "Accepted commit SHA")
    m = re.search(r"\b[0-9a-f]{7,40}\b", body or "", re.I)
    return m.group(0) if m else ""


def yaml_true(path: Path, key: str) -> bool:
    if not path.is_file():
        return False
    pat = re.compile(rf"^{re.escape(key)}:\s*(true|yes|1)\s*$", re.I)
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if pat.match(line):
            return True
    return False


ARCHIVE_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")


def lookup_change(root: Path, work_id: str) -> dict:
    changes = root / "openspec" / "changes"
    active = changes / work_id
    active_ok = active.is_dir() and not active.is_symlink()
    archive_root = changes / "archive"
    archives = []
    if archive_root.is_dir():
        for p in sorted(archive_root.iterdir()):
            if not p.is_dir():
                continue
            m = ARCHIVE_NAME.match(p.name)
            if m and m.group(2) == work_id:
                archives.append(p)
    if active_ok and archives:
        # 04 Spec Change after archive: active wins; extras are not "more than one active"
        return {"state": "active", "path": str(active), "archives": [str(a) for a in archives]}
    if active_ok:
        return {"state": "active", "path": str(active), "archives": []}
    if len(archives) > 1:
        return {"state": "ambiguous", "path": "", "archives": [str(a) for a in archives]}
    if len(archives) == 1:
        return {"state": "archived", "path": str(archives[0]), "archives": [str(archives[0])]}
    return {"state": "missing", "path": "", "archives": []}


def pointer_violations(root: Path, work_id: str) -> list[str]:
    bad = []
    plan = root / "work" / work_id / "plan.md"
    if plan.is_file():
        text = plan.read_text()
        if meaningful(section_after(text, "Approach")) or meaningful(
            section_after(text, "Work breakdown")
        ):
            bad.append(f"work/{work_id}/plan.md has meaningful plan content (pointer only)")
    for rel in (f"specs/current/{work_id}.md", f"specs/proposals/{work_id}.md"):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text()
        for heading in ("Goal", "Behavior", "Acceptance criteria"):
            if meaningful(section_after(text, heading)):
                bad.append(f"{rel} has meaningful {heading} (pointer only)")
    return bad


def skip_specs_violation(root: Path, work_id: str, change_dir: Path) -> str | None:
    meta = change_dir / ".openspec.yaml"
    if not yaml_true(meta, "skip_specs"):
        return None
    proposal = change_dir / "proposal.md"
    if not proposal.is_file():
        return "skip_specs: true without a change proposal recording a reason"
    text = proposal.read_text()
    if not re.search(r"skip_specs", text, re.I):
        return "skip_specs: true without a recorded reason in the change proposal"
    if not meaningful(section_after(text, "Why")) and not meaningful(text):
        return "skip_specs: true without a recorded reason in the change proposal"
    return None


def cmd_preflight(root: Path, work_id: str) -> dict:
    if "/" in work_id or work_id in (".", "..") or not work_id:
        die(f"invalid work-id {work_id!r}", 2)
    found = lookup_change(root, work_id)
    state = found["state"]
    sha = accept_sha(root, work_id)
    if state == "missing":
        die(f"missing OpenSpec change for {work_id}")
    if state == "ambiguous":
        die(f"more than one OpenSpec archive match for {work_id}")
    if state == "archived":
        if not sha:
            die(
                f"openspec-archived change {work_id} has no Accept SHA "
                f"(direct archive detected at {found['path']})"
            )
        # Valid Accept + archive: not a missing-change failure; skip active gate.
        found["accept_sha"] = sha
        found["run_gate"] = False
        return found
    change_dir = Path(found["path"])
    for msg in pointer_violations(root, work_id):
        die(msg)
    skip_msg = skip_specs_violation(root, work_id, change_dir)
    if skip_msg:
        die(skip_msg)
    found["accept_sha"] = sha
    found["run_gate"] = True
    return found


def emit(doc: dict) -> None:
    json.dump(doc, sys.stdout, indent=2)
    sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="openspec_cli.py")
    p.add_argument("--root", default=None)
    p.add_argument("--pin", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version-assert")
    sub.add_parser("load-pin")
    sp = sub.add_parser("validate")
    sp.add_argument("work_id")
    sp = sub.add_parser("status")
    sp.add_argument("work_id")
    sp = sub.add_parser("gate")
    sp.add_argument("work_id")
    sp = sub.add_parser("archive")
    sp.add_argument("work_id")
    sp = sub.add_parser("is-pilot")
    sp.add_argument("work_id")
    sp = sub.add_parser("preflight")
    sp.add_argument("work_id")

    args = p.parse_args(argv)
    root = repo_root(args.root)
    pin_path = Path(args.pin) if args.pin else root / "_ask" / "openspec-pin.yaml"
    pin = load_pin(pin_path)

    if args.cmd == "load-pin":
        emit(pin)
        return 0
    if args.cmd == "is-pilot":
        raise SystemExit(0 if is_pilot(root, args.work_id) else 1)
    if args.cmd == "preflight":
        emit(cmd_preflight(root, args.work_id))
        return 0

    bin_path = find_bin()
    assert_version(bin_path, pin)

    if args.cmd == "version-assert":
        print(pin["revision"])
        return 0
    if args.cmd == "validate":
        emit(cmd_validate(bin_path, args.work_id))
        return 0
    if args.cmd == "status":
        emit(cmd_status(bin_path, args.work_id, require_complete=False))
        return 0
    if args.cmd == "gate":
        emit(cmd_validate(bin_path, args.work_id))
        emit(cmd_status(bin_path, args.work_id, require_complete=True))
        return 0
    if args.cmd == "archive":
        emit(cmd_archive(bin_path, args.work_id))
        return 0
    die(f"unknown command {args.cmd}", 2)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
