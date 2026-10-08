"""Local validated-generation admission. Semantic mutations are a later layer.

Only the pointer replacement publishes. Generation payloads are complete before
that replacement; interrupted unpublished generations are harmless. Readers
never reread mutable source files to construct the published document.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import MappingProxyType

from .snapshot import Snapshot, capture, is_current, safe_relative
from .validation import RULES_VERSION


def _state_directory(root, work_id):
    root = Path(root).resolve()
    state = root / "work" / work_id / "traceability" / "model-state"
    for ancestor in (state, *state.parents):
        if ancestor == root:
            break
        if ancestor.is_symlink():
            raise OSError("model-state directory cannot use symlink ancestors")
    return state


@contextmanager
def _writer(state):
    state.mkdir(parents=True, exist_ok=True)
    with (state / "writer.lock").open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def _durable_write(path, raw):
    with path.open("wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish(state, snapshot, root):
    identity = snapshot.identity
    digest = identity["digest"]
    generations = state / "generations"
    generations.mkdir(exist_ok=True)
    destination = generations / digest
    if not destination.exists():
        staged = Path(tempfile.mkdtemp(prefix="unpublished-", dir=generations))
        blobs = staged / "blobs"
        blobs.mkdir()
        for raw in snapshot.files.values():
            if raw is not None:
                _durable_write(blobs / hashlib.sha256(raw).hexdigest(), raw)
        manifest = {"schema": "ask-engineering-generation/v1", "work_id": snapshot.work_id,
                    "snapshot": identity}
        _durable_write(staged / "manifest.json", json.dumps(manifest, sort_keys=True).encode())
        _sync_directory(blobs)
        _sync_directory(staged)
        os.replace(staged, destination)
        _sync_directory(generations)
    # Staging may take time. Recheck after it and immediately before publishing.
    if not is_current(snapshot, root):
        return False
    descriptor, temporary = tempfile.mkstemp(prefix="pointer-", dir=state)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(json.dumps({"generation": digest}, sort_keys=True).encode())
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, state / "current.json")
    _sync_directory(state)
    return True


def load_published(root, work_id):
    """Load and verify every byte from one pointer-selected generation."""
    state = _state_directory(root, work_id)
    try:
        pointer = json.loads((state / "current.json").read_bytes())
    except FileNotFoundError:
        return None
    digest = pointer.get("generation") if isinstance(pointer, dict) else None
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("invalid published generation pointer")
    generation = state / "generations" / digest
    manifest = json.loads((generation / "manifest.json").read_bytes())
    if manifest.get("schema") != "ask-engineering-generation/v1" or manifest.get("work_id") != work_id:
        raise ValueError("invalid generation manifest")
    identity = manifest["snapshot"]
    if identity["rules_version"] != RULES_VERSION:
        raise ValueError("published generation uses an older validator rule version")
    model_path = f"work/{work_id}/engineering-model.json"
    records = [{**identity["model"], "status": "present"}, *identity["inputs"]]
    files, statuses = {}, {}
    for record in records:
        path, status = record["path"], record["status"]
        if not safe_relative(path) or path in files:
            raise ValueError("invalid generation input path")
        raw = None
        if status == "present":
            blob_digest = record["sha256"]
            if not isinstance(blob_digest, str) or len(blob_digest) != 64 or any(c not in "0123456789abcdef" for c in blob_digest):
                raise ValueError("invalid generation blob identity")
            raw = (generation / "blobs" / blob_digest).read_bytes()
            if hashlib.sha256(raw).hexdigest() != blob_digest:
                raise ValueError("published generation bytes have changed")
        files[path], statuses[path] = raw, status
    if files.get(model_path) is None:
        raise ValueError("generation has no model")
    snapshot = Snapshot(work_id, MappingProxyType(files), MappingProxyType(statuses))
    if snapshot.identity != identity or identity["digest"] != digest:
        raise ValueError("published generation identity has changed")
    return snapshot


def validate_current(root, work_id):
    """Capture, validate captured bytes, and refuse a changed dependency set."""
    snapshot = None
    try:
        snapshot = capture(root, work_id)
        diagnostics = snapshot.diagnostics(root)
        if not is_current(snapshot, root):
            diagnostics.append({"code": "EM007_INPUT_CHANGED", "path": snapshot.model_path,
                                "message": "model or referenced inputs changed during validation"})
    except (OSError, UnicodeError, ValueError) as exc:
        diagnostics = [{"code": "EM001_MODEL_READ" if isinstance(exc, OSError) else "EM001_JSON",
                        "path": f"work/{work_id}/engineering-model.json", "message": str(exc)}]
    return snapshot, diagnostics


def admit(root, work_id, expected=None):
    """Bootstrap/read admission; does not authorize or execute workflow actions."""
    snapshot, diagnostics = validate_current(root, work_id)
    if not diagnostics and expected is not None and snapshot.identity["digest"] != expected:
        diagnostics = [{"code": "EM007_STALE_INPUT", "path": snapshot.model_path,
                        "message": "expected snapshot is no longer current"}]
    if not diagnostics:
        try:
            state = _state_directory(root, work_id)
            with _writer(state):
                if not _publish(state, snapshot, root):
                    diagnostics = [{"code": "EM007_INPUT_CHANGED", "path": snapshot.model_path,
                                    "message": "inputs changed before publication"}]
        except (OSError, ValueError) as exc:
            diagnostics = [{"code": "EM007_PUBLICATION", "path": snapshot.model_path, "message": str(exc)}]
    return snapshot, diagnostics
