"""Manage the Git ignore rules for a locally installed client runtime."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


BEGIN = b"# BEGIN AskIt local installation"
END = b"# END AskIt local installation"
RUNTIME = (
    "/ask", "/_ask/", "/.agents/ask/", "/.agents/skills/kit-*/",
    "/.cursor/skills/kit-*/", "/.cursor/agents/kit-*.md",
    "/.claude/agents/kit-*.md", "/.codex/agents/kit-*.toml", "/.opencode/agents/kit-*.md",
    "/.ask.env",
    "/ai-agent-engineering-guide.md", "/ai-agent-starter-kit-spec.md",
    "/work/**/*.log", "/work/*/traceability/runs/*/*.json",
    "!/work/*/traceability/runs/*/results.json",
    "/work/*/traceability/static-runs/*/*.json", "/work/*/traceability/executions.lock",
    "/work/*/inner-loop/state.lock",
)
STAGES = (
    "00-explore", "01-grill", "02-spec", "03-spec-challenge", "04-spec-change",
    "05-plan", "06-implement", "07-review", "08-refactor", "09-verify", "10-accept",
)
COMMANDS = tuple(f"/.cursor/commands/{name}.md" for name in (*STAGES, "off-path"))
SHARED = (
    "/.ask.env.example", "/.ask/README.md", "/.cursor/hooks.json",
    "/.cursor/hooks/README.md", "/.cursor/hooks/access-preflight.sh",
    "/.cursor/hooks/git-guardrails.sh", "/.cursor/rules/commit-step-discipline.mdc",
    "/.cursor/rules/humanizer-docs-specs.mdc", "/.cursor/rules/starter-kit-bootstrap.mdc",
    "/.cursor/rules/workflow-guidance.mdc", "/.cursor/rules/workstream-scope.mdc",
    "/.cursor/rules/writing-for-agents-machine-docs.mdc",
)
LEGACY = {
    b"/_ask/", b".ask.env", b".ask/tracker-context.md", b"/.ask/tracker-context.md",
    b"/.codex/hooks.json",
    b".agents/skills/", b"/.agents/skills/", b".agents/skills", b"/.agents/skills",
    b".agents/skills/*", b"!.agents/skills/kit-*/",
    b"# Installed AskIt kit", b"# Setup wizard secrets",
    b"# Prepared skills; ASK kit-* projections are committed",
    b"# Prepared Community Skills (regenerate via _ask/skills/prepare-skills.sh)",
    b"# Setup wizard secrets and current-issue context",
    b"# Exact retained caches; check-clean validates ignored runtime bytes too.",
    b"work/*/inner-loop/state.json",
    b"work/*/inner-loop/results/*.json",
    b"work/*/inner-loop/evidence/verify-*/integration.json",
    b"work/*/traceability/executions.json",
    b"work/*/traceability/completion.json",
    b"work/*/traceability/static-*.json",
    b"work/*/traceability/model-state/",
    b"work/*/traceability/runs/*/results.json",
}
# Accept previous managed rules so upgrades can replace them safely.
RULES = {rule.encode() for rule in (*RUNTIME, *COMMANDS, *SHARED)} | LEGACY


def consumer_rules(data: bytes) -> bytes:
    """Remove only the kit's previous rules and its bounded managed block."""
    lines = data.splitlines(keepends=True)
    markers = [line.rstrip(b"\r\n") for line in lines]
    if BEGIN in markers or END in markers:
        if markers.count(BEGIN) != 1 or markers.count(END) != 1:
            raise ValueError("invalid AskIt managed block in .gitignore")
        start, end = markers.index(BEGIN), markers.index(END)
        if start >= end or any(line not in RULES for line in markers[start + 1:end]):
            raise ValueError("unexpected content in AskIt managed block in .gitignore")
        del lines[start:end + 1]
    return b"".join(line for line in lines if line.strip() not in LEGACY).rstrip(b"\r\n")


def stock_file(target: Path, source: Path, rule: str, owned: dict) -> bool:
    name = rule[1:]
    local, stock = target / name, source / name
    if not local.is_file():
        return False
    data = local.read_bytes()
    return ((stock.is_file() and data == stock.read_bytes())
            or owned.get(name, {}).get("sha256") == hashlib.sha256(data).hexdigest())


def installed_ownership(target: Path) -> dict:
    manifest = Path(subprocess.check_output(
        ["git", "rev-parse", "--path-format=absolute", "--git-path", "askit-transactions/owned-files.json"],
        cwd=target, text=True,
    ).strip())
    try:
        info = manifest.lstat()
    except FileNotFoundError:
        return {}
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError(f"unsafe installed-file ownership manifest: {manifest}")
    document = json.loads(manifest.read_bytes())
    if (not isinstance(document, dict) or document.get("schema") != "askit-installed-files/v1"
            or not isinstance(document.get("files"), dict)):
        raise ValueError(f"invalid installed-file ownership manifest: {manifest}")
    return document["files"]


def update(target: Path, source: Path) -> None:
    owned = installed_ownership(target)
    rules = (*RUNTIME, *COMMANDS, *(rule for rule in SHARED if stock_file(target, source, rule, owned)))
    path = target / ".gitignore"
    client = consumer_rules(path.read_bytes() if path.exists() else b"")
    block = b"\n".join((BEGIN, *(rule.encode() for rule in rules), END, b""))
    path.write_bytes((client + b"\n\n" if client else b"") + block)
    tracked = subprocess.check_output(
        ["git", "ls-files", "--cached", "--ignored", "-z", *(f"--exclude={rule}" for rule in rules)],
        cwd=target,
    )
    if tracked:
        count = len(tracked.split(b"\0")) - 1
        print(f"askit: {count} kit paths are still tracked. "
              "Review the AskIt ignore block and remove those paths from the index with git rm --cached.",
              file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    try:
        update(args.target, args.source)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"askit: cannot update client ignore rules: {exc}")
