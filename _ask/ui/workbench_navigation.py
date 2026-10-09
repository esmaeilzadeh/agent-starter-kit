"""Build and render one connected Epic-to-Result work outline."""
from __future__ import annotations

from collections import defaultdict

import streamlit as st

from workbench_context import STATE_ROUTE, back, navigate, route_to


def _contains(model: dict) -> tuple[dict[str, list[str]], dict[str, str]]:
    children: dict[str, list[str]] = defaultdict(list)
    parent: dict[str, str] = {}
    for edge in model.get("edges", []):
        if edge.get("type") == "contains":
            children[edge.get("source")].append(edge.get("target"))
            parent[edge.get("target")] = edge.get("source")
    return children, parent


def _append(entries, ancestors, route_id, label, kind, path, *, node_id=None, indent=0):
    entries.append({"route_id": route_id, "label": label, "kind": kind,
                    "node_id": node_id or route_id, "path": path, "indent": indent})
    ancestors[route_id] = path


def build_outline(projection: dict) -> dict:
    """Join admitted hierarchy with recorded task/test mappings for navigation."""
    model = projection.get("model", {})
    nodes = {node["id"]: node for node in model.get("nodes", [])}
    children, parent = _contains(model)
    roots = [node_id for node_id, node in nodes.items()
             if node.get("type") == "intent" and node_id not in parent]
    if not roots:
        roots = [node_id for node_id, node in nodes.items()
                 if node.get("type") == "feature" and node_id not in parent]
    if not roots:
        roots = sorted(set(nodes) - set(parent))
    roots = sorted(roots)

    stories = {item["id"]: item for item in projection.get("workbench", {}).get("stories", [])}
    scenarios = {item["id"]: item for item in projection.get("scenarios", [])}
    tasks = {item["id"]: item for item in projection.get("tasks", [])}
    tests = {item["id"]: item for item in projection.get("workbench", {}).get("tests", [])}
    entries: list[dict] = []
    ancestors: dict[str, list[tuple[str, str]]] = {}
    emitted_tasks: set[str] = set()
    emitted_tests: set[str] = set()

    def scenario_ids_for_story(story_id):
        explicit = set(stories.get(story_id, {}).get("scenario_ids", []))
        explicit.update(child for child in children.get(story_id, [])
                        if nodes.get(child, {}).get("type") == "scenario")
        return sorted(explicit & set(scenarios))

    def tasks_for_scenario(scenario_id):
        return sorted(task_id for task_id, task in tasks.items()
                      if any(link.get("id") == scenario_id
                             for link in task.get("related_scenarios", [])))

    def tests_for_task(task_id, scenario_id):
        return sorted(test_id for test_id, test in tests.items()
                      if test_id not in emitted_tests and scenario_id in test.get("scenario_ids", [])
                      and (test.get("owner_task_id") == task_id or any(
                          link.get("task_id") == task_id for link in test.get("related_tasks", []))))

    def add_test(test_id, path, indent):
        test = tests[test_id]
        route_id = f"test:{test_id}"
        label = test.get("title") or test_id
        _append(entries, ancestors, route_id, label, "test", [*path, (route_id, label)],
                node_id=test_id, indent=indent)
        result_id = f"result:{test_id}"
        _append(entries, ancestors, result_id, "Result / evidence", "result",
                [*path, (route_id, label), (result_id, "Result / evidence")],
                node_id=test_id, indent=indent + 1)
        emitted_tests.add(test_id)

    def add_task(task_id, path, indent, scenario_id):
        if task_id in emitted_tasks:
            return
        task = tasks[task_id]
        label = task.get("title") or task_id
        task_path = [*path, (task_id, label)]
        _append(entries, ancestors, task_id, label, "task", task_path, indent=indent)
        emitted_tasks.add(task_id)
        related = tests_for_task(task_id, scenario_id) if scenario_id else []
        for test_id in related:
            add_test(test_id, task_path, indent + 1)

    def add_scenario(scenario_id, path, indent):
        scenario = scenarios[scenario_id]
        label = scenario.get("title") or scenario_id
        scenario_path = [*path, (scenario_id, label)]
        _append(entries, ancestors, scenario_id, label, "scenario", scenario_path,
                indent=indent)
        linked_tasks = tasks_for_scenario(scenario_id)
        for task_id in linked_tasks:
            add_task(task_id, scenario_path, indent + 1, scenario_id)
        directly_linked_tests = sorted(test_id for test_id, test in tests.items()
                                       if test_id not in emitted_tests
                                       and scenario_id in test.get("scenario_ids", []))
        for test_id in directly_linked_tests:
            test = tests[test_id]
            owner = test.get("owner_task_id")
            if not linked_tasks or (owner and owner not in linked_tasks):
                if owner in tasks:
                    add_task(owner, scenario_path, indent + 1, scenario_id)
                else:
                    add_test(test_id, scenario_path, indent + 1)

    root_routes = []
    for root_id in roots:
        root = nodes[root_id]
        title = root.get("title") or root_id
        epic_path = [(root_id, title)]
        _append(entries, ancestors, root_id, title, "epic", epic_path, indent=0)
        root_routes.append(root_id)
        descendants = set()
        pending = list(children.get(root_id, []))
        while pending:
            current = pending.pop()
            if current in descendants or current not in nodes:
                continue
            descendants.add(current)
            pending.extend(children.get(current, []))

        epic_stories = sorted(story_id for story_id in stories if story_id in descendants)
        story_scenarios: set[str] = set()
        for story_id in epic_stories:
            story = stories[story_id]
            story_title = story.get("title") or story_id
            story_path = [*epic_path, (story_id, story_title)]
            _append(entries, ancestors, story_id, story_title, "story", story_path,
                    indent=1)
            story_scenarios.update(scenario_ids_for_story(story_id))
            for scenario_id in scenario_ids_for_story(story_id):
                add_scenario(scenario_id, story_path, 2)

        direct_scenarios = sorted(scenario_id for scenario_id in scenarios
                                  if scenario_id in descendants and scenario_id not in story_scenarios)
        if direct_scenarios:
            group_id = f"unassigned-scenarios:{root_id}"
            group_label = "Scenarios without a recorded story"
            group_path = [*epic_path, (group_id, group_label)]
            _append(entries, ancestors, group_id, group_label, "group", group_path, indent=1)
            for scenario_id in direct_scenarios:
                add_scenario(scenario_id, group_path, 2)

        unrelated_tasks = sorted(task_id for task_id, task in tasks.items()
                                 if not task.get("related_scenarios") and task_id not in emitted_tasks)
        if unrelated_tasks:
            group_id = f"unmapped-tasks:{root_id}"
            group_label = "Tasks without a scenario mapping"
            group_path = [*epic_path, (group_id, group_label)]
            _append(entries, ancestors, group_id, group_label, "group", group_path, indent=1)
            for task_id in unrelated_tasks:
                add_task(task_id, group_path, 2, None)

        decisions = sorted(node_id for node_id in descendants
                           if nodes.get(node_id, {}).get("type") == "decision"
                           and nodes[node_id].get("lifecycle") == "open")
        for decision_id in decisions:
            decision_route = "decision" if len(decisions) == 1 else f"decision:{decision_id}"
            decision_label = "Decision · " + (nodes[decision_id].get("title") or decision_id)
            _append(entries, ancestors, decision_route, decision_label, "decision",
                    [*epic_path, (decision_route, decision_label)], node_id=decision_id,
                    indent=1)

    return {"entries": entries, "ancestors": ancestors, "roots": root_routes}


def render_outline(projection: dict) -> dict:
    """Render accessible native buttons for every linked level of the outline."""
    outline = build_outline(projection)
    st.markdown("**Epic**")
    for entry in outline["entries"]:
        label = entry["label"]
        if entry["kind"] == "group":
            st.caption(label)
            continue
        display = ("　" * entry["indent"]) + label
        key = f"route:{entry['route_id']}"
        if st.button(display, key=key, type="primary" if st.session_state.get(STATE_ROUTE)
                     == entry["route_id"] else "secondary", width="stretch"):
            navigate(st.session_state, entry["route_id"])
    return outline


def render_breadcrumbs(outline: dict, route_id: str) -> None:
    path = outline["ancestors"].get(route_id, [])
    with st.container(horizontal=True, vertical_alignment="center"):
        for index, (identity, label) in enumerate(path):
            if index:
                st.caption("/")
            if identity == route_id:
                st.markdown(f"**{label}**")
            elif st.button(label, key=f"breadcrumb:{identity}", type="tertiary"):
                route_to(st.session_state, identity)
        if st.button("Back", key="route:back", icon=":material/arrow_back:",
                     disabled=not st.session_state.get("_engineering_route_history")):
            back(st.session_state, outline["roots"][0] if outline["roots"] else "")
