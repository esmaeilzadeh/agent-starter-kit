from __future__ import annotations

import re
from pathlib import Path

from inner_loop.yaml_lite import parse_yaml


def glob_to_re(pat: str) -> re.Pattern:
    buf: list[str] = ["^"]
    i = 0
    while i < len(pat):
        if pat.startswith("**", i):
            buf.append(".*")
            i += 2
            if i < len(pat) and pat[i] == "/":
                i += 1
            continue
        if pat[i] == "*":
            buf.append("[^/]*")
            i += 1
            continue
        buf.append(re.escape(pat[i]))
        i += 1
    buf.append("$")
    return re.compile("".join(buf))


def _samples(pat: str) -> list[str]:
    """Paths that the glob is expected to match."""
    out = {pat.replace("**/", "").replace("**", "").replace("*", "f")}
    if "**" in pat:
        stem = pat.replace("/**", "").replace("**", "")
        out.add(stem.rstrip("/") + "/a")
        out.add(stem.rstrip("/") + "/a/b")
        out.add(stem.rstrip("/") + "/a/b.md")
    if pat.endswith(".md") or "/" in pat:
        out.add(pat.replace("*", "x"))
    return [p for p in out if p]


def globs_overlap(a: str, b: str) -> bool:
    if a == b:
        return True
    ra, rb = glob_to_re(a), glob_to_re(b)
    for sample in _samples(a) + [a]:
        if rb.match(sample):
            return True
    for sample in _samples(b) + [b]:
        if ra.match(sample):
            return True
    return False


def load_graph(root: Path, work_id: str) -> dict:
    path = root / "work" / work_id / "inner-loop" / "tasks.yaml"
    if not path.is_file():
        raise FileNotFoundError(str(path))
    data = parse_yaml(path.read_text(encoding="utf-8"))
    tasks = data.get("tasks") or []
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")
    data["tasks"] = tasks
    data["work_id"] = data.get("work_id") or work_id
    return data


def _task_map(graph: dict) -> dict[str, dict]:
    out = {}
    for t in graph.get("tasks") or []:
        tid = t.get("id")
        if not tid:
            raise ValueError("task missing id")
        if tid in out:
            raise ValueError(f"duplicate task id {tid}")
        out[tid] = t
    return out


def _depends(task: dict) -> list[str]:
    deps = task.get("depends_on") or []
    if deps is None:
        return []
    return [str(d) for d in deps]


def _paths(task: dict) -> list[str]:
    return [str(p) for p in (task.get("owned_paths") or [])]


def _reaches(adj: dict[str, list[str]], src: str, dst: str) -> bool:
    seen = set()
    stack = [src]
    while stack:
        cur = stack.pop()
        if cur == dst:
            return True
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(adj.get(cur, []))
    return False


def _cycle(adj: dict[str, list[str]]) -> bool:
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in adj}

    def dfs(n: str) -> bool:
        color[n] = GREY
        for nxt in adj[n]:
            if nxt not in color:
                continue
            if color[nxt] == GREY:
                return True
            if color[nxt] == WHITE and dfs(nxt):
                return True
        color[n] = BLACK
        return False

    return any(color[n] == WHITE and dfs(n) for n in adj)


def validate_graph(graph: dict) -> str:
    tasks = _task_map(graph)
    adj = {tid: _depends(t) for tid, t in tasks.items()}
    for tid, deps in adj.items():
        for d in deps:
            if d not in tasks:
                return "cycle"
    if _cycle(adj):
        return "cycle"
    ids = sorted(tasks)
    for i, ai in enumerate(ids):
        for bi in ids[i + 1 :]:
            serialized = _reaches(adj, ai, bi) or _reaches(adj, bi, ai)
            if serialized:
                continue
            for pa in _paths(tasks[ai]):
                for pb in _paths(tasks[bi]):
                    if globs_overlap(pa, pb):
                        return "path_conflict"
    return "ok"
