"""Explicit legacy mapping and authority-preserving reference bundles."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

from .identity import ReferenceError, parse_reference
from .store import (CatalogError, _lock, _publish_catalog, _read_catalog_bytes,
                    _recover_pending, _repo_info, _ref, _ref_value,
                    _trusted_catalog, initialize_catalog, register_revision,
                    resolve_version)


def _git(root, *args, check=True):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True)
    if check and result.returncode:
        raise CatalogError("git_error", result.stderr.decode(errors="replace").strip())
    return result


def _validate_owner(owner):
    try:
        parsed = parse_reference(f"{owner}/review/1@1")
    except (TypeError, ReferenceError) as exc:
        raise CatalogError(getattr(exc, "code", "invalid_owner"), "owner must be a canonical lowercase slug") from exc
    if parsed["owner"] != owner:
        raise CatalogError("invalid_owner", "owner must be a canonical lowercase slug")


def migrate(repository_root, owner):
    """Register only mappings explicitly declared against immutable sources.

    The declaration is ``work/<owner>/references/migration.json`` and uses
    ``ask-reference-migration/v1``. Original source files are never rewritten.
    """
    root = Path(repository_root).resolve()
    _validate_owner(owner)
    declaration = root / "work" / owner / "references" / "migration.json"
    try:
        value = json.loads(declaration.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError("migration_missing", "explicit migration declaration is unavailable") from exc
    if (not isinstance(value, dict) or value.get("schema") != "ask-reference-migration/v1"
            or value.get("owner") != owner or not isinstance(value.get("mappings"), list)):
        raise CatalogError("unsupported", "migration declaration schema or owner is unsupported")
    catalog_path = root / "work" / owner / "references" / "integrity.json"
    initialize_catalog(catalog_path, owner)
    outcomes = []
    seen_legacy = set()
    for mapping in value["mappings"]:
        required = {"legacy_reference", "logical_id", "snapshot", "item_id", "profile"}
        if not isinstance(mapping, dict) or required - set(mapping):
            raise CatalogError("unsupported", "migration mapping lacks explicit source/item declarations")
        legacy = mapping["legacy_reference"]
        if not isinstance(legacy, str) or not legacy.strip() or legacy in seen_legacy:
            raise CatalogError("ambiguous", "legacy references must be unique non-empty strings")
        seen_legacy.add(legacy)
        snapshot = mapping["snapshot"]
        if not isinstance(snapshot, dict) or set(snapshot) != {"commit", "path"}:
            raise CatalogError("missing_source", f"mapping {legacy!r} lacks an exact commit/path")
        try:
            identity = parse_reference(mapping["logical_id"] + "@1")
        except (TypeError, ReferenceError) as exc:
            raise CatalogError(getattr(exc, "code", "malformed"), "migration target is not qualified") from exc
        if identity["owner"] != owner:
            raise CatalogError("owner_mismatch", "migration target belongs to another owner")
        raw = _git(root, "show", f"{snapshot['commit']}:{snapshot['path']}").stdout
        declared = mapping.get("source_sha256")
        actual = hashlib.sha256(raw).hexdigest()
        if declared is not None and declared != actual:
            raise CatalogError("integrity_mismatch", f"legacy source digest differs for {legacy!r}")
        entry = register_revision(catalog_path, owner, identity["logical_id"], snapshot,
                                  mapping["item_id"], mapping["profile"], raw,
                                  revision=mapping.get("revision"))
        target = entry["reference"]
        stream = _lock(catalog_path)
        try:
            _root, common, relative = _repo_info(catalog_path)
            _recover_pending(catalog_path, owner, root, relative)
            catalog, old_ref = _trusted_catalog(catalog_path, owner, root, relative)
            if catalog is None or old_ref is None:
                raise CatalogError("missing_authority", "migration catalog has no trusted authority")
            mappings = dict(catalog.get("legacy_mappings", {}))
            previous = mappings.get(legacy)
            provenance = {"reference": target, "source_commit": snapshot["commit"],
                          "source_path": snapshot["path"], "item_id": mapping["item_id"],
                          "profile": mapping["profile"], "source_sha256": actual}
            if previous is not None and previous != provenance:
                raise CatalogError("conflict", f"legacy mapping {legacy!r} is immutable")
            if previous is None:
                mappings[legacy] = provenance
                catalog["legacy_mappings"] = mappings
                catalog["generation"] += 1
                _publish_catalog(catalog_path, owner, root, common, relative, catalog, old_ref)
        finally:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            stream.close()
        resolve_version(catalog_path, target, root)
        outcomes.append({"legacy_reference": legacy, "reference": target,
                         "source_sha256": actual})
    return {"status": "migrated", "owner": owner, "mappings": outcomes}


def export_bundle(repository_root, owner, output_path):
    """Export a trusted owner catalog and the Git object closure it names."""
    root = Path(repository_root).resolve()
    _validate_owner(owner)
    catalog_path = root / ("results/references/integrity.json" if owner == "repository-runs"
                           else f"work/{owner}/references/integrity.json")
    _root, _common, relative = _repo_info(catalog_path)
    stream = _lock(catalog_path)
    try:
        _recover_pending(catalog_path, owner, root, relative)
        catalog, authority = _trusted_catalog(catalog_path, owner, root, relative)
    finally:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()
    if catalog is None or authority is None:
        raise CatalogError("missing_authority", "cannot export an unregistered catalog")
    ref = _ref(owner)
    authority_bytes = _git(root, "show", f"{authority}:{relative}").stdout
    if authority_bytes != catalog_path.read_bytes():
        raise CatalogError("integrity_mismatch", "working catalog differs from trusted authority")
    with tempfile.TemporaryDirectory(prefix="ask-refs-export-") as temp:
        bundle = Path(temp) / "objects.bundle"
        _git(root, "bundle", "create", str(bundle), ref)
        manifest = {"schema": "ask-reference-bundle/v1", "owner": owner,
                    "authority_ref": ref, "authority_commit": authority,
                    "catalog_sha256": hashlib.sha256(authority_bytes).hexdigest(),
                    "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest()}
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("manifest.json", json.dumps(manifest, sort_keys=True) + "\n")
                archive.writestr("catalog.json", authority_bytes)
                archive.write(bundle, "objects.bundle")
            os.replace(temporary, target)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return {"status": "exported", "owner": owner, "authority_commit": authority,
            "catalog_sha256": manifest["catalog_sha256"], "bundle_sha256": manifest["bundle_sha256"]}


def import_bundle(repository_root, bundle_path):
    """Validate a bundle against already trusted local authority; never bootstrap it."""
    root, archive_path = Path(repository_root).resolve(), Path(bundle_path)
    try:
        with zipfile.ZipFile(archive_path) as archive:
            if set(archive.namelist()) != {"manifest.json", "catalog.json", "objects.bundle"}:
                raise CatalogError("unsupported", "reference bundle has unexpected or missing members")
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            catalog_bytes = archive.read("catalog.json")
            bundle_bytes = archive.read("objects.bundle")
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError("invalid_bundle", "reference bundle is invalid") from exc
    if (not isinstance(manifest, dict) or manifest.get("schema") != "ask-reference-bundle/v1"
            or hashlib.sha256(catalog_bytes).hexdigest() != manifest.get("catalog_sha256")
            or hashlib.sha256(bundle_bytes).hexdigest() != manifest.get("bundle_sha256")):
        raise CatalogError("integrity_mismatch", "bundle payload does not match its manifest")
    owner, ref = manifest.get("owner"), manifest.get("authority_ref")
    _validate_owner(owner)
    if ref != _ref(owner):
        raise CatalogError("invalid_bundle", "bundle authority ref does not match its owner")
    catalog = _read_catalog_bytes(catalog_bytes, owner)
    with tempfile.TemporaryDirectory(prefix="ask-refs-import-") as temp:
        bundle = Path(temp) / "objects.bundle"
        bundle.write_bytes(bundle_bytes)
        _git(root, "bundle", "verify", str(bundle))
        heads = _git(root, "bundle", "list-heads", str(bundle)).stdout.decode().splitlines()
        declared = {line.split()[1]: line.split()[0] for line in heads if len(line.split()) == 2}
        if declared != {ref: manifest.get("authority_commit")}:
            raise CatalogError("invalid_bundle", "bundle does not contain the declared authority ref")
    if _ref_value(root, ref) != manifest.get("authority_commit"):
        raise CatalogError("missing_authority", "bundle cannot establish or replace local catalog authority")
    trusted = _git(root, "show", f"{manifest['authority_commit']}:{'results/references/integrity.json' if owner == 'repository-runs' else f'work/{owner}/references/integrity.json'}").stdout
    if trusted != catalog_bytes:
        raise CatalogError("integrity_mismatch", "bundle catalog differs from trusted local authority")
    for entry in catalog["entries"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("reference"), str):
            raise CatalogError("invalid_catalog", "bundle contains a malformed catalog entry")
        resolve_version(root / ("results/references/integrity.json" if owner == "repository-runs"
                                else f"work/{owner}/references/integrity.json"), entry["reference"], root)
    # An exact retry is intentionally a no-op; conflicting authority is refused.
    return {"status": "imported", "owner": owner, "authority_commit": manifest["authority_commit"],
            "entries_verified": len(catalog["entries"]), "idempotent": True}
