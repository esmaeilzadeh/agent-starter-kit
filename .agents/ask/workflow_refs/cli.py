"""Public command facade for numeric workflow references."""
from __future__ import annotations

import argparse
import fcntl
import json
from pathlib import Path
import sys

from .identity import ReferenceError, parse_reference
from .impact import ImpactError, assess_impact, record_decision
from .project import capture_project, load_project_graph
from .projection import project_status, show_reference
from .store import (CatalogError, _lock, _publish_catalog, _recover_pending,
                    _repo_info, _trusted_catalog)
from .migration import export_bundle, import_bundle, migrate


def _json(value):
    print(json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def _persist_decision(repository_root, result):
    decision = result["decision"]
    owner = parse_reference(decision["dependent"])["owner"]
    catalog_path = repository_root / "work" / owner / "references" / "integrity.json"
    lock = _lock(catalog_path)
    try:
        root, common, relative = _repo_info(catalog_path)
        _recover_pending(catalog_path, owner, root, relative)
        catalog, old_ref = _trusted_catalog(catalog_path, owner, root, relative)
        if catalog is None or old_ref is None:
            raise CatalogError("missing_authority", "decision owner has no trusted catalog")
        raw_decisions = catalog.get("decisions", [])
        if not isinstance(raw_decisions, list):
            raise CatalogError("invalid_catalog", "trusted decision records are not a list")
        entries = catalog.get("entries", [])
        if not isinstance(entries, list):
            raise CatalogError("invalid_catalog", "trusted catalog entries are not a list")
        decisions = list(raw_decisions)
        for existing in decisions:
            if existing.get("decision") == decision and existing.get("status") == result["status"]:
                return existing["reference"]
        sequence = 0
        for item in [*entries, *decisions]:
            try:
                parsed = parse_reference(item.get("reference"))
            except (TypeError, AttributeError, ReferenceError) as exc:
                raise CatalogError("invalid_catalog", "trusted review reference is malformed") from exc
            if parsed["owner"] != owner or parsed["kind"] != "review":
                continue
            sequence = max(sequence, parsed["ids"][-1])
        sequence += 1
        reference = f"{owner}/review/{sequence}@1"
        decisions.append({"reference": reference, "status": result["status"],
                          "decision": decision})
        catalog["decisions"] = decisions
        catalog["generation"] += 1
        _publish_catalog(catalog_path, owner, root, common, relative, catalog, old_ref)
        return reference
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


def build_parser():
    parser = argparse.ArgumentParser(prog="ask references")
    sub = parser.add_subparsers(dest="command", required=True)
    show = sub.add_parser("show", help="resolve one exact numeric item revision")
    show.add_argument("reference")
    show.add_argument("--integrity", action="store_true")
    status = sub.add_parser("status", help="show one version or compact owner inventory")
    status.add_argument("reference", nargs="?")
    status.add_argument("--shared-owner", action="append", default=[])
    impact = sub.add_parser("impact", help="assess changes between two coherent project captures")
    impact.add_argument("--source", required=True, type=Path)
    impact.add_argument("--candidate", required=True, type=Path)
    impact.add_argument("--shared-owner", action="append", default=[])
    impact.add_argument("--integration-ref", default="refs/heads/develop")
    impact.add_argument("--archive-ref", default="refs/heads/main")
    decide = sub.add_parser("decide", help="assess an explicit reviewed impact decision")
    decide.add_argument("--evidence", required=True, type=Path)
    decide.add_argument("--recorded-by", required=True)
    decide.add_argument("--shared-owner", action="append", default=[])
    migration = sub.add_parser("migrate", help="apply explicitly declared legacy mappings")
    migration.add_argument("owner")
    export = sub.add_parser("export", help="export trusted records and Git object closure")
    export.add_argument("owner")
    export.add_argument("--out", required=True, type=Path)
    imp = sub.add_parser("import", help="verify an export against local trusted authority")
    imp.add_argument("bundle", type=Path)
    return parser


def main(argv=None, *, root=None):
    args = build_parser().parse_args(argv)
    repository_root = Path(root or Path.cwd()).resolve()
    try:
        if args.command == "show":
            _json(show_reference(repository_root, args.reference, integrity=args.integrity))
        elif args.command == "status":
            result = (show_reference(repository_root, args.reference) if args.reference else
                      project_status(repository_root, shared_owners=args.shared_owner))
            _json(result)
            return 0 if result.get("status") == "resolved" or result.get("status") == "complete" else 1
        elif args.command == "impact":
            source = json.loads(args.source.read_text(encoding="utf-8"))
            capture = json.loads(args.candidate.read_text(encoding="utf-8"))
            if (not isinstance(source, dict) or source.get("status") != "complete"
                    or not isinstance(source.get("refs"), dict)
                    or not isinstance(capture, dict) or capture.get("status") != "complete"
                    or not isinstance(capture.get("refs"), dict)):
                raise ValueError("source and candidate must be complete project captures")
            changed_owners = set()
            for ref in set(source["refs"]) | set(capture["refs"]):
                if source["refs"].get(ref) != capture["refs"].get(ref):
                    fields = ref.split("/")
                    if len(fields) >= 4 and fields[:2] == ["refs", "heads"] and fields[2] == "agent":
                        changed_owners.add(fields[3])
                    elif ref.startswith("refs/ask/references/"):
                        changed_owners.add(ref.rsplit("/", 1)[-1])
                    elif ref in {capture.get("integration_ref"), capture.get("archive_ref")}:
                        changed_owners.update(capture.get("owners", {}))
            graph = load_project_graph(repository_root, capture)
            changed = [reference for reference, node in graph.get("nodes", {}).items()
                       if node.get("owner") in changed_owners]
            result = assess_impact(graph, changed, capture=capture,
                                   repository_root=repository_root)
            _json(result)
            return 0 if result.get("status") == "complete" else 1
        elif args.command == "decide":
            decision = json.loads(args.evidence.read_text(encoding="utf-8"))
            capture = capture_project(repository_root, shared_owners=args.shared_owner)
            if decision.get("coordinator") != args.recorded_by:
                raise ImpactError("authority_missing", "--recorded-by must match the attributed coordinator")
            result = record_decision(decision, capture=capture,
                                     required_paths=decision.get("required_paths"),
                                     authority_check=lambda value, _capture:
                                     value.get("coordinator") == args.recorded_by)
            reference = _persist_decision(repository_root, result)
            _json({"status": "recorded", "reference": reference, "decision": result})
            return 0
        elif args.command == "migrate":
            _json(migrate(repository_root, args.owner))
        elif args.command == "export":
            _json(export_bundle(repository_root, args.owner, args.out))
        elif args.command == "import":
            _json(import_bundle(repository_root, args.bundle))
        return 0
    except (ReferenceError, CatalogError, ImpactError, OSError, UnicodeDecodeError,
            json.JSONDecodeError, ValueError) as exc:
        code = getattr(exc, "code", "invalid_request")
        _json({"status": "unavailable", "scope": "requested-reference",
               "reason": code, "detail": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
