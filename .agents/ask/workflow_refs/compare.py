"""Complete, profile-aware artifact item comparison and pinned extraction."""
from __future__ import annotations


class ComparisonError(ValueError):
    """A source cannot be completely or safely compared."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def compare_items(before, after, profile_id, before_inputs=(), after_inputs=(),
                  before_profile=None, after_profile=None):
    """Compare payloads and their complete exact dependency bindings."""
    return {"status": "incomplete", "reason": "comparison_not_implemented"}


def extract_git_item(repository_root, commit, source_path, item_id, profile_id):
    """Extract one stable item from an exact immutable Git snapshot."""
    return {"status": "incomplete", "reason": "extraction_not_implemented"}
