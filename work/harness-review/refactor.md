# Review-finding corrections

## F1: tracked runtime state during resume

Independent review reproduced loss of revision/review after source repair with
tracked state. The new regression failed before the correction (evidence/resume-red.log).
Resume now clears Git operation metadata, updates the coordinator ref, and
restores source paths with precise runtime exclusions. It does not reset or
remove runtime state/results/evidence or replace the persistent lock inode.
Public regressions cover ordinary dirty source and an actual merge conflict;
FF-before-fold recovery remains covered.

## Verification-runner provenance

Candidate verification now snapshots runner code and imports from the recorded
coordinator base, including plan expansion in a separate process. This matters
when the default in-place worker has already changed those files. Evidence
records runner base/digest. A candidate replacing run.py/plan.py still fails its
configured required check (exit 9); the missing provenance assertion failed
before the change (evidence/runner-provenance-red.log).

## Executed validation

All 29 reliability cases pass (evidence/resume-green.log). Independent re-review
and final full CheckPlan verification remain pending at this checkpoint. The
same-family model fallback limits remain; no broader security claim is made.
