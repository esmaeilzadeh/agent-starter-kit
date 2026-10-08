"""Benchmark the current validator candidate on the pilot and fixed graph sizes."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

from .validation import validate


REPOSITORY = Path(__file__).resolve().parents[3]
TIME_BIN = Path("/usr/bin/time")


def graph_document(work_id: str, node_count: int, variant: str = "valid") -> dict:
    nodes = [{"id": "intent", "type": "intent", "title": "Benchmark intent", "lifecycle": "active"}]
    task_count = node_count - 1
    nodes.extend({
        "id": f"task-{index:05d}",
        "type": "task",
        "title": f"Benchmark task {index}",
        "lifecycle": "planned",
    } for index in range(task_count))
    edges = [{"type": "contains", "source": "intent", "target": f"task-{index:05d}"}
             for index in range(task_count)]
    edges.extend({"type": "depends_on", "source": f"task-{index:05d}",
                  "target": f"task-{index - 1:05d}"}
                 for index in range(1, task_count))
    if variant == "missing-link":
        edges.append({"type": "depends_on", "source": "task-00000", "target": "missing-task"})
    elif variant == "cycle":
        edges.append({"type": "depends_on", "source": "task-00000",
                      "target": f"task-{task_count - 1:05d}"})
    return {"schema": "ask-engineering-model/v1", "work_id": work_id,
            "revision": 1, "nodes": nodes, "edges": edges}


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def measure_command(root: Path, work_id: str, repeats: int) -> dict:
    if not TIME_BIN.is_file():
        raise RuntimeError("/usr/bin/time is required to measure per-process peak RSS")
    timings: list[float] = []
    rss_kib: list[int] = []
    first_result = None
    for index in range(repeats):
        with tempfile.NamedTemporaryFile(prefix="ask-model-rss-", delete=False) as rss_file:
            rss_path = Path(rss_file.name)
        started = time.perf_counter_ns()
        result = subprocess.run(
            [str(TIME_BIN), "-f", "%M", "-o", str(rss_path), sys.executable,
             "-m", "engineering_model", "validate", "--work-id", work_id],
            cwd=root,
            env={**os.environ, "PYTHONPATH": str(REPOSITORY / "_ask/scripts")},
            capture_output=True, text=True, check=False,
        )
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
        try:
            rss_kib.append(int(rss_path.read_text(encoding="ascii").splitlines()[-1]))
        finally:
            rss_path.unlink(missing_ok=True)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"validator emitted invalid JSON: {result.stderr}") from exc
        if index == 0:
            first_result = report
        expected_exit = 0 if work_id.endswith("-valid") or work_id == "structured-agentic-environment" else 1
        if result.returncode != expected_exit:
            raise RuntimeError(f"unexpected validator exit {result.returncode}: {result.stdout} {result.stderr}")
        if bool(report.get("valid")) != (expected_exit == 0):
            raise RuntimeError(f"validator outcome differs from workload variant: {report}")
        timings.append(elapsed_ms)
    assert first_result is not None
    return {
        "first_run_ms": round(timings[0], 3),
        "repeat_p50_ms": round(statistics.median(timings[1:] or timings), 3),
        "repeat_p95_ms": round(percentile(timings[1:] or timings, 0.95), 3),
        "peak_rss_kib": max(rss_kib),
        "diagnostic_count": len(first_result["diagnostics"]),
    }


def parser_comparison(path: Path, repeats: int) -> dict:
    raw = path.read_bytes()
    result = {"input_bytes": len(raw), "stdlib_json": None, "orjson": None}
    candidates = [("stdlib_json", json.loads)]
    try:
        import orjson
    except ImportError:
        result["orjson_unavailable"] = True
    else:
        candidates.append(("orjson", orjson.loads))
        result["orjson_version"] = importlib.metadata.version("orjson")
    for name, parse in candidates:
        values = []
        for _ in range(repeats):
            started = time.perf_counter_ns()
            parse(raw)
            values.append((time.perf_counter_ns() - started) / 1_000_000)
        result[name] = {
            "warm_p50_ms": round(statistics.median(values), 3),
            "warm_p95_ms": round(percentile(values, 0.95), 3),
        }
    return result


def component_timings(path: Path, root: Path, work_id: str, repeats: int) -> dict:
    read_ms: list[float] = []
    parse_ms: list[float] = []
    graph_ms: list[float] = []
    diagnostic_count = None
    for _ in range(repeats):
        started = time.perf_counter_ns()
        raw = path.read_bytes()
        read_ms.append((time.perf_counter_ns() - started) / 1_000_000)
        started = time.perf_counter_ns()
        document = json.loads(raw)
        parse_ms.append((time.perf_counter_ns() - started) / 1_000_000)
        started = time.perf_counter_ns()
        diagnostics = validate(document, root, work_id)
        graph_ms.append((time.perf_counter_ns() - started) / 1_000_000)
        if diagnostic_count is None:
            diagnostic_count = len(diagnostics)
    def summary(values: list[float]) -> dict:
        return {"p50_ms": round(statistics.median(values), 3),
                "p95_ms": round(percentile(values, 0.95), 3)}
    return {
        "file_read": summary(read_ms),
        "stdlib_parse": summary(parse_ms),
        "model_validation": summary(graph_ms),
        "diagnostic_count": diagnostic_count,
    }


def file_closure_count(root: Path, work_id: str) -> int:
    model_path = root / "work" / work_id / "engineering-model.json"
    document = json.loads(model_path.read_bytes())
    paths = {model_path}
    for node in document["nodes"]:
        reference = node.get("reference")
        if isinstance(reference, dict) and isinstance(reference.get("path"), str):
            candidate = (root / reference["path"]).resolve()
            if candidate.is_file():
                paths.add(candidate)
    return len(paths)


def run(work_id: str, repeats: int, output: Path) -> dict:
    actual = measure_command(REPOSITORY, work_id, repeats)
    pilot = REPOSITORY / "work" / work_id / "engineering-model.json"
    results = [{
        "kind": "actual-pilot",
        "work_id": work_id,
        "node_count": len(json.loads(pilot.read_bytes())["nodes"]),
        "edge_count": len(json.loads(pilot.read_bytes())["edges"]),
        "document_file_count": file_closure_count(REPOSITORY, work_id),
        **actual,
        "components": component_timings(pilot, REPOSITORY, work_id, repeats),
        "parser_comparison": parser_comparison(pilot, repeats),
    }]
    with tempfile.TemporaryDirectory(prefix="ask-model-benchmark-") as temp:
        root = Path(temp)
        for size in (100, 1_000, 10_000):
            for variant in ("valid", "missing-link", "cycle"):
                case_id = f"benchmark-{size}-{variant}"
                model_path = root / "work" / case_id / "engineering-model.json"
                model_path.parent.mkdir(parents=True, exist_ok=True)
                model_path.write_text(json.dumps(graph_document(case_id, size, variant),
                                                 separators=(",", ":")), encoding="utf-8")
                measured = measure_command(root, case_id, repeats)
                results.append({
                    "kind": variant,
                    "work_id": case_id,
                    "node_count": size,
                    "edge_count": len(graph_document(case_id, size, variant)["edges"]),
                    "document_file_count": 1,
                    **measured,
                    "components": component_timings(model_path, root, case_id, repeats),
                    "parser_comparison": parser_comparison(model_path, repeats),
                })

    report = {
        "schema": "ask-engineering-benchmark/v1",
        "candidate": "Python validator with stdlib graph traversal",
        "implementation_status": "initial candidate; language/tool selection remains open",
        "source": {
            "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPOSITORY,
                                      capture_output=True, text=True, check=True).stdout.strip(),
            "validator_sha256": hashlib.sha256((REPOSITORY / "_ask/scripts/engineering_model/validation.py").read_bytes()).hexdigest(),
            "benchmark_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "cpu_model": next((line.split(":", 1)[1].strip()
                                for line in Path("/proc/cpuinfo").read_text(errors="replace").splitlines()
                                if line.startswith("model name")), "unavailable"),
            "logical_cpus": os.cpu_count(),
            "repeats": repeats,
            "native_toolchains": {
                name: shutil.which(name) for name in ("rustc", "cargo", "go", "cc", "clang")
            },
        },
        "measurements": results,
        "limits": [
            "First-run timing includes process startup and may benefit from the OS file cache.",
            "Repeat timings start a fresh process each time; validator-level cache is not implemented.",
            "Only the present Python candidate and available JSON parsers are measured here.",
            "The complete pre/post action guard is not implemented and is not measured.",
            "No performance target has been agreed.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_suffix(output.suffix + ".tmp")
    temp_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_output.replace(output)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-id", default="structured-agentic-environment")
    parser.add_argument("--repeats", type=int, default=15)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.repeats < 3:
        parser.error("--repeats must be at least 3")
    if args.output is None:
        output = REPOSITORY / "work" / args.work_id / "benchmarks" / "initial-python-candidate.json"
    else:
        output = args.output if args.output.is_absolute() else REPOSITORY / args.output
    if not output.resolve().is_relative_to(REPOSITORY):
        parser.error("--output must stay inside the repository")
    report = run(args.work_id, args.repeats, output)
    print(json.dumps({"output": str(output.relative_to(REPOSITORY)),
                      "measurements": len(report["measurements"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
