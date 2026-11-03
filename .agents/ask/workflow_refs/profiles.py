"""Versioned, pre-reviewed artifact comparison profiles."""
from __future__ import annotations

from types import MappingProxyType

_PROFILES = MappingProxyType({
    "structured-item/1": MappingProxyType({
        "version": 1,
        "format": "json",
        "extraction": "items-list/id",
        "presentation": "object-key-order-and-whitespace",
        "excluded_fields": (),
    }),
    "prose-item/1": MappingProxyType({
        "version": 1,
        "format": "bytes",
        "extraction": "whole-file",
        "presentation": "exact-bytes",
        "excluded_fields": (),
    }),
})


def get_profile(profile_id):
    """Return a copy of a frozen profile, or None when it is unavailable."""
    profile = _PROFILES.get(profile_id)
    return dict(profile) if profile is not None else None
