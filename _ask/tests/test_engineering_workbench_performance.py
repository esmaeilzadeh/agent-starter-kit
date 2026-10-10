"""Integrity-bound detail cache and reproducible latency budget checks."""
from __future__ import annotations

import json
from pathlib import Path
import statistics
import sys
import tempfile
import unittest
from collections import OrderedDict
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
sys.path.insert(0, str(ROOT / "_ask/ui"))
sys.path.insert(0, str(Path(__file__).parent))
from engineering_fixture import evidence_workbench
from engineering_model.admission import admit
from engineering_model.projection import project
import workbench_loading
import benchmark_workbench


def _nearest_rank(values, percentile=.95):
    ordered = sorted(values)
    return ordered[max(0, int((len(ordered) * percentile + .999999) // 1) - 1)]


class WorkbenchTests(unittest.TestCase):
    def test_lazy_work_and_integrity_bound_cache_invalidation(self):
        consumer, _ = evidence_workbench()
        self.addCleanup(consumer.close)
        root = consumer.root
        snapshot, diagnostics = admit(root, "w")
        self.assertEqual(diagnostics, [], diagnostics)
        projection = project(snapshot, root, include_evidence=False)
        tests = {item["id"]: item for item in projection.get("workbench", {}).get("tests", [])}
        test = tests.get("U") or json.loads((root / "work/w/test-plan.json").read_text())["tests"][0]
        self.assertEqual(test["id"], "U")
        cache = OrderedDict()
        context = {"kind": "working-tree"}
        self.assertEqual(len(cache), 0, "overview projection leaves selected detail cache empty")
        original_identity = workbench_loading.detail_identity(
            root, snapshot, test, source_context=context)
        first = workbench_loading.load_selected_detail(
            root, snapshot, test, node_id="U", source_context=context, cache=cache)
        same = workbench_loading.load_selected_detail(
            root, snapshot, test, node_id="U", source_context=context, cache=cache)
        self.assertIs(first, same, "revisiting unchanged selected detail uses its integrity-bound cache")
        self.assertEqual(len(cache), 1)
        self.assertEqual(first["identity"], original_identity)

        plan_path = root / "work/w/test-plan.json"
        original_plan = plan_path.read_bytes()
        plan_path.write_bytes(original_plan + b"\n")
        changed_snapshot, diagnostics = admit(root, "w")
        self.assertTrue(diagnostics, "tampered plan is not admitted as new authority")
        changed_identity = workbench_loading.detail_identity(
            root, snapshot, test, source_context=context)
        self.assertNotEqual(original_identity, changed_identity,
                            "same-mtime content changes invalidate the detail cache")
        self.assertNotEqual(first["identity"], changed_identity)
        plan_path.write_bytes(original_plan)
        self.assertIsNotNone(changed_snapshot)

        source_paths = test.get("source_paths", [])
        if source_paths:
            source_path = root / source_paths[0]
            source_before = source_path.read_bytes() if source_path.is_file() else None
            if source_before is not None:
                source_path.write_bytes(source_before + b"\n# changed bytes\n")
                self.assertNotEqual(original_identity, workbench_loading.detail_identity(
                    root, snapshot, test, source_context=context),
                    "source byte mutation invalidates detail")
                source_path.write_bytes(source_before)

        trace = root / "work/w/traceability" / "selected-cache-probe.json"
        trace.parent.mkdir(parents=True, exist_ok=True)
        trace.write_text('{"candidate":"one"}', encoding="utf-8")
        first_trace = workbench_loading.detail_identity(root, snapshot, test, source_context=context)
        trace.write_text('{"candidate":"two"}', encoding="utf-8")
        second_trace = workbench_loading.detail_identity(root, snapshot, test, source_context=context)
        self.assertNotEqual(first_trace, second_trace, "traceability bytes invalidate selected detail")
        trace.unlink()

    def test_measured_pilot_latency_budgets(self):
        consumer, _ = evidence_workbench()
        self.addCleanup(consumer.close)
        report = benchmark_workbench.run(consumer.root, "w", warm_samples=20, cold_samples=5)
        self.assertEqual(len(report["warm_ms"]), 20)
        self.assertEqual(len(report["cold_start_to_ready_ms"]), 5)
        limits = report["limits_ms"]
        for metric, maximum in (("navigation", limits["navigation"]),
                                ("filter", limits["filter"]),
                                ("source_result", limits["source_result"])):
            samples = [row[metric] for row in report["warm_ms"]]
            self.assertLessEqual(_nearest_rank(samples), maximum,
                                 f"{metric} nearest-rank p95 within {maximum}ms; samples={samples}")
        cold = [row["elapsed"] for row in report["cold_start_to_ready_ms"]]
        self.assertTrue(all(value <= limits["cold"] for value in cold),
                        f"each cold start <= {limits['cold']}ms; samples={cold}")


if __name__ == "__main__":
    unittest.main()
