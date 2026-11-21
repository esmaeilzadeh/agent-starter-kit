"""Git-retained, content-addressed snapshots of coordinator state and evidence."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile


SCHEMA = "ask-inner-loop-checkpoint/v1"
STATE_SCHEMA = "ask-inner-loop-state/v1"
REF_PREFIX = "refs/ask/inner-loop/"
REFERENCE_PREFIX = "refs/ask/references/"
ENVELOPE_SCHEMA = "ask-workflow-envelope/v1"
RECORDS_PATH = "inner-loop/integrity-records.json"


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
    state_bytes, integrity_authority, integrity_generation = _compact_state(root, work_id, state)
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
    if integrity_authority:
        if not _commit_exists(root, integrity_authority):
            raise CheckpointError("trusted workflow reference catalog commit is unavailable")
        required = sorted(set(required) | {integrity_authority})
    manifest = {
        "schema": SCHEMA,
        "work_id": work_id,
        "generation": int(state.get("revision", 0)),
        "previous_checkpoint": previous,
        "coordinator_sha": state.get("coordinator_sha", ""),
        "accepted_contract_sha": _contract_sha(root, work_id),
        "integrity_authority": integrity_authority,
        "integrity_generation": integrity_generation,
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
        state = _resolve_state(Path(root), work_id, files[state_path], commit, manifest)
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
            historical = _resolve_state(Path(root), work_id,
                                        files[manifest["state_path"]], cursor, manifest)
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


def _workflow_refs(root: Path):
    package_root = str(Path(root) / ".agents" / "ask")
    if package_root not in sys.path:
        sys.path.insert(0, package_root)
    from workflow_refs import codec, identity, store
    return codec, identity, store


def _numeric(value: str) -> bool:
    return bool(re.fullmatch(r"[1-9][0-9]*", value))


def _run_rows(task: dict) -> list[dict]:
    rows = []
    current = (task.get("evidence") or {}).get("traceability_runs") or []
    for run in current:
        if isinstance(run, dict):
            rows.append({"attempt": "current", "run": run})
    for index, attempt in enumerate(task.get("attempt_history") or [], start=1):
        evidence = (attempt.get("evidence") or {}) if isinstance(attempt, dict) else {}
        for run in evidence.get("traceability_runs") or []:
            if isinstance(run, dict):
                rows.append({"attempt": index, "run": run})
    return rows


def _state_items(state: dict) -> tuple[list[dict], dict[str, str]]:
    """Build stable structured task/test items using only declared evidence fields."""
    items: list[dict] = []
    logical_ids: dict[str, str] = {}
    work_id = state.get("work_id")
    for task_id, task in sorted((state.get("tasks") or {}).items()):
        if not _numeric(str(task_id)) or not isinstance(task, dict):
            continue
        task_num = int(task_id)
        task_item = f"task-{task_id}"
        items.append({"id": task_item, "value": task})
        key = f"task:{task_id}"
        logical_ids[key] = f"{work_id}/spec/1/plan/1/task/{task_num}"
        by_test: dict[str, list[dict]] = {}
        for row in _run_rows(task):
            run = row["run"]
            for test_id in run.get("test_ids") or []:
                if not isinstance(test_id, str):
                    continue
                parts = test_id.split("/")
                if (len(parts) != 2 or parts[0] != str(task_id)
                        or not _numeric(parts[0]) or not _numeric(parts[1])):
                    continue
                by_test.setdefault(test_id, []).append(row)
        for test_id, rows in sorted(by_test.items()):
            _task, test_num = test_id.split("/")
            test_item = "test-" + test_id.replace("/", "-")
            items.append({"id": test_item, "value": {
                "task_id": str(task_id), "test_id": test_id, "runs": rows,
            }})
            logical_ids[f"test:{test_id}"] = (
                f"{work_id}/spec/1/plan/1/task/{task_num}/test/{int(test_num)}"
            )
    return items, logical_ids


def _commit_record_source(root: Path, work_id: str, items: list[dict]) -> tuple[str, str, bytes]:
    source_path = f"work/{work_id}/{RECORDS_PATH}"
    content = (json.dumps({"schema": "ask-inner-loop-records/v1", "items": items},
                          ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    blob = _blob(root, content)
    tree = _tree(root, {source_path: blob})
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    commit = _git(root, "commit-tree", tree, "-p", head,
                  input=b"Retain immutable inner-loop workflow records\n").decode().strip()
    return commit, source_path, content


def _catalog_state_refs(root: Path, work_id: str, state: dict) -> tuple[dict[str, str], str | None, int | None]:
    items, logical_ids = _state_items(state)
    if not items:
        return {}, None, None
    codec, _identity, store = _workflow_refs(root)
    catalog_path = root / "work" / work_id / "references" / "integrity.json"
    try:
        catalog = store.initialize_catalog(catalog_path, work_id)
        source_commit, source_path, content = _commit_record_source(root, work_id, items)
        refs = {}
        generation = catalog["generation"]
        for item in items:
            # Item IDs are mapped by stable logical identity, not by searching prose.
            key = next((name for name, logical in logical_ids.items()
                        if ((name.startswith("task:") and item["id"] == "task-" + name[5:])
                            or (name.startswith("test:") and item["id"] == "test-" + name[5:].replace("/", "-")))), None)
            if key is None:
                raise CheckpointError("inner-loop catalog item has no numeric reference")
            entry = store.register_revision(
                catalog_path, work_id, logical_ids[key],
                {"commit": source_commit, "path": source_path}, item["id"],
                "structured-item/1", content, expected_generation=generation,
            )
            catalog = store.initialize_catalog(catalog_path, work_id)
            generation = catalog["generation"]
            refs[key] = entry["reference"]
        authority = _git(root, "rev-parse", "--verify", REFERENCE_PREFIX + work_id).decode().strip()
        return refs, authority, generation
    except (store.CatalogError, OSError, ValueError) as exc:
        raise CheckpointError(f"cannot publish trusted inner-loop references: {exc}") from exc


def _compact_state(root: Path, work_id: str, state: dict) -> tuple[bytes, str | None, int | None]:
    items, _logical = _state_items(state)
    if not items:
        return (json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(), None, None
    refs, authority, generation = _catalog_state_refs(root, work_id, state)
    payload = json.loads(json.dumps(state, ensure_ascii=False, allow_nan=False))
    payload["tasks"] = {task_id: task for task_id, task in (state.get("tasks") or {}).items()
                         if f"task:{task_id}" not in refs}
    codec, identity, _store = _workflow_refs(root)
    references = dict(refs)
    context = {"owner": work_id, "type": "task", "spec": 1, "plan": 1}
    try:
        envelope = codec.encode_envelope(payload, STATE_SCHEMA, context, references)
        return (json.dumps(envelope, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(), authority, generation
    except (codec.EnvelopeError, identity.ReferenceError, ValueError) as exc:
        raise CheckpointError(f"cannot encode compact inner-loop state: {exc}") from exc


def _resolve_state(root: Path, work_id: str, raw: bytes, checkpoint_sha: str,
                   manifest: dict) -> dict:
    try:
        stored = json.loads(raw)
    except (UnicodeDecodeError, ValueError) as exc:
        raise CheckpointError("checkpoint has no valid state snapshot") from exc
    if not isinstance(stored, dict) or stored.get("schema") != ENVELOPE_SCHEMA:
        return stored
    authority = manifest.get("integrity_authority")
    if (not isinstance(authority, str) or not _commit_exists(root, authority)
            or not _is_ancestor(root, authority, checkpoint_sha)):
        raise CheckpointError("compact checkpoint has no retained catalog authority")
    current_authority = subprocess.run(
        ["git", "rev-parse", "--verify", REFERENCE_PREFIX + work_id],
        cwd=root, capture_output=True, text=True,
    )
    if current_authority.returncode:
        raise CheckpointError("trusted workflow reference catalog is unavailable")
    if not _is_ancestor(root, authority, current_authority.stdout.strip()):
        raise CheckpointError("trusted workflow reference catalog diverges from checkpoint authority")
    try:
        pinned = json.loads(_git(root, "show", f"{authority}:work/{work_id}/references/integrity.json"))
    except (CheckpointError, ValueError) as exc:
        raise CheckpointError("checkpoint authority has no valid integrity catalog") from exc
    if (not isinstance(pinned, dict) or pinned.get("schema") != "ask-reference-catalog/v1"
            or pinned.get("owner") != work_id
            or pinned.get("generation") != manifest.get("integrity_generation")
            or not isinstance(pinned.get("entries"), list)):
        raise CheckpointError("checkpoint integrity catalog generation or owner is invalid")
    codec, identity, store = _workflow_refs(root)
    try:
        normalized = codec.normalize_envelope(stored)
        context = normalized["context"]
        if (context != {"owner": work_id, "type": "task", "spec": 1, "plan": 1}
                or normalized["schema"] != STATE_SCHEMA):
            raise CheckpointError("compact checkpoint context does not match its owner")
        state = normalized["payload"]
        if not isinstance(state, dict) or state.get("work_id") != work_id:
            raise CheckpointError("compact checkpoint payload has an invalid owner")
        tasks = dict(state.get("tasks") or {})
        resolved_tasks: dict[str, dict] = {}
        test_refs = []
        for name, reference in normalized["references"].items():
            parsed = identity.parse_reference(reference)
            if parsed["owner"] != work_id or parsed["ids"][:2] != (1, 1):
                raise CheckpointError("compact checkpoint contains a foreign or mis-parented reference")
            if not any(isinstance(entry, dict) and entry.get("reference") == reference
                       for entry in pinned["entries"]):
                raise CheckpointError("checkpoint reference was not present in its pinned catalog generation")
            if name.startswith("task:"):
                task_id = str(parsed["ids"][2]) if parsed["kind"] == "task" and len(parsed["ids"]) == 3 else ""
                if task_id != name[5:] or task_id in resolved_tasks:
                    raise CheckpointError("compact task reference key does not match its identity")
                result = store.resolve_version(root / "work" / work_id / "references" / "integrity.json",
                                               reference, repository_root=root)
                entry = result["entry"]
                document = json.loads(result["payload"])
                matches = [item for item in document.get("items", [])
                           if isinstance(item, dict) and item.get("id") == entry.get("item_id")]
                if len(matches) != 1 or entry.get("item_id") != "task-" + task_id:
                    raise CheckpointError("catalog task item does not match its numeric reference")
                value = matches[0].get("value")
                if not isinstance(value, dict):
                    raise CheckpointError("catalog task value is invalid")
                resolved_tasks[task_id] = value
            elif name.startswith("test:"):
                if parsed["kind"] != "test" or len(parsed["ids"]) != 4:
                    raise CheckpointError("compact test reference has invalid type or parents")
                expected_id = f"{parsed['ids'][2]}/{parsed['ids'][3]}"
                if name != "test:" + expected_id:
                    raise CheckpointError("compact test reference key does not match its identity")
                test_refs.append((reference, expected_id, parsed["ids"][2]))
            else:
                raise CheckpointError("compact checkpoint contains an unsupported reference kind")
        for reference, test_id, task_num in test_refs:
            if str(task_num) not in resolved_tasks:
                raise CheckpointError("catalog test reference has no matching task record")
            result = store.resolve_version(root / "work" / work_id / "references" / "integrity.json",
                                           reference, repository_root=root)
            entry = result["entry"]
            document = json.loads(result["payload"])
            matches = [item for item in document.get("items", [])
                       if isinstance(item, dict) and item.get("id") == entry.get("item_id")]
            expected_rows = [row for row in _run_rows(resolved_tasks[str(task_num)])
                             if test_id in (row["run"].get("test_ids") or [])]
            expected_value = {"task_id": str(task_num), "test_id": test_id,
                              "runs": expected_rows}
            if (len(matches) != 1 or entry.get("item_id") != "test-" + test_id.replace("/", "-")
                    or matches[0].get("value") != expected_value):
                raise CheckpointError("catalog test item does not match its numeric reference")
        tasks.update(resolved_tasks)
        state["tasks"] = tasks
        return state
    except (store.CatalogError, codec.EnvelopeError, identity.ReferenceError,
            OSError, ValueError, KeyError, TypeError) as exc:
        if isinstance(exc, CheckpointError):
            raise
        raise CheckpointError(f"compact checkpoint reference resolution failed: {exc}") from exc


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
                prior = _resolve_state(Path(root), work_id,
                                       prior_files[prior_manifest["state_path"]],
                                       previous, prior_manifest)
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
    refs = [_ref(work_id)]
    catalog_ref = REFERENCE_PREFIX + work_id
    if subprocess.run(["git", "show-ref", "--verify", "--quiet", catalog_ref],
                      cwd=root).returncode == 0:
        refs.append(catalog_ref)
    _git(Path(root), "bundle", "create", str(destination), *refs)


def import_bundle(root: Path, work_id: str, source: Path) -> str:
    root = Path(root).resolve()
    _git(root, "bundle", "verify", str(source))
    ref = _ref(work_id)
    catalog_ref = REFERENCE_PREFIX + work_id
    checkpoint_quarantine = f"refs/ask/quarantine/{work_id}-checkpoint"
    catalog_quarantine = f"refs/ask/quarantine/{work_id}-catalog"
    with tempfile.TemporaryDirectory(prefix="ask-checkpoint-") as temp:
        heads = _git(root, "bundle", "list-heads", str(source)).decode().splitlines()
        available_refs = {line.split()[-1] for line in heads if len(line.split()) >= 2}
        fetch_args = ["fetch", str(source), f"{ref}:{checkpoint_quarantine}"]
        has_catalog = catalog_ref in available_refs
        if has_catalog:
            fetch_args.append(f"{catalog_ref}:{catalog_quarantine}")
        _git(root, *fetch_args)
        candidate = _git(root, "rev-parse", checkpoint_quarantine).decode().strip()
        current_catalog = subprocess.run(["git", "rev-parse", "--verify", catalog_ref],
                                         cwd=root, capture_output=True, text=True)
        old_catalog = current_catalog.stdout.strip() if current_catalog.returncode == 0 else None
        imported_catalog = (_git(root, "rev-parse", catalog_quarantine).decode().strip()
                            if has_catalog else None)
        catalog_changed = False
        try:
            if imported_catalog:
                manifest, _files = _read_tree(root, candidate)
                expected_authority = manifest.get("integrity_authority")
                if (not isinstance(expected_authority, str)
                        or not _is_ancestor(root, expected_authority, imported_catalog)):
                    raise CheckpointError("bundle catalog ref does not contain checkpoint authority")
                if old_catalog and not (_is_ancestor(root, old_catalog, imported_catalog)
                                        or _is_ancestor(root, imported_catalog, old_catalog)):
                    raise CheckpointError("imported workflow catalog diverges from local authority")
                if not old_catalog or _is_ancestor(root, old_catalog, imported_catalog):
                    _git(root, "update-ref", catalog_ref, imported_catalog,
                         old_catalog or "0" * len(imported_catalog))
                    catalog_changed = True
            elif _read_tree(root, candidate)[0].get("integrity_authority"):
                raise CheckpointError("bundle omits the trusted workflow catalog ref")
            read_checkpoint(root, work_id, candidate)
            current = _resolve_ref(root, work_id)
            if current and not _is_ancestor(root, current, candidate):
                raise CheckpointError("imported checkpoint diverges from current checkpoint")
            _git(root, "update-ref", ref, candidate, current or "0" * len(candidate))
        except Exception:
            if catalog_changed:
                if old_catalog:
                    _git(root, "update-ref", catalog_ref, old_catalog, imported_catalog)
                else:
                    subprocess.run(["git", "update-ref", "-d", catalog_ref, imported_catalog],
                                   cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            raise
        finally:
            subprocess.run(["git", "update-ref", "-d", checkpoint_quarantine], cwd=root,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "update-ref", "-d", catalog_quarantine], cwd=root,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return candidate
