# Isolation for product CheckPlans. Kit path (no_production_datastore + empty
# adapters) skips identifier scans.
from __future__ import annotations

from pathlib import Path


class IsolationLeak(RuntimeError):
    pass


def check_isolation(root: Path, plan: dict, commands: list[str] | None = None) -> None:
    adapters = plan.get("adapters") or []
    if plan.get("no_production_datastore") and not adapters:
        return
    forbidden = [str(x) for x in (plan.get("refuse_identifiers") or [])]
    if not forbidden:
        return
    blobs = list(commands or [])
    yaml_path = root / ".agents" / "verification.yaml"
    if yaml_path.is_file():
        blobs.append(yaml_path.read_text(encoding="utf-8"))
    leaks: list[str] = []
    for ident in forbidden:
        for blob in blobs:
            if ident and ident in blob:
                leaks.append(ident)
                break
    if leaks:
        raise IsolationLeak("isolation leak: " + ",".join(leaks))
