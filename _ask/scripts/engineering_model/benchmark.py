"""Benchmark the validator or (--guard) actual staged actions on fixed workloads."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from copy import deepcopy
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


def parser_comparison(path: Path, repeats: int, *, guard=False) -> dict:
    raw = path.read_bytes()
    result = {"input_bytes": len(raw), "stdlib_json": None, "orjson": None}
    candidates = [("stdlib_json", json.loads)]
    if guard:
        from .snapshot import decode
        candidates.append(("production_duplicate_key_json", decode))
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
            "This graph-only mode does not measure the pre/post action guard; use --guard separately.",
            "No performance target has been agreed.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_suffix(output.suffix + ".tmp")
    temp_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_output.replace(output)
    return report


def _json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def guard_workload(root, pilot, size=None):
    """Materialize captured pilot bytes, never a copy of mutable runtime state."""
    from .snapshot import capture
    document = deepcopy(pilot.document)
    intent = next(node["id"] for node in document["nodes"] if node["type"] == "intent")
    existing_ids = {node["id"] for node in document["nodes"]}
    if size is not None:
        if size < len(document["nodes"]):
            raise ValueError("synthetic size cannot be smaller than the pilot")
        previous = None
        for index in range(size - len(document["nodes"])):
            identity = f"benchmark-task-{index:05d}"
            if identity in existing_ids:
                raise ValueError("synthetic task identity collides with pilot")
            document["nodes"].append({"id": identity, "type": "task",
                                      "title": identity, "lifecycle": "planned"})
            document["edges"].append({"type": "contains", "source": intent, "target": identity})
            if previous is not None:
                document["edges"].append({"type": "depends_on", "source": identity, "target": previous})
            previous = identity
    for relative, raw in pilot.files.items():
        if pilot.statuses[relative] not in ("present", "missing"):
            raise ValueError(f"benchmark cannot reproduce input status: {relative}")
        if raw is not None:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    if size is not None:
        (root / pilot.model_path).write_bytes(_json_bytes(document))
    captured = capture(root, pilot.work_id)
    errors = captured.diagnostics(root)
    if errors:
        raise ValueError(f"benchmark workload is invalid: {errors}")
    return captured


def _invalid_edge(document, variant):
    if variant.endswith("missing-link"):
        intent = next(node["id"] for node in document["nodes"] if node["type"] == "intent")
        return {"type": "contains", "source": intent, "target": "benchmark-missing-target"}
    tasks = [node["id"] for node in document["nodes"] if node["type"] == "task"]
    synthetic = [identity for identity in tasks if identity.startswith("benchmark-task-")]
    tasks = synthetic or tasks
    if not tasks:
        raise ValueError("guard benchmark pilot requires a task")
    # Close the synthetic dependency chain; the unchanged pilot uses a self-cycle.
    return {"type": "depends_on", "source": tasks[0], "target": tasks[-1]}


def _state_fingerprint(state):
    """Publication bytes, file identities and mtimes; deliberately exclude atime."""
    return {str(path.relative_to(state)): (hashlib.sha256(path.read_bytes()).hexdigest(),
                                         path.stat().st_mtime_ns, path.stat().st_ino)
            for path in sorted(state.rglob("*")) if path.is_file()}


def guard_sample(template, work_id, variant):
    """One fresh-process sample; all writes stay inside a disposable repository."""
    import resource
    from unittest.mock import patch
    from . import actions, canonical, snapshot
    from .admission import admit, load_published, publication_identity

    setup_started = time.perf_counter_ns()
    with tempfile.TemporaryDirectory(prefix="ask-guard-sample-") as temporary:
        root = Path(temporary)
        shutil.copytree(template, root, dirs_exist_ok=True)
        base, errors = admit(root, work_id)
        if errors:
            raise RuntimeError(f"benchmark bootstrap refused: {errors}")
        model = base.document
        intent = next(node["id"] for node in model["nodes"] if node["type"] == "intent")
        markdown = f"specs/current/{work_id}.md"
        if base.files.get(markdown) is None:
            raise ValueError("pilot closure must include its canonical Markdown specification")
        commands = [{"op": "revise_node", "id": intent,
                     "changes": {"title": "Deterministic benchmark guarded edit"}}]
        if variant.startswith("post-"):
            commands.append({"op": "add_edge", "edge": _invalid_edge(model, variant)})
        if variant.startswith("pre-"):
            model["edges"].append(_invalid_edge(model, variant))
            (root / base.model_path).write_bytes(_json_bytes(model))
        before = snapshot.capture(root, work_id)
        state = root / "work" / work_id / "traceability/model-state"
        publication_before = _state_fingerprint(state)
        event_before = publication_identity(root, work_id)
        setup_ms = (time.perf_counter_ns() - setup_started) / 1_000_000
        rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        phases = {name: 0.0 for name in ("pre", "action", "post", "publication")}
        components = {name: 0.0 for name in ("input_io", "parse", "graph", "canonical")}
        calls = {name: 0 for name in components}
        in_post = False
        invoked = False

        def timed(function, values, key):
            def wrapped(*args, **kwargs):
                started = time.perf_counter_ns()
                try:
                    return function(*args, **kwargs)
                finally:
                    values[key] += (time.perf_counter_ns() - started) / 1_000_000
                    if values is components:
                        calls[key] += 1
            return wrapped

        original_capture, original_diagnostics = actions.capture, snapshot.Snapshot.diagnostics
        original_recover = actions.recover_locked

        def staged_capture(*args, **kwargs):
            nonlocal in_post
            in_post = True
            return timed(original_capture, phases, "post")(*args, **kwargs)

        def diagnostics(self, *args, **kwargs):
            if in_post:
                return timed(original_diagnostics, phases, "post")(self, *args, **kwargs)
            return original_diagnostics(self, *args, **kwargs)

        def recovery(*args, **kwargs):
            if kwargs.get("validated") is not None:
                return timed(original_recover, phases, "publication")(*args, **kwargs)
            return original_recover(*args, **kwargs)

        def proposal():
            nonlocal invoked
            invoked = True
            return {"commands": commands,
                    "files": {markdown: base.files[markdown].decode() + "\nBenchmark staged edit.\n"}}

        original_batch = actions.apply_batch

        def batch(*args, **kwargs):
            # Fix semantic attribution time so result bytes/hashes are reproducible.
            return timed(original_batch, phases, "action")(
                *args, **kwargs, timestamp="2000-01-01T00:00:00Z")

        # Transparent timing wrappers execute the real functions and preserve results.
        # Components overlap phases; only the phase timings form a partition.
        with ExitStack() as stack:
            for module, name, replacement in (
                (actions, "validate_current", timed(actions.validate_current, phases, "pre")),
                (actions, "capture", staged_capture),
                (snapshot.Snapshot, "diagnostics", diagnostics),
                (actions, "recover_locked", recovery),
                (actions, "apply_batch", batch),
                (snapshot, "read_input", timed(snapshot.read_input, components, "input_io")),
                (actions, "read_input", timed(actions.read_input, components, "input_io")),
                (snapshot, "decode", timed(snapshot.decode, components, "parse")),
                (canonical, "decode", timed(canonical.decode, components, "parse")),
                (snapshot, "validate", timed(snapshot.validate, components, "graph")),
                (canonical, "diagnostics", timed(canonical.diagnostics, components, "canonical")),
            ):
                stack.enter_context(patch.object(module, name, replacement))
            started = time.perf_counter_ns()
            receipt = actions.edit(root, work_id, base.identity["digest"], proposal)
            total_ms = (time.perf_counter_ns() - started) / 1_000_000
        rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        phases["orchestration_cas_journal"] = max(0.0, total_ms - sum(phases.values()))
        current = snapshot.capture(root, work_id)
        published = load_published(root, work_id)
        failed = variant != "valid"
        expected_steps = ["pre"] if variant.startswith("pre-") else ["pre", "action", "post"]
        if not failed:
            expected_steps.append("publication")
        checks = {
            "expected_outcome": receipt["valid"] == (not failed),
            "expected_steps": receipt["steps"] == expected_steps,
            "action_invocation": invoked == (not variant.startswith("pre-")),
            "publication": (_state_fingerprint(state) == publication_before and
                            publication_identity(root, work_id) == event_before) if failed else (
                                published.identity == current.identity == receipt["snapshot"] and
                                publication_identity(root, work_id) != event_before),
            "working_projection": current.identity == before.identity if failed else (
                current.files[markdown] != base.files[markdown] and
                current.files[base.model_path] != base.files[base.model_path]),
        }
        expected_code = "EM001_DEPENDENCY_CYCLE" if variant.endswith("cycle") else "EM001_DANGLING_EDGE"
        if failed:
            checks["expected_diagnostic"] = expected_code in {d["code"] for d in receipt["diagnostics"]}
        if not all(checks.values()):
            raise RuntimeError(f"guard benchmark behavior mismatch: {checks}, {receipt}")
        return {"setup_ms": setup_ms, "guard_ms": total_ms, "phases_ms": phases,
                "components_ms": components, "component_calls": calls,
                "rss_before_guard_kib": rss_before, "rss_after_guard_kib": rss_after,
                "rss_guard_highwater_increase_kib": max(0, rss_after - rss_before),
                "checks": checks, "steps": receipt["steps"],
                "diagnostic_codes": sorted({d["code"] for d in receipt["diagnostics"]}),
                "input_digest": before.identity["digest"], "result_digest": current.identity["digest"],
                "candidate_digest": receipt["snapshot"]["digest"] if receipt["snapshot"] else None,
                "workload_sha256": hashlib.sha256(_json_bytes({
                    "variant": variant, "input": before.identity,
                    "proposal": {"commands": commands, "files": {
                        markdown: base.files[markdown].decode() + "\nBenchmark staged edit.\n"}},
                    "semantic_timestamp": "2000-01-01T00:00:00Z",
                })).hexdigest()}


def _distribution(values, unit):
    return {f"p50_{unit}": round(statistics.median(values), 3),
            f"p95_{unit}": round(percentile(values, .95), 3),
            f"max_{unit}": round(max(values), 3)}


def measure_guard(template, work_id, variant, repeats):
    if not TIME_BIN.is_file():
        raise RuntimeError("/usr/bin/time is required to measure per-process peak RSS")
    samples = []
    worker = ("import json,sys; from pathlib import Path; "
              "from engineering_model.benchmark import guard_sample; "
              "print(json.dumps(guard_sample(Path(sys.argv[1]),sys.argv[2],sys.argv[3])))")
    for _ in range(repeats):
        with tempfile.TemporaryDirectory(prefix="ask-guard-rss-") as temporary:
            rss_path = Path(temporary) / "rss"
            started = time.perf_counter_ns()
            process = subprocess.run(
                [str(TIME_BIN), "-f", "%M", "-o", str(rss_path), sys.executable,
                 "-c", worker, str(template), work_id, variant], cwd=template,
                env={**os.environ, "PYTHONPATH": str(REPOSITORY / "_ask/scripts"),
                     "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True)
            wall_ms = (time.perf_counter_ns() - started) / 1_000_000
            if process.returncode:
                raise RuntimeError(f"guard worker failed: {process.stderr} {process.stdout}")
            sample = json.loads(process.stdout)
            sample.update(process_wall_ms=wall_ms,
                          peak_rss_kib=int(rss_path.read_text().strip()))
            samples.append(sample)
    if len({tuple(s[key] for key in ("input_digest", "result_digest", "candidate_digest", "workload_sha256"))
            for s in samples}) != 1:
        raise RuntimeError("workload or result bytes differed between repeats")
    repeated = samples[1:]
    return {"variant": variant, "sample_count": repeats,
            "cold_first_process": samples[0],
            "repeats_fresh_process": {
                **{key: _distribution([s[key] for s in repeated], "kib" if key.endswith("kib") else "ms")
                   for key in ("process_wall_ms", "setup_ms", "guard_ms", "peak_rss_kib",
                               "rss_before_guard_kib", "rss_after_guard_kib", "rss_guard_highwater_increase_kib")},
                **{group: {name: _distribution([s[group][name] for s in repeated], "ms")
                           for name in samples[0][group]} for group in ("phases_ms", "components_ms")},
            }}


def _guard_sources():
    paths = [REPOSITORY / "_ask/scripts/engineering_model" / (name + ".py") for name in (
        "__init__", "benchmark", "validation", "snapshot", "canonical", "actions", "admission", "domain")]
    paths += sorted((REPOSITORY / ".agents/ask/verification/traceability").glob("*.py"))
    return {str(path.relative_to(REPOSITORY)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def run_guard(work_id, repeats):
    from .snapshot import capture
    hashes = _guard_sources()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPOSITORY,
                            capture_output=True, text=True, check=True).stdout.strip()
    pilot = capture(REPOSITORY, work_id)
    results = []
    with tempfile.TemporaryDirectory(prefix="ask-guard-benchmark-") as temporary:
        for size in (None, 100, 1_000, 10_000):
            root = Path(temporary) / (str(size) if size else "pilot")
            captured = guard_workload(root, pilot, size)
            parsers = {path: parser_comparison(root / path, repeats, guard=True)
                       for path, raw in captured.files.items() if raw is not None and path.endswith(".json")}
            results.append({
                "kind": "actual-pilot" if size is None else "synthetic-pilot-closure",
                "work_id": work_id, "node_count": len(captured.document["nodes"]),
                "edge_count": len(captured.document["edges"]),
                "closure_file_count": len(captured.files),
                "present_file_count": sum(raw is not None for raw in captured.files.values()),
                "closure_bytes": sum(len(raw) for raw in captured.files.values() if raw is not None),
                "workload_sha256": captured.identity["digest"], "input_manifest": captured.identity,
                "parser_comparison": parsers,
                "actions": [measure_guard(root, work_id, variant, repeats) for variant in (
                    "valid", "pre-missing-link", "pre-cycle", "post-missing-link", "post-cycle")],
            })
    if _guard_sources() != hashes:
        raise RuntimeError("benchmark implementation inputs changed during measurement; rerun on stable sources")
    return {"schema": "ask-engineering-guard-benchmark/v1", "candidate": "actual Python actions.edit",
            "source": {"commit": commit, "files_sha256": hashes,
                "content_may_include_uncommitted_changes": True,
                "tree_sha256": hashlib.sha256(_json_bytes(hashes)).hexdigest()},
            "environment": {"python": sys.version, "platform": platform.platform(),
                            "machine": platform.machine(), "logical_cpus": os.cpu_count(),
                            "cpu_model": next((line.split(":", 1)[1].strip() for line in
                                Path("/proc/cpuinfo").read_text(errors="replace").splitlines()
                                if line.startswith("model name")), "unavailable"),
                            "repeats": repeats, "time_binary": str(TIME_BIN),
                            "time_version": subprocess.run([str(TIME_BIN), "--version"],
                                capture_output=True, text=True, check=True).stdout.splitlines()[0],
                            "native_toolchains": {name: shutil.which(name)
                                for name in ("rustc", "cargo", "go", "cc", "clang")}},
            "measurements": results,
            "limits": [
                "Cold means first measured process per workload/variant, not cold OS caches; no cache flushing.",
                "Every repeat uses a fresh process and disposable repository; setup/bootstrap is outside guard_ms.",
                "process_wall_ms includes imports, fixture copy, bootstrap, verification and cleanup.",
                "Phase timings partition guard_ms; action measures semantic apply_batch; remainder includes proposal loading, serialization, CAS and journal work.",
                "Components are inclusive/overlapping: captured-input I/O, duplicate-key-aware parsing, graph/reference validation and canonical validation; they are not additive.",
                "Peak RSS includes imports/setup/action; before/after are process high-water marks, not live or attributable allocations (Linux KiB).",
                "Parser comparison uses resident bytes, stdlib json, production duplicate-key parsing and optional orjson; it does not prove equivalent duplicate-key/schema semantics or select a native backend.",
                "Timing wrappers add instrumentation overhead. No performance target or OS-cache-cold claim.",
                "Stdout only; no repository reports, refs or runtime state are written.",
            ]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-id", default="structured-agentic-environment")
    parser.add_argument("--repeats", type=int, default=15)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--guard", action="store_true", help="measure real staged actions in temporary roots; JSON stdout only")
    args = parser.parse_args(argv)
    if args.repeats < 3:
        parser.error("--repeats must be at least 3")
    if args.guard:
        if args.output is not None:
            parser.error("--guard emits JSON stdout and does not accept --output")
        print(json.dumps(run_guard(args.work_id, args.repeats), sort_keys=True))
        return 0
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
