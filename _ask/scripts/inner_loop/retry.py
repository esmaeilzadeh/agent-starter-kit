from __future__ import annotations


def next_action(review_round: int, debug_round: int, verdict: str, boundary: str) -> str:
    """Return implement | debug | integrate | blocked."""
    if boundary == "glob_too_narrow":
        return "blocked"
    if verdict == "APPROVED":
        return "integrate"
    if verdict != "REJECTED":
        raise ValueError(f"unknown verdict {verdict}")
    if review_round < 2:
        return "implement"
    if debug_round < 2:
        return "debug"
    return "blocked"
