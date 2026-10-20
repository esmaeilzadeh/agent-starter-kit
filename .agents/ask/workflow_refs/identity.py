"""Canonical qualified numeric workflow references."""


class ReferenceError(ValueError):
    """A reference is malformed, ambiguous, or lacks declared context."""


def parse_reference(value, context=None):
    return None


def normalize_references(values, context=None):
    return ()


def reference_sort_key(value):
    return None


def display_git_id(full_id, known_ids):
    return None


def resolve_git_id(display, known_ids):
    return None
