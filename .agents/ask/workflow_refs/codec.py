"""Lossless compact workflow envelope encoding."""


class EnvelopeError(ValueError):
    """An envelope has unsupported schema, context, or typed references."""


def encode_envelope(payload, payload_schema, context, references=None):
    return {}


def decode_envelope(encoded):
    return {}


def normalize_envelope(envelope, resolver=None):
    return {}
