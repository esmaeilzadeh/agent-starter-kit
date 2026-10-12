"""Integrity-bound detail cache and reproducible latency budget checks."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
import unittest
from collections import OrderedDict
from types import MappingProxyType
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
sys.path.insert(0, str(ROOT / "_ask/ui"))
sys.path.insert(0, str(Path(__file__).parent))
from engineering_fixture import evidence_workbench
from engineering_model.admission import admit
from engineering_model.projection import project
from engineering_model.snapshot import Snapshot
from engineering_model.workbench import build_workbench
import workbench_loading
import benchmark_workbench
from workbench_navigation import build_outline


def _nearest_rank(values, percentile=.95):
    ordered = sorted(values)
    return ordered[max(0, int((len(ordered) * percentile + .999999) // 1) - 1)]


def _structural_workload(task_count: int) -> dict:
    """Measure projection and connected-outline construction at fixed graph sizes."""
    import hashlib
    import yaml

    work_id = f"scale-{task_count}"
    spec = {"schema": "ask-spec/v1", "work_id": work_id, "revision": 1,
            "criteria": [{"id": "C1", "given": "Input", "when": "Rendered", "then": ["Output"],
                          "verification_mode": "tests"}]}
    plan = {"schema": "ask-test-plan/v1", "work_id": work_id,
            "spec_digest": hashlib.sha256(json.dumps(spec, sort_keys=True,
                separators=(",", ":")).encode()).hexdigest(),
            "obligations": [{"criterion_id": "C1", "required_types": ["unit"]}],
            "runners": [{"id": "scale", "adapter": "unittest", "argv": ["python", "-m", "unittest"]}],
            "task_scopes": [], "tests": []}
    graph = {"schema": "ask-inner-loop-tasks/v1", "work_id": work_id, "tasks": []}
    model = {"schema": "ask-engineering-model/v1", "work_id": work_id, "revision": 1,
             "nodes": [{"id": "purpose", "type": "intent", "title": "Scale fixture", "lifecycle": "active"},
                       {"id": "scenario", "type": "scenario", "title": "Shared behavior", "lifecycle": "active",
                        "reference": {"path": f"specs/current/{work_id}.json", "id": "C1"}}],
             "edges": [{"type": "contains", "source": "purpose", "target": "scenario"}]}
    for index in range(task_count):
        task_id, test_id = f"task-{index:04d}", f"TEST-{index:04d}"
        graph["tasks"].append({"id": task_id, "title": f"Task {index:04d}", "outcome": "Inspect scoped behavior",
                               "depends_on": [], "owned_paths": [f"src/module-{index:04d}.py"]})
        plan["task_scopes"].append({"task_id": task_id, "test_ids": [test_id]})
        plan["tests"].append({"id": test_id, "criterion_ids": ["C1"], "type": "unit",
                              "change_kind": "new", "runner_id": "scale",
                              "case_id": f"test_scale.Cases.test_{index:04d}",
                              "source_paths": ["test_scale.py"]})
    docs = {
        f"work/{work_id}/engineering-model.json": json.dumps(model, sort_keys=True).encode(),
        f"work/{work_id}/test-plan.json": json.dumps(plan, sort_keys=True).encode(),
        f"work/{work_id}/inner-loop/tasks.yaml": yaml.safe_dump(graph, sort_keys=True).encode(),
        f"specs/current/{work_id}.json": json.dumps(spec, sort_keys=True).encode(),
        f"specs/current/{work_id}.md": b"# Structural workload\n",
    }
    files = {**docs}
    statuses = {path: "present" for path in docs}
    snapshot = Snapshot(work_id, MappingProxyType(files), MappingProxyType(statuses))
    projection_samples, outline_samples = [], []
    for _ in range(5):
        started = time.perf_counter()
        projection = project(snapshot, Path("."), include_evidence=False)
        projection_samples.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        outline = build_outline(projection)
        outline_samples.append((time.perf_counter() - started) * 1000)
        assert len(projection["workbench"]["tasks"]) == task_count
        assert len(projection["workbench"]["tests"]) == task_count
        assert sum(entry["kind"] == "task" for entry in outline["entries"]) == task_count
        assert sum(entry["kind"] == "test" for entry in outline["entries"]) == task_count
    graph_edges = len(model["edges"]) + sum(len(task["depends_on"]) for task in graph["tasks"])
    return {"task_count": task_count, "test_count": len(plan["tests"]),
            "model_node_count": len(model["nodes"]), "graph_edge_count": graph_edges,
            "source_file_count": len({path for test in plan["tests"] for path in test["source_paths"]}),
            "document_bytes": {path: len(raw) for path, raw in docs.items()},
            "total_document_bytes": sum(map(len, docs.values())),
            "projection_ms": projection_samples, "outline_ms": outline_samples}


class WorkbenchTests(unittest.TestCase):
    def test_lazy_work_and_integrity_bound_cache_invalidation(self):
        consumer, _ = evidence_workbench()
        self.addCleanup(consumer.close)
        root = consumer.root
        snapshot, diagnostics = admit(root, "w")
        self.assertEqual(diagnostics, [], diagnostics)
        projection = project(snapshot, root, include_evidence=False)
        tests = {item["id"]: item for item in projection.get("workbench", {}).get("tests", [])}
        self.assertIn("U", tests, "selected test metadata comes from the admitted projection")
        test = tests["U"]
        for field in ("case_id", "runner_id", "source_paths", "type", "scenario_ids"):
            self.assertIn(field, test, f"projection retains canonical test field {field}")
        self.assertEqual(test["id"], "U")
        cache = OrderedDict()
        context = {"kind": "working-tree"}
        self.assertEqual(len(cache), 0, "overview projection leaves selected detail cache empty")
        original_identity = workbench_loading.detail_identity(
            root, snapshot, test, source_context=context)
        first = workbench_loading.load_selected_detail(
            root, snapshot, test, node_id="case", source_context=context, cache=cache)
        same = workbench_loading.load_selected_detail(
            root, snapshot, test, node_id="case", source_context=context, cache=cache)
        self.assertIs(first, same, "revisiting unchanged selected detail uses its integrity-bound cache")
        self.assertEqual(len(cache), 1)
        self.assertEqual(first["identity"], original_identity)

        # Exercise the real retained run log and review record instead of a synthetic probe file.
        log_path = next((root / "work/w/traceability/runs").glob("*/*.log"), None)
        review_path = root / "work/w/traceability/reviews" / f"{consumer.sha}.json"
        self.assertIsNotNone(log_path, "fixture retains a real execution log")
        self.assertTrue(review_path.is_file(), "fixture retains a candidate-bound review")
        log_before = log_path.read_bytes()
        review_before = review_path.read_bytes()
        ref = "refs/ask/accepted-tests/w"
        accepted_before = consumer.git("rev-parse", ref)
        try:
            log_path.write_bytes(log_before + b"tampered")
            log_identity = workbench_loading.detail_identity(root, snapshot, test, source_context=context)
            self.assertNotEqual(original_identity, log_identity,
                                "a retained execution-log mutation invalidates selected detail")
            changed_log = workbench_loading.load_selected_detail(
                root, snapshot, test, node_id="case", source_context=context, cache=cache)
            self.assertIsNot(first, changed_log)
            self.assertNotEqual(first["evidence"], changed_log["evidence"])
            self.assertIn(changed_log["evidence"].get("status"), {"invalid", "unavailable"})
            log_path.write_bytes(log_before)

            review_doc = json.loads(review_before)
            review_doc["candidate_sha"] = "0" * 40
            review_path.write_text(json.dumps(review_doc), encoding="utf-8")
            review_identity = workbench_loading.detail_identity(root, snapshot, test, source_context=context)
            self.assertNotEqual(original_identity, review_identity,
                                "a retained semantic-review mutation invalidates selected detail")

            consumer.git("update-ref", ref, consumer.red_sha)
            ref_identity = workbench_loading.detail_identity(root, snapshot, test, source_context=context)
            self.assertNotEqual(review_identity, ref_identity,
                                "the accepted authority ref participates in selected-detail identity")
            changed_authority = workbench_loading.load_selected_detail(
                root, snapshot, test, node_id="case", source_context=context, cache=cache)
            self.assertIn(changed_authority["evidence"].get("status"), {"invalid", "unavailable"})

            # Stale displayed identity still cannot authorize a guarded mutation.
            before_model = (root / "work/w/engineering-model.json").read_bytes()
            from engineering_model.actions import edit
            stale = edit(root, "w", "0" * 64, {"commands": []})
            self.assertFalse(stale["valid"], "admission/guard rejects a stale displayed identity")
            self.assertEqual((root / "work/w/engineering-model.json").read_bytes(), before_model)
        finally:
            log_path.write_bytes(log_before)
            review_path.write_bytes(review_before)
            consumer.git("update-ref", ref, accepted_before)

        source_path = root / test["source_paths"][0]
        source_before = source_path.read_bytes()
        source_stat = source_path.stat()
        try:
            source_path.write_bytes(source_before + b"\n# changed source bytes\n")
            os.utime(source_path, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
            self.assertNotEqual(original_identity, workbench_loading.detail_identity(
                root, snapshot, test, source_context=context),
                "guaranteed same-mtime source mutation invalidates selected detail")
        finally:
            source_path.write_bytes(source_before)
            os.utime(source_path, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))

    def test_overview_is_lazy_and_selected_details_are_cached(self):
        consumer, _ = evidence_workbench()
        self.addCleanup(consumer.close)
        source_reads = patch.object(workbench_loading, "_working_source",
                                    wraps=workbench_loading._working_source)
        history_reads = patch.object(workbench_loading, "execution_history",
                                     wraps=workbench_loading.execution_history)
        evidence_reads = patch("engineering_model.projection.inspect_evidence",
                               wraps=__import__("engineering_model.projection", fromlist=["inspect_evidence"]).inspect_evidence)
        with (patch.dict(os.environ, {"ASK_MODEL_ROOT": str(consumer.root)}),
              source_reads as source, history_reads as history, evidence_reads as evidence):
            app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            view = app.session_state["_engineering_displayed_view"]
            metadata = {item["id"]: item for item in view["projection"]["workbench"]["tests"]}
            self.assertIn("U", metadata, "initial overview has canonical selected-test metadata")
            self.assertEqual(source.call_count, 0, "overview reads no test source")
            self.assertEqual(history.call_count, 0, "overview reads no execution history")
            self.assertEqual(evidence.call_count, 0, "overview performs no evidence inspection")

            app.button(key="route:scenario").click().run(timeout=20)
            app.button(key="route:purpose").click().run(timeout=20)
            self.assertEqual(source.call_count, 0, "metadata navigation and revisit remain source-lazy")
            self.assertEqual(history.call_count, 0, "metadata navigation and revisit remain evidence-lazy")
            self.assertEqual(evidence.call_count, 0)

            app.button(key="route:test:U").click().run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            self.assertGreater(source.call_count, 0, "selected test loads its qualified source")
            self.assertGreater(history.call_count, 0, "selected test loads its retained outcome")
            self.assertGreater(evidence.call_count, 0, "selected test evaluates only its retained evidence")
            selected_counts = source.call_count, history.call_count, evidence.call_count
            app.button(key="route:purpose").click().run(timeout=20)
            app.button(key="route:test:U").click().run(timeout=20)
            self.assertEqual((source.call_count, history.call_count, evidence.call_count), selected_counts,
                             "revisiting unchanged metadata and detail reuses the bounded cache")

    def test_measured_pilot_latency_budgets(self):
        consumer, _ = evidence_workbench()
        self.addCleanup(consumer.close)
        candidate_sha = __import__("subprocess").run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
            text=True, check=True).stdout.strip()
        evidence_dir = Path(os.environ.get("ASK_WB009_EVIDENCE_DIR", ROOT /
            "work/structured-agentic-environment/inner-loop/evidence"))
        output = evidence_dir / f"WB-009-latency-{candidate_sha}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.unlink(missing_ok=True)
        env = dict(os.environ, ASK_BROWSER_CHANNEL=os.environ.get("ASK_BROWSER_CHANNEL", "chrome"))
        completed = __import__("subprocess").run([
            sys.executable, str(ROOT / "_ask/ui/benchmark_workbench.py"),
            "--model-root", str(consumer.root), "--work-id", "w",
            "--warm-samples", "20", "--cold-samples", "5", "--output", str(output),
        ], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
        self.assertTrue(output.is_file(), "raw benchmark report survives pass, budget miss or browser failure")
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["code_candidate_sha"], candidate_sha)
        self.assertEqual(report["workload"]["kind"], "isolated-consumer-fixture")
        self.assertTrue(report["workload"]["synthetic_model"])
        self.assertEqual(report["run_status"], "complete", report.get("error"))
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout), report,
                         "persisted raw report matches exact CLI output")
        self.assertEqual(len(report["warm_ms"]), 20)
        self.assertEqual(len(report["cold_start_to_ready_ms"]), 5)
        limits = report["limits_ms"]
        for metric, maximum in (("overview", 1500),
                                ("metadata_navigation", 500),
                                ("filter", 500),
                                ("source_result", limits["source_result"])):
            samples = [row[metric] for row in report["warm_ms"]]
            self.assertLessEqual(_nearest_rank(samples), maximum,
                                 f"{metric} nearest-rank p95 within {maximum}ms; samples={samples}")
        self.assertEqual(limits["overview"], 1500)
        self.assertEqual(limits["metadata_navigation"], 500)
        self.assertEqual(limits["filter"], 500)
        self.assertEqual(limits["source_result"], 1000)
        cold = [row["elapsed"] for row in report["cold_start_to_ready_ms"]]
        self.assertTrue(all(value <= limits["cold"] for value in cold),
                        f"each cold start <= {limits['cold']}ms; samples={cold}")
        self.assertEqual([item["task_count"] for item in report["structural_workloads"]], [100, 1000])
        self.assertEqual(report["code_candidate_sha"], report["workload"]["code_candidate_sha"])


if __name__ == "__main__":
    unittest.main()
