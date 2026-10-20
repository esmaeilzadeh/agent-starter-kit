"""Reproduce the frozen legacy workflow-reference benchmark."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

import tiktoken


WORK_ID = "shorter-hashes"
MANIFEST_PATH = f"work/{WORK_ID}/benchmark/baseline.json"
REQUIREMENTS_PATH = f"work/{WORK_ID}/benchmark/requirements.txt"
EXPECTED_MANIFEST_SHA256 = "e492b8773bb58fccfccab38f123565a499a423cc3d46becf7f7b6d8f440be29f"
EXPECTED_REQUIREMENTS_SHA256 = "ac785205f5d97970c4a7f8aef135c62cfda01985ba2000973008c823ccc01d2f"
EXPECTED_BASELINE_SOURCE = "9a3d25d035baafc23508f242020d46fae7ff5b14"
EXPECTED_TOKENIZER = {
    "package": "tiktoken",
    "version": "0.12.0",
    "encoding": "cl100k_base",
    "operation": "encode_ordinary",
    "text_encoding": "utf-8",
}


class BenchmarkError(ValueError):
    """The frozen benchmark inputs are incomplete or no longer comparable."""


def _git_blob(root: Path, revision: str, path: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "show", f"{revision}:{path}"],
            cwd=root,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BenchmarkError(f"missing frozen Git input {revision}:{path}") from exc
    return result.stdout


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_json(path: Path, label: str) -> tuple[dict, bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"missing or invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise BenchmarkError(f"invalid {label}: expected a JSON object")
    return value, raw


def _safe_source_path(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise BenchmarkError("frozen source path is missing")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        raise BenchmarkError(f"unsafe frozen source path: {value!r}")
    return value


def _tokenizer(manifest: dict):
    declared = manifest.get("tokenizer")
    if not isinstance(declared, dict):
        raise BenchmarkError("frozen tokenizer declaration is missing")
    actual = {key: declared.get(key) for key in EXPECTED_TOKENIZER}
    if actual != EXPECTED_TOKENIZER:
        raise BenchmarkError("frozen tokenizer declaration differs from the sealed tokenizer")
    try:
        installed = importlib.metadata.version("tiktoken")
    except importlib.metadata.PackageNotFoundError as exc:
        raise BenchmarkError("pinned tiktoken package is not installed") from exc
    if installed != EXPECTED_TOKENIZER["version"]:
        raise BenchmarkError(
            f"wrong tiktoken version: expected {EXPECTED_TOKENIZER['version']}, found {installed}"
        )
    try:
        encoding = tiktoken.get_encoding(EXPECTED_TOKENIZER["encoding"])
        if not callable(getattr(encoding, "encode_ordinary", None)):
            raise BenchmarkError("pinned tokenizer has no encode_ordinary operation")
    except (KeyError, ValueError) as exc:
        raise BenchmarkError("pinned tiktoken encoding is unavailable") from exc
    return encoding


def _verify_contract_files(root: Path, manifest_bytes: bytes) -> None:
    if _sha256(manifest_bytes) != EXPECTED_MANIFEST_SHA256:
        raise BenchmarkError("frozen workload manifest changed after independent review")
    requirements_path = root / REQUIREMENTS_PATH
    try:
        requirements = requirements_path.read_bytes()
    except OSError as exc:
        raise BenchmarkError("pinned tokenizer requirements are missing") from exc
    if _sha256(requirements) != EXPECTED_REQUIREMENTS_SHA256:
        raise BenchmarkError("pinned tokenizer requirements changed after independent review")


def _json_text(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def _first_task_row(text: str, task_id: str) -> str:
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines)
                  if line.startswith("| " + task_id + " |")), None)
    if start is None:
        raise BenchmarkError(f"frozen plan is missing first task row {task_id}")
    end = next((index for index in range(start + 1, len(lines))
                if lines[index].startswith("| ") and not lines[index].startswith("|   ")), len(lines))
    return "\n".join(lines[start:end]) + "\n"


def _first_yaml_task(text: str, task_id: str) -> str:
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines)
                  if line == f"  - id: {task_id}"), None)
    if start is None:
        raise BenchmarkError(f"frozen task graph is missing first task {task_id}")
    end = next((index for index in range(start + 1, len(lines))
                if lines[index].startswith("  - id: ")), len(lines))
    return "\n".join(lines[:3] + lines[start:end]) + "\n"


def _test_plan_projection(value: dict) -> dict:
    scopes = value.get("task_scopes")
    tests = value.get("tests")
    if not isinstance(scopes, list) or not scopes or not isinstance(scopes[0], dict) or not isinstance(tests, list):
        raise BenchmarkError("frozen test plan has no first task scope")
    scope = scopes[0]
    ids = scope.get("test_ids")
    if not isinstance(ids, list) or not all(isinstance(item, str) for item in ids):
        raise BenchmarkError("frozen first task scope has invalid test IDs")
    selected = [case for case in tests if case.get("id") in ids]
    if len(selected) != len(ids):
        raise BenchmarkError("frozen first task scope references missing tests")
    criterion_ids = {criterion for case in selected for criterion in case.get("criterion_ids", [])}
    obligations = value.get("obligations", [])
    runners = value.get("runners", [])
    runner_ids = {case.get("runner_id") for case in selected}
    projected = {
        key: value[key] for key in ("schema", "work_id", "spec_digest") if key in value
    }
    projected.update({
        "task_scopes": [scope],
        "tests": selected,
        "obligations": [row for row in obligations if row.get("criterion_id") in criterion_ids],
        "runners": [row for row in runners if row.get("id") in runner_ids],
    })
    if "task_scoped_baseline_regression_exemptions" in value:
        exemptions = value["task_scoped_baseline_regression_exemptions"]
        if isinstance(exemptions, dict) and scope.get("task_id") in exemptions:
            projected["task_scoped_baseline_regression_exemptions"] = {
                scope["task_id"]: exemptions[scope["task_id"]]
            }
    return projected


def _projection_for_path(journey_id: str, source_path: str, text: str, source_contents: dict[str, str]) -> str:
    """Return the frozen agent-visible projection while corpus verification stays whole-file."""
    if source_path.endswith("test-plan.json") and journey_id in {"resume", "review"}:
        value = json.loads(text)
        projection = _test_plan_projection(value)
        return _json_text(projection)
    if journey_id == "review" and source_path.endswith("structured-agentic-environment.json"):
        value = json.loads(text)
        test_plan_path = "work/structured-agentic-environment/test-plan.json"
        scope = _test_plan_projection(json.loads(source_contents[test_plan_path]))
        criteria = {criterion for case in scope["tests"] for criterion in case.get("criterion_ids", [])}
        value["criteria"] = [row for row in value.get("criteria", []) if row.get("id") in criteria]
        return _json_text(value)
    if journey_id == "review" and source_path.endswith("tasks.yaml"):
        return _first_yaml_task(text, "WB-001")
    if source_path.endswith("plan.md") and journey_id == "resume":
        task_row = _first_task_row(text, "stage-inference")
        parts = []
        for heading in ("## Specification", "## Approach"):
            start = text.find(heading)
            if start >= 0:
                end = text.find("\n## ", start + len(heading))
                parts.append(text[start:] if end < 0 else text[start:end])
        parts.append("## First task row\n" + task_row)
        return "\n\n".join(parts) + "\n"
    if source_path.endswith("plan.md") and journey_id == "review":
        authority_start = text.find("## Status and authority")
        authority_end = text.find("\n## ", authority_start + 1)
        authority = text[authority_start:authority_end] if authority_start >= 0 and authority_end >= 0 else ""
        specification_start = text.find("## Specification")
        specification_end = text.find("\n## ", specification_start + 1)
        specification = text[specification_start:specification_end] if specification_start >= 0 and specification_end >= 0 else ""
        return authority + "\n\n" + specification + "\n\n## First task row\n" + _first_task_row(text, "WB-001")
    if source_path.endswith(".json"):
        try:
            return _json_text(json.loads(text))
        except json.JSONDecodeError as exc:
            raise BenchmarkError(f"invalid frozen JSON input: {source_path}") from exc
    return text


def capture_baseline(root, manifest_path=None):
    """Capture exact legacy inputs, tokenizer counts, and unique metadata bytes.

    The manifest and requirements must match the independent plan review. Every
    source comes from its frozen Git commit and is checked before it contributes
    to a transcript or byte total.
    """
    root = Path(root).resolve()
    path = Path(manifest_path) if manifest_path is not None else root / MANIFEST_PATH
    manifest, manifest_bytes = _read_json(path, "baseline manifest")
    _verify_contract_files(root, manifest_bytes)

    if manifest.get("schema") != "ask-reference-benchmark/v1":
        raise BenchmarkError("unsupported frozen benchmark manifest")
    if manifest.get("baseline_source") != EXPECTED_BASELINE_SOURCE:
        raise BenchmarkError("frozen baseline source changed")
    encoding = _tokenizer(manifest)
    workload = manifest.get("workload_version")
    if workload != "references-journeys/1":
        raise BenchmarkError("frozen workload version changed")

    try:
        files = manifest["files"]
        journeys = manifest["journeys"]
    except KeyError as exc:
        raise BenchmarkError("frozen manifest is missing files or journeys") from exc
    if not isinstance(files, list) or not isinstance(journeys, list) or not journeys:
        raise BenchmarkError("frozen manifest has invalid files or journeys")

    file_table = {}
    verified_contents = {}
    for record in files:
        if not isinstance(record, dict):
            raise BenchmarkError("frozen file record is invalid")
        source_path = _safe_source_path(record.get("path"))
        if source_path in file_table:
            raise BenchmarkError(f"duplicate frozen source path: {source_path}")
        expected_digest = record.get("sha256")
        expected_bytes = record.get("bytes")
        if (not isinstance(expected_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_digest)
                or isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes < 0
                or not isinstance(record.get("metadata"), bool)):
            raise BenchmarkError(f"invalid integrity record for {source_path}")
        content = _git_blob(root, EXPECTED_BASELINE_SOURCE, source_path)
        if len(content) != expected_bytes or _sha256(content) != expected_digest:
            raise BenchmarkError(f"frozen source integrity mismatch: {source_path}")
        try:
            text = content.decode(EXPECTED_TOKENIZER["text_encoding"])
        except UnicodeDecodeError as exc:
            raise BenchmarkError(f"frozen source is not UTF-8: {source_path}") from exc
        file_table[source_path] = record
        verified_contents[source_path] = text

    seen_journeys = set()
    used_files = set()
    measured_journeys = []
    total_tokens = 0
    metadata_files = set()
    for journey in journeys:
        if not isinstance(journey, dict):
            raise BenchmarkError("frozen journey is invalid")
        journey_id = journey.get("id")
        question = journey.get("question")
        source_paths = journey.get("source_paths")
        if (not isinstance(journey_id, str) or not journey_id or journey_id in seen_journeys
                or not isinstance(question, str) or not question
                or not isinstance(source_paths, list) or not source_paths):
            raise BenchmarkError("frozen journey is missing an ID, question, or source paths")
        seen_journeys.add(journey_id)
        source_inputs = []
        transcript_parts = [f"Question:\n{question}"]
        journey_metadata = set()
        for value in source_paths:
            source_path = _safe_source_path(value)
            if source_path not in file_table:
                raise BenchmarkError(f"journey references missing frozen source: {source_path}")
            used_files.add(source_path)
            projected_text = _projection_for_path(
                journey_id, source_path, verified_contents[source_path], verified_contents
            )
            source_inputs.append({"path": source_path, "text": projected_text})
            transcript_parts.append(f"Source ({source_path}):\n{projected_text}")
            if file_table[source_path]["metadata"]:
                journey_metadata.add(source_path)
                metadata_files.add(source_path)
        transcript = "\n\n".join(transcript_parts)
        token_count = len(encoding.encode_ordinary(transcript))
        total_tokens += token_count
        measured_journeys.append({
            "id": journey_id,
            "question": question,
            "baseline_projection": journey.get("baseline_projection", ""),
            "projection_serialization": journey.get("projection_serialization", ""),
            "source_inputs": source_inputs,
            "transcript": transcript,
            "input_tokens": token_count,
            "metadata_files": sorted(journey_metadata),
            "metadata_bytes": sum(file_table[item]["bytes"] for item in journey_metadata),
        })

    if used_files != set(file_table):
        missing = sorted(set(file_table) - used_files)
        raise BenchmarkError(f"frozen corpus contains unassigned files: {', '.join(missing)}")
    return {
        "schema": "ask-reference-benchmark/v1",
        "baseline_source": EXPECTED_BASELINE_SOURCE,
        "tokenizer": dict(EXPECTED_TOKENIZER),
        "workload_version": workload,
        "source_files": files,
        "journeys": measured_journeys,
        "total_input_tokens": total_tokens,
        "metadata_files": sorted(metadata_files),
        "unique_metadata_bytes": sum(file_table[item]["bytes"] for item in metadata_files),
    }
