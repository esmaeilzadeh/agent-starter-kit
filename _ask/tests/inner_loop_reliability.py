"""Public state/coordinator contracts, using processes and disposable Git repos."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from inner_loop.state import SecondWriter, cas_apply, cas_init, load_state


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
