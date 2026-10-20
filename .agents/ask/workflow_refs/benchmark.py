"""Reproduce the frozen legacy workflow-reference benchmark."""

class BenchmarkError(ValueError):
    """The frozen benchmark inputs are incomplete or no longer comparable."""


def capture_baseline(root, manifest_path=None):
    """Capture the baseline agent inputs and unique metadata accounting."""
    return {"schema": "ask-reference-benchmark/v1"}
