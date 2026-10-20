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
            source_inputs.append({"path": source_path, "text": verified_contents[source_path]})
            transcript_parts.append(f"Source ({source_path}):\n{verified_contents[source_path]}")
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
