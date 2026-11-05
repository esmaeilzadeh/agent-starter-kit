#!/usr/bin/env bash
# Record an experiment run; refuse dirty tree, missing SHA, or SHA != HEAD.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
RUN_ID="" SHA="" METRIC="" NOTES="" OUT=""
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
[[ -n "$RUN_ID" ]] || { echo 'record-run: --run-id required' >&2; exit 2; }
[[ -n "$SHA" ]] || { echo 'record-run: refusing — --commit-sha is required (missing commit SHA)' >&2; exit 1; }
[[ -n "$METRIC" ]] || { echo 'record-run: --metric required' >&2; exit 2; }
"$ROOT/_ask/scripts/check-clean-worktree.sh"
HEAD_FULL="$(git rev-parse HEAD)"
HEAD_SHORT="$(git rev-parse --short HEAD)"
if [[ "$SHA" != "$HEAD_FULL" && "$SHA" != "$HEAD_SHORT" ]]; then
  echo "record-run: refusing — --commit-sha must be HEAD ($HEAD_SHORT)" >&2
  exit 1
fi
SHA="$HEAD_FULL"
OUT="${OUT:-results/${RUN_ID}}"
[[ -f "${OUT}/config.yaml" ]] || { echo "record-run: refusing — missing ${OUT}/config.yaml" >&2; exit 1; }
[[ ! -e "${OUT}/run_manifest.json" ]] || { echo "record-run: refusing — run output already exists" >&2; exit 1; }
export ASK_RUN_ROOT="$ROOT" ASK_RUN_ID="$RUN_ID" ASK_RUN_SHA="$SHA" ASK_RUN_METRIC="$METRIC" ASK_RUN_NOTES="$NOTES" ASK_RUN_OUT="$OUT"
python3 - <<'PY'
import fcntl
import hashlib
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import tempfile
from datetime import datetime, timezone

root = Path(os.environ["ASK_RUN_ROOT"]).resolve()
run_id = os.environ["ASK_RUN_ID"]
source_sha = os.environ["ASK_RUN_SHA"]
metric = os.environ["ASK_RUN_METRIC"]
notes = os.environ.get("ASK_RUN_NOTES") or ""
out = Path(os.environ["ASK_RUN_OUT"])

registry_path = root / "results/RUN_REGISTRY.md"
if registry_path.exists():
    registry_text = registry_path.read_text(encoding="utf-8")
    if any(line.startswith(f"| {run_id} |") for line in registry_text.splitlines()):
        raise SystemExit("record-run: run ID already exists in the registry")

def git(*args, input_bytes=None, env=None):
    return subprocess.run(["git", *args], cwd=root, input=input_bytes, env=env,
                          check=True, capture_output=True).stdout

sys_path = str(root / ".agents/ask")
import sys
sys.path.insert(0, sys_path)
from workflow_refs.store import (CatalogError, _lock, _publish_catalog, _recover_pending,
                                 _repo_info, _trusted_catalog, initialize_catalog,
                                 register_revision)

catalog_path = root / "results/references/integrity.json"
initialize_catalog(catalog_path, "repository-runs")
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
numbers = []
for entry in catalog["entries"]:
    ref = entry.get("reference", "")
    prefix = "repository-runs/run/"
    if ref.startswith(prefix) and "@" in ref:
        try:
            numbers.append(int(ref[len(prefix):].split("@", 1)[0]))
        except ValueError:
            raise SystemExit("record-run: trusted run catalog contains malformed numeric identity")
number = max(numbers, default=0) + 1
reference = f"repository-runs/run/{number}@1"
record = {"items": [{"id": f"run-{number}", "run_id": run_id, "metric": metric,
                     "notes": notes, "inputs": []}]}
payload = (json.dumps(record, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()
source_path = f"results/references/records/run-{number}.json"
blob = git("hash-object", "-w", "--stdin", input_bytes=payload).decode().strip()
common_text = git("rev-parse", "--git-common-dir").decode().strip()
common = Path(common_text)
if not common.is_absolute(): common = (root / common).resolve()
index = common / "ask-locks" / f"record-run-index-{os.getpid()}"
index.parent.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env["GIT_INDEX_FILE"] = str(index)
try:
    git("read-tree", source_sha, env=env)
    git("update-index", "--add", "--cacheinfo", f"100644,{blob},{source_path}", env=env)
    tree = git("write-tree", env=env).decode().strip()
    snapshot_commit = git("commit-tree", tree, "-p", source_sha,
                          input_bytes=b"Record immutable experiment run source\n").decode().strip()
finally:
    index.unlink(missing_ok=True)
entry = register_revision(catalog_path, "repository-runs", f"repository-runs/run/{number}",
                          {"commit": snapshot_commit, "path": source_path}, f"run-{number}",
                          "structured-item/1", payload, revision=1)

# Keep the original source identity once in the trusted integrity catalog.
stream = _lock(catalog_path)
try:
    _root, common, relative = _repo_info(catalog_path)
    _recover_pending(catalog_path, "repository-runs", root, relative)
    current, old_ref = _trusted_catalog(catalog_path, "repository-runs", root, relative)
    bindings = dict(current.get("source_bindings", {}))
    if entry["reference"] in bindings:
        raise CatalogError("conflict", "run source binding already exists")
    bindings[entry["reference"]] = {"commit": source_sha, "path": source_path,
                                    "config_path": (out / "config.yaml").as_posix(),
                                    "config_sha256": hashlib.sha256((root / out / "config.yaml").read_bytes()).hexdigest(),
                                    "branch": git("rev-parse", "--abbrev-ref", "HEAD").decode().strip(),
                                    "describe": git("describe", "--always", "--dirty", "--tags").decode().strip()}
    current["source_bindings"] = bindings
    current["generation"] += 1
    _publish_catalog(catalog_path, "repository-runs", root, common, relative, current, old_ref)
finally:
    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    stream.close()

now = datetime.now(timezone.utc).isoformat()
manifest = {"schema": "eval-run-meta/v2", "started_at": now, "finished_at": now,
            "run_reference": entry["reference"], "run_id": run_id, "metric": metric,
            "notes": notes, "out": str(out), "hostname": socket.gethostname(),
            "platform": platform.platform()}
summary = {"schema": "eval-run-summary/v2", "metric": metric,
           "run_reference": entry["reference"], "run_meta": manifest}
out.mkdir(parents=True, exist_ok=True)
(out / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
(out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
registry = registry_path
registry.parent.mkdir(parents=True, exist_ok=True)
text = registry.read_text(encoding="utf-8") if registry.exists() else "# Eval run registry\n"
section = "## Numeric run references"
table = "| run-id | reference | metric | path |\n| --- | --- | --- | --- |\n"
if section not in text:
    text += ("\n" if not text.endswith("\n") else "") + f"\n{section}\n\n{table}"
if f"| {run_id} | {entry['reference']} |" in text:
    raise SystemExit("record-run: numeric run reference already appears in registry")
text += f"| {run_id} | `{entry['reference']}` | {metric} | `{out}` |\n"
registry.write_text(text, encoding="utf-8")
print(f"record-run: wrote {entry['reference']} -> {out}")
PY
