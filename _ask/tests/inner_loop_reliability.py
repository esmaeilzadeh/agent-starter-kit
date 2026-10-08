"""Public state/coordinator contracts, using processes and disposable Git repos."""
from __future__ import annotations

import os
import json
import shlex
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from inner_loop.state import SecondWriter, cas_apply, cas_init, load_state
from inner_loop.driver import NotIntegrable, integrate_ready, run_until, resume_from_state
from inner_loop.evidence import record_review
from traceability_support import seed as seed_traceability, accept as accept_traceability, review as review_traceability


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q", "-b", "agent/w")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write(".gitignore", "work/w/inner-loop/state.*\nwork/w/inner-loop/results/\nwork/w/inner-loop/evidence/\n")
        self.write(".agents/verification.yaml", "schema: ask-checkplan/v1\nno_production_datastore: true\nchecks:\n  - id: required\n    tier: mandatory\n    command: 'true'\n")
        source = Path(__file__).resolve().parents[2] / ".agents/ask/verification"
        shutil.copytree(source, self.root / ".agents/ask/verification",
                        ignore=shutil.ignore_patterns("__pycache__"))
        self.write("_ask/policies/delegation.md", "Coordinator delegates review to an identified review agent.\n")
        self.write("work/w/inner-loop/tasks.yaml", "schema: ask-inner-loop-tasks/v1\nwork_id: w\ntasks:\n  - id: a\n    depends_on: []\n    owned_paths: [src/**]\n  - id: b\n    depends_on: [a]\n    owned_paths: [src/**]\n")
        self.write("src/value", "base\n")
        seed_traceability(self.root,"w")
        self.commit("base")
        accept_traceability(self.root,"w")
        self.base = self.git("rev-parse", "HEAD")
        self.assertEqual(run_until(self.root, "w"), "running=a")
        self.write("src/value", "candidate\n")
        self.commit("candidate")
        self.candidate = self.git("rev-parse", "HEAD")
        self.result = {
            "schema": "ask-task-result/v2", "work_id": "w", "task_id": "a",
            "base_sha": self.base, "candidate_sha": self.candidate,
            "tdd": {"seam": "src", "red": {"command": "test", "output": "FAIL", "exit_code": 1},
                    "green": {"command": "test", "output": "PASS", "exit_code": 0}},
            "exemption": None,
        }
        self.submit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.PIPE).strip()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)

    def submit(self):
        return self.write("work/w/inner-loop/results/a.json", json.dumps(self.result))

    def review(self, **options):
        review_traceability(self.root,"w",self.result["candidate_sha"])
        self.write("work/w/inner-loop/evidence/review.md", "Reviewer: independent-agent; APPROVED\n")
        return record_review(self.root, "w", "a", "independent-agent", "_ask/policies/delegation.md",
                             "work/w/inner-loop/evidence/review.md", **options)

    def check(self, command=None):
        content = "schema: ask-checkplan/v1\nno_production_datastore: true\n"
        if command is not None:
            content += f"checks:\n  - id: required\n    tier: mandatory\n    command: {json.dumps(command)}\n"
        self.write(".agents/verification.yaml", content)
        self.commit("check configuration")
        self.candidate = self.git("rev-parse", "HEAD")
        self.result["candidate_sha"] = self.candidate
        self.submit()

    def task_branch(self):
        self.git("switch", "-qc", "task", self.candidate)
        self.git("branch", "-f", "agent/w", self.base)
        self.git("switch", "-q", "agent/w")
        doc = load_state(self.root, "w")
        cas_apply(self.root, "w", doc["revision"],
                  lambda d: d["tasks"]["a"].update(task_branch="task"))

    def wait_for(self, path, proc):
        deadline = time.monotonic() + 10
        while not path.exists():
            if proc.poll() is not None or time.monotonic() > deadline:
                self.fail("integration child did not reach checkpoint")
            time.sleep(.005)

    def integrate_process(self, prelude=""):
        code = """
import os,sys,time
from pathlib import Path
from inner_loop.driver import integrate_ready,NotIntegrable
root=Path(sys.argv[1])
PRELUDE
try:
 print(integrate_ready(root,'w','a'))
except NotIntegrable as exc:
 print(str(exc),file=sys.stderr)
 sys.exit(2)
""".replace("PRELUDE", prelude)
        proc = subprocess.Popen([sys.executable, "-c", code, str(self.root)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: proc.kill() if proc.poll() is None else None)
        return proc

    def paused_integration(self):
        started = self.root / "work/w/inner-loop/evidence/check-started"
        proceed = self.root / "work/w/inner-loop/evidence/check-continue"
        self.check(f"touch {shlex.quote(str(started))}; while [ ! -e {shlex.quote(str(proceed))} ]; do sleep .01; done")
        self.review()
        proc = self.integrate_process()
        self.wait_for(started, proc)
        return proc, proceed

    def test_other_candidate_report_is_rejected(self):
        self.result["candidate_sha"] = self.base
        self.submit()
        with self.assertRaisesRegex(NotIntegrable, "candidate"):
            integrate_ready(self.root, "w", "a")
        self.assertEqual(load_state(self.root, "w")["tasks"]["a"]["status"], "running")

    def test_other_work_task_and_base_reports_are_rejected(self):
        for field, value in [("work_id", "other"), ("task_id", "b"), ("base_sha", self.candidate)]:
            with self.subTest(field=field):
                original = self.result[field]
                self.result[field] = value
                self.submit()
                with self.assertRaisesRegex(NotIntegrable, field):
                    integrate_ready(self.root, "w", "a")
                self.result[field] = original

    def test_worker_passing_fields_do_not_authorize_integration(self):
        self.result["review"] = {"verdict": "APPROVED", "reviewer": "made-up"}
        self.submit()
        with self.assertRaisesRegex(NotIntegrable, "coordinator-recorded review"):
            integrate_ready(self.root, "w", "a")

    def test_successful_in_place_integration_records_executed_lineage(self):
        self.review()
        self.assertEqual(integrate_ready(self.root, "w", "a"), self.candidate)
        state = load_state(self.root, "w")
        task = state["tasks"]["a"]
        self.assertEqual(task["status"], "integrated")
        evidence = task["evidence"]["verification"]
        self.assertEqual((evidence["base_sha"], evidence["candidate_sha"], evidence["resulting_sha"]),
                         (self.base, self.candidate, self.candidate))
        self.assertEqual(evidence["checks"][0]["command"], "true")
        self.assertEqual(evidence["checks"][0]["exit_code"], 0)
        self.assertEqual(evidence["review"]["reviewer"], "independent-agent")
        self.assertTrue((self.root / evidence["record_path"]).is_file())
        self.assertEqual(state["coordinator_sha"], self.candidate)

    def test_failed_candidate_checks_prevent_fast_forward_and_state_fold(self):
        self.check("exit 7")
        self.task_branch()
        self.review()
        with self.assertRaisesRegex(NotIntegrable, "verification failed"):
            integrate_ready(self.root, "w", "a")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        self.assertEqual(load_state(self.root, "w")["tasks"]["a"]["status"], "running")
        reports = list(self.root.glob("work/w/inner-loop/evidence/verify-*/integration.json"))
        self.assertEqual(len(reports), 1)
        evidence = json.loads(reports[0].read_text())
        self.assertEqual(evidence["result"], "fail")
        self.assertEqual(evidence["checks"][0]["exit_code"], 7)

    def test_candidate_cannot_replace_the_verifier_checking_it(self):
        self.write(".agents/ask/verification/run.py", "raise SystemExit(0)\n")
        self.write(".agents/ask/verification/plan.py", "raise RuntimeError('candidate import must not run')\n")
        self.check("exit 9")
        self.task_branch()
        self.review()
        with self.assertRaisesRegex(NotIntegrable, "verification failed"):
            integrate_ready(self.root, "w", "a")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        reports = list(self.root.glob("work/w/inner-loop/evidence/verify-*/integration.json"))
        report = json.loads(reports[0].read_text())
        self.assertEqual(report["checks"][0]["exit_code"], 9)
        self.assertEqual(report["runner_sha"], self.base)

    def test_empty_checkplan_does_not_integrate(self):
        self.check()
        self.review()
        with self.assertRaisesRegex(NotIntegrable, "empty CheckPlan"):
            integrate_ready(self.root, "w", "a")
        self.assertEqual(load_state(self.root, "w")["coordinator_sha"], self.base)

    def test_fast_forward_matches_verified_candidate(self):
        self.task_branch()
        self.review()
        self.assertEqual(integrate_ready(self.root, "w", "a"), self.candidate)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.candidate)
        self.assertEqual(len(self.git("worktree", "list", "--porcelain").split("worktree ")) - 1, 1)

    def test_changed_result_or_review_cannot_reuse_approval(self):
        self.review()
        self.result["notes"] = "changed after review"
        self.submit()
        with self.assertRaisesRegex(NotIntegrable, "stale coordinator-recorded review"):
            integrate_ready(self.root, "w", "a")
        self.review()
        self.write("work/w/inner-loop/evidence/review.md", "changed after recording")
        with self.assertRaisesRegex(NotIntegrable, "stale review evidence"):
            integrate_ready(self.root, "w", "a")

    def test_review_rejection_and_boundary_rejection_prevent_integration(self):
        for options in ({"verdict": "REJECTED"}, {"boundary": "glob_too_narrow"}):
            self.review(**options)
            with self.assertRaisesRegex(NotIntegrable, "review must be APPROVED"):
                integrate_ready(self.root, "w", "a")

    def test_exemption_needs_supported_reason_and_coordinator_review(self):
        self.result["tdd"] = None
        self.result["exemption"] = {"kind": "documentation-only", "reason": "prose only", "reviewer_ack": True}
        self.submit()
        with self.assertRaisesRegex(NotIntegrable, "coordinator-recorded review"):
            integrate_ready(self.root, "w", "a")
        self.result["exemption"]["kind"] = "skip-tests"
        self.submit()
        with self.assertRaisesRegex(NotIntegrable, "unsupported exemption"):
            self.review()
        self.result["exemption"]["kind"] = "documentation-only"
        self.submit()
        self.review()
        integrate_ready(self.root, "w", "a")
        review = load_state(self.root, "w")["tasks"]["a"]["evidence"]["review"]
        self.assertEqual(review["exemption_reason"], "prose only")
        self.assertEqual(review["policy"], "_ask/policies/delegation.md")

    def test_tdd_history_requires_typed_exit_codes_and_captured_output(self):
        for field, value in [("exit_code", "0"), ("exit_code", False), ("output", "")]:
            self.result["tdd"]["green"][field] = value
            self.submit()
            with self.assertRaisesRegex(NotIntegrable, "green requires"):
                self.review()
            self.result["tdd"]["green"] = {"command": "test", "output": "PASS", "exit_code": 0}

    def test_uncommitted_source_is_refused(self):
        self.review()
        self.write("src/value", "uncommitted")
        with self.assertRaisesRegex(NotIntegrable, "dirty coordinator source"):
            integrate_ready(self.root, "w", "a")

    def test_verification_that_modifies_candidate_source_is_refused(self):
        self.check("printf changed >> src/value")
        self.review()
        with self.assertRaisesRegex(NotIntegrable, "source/CheckPlan changed"):
            integrate_ready(self.root, "w", "a")
        self.assertEqual((self.root / "src/value").read_text(), "candidate\n")
        self.assertEqual(load_state(self.root, "w")["tasks"]["a"]["status"], "running")

    def test_result_drift_during_verification_is_refused(self):
        proc, proceed = self.paused_integration()
        self.result["notes"] = "modified while checks run"
        self.submit()
        proceed.touch()
        _, err = proc.communicate(timeout=15)
        self.assertEqual(proc.returncode, 2, err)
        self.assertIn("changed during verification", err)
        self.assertEqual(load_state(self.root, "w")["tasks"]["a"]["status"], "running")

    def test_review_drift_during_verification_is_refused(self):
        proc, proceed = self.paused_integration()
        self.write("work/w/inner-loop/evidence/review.md", "withdrawn review")
        proceed.touch()
        _, err = proc.communicate(timeout=15)
        self.assertEqual(proc.returncode, 2, err)
        self.assertIn("stale review evidence", err)

    def test_resume_preserves_candidate_after_ff_before_state_fold_interruption(self):
        self.task_branch()
        self.review()
        marker = self.root / "work/w/inner-loop/evidence/before-state-fold"
        proc = self.integrate_process("""
def interrupt(src,dst):
 (root/'work/w/inner-loop/evidence/before-state-fold').touch()
 time.sleep(60)
os.replace=interrupt
""")
        self.wait_for(marker, proc)
        proc.kill()
        proc.communicate(timeout=5)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.candidate)
        self.assertEqual(load_state(self.root, "w")["coordinator_sha"], self.base)
        self.assertEqual(resume_from_state(self.root, "w"), "running=b")
        state = load_state(self.root, "w")
        self.assertEqual(state["tasks"]["a"]["status"], "integrated")
        self.assertEqual(state["coordinator_sha"], self.candidate)
        self.assertEqual(state["tasks"]["b"]["base_sha"], self.candidate)

    def test_concurrent_state_update_cannot_interleave_with_integration(self):
        integrating, proceed = self.paused_integration()
        code = """
import sys
from pathlib import Path
from inner_loop.state import load_state,cas_apply,CasConflict
root=Path(sys.argv[1]); observed=load_state(root,'w')['revision']
(root/'work/w/inner-loop/evidence/update-started').touch()
try:
 cas_apply(root,'w',observed,lambda d: d['tasks']['a'].update(status='cancelled'))
 print('cancelled')
except CasConflict: print('conflict')
"""
        updater = subprocess.Popen([sys.executable, "-c", code, str(self.root)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: updater.kill() if updater.poll() is None else None)
        self.wait_for(self.root / "work/w/inner-loop/evidence/update-started", updater)
        time.sleep(.05)
        self.assertIsNone(updater.poll())
        self.assertEqual(load_state(self.root, "w")["tasks"]["a"]["status"], "running")
        proceed.touch()
        _, err = integrating.communicate(timeout=15)
        self.assertEqual(integrating.returncode, 0, err)
        out, err = updater.communicate(timeout=10)
        self.assertEqual(updater.returncode, 0, err)
        self.assertEqual(out.strip(), "conflict")
        self.assertEqual(load_state(self.root, "w")["tasks"]["a"]["status"], "integrated")

    def test_candidate_branch_drift_during_verification_is_refused(self):
        started = self.root / "work/w/inner-loop/evidence/check-started"
        proceed = self.root / "work/w/inner-loop/evidence/check-continue"
        self.check(f"touch {shlex.quote(str(started))}; while [ ! -e {shlex.quote(str(proceed))} ]; do sleep .01; done")
        self.task_branch()
        self.review()
        proc = self.integrate_process()
        self.wait_for(started, proc)
        self.git("branch", "-f", "task", self.base)
        proceed.touch()
        _, err = proc.communicate(timeout=15)
        self.assertEqual(proc.returncode, 2, err)
        self.assertIn("candidate_sha mismatch", err)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_non_fast_forward_combination_is_refused(self):
        self.task_branch()
        self.write("src/other", "unrelated coordinator change")
        self.commit("divergent coordinator")
        with self.assertRaises(NotIntegrable):
            self.review()

    def test_worker_role_cannot_record_coordinator_review(self):
        from inner_loop.state import ProtocolViolation
        self.write("work/w/inner-loop/evidence/review.md", "APPROVED")
        previous = os.environ.get("ASK_INNER_LOOP_ROLE")
        os.environ["ASK_INNER_LOOP_ROLE"] = "worker"
        try:
            with self.assertRaises(ProtocolViolation):
                record_review(self.root, "w", "a", "worker", "_ask/policies/delegation.md",
                              "work/w/inner-loop/evidence/review.md")
        finally:
            if previous is None:
                os.environ.pop("ASK_INNER_LOOP_ROLE", None)
            else:
                os.environ["ASK_INNER_LOOP_ROLE"] = previous

    def test_resume_source_repair_preserves_tracked_runtime_revision_and_review(self):
        self.git("add", "-f", "work/w/inner-loop/state.json")
        self.git("commit", "-qm", "track runtime snapshot")
        self.candidate = self.git("rev-parse", "HEAD")
        self.result["candidate_sha"] = self.candidate
        self.submit()
        self.review()
        before = load_state(self.root, "w")
        self.write("src/value", "dirty source")
        try:
            resume_from_state(self.root, "w")
        except NotIntegrable:
            pass  # Source repair invalidates the old in-place candidate.
        after = load_state(self.root, "w")
        self.assertEqual(after, before)
        self.assertEqual(after["tasks"]["a"]["evidence"]["review"]["reviewer"], "independent-agent")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)
        self.assertEqual((self.root / "src/value").read_text(), "base\n")

    def test_resume_merge_repair_preserves_tracked_runtime_state(self):
        self.git("switch", "-qc", "other", self.base)
        self.write("src/value", "other branch\n")
        self.commit("conflicting branch")
        self.git("switch", "-q", "agent/w")
        self.git("add", "-f", "work/w/inner-loop/state.json")
        self.git("commit", "-qm", "track runtime snapshot")
        self.result["candidate_sha"] = self.git("rev-parse", "HEAD")
        self.submit()
        self.review()
        before = load_state(self.root, "w")
        with self.assertRaises(subprocess.CalledProcessError):
            self.git("merge", "other")
        try:
            resume_from_state(self.root, "w")
        except NotIntegrable:
            pass
        self.assertEqual(load_state(self.root, "w"), before)
        self.assertFalse((self.root / ".git/MERGE_HEAD").exists())
        self.assertEqual((self.root / "src/value").read_text(), "base\n")


class StateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        cas_init(self.root, "w", ["a", "b"])

    def contend(self, operation):
        code = """
import sys,time
from pathlib import Path
from inner_loop.state import cas_init,cas_apply,spawn_writer,CasConflict,SecondWriter
root=Path(sys.argv[1]); token=sys.argv[2]
(root/token).touch()
while not (root/'go').exists(): time.sleep(.005)
try:
 OPERATION
 print('success')
except (CasConflict,SecondWriter): print('conflict')
""".replace("OPERATION", operation)
        procs = [subprocess.Popen([sys.executable, "-c", code, str(self.root), str(i)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for i in range(2)]
        self.addCleanup(lambda: [p.kill() for p in procs if p.poll() is None])
        deadline = time.monotonic() + 10
        while not all((self.root / str(i)).exists() for i in range(2)):
            if time.monotonic() > deadline:
                self.fail("child startup timed out")
            time.sleep(.005)
        (self.root / "go").touch()
        outputs = []
        for p in procs:
            out, err = p.communicate(timeout=10)
            self.assertEqual(p.returncode, 0, err)
            outputs.append(out.strip())
        return sorted(outputs)

    def test_competing_same_revision_cannot_both_succeed(self):
        self.assertEqual(self.contend("cas_apply(root,'w',0,lambda d: time.sleep(.25))"),
                         ["conflict", "success"])
        self.assertEqual(load_state(self.root, "w")["revision"], 1)

    def test_competing_starts_leave_one_writer(self):
        self.assertEqual(self.contend("spawn_writer(root,'w',['a','b'][int(token)])"),
                         ["conflict", "success"])
        state = load_state(self.root, "w")
        self.assertEqual(sum(t["status"] == "running" for t in state["tasks"].values()), 1)
        self.assertEqual(state["revision"], 1)

    def test_concurrent_initialization_does_not_reset_state(self):
        cas_apply(self.root, "w", 0, lambda d: d.update(coordinator_sha="kept"))
        self.assertEqual(self.contend("cas_init(root,'w',['wrong'])"), ["success", "success"])
        state = load_state(self.root, "w")
        self.assertEqual(state["revision"], 1)
        self.assertEqual(state["coordinator_sha"], "kept")
        self.assertEqual(sorted(state["tasks"]), ["a", "b"])

    def test_every_transaction_preserves_single_writer(self):
        def mutate(doc):
            for task in doc["tasks"].values():
                task["status"] = "running"
        with self.assertRaises(SecondWriter):
            cas_apply(self.root, "w", 0, mutate)
        self.assertEqual(load_state(self.root, "w")["revision"], 0)

    def test_readers_observe_complete_documents_during_writes(self):
        code = """
import sys,time
from pathlib import Path
from inner_loop.state import cas_apply
root=Path(sys.argv[1])
for i in range(80):
 cas_apply(root,'w',i,lambda d: d.update(payload='x'*100000))
 time.sleep(.001)
"""
        proc = subprocess.Popen([sys.executable, "-c", code, str(self.root)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: proc.kill() if proc.poll() is None else None)
        reads = 0
        deadline = time.monotonic() + 15
        while proc.poll() is None:
            state = load_state(self.root, "w")
            self.assertGreaterEqual(state["revision"], 0)
            reads += 1
            if time.monotonic() > deadline:
                self.fail("writer timed out")
        _, err = proc.communicate(timeout=5)
        self.assertEqual(proc.returncode, 0, err)
        self.assertGreater(reads, 0)
        self.assertEqual(load_state(self.root, "w")["revision"], 80)

    def test_interrupted_replacement_preserves_old_state_and_releases_lock(self):
        code = """
import os,sys,time
from pathlib import Path
from inner_loop.state import cas_apply
root=Path(sys.argv[1])
def interrupt(src,dst):
 (root/'before-replace').touch()
 time.sleep(60)
os.replace=interrupt
cas_apply(root,'w',0,lambda d: d.update(coordinator_sha='uncommitted'))
"""
        proc = subprocess.Popen([sys.executable, "-c", code, str(self.root)])
        self.addCleanup(lambda: proc.kill() if proc.poll() is None else None)
        deadline = time.monotonic() + 10
        while not (self.root / "before-replace").exists():
            if proc.poll() is not None or time.monotonic() > deadline:
                self.fail("writer did not reach replacement")
            time.sleep(.005)
        proc.kill()
        proc.wait(timeout=5)
        self.assertEqual(load_state(self.root, "w")["coordinator_sha"], "")
        self.assertEqual(cas_apply(self.root, "w", 0, lambda d: None)["revision"], 1)


if __name__ == "__main__":
    unittest.main()
