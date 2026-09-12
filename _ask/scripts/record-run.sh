#!/usr/bin/env bash
# Record an experiment run; refuse dirty tree, missing SHA, or SHA ≠ HEAD.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

RUN_ID=""
SHA=""
METRIC=""
NOTES=""
OUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id) RUN_ID="$2"; shift 2 ;;
    --commit-sha) SHA="$2"; shift 2 ;;
    --metric) METRIC="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    *) echo "record-run: unknown arg $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$RUN_ID" ]]; then
  echo "record-run: --run-id required" >&2
  exit 2
fi
if [[ -z "$SHA" ]]; then
  echo "record-run: refusing — --commit-sha is required (missing commit SHA)" >&2
  exit 1
fi
if [[ -z "$METRIC" ]]; then
  echo "record-run: --metric required" >&2
  exit 2
fi

"$ROOT/_ask/scripts/check-clean-worktree.sh"

HEAD_FULL="$(git rev-parse HEAD)"
HEAD_SHORT="$(git rev-parse --short HEAD)"
if [[ "$SHA" != "$HEAD_FULL" && "$SHA" != "$HEAD_SHORT" ]]; then
  echo "record-run: refusing — --commit-sha must be HEAD ($HEAD_SHORT)" >&2
  exit 1
fi
SHA="$HEAD_FULL"

OUT="${OUT:-results/${RUN_ID}}"
if [[ ! -f "${OUT}/config.yaml" ]]; then
  echo "record-run: refusing — missing ${OUT}/config.yaml" >&2
  exit 1
fi

mkdir -p "$OUT"
export ASK_RUN_ID="$RUN_ID" ASK_RUN_SHA="$SHA" ASK_RUN_METRIC="$METRIC" ASK_RUN_NOTES="$NOTES" ASK_RUN_OUT="$OUT"
python3 - <<'PY'
import json, os, platform, socket, subprocess
from datetime import datetime, timezone
from pathlib import Path

def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None

out = Path(os.environ["ASK_RUN_OUT"])
sha = os.environ["ASK_RUN_SHA"]
branch = git("rev-parse", "--abbrev-ref", "HEAD")
describe = git("describe", "--always", "--dirty", "--tags")
meta = {
    "schema": "eval-run-meta/v1",
    "started_at": datetime.now(timezone.utc).isoformat(),
    "finished_at": datetime.now(timezone.utc).isoformat(),
    "git_sha": sha,
    "git_branch": branch,
    "git_dirty": False,
    "git_describe": describe,
    "hostname": socket.gethostname(),
    "platform": platform.platform(),
    "run_id": os.environ["ASK_RUN_ID"],
    "metric": os.environ["ASK_RUN_METRIC"],
    "notes": os.environ.get("ASK_RUN_NOTES") or "",
    "out": str(out),
}
(out / "run_manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
summary = {"metric": os.environ["ASK_RUN_METRIC"], "run_meta": meta}
(out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

reg = Path("results/RUN_REGISTRY.md")
reg.parent.mkdir(parents=True, exist_ok=True)
if not reg.exists():
    reg.write_text("# Eval run registry\n\nCite **path + git_sha + metric**.\n\n| run-id | metric | git_sha | path |\n| --- | --- | --- | --- |\n")
row = f"| {os.environ['ASK_RUN_ID']} | {os.environ['ASK_RUN_METRIC']} | `{sha}` | `{out}` |\n"
text = reg.read_text()
if f"| {os.environ['ASK_RUN_ID']} |" in text:
    lines = []
    for line in text.splitlines(True):
        if line.startswith(f"| {os.environ['ASK_RUN_ID']} |"):
            lines.append(row)
        else:
            lines.append(line)
    reg.write_text("".join(lines))
else:
    if not text.endswith("\n"):
        text += "\n"
    reg.write_text(text + row)
print(f"record-run: wrote {os.environ['ASK_RUN_ID']} @ {sha} -> {out}")
PY
