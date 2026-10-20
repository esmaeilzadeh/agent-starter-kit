"""Behavioral tests for the frozen reference benchmark input."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agents/ask"))

from workflow_refs.benchmark import BenchmarkError, capture_baseline


MANIFEST = ROOT / "work/shorter-hashes/benchmark/baseline.json"
BASELINE_SOURCE = "9a3d25d035baafc23508f242020d46fae7ff5b14"
PLAN_REVIEW_PATH = "work/structured-agentic-environment/traceability/plan-review.json"


def git_blob(revision: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


class ReferenceTests(unittest.TestCase):
    def test_frozen_corpus_and_tokenizer(self):
        import tiktoken

        first = capture_baseline(ROOT)
        second = capture_baseline(ROOT)

        self.assertEqual(first, second, "the frozen measurement must be reproducible")
        self.assertEqual(first.get("schema"), "ask-reference-benchmark/v1")
        self.assertEqual(first.get("baseline_source"), BASELINE_SOURCE)
        self.assertEqual(first.get("tokenizer"), {
            "package": "tiktoken",
            "version": "0.12.0",
            "encoding": "cl100k_base",
            "operation": "encode_ordinary",
            "text_encoding": "utf-8",
        })
        self.assertEqual([row["id"] for row in first.get("journeys", [])],
                         ["resume", "review", "completion"])

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        expected_files = manifest["files"]
        self.assertEqual(first.get("source_files"), expected_files)
        self.assertEqual(len(expected_files), 14)
        self.assertEqual(first.get("unique_metadata_bytes"),
                         sum(row["bytes"] for row in expected_files if row["metadata"]))

        encoding = tiktoken.get_encoding("cl100k_base")
        for journey, frozen in zip(first["journeys"], manifest["journeys"]):
            self.assertEqual(journey["question"], frozen["question"])
            self.assertIn("Question:\n" + frozen["question"], journey["transcript"])
            self.assertEqual(journey["input_tokens"],
                             len(encoding.encode_ordinary(journey["transcript"])))

        with patch("importlib.metadata.version", return_value="0.0.1"):
            with self.assertRaises(BenchmarkError):
                capture_baseline(ROOT)

        with patch("workflow_refs.benchmark._git_blob", return_value=b"corrupt source"):
            with self.assertRaisesRegex(BenchmarkError, "frozen source integrity mismatch"):
                capture_baseline(ROOT)
        with patch("workflow_refs.benchmark._git_blob",
                   side_effect=BenchmarkError("missing frozen Git input")):
            with self.assertRaisesRegex(BenchmarkError, "missing frozen Git input"):
                capture_baseline(ROOT)

        for mutate in (
            lambda value: value["files"][0].update(sha256="0" * 64),
            lambda value: value["tokenizer"].update(version="0.0.1"),
            lambda value: value["journeys"][0]["source_paths"].append("work/missing.json"),
            lambda value: value["journeys"][0].update(question="changed workload"),
        ):
            changed = copy.deepcopy(manifest)
            mutate(changed)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "baseline.json"
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaises(BenchmarkError):
                    capture_baseline(ROOT, manifest_path=path)

    def test_equivalent_questions_and_lookup_accounting(self):
        import tiktoken

        report = capture_baseline(ROOT)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        file_table = {row["path"]: row for row in manifest["files"]}
        used_files = set()
        encoding = tiktoken.get_encoding("cl100k_base")

        self.assertEqual(len(report["journeys"]), len(manifest["journeys"]))
        for measured, frozen in zip(report["journeys"], manifest["journeys"]):
            self.assertEqual(measured["question"], frozen["question"])
            self.assertIn("Question:\n" + frozen["question"], measured["transcript"])
            self.assertEqual(measured["input_tokens"],
                             len(encoding.encode_ordinary(measured["transcript"])))
            sources = measured["source_inputs"]
            self.assertEqual([item["path"] for item in sources], frozen["source_paths"])
            for item in sources:
                expected = file_table[item["path"]]
                actual = git_blob(BASELINE_SOURCE, item["path"])
                self.assertEqual(len(actual), expected["bytes"])
                self.assertEqual(hashlib.sha256(actual).hexdigest(), expected["sha256"])
                self.assertIn(f"Source ({item['path']}):\n{item['text']}", measured["transcript"])
                used_files.add(item["path"])

        self.assertEqual(used_files, set(file_table))
        by_id = {row["id"]: row for row in report["journeys"]}
        resume_sources = {item["path"]: item["text"]
                          for item in by_id["resume"]["source_inputs"]}
        resume_plan_path = "work/status-template-stage-detection/test-plan.json"
        resume_plan = json.loads(resume_sources[resume_plan_path])
        frozen_resume_plan = json.loads(git_blob(BASELINE_SOURCE, resume_plan_path))
        resume_scope = frozen_resume_plan["task_scopes"][0]
        resume_ids = set(resume_scope["test_ids"])
        resume_tests = [test for test in frozen_resume_plan["tests"] if test["id"] in resume_ids]
        resume_criteria = {criterion for test in resume_tests for criterion in test["criterion_ids"]}
        self.assertEqual(resume_plan["task_scopes"], [resume_scope])
        self.assertEqual(resume_plan["tests"], resume_tests)
        self.assertEqual(resume_plan["obligations"], [row for row in frozen_resume_plan["obligations"]
                                                       if row["criterion_id"] in resume_criteria])
        resume_runner_ids = {test["runner_id"] for test in resume_tests}
        self.assertEqual(resume_plan["runners"], [row for row in frozen_resume_plan["runners"]
                                                   if row["id"] in resume_runner_ids])
        self.assertNotIn("approval-checkpoint", by_id["resume"]["transcript"])
        resume_plan_text = resume_sources["work/status-template-stage-detection/plan.md"]
        self.assertIn("stage-inference", resume_plan_text)
        self.assertNotIn("approval-checkpoint", resume_plan_text)
        for path in ("work/status-template-stage-detection/intent-confirmation.json",
                     "work/status-template-stage-detection/traceability-accepted.json"):
            self.assertEqual(json.loads(resume_sources[path]),
                             json.loads(git_blob(BASELINE_SOURCE, path)))

        review_sources = {item["path"]: item["text"]
                          for item in by_id["review"]["source_inputs"]}
        task_plan = json.loads(review_sources["work/structured-agentic-environment/test-plan.json"])
        frozen_task_plan = json.loads(git_blob(
            BASELINE_SOURCE, "work/structured-agentic-environment/test-plan.json"
        ))
        first_scope = task_plan["task_scopes"][0]
        frozen_scope = frozen_task_plan["task_scopes"][0]
        self.assertEqual(first_scope["task_id"], "WB-001")
        self.assertEqual(task_plan["task_scopes"], [frozen_scope])
        selected_ids = set(frozen_scope["test_ids"])
        selected_tests = [test for test in frozen_task_plan["tests"] if test["id"] in selected_ids]
        self.assertEqual(task_plan["tests"], selected_tests)
        selected_criteria = {criterion for test in selected_tests for criterion in test["criterion_ids"]}
        expected_obligations = [row for row in frozen_task_plan["obligations"]
                                if row["criterion_id"] in selected_criteria]
        self.assertEqual(task_plan["obligations"], expected_obligations)
        selected_runners = {test["runner_id"] for test in selected_tests}
        expected_runners = [row for row in frozen_task_plan["runners"] if row["id"] in selected_runners]
        self.assertEqual(task_plan["runners"], expected_runners)
        self.assertTrue(selected_ids.isdisjoint({"WB-inventory", "WB-snapshot", "WB-source-errors"}))
        self.assertNotIn("WB-002", by_id["review"]["transcript"])
        self.assertIn("WB-001", review_sources["work/structured-agentic-environment/inner-loop/tasks.yaml"])
        self.assertNotIn("WB-002", review_sources["work/structured-agentic-environment/inner-loop/tasks.yaml"])
        self.assertIn("WB-001", review_sources["work/structured-agentic-environment/plan.md"])
        self.assertNotIn("WB-002", review_sources["work/structured-agentic-environment/plan.md"])
        spec_path = "specs/current/structured-agentic-environment.json"
        spec = json.loads(review_sources[spec_path])
        frozen_spec = json.loads(git_blob(BASELINE_SOURCE, spec_path))
        self.assertEqual(spec["criteria"], [row for row in frozen_spec["criteria"]
                                             if row["id"] in selected_criteria])
        self.assertIn("traceability-accepted.json", by_id["review"]["transcript"])
        self.assertIn(PLAN_REVIEW_PATH, review_sources)

        completion_sources = {item["path"]: item["text"]
                              for item in by_id["completion"]["source_inputs"]}
        result_path = "work/structured-agentic-environment/traceability/runs/03333875786242e2bc771c816a81fbf7/results.json"
        log_path = "work/structured-agentic-environment/traceability/runs/03333875786242e2bc771c816a81fbf7/6da66e942ce3447ca329242c39254aa2.log"
        frozen_result = json.loads(git_blob(BASELINE_SOURCE, result_path))
        captured_result = json.loads(completion_sources[result_path])
        self.assertEqual(captured_result, frozen_result)
        self.assertIn(captured_result["candidate_sha"], by_id["completion"]["transcript"])
        self.assertTrue(captured_result["cases"])
        self.assertIn(completion_sources[log_path], by_id["completion"]["transcript"])
        self.assertEqual(report["total_input_tokens"],
                         sum(row["input_tokens"] for row in report["journeys"]))

        metadata_files = {path for path, row in file_table.items() if row["metadata"]}
        self.assertEqual(report["metadata_files"], sorted(metadata_files))
        self.assertEqual(report["unique_metadata_bytes"],
                         sum(file_table[path]["bytes"] for path in metadata_files))


if __name__ == "__main__":
    unittest.main()
