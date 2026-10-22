"""Coordinator-controlled task attempt transitions."""
from __future__ import annotations

from pathlib import Path

from inner_loop.state import ProtocolViolation


def interrupt_task(root: Path, work_id: str, task_id: str, reason: str) -> dict:
    raise ProtocolViolation("task attempt interruption is not implemented")


def reopen_task(root: Path, work_id: str, task_id: str, reason: str) -> dict:
    raise ProtocolViolation("task attempt reopening is not implemented")
