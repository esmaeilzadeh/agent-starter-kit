"""Versioned, pre-reviewed artifact comparison profiles."""
from __future__ import annotations


PROFILES = {
    "structured-item/1": {
        "version": 1,
        "format": "json",
        "presentation": "object-key-order-and-whitespace",
        "excluded_fields": (),
    },
    "prose-item/1": {
        "version": 1,
        "format": "bytes",
        "presentation": "exact-bytes",
        "excluded_fields": (),
    },
}


def get_profile(profile_id):
    """Return a copy of a frozen profile, or None when it is unavailable."""
    profile = PROFILES.get(profile_id)
    return dict(profile) if profile is not None else None
