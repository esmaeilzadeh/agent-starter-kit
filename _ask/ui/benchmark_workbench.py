"""Reproducible browser latency harness for an Engineering Workbench model.

The harness starts only servers on ephemeral local ports and binds raw samples to
the app source and the supplied model checkout. Run as a module from the repo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import time
from importlib.metadata import version, PackageNotFoundError
from urllib.error import URLError
from urllib.request import urlopen
import yaml

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))

from engineering_model.projection import project
from engineering_model.admission import admit, validate_current
from engineering_model.workbench_evidence import execution_history
from workbench_navigation import build_outline


def _key_class(key: str) -> str:
    import re
    return "st-key-" + re.sub(r"[^A-Za-z0-9_-]", "-", key)


def structural_workload(task_count: int) -> dict:
    """Measure projection for a fully admitted deterministic task/test graph."""
    work_id = f"scale-{task_count}"
    with tempfile.TemporaryDirectory(prefix=f"ask-workbench-scale-{task_count}-") as temporary:
        root = Path(temporary)
        (root / f"work/{work_id}/inner-loop").mkdir(parents=True)
        (root / "specs/current").mkdir(parents=True)
        (root / "tests").mkdir()
        spec = {"schema": "ask-spec/v1", "work_id": work_id, "revision": 1,
                "criteria": [{"id": "C1", "given": "Input", "when": "Rendered",
                              "then": ["Output"], "verification_mode": "tests"}]}
        spec_bytes = json.dumps(spec, sort_keys=True).encode()
        (root / f"specs/current/{work_id}.json").write_bytes(spec_bytes)
        (root / f"specs/current/{work_id}.md").write_text("# Structural workload\n", encoding="utf-8")
        spec_digest = hashlib.sha256(json.dumps(
            spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        plan = {"schema": "ask-test-plan/v1", "work_id": work_id, "spec_digest": spec_digest,
                "obligations": [{"criterion_id": "C1", "required_types": ["unit"]}],
                "runners": [{"id": "scale", "adapter": "unittest",
                             "argv": ["python3", "-m", "unittest", "test_scale"]}],
                "task_scopes": [], "tests": []}
        nodes = [
            {"id": "purpose", "type": "intent", "title": "Scale fixture", "lifecycle": "active"},
            {"id": "requirement", "type": "requirement", "title": "Requirement", "lifecycle": "active",
             "reference": {"path": f"specs/current/{work_id}.json", "id": "C1"}},
            {"id": "scenario", "type": "scenario", "title": "Shared behavior", "lifecycle": "active",
             "reference": {"path": f"specs/current/{work_id}.json", "id": "C1"}},
        ]
        edges = [{"type": "contains", "source": "purpose", "target": "requirement"},
                 {"type": "contains", "source": "requirement", "target": "scenario"}]
        graph_lines = ["schema: ask-inner-loop-tasks/v1", f"work_id: {work_id}", "tasks:"]
        source_paths = []
        for index in range(task_count):
            task_id, test_id, case_node = f"task-{index:04d}", f"TEST-{index:04d}", f"case-{index:04d}"
            source_path = f"tests/test_{index:04d}.py"
            source_paths.append(source_path)
            nodes.extend([
                {"id": task_id, "type": "task", "title": f"Task {index:04d}", "lifecycle": "planned"},
                {"id": case_node, "type": "test", "title": test_id, "lifecycle": "active",
                 "reference": {"path": f"work/{work_id}/test-plan.json", "id": test_id}},
            ])
            edges.extend([
                {"type": "contains", "source": "purpose", "target": task_id},
                {"type": "covers", "source": case_node, "target": "scenario"},
            ])
            graph_lines.extend((f"  - id: {task_id}", f"    title: Task {index:04d}",
                                "    outcome: Inspect scoped behavior", "    depends_on: []",
                                f"    owned_paths: [src/module-{index:04d}.py]"))
            plan["task_scopes"].append({"task_id": task_id, "test_ids": [test_id]})
            plan["tests"].append({
                "id": test_id, "criterion_ids": ["C1"], "type": "unit", "change_kind": "new",
                "runner_id": "scale", "case_id": f"test_scale.Cases.test_{index:04d}",
                "source_paths": [source_path],
                "scenario": {"given": "Input", "when": "Rendered", "then": ["Output"]},
                "expected_assertions": [{"criterion_id": "C1", "checks": ["Output"]}],
            })
        model = {"schema": "ask-engineering-model/v1", "work_id": work_id, "revision": 1,
                 "nodes": nodes, "edges": edges}
        docs = {
            f"work/{work_id}/engineering-model.json": json.dumps(model, sort_keys=True).encode(),
            f"work/{work_id}/test-plan.json": json.dumps(plan, sort_keys=True).encode(),
            f"work/{work_id}/inner-loop/tasks.yaml": ("\n".join(graph_lines) + "\n").encode(),
            f"specs/current/{work_id}.json": spec_bytes,
            f"specs/current/{work_id}.md": b"# Structural workload\n",
        }
        (root / f"work/{work_id}/engineering-model.json").write_bytes(docs[f"work/{work_id}/engineering-model.json"])
        (root / f"work/{work_id}/test-plan.json").write_bytes(docs[f"work/{work_id}/test-plan.json"])
        (root / f"work/{work_id}/inner-loop/tasks.yaml").write_bytes(docs[f"work/{work_id}/inner-loop/tasks.yaml"])
        for index, path in enumerate(source_paths):
            (root / path).write_text(f"def test_{index:04d}():\n    assert True\n", encoding="utf-8")
        snapshot, validation_errors = validate_current(root, work_id)
        if validation_errors:
            raise AssertionError(f"scale-{task_count} fixture is not valid: {validation_errors[:3]}")
        admitted, admission_errors = admit(root, work_id)
        if admission_errors:
            raise AssertionError(f"scale-{task_count} fixture was not admitted: {admission_errors[:3]}")
        if admitted.identity != snapshot.identity:
            raise AssertionError("admission changed the validated source identity")
        projection_samples, outline_samples = [], []
        for _ in range(5):
            started = time.perf_counter()
            projected = project(admitted, root, include_evidence=False)
            projection_samples.append((time.perf_counter() - started) * 1000)
            started = time.perf_counter()
            outline = build_outline(projected)
            outline_samples.append((time.perf_counter() - started) * 1000)
            assert len(projected["workbench"]["tasks"]) == task_count
            assert len(projected["workbench"]["tests"]) == task_count
            assert sum(entry["kind"] == "task" for entry in outline["entries"]) == task_count
            assert sum(entry["kind"] == "test" for entry in outline["entries"]) == task_count
        return {"task_count": task_count, "test_count": len(plan["tests"]),
                "model_node_count": len(model["nodes"]), "graph_edge_count": len(model["edges"]),
                "source_file_count": len(set(source_paths)),
                "admitted": True, "evidence_included": False,
                "document_bytes": {path: len(raw) for path, raw in docs.items()},
                "total_document_bytes": sum(map(len, docs.values())),
                "projection_ms": projection_samples, "outline_ms": outline_samples}


def digest_tree(root: Path, paths):
    digest = hashlib.sha256()
    sizes = {}
    for relative in paths:
        path = root / relative
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        digest.update(relative.encode() + b"\0" + raw)
        sizes[relative] = len(raw)
    return digest.hexdigest(), sizes


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_server(model_root: Path, work_id: str | None = None):
    port = free_port()
    env = dict(os.environ, ASK_MODEL_ROOT=str(model_root), ASK_PYTHON=sys.executable,
               PYTHONPATH=str(ROOT / "_ask/scripts"))
    if work_id:
        env["ASK_WORK_ID"] = work_id
    started = time.perf_counter()
    process = subprocess.Popen([str(ROOT / "ask"), "ui", "--server.headless=true",
                                f"--server.port={port}", "--server.address=127.0.0.1"],
                               cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    return process, f"http://127.0.0.1:{port}", started


def await_http(process, url, timeout=20):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Streamlit exited during startup: {process.returncode}")
        try:
            with urlopen(url, timeout=.5):
                return
        except (URLError, TimeoutError):
            time.sleep(.05)
    raise TimeoutError("Streamlit HTTP startup exceeded the harness timeout")


def ready(page, root_route="purpose", root_title="Purpose", work_id=None):
    page.get_by_role("heading", name="Engineering workbench", exact=True).wait_for(timeout=10000)
    if work_id:
        selector = page.get_by_label("Workstream")
        selector.wait_for(timeout=10000)
        if selector.input_value() != work_id:
            selector.click()
            selector.fill(work_id)
            selector.press("ArrowDown")
            page.get_by_role("option", name=work_id, exact=True).click()
            expect(selector).to_have_value(work_id, timeout=10000)
    selected = page.locator(f'[class~="{_key_class("route:" + root_route)}"]').get_by_role("button")
    selected.wait_for(timeout=10000)
    expect(selected).to_have_attribute("kind", "primary", timeout=10000)
    expect(page.get_by_role("heading", name=root_title, exact=True)).to_be_visible(timeout=10000)
    for label in ("Stories and scenarios", "Task progress", "Needs attention",
                  "Scenarios", "Tasks", "Blocked tasks", "Open decisions"):
        expect(page.get_by_text(label, exact=True)).to_be_visible(timeout=10000)
    return selected


def route_click(page, route_id, detail_heading):
    button = page.locator(f'[class~="{_key_class("route:" + route_id)}"]').get_by_role("button")
    if not button.count():
        raise AssertionError(f"required workbench route {route_id!r} is missing")
    button.click()
    expect(button).to_have_attribute("kind", "primary", timeout=10000)
    expect(page.get_by_role("heading", name=detail_heading, exact=True)).to_be_visible(timeout=10000)


def run(model_root: Path, work_id: str, warm_samples=20, cold_samples=5,
        output_path: Path | None = None, test_id: str = "E"):
    sources, sizes = digest_tree(ROOT, [
        "_ask/ui/streamlit_app.py", "_ask/ui/workbench_loading.py",
        "_ask/ui/workbench_navigation.py", "_ask/ui/workbench_tests.py",
        "_ask/ui/workbench_tasks.py", "_ask/scripts/engineering_model/workbench.py",
    ])
    try:
        model_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=model_root,
                                    capture_output=True, text=True, timeout=3, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        model_head = "gitless"
    model_paths = [f"work/{work_id}/engineering-model.json", f"work/{work_id}/test-plan.json"]
    model_digest, model_sizes = digest_tree(model_root, model_paths)
    workload_paths = [*model_paths, f"work/{work_id}/inner-loop/tasks.yaml",
                      f"specs/current/{work_id}.json", f"specs/current/{work_id}.md"]
    workload_digest, workload_sizes = digest_tree(model_root, workload_paths)
    model_document = json.loads((model_root / model_paths[0]).read_text(encoding="utf-8"))
    plan_document = json.loads((model_root / model_paths[1]).read_text(encoding="utf-8"))
    admitted_snapshot, admission_errors = validate_current(model_root, work_id)
    if admission_errors:
        raise ValueError("benchmark requires an admitted workstream: " + "; ".join(
            str(item.get("message", item)) for item in admission_errors))
    current_spec = json.loads(admitted_snapshot.files[f"specs/current/{work_id}.json"])
    current_plan = json.loads(admitted_snapshot.files[model_paths[1]])
    canonical = lambda value: hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    pilot_test = next((item for item in current_plan.get("tests", [])
                       if item.get("id") == test_id), None)
    if pilot_test is None:
        raise ValueError(f"benchmark workstream has no selected {test_id!r} test case")
    projection = project(admitted_snapshot, model_root, include_evidence=False)
    outline = build_outline(projection)
    root_route = outline["roots"][0]
    root_title = next(entry["label"] for entry in outline["entries"]
                      if entry["route_id"] == root_route)
    projected_test = next(item for item in projection["workbench"]["tests"]
                          if item.get("id") == test_id)
    scenario_id = next(iter(projected_test.get("scenario_ids", [])), None)
    scenario = next((item for item in projection.get("scenarios", [])
                     if item.get("id") == scenario_id), None)
    if scenario is None:
        raise ValueError(f"selected test {test_id!r} has no admitted scenario")
    scenario_title = str(scenario.get("title") or scenario_id)
    case_id = str(pilot_test.get("case_id", ""))
    source_paths = list(projected_test.get("source_paths", []))
    source_path = str(source_paths[0]) if source_paths else ""
    expected_history = execution_history(
        model_root, work_id, pilot_test, spec_digest=canonical(current_spec),
        plan_digest=canonical(current_plan), candidate_sha=model_head)
    if expected_history.get("status") != "available":
        raise ValueError("benchmark fixture retained history is unavailable: " +
                         str(expected_history.get("diagnostic")))
    expected_outcomes = [str(item.get("outcome", "unavailable")).replace("_", " ").title()
                         for item in expected_history.get("runs", [])]
    graph_path = model_root / workload_paths[2]
    graph_document = (yaml.safe_load(graph_path.read_text(encoding="utf-8"))
                      if graph_path.is_file() else {"tasks": []}) or {"tasks": []}
    code_candidate_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, check=False).stdout.strip() or "unknown"
    try:
        browser_version = version("playwright")
        streamlit_version = version("streamlit")
    except PackageNotFoundError:
        browser_version = streamlit_version = "unknown"
    data = {"code_candidate_sha": code_candidate_sha,
            "code_source_sha256": sources, "model_root": str(model_root), "model_work_id": work_id,
            "model_git_sha": model_head, "model_input_sha256": model_digest,
            "code_file_bytes": sizes, "model_file_bytes": model_sizes,
            "environment": {"python": sys.version, "platform": platform.platform(),
                            "playwright": browser_version, "streamlit": streamlit_version,
                            "browser_channel": os.environ.get("ASK_BROWSER_CHANNEL", "bundled-chromium")},
            "warm_ms": [], "cold_start_to_ready_ms": [], "limits_ms": {
                "overview": 1500, "metadata_navigation": 500, "filter": 500,
                "source_result": 1000, "cold": 4000},
            "workload": {"kind": ("real-pilot" if model_root.resolve() == ROOT.resolve()
                                    else "isolated-consumer-fixture"),
                         "synthetic_model": model_root.resolve() != ROOT.resolve(),
                         "code_candidate_sha": code_candidate_sha,
                         "selected_test_id": test_id, "selected_case_id": case_id,
                         "selected_scenario_id": scenario_id,
                         "model_input_sha256": workload_digest,
                         "document_bytes": workload_sizes,
                         "total_document_bytes": sum(workload_sizes.values()),
                         "task_count": len(graph_document.get("tasks", [])),
                         "model_task_count": sum(node.get("type") == "task"
                                                 for node in model_document.get("nodes", [])),
                         "test_count": len(plan_document.get("tests", [])),
                         "model_node_count": len(model_document.get("nodes", [])),
                         "graph_edge_count": len(model_document.get("edges", []))},
            "structural_workloads": [structural_workload(size) for size in (100, 1000)],
            "run_status": "running"}

    def persist_partial():
        if output_path is None:
            return
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(destination)

    persist_partial()
    with sync_playwright() as pw:
        launch_options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("ASK_BROWSER_CHANNEL"):
            launch_options["channel"] = os.environ["ASK_BROWSER_CHANNEL"]
        elif os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE"):
            launch_options["executable_path"] = os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE"]
        browser = pw.chromium.launch(**launch_options)
        data["environment"]["browser_version"] = browser.version
        persist_partial()
        process, url, _ = start_server(model_root, work_id)
        try:
            await_http(process, url)
            for index in range(warm_samples):
                context = browser.new_context()
                page = context.new_page()
                started = time.perf_counter()
                page.goto(url, wait_until="domcontentloaded")
                ready(page, root_route, root_title, work_id)
                expect(page.get_by_role("heading", name=root_title, exact=True)).to_be_visible()
                for label in ("Stories and scenarios", "Task progress", "Needs attention",
                              "Scenarios", "Tasks", "Blocked tasks", "Open decisions"):
                    expect(page.get_by_text(label, exact=True)).to_be_visible()
                if output_path is not None and index == 0:
                    screenshot_path = Path(output_path).with_suffix(".overview.png")
                    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    screenshot_bytes = screenshot_path.read_bytes()
                    data["pilot_screenshot"] = {
                        "path": str(screenshot_path), "bytes": len(screenshot_bytes),
                        "sha256": hashlib.sha256(screenshot_bytes).hexdigest(),
                    }
                    persist_partial()
                overview = (time.perf_counter() - started) * 1000
                t = time.perf_counter()
                route_click(page, scenario_id, scenario_title)
                expect(page.get_by_text(str(scenario.get("given", "")), exact=True)).to_be_visible()
                expect(page.get_by_text(str(scenario.get("then", [""])[0]), exact=True)).to_be_visible()
                metadata_navigation = (time.perf_counter() - t) * 1000
                route_click(page, root_route, root_title)
                expect(page.get_by_text("Results are not loaded", exact=False)).to_be_visible()
                t = time.perf_counter()
                page.get_by_role("button", name="View scenarios", exact=True).click()
                expect(page.get_by_role("button", name="Clear filter", exact=True)).to_be_visible()
                expected_scenarios = {item["id"] for item in projection.get("scenarios", [])}
                prefix = _key_class("overview:filter:open:scenarios:")
                actual_scenarios = page.locator("[class*='st-key-overview-filter-open-scenarios-']").evaluate_all(
                    "(els, prefix) => [...new Set(els.flatMap(el => [...el.classList]"
                    ".filter(name => name.startsWith(prefix)).map(name => name.slice(prefix.length))))]",
                    prefix)
                if set(actual_scenarios) != expected_scenarios:
                    raise AssertionError(f"scenario filter opened {actual_scenarios}, expected {sorted(expected_scenarios)}")
                expect(page.get_by_role("button", name="Open record", exact=True)).to_have_count(
                    len(expected_scenarios))
                for identity in expected_scenarios:
                    expect(page.locator(
                        f'[class~="{_key_class(f"overview:filter:open:scenarios:{identity}")}"]'
                    ).get_by_role("button", name="Open record", exact=True)).to_be_visible()
                filter_ms = (time.perf_counter() - t) * 1000
                page.get_by_role("button", name="Clear filter", exact=True).click()
                t = time.perf_counter()
                test_title = projected_test.get("title") or test_id
                route_click(page, f"test:{test_id}", str(test_title))
                expect(page.get_by_text(case_id, exact=False).first).to_be_visible()
                expect(page.get_by_text("Selected source path: " + source_path,
                                        exact=False)).to_be_visible()
                route_click(page, f"result:{test_id}", str(test_title))
                expect(page.get_by_text(f"Selected test: {test_id} · revision-bound planned identity",
                                        exact=True)).to_be_visible()
                expect(page.get_by_role("heading", name="Recorded execution", exact=True)).to_be_visible()
                expect(page.get_by_text("Historical evidence", exact=True)).to_be_visible()
                for outcome in sorted(set(expected_outcomes)):
                    expect(page.get_by_text("Recorded outcome: " + outcome, exact=True)).to_have_count(
                        expected_outcomes.count(outcome))
                expect(page.get_by_text("Output integrity: valid", exact=True)).to_have_count(
                    len(expected_outcomes))
                source_result = (time.perf_counter() - t) * 1000
                data["warm_ms"].append({"sample": index, "overview": overview,
                                        "metadata_navigation": metadata_navigation,
                                        "filter": filter_ms, "source_result": source_result})
                persist_partial()
                context.close()
        finally:
            process.terminate()
            process.wait(timeout=5)
        for index in range(cold_samples):
            process, url, started = start_server(model_root, work_id)
            try:
                await_http(process, url)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")
                ready(page, root_route, root_title, work_id)
                data["cold_start_to_ready_ms"].append({"sample": index,
                    "elapsed": (time.perf_counter() - started) * 1000})
                persist_partial()
                page.close()
            finally:
                process.terminate()
                process.wait(timeout=5)
        browser.close()
    data["run_status"] = "complete"
    persist_partial()
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-root", type=Path, default=ROOT)
    parser.add_argument("--work-id", default=None)
    parser.add_argument("--warm-samples", type=int, default=20)
    parser.add_argument("--cold-samples", type=int, default=5)
    parser.add_argument("--test-id", default="E")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    work_id = args.work_id or os.environ.get("ASK_WORK_ID") or "structured-agentic-environment"
    try:
        result = run(args.model_root.resolve(), work_id, args.warm_samples, args.cold_samples,
                     output_path=args.output, test_id=args.test_id)
    except Exception as exc:
        if args.output and args.output.is_file():
            partial = json.loads(args.output.read_text(encoding="utf-8"))
            partial["run_status"] = "failed"
            partial["error"] = {"type": type(exc).__name__, "message": str(exc)}
            temporary = args.output.with_suffix(args.output.suffix + ".tmp")
            temporary.write_text(json.dumps(partial, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
            temporary.replace(args.output)
        raise
    raw = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(raw + "\n", encoding="utf-8")
    print(raw)


if __name__ == "__main__":
    main()
