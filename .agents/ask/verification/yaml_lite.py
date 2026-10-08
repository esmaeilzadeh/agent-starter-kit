# YAML subset for CheckPlan files: mappings, list-of-maps, inline lists.
from __future__ import annotations


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
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(p) for p in inner.split(",")]
    return raw


def parse_yaml(text: str) -> dict:
    lines = text.splitlines()
    root: dict = {}
    stack: list[tuple[int, object]] = [(-1, root)]
    i = 0
    n = len(lines)

    def parent_at(indent: int):
        while stack and indent <= stack[-1][0] and len(stack) > 1:
            stack.pop()
        return stack[-1][1]

    while i < n:
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = raw.lstrip()
        parent = parent_at(indent)

        if content.startswith("- "):
            item = content[2:].strip()
            if not isinstance(parent, list):
                raise ValueError(f"list item without list parent: {content}")
            if ":" in item and not item.startswith("["):
                key, rest = item.split(":", 1)
                node = {key.strip(): parse_scalar(rest)}
                parent.append(node)
                stack.append((indent, node))
            else:
                parent.append(parse_scalar(item))
            i += 1
            continue

        if ":" not in content:
            raise ValueError(f"expected key: {content}")
        key, rest = content.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        if not isinstance(parent, dict):
            raise ValueError(f"key under non-mapping: {key}")

        if rest == "":
            j = i + 1
            while j < n and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
                j += 1
            if j < n:
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
