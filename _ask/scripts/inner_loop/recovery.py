"""Work-ID-scoped reconciliation before state initialization or writer admission."""
from __future__ import annotations

from pathlib import Path


class RecoveryRequired(RuntimeError):
    """The runtime history cannot safely authorize a new or resumed attempt."""

    def __init__(self, report: dict):
        super().__init__("recovery_required")
        self.report = report


def inspect(root: Path, work_id: str, graph: dict, state: dict | None = None) -> dict | None:
    """Return a recovery report when retained evidence conflicts with the cache."""
    return None


def require_safe(root: Path, work_id: str, graph: dict, state: dict | None = None) -> None:
    report = inspect(root, work_id, graph, state)
    if report is not None:
        raise RecoveryRequired(report)

