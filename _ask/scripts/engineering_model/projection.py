"""Deterministic machine and Markdown views over an admitted snapshot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from pathlib import PurePosixPath

from .domain import task_states
from .evidence import inspect as inspect_evidence
from .identities import execution_identity
from .snapshot import decode, read_input
from .workbench import build_workbench


def _captured_json(snapshot, path):
    raw = snapshot.files.get(path)
    if raw is None:
        return None
    try:
        return decode(raw)
    except (UnicodeError, ValueError, TypeError):
        return None


def _reference_text(reference):
    """Format canonical, symbol, and path-only references without assuming an ID."""
    path = reference.get("path", "")
    if reference.get("id") is not None:
        return f"{path}#{reference['id']}"
    if reference.get("symbol") is not None:
        return f"{path}::{reference['symbol']}"
    return path


def _work_id_from_spec_path(path):
    parts = PurePosixPath(path).parts if isinstance(path, str) else ()
    if len(parts) == 3 and parts[:2] == ("specs", "current") and parts[2].endswith(".json"):
        work_id = parts[2][:-5]
        if work_id:
            return work_id
    return None


def _attention(model, tasks):
    items = []
    for node in model.get("nodes", []):
        kind, state = node.get("type"), node.get("lifecycle")
        reason = None
        if kind == "decision" and state == "open":
            reason = "decision requires an explicit resolution"
        elif kind == "assumption" and state in {"unverified", "rejected", "retired"}:
            reason = f"assumption is {state}"
        elif kind == "risk" and state == "open":
            reason = "risk is open"
        if reason:
            items.append({"id": node["id"], "type": kind, "status": state, "reason": reason})
    for task in tasks:
        if task["status"] == "blocked":
            items.append({"id": task["id"], "type": "task", "status": "blocked",
                          "reason": "task has unresolved prerequisites",
                          "blockers": task["blockers"]})
    return sorted(items, key=lambda item: (item["type"], item["id"]))


def _hierarchy(model, selected_id=None):
    nodes = {node["id"]: node for node in model.get("nodes", [])}
    children = {identity: [] for identity in nodes}
    parents = set()
    for edge in model.get("edges", []):
        if edge["type"] == "contains" and edge["source"] in nodes and edge["target"] in nodes:
            children[edge["source"]].append(edge["target"])
            parents.add(edge["target"])
    for values in children.values():
        values.sort()

    def branch(identity):
        node = nodes[identity]
        reference = node.get("reference")
        result = {"id": identity, "type": node["type"], "title": node["title"],
                  "lifecycle": node["lifecycle"], "children": [branch(child) for child in children[identity]]}
        if reference is not None:
            result["reference"] = reference
        return result

    roots = [selected_id] if selected_id is not None else sorted(set(nodes) - parents)
    return {"roots": [branch(identity) for identity in roots],
            "node_ids": sorted(nodes)}


def _scenario_views(snapshot, model, evidence_by_reference):
    nodes = {node["id"]: node for node in model.get("nodes", [])}
    covered_by = {}
    for edge in model.get("edges", []):
        if edge["type"] == "covers":
            covered_by.setdefault(edge["target"], []).append(edge["source"])
    result = []
    for node in model.get("nodes", []):
        if node.get("type") != "scenario":
            continue
        reference = node.get("reference", {})
        spec = _captured_json(snapshot, reference.get("path"))
        criteria = spec.get("criteria", []) if isinstance(spec, dict) else []
        criterion = next((item for item in criteria
                          if isinstance(item, dict) and item.get("id") == reference.get("id")), None)
        view = {"id": node["id"], "title": node["title"], "reference": reference}
        if criterion is not None:
            view["criterion_id"] = criterion["id"]
            if model.get("schema") == "ask-engineering-model/v2":
                view["criterion"] = {field: criterion[field] for field in
                                     ("given", "when", "then", "verification_mode")
                                     if field in criterion}
            else:
                for field in ("given", "when", "then", "verification_mode"):
                    view[field] = criterion[field]
        else:
            view["canonical_status"] = "unavailable"
        if model.get("schema") == "ask-engineering-model/v2":
            selector = node.get("case")
            if selector is None:
                view["canonical_status"] = "not-selected" if node.get("lifecycle") == "draft" else "unavailable"
            elif isinstance(selector, dict):
                case_work = selector.get("work_id")
                case_id = selector.get("case_id")
                plan_path = f"work/{case_work}/test-plan.json" if isinstance(case_work, str) else None
                plan = _captured_json(snapshot, plan_path) if plan_path else None
                actual_digest = (hashlib.sha256(json.dumps(
                    plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                    if isinstance(plan, dict) else None)
                tests_for_case = (plan.get("tests", []) if isinstance(plan, dict) else [])
                selected = [item for item in tests_for_case if isinstance(item, dict)
                            and item.get("id") == case_id] if isinstance(tests_for_case, list) else []
                if (isinstance(plan, dict) and plan.get("work_id") == case_work
                        and actual_digest == selector.get("plan_digest") and len(selected) == 1
                        and isinstance(selected[0].get("scenario"), dict)):
                    flow = selected[0]["scenario"]
                    for field in ("given", "when", "then"):
                        if field in flow:
                            view[field] = flow[field]
                    view["canonical_case"] = {"work_id": case_work, "plan_digest": actual_digest,
                                               "case_id": case_id}
                    view["canonical_status"] = "available"
                else:
                    view["canonical_status"] = "unavailable"
            else:
                view["canonical_status"] = "unavailable"
        cases = []
        for test_id in sorted(covered_by.get(node["id"], [])):
            test_node = nodes.get(test_id)
            test_ref = test_node.get("reference", {}) if test_node else {}
            plan = _captured_json(snapshot, test_ref.get("path"))
            tests = plan.get("tests", []) if isinstance(plan, dict) else []
            case = next((item for item in tests
                         if isinstance(item, dict) and item.get("id") == test_ref.get("id")), None)
            case_view = {"node_id": test_id, "reference": test_ref}
            if test_node:
                case_view["title"] = test_node["title"]
            if case is None:
                case_view["canonical_status"] = "unavailable"
            else:
                for field in ("id", "type", "scenario", "expected_assertions", "runner_id", "case_id", "source_paths"):
                    if field in case:
                        case_view[field] = case[field]
                case_view["canonical_status"] = "available"
            cases.append(case_view)
        view["tests"] = cases
        if criterion is not None:
            view["evidence"] = evidence_by_reference.get((reference.get("path"), criterion["id"]))
        result.append(view)
    return result


def _task_context(snapshot, node_id):
    selected = {"spec": [], "plan": []}
    for record in snapshot.passages.values():
        if record.get("node_id") != node_id or record.get("kind") != "context":
            continue
        role = record.get("role")
        if role not in selected:
            continue
        resolution = record.get("resolution")
        resolution = resolution if isinstance(resolution, dict) else {}
        selected[role].append({
            "path": record.get("path"),
            "revision": record.get("revision"),
            "selector": record.get("selector"),
            "state": resolution.get("state", "unavailable"),
            "text": resolution.get("text"),
            "match_count": resolution.get("match_count"),
            "start_line": resolution.get("start_line"),
            "end_line": resolution.get("end_line"),
            "source_sha256": record.get("sha256"),
        })
    return selected


def project(snapshot, root, *, node_id=None, candidate_sha=None, include_evidence=True):
    """Project one immutable snapshot and a read-only evidence inspection."""
    model = snapshot.document
    nodes = {node["id"]: node for node in model.get("nodes", [])}
    if node_id is not None and node_id not in nodes:
        raise ValueError(f"unknown Engineering Model node: {node_id}")
    tasks = task_states(model)
    for task in tasks:
        task["context"] = _task_context(snapshot, task["id"])
    runtime_owners = {snapshot.work_id}
    if isinstance(model.get("nodes"), list):
        for node in model["nodes"]:
            alias = execution_identity(node) if isinstance(node, dict) else None
            if alias is not None:
                runtime_owners.add(alias[0])
    runtime_states = {}
    repository = Path(root).resolve()
    for owner in sorted(runtime_owners):
        status_path = f"work/{owner}/inner-loop/state.json"
        source_status, raw = read_input(repository, status_path)
        if source_status != "present":
            runtime_states[owner] = {"state": None,
                                     "source": "no-runtime-record" if source_status == "missing"
                                     else f"unavailable-{source_status}"}
            continue
        try:
            state = decode(raw)
        except (UnicodeError, ValueError, TypeError):
            state = None
        if (model.get("schema") == "ask-engineering-model/v1" and owner == snapshot.work_id
                and isinstance(state, dict) and isinstance(state.get("tasks"), dict)
                and state.get("schema") is None and state.get("work_id") in {None, owner}):
            runtime_states[owner] = {"state": state, "source": "task-state"}
            continue
        if (not isinstance(state, dict) or state.get("schema") != "ask-inner-loop-state/v1"
                or state.get("work_id") != owner or not isinstance(state.get("tasks"), dict)):
            runtime_states[owner] = {"state": None, "source": "unavailable-malformed-owner-state"}
        else:
            runtime_states[owner] = {"state": state, "source": "inner-loop-state"}
    workbench = build_workbench(snapshot, model, tasks, runtime_states)
    for task in workbench.get("tasks", []):
        product_node_id = task.get("product_node_id")
        if product_node_id is not None:
            task["context"] = _task_context(snapshot, product_node_id)
    evidence_work_ids = {snapshot.work_id}
    if include_evidence:
        for node in model.get("nodes", []):
            if node.get("type") not in {"requirement", "scenario"}:
                continue
            reference = node.get("reference", {})
            work_id = _work_id_from_spec_path(reference.get("path"))
            if work_id:
                evidence_work_ids.add(work_id)
    evidence_by_workstream = ({
        work_id: inspect_evidence(Path(root), work_id, candidate_sha)
        for work_id in sorted(evidence_work_ids)
    } if include_evidence else {})
    evidence_by_reference = {}
    for result in evidence_by_workstream.values():
        for item in result.get("scenarios", []):
            if not isinstance(item, dict):
                continue
            reference = item.get("reference", {})
            key = (reference.get("path"), reference.get("id"))
            if all(key):
                evidence_by_reference[key] = item
    scenarios = _scenario_views(snapshot, model, evidence_by_reference)
    selected_scenarios = None
    if node_id is not None:
        selected = nodes[node_id]
        if selected["type"] == "scenario":
            selected_scenarios = {node_id}
        elif selected["type"] == "test":
            selected_scenarios = {edge["target"] for edge in model.get("edges", [])
                                  if edge["type"] == "covers" and edge["source"] == node_id}
        elif selected.get("reference", {}).get("id"):
            selected_scenarios = {item["id"] for item in model.get("nodes", [])
                                  if item.get("type") == "scenario"
                                  and item.get("reference", {}).get("id") == selected["reference"]["id"]}
        else:
            selected_scenarios = set()
        scenarios = [item for item in scenarios if item["id"] in selected_scenarios]
        tasks = [item for item in tasks if item["id"] == node_id]
    attention = _attention(model, tasks)
    if node_id is not None:
        attention = [item for item in attention if item["id"] == node_id]
    projection = {
        "schema": "ask-engineering-projection/v1",
        "work_id": snapshot.work_id,
        "snapshot": snapshot.identity,
        "model": model,
        "hierarchy": _hierarchy(model, node_id),
        "tasks": tasks,
        "workbench": workbench,
        "attention": attention,
        "scenarios": scenarios,
        "evidence": {"schema": "ask-engineering-evidence-set/v1",
                     "by_workstream": evidence_by_workstream},
    }
    if node_id is not None:
        projection["selected_node"] = nodes[node_id]
    return projection


def markdown(projection):
    """Render a stable textual view without adding computed completion claims."""
    identity = projection["snapshot"]
    lines = [f"# Engineering Model: {projection['work_id']}", "",
             f"Snapshot: `{identity['digest']}`", "", "## Hierarchy"]

    def render_branch(branch, depth=0):
        prefix = "  " * depth + "- "
        lines.append(f"{prefix}`{branch['id']}` ({branch['type']}, {branch['lifecycle']}): {branch['title']}")
        reference = branch.get("reference")
        if reference:
            lines.append("  " * (depth + 1) + f"Reference: `{_reference_text(reference)}`")
        for child in branch["children"]:
            render_branch(child, depth + 1)

    for root in projection["hierarchy"]["roots"]:
        render_branch(root)
    lines.extend(["", "## Tasks"])
    projected_work = projection.get("workbench", {}).get("tasks", [])
    if projection.get("model", {}).get("schema") != "ask-engineering-model/v2":
        for task in projection["tasks"]:
            lines.append(f"- `{task['id']}`: {task['status']} (lifecycle: {task['lifecycle']})")
            for blocker in task["blockers"]:
                lines.append(f"  - Blocked by `{blocker['id']}`: {blocker['reason']}")
    elif projected_work:
        for task in projected_work:
            execution = task.get("execution_identity")
            execution_label = (f"{execution.get('work_id')}:{execution.get('task_id')}"
                               if isinstance(execution, dict) else "unbound")
            product = task.get("product_identity")
            product_label = (f"{product.get('work_id')}:{product.get('node_id')}"
                             if isinstance(product, dict) else "unbound")
            lines.append(f"- `{task['id']}`: {task['status']} (product `{product_label}`, execution `{execution_label}`)")
            if "readiness_status" in task:
                readiness = task.get("readiness_status") or "unavailable"
                readiness_source = task.get("readiness_source", "unavailable")
                lifecycle = task.get("model_lifecycle") or "unavailable"
                runtime = task.get("runtime_status") or "unavailable"
                verification = task.get("verification_status") or "unavailable"
                lines.append(f"  - Readiness: {readiness} (source: {readiness_source}); definition lifecycle: {lifecycle}; "
                             f"runtime status: {runtime} (source: {task.get('status_source', 'unavailable')}); "
                             f"verification status: {verification} (source: {task.get('verification_source', 'unavailable')})")
                for blocker in task.get("readiness_blockers", []):
                    lines.append(f"  - Readiness blocker `{blocker['id']}`: {blocker['reason']}")
            if task.get("outcome"):
                lines.append(f"  - Outcome: {task['outcome']}")
            if task.get("dependencies"):
                lines.append("  - Depends on: " + ", ".join(f"`{item}`" for item in task["dependencies"]))
            if task.get("owned_test_ids"):
                lines.append("  - Scoped tests: " + ", ".join(f"`{item}`" for item in task["owned_test_ids"]))
            for role, passages in task.get("context", {}).items():
                for passage in passages:
                    lines.append(f"  - {role.title()} passage ({passage['state']}): `{passage['path']}`")
                    if passage.get("text"):
                        lines.extend("    " + line for line in passage["text"].rstrip().splitlines())
    else:
        for task in projection["tasks"]:
            lines.append(f"- `{task['id']}`: {task['status']} (lifecycle: {task['lifecycle']})")
            for blocker in task["blockers"]:
                lines.append(f"  - Blocked by `{blocker['id']}`: {blocker['reason']}")
    lines.extend(["", "## Attention"])
    for item in projection["attention"]:
        lines.append(f"- `{item['id']}` ({item['type']}): {item['reason']}")
    lines.extend(["", "## Scenarios"])
    for scenario in projection["scenarios"]:
        lines.extend([f"### `{scenario['id']}`: {scenario['title']}",
                      f"Reference: `{_reference_text(scenario['reference'])}`"])
        if scenario.get("canonical_status") is not None:
            if scenario.get("canonical_status") == "available":
                case = scenario.get("canonical_case", {})
                lines.append(f"Selected canonical case: `{case.get('work_id')}#{case.get('case_id')}`")
            else:
                lines.append(f"Selected canonical case: {scenario['canonical_status']}")
        for field in ("given", "when", "then"):
            if field in scenario:
                value = scenario[field]
                if isinstance(value, list):
                    lines.append(f"{field.title()}:")
                    lines.extend(f"- {entry}" for entry in value)
                else:
                    lines.append(f"{field.title()}: {value}")
        if scenario.get("canonical_status") == "unavailable":
            lines.append("Canonical scenario details: unavailable in captured snapshot")
        record = scenario.get("evidence")
        if record is None:
            lines.append("Adapter evidence record: none returned for this criterion")
        else:
            lines.append("Adapter evidence record: " + json.dumps(record, ensure_ascii=False, sort_keys=True))
        for case in scenario["tests"]:
            lines.append(f"- Test node `{case['node_id']}` reference: `{_reference_text(case['reference'])}`")
            if case.get("canonical_status") == "available":
                if case.get("case_id"):
                    lines.append(f"  Case: `{case['case_id']}` via `{case['runner_id']}` ({case['type']})")
                else:
                    lines.append(f"  Planned test: `{case.get('id', case['node_id'])}`")
                for assertion in case.get("expected_assertions", []):
                    lines.append(f"  Planned assertions for `{assertion['criterion_id']}`:")
                    lines.extend(f"  - {check}" for check in assertion["checks"])
            else:
                lines.append("  Planned case details: unavailable in captured snapshot")
    evidence = projection["evidence"]
    lines.extend(["", "## Evidence"])
    for work_id, inspection in sorted(evidence["by_workstream"].items()):
        lines.extend([f"### `{work_id}`", f"Status: {inspection.get('status', 'unknown')}",
                      f"Candidate: `{inspection.get('candidate_sha')}`",
                      f"Current revision: `{inspection.get('current_sha')}`",
                      f"Historical: {str(bool(inspection.get('historical'))).lower()}"])
        completion = inspection.get("completion")
        if completion is not None:
            lines.append("Adapter completion details: " + json.dumps(completion, ensure_ascii=False, sort_keys=True))
    return "\n".join(lines) + "\n"
