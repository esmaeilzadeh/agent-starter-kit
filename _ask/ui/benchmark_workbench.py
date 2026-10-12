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
import time
from importlib.metadata import version, PackageNotFoundError
from urllib.error import URLError
from urllib.request import urlopen
import yaml

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))

from engineering_model.projection import project
from engineering_model.snapshot import Snapshot
from workbench_navigation import build_outline


def _key_class(key: str) -> str:
    import re
    return "st-key-" + re.sub(r"[^A-Za-z0-9_-]", "-", key)


def structural_workload(task_count: int) -> dict:
    """Exercise projection and outline construction against a deterministic graph size."""
    work_id = f"scale-{task_count}"
    spec = {"schema": "ask-spec/v1", "work_id": work_id, "revision": 1,
            "criteria": [{"id": "C1", "given": "Input", "when": "Rendered", "then": ["Output"],
                          "verification_mode": "tests"}]}
    plan = {"schema": "ask-test-plan/v1", "work_id": work_id,
            "task_scopes": [], "tests": []}
    model = {"schema": "ask-engineering-model/v1", "work_id": work_id, "revision": 1,
             "nodes": [{"id": "purpose", "type": "intent", "title": "Scale fixture", "lifecycle": "active"},
                       {"id": "scenario", "type": "scenario", "title": "Shared behavior", "lifecycle": "active",
                        "reference": {"path": f"specs/current/{work_id}.json", "id": "C1"}}],
             "edges": [{"type": "contains", "source": "purpose", "target": "scenario"}]}
    graph_lines = ["schema: ask-inner-loop-tasks/v1", f"work_id: {work_id}", "tasks:"]
    for index in range(task_count):
        task_id, test_id = f"task-{index:04d}", f"TEST-{index:04d}"
        graph_lines.extend((f"  - id: {task_id}", f"    title: Task {index:04d}",
                            "    outcome: Inspect scoped behavior", "    depends_on: []",
                            f"    owned_paths: [src/module-{index:04d}.py]"))
        plan["task_scopes"].append({"task_id": task_id, "test_ids": [test_id]})
        plan["tests"].append({"id": test_id, "criterion_ids": ["C1"], "type": "unit",
                              "case_id": f"test_scale.Cases.test_{index:04d}",
                              "source_paths": ["test_scale.py"]})
    docs = {
        f"work/{work_id}/engineering-model.json": json.dumps(model, sort_keys=True).encode(),
        f"work/{work_id}/test-plan.json": json.dumps(plan, sort_keys=True).encode(),
        f"work/{work_id}/inner-loop/tasks.yaml": ("\n".join(graph_lines) + "\n").encode(),
        f"specs/current/{work_id}.json": json.dumps(spec, sort_keys=True).encode(),
        f"specs/current/{work_id}.md": b"# Structural workload\n",
    }
    snapshot = Snapshot(work_id, docs, {path: "present" for path in docs})
    projection_samples, outline_samples = [], []
    for _ in range(5):
        started = time.perf_counter()
        projected = project(snapshot, Path("."), include_evidence=False)
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
            "source_file_count": len({path for item in plan["tests"] for path in item["source_paths"]}),
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


def start_server(model_root: Path):
    port = free_port()
    env = dict(os.environ, ASK_MODEL_ROOT=str(model_root), ASK_PYTHON=sys.executable,
               PYTHONPATH=str(ROOT / "_ask/scripts"))
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


def ready(page):
    page.get_by_role("heading", name="Engineering workbench", exact=True).wait_for(timeout=10000)
    selected = page.locator(f'[class~="{_key_class("route:purpose")}"]').get_by_role("button")
    selected.wait_for(timeout=10000)
    expect(selected).to_have_attribute("kind", "primary", timeout=10000)
    return selected


def route_click(page, route_id, detail_heading):
    button = page.locator(f'[class~="{_key_class("route:" + route_id)}"]').get_by_role("button")
    if not button.count():
        raise AssertionError(f"required workbench route {route_id!r} is missing")
    button.click()
    expect(button).to_have_attribute("kind", "primary", timeout=10000)
    expect(page.get_by_role("heading", name=detail_heading, exact=True)).to_be_visible(timeout=10000)


def run(model_root: Path, work_id: str, warm_samples=20, cold_samples=5,
        output_path: Path | None = None):
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
            "workload": {"kind": "isolated-consumer-fixture", "synthetic_model": True,
                         "code_candidate_sha": code_candidate_sha,
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
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_path.with_suffix(output_path.suffix + ".tmp")
        temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(output_path)

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
        process, url, _ = start_server(model_root)
        try:
            await_http(process, url)
            for index in range(warm_samples):
                context = browser.new_context()
                page = context.new_page()
                started = time.perf_counter()
                page.goto(url, wait_until="domcontentloaded")
                ready(page)
                expect(page.get_by_role("heading", name="Purpose", exact=True)).to_be_visible()
                for label in ("Stories and scenarios", "Task progress", "Needs attention",
                              "Scenarios", "Tasks", "Blocked tasks", "Open decisions"):
                    expect(page.get_by_text(label, exact=True)).to_be_visible()
                overview = (time.perf_counter() - started) * 1000
                t = time.perf_counter()
                route_click(page, "scenario", "Uppercase behavior")
                expect(page.get_by_text("lowercase text", exact=True)).to_be_visible()
                expect(page.get_by_text("uppercase text is returned", exact=True)).to_be_visible()
                route_click(page, "purpose", "Purpose")
                expect(page.get_by_text("Results are not loaded", exact=False)).to_be_visible()
                metadata_navigation = (time.perf_counter() - t) * 1000
                t = time.perf_counter()
                route_click(page, "build", "Build")
                expect(page.get_by_text("Task status", exact=True)).to_be_visible()
                status_filter = page.get_by_label("Status filter")
                if not status_filter.count():
                    raise AssertionError("selected task is missing its status filter")
                t = time.perf_counter()
                status_filter.click()
                options = [value.strip() for value in page.get_by_role("option").all_text_contents()]
                alternative = next((value for value in options if value and value.casefold() != "all"), None)
                if alternative is None:
                    raise AssertionError("selected task exposes no concrete status to filter")
                page.get_by_role("option", name=alternative, exact=True).click()
                status_filter.click()
                selected_option = page.get_by_role("option", name=alternative, exact=True)
                expect(selected_option).to_have_attribute("aria-selected", "true")
                page.keyboard.press("Escape")
                filter_ms = (time.perf_counter() - t) * 1000
                t = time.perf_counter()
                route_click(page, "test:U", "Uppercase assertion")
                expect(page.get_by_text("test_app.Cases.test_unit", exact=False)).to_be_visible()
                expect(page.get_by_text("Selected source path: test_app.py", exact=True)).to_be_visible()
                route_click(page, "result:U", "Uppercase assertion")
                expect(page.get_by_text("Selected test: U · revision-bound planned identity",
                                        exact=True)).to_be_visible()
                expect(page.get_by_role("heading", name="Recorded execution", exact=True)).to_be_visible()
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
            process, url, started = start_server(model_root)
            try:
                await_http(process, url)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")
                ready(page)
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
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    work_id = args.work_id or os.environ.get("ASK_WORK_ID") or "structured-agentic-environment"
    try:
        result = run(args.model_root.resolve(), work_id, args.warm_samples, args.cold_samples,
                     output_path=args.output)
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
