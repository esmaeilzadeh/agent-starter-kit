from __future__ import annotations

from pathlib import Path

from verification.yaml_lite import parse_yaml


def load_plan(root: Path) -> dict:
    path = root / ".agents" / "verification.yaml"
    if not path.is_file():
        raise FileNotFoundError(
            "missing .agents/verification.yaml; run the human-only verify wizard"
        )
    return parse_yaml(path.read_text(encoding="utf-8"))


def _preset_dir(root: Path) -> Path:
    return root / ".agents" / "ask" / "verification" / "presets"


def expand_plan(root: Path, plan: dict) -> list[dict]:
    checks: list[dict] = []
    raw = plan.get("checks") or []
    if isinstance(raw, list):
        checks.extend(raw)
    for name in plan.get("presets") or []:
        pp = _preset_dir(root) / f"{name}.yaml"
        if not pp.is_file():
            raise FileNotFoundError(f"unknown preset {name}")
        preset = parse_yaml(pp.read_text(encoding="utf-8"))
        checks.extend(preset.get("checks") or [])
    expanded: list[dict] = []
    for c in checks:
        glob = c.get("glob")
        if glob:
            for path in sorted(root.glob(str(glob))):
                if path.is_file() and path.stat().st_mode & 0o111:
                    expanded.append(
                        {
                            "id": f"{c.get('id', glob)}:{path.relative_to(root)}",
                            "tier": c.get("tier", "mandatory"),
                            "command": str(path.relative_to(root)),
                        }
                    )
        elif c.get("command"):
            expanded.append(c)
    return expanded
