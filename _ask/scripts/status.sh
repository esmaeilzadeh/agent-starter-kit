#!/usr/bin/env bash
# List kit workstreams from agent/* refs (live) and default-branch work/ (archive).
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "status: not a git repository" >&2
  exit 2
fi
cd "$(git rev-parse --show-toplevel)"

WORK_ID=""
JSON=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --work-id) WORK_ID="$2"; shift 2 ;;
    --json) JSON=1; shift ;;
    -h|--help)
      cat <<'EOF'
Usage: ./ask status [--work-id <id>] [--json]

Live workstreams are inferred from local refs/heads/agent/* (no checkout).
Archived workstreams are work/* on the default branch with no matching agent/* branch.
EOF
      exit 0
      ;;
    *) echo "status: unknown arg $1" >&2; exit 2 ;;
  esac
done

export ASK_STATUS_WORK_ID="$WORK_ID"
export ASK_STATUS_JSON="$JSON"

python3 - <<'PY'
import json, os, re, subprocess, sys

def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} failed")
    return r.stdout

def default_branch():
    head = git("symbolic-ref", "refs/remotes/origin/HEAD", check=False).strip()
    if head.startswith("refs/remotes/origin/"):
        name = head.split("/", 3)[-1]
        if subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"]).returncode == 0:
            return name
    for name in ("main", "master"):
        if subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"]).returncode == 0:
            return name
    return git("rev-parse", "--abbrev-ref", "HEAD").strip()

def blob(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout

def section_after(text, heading):
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^##\s+{re.escape(heading)}\s*$", line, re.I):
            start = i + 1
            break
    if start is None:
        return ""
    body = []
    for line in lines[start:]:
        if re.match(r"^##\s+", line):
            break
        body.append(line)
    return "\n".join(body)

def meaningful(text):
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
        # kit explore-map template boilerplate
        if line.startswith("**Contract:**"):
            continue
        return True
    return False

def sha_in(text):
    return bool(re.search(r"\b[0-9a-f]{7,40}\b", text or "", re.I))

def artifacts(ref, work_id):
    base = f"work/{work_id}"
    explore = blob(ref, f"{base}/explore-map.md")
    intent = blob(ref, f"{base}/intent.md")
    plan = blob(ref, f"{base}/plan.md")
    review = blob(ref, f"{base}/review.md")
    result = blob(ref, f"{base}/result.json")
    acceptance = blob(ref, f"{base}/acceptance.md")
    out = {
        "work_dir": blob(ref, base) is not None or any(
            x is not None for x in (explore, intent, plan, review, result, acceptance)
        ),
        "explore_handoff": meaningful(section_after(explore or "", "Handoff to Intent")),
        "intent": meaningful(section_after(intent or "", "What")),
        "plan": meaningful(section_after(plan or "", "Approach"))
            or meaningful(section_after(plan or "", "Work breakdown")),
        "review": meaningful(section_after(review or "", "Review verdict"))
            or meaningful(section_after(review or "", "Findings")),
        "result": False,
        "result_sha": "",
        "accepted": False,
        "accepted_sha": "",
    }
    if result:
        try:
            doc = json.loads(result)
            sha = str(doc.get("commit_sha") or "")
            out["result"] = bool(sha)
            out["result_sha"] = sha
        except json.JSONDecodeError:
            out["result"] = False
    if acceptance:
        acc = section_after(acceptance, "Accepted commit SHA")
        out["accepted"] = sha_in(acc)
        m = re.search(r"\b[0-9a-f]{7,40}\b", acc or "", re.I)
        out["accepted_sha"] = m.group(0) if m else ""
    return out

def stage(art):
    if not art["work_dir"]:
        return "missing-work"
    if art["accepted"]:
        return "accepted"
    if art["result"]:
        return "recorded"
    if art["review"]:
        return "reviewed"
    if art["plan"]:
        return "planned"
    if art["intent"]:
        return "intent"
    if art["explore_handoff"]:
        return "explored"
    return "seeded"

def tip(ref):
    return git("rev-parse", "--short", ref).strip()

def is_ancestor(commit, onto):
    r = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, onto],
        capture_output=True, text=True,
    )
    return r.returncode == 0

want = os.environ.get("ASK_STATUS_WORK_ID") or ""
as_json = os.environ.get("ASK_STATUS_JSON") == "1"

agent_refs = []
for line in git("for-each-ref", "--format=%(refname:short)", "refs/heads/agent").splitlines():
    name = line.strip()
    if not name.startswith("agent/"):
        continue
    wid = name[len("agent/") :]
    if not wid:
        continue
    agent_refs.append((wid, name))

default = default_branch()
live_refs = [(wid, name) for wid, name in agent_refs if not is_ancestor(name, default)]
live_ids = {w for w, _ in live_refs}
archive_ids = []
ls = subprocess.run(["git", "ls-tree", "-d", "--name-only", f"{default}:work"], capture_output=True, text=True)
if ls.returncode == 0:
    for name in ls.stdout.splitlines():
        wid = name.strip()
        if wid and wid not in live_ids:
            archive_ids.append(wid)

rows = []
for wid, ref in live_refs:
    if want and wid != want:
        continue
    art = artifacts(ref, wid)
    rows.append({
        "work_id": wid,
        "life": "live",
        "branch": ref,
        "tip": tip(ref),
        "stage": stage(art),
        "artifacts": art,
    })
for wid in archive_ids:
    if want and wid != want:
        continue
    art = artifacts(default, wid)
    rows.append({
        "work_id": wid,
        "life": "archived",
        "branch": default,
        "tip": tip(default),
        "stage": stage(art),
        "artifacts": art,
    })

if as_json:
    print(json.dumps({"default_branch": default, "workstreams": rows}, indent=2))
    sys.exit(0)

if not rows:
    if want:
        print(f"status: no workstream '{want}' (no agent/{want} and no archived work/{want} on {default})")
    else:
        print(f"status: no live agent/* branches; no archived work/* on {default}")
    sys.exit(0)

print(f"status: default={default}")
print(f"{'LIFE':<10} {'WORK-ID':<28} {'STAGE':<14} {'BRANCH':<28} {'TIP':<10} ARTIFACTS")
for row in rows:
    art = row["artifacts"]
    flags = []
    if art["explore_handoff"]:
        flags.append("handoff")
    if art["intent"]:
        flags.append("intent")
    if art["plan"]:
        flags.append("plan")
    if art["review"]:
        flags.append("review")
    if art["result"]:
        flags.append("result")
    if art["accepted"]:
        flags.append("accept")
    mark = ",".join(flags) if flags else "-"
    print(f"{row['life']:<10} {row['work_id']:<28} {row['stage']:<14} {row['branch']:<28} {row['tip']:<10} {mark}")
PY
