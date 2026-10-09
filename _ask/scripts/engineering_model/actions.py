"""Single-writer staged document actions and recoverable working-file projection.

The generation pointer is the authority, not independent working-file renames.
A durable journal permits forward recovery without executing an action twice.
Conflicting external writes are preserved and block admission.
"""
import base64
import ctypes
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .admission import (_durable_write, _publish, _state_directory, _sync_directory,
                        _writer, load_published, validate_current)
from .snapshot import capture, is_current, read_input, safe_relative
from .domain import apply_batch


class Refused(ValueError):
    def __init__(self, code, message, path="$"):
        super().__init__(message)
        self.diagnostic = {"code": code, "message": message, "path": path}


def _encoded(raw):
    return base64.b64encode(raw).decode() if raw is not None else None


def _decoded(value):
    return base64.b64decode(value, validate=True) if value is not None else None


def _signature(status, raw):
    return {"status": status, "sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None}


_UNSET = object()
_AT_FDCWD = -100
_RENAME_NOREPLACE = 1
_RENAME_EXCHANGE = 2


def _renameat2(source, target, flags):
    renameat2 = ctypes.CDLL(None, use_errno=True).renameat2
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    if renameat2(_AT_FDCWD, os.fsencode(source), _AT_FDCWD, os.fsencode(target), flags) != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(target))


def _write_target(root, relative, raw, *, expected=_UNSET):
    if not safe_relative(relative):
        raise Refused("EM007_UNSAFE_CHANGE", "unsafe change path", relative)
    path = root / relative
    for parent in (path, *path.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise Refused("EM007_UNSAFE_CHANGE", "managed changes cannot replace symlink paths", relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    if expected is _UNSET:
        status, expected = read_input(root, relative)
        if status not in {"present", "missing"}:
            raise Refused("EM007_RECOVERY_CONFLICT", "change target cannot be safely compared", relative)
    accepted = expected if isinstance(expected, tuple) else (expected,)
    replacement = raw if raw is not None else b""
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise Refused("EM007_UNSAFE_CHANGE", "managed target must be a regular file", relative)
    descriptor, staged = tempfile.mkstemp(prefix=".ask-document-", dir=path.parent)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(replacement)
        stream.flush()
        os.fsync(stream.fileno())
    if not path.exists():
        if raw is None:
            Path(staged).unlink(missing_ok=True)
            return
        if None not in accepted:
            Path(staged).unlink(missing_ok=True)
            raise Refused("EM007_RECOVERY_CONFLICT", "change target disappeared before publication", relative)
        try:
            _renameat2(staged, path, _RENAME_NOREPLACE)
        except FileExistsError as exc:
            Path(staged).unlink(missing_ok=True)
            raise Refused("EM007_RECOVERY_CONFLICT", "external save appeared before publication", relative) from exc
    else:
        try:
            _renameat2(staged, path, _RENAME_EXCHANGE)
        except OSError as exc:
            Path(staged).unlink(missing_ok=True)
            raise Refused("EM007_RECOVERY_CONFLICT", "change target changed or cannot be atomically compared", relative) from exc
        displaced = Path(staged).read_bytes()
        if displaced not in accepted:
            try:
                if path.read_bytes() == replacement:
                    _renameat2(staged, path, _RENAME_EXCHANGE)
                    Path(staged).unlink(missing_ok=True)
                else:
                    raise OSError("destination changed again during conflict recovery")
            except OSError as exc:
                raise Refused("EM007_RECOVERY_CONFLICT",
                              f"external save preserved; displaced bytes retained at {staged}: {exc}", relative) from exc
            raise Refused("EM007_RECOVERY_CONFLICT", "external save raced with managed publication", relative)
        if raw is None:
            path.unlink()
        Path(staged).unlink(missing_ok=True)
    _sync_directory(path.parent)


def _clear_journal(state):
    (state / "pending.json").unlink()
    _sync_directory(state)


def _observe(root, snapshot, changes, candidate):
    observations = {path: _signature(snapshot.statuses[path], raw)
                    for path, raw in snapshot.files.items() if path not in changes}
    for path, raw in candidate.files.items():
        if path not in changes:
            observations[path] = _signature(candidate.statuses[path], raw)
    return observations


def _observations_current(root, observations):
    return all(_signature(*read_input(root, path)) == signature
               for path, signature in observations.items())


def _rollback(root, journal):
    """Restore only our known bytes; never overwrite a conflicting external save."""
    conflicts = []
    for path, record in journal["changes"].items():
        status, current = read_input(root, path)
        before, after = _decoded(record["before"]), _decoded(record["after"])
        if current == after and status in ("present", "missing"):
            _write_target(root, path, before, expected=after)
        elif current != before or status not in ("present", "missing"):
            conflicts.append(path)
    return conflicts


def recover_locked(root, work_id, state, *, validated=None):
    """Resume a journal under the writer lock; no semantic action is re-invoked."""
    path = state / "pending.json"
    if not path.exists():
        return
    try:
        journal = json.loads(path.read_bytes())
        if journal.get("schema") != "ask-document-transaction/v1" or journal.get("work_id") != work_id:
            raise ValueError("invalid document transaction journal")
        published = load_published(root, work_id)
        pointer = published.identity["digest"] if published is not None else None
        if pointer == journal["result_digest"]:
            _clear_journal(state)
            return
        if pointer != journal["base_generation"]:
            raise Refused("EM007_RECOVERY_CONFLICT", "published generation changed during interrupted action")
        if not _observations_current(root, journal["observations"]):
            conflicts = _rollback(root, journal)
            if not conflicts:
                _clear_journal(state)
            raise Refused("EM007_RECOVERY_CONFLICT", "external input changed during interrupted action")
        for relative, record in journal["changes"].items():
            status, raw = read_input(root, relative)
            before, after = _decoded(record["before"]), _decoded(record["after"])
            if status not in ("present", "missing") or raw not in (before, after):
                raise Refused("EM007_RECOVERY_CONFLICT", "external save conflicts with interrupted action", relative)
        for relative, record in journal["changes"].items():
            before, after = _decoded(record["before"]), _decoded(record["after"])
            _write_target(root, relative, _decoded(record["after"]),
                          expected=(before, after))
        if validated is None:
            candidate, errors = validate_current(root, work_id, allow_pending=True)
        else:
            candidate, errors = validated, []
            if not is_current(candidate, root):
                errors = [{"code": "EM007_INPUT_CHANGED"}]
        if errors or candidate.identity["digest"] != journal["result_digest"]:
            conflicts = _rollback(root, journal)
            if not conflicts:
                _clear_journal(state)
            raise Refused("EM007_RECOVERY_CONFLICT", "interrupted candidate is no longer valid/current")
        if not _publish(state, candidate, root, guarded_base=journal["base_digest"]):
            raise Refused("EM007_RECOVERY_CONFLICT", "inputs changed during recovery publication")
        _clear_journal(state)
    except (KeyError, TypeError, UnicodeError, ValueError) as exc:
        if isinstance(exc, Refused):
            raise
        raise Refused("EM007_RECOVERY_CONFLICT", str(exc)) from exc


def run_action(root, work_id, expected, action):
    """Call action once on validated captured bytes; publish only its valid result.

    action returns a map of repository-relative document paths to bytes (or None
    for deletion). It must stage proposals, not mutate repository files itself.
    """
    root = Path(root).resolve()
    steps, base, candidate = [], None, None
    diagnostics = []
    try:
        state = _state_directory(root, work_id)
        with _writer(state):
            recover_locked(root, work_id, state)
            steps.append("pre")
            base, diagnostics = validate_current(root, work_id)
            if diagnostics:
                return _result(base, None, diagnostics, steps)
            if base.identity["digest"] != expected:
                raise Refused("EM007_STALE_INPUT", "displayed input snapshot is no longer current")
            published = load_published(root, work_id)
            generation = published.identity["digest"] if published is not None else None
            steps.append("action")
            changes = action(base)
            if not isinstance(changes, dict) or not changes:
                raise Refused("EM002_ACTION", "action must propose a nonempty document change batch")
            originals = {}
            for path, raw in changes.items():
                if not safe_relative(path) or (raw is not None and not isinstance(raw, bytes)):
                    raise Refused("EM002_ACTION", "changes require safe relative paths and byte payloads")
                status, original = read_input(root, path)
                if status not in ("present", "missing"):
                    raise Refused("EM007_UNSAFE_CHANGE", "change target cannot be safely read", path)
                originals[path] = original
            steps.append("post")
            candidate = capture(root, work_id, overrides=changes)
            diagnostics = candidate.diagnostics(root)
            if diagnostics:
                return _result(base, candidate, diagnostics, steps)
            if any(path not in base.files and path not in candidate.files for path in changes):
                raise Refused("EM002_ACTION", "change is outside the definition/reference closure")
            observations = _observe(root, base, changes, candidate)
            if not is_current(base, root) or not _observations_current(root, observations):
                raise Refused("EM007_INPUT_CHANGED", "inputs changed while the action was staged")
            journal = {
                "schema": "ask-document-transaction/v1", "work_id": work_id,
                "base_generation": generation, "base_digest": base.identity["digest"],
                "result_digest": candidate.identity["digest"], "observations": observations,
                "changes": {path: {"before": _encoded(originals[path]), "after": _encoded(raw)}
                            for path, raw in changes.items()},
            }
            _durable_write(state / "pending.json", json.dumps(journal, sort_keys=True).encode())
            _sync_directory(state)
            # Recovery applies the staged bytes, validates again, and moves the
            # single publication pointer. It never calls action again.
            recover_locked(root, work_id, state, validated=candidate)
            steps.append("publication")
    except Refused as exc:
        diagnostics = [exc.diagnostic]
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        diagnostics = [{"code": "EM002_ACTION", "path": "$", "message": str(exc)}]
    return _result(base, candidate, diagnostics, steps)


def _result(base, candidate, diagnostics, steps):
    return {"schema": "ask-engineering-action/v1", "valid": not diagnostics,
            "diagnostics": diagnostics, "steps": steps,
            "validation_counts": {"pre": steps.count("pre"), "post": steps.count("post")},
            "input_snapshot": base.identity if base is not None else None,
            "snapshot": candidate.identity if candidate is not None else None}


def edit(root, work_id, expected, proposal):
    """Guard a semantic batch plus coordinated canonical document changes.

    A callable proposal loader is opened only after pre-validation, so even
    parsing/action invocation cannot precede admission.
    """
    def action(snapshot):
        batch = proposal() if callable(proposal) else proposal
        if not isinstance(batch, dict) or set(batch) - {"commands", "files"}:
            raise Refused("EM002_ACTION", "batch supports only commands and files")
        files, commands = batch.get("files", {}), batch.get("commands", [])
        if not isinstance(files, dict) or (not files and not commands):
            raise Refused("EM002_ACTION", "batch must contain semantic commands or document changes")
        allowed = {f"specs/current/{work_id}.json", f"specs/current/{work_id}.md", f"work/{work_id}/test-plan.json"}
        if not set(files) <= allowed:
            raise Refused("EM002_ACTION", "file changes must target the selected workstream's canonical documents")
        changes = {}
        for path, text in files.items():
            if text is not None and not isinstance(text, str):
                raise Refused("EM002_ACTION", "file payload must be text or null", path)
            changes[path] = text.encode("utf-8") if text is not None else None
        changed_references = {
            path for path, payload in changes.items()
            if snapshot.files.get(path) != payload
        }
        result = apply_batch(snapshot.document, commands, changed_references=changed_references)
        if not result["valid"]:
            diagnostic = result["diagnostics"][0]
            raise Refused(diagnostic["code"], diagnostic["message"], diagnostic["path"])
        changes[snapshot.model_path] = json.dumps(result["model"], ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n"
        return changes
    return run_action(root, work_id, expected, action)
