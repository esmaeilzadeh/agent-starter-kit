"""Read a selected test with its necessary same-revision source context."""
from __future__ import annotations

import ast
from pathlib import Path, PurePosixPath
import subprocess

from .workbench_evidence import _blob, _commit, _safe_path, _selector_node


def _source(text, node):
    lines = text.splitlines()
    start = min([node.lineno, *(item.lineno for item in getattr(node, "decorator_list", []))])
    return "\n".join(lines[start - 1:node.end_lineno])


def _target_names(node):
    return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}


def _loaded_names(nodes):
    return {child.id for node in nodes for child in ast.walk(node)
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load)}


def _self_calls(nodes):
    return {child.func.attr for node in nodes for child in ast.walk(node)
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
            and isinstance(child.func.value, ast.Name) and child.func.value.id == "self"}


def _record(text, node, selector, role, source_path, source_sha, current_sha):
    return {"selector": selector, "role": role, "status": "available",
            "source": _source(text, node), "source_path": source_path,
            "source_sha": source_sha, "current_sha": current_sha}


def read_test(root, test, source_sha, *, current_sha=None):
    """Read a qualified test, direct setup/helpers and referenced module fixtures.

    Source is always taken from ``source_sha``. The current revision is used only
    to label applicability; it never supplies replacement helper bytes.
    """
    selector = test.get("case_id") if isinstance(test, dict) else None
    result = {"status": "unavailable", "context_status": "unavailable",
              "selector": selector, "source_sha": None, "current_sha": None,
              "test_source": "", "context": [],
              "flow": test.get("scenario") if isinstance(test, dict) else None,
              "expected_assertions": (test.get("expected_assertions", [])
                                      if isinstance(test, dict) else []),
              "diagnostic": "readable test context is unavailable"}
    try:
        root = Path(root).resolve()
        if not isinstance(test, dict) or not isinstance(selector, str):
            raise ValueError("accepted test selector is missing")
        paths = test.get("source_paths")
        if not isinstance(paths, list) or not paths:
            raise ValueError("accepted test source paths are missing")
        sha = _commit(root, source_sha)
        current = _commit(root, current_sha) if current_sha is not None else None
        module = selector.split(".", 1)[0]
        candidates = [path for path in paths if _safe_path(path)
                      and PurePosixPath(path).stem == module]
        if not candidates and len(paths) == 1 and _safe_path(paths[0]):
            candidates = list(paths)
        if len(candidates) != 1:
            raise ValueError("qualified test module does not select one accepted source path")
        source_path = candidates[0]
        text = _blob(root, sha, source_path).decode("utf-8")
        tree = ast.parse(text, filename=source_path)
        selected_module, selected, _start, _end = _selector_node(tree, selector)
        if selected_module != PurePosixPath(source_path).stem:
            raise ValueError("qualified selector module differs from accepted source path")
        result.update(status="current" if current is None or sha == current else "historical",
                      context_status="complete", source_sha=sha, current_sha=current,
                      source_path=source_path, test_source=_source(text, selected),
                      diagnostic=None)

        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        test_class = parents.get(selected)
        if not isinstance(test_class, ast.ClassDef):
            test_class = None
        class_methods = ({node.name: node for node in test_class.body
                          if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
                         if test_class else {})
        top_functions = {node.name: node for node in tree.body
                         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        context = []
        if imports:
            first, last = imports[0].lineno, max(node.end_lineno for node in imports)
            context.append({"selector": "<imports>", "role": "import-boundary",
                            "status": "available", "source": "\n".join(text.splitlines()[first - 1:last]),
                            "source_path": source_path, "source_sha": sha, "current_sha": current})

        selected_nodes = [selected]
        for setup_name in ("setUp", "asyncSetUp", "setUpClass"):
            if setup_name in class_methods and class_methods[setup_name] not in selected_nodes:
                selected_nodes.append(class_methods[setup_name])
                context.append(_record(text, class_methods[setup_name],
                                       f"{test_class.name}.{setup_name}", "setup",
                                       source_path, sha, current))

        referenced_methods = set()
        pending = list(selected_nodes)
        while pending:
            node = pending.pop()
            for name in _self_calls([node]):
                helper = class_methods.get(name)
                if helper is not None and helper not in selected_nodes:
                    selected_nodes.append(helper)
                    pending.append(helper)
                    referenced_methods.add(name)
                elif helper is None and name.startswith("_"):
                    context.append({"selector": f"{test_class.name}.{name}" if test_class else name,
                                    "role": "helper", "status": "missing", "source": "",
                                    "source_path": source_path, "source_sha": sha,
                                    "current_sha": current,
                                    "diagnostic": "referenced helper is missing at selected revision"})
        for name in sorted(referenced_methods):
            context.append(_record(text, class_methods[name], f"{test_class.name}.{name}",
                                   "helper", source_path, sha, current))

        module_names = _loaded_names(selected_nodes)
        for name in sorted(module_names & top_functions.keys()):
            function = top_functions[name]
            context.append(_record(text, function, f"{module}.{name}", "helper",
                                   source_path, sha, current))
            module_names.update(_loaded_names([function]))

        assignments = {}
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    assignments.update({name: node for name in _target_names(target)})
        for name in sorted(module_names & assignments.keys()):
            context.append(_record(text, assignments[name], name, "fixture", source_path, sha, current))
        if any(item["status"] == "missing" for item in context):
            result["context_status"] = "incomplete"
        context.sort(key=lambda item: (item.get("source_path", ""),
                                       _line_for_selector(tree, item.get("selector"))))
        result["context"] = context
        result["diagnostic"] = ("one or more referenced helpers are missing at selected revision"
                                if result["context_status"] == "incomplete" else None)
    except (OSError, UnicodeError, ValueError, TypeError, SyntaxError, subprocess.SubprocessError) as exc:
        result["diagnostic"] = str(exc)
    return result


def _line_for_selector(tree, selector):
    if not isinstance(selector, str) or selector == "<imports>":
        return 0
    name = selector.rsplit(".", 1)[-1]
    matches = [node.lineno for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
               and node.name == name]
    return matches[0] if matches else 0
