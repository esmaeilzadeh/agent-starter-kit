"""Immutable integrity catalog publication and resolution.

Each catalog has one persistent advisory lock, a monotonically increasing
generation, and append-only revision entries. The JSON file is the public
catalog; every entry binds an exact Git snapshot and payload digest.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import uuid

from .identity import ReferenceError, parse_reference


class CatalogError(ValueError):
    """A catalog is invalid, stale, unavailable, or conflicts with history."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def payload_digests(payload, semantics=None):
    if semantics not in (None, "canonical-json/1", "exact-bytes/1"):
        raise CatalogError("unsupported", f"unsupported digest semantics: {semantics}")
    raw = _payload_bytes(payload)
    byte_digest = hashlib.sha256(raw).hexdigest()
    if semantics == "exact-bytes/1":
        return {"exact-bytes/1": byte_digest}
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        if semantics is None:
            return {"exact-bytes/1": byte_digest}
        raise CatalogError("invalid_payload", "canonical JSON digest requires valid UTF-8 JSON") from exc
    try:
        canonical = json.dumps(value, sort_keys=True, ensure_ascii=False,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CatalogError("invalid_payload", "JSON value cannot be canonically serialized") from exc
    if semantics == "canonical-json/1":
        return {"canonical-json/1": hashlib.sha256(canonical).hexdigest()}
    return {"canonical-json/1": hashlib.sha256(canonical).hexdigest(), "exact-bytes/1": byte_digest}


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _payload_bytes(payload) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, str):
        return payload.encode("utf-8")
    try:
        return (json.dumps(payload, ensure_ascii=False, separators=(",", ":"),
                           allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CatalogError("invalid_payload", "catalog payload must be bytes, UTF-8 text, or JSON value") from exc


def _atomic_json(path: Path, value: dict) -> None:
    _atomic_bytes(path, _catalog_bytes(value))


def _catalog_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _atomic_bytes(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix="." + path.name + ".",
                                         suffix=".tmp", delete=False) as stream:
            name = stream.name
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if name is not None:
            Path(name).unlink(missing_ok=True)


def _read_catalog(path: Path, owner: str) -> dict:
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError("missing", f"catalog is missing or invalid: {path}") from exc
    if (not isinstance(catalog, dict) or catalog.get("schema") != "ask-reference-catalog/v1"
            or catalog.get("owner") != owner or type(catalog.get("generation")) is not int
            or catalog["generation"] < 0 or not isinstance(catalog.get("entries"), list)):
        raise CatalogError("invalid_catalog", "catalog schema, owner, generation, or entries are invalid")
    return catalog


def _git(root: Path, *args: str, input_bytes=None, env=None) -> bytes:
    try:
        return subprocess.run(["git", *args], cwd=root, input=input_bytes,
                              capture_output=True, check=True, env=env).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"")
        raise CatalogError("git_error", f"Git reference operation failed: {detail.decode(errors='replace').strip()}") from exc


def _repo_info(path: Path) -> tuple[Path, Path, str]:
    start = path.parent
    while not start.exists() and start != start.parent:
        start = start.parent
    start = start.resolve()
    try:
        root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=start,
                                   capture_output=True, text=True, check=True).stdout.strip()).resolve()
        common_text = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root,
                                     capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CatalogError("missing_repository", "integrity catalog must live inside a Git worktree") from exc
    common = Path(common_text)
    if not common.is_absolute():
        common = (root / common).resolve()
    try:
        relative = path.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise CatalogError("unsafe_path", "integrity catalog must be inside its Git worktree") from exc
    return root, common, relative


def _lock(path: Path):
    _root, common, _relative = _repo_info(path)
    lock_path = common / "ask-locks" / "references.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    stream = lock_path.open("a+b")
    fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
    return stream


def _ref(owner: str) -> str:
    return f"refs/ask/references/{owner}"


def _ref_value(root: Path, ref: str) -> str | None:
    result = subprocess.run(["git", "rev-parse", "--verify", ref], cwd=root,
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def _tree_blob(root: Path, ref_value: str, relative: str) -> bytes:
    try:
        return _git(root, "show", f"{ref_value}:{relative}")
    except CatalogError as exc:
        raise CatalogError("missing_authority", "trusted catalog ref has no integrity file") from exc


def _read_catalog_bytes(raw: bytes, owner: str) -> dict:
    try:
        catalog = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError("invalid_catalog", "trusted catalog JSON is invalid") from exc
    if (not isinstance(catalog, dict) or catalog.get("schema") != "ask-reference-catalog/v1"
            or catalog.get("owner") != owner or type(catalog.get("generation")) is not int
            or catalog["generation"] < 0 or not isinstance(catalog.get("entries"), list)
            or not isinstance(catalog.get("snapshots"), dict)):
        raise CatalogError("invalid_catalog", "catalog schema, owner, generation, or entries are invalid")
    return catalog


def _recover_pending(path: Path, owner: str, root: Path, relative: str) -> None:
    journal = path.with_name(path.name + ".pending")
    if not journal.exists():
        return
    try:
        pending = json.loads(journal.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError("invalid_journal", "catalog publication journal is invalid") from exc
    current = _ref_value(root, _ref(owner))
    if current == pending.get("new_ref"):
        raw = _tree_blob(root, current, relative)
        if hashlib.sha256(raw).hexdigest() != pending.get("catalog_sha256"):
            raise CatalogError("integrity_mismatch", "published catalog differs from recovery journal")
        _atomic_bytes(path, raw)
        journal.unlink(missing_ok=True)
    elif current == pending.get("old_ref"):
        journal.unlink(missing_ok=True)
    else:
        raise CatalogError("conflict", "catalog ref changed outside its pending publication")


def _trusted_catalog(path: Path, owner: str, root: Path, relative: str) -> tuple[dict | None, str | None]:
    ref_value = _ref_value(root, _ref(owner))
    if ref_value is None:
        if path.exists():
            raise CatalogError("missing_authority", "unregistered catalog file cannot establish its own authority")
        return None, None
    trusted_bytes = _tree_blob(root, ref_value, relative)
    catalog = _read_catalog_bytes(trusted_bytes, owner)
    if path.exists():
        try:
            local = path.read_bytes()
        except OSError as exc:
            raise CatalogError("missing", "catalog file is unavailable") from exc
        if local != trusted_bytes:
            raise CatalogError("integrity_mismatch", "working catalog differs from its trusted Git ref")
    else:
        # A complete authority ref can restore a missing worktree copy after a
        # process interruption; restoration uses exact ref bytes only.
        _atomic_bytes(path, trusted_bytes)
    return catalog, ref_value


def _publish_catalog(path: Path, owner: str, root: Path, common: Path,
                     relative: str, catalog: dict, old_ref: str | None) -> str:
    raw = _catalog_bytes(catalog)
    blob = _git(root, "hash-object", "-w", "--stdin", input_bytes=raw).decode().strip()
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    index_path = common / "ask-locks" / f"references-index-{uuid.uuid4().hex}"
    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = str(index_path)
    try:
        _git(root, "read-tree", head, env=env)
        _git(root, "update-index", "--add", "--cacheinfo", f"100644,{blob},{relative}", env=env)
        tree = _git(root, "write-tree", env=env).decode().strip()
        commit = _git(root, "commit-tree", tree, "-p", head,
                      input_bytes=b"Publish immutable workflow reference catalog\n").decode().strip()
    finally:
        index_path.unlink(missing_ok=True)
    journal = path.with_name(path.name + ".pending")
    _atomic_json(journal, {"old_ref": old_ref, "new_ref": commit,
                           "catalog_sha256": hashlib.sha256(raw).hexdigest()})
    object_format = _git(root, "rev-parse", "--show-object-format").decode().strip()
    zero_id = "0" * {"sha1": 40, "sha256": 64}.get(object_format, 0)
    if not zero_id:
        raise CatalogError("unsupported", f"unsupported Git object format: {object_format}")
    _git(root, "update-ref", _ref(owner), commit, old_ref or zero_id)
    _atomic_bytes(path, raw)
    journal.unlink(missing_ok=True)
    return commit


def _safe_snapshot(snapshot: object) -> tuple[str, str]:
    if not isinstance(snapshot, dict):
        raise CatalogError("invalid_snapshot", "snapshot must declare commit and repository path")
    commit = snapshot.get("commit")
    source_path = snapshot.get("path")
    if not isinstance(commit, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
        raise CatalogError("invalid_snapshot", "snapshot commit must be a full Git object ID")
    if not isinstance(source_path, str) or not source_path:
        raise CatalogError("invalid_snapshot", "snapshot path is missing")
    posix = PurePosixPath(source_path)
    if posix.is_absolute() or ".." in posix.parts or "\\" in source_path:
        raise CatalogError("invalid_snapshot", "snapshot path must be repository-relative and safe")
    return commit, source_path


def _validate_commit(root: Path, commit: str) -> None:
    try:
        object_format = _git(root, "rev-parse", "--show-object-format").decode().strip()
        expected_length = {"sha1": 40, "sha256": 64}.get(object_format)
        resolved = _git(root, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    except CatalogError as exc:
        raise CatalogError("invalid_snapshot", "snapshot commit must resolve to a full commit ID") from exc
    if expected_length is None or len(commit) != expected_length or resolved != commit:
        raise CatalogError("invalid_snapshot", "snapshot commit must be a full ID in this repository's object format")


def initialize_catalog(path, owner):
    path = Path(path)
    if not isinstance(owner, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", owner):
        raise CatalogError("invalid_owner", "catalog owner must be a lowercase slug")
    root, common, relative = _repo_info(path)
    stream = _lock(path)
    try:
        _recover_pending(path, owner, root, relative)
        catalog, old_ref = _trusted_catalog(path, owner, root, relative)
        if catalog is not None:
            return catalog
        catalog = {"schema": "ask-reference-catalog/v1", "owner": owner,
                   "generation": 0, "snapshots": {}, "entries": []}
        _publish_catalog(path, owner, root, common, relative, catalog, old_ref)
        return catalog
    finally:
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


def register_revision(catalog_path, owner, logical_id, snapshot, item_id, profile, payload,
                     expected_generation=None, after_publish=None, revision=None):
    path = Path(catalog_path)
    try:
        identity = parse_reference(logical_id if "@" in str(logical_id) else str(logical_id) + "@1")
    except ReferenceError as exc:
        raise CatalogError(exc.code, str(exc)) from exc
    if identity["owner"] != owner:
        raise CatalogError("owner_mismatch", "reference owner differs from catalog owner")
    if identity["revision"] != 1 and "@" in str(logical_id):
        identity["logical_id"] = str(logical_id).rsplit("@", 1)[0]
    commit, source_path = _safe_snapshot(snapshot)
    root, _common, relative = _repo_info(path)
    if not isinstance(item_id, str) or not item_id.strip() or not isinstance(profile, str) or not profile.strip():
        raise CatalogError("invalid_entry", "stable item ID and comparison profile are required")
    raw = _payload_bytes(payload)
    digests = payload_digests(raw, semantics="exact-bytes/1" if profile == "prose-item/1" else None)
    try:
        pinned = subprocess.run(["git", "show", f"{commit}:{source_path}"], cwd=root,
                                check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CatalogError("missing_source", "cannot publish an unavailable Git source") from exc
    if pinned != raw:
        raise CatalogError("integrity_mismatch", "catalog payload must exactly match its pinned Git source")
    stream = _lock(path)
    try:
        _recover_pending(path, owner, root, relative)
        catalog, old_ref = _trusted_catalog(path, owner, root, relative)
        if catalog is None or old_ref is None:
            raise CatalogError("missing_authority", "initialize the trusted catalog before publishing revisions")
        generation = catalog["generation"]
        if expected_generation is not None and expected_generation != generation:
            raise CatalogError("conflict", f"stale catalog generation: expected {expected_generation}, found {generation}")
        entries = catalog["entries"]
        # A retry after a crash immediately after atomic replacement returns the
        # already-published entry instead of allocating a duplicate revision.
        for entry in entries:
            if (entry.get("logical_id") == identity["logical_id"]
                    and catalog["snapshots"].get(entry.get("snapshot_id")) == {"commit": commit, "path": source_path}
                    and entry.get("item_id") == item_id and entry.get("profile") == profile
                    and entry.get("digests") == digests
                    and (revision is None or entry.get("revision") == revision)):
                return entry
        prior_revisions = []
        for entry in entries:
            try:
                parsed = parse_reference(entry.get("reference"))
            except (ReferenceError, TypeError):
                raise CatalogError("invalid_catalog", "existing catalog entry has malformed reference")
            if parsed["logical_id"] == identity["logical_id"]:
                prior_revisions.append(parsed["revision"])
        next_revision = max(prior_revisions, default=0) + 1
        if revision is not None:
            if type(revision) is not int or revision != next_revision:
                raise CatalogError("immutable", "revision is already published or is not the next numeric revision")
            next_revision = revision
        reference = f"{identity['logical_id']}@{next_revision}"
        snapshot_bytes = json.dumps({"commit": commit, "path": source_path}, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")
        snapshot_id = hashlib.sha256(snapshot_bytes).hexdigest()
        snapshots = dict(catalog.get("snapshots", {}))
        snapshots[snapshot_id] = {"commit": commit, "path": source_path}
        entry = {
            "reference": reference,
            "logical_id": identity["logical_id"],
            "revision": next_revision,
            "snapshot_id": snapshot_id,
            "item_id": item_id,
            "profile": profile,
            "digest_algorithm": "sha256",
            "digests": digests,
            "digest_semantics": sorted(digests),
            "generation": generation + 1,
        }
        catalog["entries"] = [*entries, entry]
        catalog["snapshots"] = snapshots
        catalog["generation"] = generation + 1
        _publish_catalog(path, owner, root, _common, relative, catalog, old_ref)
        if after_publish is not None:
            after_publish()
        return entry
    finally:
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


def resolve_version(catalog_path, reference, repository_root=None):
    try:
        parsed = parse_reference(reference)
    except ReferenceError as exc:
        raise CatalogError(exc.code, str(exc)) from exc
    path = Path(catalog_path)
    # Owner is encoded in the qualified reference. Resolution never consults
    # HEAD or the checkout; it reads only the entry's exact commit/path.
    root = Path(repository_root).resolve() if repository_root is not None else _repo_info(path)[0]
    _root, _common, relative = _repo_info(path)
    stream = _lock(path)
    try:
        _recover_pending(path, parsed["owner"], root, relative)
        catalog, _ref_value_current = _trusted_catalog(path, parsed["owner"], root, relative)
    finally:
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()
    if catalog is None:
        raise CatalogError("missing_authority", "trusted catalog is not registered")
    matches = [entry for entry in catalog["entries"] if entry.get("reference") == parsed["canonical"]]
    if len(matches) != 1:
        raise CatalogError("missing", f"catalog has no unique entry for {parsed['canonical']}")
    entry = matches[0]
    if entry.get("digest_algorithm") != "sha256" or not isinstance(entry.get("digests"), dict):
        raise CatalogError("invalid_entry", "entry has no supported full digest authority")
    snapshot_id = entry.get("snapshot_id")
    snapshot = catalog.get("snapshots", {}).get(snapshot_id)
    if not isinstance(snapshot, dict):
        raise CatalogError("invalid_entry", "entry has no shared immutable snapshot")
    commit, source_path = _safe_snapshot(snapshot)
    _validate_commit(root, commit)
    try:
        result = subprocess.run(["git", "show", f"{commit}:{source_path}"], cwd=root,
                                check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CatalogError("missing", "pinned Git source is unavailable") from exc
    raw = result.stdout
    semantics = entry.get("digest_semantics")
    if not isinstance(semantics, list) or not semantics or any(
            name not in {"canonical-json/1", "exact-bytes/1"} for name in semantics):
        raise CatalogError("unsupported", "catalog entry has unsupported digest semantics")
    verified_digests = {}
    for semantics_name in semantics:
        expected = entry["digests"].get(semantics_name)
        actual = payload_digests(raw, semantics=semantics_name)
        if not isinstance(expected, str) or actual[semantics_name] != expected:
            raise CatalogError("integrity_mismatch", f"pinned source failed {semantics_name} verification")
        verified_digests.update(actual)
    return {"entry": entry, "payload": raw, "digests": verified_digests}
