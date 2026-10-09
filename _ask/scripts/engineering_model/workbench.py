"""Join captured task scopes to Engineering Model relationships."""
from __future__ import annotations

from .snapshot import decode
from inner_loop.yaml_lite import parse_yaml


def _captured_json(snapshot, path):
    raw = snapshot.files.get(path)
    if raw is None:
        return None
    try:
        return decode(raw)
    except (UnicodeError, ValueError, TypeError):
        return None


def build_workbench(snapshot, model, model_task_states, runtime_state=None):
    """Return task, story, and test relationships without inventing history."""
    work_id = snapshot.work_id
    plan_path = f"work/{work_id}/test-plan.json"
    plan = _captured_json(snapshot, plan_path)
    graph_path = f"work/{work_id}/inner-loop/tasks.yaml"
    graph_raw = snapshot.files.get(graph_path)
    try:
        graph = parse_yaml(graph_raw.decode("utf-8")) if graph_raw is not None else {}
    except (UnicodeError, ValueError, TypeError):
        graph = {}
    if not isinstance(plan, dict) or plan.get("work_id") != work_id:
        plan = {}
    if not isinstance(graph, dict) or graph.get("work_id", work_id) != work_id:
        graph = {}

    graph_tasks = graph.get("tasks", []) if isinstance(graph.get("tasks", []), list) else []
    task_definitions = {task.get("id"): task for task in graph_tasks
                        if isinstance(task, dict) and isinstance(task.get("id"), str)}
    scopes = plan.get("task_scopes", []) if isinstance(plan.get("task_scopes", []), list) else []
    tests = plan.get("tests", []) if isinstance(plan.get("tests", []), list) else []
    test_definitions = {test.get("id"): test for test in tests
                        if isinstance(test, dict) and isinstance(test.get("id"), str)}
    scope_tests = {}
    orphan_scope_task_ids = set()
    for scope in scopes:
        if not isinstance(scope, dict) or not isinstance(scope.get("task_id"), str):
            continue
        task_id = scope["task_id"]
        if task_id not in task_definitions:
            orphan_scope_task_ids.add(task_id)
        scope_tests.setdefault(task_id, set()).update(
            test_id for test_id in scope.get("test_ids", [])
            if isinstance(test_id, str) and test_id in test_definitions
        )

    nodes = {node.get("id"): node for node in model.get("nodes", [])
             if isinstance(node, dict) and isinstance(node.get("id"), str)}
    test_node_by_case = {}
    scenario_ids_by_case = {}
    explicit_scenarios_by_task = {}
    scenarios_by_criterion = {}
    canonical_spec_path = f"specs/current/{work_id}.json"
    for node in nodes.values():
        if node.get("type") == "scenario":
            ref = node.get("reference", {})
            if ref.get("path") == canonical_spec_path and isinstance(ref.get("id"), str):
                scenarios_by_criterion.setdefault(ref["id"], set()).add(node["id"])
        if node.get("type") != "test":
            continue
        ref = node.get("reference", {})
        if ref.get("path") != plan_path or not isinstance(ref.get("id"), str):
            continue
        case_id = ref["id"]
        test_node_by_case.setdefault(case_id, []).append(node)
        scenario_ids_by_case.setdefault(case_id, set())
    for case_id, test in test_definitions.items():
        scenario_ids_by_case.setdefault(case_id, set()).update(
            scenario_id
            for criterion_id in test.get("criterion_ids", [])
            if isinstance(criterion_id, str)
            for scenario_id in scenarios_by_criterion.get(criterion_id, set())
        )
    for edge in model.get("edges", []):
        if not isinstance(edge, dict):
            continue
        if edge.get("type") == "implements":
            implementation = nodes.get(edge.get("source"))
            target = nodes.get(edge.get("target"))
            if implementation and target and implementation.get("type") == "implementation":
                if target.get("type") == "task":
                    explicit_scenarios_by_task.setdefault(target["id"], set())
                elif target.get("type") == "scenario":
                    for relation in model.get("edges", []):
                        if relation.get("type") != "implements" or relation.get("source") != edge["source"]:
                            continue
                        task = nodes.get(relation.get("target"))
                        if task and task.get("type") == "task":
                            explicit_scenarios_by_task.setdefault(task["id"], set()).add(target["id"])
            continue
        if edge.get("type") != "covers":
            continue
        test_node = nodes.get(edge.get("source"))
        scenario = nodes.get(edge.get("target"))
        ref = test_node.get("reference", {}) if test_node else {}
        if (test_node and scenario and ref.get("path") == plan_path
                and isinstance(ref.get("id"), str) and scenario.get("type") == "scenario"):
            scenario_ids_by_case.setdefault(ref["id"], set()).add(scenario["id"])

    runtime_tasks = (runtime_state.get("tasks", {}) if isinstance(runtime_state, dict)
                     and runtime_state.get("work_id") == work_id else {})
    task_rows = []
    for task_id, definition in sorted(task_definitions.items()):
        record = runtime_tasks.get(task_id) if isinstance(runtime_tasks, dict) else None
        state = record.get("status") if isinstance(record, dict) else None
        status = {
            "running": "active", "integrated": "completed", "blocked": "blocked",
            "failed": "failed", "escalated": "blocked", "cancelled": "cancelled",
        }.get(state, "planned")
        owned_tests = sorted(scope_tests.get(task_id, set()))
        mapped_scenarios = {scenario for test_id in owned_tests
                            for scenario in scenario_ids_by_case.get(test_id, set())}
        explicit_scenarios = explicit_scenarios_by_task.get(task_id, set())
        scenarios = sorted(mapped_scenarios | explicit_scenarios)
        task_rows.append({
            "id": task_id,
            "title": definition.get("title", task_id),
            "outcome": definition.get("outcome", ""),
            "dependencies": sorted(x for x in definition.get("depends_on", []) if isinstance(x, str)),
            "owned_paths": sorted(x for x in definition.get("owned_paths", []) if isinstance(x, str)),
            "owned_test_ids": owned_tests,
            "related_scenarios": [
                {"id": scenario,
                 "via": "recorded-implementation" if scenario in explicit_scenarios else "test-mapping"}
                for scenario in scenarios
            ],
            "status": status,
            "status_source": "task-state" if record else "no-runtime-record",
            "record_source": "task-graph",
            "runtime_status": state,
            "result_path": record.get("result_path") if isinstance(record, dict) else None,
        })
    known_task_ids = set(task_definitions)
    for task in model_task_states:
        task_id = task.get("id")
        if task_id in known_task_ids:
            continue
        node = nodes.get(task_id, {})
        task_rows.append({
            "id": task_id, "title": node.get("title", task_id), "outcome": "",
            "dependencies": [], "owned_paths": [], "owned_test_ids": [],
            "related_scenarios": [
                {"id": scenario, "via": "recorded-implementation"}
                for scenario in sorted(explicit_scenarios_by_task.get(task_id, set()))
            ], "status": "not-recorded",
            "status_source": "no-task-record", "record_source": "engineering-model",
            "runtime_status": None, "result_path": None,
            "lifecycle": task.get("lifecycle"), "model_status": task.get("status"),
        })
    task_rows.sort(key=lambda item: item["id"])

    owner_by_test = {}
    for task_id, owned_ids in scope_tests.items():
        if task_id not in task_definitions:
            continue
        for test_id in owned_ids:
            owner_by_test.setdefault(test_id, []).append(task_id)
    test_rows = []
    for test_id, test in sorted(test_definitions.items()):
        owners = sorted(owner_by_test.get(test_id, []))
        scenario_ids = sorted(scenario_ids_by_case.get(test_id, set()))
        related_tasks = set()
        for scenario_id in scenario_ids:
            for task in task_rows:
                if any(link["id"] == scenario_id for link in task.get("related_scenarios", [])):
                    related_tasks.add(task["id"])
        owner = owners[0] if len(owners) == 1 else None
        test_rows.append({
            "id": test_id,
            "title": next((node.get("title") for node in test_node_by_case.get(test_id, [])), test_id),
            "type": test.get("type"),
            "scenario_ids": scenario_ids,
            "owner_task_id": owner,
            "ownership_status": "owned" if owner else "unowned-or-ambiguous",
            "related_tasks": [{"task_id": task_id, "via": "scenario-coverage"}
                              for task_id in sorted(related_tasks) if task_id != owner],
        })

    story_rows = []
    story_scenarios = set()
    for story in nodes.values():
        if story.get("type") != "story":
            continue
        scenario_ids = sorted(edge["target"] for edge in model.get("edges", [])
                              if edge.get("type") == "contains" and edge.get("source") == story["id"]
                              and nodes.get(edge.get("target"), {}).get("type") == "scenario")
        story_scenarios.update(scenario_ids)
        story_rows.append({"id": story["id"], "title": story["title"],
                           "scenario_ids": scenario_ids, "record_source": "engineering-model"})
    all_scenarios = sorted(node["id"] for node in nodes.values() if node.get("type") == "scenario")
    return {
        "tasks": task_rows,
        "tests": test_rows,
        "stories": sorted(story_rows, key=lambda item: item["id"]),
        "unassigned_scenario_ids": sorted(set(all_scenarios) - story_scenarios),
        "orphan_scope_task_ids": sorted(orphan_scope_task_ids),
    }
