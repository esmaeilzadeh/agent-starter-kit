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

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


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
    marker = page.locator("[data-workbench-ready][data-workbench-route][data-workbench-serial]")
    try:
        marker.wait_for(timeout=10000)
    except Exception as exc:
        if page.get_by_text("Engineering workbench", exact=True).count():
            raise AssertionError("rendered workbench is missing its content-specific ready marker") from exc
        raise
    return page.locator("[data-workbench-ready]").get_attribute("data-workbench-serial")


def wait_changed(page, previous):
    page.wait_for_function(
        "previous => { const el = document.querySelector('[data-workbench-ready]'); "
        "return el && el.getAttribute('data-workbench-serial') !== previous; }",
        arg=previous, timeout=10000)


def route_click(page, name):
    button = page.get_by_role("button", name=name, exact=False).first
    if not button.count():
        raise AssertionError(f"required workbench route {name!r} is missing")
    serial = ready(page)
    button.click()
    wait_changed(page, serial)


def run(model_root: Path, work_id: str, warm_samples=20, cold_samples=5):
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
    try:
        browser_version = version("playwright")
        streamlit_version = version("streamlit")
    except PackageNotFoundError:
        browser_version = streamlit_version = "unknown"
    data = {"code_candidate_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
             capture_output=True, text=True, check=False).stdout.strip() or "unknown",
            "code_source_sha256": sources, "model_root": str(model_root), "model_work_id": work_id,
            "model_git_sha": model_head, "model_input_sha256": model_digest,
            "code_file_bytes": sizes, "model_file_bytes": model_sizes,
            "environment": {"python": sys.version, "platform": platform.platform(),
                            "playwright": browser_version, "streamlit": streamlit_version},
            "warm_ms": [], "cold_start_to_ready_ms": [], "limits_ms": {
                "navigation": 1500, "filter": 500, "source_result": 1000, "cold": 4000}}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        process, url, _ = start_server(model_root)
        try:
            await_http(process, url)
            for index in range(warm_samples):
                context = browser.new_context()
                page = context.new_page()
                started = time.perf_counter()
                page.goto(url, wait_until="domcontentloaded")
                ready(page)
                navigation = (time.perf_counter() - started) * 1000
                t = time.perf_counter()
                route_click(page, "Uppercase behavior")
                navigation = (time.perf_counter() - t) * 1000
                route_click(page, "Build")
                status_filter = page.get_by_label("Status filter")
                if not status_filter.count():
                    raise AssertionError("selected task is missing its status filter")
                before = ready(page)
                t = time.perf_counter()
                status_filter.click()
                page.get_by_role("option", name="All", exact=True).click()
                wait_changed(page, before)
                filter_ms = (time.perf_counter() - t) * 1000
                t = time.perf_counter()
                route_click(page, "Uppercase assertion")
                route_click(page, "Result / evidence")
                source_result = (time.perf_counter() - t) * 1000
                data["warm_ms"].append({"sample": index, "navigation": navigation,
                                        "filter": filter_ms, "source_result": source_result})
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
                page.close()
            finally:
                process.terminate()
                process.wait(timeout=5)
        browser.close()
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
    result = run(args.model_root.resolve(), work_id, args.warm_samples, args.cold_samples)
    raw = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(raw + "\n", encoding="utf-8")
    print(raw)


if __name__ == "__main__":
    main()
