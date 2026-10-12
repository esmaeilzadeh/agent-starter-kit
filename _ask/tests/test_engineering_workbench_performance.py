"""Integrity-bound detail cache and reproducible latency budget checks."""
from __future__ import annotations

import json
import os
import copy
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
from workbench_tests import render_test


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
    @staticmethod
    def _render_test_text(projection, test_id, detail):
        script = """
import sys
sys.path.insert(0, %r)
from workbench_tests import render_test
render_test(%r, %r, detail=%r)
""" % (str(ROOT / "_ask/ui"), projection, test_id, detail)
        app = AppTest.from_string(script).run(timeout=30)
        if app.exception:
            raise AssertionError(app.exception)
        return "\n".join(str(item.value) for group in (
            app.subheader, app.markdown, app.caption, app.info, app.error, app.warning,
            app.success, app.text, app.code) for item in group)

    def test_lazy_work_and_integrity_bound_cache_invalidation(self):
        new_reds = []

        def require(condition, message):
            if not condition:
                new_reds.append(message)

        from traceability_fixture import Consumer
        original_write = Consumer.write

        def include_helper_source(consumer, name, document):
            if name == "work/w/test-plan.json" and isinstance(document, dict):
                for accepted_test in document.get("tests", []):
                    if "app.py" not in accepted_test["source_paths"]:
                        accepted_test["source_paths"].append("app.py")
            return original_write(consumer, name, document)

        with patch.object(Consumer, "write", include_helper_source):
            consumer, historical = evidence_workbench()
        self.addCleanup(consumer.close)
        root = consumer.root
        snapshot, diagnostics = admit(root, "w")
        self.assertEqual(diagnostics, [], diagnostics)
        projection = project(snapshot, root, include_evidence=False)
        current_candidate = consumer.git("rev-parse", "HEAD")
        current_run = consumer.command("traceability", "run", "w", "--scope", "workstream",
                                      "--phase", "final_green", "--candidate-sha", current_candidate)
        self.assertEqual(current_run.returncode, 0, current_run.stdout + current_run.stderr)
        current_report = json.loads(current_run.stdout)
        current_green = next(case for case in current_report["cases"]
                             if case.get("test_id") == "U" and case.get("phase") == "final_green")
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
            root, snapshot, test, source_context=context, candidate_sha=historical)
        first = workbench_loading.load_selected_detail(
            root, snapshot, test, node_id="case", source_context=context,
            candidate_sha=historical, cache=cache)
        same = workbench_loading.load_selected_detail(
            root, snapshot, test, node_id="case", source_context=context,
            candidate_sha=historical, cache=cache)
        self.assertIs(first, same, "revisiting unchanged selected detail uses its integrity-bound cache")
        self.assertEqual(len(cache), 1)
        self.assertEqual(first["identity"], original_identity)

        # A working-tree source selection must show exact local bytes even when
        # evidence inspection is explicitly pinned to a historical candidate.
        source_path = root / test["source_paths"][0]
        source_before = source_path.read_bytes()
        source_marker = b"# working-tree-only-marker\n        "
        assertion = b"self.assertEqual(render('hello'),'HELLO')"
        try:
            self.assertIn(assertion, source_before, "fixture contains the selected source assertion")
            source_path.write_bytes(source_before.replace(assertion, source_marker + assertion, 1))
            working_detail = workbench_loading.load_selected_detail(
                root, snapshot, test, node_id="case", source_context=context,
                candidate_sha=current_candidate, cache=cache)
            require(working_detail["source"].get("status") == "working-tree",
                    "working-tree selection silently switches to a Git revision source")
            require("working-tree-only-marker" in working_detail["source"].get("source", ""),
                    "selected working-tree source omits exact uncommitted bytes")
            selected_green = next(run for run in working_detail["execution_history"].get("runs", [])
                                  if run.get("output_artifact") == current_green.get("output_artifact"))
            self.assertEqual(selected_green["source_status"], "current",
                             "fresh evidence must be current for the pinned Git candidate")
            rendered_current = self._render_test_text(projection, "U", working_detail)
            require("Git candidate currency: current" in rendered_current,
                    "recorded evidence does not state its currency against the selected Git candidate")
            require("Working source applicability: differs from selected source" in rendered_current,
                    "current Git evidence is incorrectly applicable to different working-tree test bytes")
        finally:
            source_path.write_bytes(source_before)

        # A second accepted helper file can change the test's behavior while
        # its selected test module and method remain unchanged.
        helper_path = root / "app.py"
        helper_before = helper_path.read_bytes()
        helper_after = b"def render(value): return value.lower()\n"
        try:
            helper_path.write_bytes(helper_after)
            helper_detail = workbench_loading.load_selected_detail(
                root, snapshot, test, node_id="case", source_context=context,
                candidate_sha=current_candidate, cache=cache)
            self.assertEqual(helper_detail["source"].get("source"),
                             workbench_loading.qualified_source(
                                 root, test, current_candidate,
                                 current_sha=current_candidate).get("source"),
                             "only a declared helper file changed; the test method is unchanged")
            helper_green = next(run for run in helper_detail["execution_history"].get("runs", [])
                                if run.get("output_artifact") == current_green.get("output_artifact"))
            require(helper_green.get("working_source_applicability") == "differs from selected source",
                    "changed accepted helper bytes are incorrectly reported as matching the selected source")
        finally:
            helper_path.write_bytes(helper_before)

        # A module import/helper change can alter selected-test behavior even
        # when the method body itself is byte-for-byte unchanged.
        helper_import = b"from app import render\n"
        helper_alias = b"from app import render as render\n"
        accepted_method = workbench_loading.qualified_source(
            root, test, current_candidate, current_sha=current_candidate).get("source")
        try:
            self.assertIn(helper_import, source_before)
            source_path.write_bytes(source_before.replace(helper_import, helper_alias, 1))
            helper_detail = workbench_loading.load_selected_detail(
                root, snapshot, test, node_id="case", source_context=context,
                candidate_sha=current_candidate, cache=cache)
            self.assertEqual(helper_detail["source"].get("source"), accepted_method,
                             "the helper-only fixture leaves the selected method snippet unchanged")
            helper_green = next(run for run in helper_detail["execution_history"].get("runs", [])
                                if run.get("output_artifact") == current_green.get("output_artifact"))
            self.assertEqual(helper_green.get("working_source_applicability"),
                             "differs from selected source",
                             "full accepted source-file bytes include helper/import behavior")
        finally:
            source_path.write_bytes(source_before)

        # Exercise the exact retained final-green artifact selected by this fixture.
        green_execution = next(item for item in consumer.green["executions"]
                               if item.get("phase") == "final_green")
        log_path = root / green_execution["output_artifact"]
        review_path = root / "work/w/traceability/reviews" / f"{historical}.json"
        self.assertTrue(log_path.is_file(), "selected final-green execution retains its exact output artifact")
        self.assertTrue(review_path.is_file(), "fixture retains a candidate-bound review")
        green_run = next(run for run in first["execution_history"]["runs"]
                         if run.get("output_artifact") == green_execution["output_artifact"]
                         and run.get("test_id") == "U")
        self.assertEqual(green_run["output_status"], "valid")
        log_before = log_path.read_bytes()
        review_before = review_path.read_bytes()
        ref = "refs/ask/accepted-tests/w"
        accepted_before = consumer.git("rev-parse", ref)
        try:
            log_path.write_bytes(log_before + b"tampered")
            log_identity = workbench_loading.detail_identity(
                root, snapshot, test, source_context=context, candidate_sha=historical)
            self.assertNotEqual(original_identity, log_identity,
                                "a retained execution-log mutation invalidates selected detail")
            changed_log = workbench_loading.load_selected_detail(
                root, snapshot, test, node_id="case", source_context=context,
                candidate_sha=historical, cache=cache)
            self.assertIsNot(first, changed_log)
            tampered_green = next(run for run in changed_log["execution_history"].get("runs", [])
                                  if run.get("output_artifact") == green_execution["output_artifact"]
                                  and run.get("test_id") == "U")
            self.assertEqual(tampered_green["output_status"], "invalid",
                             "reload marks this exact selected final-green artifact invalid")
            rendered = self._render_test_text(projection, "U", changed_log)
            require("Output integrity: invalid" in rendered,
                    "tampered selected output is missing its explicit invalid-integrity label")
            require("Untrusted execution evidence" in rendered,
                    "tampered selected output is missing its untrusted-state label")
            require("Recorded outcome: Passed" in rendered,
                    "actual recorded outcome is not presented separately from integrity state")
            log_path.write_bytes(log_before)

            review_doc = json.loads(review_before)
            review_doc["candidate_sha"] = "0" * 40
            review_path.write_text(json.dumps(review_doc), encoding="utf-8")
            review_identity = workbench_loading.detail_identity(
                root, snapshot, test, source_context=context, candidate_sha=historical)
            self.assertNotEqual(original_identity, review_identity,
                                "a retained semantic-review mutation invalidates selected detail")
            review_path.write_bytes(review_before)

            consumer.git("update-ref", ref, consumer.red_sha)
            ref_identity = workbench_loading.detail_identity(
                root, snapshot, test, source_context=context, candidate_sha=historical)
            self.assertNotEqual(original_identity, ref_identity,
                                "the accepted authority ref participates in selected-detail identity")
            changed_authority = workbench_loading.load_selected_detail(
                root, snapshot, test, node_id="case", source_context=context,
                candidate_sha=historical, cache=cache)
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

        # Plan-only tests still have canonical workstream evidence without a model test node.
        plan_only = next(item for item in projection["workbench"]["tests"] if item["id"] == "E")
        from engineering_model.evidence import inspect as inspect_workstream_evidence
        authoritative = inspect_workstream_evidence(root, "w", historical)
        plan_only_detail = workbench_loading.load_selected_detail(
            root, snapshot, plan_only, node_id="E", source_context=context,
            candidate_sha=historical)
        self.assertEqual(authoritative["status"], "historical")
        require(plan_only_detail["evidence"]["status"] == "historical",
                "plan-only test does not resolve canonical workstream evidence")
        self.assertEqual(plan_only_detail["execution_history"]["runs"][-1]["test_id"], "E")

        source_path = root / test["source_paths"][0]
        source_before = source_path.read_bytes()
        source_stat = source_path.stat()
        try:
            source_path.write_bytes(source_before + b"\n# changed source bytes\n")
            os.utime(source_path, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
            self.assertNotEqual(original_identity, workbench_loading.detail_identity(
                root, snapshot, test, source_context=context, candidate_sha=historical),
                "guaranteed same-mtime source mutation invalidates selected detail")
        finally:
            source_path.write_bytes(source_before)
            os.utime(source_path, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))

        # A new HEAD changes current-candidate identity even when selected files are unchanged.
        current_identity = workbench_loading.detail_identity(
            root, snapshot, test, source_context=context, candidate_sha=None)
        pinned_identity = workbench_loading.detail_identity(
            root, snapshot, test, source_context=context, candidate_sha=historical)
        consumer.git("commit", "--allow-empty", "-m", "advance current candidate identity")
        advanced_head = consumer.git("rev-parse", "HEAD")
        pinned_after_advance = workbench_loading.detail_identity(
            root, snapshot, test, source_context=context, candidate_sha=historical)
        require(pinned_identity != pinned_after_advance,
                "current HEAD is missing from cache identity when an evidence candidate is explicitly pinned")
        advanced = workbench_loading.load_selected_detail(
            root, snapshot, test, node_id="case", source_context=context,
            candidate_sha=None, cache=cache)
        require(current_identity != advanced["identity"],
                "current HEAD is missing from cache identity when no SHA is supplied")
        require(advanced["candidate_sha"] == advanced_head,
                "detail loading did not resolve an omitted candidate to current HEAD")

        # Exercise related-route navigation in the real app under this valid fixture root.
        with patch.dict(os.environ, {"ASK_MODEL_ROOT": str(root)}):
            route_app = AppTest.from_file(str(ROOT / "_ask/ui/streamlit_app.py")).run(timeout=30)
            self.assertFalse(route_app.exception, route_app.exception)
            displayed = route_app.session_state["_engineering_displayed_view"]
            resolved_projection = copy.deepcopy(displayed["projection"])
            choice = next(node for node in resolved_projection["model"]["nodes"]
                          if node.get("id") == "choice")
            choice["lifecycle"] = "resolved"
            displayed["projection"] = resolved_projection
            route_app.session_state["_engineering_displayed_view"] = displayed
            route_app.button(key="overview:attention:decision:choice").click().run(timeout=30)
            self.assertFalse(route_app.exception, route_app.exception)
            require(route_app.session_state["_engineering_route"] == "resolved-decision:choice",
                    "resolved decision cannot be opened by the shared related-route helper")
        self.assertEqual(new_reds, [], "new workbench defects:\n- " + "\n- ".join(new_reds))

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

            app.button(key="refresh").click().run(timeout=20)
            self.assertFalse(app.exception, app.exception)
            app.button(key="route:test:U").click().run(timeout=20)
            self.assertGreater(source.call_count, selected_counts[0],
                               "explicit refresh re-reads selected source bytes")
            self.assertGreater(history.call_count, selected_counts[1],
                               "explicit refresh re-evaluates retained execution history")
            self.assertGreater(evidence.call_count, selected_counts[2],
                               "explicit refresh revalidates retained evidence")

    def test_measured_pilot_latency_budgets(self):
        candidate_sha = __import__("subprocess").run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
            text=True, check=True).stdout.strip()
        evidence_dir = Path(os.environ.get("ASK_WB009_EVIDENCE_DIR", Path(
            __import__("tempfile").gettempdir()) / "ask-wb009-evidence" / "structured-agentic-environment"))
        output = evidence_dir / f"WB-009-latency-{candidate_sha}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.unlink(missing_ok=True)
        env = dict(os.environ, ASK_BROWSER_CHANNEL=os.environ.get("ASK_BROWSER_CHANNEL", "chrome"))
        completed = __import__("subprocess").run([
            sys.executable, str(ROOT / "_ask/ui/benchmark_workbench.py"),
            "--model-root", str(ROOT), "--work-id", "structured-agentic-environment",
            "--test-id", "MV-valid",
            "--warm-samples", "20", "--cold-samples", "5", "--output", str(output),
        ], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
        self.assertTrue(output.is_file(), "raw benchmark report survives pass, budget miss or browser failure")
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["code_candidate_sha"], candidate_sha)
        self.assertEqual(report["workload"]["kind"], "real-pilot")
        self.assertFalse(report["workload"]["synthetic_model"])
        self.assertEqual(report["workload"]["selected_test_id"], "MV-valid")
        self.assertEqual(report["workload"]["selected_case_id"],
                         "test_engineering_model.ModelValidationTests.test_valid_broad_model_and_external_refs")
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
        self.assertEqual(limits["cold"], 4000)
        cold = [row["elapsed"] for row in report["cold_start_to_ready_ms"]]
        self.assertTrue(all(value <= limits["cold"] for value in cold),
                        f"each cold start <= {limits['cold']}ms; samples={cold}")
        workloads = report["structural_workloads"]
        self.assertEqual([item["task_count"] for item in workloads], [100, 1000])
        for item in workloads:
            count = item["task_count"]
            self.assertTrue(item["admitted"])
            self.assertFalse(item["evidence_included"])
            self.assertEqual(item["test_count"], count)
            self.assertEqual(item["model_node_count"], 3 + 2 * count)
            self.assertEqual(item["graph_edge_count"], 2 + 2 * count)
            self.assertEqual(item["source_file_count"], count)
        self.assertEqual(report["code_candidate_sha"], report["workload"]["code_candidate_sha"])


if __name__ == "__main__":
    unittest.main()
