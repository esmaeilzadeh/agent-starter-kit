"""Git-retained, content-addressed snapshots of coordinator state and evidence."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile


SCHEMA = "ask-inner-loop-checkpoint/v1"
REF_PREFIX = "refs/ask/inner-loop/"


class CheckpointError(RuntimeError):
    pass


def is_repository(root: Path) -> bool:
    proc = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=root,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc.returncode == 0


def _git(root: Path, *args: str, input: bytes | None = None) -> bytes:
    proc = subprocess.run(["git", *args], cwd=root, input=input, capture_output=True)
    if proc.returncode:
        detail = proc.stderr.decode("utf-8", "replace").strip()
        raise CheckpointError(detail or f"git {' '.join(args)} failed")
    return proc.stdout


def _ref(work_id: str) -> str:
    if not work_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for c in work_id):
        raise CheckpointError("invalid checkpoint work_id")
    return REF_PREFIX + work_id


def _safe_path(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise CheckpointError(f"unsafe checkpoint path: {name}")
    if "\n" in name or "\0" in name or "\t" in name:
        raise CheckpointError(f"unsafe checkpoint path: {name}")
    return name


def _destination(root: Path, name: str) -> Path:
    root = Path(root).resolve()
    relative = Path(*_safe_path(name).split("/"))
    destination = root / relative
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise CheckpointError(f"refusing path through symlink: {name}")
    if not destination.resolve(strict=False).is_relative_to(root):
        raise CheckpointError(f"checkpoint path escapes repository: {name}")
    return destination


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=".checkpoint-",
                                         suffix=".tmp", delete=False) as stream:
            temp_name = stream.name
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)


def _commit_exists(root: Path, sha: str) -> bool:
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        return False
    proc = subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=root,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc.returncode == 0


def _resolve_ref(root: Path, work_id: str) -> str | None:
    proc = subprocess.run(["git", "rev-parse", "--verify", _ref(work_id)], cwd=root,
                          capture_output=True, text=True)
    if proc.returncode:
        return None
    sha = proc.stdout.strip()
    if not _commit_exists(root, sha):
        raise CheckpointError("checkpoint ref does not point to a commit")
    return sha


def _blob(root: Path, content: bytes) -> str:
    return _git(root, "hash-object", "-w", "--stdin", input=content).decode().strip()


def _tree(root: Path, files: dict[str, str]) -> str:
    """Create nested Git trees without touching the caller's index."""
    nodes: dict[str, dict] = {}
    for path, sha in files.items():
        parts = _safe_path(path).split("/")
        node = nodes
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = sha

    def write(node: dict) -> str:
        rows = []
        for name, child in sorted(node.items()):
            if isinstance(child, dict):
                sha = write(child)
                rows.append(f"040000 tree {sha}\t{name}\n")
            else:
                rows.append(f"100644 blob {child}\t{name}\n")
        return _git(root, "mktree", input="".join(rows).encode()).decode().strip()

    return write(nodes)


def _read_tree(root: Path, commit: str) -> tuple[dict, dict[str, bytes]]:
    if not _commit_exists(root, commit):
        raise CheckpointError("checkpoint target is missing or is not a commit")
    raw = _git(root, "ls-tree", "-r", "-z", "--full-tree", commit)
    files: dict[str, bytes] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        header, name_raw = record.split(b"\t", 1)
        mode, kind, sha = header.decode().split()
        try:
            name = _safe_path(name_raw.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise CheckpointError("checkpoint path is not valid UTF-8") from exc
        if mode != "100644" or kind != "blob":
            raise CheckpointError(f"unsupported checkpoint tree entry: {name}")
        files[name] = _git(root, "cat-file", "blob", sha)
    try:
        manifest = json.loads(files["checkpoint.json"])
    except (KeyError, ValueError) as exc:
        raise CheckpointError("checkpoint manifest is missing or invalid") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise CheckpointError("unsupported checkpoint schema")
    if not isinstance(manifest.get("work_id"), str):
        raise CheckpointError("checkpoint work_id is invalid")
    return manifest, files


def _runtime_files(root: Path, work_id: str) -> dict[str, bytes]:
    base = root / "work" / work_id
    files: dict[str, bytes] = {}
    for directory in (base / "inner-loop", base / "traceability"):
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise CheckpointError(f"refusing symlink in checkpoint evidence: {path.relative_to(root)}")
            if path.is_file() and path.name != "state.lock" and not path.name.endswith(".tmp"):
                name = _safe_path(path.relative_to(root).as_posix())
                files[name] = path.read_bytes()
    return files


def _required_commits(root: Path, work_id: str, state: dict) -> list[str]:
    commits: set[str] = set()
    for sha in [state.get("coordinator_sha", ""), *[
        task.get("base_sha", "") for task in (state.get("tasks") or {}).values()
    ]]:
        if sha:
            if not _commit_exists(root, sha):
                raise CheckpointError(f"required checkpoint commit is missing: {sha}")
            commits.add(sha)
    for task in (state.get("tasks") or {}).values():
        for attempt in task.get("attempt_history") or []:
            sha = attempt.get("interrupted_candidate_sha", "")
            if sha:
                if not _commit_exists(root, sha):
                    raise CheckpointError(f"required interrupted candidate commit is missing: {sha}")
                commits.add(sha)
    pin = root / "work" / work_id / "traceability-accepted.json"
    if pin.is_file():
        try:
            sha = json.loads(pin.read_text(encoding="utf-8")).get("contract_sha", "")
        except (OSError, ValueError):
            sha = ""
        if sha:
            if not _commit_exists(root, sha):
                raise CheckpointError(f"accepted contract commit is missing: {sha}")
            commits.add(sha)
    # TaskResults, review records, and run reports may name source and authority
    # commits. Preserve only fields with known commit identity semantics.
    for name, raw in _runtime_files(root, work_id).items():
        if not name.endswith(".json"):
            continue
        try:
            doc = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(doc, dict):
            continue
        failed_static_receipt = (
            name == f"work/{work_id}/traceability/static-{doc.get('candidate_sha')}.json"
            and doc.get("result") == "fail"
        )
        for key in ("base_sha", "candidate_sha", "interrupted_candidate_sha", "source_sha", "authority_sha", "runner_sha",
                    "contract_sha", "accepted_tests_sha", "red_sha", "green_sha"):
            sha = doc.get(key)
            if isinstance(sha, str) and sha:
                # Failed static receipts are diagnostic evidence only. Keep
                # their exact bytes in the checkpoint, but do not require an
                # ephemeral failed candidate to remain in the source closure.
                if key == "candidate_sha" and failed_static_receipt:
                    continue
                if not _commit_exists(root, sha):
                    raise CheckpointError(f"required checkpoint commit is missing: {sha}")
                commits.add(sha)
    return sorted(commits)


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant],
                          cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def publish(root: Path, work_id: str, state: dict) -> str:
    """Publish a complete snapshot using the ref as the transaction commit point.

    Caller must hold the work state's lock. The ref compare-and-swap happens
    before the runtime cache replacement.
    """
    root = Path(root).resolve()
    if not is_repository(root):
        raise CheckpointError("checkpointing requires a Git worktree or repository")
    ref = _ref(work_id)
    previous = _resolve_ref(root, work_id)
    runtime = _runtime_files(root, work_id)
    state_bytes = (json.dumps(state, indent=2) + "\n").encode()
    runtime[f"work/{work_id}/inner-loop/state.json"] = state_bytes
    artifact_entries = {}
    objects = {}
    for name, content in sorted(runtime.items()):
        _safe_path(name)
        sha = _blob(root, content)
        path = "artifacts/" + name
        objects[path] = sha
        artifact_entries[name] = {"path": path, "blob": sha,
                                  "sha256": hashlib.sha256(content).hexdigest(),
                                  "size": len(content)}
    required = _required_commits(root, work_id, state)
    manifest = {
        "schema": SCHEMA,
        "work_id": work_id,
        "generation": int(state.get("revision", 0)),
        "previous_checkpoint": previous,
        "coordinator_sha": state.get("coordinator_sha", ""),
        "accepted_contract_sha": _contract_sha(root, work_id),
        "retained_commits": required,
        "artifacts": artifact_entries,
        "state_path": f"artifacts/work/{work_id}/inner-loop/state.json",
    }
    manifest_raw = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    objects["checkpoint.json"] = _blob(root, manifest_raw)
    tree = _tree(root, objects)
    parents = []
    if previous:
        parents.append(previous)
    for sha in required:
        if previous and _is_ancestor(root, sha, previous):
            continue
        if sha not in parents:
            parents.append(sha)
    args = ["commit-tree", tree]
    for parent in parents:
        args.extend(("-p", parent))
    commit = _git(root, *args, input=b"coordinator checkpoint\n").decode().strip()
    if os.environ.get("ASK_INNER_LOOP_CRASH_AT") == "before_ref_publication":
        os._exit(75)
    zero = "0" * len(commit)
    # update-ref is an atomic CAS even when refs.lock contention occurs.
    _git(root, "update-ref", ref, commit, previous or zero)
    if os.environ.get("ASK_INNER_LOOP_CRASH_AT") == "after_ref_publication":
        os._exit(76)
    return commit


def _contract_sha(root: Path, work_id: str) -> str:
    pin = root / "work" / work_id / "traceability-accepted.json"
    if not pin.is_file():
        return ""
    try:
        value = json.loads(pin.read_text(encoding="utf-8")).get("contract_sha", "")
    except (OSError, ValueError):
        return ""
    return value if isinstance(value, str) else ""


def read_checkpoint(root: Path, work_id: str, commit: str | None = None) -> tuple[str, dict, dict[str, bytes]] | None:
    if commit is None:
        commit = _resolve_ref(Path(root), work_id)
    if not commit:
        return None
    manifest, files = _read_tree(Path(root), commit)
    if manifest.get("work_id") != work_id:
        raise CheckpointError("checkpoint work_id mismatch")
    artifact_map = manifest.get("artifacts")
    if not isinstance(artifact_map, dict):
        raise CheckpointError("invalid checkpoint artifacts map")
    for name, entry in artifact_map.items():
        if not isinstance(entry, dict):
            raise CheckpointError(f"invalid checkpoint artifact record: {name}")
        _safe_path(name)
        artifact_path = entry.get("path")
        blob = entry.get("blob")
        digest = entry.get("sha256")
        size = entry.get("size")
        if (not isinstance(artifact_path, str) or not isinstance(blob, str)
                or not isinstance(digest, str) or not isinstance(size, int) or size < 0):
            raise CheckpointError(f"invalid checkpoint artifact metadata: {name}")
        path = _safe_path(artifact_path)
        content = files.get(path)
        if (content is None or hashlib.sha256(content).hexdigest() != entry.get("sha256")
                or len(content) != size or _blob_id(root, content) != blob):
            raise CheckpointError(f"checkpoint artifact is missing or has a bad digest: {name}")
        if _blob_type(root, blob) != "blob":
            raise CheckpointError(f"checkpoint artifact object is invalid: {name}")
    for sha in manifest.get("retained_commits", []):
        if (not _commit_exists(Path(root), sha)
                or not _is_ancestor(Path(root), sha, commit)):
            raise CheckpointError(f"checkpoint commit closure is incomplete: {sha}")
    state_path = _safe_path(manifest.get("state_path", ""))
    try:
        state = json.loads(files[state_path])
    except (KeyError, ValueError) as exc:
        raise CheckpointError("checkpoint has no valid state snapshot") from exc
    generation = manifest.get("generation")
    if not isinstance(state, dict) or not isinstance(generation, int):
        raise CheckpointError("checkpoint state or generation has an invalid type")
    try:
        state_generation = int(state.get("revision", -1))
    except (TypeError, ValueError) as exc:
        raise CheckpointError("checkpoint state revision is invalid") from exc
    if state.get("work_id") != work_id or state_generation != generation:
        raise CheckpointError("checkpoint state does not match its generation")
    previous = manifest.get("previous_checkpoint")
    if previous is not None:
        if not isinstance(previous, str) or not _commit_exists(Path(root), previous):
            raise CheckpointError("previous checkpoint is missing or invalid")
        parents = _git(Path(root), "rev-list", "--parents", "-n", "1", commit).decode().split()[1:]
        if not parents or parents[0] != previous:
            raise CheckpointError("checkpoint chain does not match its first parent")
    retained = manifest.get("retained_commits", [])
    if not isinstance(retained, list) or any(not isinstance(sha, str) for sha in retained):
        raise CheckpointError("invalid retained commit list")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise CheckpointError("invalid checkpoint artifacts map")
    return commit, state, files


def is_checkpoint_state_ancestor(root: Path, work_id: str, state: dict,
                                 checkpoint_sha: str) -> bool:
    """Return whether an exact cached state appears in this checkpoint's history."""
    seen: set[str] = set()
    cursor = checkpoint_sha
    while cursor:
        if cursor in seen:
            raise CheckpointError("checkpoint history contains a cycle")
        seen.add(cursor)
        manifest, files = _read_tree(Path(root), cursor)
        if manifest.get("work_id") != work_id:
            raise CheckpointError("checkpoint history work_id mismatch")
        try:
            historical = json.loads(files[manifest["state_path"]])
        except (KeyError, ValueError, TypeError) as exc:
            raise CheckpointError("checkpoint history has no valid state snapshot") from exc
        if historical == state:
            return True
        cursor = manifest.get("previous_checkpoint")
        if cursor is not None and (not isinstance(cursor, str) or not cursor):
            raise CheckpointError("checkpoint history pointer is invalid")
    return False


def _blob_type(root: Path, sha: str) -> str:
    if len(sha) != 40:
        return ""
    proc = subprocess.run(["git", "cat-file", "-t", sha], cwd=root, capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _blob_id(root: Path, content: bytes) -> str:
    return _git(root, "hash-object", "--stdin", input=content).decode().strip()


def restore_cache(root: Path, work_id: str, cached: dict | None = None) -> dict | None:
    """Restore missing or exact-ancestor cache; reject unexplained newer state."""
    checkpoint = read_checkpoint(root, work_id)
    if checkpoint is None:
        return None
    _commit, current, files = checkpoint
    manifest, _ = _read_tree(Path(root), checkpoint[0])
    if cached is not None and cached == current:
        return current
    if cached is not None and int(cached.get("revision", -1)) >= int(current.get("revision", -1)):
        # Preserve unexplained same/newer cache bytes for the normal recovery
        # inspector, which can report all conflicting task evidence together.
        return cached
    if cached is not None:
        # Older cache is replayable only if it exactly matches an earlier
        # checkpoint in this chain. Revision numbers alone are not authority.
        previous = manifest.get("previous_checkpoint")
        matched = False
        while previous:
            prior_manifest, prior_files = _read_tree(Path(root), previous)
            try:
                prior = json.loads(prior_files[prior_manifest["state_path"]])
            except (KeyError, ValueError):
                raise CheckpointError("previous checkpoint has invalid state")
            if prior == cached:
                matched = True
                break
            previous = prior_manifest.get("previous_checkpoint")
        if not matched and int(cached.get("revision", -1)) >= int(current.get("revision", -1)):
            raise CheckpointError("runtime cache is newer or divergent from checkpoint")
        if not matched:
            raise CheckpointError("runtime cache does not match checkpoint history")
    artifacts_to_restore = []
    state_snapshot_path = _safe_path(manifest.get("state_path", ""))
    state_artifact_name = state_snapshot_path.removeprefix("artifacts/")
    for name, entry in (manifest.get("artifacts") or {}).items():
        if not isinstance(entry, dict):
            raise CheckpointError(f"invalid checkpoint artifact record: {name}")
        destination = _destination(root, name)
        content = files[_safe_path(entry["path"])]
        if name != state_artifact_name and destination.exists():
            if destination.is_symlink() or not destination.is_file() or destination.read_bytes() != content:
                raise CheckpointError(f"runtime evidence conflicts with checkpoint: {name}")
        artifacts_to_restore.append((destination, content))
    state_path = _destination(root, f"work/{work_id}/inner-loop/state.json")
    for destination, content in artifacts_to_restore:
        if destination == state_path:
            continue
        if not destination.exists() or destination.read_bytes() != content:
            _atomic_write(destination, content)
    _atomic_write(state_path, (json.dumps(current, indent=2) + "\n").encode())
    return current


def export_bundle(root: Path, work_id: str, destination: Path) -> None:
    checkpoint = read_checkpoint(root, work_id)
    if checkpoint is None:
        raise CheckpointError("no checkpoint is available for export")
    _git(Path(root), "bundle", "create", str(destination), _ref(work_id))


def import_bundle(root: Path, work_id: str, source: Path) -> str:
    root = Path(root).resolve()
    _git(root, "bundle", "verify", str(source))
    ref = _ref(work_id)
    with tempfile.TemporaryDirectory(prefix="ask-checkpoint-") as temp:
        quarantine = f"refs/ask/quarantine/{work_id}"
        fetched = _git(root, "fetch", str(source), f"{ref}:{quarantine}")
        del fetched
        candidate = _git(root, "rev-parse", quarantine).decode().strip()
        try:
            read_checkpoint(root, work_id, candidate)
            current = _resolve_ref(root, work_id)
            if current and not _is_ancestor(root, current, candidate):
                raise CheckpointError("imported checkpoint diverges from current checkpoint")
            _git(root, "update-ref", ref, candidate, current or "0" * len(candidate))
        finally:
            subprocess.run(["git", "update-ref", "-d", quarantine], cwd=root,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return candidate
