"""Coherent local project reference inventory and immutable source vectors."""
from __future__ import annotations

import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess


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


def _reflog_generation(common, integration_ref, archive_ref):
    """Fingerprint ref movement, including advance-and-return ABA changes."""
    digest = hashlib.sha256()
    roots = [common / "logs" / "refs" / "heads" / "agent",
             common / "logs" / "refs" / "ask" / "references"]
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


def _inventory(root, integration_ref, archive_ref):
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
    for name, sha in refs.items():
        if name.startswith("refs/heads/agent/"):
            owner = name.removeprefix("refs/heads/agent/")
            add_owner(owner, "live", name, sha)
        elif name.startswith("refs/ask/references/"):
            owner = name.removeprefix("refs/ask/references/")
            if not owner or "/" in owner:
                raise ProjectError("invalid_owner", f"invalid shared owner ref: {name}")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", owner):
                raise ProjectError("invalid_owner", f"invalid shared owner ref: {name}")
            add_owner(owner, "shared", name, sha)
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
    for owner in archived - live:
        archive_refs = {ref: refs[ref] for ref in (integration_ref, archive_ref) if ref}
        if owner in owners and owners[owner]["kind"] != "archive":
            raise ProjectError("identity_conflict", f"owner {owner!r} is both archived and {owners[owner]['kind']}")
        if owner not in owners:
            owners[owner] = {"kind": "archive", "refs": archive_refs}
    return refs, owners


def capture_project(repository_root, integration_ref="refs/heads/develop",
                    archive_ref="refs/heads/main", retries=2, during_scan=None):
    """Capture a stable owner/ref inventory and selected source vector.

    Cooperating catalog publishers use the same persistent Git-common-dir lock.
    The before/after inventory check also detects non-cooperating ref changes;
    unsupported remote refs are intentionally outside this local capture.
    """
    root = Path(repository_root).resolve()
    common = _common_dir(root)
    lock_path = common / "ask-locks" / "references.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    last_code = "discovery_incomplete"
    for attempt in range(max(1, retries)):
        with lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                before, owners = _inventory(root, integration_ref, archive_ref)
                before_movement = _reflog_generation(common, integration_ref, archive_ref)
                if during_scan is not None:
                    during_scan(attempt, dict(before))
                after, _ = _inventory(root, integration_ref, archive_ref)
                after_movement = _reflog_generation(common, integration_ref, archive_ref)
                if before != after or before_movement != after_movement:
                    last_error = "reference inventory changed during capture"
                    continue
                vector = {"refs": dict(sorted(before.items())), "owners": owners,
                          "integration_ref": integration_ref, "archive_ref": archive_ref,
                          "movement_generation": after_movement,
                          "scope": "local-cooperating-repository"}
                encoded = json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()
                vector["generation"] = hashlib.sha256(encoded).hexdigest()
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
                              capture.get("archive_ref"))
    if current.get("status") != "complete":
        return current
    if current.get("generation") != capture.get("generation"):
        return {"status": "incomplete", "reason": "stale_inventory",
                "expected_generation": capture.get("generation"),
                "current_generation": current.get("generation")}
    return {"status": "complete", "generation": current["generation"]}
