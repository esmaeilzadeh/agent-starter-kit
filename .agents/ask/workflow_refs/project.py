"""Coherent local project reference inventory and immutable source vectors."""
from __future__ import annotations

import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
from decimal import Decimal

from .compare import compare_items, extract_git_item
from .identity import ReferenceError, parse_reference
from .profiles import get_profile
from .store import payload_digests


class ProjectError(ValueError):
    """Project discovery is invalid or cannot establish a complete scope."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _git(root, *args):
    try:
        return subprocess.run(["git", *args], cwd=root, check=True,
                              capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ProjectError("discovery_incomplete", f"Git discovery failed: {' '.join(args)}") from exc


def _common_dir(root):
    value = Path(_git(root, "rev-parse", "--git-common-dir"))
    return value.resolve() if value.is_absolute() else (root / value).resolve()


def _reflog_generation(common, integration_ref, archive_ref, *, catalogs=True):
    """Fingerprint ref movement, including advance-and-return ABA changes."""
    digest = hashlib.sha256()
    roots = [common / "logs" / "refs" / "heads" / "agent"]
    if catalogs:
        roots.append(common / "logs" / "refs" / "ask" / "references")
    roots.extend(common / "logs" / Path(ref) for ref in (integration_ref, archive_ref) if ref)
    paths = set()
    for root in roots:
        if root.is_dir():
            paths.update(item for item in root.rglob("*") if item.is_file())
        elif root.is_file():
            paths.add(root)
    for path in sorted(paths):
        digest.update(path.relative_to(common / "logs").as_posix().encode())
        try:
            digest.update(path.read_bytes())
        except OSError as exc:
            raise ProjectError("discovery_incomplete", "reference movement log is unavailable") from exc
    return digest.hexdigest()


def _ref_storage_generation(common, integration_ref=None, archive_ref=None, *, catalogs=True):
    """Observe loose/packed owner-ref storage changes even without reflogs."""
    roots = [common / "refs" / "heads" / "agent"]
    if catalogs:
        roots.append(common / "refs" / "ask" / "references")
    digest = hashlib.sha256()
    paths = set()
    for root in roots:
        if root.exists():
            paths.add(root)
            if root.is_dir():
                paths.update(root.rglob("*"))
    packed = common / "packed-refs"
    if packed.exists():
        paths.add(packed)
    for ref in (integration_ref, archive_ref):
        if not ref:
            continue
        path = common / Path(ref)
        if path.exists():
            paths.add(path)
        parent = path.parent
        while parent != common and common in parent.parents:
            paths.add(parent)
            parent = parent.parent
    try:
        for path in sorted(paths):
            stat = path.lstat()
            digest.update(path.relative_to(common).as_posix().encode())
            digest.update(f"{stat.st_ino}:{stat.st_mtime_ns}:{stat.st_size}:{stat.st_mode}".encode())
    except OSError as exc:
        raise ProjectError("discovery_incomplete", "owner reference storage cannot be inspected") from exc
    return digest.hexdigest()


def _inventory(root, integration_ref, archive_ref, shared_owners):
    refs = {}
    owners = {}
    def add_owner(owner, kind, ref, sha):
        existing = owners.get(owner)
        if existing is not None and existing["kind"] != kind:
            raise ProjectError("identity_conflict", f"owner {owner!r} is declared as both {existing['kind']} and {kind}")
        if existing is None:
            existing = owners[owner] = {"kind": kind, "refs": {}}
        existing["refs"][ref] = sha
    raw = _git(root, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads/agent", "refs/ask/references")
    for row in raw.splitlines():
        if not row:
            continue
        name, sha = row.split(" ", 1)
        # Inner task refs are execution worktrees, never project owners.
        if name.startswith("refs/heads/agent/"):
            owner = name.removeprefix("refs/heads/agent/")
            owner_parts = owner.split("/")
            if len(owner_parts) == 3 and owner_parts[1] == "task" and owner_parts[2].isdigit():
                continue
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", owner):
                raise ProjectError("invalid_owner", f"invalid live owner ref: {name}")
            refs[name] = sha
        else:
            refs[name] = sha
    for ref in (integration_ref, archive_ref):
        if ref:
            sha = _git(root, "rev-parse", "--verify", ref + "^{commit}")
            refs[ref] = sha
    # Archived workstreams are those present in selected integration/archive trees
    # without a live owner ref. Keep both source refs in each archived vector.
    archived = set()
    for ref in (integration_ref, archive_ref):
        if not ref:
            continue
        sha = refs[ref]
        listing = _git(root, "ls-tree", "--name-only", sha + ":work").splitlines()
        archived.update(name for name in listing if name and name != "INDEX.md")
    live = {name.removeprefix("refs/heads/agent/") for name in refs
            if name.startswith("refs/heads/agent/")}
    for name, sha in refs.items():
        if name.startswith("refs/heads/agent/"):
            owner = name.removeprefix("refs/heads/agent/")
            add_owner(owner, "live", name, sha)
        elif name.startswith("refs/ask/references/"):
            owner = name.removeprefix("refs/ask/references/")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", owner):
                raise ProjectError("invalid_owner", f"invalid shared owner ref: {name}")
            if owner in live:
                add_owner(owner, "live", name, sha)
            elif owner in archived:
                if owner not in owners:
                    owners[owner] = {"kind": "archive", "refs":
                        {ref: refs[ref] for ref in (integration_ref, archive_ref) if ref}}
                owners[owner]["refs"][name] = sha
            elif owner in shared_owners:
                add_owner(owner, "shared", name, sha)
            else:
                raise ProjectError("unknown_owner_registration", f"shared owner {owner!r} is not explicitly registered")
    for owner in archived - live:
        archive_refs = {ref: refs[ref] for ref in (integration_ref, archive_ref) if ref}
        if owner in owners and owners[owner]["kind"] != "archive":
            raise ProjectError("identity_conflict", f"owner {owner!r} is both archived and {owners[owner]['kind']}")
        if owner not in owners:
            owners[owner] = {"kind": "archive", "refs": archive_refs}
    return refs, owners


def _context_generation(root, vector):
    """Hash dependency context while ignoring decision-only catalog publication.

    The exact catalog refs remain in ``vector['refs']`` and still select all
    graph data. A decision record is metadata about the captured graph, though,
    and publishing that record must not invalidate the generation it names.
    Catalog item entries and every other selected ref remain generation-bound.
    """
    refs = {}
    for name, sha in vector["refs"].items():
        if not name.startswith("refs/ask/references/"):
            refs[name] = sha
            continue
        owner = name.rsplit("/", 1)[-1]
        catalog_path = ("results/references/integrity.json" if owner == "repository-runs"
                        else f"work/{owner}/references/integrity.json")
        try:
            catalog = json.loads(_regular_file_at(root, sha, catalog_path).decode("utf-8"))
        except (ProjectError, UnicodeDecodeError, json.JSONDecodeError):
            refs[name] = sha
            continue
        if (not isinstance(catalog, dict) or catalog.get("schema") != "ask-reference-catalog/v1"
                or catalog.get("owner") != owner or not isinstance(catalog.get("decisions", []), list)):
            refs[name] = sha
            continue
        context_catalog = dict(catalog)
        context_catalog.pop("generation", None)
        context_catalog.pop("decisions", None)
        canonical = json.dumps(context_catalog, sort_keys=True, separators=(",", ":")).encode()
        refs[name] = hashlib.sha256(canonical).hexdigest()
    stable = {key: value for key, value in vector.items()
              if key not in {"movement_generation", "storage_generation", "generation", "status"}}
    stable["refs"] = refs
    # ``owners`` repeats the same ref/object mapping for scoped lookup. Keep it
    # on the same normalized identities as ``refs`` so publishing decision-only
    # catalog metadata does not change the context through this second path.
    owners = {}
    for owner, details in vector.get("owners", {}).items():
        if not isinstance(details, dict):
            owners[owner] = details
            continue
        normalized = dict(details)
        owner_refs = details.get("refs")
        if isinstance(owner_refs, dict):
            normalized["refs"] = {name: refs.get(name, sha)
                                  for name, sha in owner_refs.items()}
        owners[owner] = normalized
    stable["owners"] = owners
    encoded = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def capture_project(repository_root, integration_ref="refs/heads/develop",
                    archive_ref="refs/heads/main", retries=2, during_scan=None,
                    shared_owners=None):
    """Capture a stable owner/ref inventory and selected source vector.

    Cooperating catalog publishers use the same persistent Git-common-dir lock.
    The before/after inventory check also detects non-cooperating ref changes;
    unsupported remote refs are intentionally outside this local capture.
    """
    root = Path(repository_root).resolve()
    shared_owners = set(shared_owners or ()) | {"repository-runs"}
    if any(not isinstance(owner, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", owner)
           for owner in shared_owners):
        return {"status": "incomplete", "reason": "invalid_owner_registration"}
    common = _common_dir(root)
    ref_storage = subprocess.run(["git", "config", "--get", "extensions.refStorage"],
                                 cwd=root, capture_output=True, text=True)
    if ref_storage.returncode not in (0, 1) or (ref_storage.returncode == 0
                                                and ref_storage.stdout.strip() != "files"):
        return {"status": "incomplete", "reason": "unsupported_ref_storage",
                "scope": "local-cooperating-repository"}
    lock_path = common / "ask-locks" / "references.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    last_code = "discovery_incomplete"
    for attempt in range(max(1, retries)):
        with lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                before, owners = _inventory(root, integration_ref, archive_ref, shared_owners)
                before_movement = _reflog_generation(common, integration_ref, archive_ref)
                before_storage = _ref_storage_generation(common, integration_ref, archive_ref)
                if during_scan is not None:
                    during_scan(attempt, dict(before))
                after, _ = _inventory(root, integration_ref, archive_ref, shared_owners)
                after_movement = _reflog_generation(common, integration_ref, archive_ref)
                after_storage = _ref_storage_generation(common, integration_ref, archive_ref)
                if before != after or before_movement != after_movement or before_storage != after_storage:
                    last_error = "reference inventory changed during capture"
                    continue
                vector = {"refs": dict(sorted(before.items())), "owners": owners,
                          "integration_ref": integration_ref, "archive_ref": archive_ref,
                          "shared_owners": sorted(shared_owners),
                          "movement_generation": after_movement,
                          "storage_generation": after_storage,
                          "source_movement_generation": _reflog_generation(
                              common, integration_ref, archive_ref, catalogs=False),
                          "source_storage_generation": _ref_storage_generation(
                              common, integration_ref, archive_ref, catalogs=False),
                          "scope": "local-cooperating-repository"}
                vector["generation"] = _context_generation(root, vector)
                vector["status"] = "complete"
                return vector
            except ProjectError as exc:
                last_error = str(exc)
                last_code = exc.code
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return {"status": "incomplete", "reason": last_code,
            "detail": last_error, "scope": "local-cooperating-repository"}


def validate_capture(repository_root, capture):
    """Confirm a capture still names the exact applicable ref generation."""
    if not isinstance(capture, dict) or capture.get("status") != "complete":
        return {"status": "incomplete", "reason": "capture_unavailable"}
    current = capture_project(repository_root, capture.get("integration_ref"),
                              capture.get("archive_ref"), shared_owners=capture.get("shared_owners", []))
    if current.get("status") != "complete":
        return current
    # Source movement always invalidates context; catalog-only decisions may
    # advance authority without changing graph inputs. Same-ref ABA is stale.
    same_refs_moved = (current.get("refs") == capture.get("refs") and any(
        current.get(key) != capture.get(key)
        for key in ("movement_generation", "storage_generation")))
    if current.get("generation") != capture.get("generation") or same_refs_moved:
        return {"status": "incomplete", "reason": "stale_inventory",
                "expected_generation": capture.get("generation"),
                "current_generation": current.get("generation")}
    return {"status": "complete", "generation": current["generation"]}


def _regular_file_at(root, commit, path):
    try:
        entry = subprocess.run(["git", "ls-tree", "-z", commit, "--", path], cwd=root,
                               capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ProjectError("discovery_incomplete", f"committed source object is unavailable: {path}") from exc
    if not entry:
        raise ProjectError("discovery_incomplete", f"committed declaration is missing: {path}")
    mode = entry.split(b"\t", 1)[0].split(b" ", 1)[0]
    if mode not in (b"100644", b"100755"):
        raise ProjectError("discovery_incomplete", f"committed declaration is not a regular file: {path}")
    try:
        return subprocess.run(["git", "show", f"{commit}:{path}"], cwd=root,
                              capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ProjectError("discovery_incomplete", f"committed declaration is unavailable: {path}") from exc


def load_project_graph(repository_root, capture):
    """Load every dependency edge from captured, authority-registered catalogs."""
    root = Path(repository_root).resolve()
    validity = validate_capture(root, capture)
    if validity.get("status") != "complete":
        return {"status": "incomplete", "reason": validity.get("reason", "stale_inventory"),
                "unresolved": []}
    nodes = {}
    unresolved = []
    latest_entries = {}
    for owner in sorted(capture.get("owners", {})):
        authority_ref = f"refs/ask/references/{owner}"
        authority_sha = capture.get("refs", {}).get(authority_ref)
        if not authority_sha:
            unresolved.append({"owner": owner, "reason": "catalog_authority_missing"})
            continue
        catalog_path = ("results/references/integrity.json" if owner == "repository-runs"
                        else f"work/{owner}/references/integrity.json")
        try:
            raw = _regular_file_at(root, authority_sha, catalog_path)
            catalog = json.loads(raw.decode("utf-8"))
        except (ProjectError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            unresolved.append({"owner": owner, "reason": getattr(exc, "code", "catalog_invalid"),
                               "detail": str(exc)})
            continue
        if (not isinstance(catalog, dict) or catalog.get("schema") != "ask-reference-catalog/v1"
                or catalog.get("owner") != owner or type(catalog.get("generation")) is not int
                or not isinstance(catalog.get("entries"), list)
                or not isinstance(catalog.get("snapshots"), dict)):
            unresolved.append({"owner": owner, "reason": "catalog_invalid"})
            continue
        for entry in catalog["entries"]:
            if not isinstance(entry, dict):
                unresolved.append({"owner": owner, "reference": None,
                                   "reason": "catalog_entry_invalid", "detail": "entry must be an object"})
                continue
            try:
                parsed = parse_reference(entry.get("reference"))
                if parsed["owner"] != owner or entry.get("profile") is None:
                    raise ProjectError("identity_conflict", "catalog entry owner/profile differs")
                profile = get_profile(entry["profile"])
                snapshot = catalog["snapshots"].get(entry.get("snapshot_id"))
                if profile is None or not isinstance(snapshot, dict):
                    raise ProjectError("comparison_incomplete", "catalog source/profile is unavailable")
                commit, source_path = snapshot.get("commit"), snapshot.get("path")
                if not isinstance(commit, str) or not isinstance(source_path, str):
                    raise ProjectError("discovery_incomplete", "catalog snapshot is malformed")
                source = _regular_file_at(root, commit, source_path)
                semantics = entry.get("digest_semantics")
                if not isinstance(semantics, list) or not semantics:
                    raise ProjectError("comparison_incomplete", "catalog digest semantics are missing")
                verified = {}
                for semantics_name in semantics:
                    values = payload_digests(source, semantics=semantics_name)
                    verified[semantics_name] = values[semantics_name]
                if verified != entry.get("digests"):
                    raise ProjectError("integrity_mismatch", "catalog source digest does not match authority")
                extracted = extract_git_item(root, commit, source_path, entry.get("item_id"), entry["profile"])
                if extracted.get("status") != "found":
                    raise ProjectError("comparison_incomplete", f"catalog item extraction is {extracted.get('status')}")
                payload = extracted["payload"]
                if not isinstance(payload, dict) or not isinstance(payload.get("inputs"), list):
                    raise ProjectError("discovery_incomplete", "item has no complete input declaration")
                reference = parsed["canonical"]
                if reference in nodes:
                    raise ProjectError("identity_conflict", f"duplicate catalog item: {reference}")
                nodes[reference] = {"reference": reference, "owner": owner,
                    "source": extracted["source"], "profile": entry["profile"],
                    "payload": payload, "inputs": payload["inputs"],
                    "active": payload.get("active") if type(payload.get("active")) is bool else None,
                    "lifecycle_explicit": type(payload.get("active")) is bool}
                current = latest_entries.get(parsed["logical_id"])
                if current is None or parsed["revision"] > current[0]:
                    latest_entries[parsed["logical_id"]] = (parsed["revision"], entry, payload, owner, snapshot)
            except (ProjectError, ReferenceError, TypeError, KeyError, ValueError) as exc:
                unresolved.append({"owner": owner, "reference": entry.get("reference"),
                                   "reason": getattr(exc, "code", "catalog_entry_invalid"),
                                   "detail": str(exc)})
    if unresolved:
        return {"status": "incomplete", "capture_generation": capture["generation"],
                "nodes": nodes, "unresolved": unresolved}
    latest = {}
    for logical_id, (revision, _entry, _payload, _owner, _snapshot) in latest_entries.items():
        latest[logical_id] = (revision, f"{logical_id}@{revision}")
    for ref, node in nodes.items():
        if node["active"] is None:
            node["active"] = latest[parse_reference(ref)["logical_id"]][1] == ref
    changed_active = True
    while changed_active:
        changed_active = False
        for node in nodes.values():
            if not node["active"]:
                continue
            for edge in node["inputs"]:
                target = parse_reference(edge["reference"])["canonical"]
                if (target in nodes and not nodes[target]["active"]
                        and not nodes[target]["lifecycle_explicit"]):
                    nodes[target]["active"] = True
                    changed_active = True
    graph = {"nodes": nodes, "capture_generation": capture["generation"],
             "deletions": {}, "changes": [], "candidate_inputs": {},
             "unregistered_candidates": []}
    for logical_id, (_revision, entry, old_payload, owner, snapshot) in latest_entries.items():
        owner_info = capture["owners"].get(owner, {})
        if owner_info.get("kind") == "live":
            candidate_ref = f"refs/heads/agent/{owner}"
        elif owner_info.get("kind") == "archive":
            candidate_ref = capture.get("integration_ref") or capture.get("archive_ref")
        else:
            candidate_ref = f"refs/ask/references/{owner}"
        candidate_commit = capture.get("refs", {}).get(candidate_ref)
        if not candidate_commit or not isinstance(snapshot, dict):
            unresolved.append({"owner": owner, "reference": entry.get("reference"),
                               "reason": "candidate_source_unavailable"})
            continue
        candidate = extract_git_item(root, candidate_commit, snapshot["path"], entry["item_id"], entry["profile"])
        ref = entry["reference"]
        if candidate.get("status") == "absent":
            graph["deletions"][ref] = {"status": "absent", "source_available": True,
                                       "source": candidate["source"]}
        elif candidate.get("status") != "found":
            unresolved.append({"owner": owner, "reference": ref,
                               "reason": "candidate_source_incomplete", "detail": candidate.get("reason")})
        else:
            if not isinstance(candidate.get("payload"), dict) or not isinstance(candidate["payload"].get("inputs"), list):
                unresolved.append({"owner": owner, "reference": ref,
                                   "reason": "candidate_declarations_missing"})
                continue
            candidate_inputs = candidate["payload"]["inputs"]
            graph["candidate_inputs"][ref] = candidate_inputs
            current_identity = parse_reference(ref)
            candidate_version = candidate["payload"].get("version", current_identity["revision"])
            if (isinstance(candidate_version, (int, Decimal)) and not isinstance(candidate_version, bool)
                    and candidate_version > 0 and int(candidate_version) == candidate_version):
                candidate_ref = f"{current_identity['logical_id']}@{int(candidate_version)}"
                if (candidate_ref not in nodes or
                        (candidate_ref == ref and candidate_inputs != old_payload["inputs"])):
                    graph["unregistered_candidates"].append({
                        "reference": ref, "candidate_reference": candidate_ref,
                        "source": candidate["source"]})
            else:
                graph["unregistered_candidates"].append({
                    "reference": ref, "reason": "candidate_revision_missing",
                    "source": candidate["source"]})
            comparison = compare_items(old_payload, candidate["payload"], entry["profile"],
                old_payload["inputs"], candidate_inputs)
            if comparison["status"] == "incomplete":
                unresolved.append({"owner": owner, "reference": ref,
                                   "reason": "comparison_incomplete", "detail": comparison.get("reason")})
            elif comparison["status"] == "changed":
                graph["changes"].append({"reference": ref, "comparison": comparison,
                                         "candidate": candidate["source"]})
    if unresolved:
        graph.update({"status": "incomplete", "unresolved": unresolved})
        return graph
    # The impact validator checks reference resolution and cycles. Reuse it here
    # so an owner inventory is never mistaken for a complete dependency graph.
    from .impact import _graph
    try:
        _graph(graph)
    except ValueError as exc:
        return {"status": "incomplete", "capture_generation": capture["generation"],
                "nodes": nodes, "unresolved": [{"reason": getattr(exc, "code", "discovery_incomplete"),
                                                  "detail": str(exc)}]}
    graph["status"] = "complete"
    return graph
