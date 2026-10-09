"""Read-only test source and retained execution projections for the workbench."""
from __future__ import annotations


def qualified_source(root, test, source_sha, *, current_sha=None):
    """Resolve the accepted qualified selector from exactly one Git revision."""
    return {"status": "unavailable", "selector": test.get("case_id"),
            "source_sha": source_sha, "current_sha": current_sha,
            "source": "", "diagnostic": "qualified source is unavailable"}


def execution_history(root, work_id, test, *, spec_digest, plan_digest, candidate_sha):
    """Return actual retained case outcomes, without asserting completion."""
    return {"status": "unavailable", "completion": "not_evaluated", "runs": [],
            "diagnostic": "retained execution evidence is unavailable"}
