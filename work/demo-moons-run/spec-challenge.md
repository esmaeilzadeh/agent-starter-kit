# Specification Challenge

## Model

- model: grok-4.6
- runtime: cursor
- parent_model: grok-4.6
- Note: same-family as Spec; walkthrough used cheap-pool default after user asked to execute Path A.

## Specification

Canonical: `openspec/changes/demo-moons-run/` (proposal, delta spec
`specs/demo-moons-runs/spec.md`, design, tasks). `openspec validate
demo-moons-run --strict` passes (measured, exit 0). `openspec_cli.py
preflight demo-moons-run` passes (measured, exit 0). Kit `plan.md` and
`specs/current/demo-moons-run.md` are pointers, as designed.

All claims below were measured against the tree on
`agent/demo-moons-run`, not assumed.

## Ambiguities

1. **"Training MUST NOT start on a dirty tree" has no enforcement
   point.** `scripts/train_moons.py` performs no cleanliness check; the
   only dirty-tree gate is inside `record-run.sh` (line 37 calls
   `check-clean-worktree.sh`). The requirement is process-only and its
   scenario ("Clean config commit") is a permission, not a test. An
   implementer can train on a dirty tree and nothing refuses until
   record-run. The spec does not say whether this gate placement
   satisfies the requirement or whether the trainer was expected to
   refuse.
2. **Which commit the bound SHA names.** With the intermediate commit
   the design requires (see counterexample), the recorded SHA names the
   `train_output.json` commit, not the config commit. The spec's
   SHA-bound requirement ("`--commit-sha` equal to HEAD") admits both;
   design says "HEAD still names the trained config" (true — the config
   is in that commit's tree). Consistent, but a reader of tasks.md alone
   would expect the config commit to be the cited one.

## Missing failure cases

**Strongest counterexample — tasks.md dead-ends at 2.3 (measured).**

1. `.gitignore` does not cover `results/` artifacts:
   `git check-ignore -v results/moons-narrow/train_output.json` exits 1
   (not ignored).
2. Follow tasks.md literally: 2.1 commits `config.yaml` (tree clean);
   2.2 runs `train_moons.py`, which writes
   `results/moons-narrow/train_output.json` (`train_moons.py:52`) — a
   new untracked file.
3. 2.3 runs `./ask record-run`. `record-run.sh:37` calls
   `check-clean-worktree.sh`, which refuses on any
   `git status --porcelain` output, and porcelain reports untracked
   files (`check-clean-worktree.sh:11`). Exit non-zero; no registry
   row. Task 2.3 cannot complete.

So commit-before-train plus record-run's dirty-tree refuse **is**
jointly satisfiable — but only via a sequence tasks.md does not
contain: commit config → train → **commit `train_output.json`** →
record-run → **commit record-run artifacts**. Design.md prescribes the
intermediate commit ("Then commit that output before `record-run`");
tasks.md never absorbed it. Task 3.1 also presupposes "after the narrow
record-run artifacts are committed" with no task 2.4 listing that
commit. The same defect exists upstream in the demo seed:
`_ask/docs/demo/end-to-end-plan.md` Path A A5 runs train then
record-run with no intermediate commit, so the documented Path A script
fails at record-run on a fresh run — directly threatening the Why
("the same Path A must still complete under the OpenSpec redesign").
Design's risk row already scopes this as a walkthrough finding, not a
silent script edit.

Secondary: the "Config missing" scenario is already satisfied by
existing code (`train_moons.py:27-30` exits 1, writes nothing) — no
gap there.

## Over-constraint risks

- "This workstream SHALL record **exactly** these two runs" plus the
  fixed shared fields leave no room for a failed-then-retried training
  attempt: any retrain with a different seed or hyperparameter would
  violate the letter of the spec and require a Spec Change. Acceptable
  for a LOW-risk demo, but the word "exactly" makes record-run's
  row-replacement behavior (re-recording the same run-id updates the
  row in place, `record-run.sh:93-99`) the only legal retry path.
- Distinct-SHA requirement is satisfiable (narrow binds the
  train_output commit; wide binds a strictly later commit), but it
  forbids the legitimate degenerate case of both runs citing one commit
  that contains both configs — a reasonable alternative the spec
  excludes without stating why.

## Under-constraint risks

1. **Metric provenance is not bound.** Nothing requires `--metric` to
   equal the `accuracy` in `train_output.json`; `record-run.sh` accepts
   any string. A registry row could cite a number that does not match
   the artifact at the bound path, and every scenario still passes.
   The Why ("a score without path + SHA is not citable") implies the
   cited score is the trained one; the spec never says so.
2. **Config-at-SHA is not pinned.** record-run checks `config.yaml`
   exists on disk (`record-run.sh:48`), not in the bound commit. A
   commit that edits `config.yaml` between training and record-run
   would bind a SHA whose config differs from what was trained. No
   requirement forbids post-train config edits.

## Recommended clarifications

1. Add the two missing commit tasks to `tasks.md`: commit
   `train_output.json` before each record-run (2.2→2.3, 3.2→3.3), and
   commit narrow's record-run artifacts before 3.1. This absorbs
   design.md's existing decision; no What/Why change, no human
   decision needed.
2. Record the demo-doc Path A defect (A5 missing the intermediate
   commit) as a walkthrough finding, per design.md's risk row — do not
   silently edit `_ask/docs/demo/end-to-end-plan.md` in this
   workstream.
3. Optional, Spec Change territory if pursued: state that `--metric`
   MUST be the `accuracy` value from the run's `train_output.json`,
   and that no commit between train and record-run may touch that
   run's `config.yaml`.
4. Optional: clarify in the Commit-before-train requirement that the
   dirty-tree gate lives in `record-run`, not the trainer.

## Challenge verdict

**PASS.**

The core constraint set (commit-before-train + dirty-tree refuse +
SHA = HEAD + distinct SHAs) is jointly satisfiable — proven by the
sequence commit-config → train → commit-output → record-run →
commit-artifacts, which violates no requirement. The strongest
counterexample is a tasks-level omission whose resolution design.md
already decided; absorbing it is clerical, not a human decision.
Clarifications 1–2 should land before or during implementation; 3–4
are optional hardening.
