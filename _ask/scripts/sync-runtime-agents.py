#!/usr/bin/env python3
"""Emit Cursor / Claude / Codex stage agents from .agents/ask/bindings (fallback _ask/bindings)."""
from __future__ import annotations

import os
import json
import re
import subprocess
import sys
import unicodedata
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
MISSING = object()
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
        quote = None
        out = []
        i = 0
        while i < len(s):
            ch = s[i]
            if quote == "'" and ch == "'" and i + 1 < len(s) and s[i + 1] == "'":
                out.extend((ch, s[i + 1]))
                i += 2
                continue
            if quote == '"' and ch == "\\" and i + 1 < len(s):
                out.extend((ch, s[i + 1]))
                i += 2
                continue
            if quote:
                if ch == quote:
                    quote = None
            elif ch in "'\"" and (not s[:i].strip() or s[:i].rstrip().endswith((":", "-"))):
                quote = ch
            elif ch == "#":
                break
            out.append(ch)
            i += 1
        return "".join(out).rstrip()

    def parse_scalar(raw: str):
        raw = raw.strip()
        if raw in ("", "~", "null"):
            return None
        if raw.startswith('"') and raw.endswith('"'):
            return json.loads(raw)
        if raw.startswith("'") and raw.endswith("'"):
            return raw[1:-1].replace("''", "'")
        if raw.lower() in ("true", "false"):
            return raw.lower() == "true"
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            return [] if not inner else [parse_scalar(item) for item in inner.split(",")]
        if raw.startswith("{") and raw.endswith("}"):
            return {}
        if re.fullmatch(r"[+-]?(?:0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+|(?:[0-9][0-9_]*(?:\.[0-9_]*)?|\.[0-9_]+)(?:[eE][+-]?[0-9_]+)?)", raw):
            return 0
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
        return MISSING
    rt = data.get(runtime)
    if isinstance(rt, dict) and stage in rt:
        return rt[stage]
    if stage in data and not isinstance(data[stage], dict):
        return data[stage]
    stages = data.get("stages")
    if isinstance(stages, dict) and stage in stages:
        return stages[stage]
    return MISSING


def validate_model(value, runtime: str, stage: str) -> str:
    if (not isinstance(value, str) or not value.strip()
            or any(unicodedata.category(ch) in {"Cc", "Zl", "Zp"} for ch in value)):
        raise SystemExit(f"invalid model for {runtime} {stage}: expected a nonempty single-line string")
    return value


def parse_generated_toml(text: str) -> dict:
    """Parse the assignment and multiline-string subset used by agent.toml.tpl."""
    def validate_multiline_escapes(value: str) -> None:
        index = 0
        while index < len(value):
            char = value[index]
            if char == "\\":
                index += 1
                if index == len(value):
                    raise ValueError("unterminated TOML escape")
                escape = value[index]
                if escape == "\n":
                    index += 1
                    while index < len(value) and value[index].isspace():
                        index += 1
                    continue
                if escape in 'btnfr"\\':
                    index += 1
                    continue
                if escape in "uU":
                    width = 4 if escape == "u" else 8
                    digits = value[index + 1:index + 1 + width]
                    if len(digits) != width or not re.fullmatch(r"[0-9a-fA-F]+", digits):
                        raise ValueError("invalid TOML Unicode escape")
                    codepoint = int(digits, 16)
                    if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
                        raise ValueError("invalid TOML Unicode scalar")
                    index += width + 1
                    continue
                raise ValueError(f"invalid TOML escape: \\{escape}")
            if unicodedata.category(char) == "Cc" and char not in "\t\n\r":
                raise ValueError("control character in TOML multiline string")
            index += 1

    document = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*(.*)", line)
        if not match:
            raise ValueError(f"invalid TOML assignment: {line}")
        key, raw = match.groups()
        if key in document:
            raise ValueError(f"duplicate TOML field: {key}")
        if raw.startswith('"""'):
            body = [raw[3:]] if raw[3:] else []
            while not body or not body[-1].endswith('"""'):
                if index == len(lines):
                    raise ValueError(f"unterminated TOML multiline string: {key}")
                body.append(lines[index])
                index += 1
            if body[-1] != '"""':
                raise ValueError(f"invalid TOML multiline string terminator: {key}")
            body.pop()
            value = "\n".join(body).lstrip("\n")
            validate_multiline_escapes(value)
            document[key] = value
        else:
            value = json.loads(raw)
            if not isinstance(value, str):
                raise ValueError(f"expected TOML string field: {key}")
            document[key] = value
    allowed = {"name", "description", "model", "model_reasoning_effort", "developer_instructions"}
    if not {"name", "description", "model", "developer_instructions"} <= document.keys() or document.keys() - allowed:
        raise ValueError("unexpected generated TOML fields")
    return document


def validate_rendered_model(text: str, runtime: str, slug: str, stage: str) -> None:
    try:
        if runtime == "codex":
            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib
                except ImportError:
                    document = parse_generated_toml(text)
                else:
                    document = tomllib.loads(text)
            else:
                document = tomllib.loads(text)
        else:
            parts = text.split("---", 2)
            if len(parts) != 3 or parts[0].strip():
                raise ValueError("missing frontmatter")
            frontmatter = parts[1]
            if len(re.findall(r"^model:", frontmatter, re.MULTILINE)) != 1:
                raise ValueError("expected exactly one model field")
            document = parse_yaml(frontmatter)
    except Exception as exc:
        raise SystemExit(f"invalid {runtime} template for {stage}: {exc}") from exc
    if not isinstance(document, dict) or document.get("model") != slug:
        raise SystemExit(f"invalid {runtime} template for {stage}: model field failed round-trip")


def run_transaction(root: Path) -> int:
    inputs = ["_ask/scripts", ".agents/ask", ".agents/ask.local", "_ask/bindings"]
    if work_id := os.environ.get("ASK_WORK_ID"):
        inputs.append(f"work/{work_id}")
    command = [
        sys.executable, str(root / "_ask/scripts/write-transaction.py"), "run",
        "--root", str(root),
    ]
    for path in (".cursor/agents", ".claude/agents", ".codex/agents", ".opencode/agents"):
        command.extend(("--path", path))
    for path in inputs:
        command.extend(("--input-path", path))
    command.extend(("--", sys.executable, "{target}/_ask/scripts/sync-runtime-agents.py"))
    return subprocess.run(command, cwd=root, check=False).returncode


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

    env_rt_key = f"{env_stage_key(stage)}_{runtime.upper()}"
    env_any_key = env_stage_key(stage)
    if env_rt_key in env:
        return validate_model(env[env_rt_key], runtime, stage)
    env_any = env.get(env_any_key, MISSING)
    if env_any is not MISSING:
        validate_model(env_any, runtime, stage)
        if not is_role_or_pool(env_any):
            return env_any

    for overlay in (work, consumer):
        hit = value_from_overlay(overlay, stage, runtime)
        if hit is MISSING:
            continue
        validate_model(hit, runtime, stage)
        if not is_role_or_pool(hit):
            return hit
        return slug_from_role_or_pool(hit, stage, risk, defaults, runtime_cfg)

    if env_any is not MISSING and is_role_or_pool(env_any):
        return slug_from_role_or_pool(env_any, stage, risk, defaults, runtime_cfg)

    role = (defaults.get("stages") or {}).get(stage)
    return slug_from_role_or_pool(validate_model(role, runtime, stage), stage, risk, defaults, runtime_cfg)


def slug_from_role_or_pool(token: str, stage: str, risk: str, defaults: dict, runtime_cfg: dict) -> str:
    pools = runtime_cfg.get("pools") or {}
    roles = runtime_cfg.get("roles") or {}
    if token in ("cheap", "diverse"):
        slug = pools.get(token)
        if not slug:
            raise SystemExit(f"runtime missing pool {token}")
        return slug
    if token == "review":
        pool = (defaults.get("review_pool") or {}).get(risk, "cheap")
        slug = pools.get(pool)
        if not slug:
            raise SystemExit(f"runtime missing pool {pool} for risk {risk}")
        return slug
    slug = roles.get(token)
    if not slug:
        raise SystemExit(f"runtime missing role {token}")
    return slug


def render(tpl: str, **kw: str) -> str:
    def replace(match):
        key = match.group(1)
        if key not in kw:
            raise ValueError(f"unknown template field: {key}")
        return kw[key]
    return re.sub(r"\{\{([a-z_]+)\}\}", replace, tpl)


def resolve_effort(stage: str, model: str, cfg: dict, consumer: dict, work: dict, env: dict) -> str | None:
    """Codex-only effort; explicit inheritance and unknown models stay unpinned."""
    key = "ASK_EFFORT_" + stage.upper().replace("-", "_")
    value = env.get(key + "_CODEX", env.get(key))
    if value is None:
        for overlay in (work, consumer):
            value = value_from_overlay(overlay.get("reasoning_effort") or {}, stage, "codex")
            if value is not MISSING:
                break
    if value is MISSING:
        value = None
    if value is None:
        efforts = cfg.get("reasoning_effort") or {}
        models = efforts.get("models") or {}
        if model in models:
            value = (efforts.get("stages") or {}).get(stage, models[model])
    if value is None or value == "inherit":
        return None
    if not isinstance(value, str) or value not in {"low", "medium", "high", "xhigh", "max"}:
        raise SystemExit(f"invalid reasoning effort for codex {stage}: {value!r}")
    return value


def bindings_dir(root: Path) -> Path:
    ask_bind = root / ".agents" / "ask" / "bindings"
    if (root / ".agents" / "ask" / "stages").is_dir() and ask_bind.is_dir():
        return ask_bind
    return root / "_ask" / "bindings"


def main() -> int:
    root = (Path(__file__).resolve().parents[2] if os.environ.get("ASKIT_TRANSACTION_ACTIVE") == "1"
            else Path(os.environ.get("ASK_ROOT") or Path(__file__).resolve().parents[2]))
    root = root.resolve()
    os.chdir(root)
    bind = bindings_dir(root)
    defaults = load_yaml(bind / "models.defaults.yaml")
    models = root / ".agents" / "ask.local" / "bindings" / "models.yaml"
    if not models.is_file():
        models = root / "_ask" / "bindings" / "models.yaml"
    consumer = load_yaml(models)
    work = {}
    work_id = os.environ.get("ASK_WORK_ID")
    if work_id:
        work = load_yaml(root / "work" / work_id / "models.yaml")

    md_tpl = (bind / "templates" / "agent.md.tpl").read_text(encoding="utf-8")
    toml_tpl = (bind / "templates" / "agent.toml.tpl").read_text(encoding="utf-8")
    opencode_tpl = (bind / "templates" / "agent.opencode.md.tpl").read_text(encoding="utf-8")

    outputs = []
    for runtime in RUNTIMES:
        cfg = load_yaml(bind / "runtimes" / f"{runtime}.yaml")
        if not cfg:
            print(f"sync-runtime-agents: skip {runtime} (no yaml)", file=sys.stderr)
            continue
        out_dir = root / OUT_DIRS[runtime]
        for stage in STAGES:
            slug = validate_model(resolve_slug(stage, runtime, defaults, cfg, consumer, work, os.environ), runtime, stage)
            name = f"kit-{stage}"
            desc = f"Kit protocol stage {stage} ({runtime})."
            readonly = "readonly: true\n" if stage == "07-review" else ""
            permission_block = "permission:\n  edit: deny\n" if stage == "07-review" else ""
            if runtime == "codex":
                effort = resolve_effort(stage, slug, cfg, consumer, work, os.environ)
                text = render(
                    toml_tpl,
                    name=name,
                    description=desc,
                    model=json.dumps(slug, ensure_ascii=False),
                    reasoning_effort_line=f'model_reasoning_effort = "{effort}"\n' if effort else "",
                    runtime=runtime,
                    stage=stage,
                )
                dest = out_dir / f"{name}.toml"
            elif runtime == "opencode":
                text = render(
                    opencode_tpl,
                    description=desc,
                    model=json.dumps(slug, ensure_ascii=False),
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
                    model=json.dumps(slug, ensure_ascii=False),
                    readonly_line=readonly,
                    runtime=runtime,
                    stage=stage,
                )
                dest = out_dir / f"{name}.md"
            validate_rendered_model(text, runtime, slug, stage)
            outputs.append((dest, text))
    # Preflight every assignment before touching any runtime's existing output.
    for dest, text in outputs:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    for out_dir in sorted({dest.parent for dest, _ in outputs}):
        print(f"sync-runtime-agents: wrote {out_dir}")
    return 0


if __name__ == "__main__":
    transaction_root = Path(os.environ.get("ASK_ROOT") or Path(__file__).resolve().parents[2]).resolve()
    if os.environ.get("ASKIT_TRANSACTION_ACTIVE") != "1" and (transaction_root / ".git").exists():
        raise SystemExit(run_transaction(transaction_root))
    # shortcut: non-Git fixture roots run in place; standalone non-repository sync is unsupported.
    raise SystemExit(main())
