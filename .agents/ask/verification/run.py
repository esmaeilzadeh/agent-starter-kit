# CheckPlan / VerifyResult runner. Language CLIs live in presets, not here.
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from verification.plan import expand_plan, load_plan  # noqa: E402


def main() -> int:
    root = Path(os.environ.get("ASK_ROOT") or HERE.parents[3]).resolve()
    os.chdir(root)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=root,
    ).stdout.strip() or "unknown"
    out_dir = Path(os.environ.get("VERIFY_OUT_DIR") or ".")
    out_json = Path(os.environ.get("VERIFY_JSON") or out_dir / "verification-result.json")

    try:
        plan = load_plan(root)
        checks = expand_plan(root, plan)
    except FileNotFoundError as e:
        print(f"verify: {e}", file=sys.stderr)
        return 1

    mandatory = [c for c in checks if c.get("tier", "mandatory") == "mandatory"]
    if not checks or not mandatory:
        print("verify: empty CheckPlan or zero mandatory checks", file=sys.stderr)
        return 1

    results = []
    overall = 0
    for c in checks:
        cmd = c["command"]
        print(f"verify: running: {cmd}")
        proc = subprocess.run(["bash", "-lc", cmd], cwd=root)
        code = proc.returncode
        status = "pass" if code == 0 else "fail"
        if code != 0:
            overall = 1
        results.append(
            {
                "id": c.get("id", cmd),
                "tier": c.get("tier", "mandatory"),
                "command": cmd,
                "status": status,
                "exit_code": code,
                "evidence": "",
            }
        )

    doc = {
        "schema": "ask-verify-result/v1",
        "commit_sha": sha,
        "result": "pass" if overall == 0 else "fail",
        "checks": results,
    }
    print(json.dumps(doc, indent=2))
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"verify: commit_sha={sha}")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
