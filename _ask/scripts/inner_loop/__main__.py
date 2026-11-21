#!/usr/bin/env python3
"""CLI: ./ask inner-loop validate|status|cas-init|cas-apply|spawn-writer"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from inner_loop.allowlist import classify_paths, outside_paths, staged_paths  # noqa: E402
from inner_loop.evidence import checkpoint_run, preflight_run, record_review  # noqa: E402
from inner_loop.driver import (  # noqa: E402
    NotIntegrable,
    cancel,
    git_sha,
    resume_from_state,
    run_until,
)
from inner_loop.graph import load_graph, validate_graph, _task_map  # noqa: E402
from inner_loop.integrate import Escalate, Forbidden, integrate, resume  # noqa: E402
from inner_loop.retry import next_action  # noqa: E402
from inner_loop.state import (  # noqa: E402
    CasConflict,
    ProtocolViolation,
    SecondWriter,
    cas_apply,
    cas_init,
    load_state,
    spawn_writer,
)
from inner_loop.recovery import (  # noqa: E402
    RecoveryRequired,
    audit_legacy_workstream,
    inspect as inspect_recovery,
    legacy_adoption_proposal,
    validate_legacy_adoption_proposal,
)
from inner_loop.checkpoint import CheckpointError, export_bundle, import_bundle  # noqa: E402
from inner_loop.attempts import interrupt_task, reopen_task  # noqa: E402
from engineering_model.actions import Refused
from engineering_model.workflow import adopted, branch_work_id, guarded_workflow, workflow_admission


def repo_root(ns_root: str | None) -> Path:
    if ns_root:
        return Path(ns_root).resolve()
    return HERE.parents[2]


def cmd_validate(root: Path, work_id: str) -> int:
    graph = load_graph(root, work_id)
    result = validate_graph(graph)
    print(result)
    return 0 if result == "ok" else 1


def cmd_status(root: Path, work_id: str) -> int:
    try:
        doc = load_state(root, work_id)
    except FileNotFoundError:
        doc = None
    except json.JSONDecodeError:
        doc = None
    graph = load_graph(root, work_id)
    report = inspect_recovery(root, work_id, graph, doc)
    if report is not None:
        print(json.dumps(report, indent=2))
        return 2
    if doc is None:
        print("no state")
        return 1
    print(f"revision={doc.get('revision')} sha={doc.get('coordinator_sha')}")
    for tid, t in sorted((doc.get("tasks") or {}).items()):
        print(f"{tid}\t{t.get('status')}")
    return 0


def cmd_reconcile(root: Path, work_id: str) -> int:
    graph = load_graph(root, work_id)
    try:
        doc = load_state(root, work_id)
    except FileNotFoundError:
        doc = None
    except json.JSONDecodeError:
        doc = None
    report = inspect_recovery(root, work_id, graph, doc)
    if report is None:
        print(json.dumps({"status": "ready", "work_id": work_id}, indent=2))
        return 0
    print(json.dumps(report, indent=2))
    return 2


@guarded_workflow
def cmd_cas_init(root: Path, work_id: str) -> int:
    graph = load_graph(root, work_id)
    ids = list(_task_map(graph))
    doc = cas_init(root, work_id, ids, coordinator_sha=git_sha(root))
    print(f"revision={doc['revision']}")
    return 0


@guarded_workflow
def cmd_cas_apply(root: Path, work_id: str, observed: int) -> int:
    def mut(doc: dict) -> None:
        return None

    doc = cas_apply(root, work_id, observed, mut)
    print(f"revision={doc['revision']}")
    return 0


def cmd_spawn(root: Path, work_id: str, task_id: str) -> int:
    with workflow_admission(root, work_id, delivery_task_id=task_id):
        doc = spawn_writer(root, work_id, task_id)
    print(f"running={task_id} revision={doc['revision']}")
    return 0


@guarded_workflow
def cmd_interrupt(root: Path, work_id: str, task_id: str, reason: str) -> dict:
    return interrupt_task(root, work_id, task_id, reason)


@guarded_workflow
def cmd_reopen(root: Path, work_id: str, task_id: str, reason: str) -> dict:
    return reopen_task(root, work_id, task_id, reason)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ask inner-loop", allow_abbrev=False)
    p.add_argument("--root", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate TaskGraph")
    v.add_argument("work_id")

    s = sub.add_parser("status", help="print coordinator state")
    s.add_argument("work_id")

    rc = sub.add_parser("reconcile", help="read-only recovery preflight")
    rc.add_argument("work_id")

    ci = sub.add_parser("cas-init", help="initialize state.json without overwriting existing state")
    ci.add_argument("work_id")

    ca = sub.add_parser("cas-apply", help="CAS increment")
    ca.add_argument("work_id")
    ca.add_argument("--observed", type=int, required=True)

    sp = sub.add_parser("spawn-writer", help="mark one task running")
    sp.add_argument("work_id")
    sp.add_argument("task_id")

    rv = sub.add_parser("record-review", help="coordinator records candidate-bound delegated review")
    rv.add_argument("work_id")
    rv.add_argument("task_id")
    rv.add_argument("--reviewer", required=True)
    rv.add_argument("--policy", default="_ask/policies/delegation.md")
    rv.add_argument("--evidence", required=True)
    rv.add_argument("--verdict", choices=["APPROVED", "REJECTED"], default="APPROVED")
    rv.add_argument("--boundary", choices=["ok", "extras", "glob_too_narrow"], default="ok")

    cp = sub.add_parser("check-paths", help="refuse paths outside globs")
    cp.add_argument("--glob", action="append", dest="globs", required=True)
    cp.add_argument("paths", nargs="*")

    cl = sub.add_parser("classify-paths", help="extras vs glob_too_narrow")
    cl.add_argument("--glob", action="append", dest="globs", required=True)
    cl.add_argument("--required", default="")
    cl.add_argument("paths", nargs="*")

    ix = sub.add_parser("check-index", help="refuse staged paths outside globs")
    ix.add_argument("--glob", action="append", dest="globs", required=True)

    na = sub.add_parser("next-action", help="bounded retry dispatch")
    na.add_argument("--review-round", type=int, required=True)
    na.add_argument("--debug-round", type=int, required=True)
    na.add_argument("--verdict", required=True)
    na.add_argument("--boundary", default="ok")

    ig = sub.add_parser("integrate", help="fast-forward only onto coordinator")
    ig.add_argument("--task-ref", required=True)
    ig.add_argument("--method", default="ff-only")
    ig.add_argument("--task-id", help="qualified selected inner-loop Task identity")

    rs = sub.add_parser("resume-repair", help="abort dirty/in-progress to coordinator_sha")
    rs.add_argument("--coordinator-sha", required=True)

    rn = sub.add_parser("run", help="start next ready writer or integrate_ready")
    rn.add_argument("work_id")

    ce = sub.add_parser("checkpoint-export", help="export retained checkpoint and its object closure")
    ce.add_argument("work_id")
    ce.add_argument("--out", required=True)

    ci_bundle = sub.add_parser("checkpoint-import", help="import a retained checkpoint bundle")
    ci_bundle.add_argument("work_id")
    ci_bundle.add_argument("bundle")

    rm = sub.add_parser("resume", help="abort to state.json coordinator_sha, then run")
    rm.add_argument("work_id")

    cn = sub.add_parser("cancel", help="cancel task_id or all")
    cn.add_argument("work_id")
    cn.add_argument("target")

    it = sub.add_parser("interrupt", help="preserve and stop the current task attempt")
    it.add_argument("work_id")
    it.add_argument("task_id")
    it.add_argument("--reason", required=True)

    ro = sub.add_parser("reopen", help="start a new attempt after explicit interruption")
    ro.add_argument("work_id")
    ro.add_argument("task_id")
    ro.add_argument("--reason", required=True)

    cr = sub.add_parser("checkpoint-run", help="validate and retain one traceability run")
    cr.add_argument("work_id")
    cr.add_argument("task_id")
    cr.add_argument("--run-id", required=True)

    pf = sub.add_parser("preflight-run", help="read-only validation of a retained run for an interrupted task")
    pf.add_argument("work_id")
    pf.add_argument("task_id")
    pf.add_argument("--run-id", required=True)

    la = sub.add_parser("legacy-audit", help="read-only audit of a pre-checkpoint workstream")
    la.add_argument("work_id")
    la.add_argument("--ref", required=True, help="exact product branch or commit to audit")

    lp = sub.add_parser("legacy-proposal", help="prepare a non-mutating legacy adoption proposal")
    lp.add_argument("--audit", required=True, help="JSON produced by legacy-audit")

    lv = sub.add_parser("legacy-validate-adoption", help="validate reviewed proposal preconditions without adopting")
    lv.add_argument("--audit", required=True)
    lv.add_argument("--proposal", required=True)

    args = p.parse_args(argv)
    root = repo_root(args.root)
    try:
        if args.cmd == "validate":
            return cmd_validate(root, args.work_id)
        if args.cmd == "status":
            return cmd_status(root, args.work_id)
        if args.cmd == "reconcile":
            return cmd_reconcile(root, args.work_id)
        if args.cmd == "cas-init":
            return cmd_cas_init(root, args.work_id)
        if args.cmd == "cas-apply":
            return cmd_cas_apply(root, args.work_id, args.observed)
        if args.cmd == "spawn-writer":
            return cmd_spawn(root, args.work_id, args.task_id)
        if args.cmd == "record-review":
            with workflow_admission(root,args.work_id,delivery_task_id=args.task_id):
                review = record_review(root, args.work_id, args.task_id, args.reviewer, args.policy,
                                       args.evidence, args.verdict, args.boundary,
                                       delivery_task_id=args.task_id)
            print(f"review={review['verdict']} candidate={review['candidate_sha']}")
            return 0
        if args.cmd == "check-paths":
            bad = outside_paths(args.paths, args.globs)
            if bad:
                print("reject: " + " ".join(bad), file=sys.stderr)
                return 1
            print("ok")
            return 0
        if args.cmd == "classify-paths":
            required = [x for x in args.required.split(",") if x]
            print(classify_paths(args.paths, args.globs, required))
            return 0
        if args.cmd == "check-index":
            names = staged_paths(root)
            bad = outside_paths(names, args.globs)
            if bad:
                print("reject: " + " ".join(bad), file=sys.stderr)
                return 1
            print("ok")
            return 0
        if args.cmd == "next-action":
            print(
                next_action(
                    args.review_round, args.debug_round, args.verdict, args.boundary
                )
            )
            return 0
        if args.cmd == "integrate":
            sha = integrate(root, args.task_ref, args.method, delivery_task_id=args.task_id)
            print(sha)
            return 0
        if args.cmd == "resume-repair":
            print(resume(root, args.coordinator_sha))
            return 0
        if args.cmd == "run":
            print(run_until(root, args.work_id))
            return 0
        if args.cmd == "checkpoint-export":
            export_bundle(root, args.work_id, Path(args.out))
            return 0
        if args.cmd == "checkpoint-import":
            print(import_bundle(root, args.work_id, Path(args.bundle)))
            return 0
        if args.cmd == "resume":
            print(resume_from_state(root, args.work_id))
            return 0
        if args.cmd == "cancel":
            print(cancel(root, args.work_id, args.target))
            return 0
        if args.cmd == "interrupt":
            doc = cmd_interrupt(root, args.work_id, args.task_id, args.reason)
            print(f"interrupted={args.task_id} revision={doc['revision']}")
            return 0
        if args.cmd == "reopen":
            doc = cmd_reopen(root, args.work_id, args.task_id, args.reason)
            print(f"running={args.task_id} revision={doc['revision']}")
            return 0
        if args.cmd == "checkpoint-run":
            with workflow_admission(root, args.work_id, delivery_task_id=args.task_id):
                result = checkpoint_run(root, args.work_id, args.task_id, args.run_id)
            print(json.dumps(result, indent=2))
            return 0
        if args.cmd == "preflight-run":
            result = preflight_run(root, args.work_id, args.task_id, args.run_id)
            print(json.dumps(result, indent=2))
            return 0
        if args.cmd == "legacy-audit":
            report = audit_legacy_workstream(root, args.work_id, args.ref)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0
        if args.cmd == "legacy-proposal":
            audit = json.loads(Path(args.audit).read_text(encoding="utf-8"))
            print(json.dumps(legacy_adoption_proposal(audit), indent=2, sort_keys=True))
            return 0
        if args.cmd == "legacy-validate-adoption":
            audit = json.loads(Path(args.audit).read_text(encoding="utf-8"))
            proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
            result = validate_legacy_adoption_proposal(root, audit, proposal)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["status"] == "preconditions_validated" else 2
        print(f"{args.cmd} not implemented yet", file=sys.stderr)
        return 2
    except ProtocolViolation as e:
        print(e, file=sys.stderr)
        return 2
    except RecoveryRequired as e:
        print(json.dumps(e.report, indent=2), file=sys.stderr)
        return 2
    except CheckpointError as e:
        print(json.dumps({"status": "recovery_required", "error": str(e)}, indent=2), file=sys.stderr)
        return 2
    except CasConflict as e:
        print(e, file=sys.stderr)
        return 2
    except Forbidden as e:
        print(e, file=sys.stderr)
        return 2
    except Escalate as e:
        print(e, file=sys.stderr)
        return 2
    except SecondWriter as e:
        print(e, file=sys.stderr)
        return 2
    except NotIntegrable as e:
        print(e, file=sys.stderr)
        return 2
    except Refused as e:
        print(e.diagnostic['code']+': '+str(e),file=sys.stderr)
        return 1
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
