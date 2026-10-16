"""Exact passage selectors over caller-supplied, captured repository bytes."""
from pathlib import Path, PureWindowsPath
import re


RULES_VERSION = "engineering-passages/v2"
HEADING_DISCOVERY_VERSION = "markdown-heading-chain/v2"
PLAN_TASK_DISCOVERY_VERSION = "markdown-task-row/v1"

_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_SEPARATOR = re.compile(r"^:?-{3,}:?$")


def _safe_path(value):
    return (isinstance(value, str) and bool(value) and value != "."
            and not Path(value).is_absolute() and not PureWindowsPath(value).drive
            and "\\" not in value and ".." not in Path(value).parts)


def _heading_text(value):
    return value.strip().strip("#").strip()


def _selector(selector):
    if not isinstance(selector, dict):
        raise ValueError("selector must be an object")
    kind = selector.get("kind")
    if kind == "heading" and set(selector) == {"kind", "path"}:
        path = selector.get("path")
        if (not isinstance(path, list) or not path
                or any(not isinstance(part, str) or not part.strip() for part in path)):
            raise ValueError("heading selector path must contain nonempty literal texts")
        return kind, [_heading_text(part) for part in path]
    if kind == "plan-task" and set(selector) == {"kind", "heading_path", "task_id"}:
        path, task_id = selector.get("heading_path"), selector.get("task_id")
        if (not isinstance(path, list) or not path
                or any(not isinstance(part, str) or not part.strip() for part in path)
                or not isinstance(task_id, str) or not task_id.strip()):
            raise ValueError("plan-task selector needs a heading path and literal nonempty task ID")
        return kind, [_heading_text(part) for part in path], task_id
    raise ValueError("unknown selector kind or invalid selector shape")


def _headings(lines):
    stack = []
    found = []
    for index, line in enumerate(lines):
        match = _HEADING.match(line.rstrip("\r\n"))
        if not match:
            continue
        level, text = len(match.group(1)), _heading_text(match.group(2))
        stack = [(depth, title) for depth, title in stack if depth < level]
        chain = [title for _depth, title in stack] + [text]
        found.append((index, level, chain, text))
        stack.append((level, text))
    return found


def _without_fenced_code(lines):
    """Mask fenced examples for discovery while preserving source line numbers."""
    fence_char = None
    fence_size = 0
    result = []
    for line in lines:
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})(.*)$", stripped)
        if fence_char is None:
            if marker:
                fence_char, fence_size = marker.group(1)[0], len(marker.group(1))
                result.append("\n" if line.endswith("\n") else "")
            else:
                result.append(line)
            continue
        if (marker and marker.group(1)[0] == fence_char
                and len(marker.group(1)) >= fence_size and not marker.group(2).strip()):
            fence_char, fence_size = None, 0
        result.append("\n" if line.endswith("\n") else "")
    return result


def _section(lines, headings, heading):
    start, level, _chain, _text = heading
    end = len(lines)
    for index, other_level, _other_chain, _other_text in headings:
        if index > start and other_level <= level:
            end = index
            break
    return start, end, "".join(lines[start:end])


def _result(path, selector, state, count=0, text=None, start=None, end=None, error=None):
    return {"path": path, "selector": selector, "state": state, "match_count": count,
            "text": text, "start_line": start, "end_line": end, "error": error}


def resolve(path, raw, selector, status=None):
    """Resolve one exact heading or Task table row without filesystem access.

    `raw` must be bytes already captured by Snapshot. Missing files are
    represented by `None`; callers must pass unsafe statuses as errors.
    """
    if not _safe_path(path):
        raise ValueError("selector path must be a safe repository-relative path")
    parsed = _selector(selector)
    if status in {"unsafe", "outside-repository", "unresolvable", "unreadable", "symlink"}:
        raise ValueError("selector path is unsafe or unreadable")
    if raw is None:
        return _result(path, selector, "unavailable")
    if not isinstance(raw, bytes):
        raise ValueError("captured passage must be bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("captured passage is not valid UTF-8") from exc
    lines = text.splitlines(keepends=True)
    discovery_lines = _without_fenced_code(lines)
    if parsed[0] == "heading":
        expected = parsed[1]
        headings = _headings(discovery_lines)
        matches = [item for item in headings if item[2] == expected]
        if not matches:
            return _result(path, selector, "unavailable")
        if len(matches) > 1:
            return _result(path, selector, "ambiguous", len(matches))
        start, end, selected = _section(lines, headings, matches[0])
        return _result(path, selector, "available", 1, selected, start + 1, end)

    _kind, heading_path, task_id = parsed
    headings = _headings(discovery_lines)
    heading_matches = [item for item in headings if item[2] == heading_path]
    if not heading_matches:
        return _result(path, selector, "unavailable")
    if len(heading_matches) > 1:
        return _result(path, selector, "ambiguous", len(heading_matches))
    start, end, _heading_text_value = _section(lines, headings, heading_matches[0])
    section_lines = discovery_lines[start:end]
    candidates = []
    index = 0
    while index + 1 < len(section_lines):
        header = section_lines[index]
        separator = section_lines[index + 1]
        if header.lstrip().startswith("|") and separator.lstrip().startswith("|"):
            headers = [cell.strip() for cell in header.strip().strip("|").split("|")]
            separators = [cell.strip() for cell in separator.strip().strip("|").split("|")]
            if len(headers) == len(separators) and "Task ID" in headers and all(
                    _SEPARATOR.fullmatch(cell.replace(" ", "")) for cell in separators):
                column = headers.index("Task ID")
                row_index = index + 2
                while row_index < len(section_lines) and section_lines[row_index].lstrip().startswith("|"):
                    row = [cell.strip() for cell in section_lines[row_index].strip().strip("|").split("|")]
                    if len(row) == len(headers) and row[column] == task_id:
                        candidates.append((index, row_index, row_index))
                    row_index += 1
                index = row_index
            else:
                index += 1
        else:
            index += 1
    if not candidates:
        return _result(path, selector, "unavailable")
    if len(candidates) > 1:
        return _result(path, selector, "ambiguous", len(candidates))
    header_index, _separator_index, row_index = candidates[0]
    selected = "".join(lines[start + index] for index in
                       (header_index, header_index + 1, row_index))
    absolute_start = start + header_index + 1
    absolute_end = start + row_index + 1
    return _result(path, selector, "available", 1, selected, absolute_start, absolute_end)


def required_task_passages(snapshot, node_id):
    """Return unresolved required roles for a real selected Task node."""
    nodes = snapshot.document.get("nodes", [])
    node = next((item for item in nodes if isinstance(item, dict) and item.get("id") == node_id), None)
    if not isinstance(node, dict) or node.get("type") != "task":
        raise ValueError("selected node must identify a Task in the captured model")
    records = [record for record in snapshot.passages.values()
               if record.get("node_id") == node_id and record.get("kind") == "context"]
    by_role = {}
    for record in records:
        by_role.setdefault(record.get("role"), []).append(record)
    missing = []
    for role in ("spec", "plan"):
        entries = by_role.get(role, [])
        if len(entries) != 1 or entries[0].get("resolution", {}).get("state") != "available":
            missing.append(role)
            continue
        if role == "plan":
            execution = node.get("execution")
            expected_task_id = execution.get("task_id") if isinstance(execution, dict) else None
            expected_owner = execution.get("work_id") if isinstance(execution, dict) else None
            selector = entries[0].get("resolution", {}).get("selector")
            passage_path = entries[0].get("path")
            if (not isinstance(expected_task_id, str) or not expected_task_id.strip()
                    or not isinstance(expected_owner, str) or not expected_owner.strip()
                    or not isinstance(selector, dict) or selector.get("kind") != "plan-task"
                    or selector.get("task_id") != expected_task_id
                    or not isinstance(passage_path, str)
                    or not passage_path.startswith(f"work/{expected_owner}/")):
                missing.append(role)
    return missing


def selected_task_node(snapshot, *, selected_task_id=None, selected_execution=None):
    """Resolve only an explicit product Task ID or qualified execution pair."""
    nodes = snapshot.document.get("nodes", [])
    tasks = [item for item in nodes if isinstance(item, dict) and item.get("type") == "task"]
    matches_by_product = None
    matches_by_execution = None
    if selected_task_id is not None:
        if not isinstance(selected_task_id, str) or not selected_task_id.strip():
            raise ValueError("selected Task ID must be nonempty text")
        matches_by_product = [node for node in tasks if node.get("id") == selected_task_id]
    if selected_execution is not None:
        if (not isinstance(selected_execution, dict) or set(selected_execution) != {"work_id", "task_id"}
                or not all(isinstance(selected_execution.get(key), str) and selected_execution[key].strip()
                           for key in ("work_id", "task_id"))):
            raise ValueError("selected execution must contain exact work_id and task_id strings")
        matches_by_execution = [node for node in tasks if node.get("execution") == selected_execution]
    if matches_by_product is None and matches_by_execution is None:
        return None
    if matches_by_product is not None and matches_by_execution is not None:
        if (len(matches_by_product) != 1 or len(matches_by_execution) != 1
                or matches_by_product[0] is not matches_by_execution[0]):
            raise ValueError("product Task and qualified execution selectors conflict")
        return matches_by_product[0]
    matches = matches_by_product if matches_by_product is not None else matches_by_execution
    if len(matches) != 1:
        raise ValueError("selected identity must resolve to exactly one captured Task")
    return matches[0]
