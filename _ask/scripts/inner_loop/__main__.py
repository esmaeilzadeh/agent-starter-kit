#!/usr/bin/env python3
"""CLI: ./ask inner-loop validate|status|cas-init|cas-apply|spawn-writer"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from inner_loop.graph import load_graph, validate_graph, _task_map  # noqa: E402
from inner_loop.state import (  # noqa: E402
    CasConflict,
    ProtocolViolation,
    SecondWriter,
    cas_apply,
    cas_init,
    load_state,
    spawn_writer,
)


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
        print("no state")
        return 1
    print(f"revision={doc.get('revision')} sha={doc.get('coordinator_sha')}")
    for tid, t in sorted((doc.get("tasks") or {}).items()):
        print(f"{tid}\t{t.get('status')}")
    return 0


def cmd_cas_init(root: Path, work_id: str) -> int:
    graph = load_graph(root, work_id)
    ids = list(_task_map(graph))
    cas_init(root, work_id, ids)
    print("revision=0")
    return 0


def cmd_cas_apply(root: Path, work_id: str, observed: int) -> int:
    def mut(doc: dict) -> None:
        return None

    doc = cas_apply(root, work_id, observed, mut)
    print(f"revision={doc['revision']}")
    return 0


def cmd_spawn(root: Path, work_id: str, task_id: str) -> int:
    doc = spawn_writer(root, work_id, task_id)
    print(f"running={task_id} revision={doc['revision']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ask inner-loop")
    p.add_argument("--root", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate TaskGraph")
    v.add_argument("work_id")

    s = sub.add_parser("status", help="print coordinator state")
    s.add_argument("work_id")

    ci = sub.add_parser("cas-init", help="write initial state.json")
    ci.add_argument("work_id")

    ca = sub.add_parser("cas-apply", help="CAS increment")
    ca.add_argument("work_id")
    ca.add_argument("--observed", type=int, required=True)

    sp = sub.add_parser("spawn-writer", help="mark one task running")
    sp.add_argument("work_id")
    sp.add_argument("task_id")

    for name in ("run", "resume", "cancel"):
        spn = sub.add_parser(name, help="later inner-loop task")
        spn.add_argument("work_id", nargs="?")

    args = p.parse_args(argv)
    root = repo_root(args.root)
    try:
        if args.cmd == "validate":
            return cmd_validate(root, args.work_id)
        if args.cmd == "status":
            return cmd_status(root, args.work_id)
        if args.cmd == "cas-init":
            return cmd_cas_init(root, args.work_id)
        if args.cmd == "cas-apply":
            return cmd_cas_apply(root, args.work_id, args.observed)
        if args.cmd == "spawn-writer":
            return cmd_spawn(root, args.work_id, args.task_id)
        print(f"{args.cmd} not implemented in t3-runner-graph", file=sys.stderr)
        return 2
    except ProtocolViolation as e:
        print(e, file=sys.stderr)
        return 2
    except CasConflict as e:
        print(e, file=sys.stderr)
        return 2
    except SecondWriter as e:
        print(e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
