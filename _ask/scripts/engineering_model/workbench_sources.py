"""Revision-bound work inventory and committed source snapshots."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSnapshot:
    commit: str
    files: dict
    diagnostics: tuple
    editable: bool = False


def discover_work(root):
    return {"current_work_id": None, "workstreams": [], "later": []}


def read_snapshot(root, ref, work_id, *, paths=()):
    return SourceSnapshot("", {}, ())
