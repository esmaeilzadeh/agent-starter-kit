"""Lossless compact workflow envelope encoding."""
from __future__ import annotations

import json
from copy import deepcopy

from .identity import ReferenceError, parse_reference


class EnvelopeError(ValueError):
    """An envelope has unsupported schema, context, or typed references."""


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _validate_context(context):
    if not isinstance(context, dict) or not isinstance(context.get("type"), str):
        raise EnvelopeError("missing_context: envelope requires owner and record type")
    try:
        parse_reference({"id": 1, "revision": 1}, context)
    except ReferenceError as exc:
        raise EnvelopeError(f"{exc.code}: {exc}") from exc
    return {key: value for key, value in context.items()}


def _reference_form(reference, context):
    try:
        parsed = parse_reference(reference)
    except ReferenceError as exc:
        raise EnvelopeError(f"{exc.code}: {exc}") from exc
    if (parsed["owner"] == context["owner"] and parsed["kind"] == context["type"]):
        parent_keys = {"part": ("spec",), "plan": ("spec",),
                       "item": ("spec", "plan"), "task": ("spec", "plan"),
                       "test": ("spec", "plan", "task")}
        keys = parent_keys.get(parsed["kind"], ())
        parents = parsed["ids"][:-1]
        if len(keys) == len(parents) and all(context.get(key) == value for key, value in zip(keys, parents)):
            return {"id": parsed["ids"][-1], "revision": parsed["revision"]}
    return parsed["canonical"]


def encode_envelope(payload, payload_schema, context, references=None):
    if not isinstance(payload_schema, str) or not payload_schema.strip():
        raise EnvelopeError("invalid_payload_schema")
    context = _validate_context(context)
    if not isinstance(references or {}, dict):
        raise EnvelopeError("references must be an object")
    try:
        payload = json.loads(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise EnvelopeError("payload must contain only JSON values") from exc
    encoded_refs = {}
    for name, reference in (references or {}).items():
        if not isinstance(name, str) or not name:
            raise EnvelopeError("reference names must be non-empty strings")
        encoded_refs[name] = _reference_form(reference, context)
    return {
        "schema": "ask-workflow-envelope/v1",
        "payload_schema": payload_schema,
        "context": context,
        "payload": payload,
        "references": encoded_refs,
    }


def decode_envelope(encoded):
    try:
        if isinstance(encoded, str):
            envelope = json.loads(encoded, object_pairs_hook=_pairs)
        elif isinstance(encoded, dict):
            envelope = json.loads(json.dumps(encoded, ensure_ascii=False, allow_nan=False), object_pairs_hook=_pairs)
        else:
            raise EnvelopeError("envelope must be an object or JSON text")
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        if isinstance(exc, EnvelopeError):
            raise
        raise EnvelopeError(f"invalid envelope JSON: {exc}") from exc
    if not isinstance(envelope, dict) or envelope.get("schema") != "ask-workflow-envelope/v1":
        raise EnvelopeError("unsupported envelope schema")
    if (not isinstance(envelope.get("payload_schema"), str) or "payload" not in envelope
            or not isinstance(envelope.get("references"), dict)):
        raise EnvelopeError("envelope requires payload schema, payload, and references")
    context = _validate_context(envelope.get("context"))
    envelope["context"] = context
    for value in envelope["references"].values():
        if isinstance(value, dict):
            try:
                parse_reference(value, context)
            except ReferenceError as exc:
                raise EnvelopeError(f"{exc.code}: {exc}") from exc
        elif isinstance(value, str):
            try:
                parse_reference(value)
            except ReferenceError as exc:
                raise EnvelopeError(f"{exc.code}: {exc}") from exc
        else:
            raise EnvelopeError("typed references must be numeric objects or full qualified references")
    return envelope


def normalize_envelope(envelope, resolver=None):
    value = decode_envelope(envelope)
    references = {}
    for name, reference in value["references"].items():
        try:
            references[name] = parse_reference(reference, value["context"])["canonical"]
        except ReferenceError as exc:
            raise EnvelopeError(f"{exc.code}: {exc}") from exc
    if resolver is not None:
        references = {name: resolver(reference) for name, reference in references.items()}
    return {
        "schema": value["payload_schema"],
        "context": deepcopy(value["context"]),
        "payload": deepcopy(value["payload"]),
        "references": references,
    }
