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


def _self_method_references(nodes):
    """Find class method references through ``self``, including callbacks."""
    return {child.attr for node in nodes for child in ast.walk(node)
            if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name)
            and child.value.id == "self"}


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
        selector_parts = selector.split(".")
        candidates = []
        normalized_selectors = {}
        for path in paths:
            if not _safe_path(path):
                continue
            path_parts = list(PurePosixPath(path).with_suffix("").parts)
            for index in range(len(selector_parts) - 1, -1, -1):
                if selector_parts[index - len(path_parts):index] == path_parts:
                    candidates.append(path)
                    normalized_selectors[path] = ".".join(
                        [PurePosixPath(path).stem, *selector_parts[index:]])
                    break
        if not candidates and len(paths) == 1 and _safe_path(paths[0]):
            candidates = list(paths)
            normalized_selectors[paths[0]] = selector
        if len(candidates) != 1:
            raise ValueError("qualified test module does not select one accepted source path")
        source_path = candidates[0]
        local_selector = normalized_selectors[source_path]
        module = PurePosixPath(source_path).stem
        text = _blob(root, sha, source_path).decode("utf-8")
        tree = ast.parse(text, filename=source_path)
        selected_module, selected, _start, _end = _selector_node(tree, local_selector)
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

        declared_context = test.get("source_context", [])
        if not isinstance(declared_context, list):
            raise ValueError("curated source context must be an array")
        for entry in declared_context:
            if (not isinstance(entry, dict) or not _safe_path(entry.get("path"))
                    or not isinstance(entry.get("qualified_name"), str)
                    or not isinstance(entry.get("role"), str)):
                raise ValueError("curated source context entry is malformed")
            revision = entry.get("revision")
            if revision == "snapshot":
                revision = current or sha
            try:
                context_sha = _commit(root, revision)
                context_text = _blob(root, context_sha, entry["path"]).decode("utf-8")
                context_tree = ast.parse(context_text, filename=entry["path"])
                selector_parts = entry["qualified_name"].split(".")
                path_parts = list(PurePosixPath(entry["path"]).with_suffix("").parts)
                source_module = PurePosixPath(entry["path"]).stem
                context_selector = entry["qualified_name"]
                for index in range(len(selector_parts) - 1, -1, -1):
                    if selector_parts[index - len(path_parts):index] == path_parts:
                        context_selector = ".".join([source_module, *selector_parts[index:]])
                        break
                else:
                    if selector_parts[0] != source_module:
                        raise ValueError("curated selector does not identify its source path")
                selected_module, context_node, _begin, _finish = _selector_node(
                    context_tree, context_selector)
                if selected_module != source_module:
                    raise ValueError("curated selector module differs from source path")
                record = _record(context_text, context_node, entry["qualified_name"],
                                 entry["role"], entry["path"], context_sha, current)
                record["explanation"] = entry.get("explanation")
                context.append(record)
            except (OSError, UnicodeError, ValueError, TypeError, SyntaxError,
                    subprocess.SubprocessError) as exc:
                context.append({"selector": entry.get("qualified_name"),
                                "role": entry.get("role"), "status": "missing", "source": "",
                                "source_path": entry.get("path"), "source_sha": None,
                                "current_sha": current, "explanation": entry.get("explanation"),
                                "diagnostic": str(exc)})

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
            for name in _self_method_references([node]):
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
        pending_functions = list(module_names & top_functions.keys())
        included_functions = set()
        while pending_functions:
            name = pending_functions.pop()
            if name in included_functions:
                continue
            included_functions.add(name)
            function = top_functions[name]
            context.append(_record(text, function, f"{module}.{name}", "helper",
                                   source_path, sha, current))
            dependencies = _loaded_names([function])
            module_names.update(dependencies)
            pending_functions.extend(dependencies.intersection(top_functions).difference(included_functions))

        assignments = {}
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    assignments.update({name: node for name in _target_names(target)})
        fixture_names = set()
        pending_fixtures = list(module_names & assignments.keys())
        while pending_fixtures:
            name = pending_fixtures.pop()
            if name in fixture_names:
                continue
            fixture_names.add(name)
            assignment = assignments[name]
            dependencies = _loaded_names([assignment]) & assignments.keys()
            module_names.update(_loaded_names([assignment]))
            pending_fixtures.extend(dependencies - fixture_names)
        for name in sorted(fixture_names):
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
