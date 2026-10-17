"""Real-browser performance budgets and structural scale evidence."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/ui"))

from benchmark_workbench import run  # noqa: E402


class WorkbenchPerformanceTests(unittest.TestCase):
    def test_real_pilot_twenty_warm_five_cold_samples_respect_budgets(self):
        runtime = Path(os.environ.get("ASK_TRACEABILITY_RUNTIME_ROOT", ROOT)).resolve()
        output = runtime / "work/revising-workbench/traceability/rwb109/browser-benchmark.json"
        result = run(ROOT, "revising-workbench", warm_samples=20, cold_samples=5,
                     output_path=output, test_id="WB-evidence-identity")
        self.assertEqual(result["run_status"], "complete")
        self.assertEqual(len(result["warm_ms"]), 20)
        self.assertEqual(len(result["cold_start_to_ready_ms"]), 5)
        self.assertEqual({item["task_count"] for item in result["structural_workloads"]}, {100, 1000})

        def p95(values):
            ordered = sorted(values)
            return ordered[math.ceil(.95 * len(ordered)) - 1]

        observed = {
            key: p95([sample[key] for sample in result["warm_ms"]])
            for key in ("overview", "metadata_navigation", "filter", "source_result")
        }
        limits = {"overview": 1500, "metadata_navigation": 500,
                  "filter": 500, "source_result": 1000}
        cold = [sample["elapsed"] for sample in result["cold_start_to_ready_ms"]]
        outcome = {"p95_ms": observed, "limits_ms": limits, "cold_ms": cold,
                   "cold_limit_ms": 4000,
                   "passed": all(observed[key] <= limit for key, limit in limits.items())
                   and all(value <= 4000 for value in cold)}
        result["budget_validation"] = outcome
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.assertTrue(outcome["passed"], outcome)
