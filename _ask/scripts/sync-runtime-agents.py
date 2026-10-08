#!/usr/bin/env python3
"""Emit Cursor / Claude / Codex stage agents from .agents/ask/bindings (fallback _ask/bindings)."""
from __future__ import annotations

import os
import sys
from pathlib import Path


STAGES = [
    "00-explore",
    "01-grill",
    "02-spec",
    "03-spec-challenge",
    "04-spec-change",
    "05-plan",
    "06-implement",
    "07-review",
    "08-refactor",
    "09-verify",
    "10-accept",
]

RUNTIMES = ("cursor", "claude", "codex", "opencode")
OUT_DIRS = {
    "cursor": Path(".cursor/agents"),
    "claude": Path(".claude/agents"),
    "codex": Path(".codex/agents"),
    "opencode": Path(".opencode/agents"),
}


def parse_yaml(text: str) -> dict:
    """Indent-based subset: mappings, string lists, scalars, |/> blocks."""
    lines = text.splitlines()
    root: dict = {}
    stack: list[tuple[int, object]] = [(-1, root)]
    i = 0

    def strip_comment(s: str) -> str:
        in_q = False
        out = []
        for ch in s:
            if ch == '"' and not in_q:
                in_q = True
                out.append(ch)
            elif ch == '"' and in_q:
                in_q = False
                out.append(ch)
            elif ch == "#" and not in_q:
                break
            else:
                out.append(ch)
        return "".join(out).rstrip()

    def parse_scalar(raw: str):
        raw = raw.strip()
        if raw in ("", "~", "null"):
            return None
        if (raw.startswith('"') and raw.endswith('"')) or (
            raw.startswith("'") and raw.endswith("'")
        ):
            return raw[1:-1]
        if raw.lower() in ("true", "false"):
            return raw.lower() == "true"
        return raw

    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = strip_comment(raw.lstrip(" "))
        if not content:
            i += 1
            continue
        while stack and indent <= stack[-1][0] and len(stack) > 1:
            stack.pop()
        parent = stack[-1][1]

        if content.startswith("- "):
            item = parse_scalar(content[2:])
            if not isinstance(parent, list):
                raise ValueError(f"list item without list parent: {content}")
            parent.append(item)
            i += 1
            continue

        if ":" not in content:
            raise ValueError(f"expected key: {content}")
        key, rest = content.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        if not isinstance(parent, dict):
            raise ValueError(f"key under non-mapping: {key}")

        if rest in ("|", ">"):
            block: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    block.append("")
                    i += 1
                    continue
                nindent = len(nxt) - len(nxt.lstrip(" "))
                if nindent <= indent:
                    break
                block.append(nxt[indent + 2 :] if nindent >= indent + 2 else nxt.lstrip())
                i += 1
            parent[key] = " ".join(x.strip() for x in block if x.strip()) if rest == ">" else "\n".join(block)
            continue

        if rest == "":
            # peek
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
                j += 1
            if j < len(lines):
                peek = lines[j]
                pindent = len(peek) - len(peek.lstrip(" "))
                if pindent > indent and peek.lstrip().startswith("- "):
                    parent[key] = []
                    stack.append((indent, parent[key]))
                    i += 1
                    continue
                if pindent > indent:
                    parent[key] = {}
                    stack.append((indent, parent[key]))
                    i += 1
                    continue
            parent[key] = {}
            stack.append((indent, parent[key]))
            i += 1
            continue

        parent[key] = parse_scalar(rest)
        i += 1
    return root


def load_yaml(path: Path) -> dict:
    if not path.is_file():
        return {}
    return parse_yaml(path.read_text(encoding="utf-8"))


def env_stage_key(stage: str) -> str:
    return "ASK_MODEL_" + stage.upper().replace("-", "_")


def value_from_overlay(data: dict, stage: str, runtime: str):
    if not data:
        return None
    rt = data.get(runtime)
    if isinstance(rt, dict) and stage in rt:
        return rt[stage]
    if stage in data and not isinstance(data[stage], dict):
        return data[stage]
    stages = data.get("stages")
    if isinstance(stages, dict) and stage in stages:
        return stages[stage]
    return None


def is_role_or_pool(val: str) -> bool:
    return val in ("thinking", "typing", "adversarial", "review", "cheap", "diverse")


def resolve_slug(
    stage: str,
    runtime: str,
    defaults: dict,
    runtime_cfg: dict,
    consumer: dict,
    work: dict,
    env: dict,
) -> str:
    risk = (
        (work.get("risk") if work else None)
        or (consumer.get("risk") if consumer else None)
        or env.get("ASK_RISK")
        or "LOW"
    )
    risk = str(risk).upper()

    env_rt = env.get(f"{env_stage_key(stage)}_{runtime.upper()}")
    if env_rt:
        return env_rt
    env_any = env.get(env_stage_key(stage))
    if env_any and not is_role_or_pool(env_any):
        return env_any

    for overlay in (work, consumer):
        hit = value_from_overlay(overlay, stage, runtime)
        if hit is None:
            continue
        hit = str(hit)
        if not is_role_or_pool(hit):
            return hit
        return slug_from_role_or_pool(hit, stage, risk, defaults, runtime_cfg)

    if env_any and is_role_or_pool(env_any):
        return slug_from_role_or_pool(env_any, stage, risk, defaults, runtime_cfg)

    role = (defaults.get("stages") or {}).get(stage)
    return slug_from_role_or_pool(str(role), stage, risk, defaults, runtime_cfg)


def slug_from_role_or_pool(token: str, stage: str, risk: str, defaults: dict, runtime_cfg: dict) -> str:
    pools = runtime_cfg.get("pools") or {}
    roles = runtime_cfg.get("roles") or {}
    if token in ("cheap", "diverse"):
        slug = pools.get(token)
        if not slug:
            raise SystemExit(f"runtime missing pool {token}")
        return str(slug)
    if token == "review":
        pool = (defaults.get("review_pool") or {}).get(risk, "cheap")
        slug = pools.get(pool)
        if not slug:
            raise SystemExit(f"runtime missing pool {pool} for risk {risk}")
        return str(slug)
    slug = roles.get(token)
    if not slug:
        raise SystemExit(f"runtime missing role {token}")
    return str(slug)


def render(tpl: str, **kw: str) -> str:
    out = tpl
    for k, v in kw.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def bindings_dir(root: Path) -> Path:
    ask_bind = root / ".agents" / "ask" / "bindings"
    if (root / ".agents" / "ask" / "stages").is_dir() and ask_bind.is_dir():
        return ask_bind
    return root / "_ask" / "bindings"


def main() -> int:
    root = Path(os.environ.get("ASK_ROOT") or Path(__file__).resolve().parents[2])
    os.chdir(root)
    bind = bindings_dir(root)
    defaults = load_yaml(bind / "models.defaults.yaml")
    consumer = load_yaml(root / "_ask" / "bindings" / "models.yaml")
    local_bind = root / ".agents" / "ask.local" / "bindings"
    if local_bind.is_dir():
        extra = load_yaml(local_bind / "models.yaml")
        if extra:
            consumer = {**consumer, **extra}
    work = {}
    work_id = os.environ.get("ASK_WORK_ID")
    if work_id:
        work = load_yaml(root / "work" / work_id / "models.yaml")

    md_tpl = (bind / "templates" / "agent.md.tpl").read_text(encoding="utf-8")
    toml_tpl = (bind / "templates" / "agent.toml.tpl").read_text(encoding="utf-8")
    opencode_tpl = (bind / "templates" / "agent.opencode.md.tpl").read_text(encoding="utf-8")

    for runtime in RUNTIMES:
        cfg = load_yaml(bind / "runtimes" / f"{runtime}.yaml")
        if not cfg:
            print(f"sync-runtime-agents: skip {runtime} (no yaml)", file=sys.stderr)
            continue
        out_dir = root / OUT_DIRS[runtime]
        out_dir.mkdir(parents=True, exist_ok=True)
        for stage in STAGES:
            slug = resolve_slug(stage, runtime, defaults, cfg, consumer, work, os.environ)
            name = f"kit-{stage}"
            desc = f"Kit protocol stage {stage} ({runtime})."
            readonly = "readonly: true\n" if stage == "07-review" else ""
            permission_block = "permission:\n  edit: deny\n" if stage == "07-review" else ""
            if runtime == "codex":
                text = render(
                    toml_tpl,
                    name=name,
                    description=desc,
                    model=slug,
                    runtime=runtime,
                    stage=stage,
                )
                dest = out_dir / f"{name}.toml"
            elif runtime == "opencode":
                text = render(
                    opencode_tpl,
                    description=desc,
                    model=slug,
                    permission_block=permission_block,
                    runtime=runtime,
                    stage=stage,
                )
                dest = out_dir / f"{name}.md"
            else:
                text = render(
                    md_tpl,
                    name=name,
                    description=desc,
                    model=slug,
                    readonly_line=readonly,
                    runtime=runtime,
                    stage=stage,
                )
                dest = out_dir / f"{name}.md"
            dest.write_text(text, encoding="utf-8")
        print(f"sync-runtime-agents: wrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
