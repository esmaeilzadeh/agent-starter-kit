# Plan

## Specification

`specs/current/openspec-governance-integration.md` (Status CURRENT). Do not
restate Goal, Behavior, or Acceptance criteria here.

Pin decision (closes the spec Open question for this workstream):
`@fission-ai/openspec` revision `1.13.0`. Challenge measurements in
`work/openspec-governance-integration/spec-challenge.md` are 1.12.0; re-measure
targeted JSON field names and init flags on 1.13.0 before wiring gates.

Until the named **cutover** commit, this file is the plan source of truth and
the CURRENT kit spec remains the complete requirements document. Cutover copies
this Work breakdown into OpenSpec `design.md` / `tasks.md`, then replaces this
file with a pointer.

## Approach

Add a fail-closed OpenSpec invoke helper (pin, version assert, targeted CLI,
JSON shape checks, `nextSteps` strip). Non-pilot paths stay on today's scripts.
Mark this work-id as the dogfood pilot (`Engine: openspec` already in intent).

Sequence is load-bearing: record the pre-switch baseline and create the OpenSpec
change **before** `check-workstream` / `status` / `verify` start requiring it.
Cutover is one commit: init structure-only, write
`openspec/changes/openspec-governance-integration/` from the CURRENT spec plus
this plan, replace both kit spec copies and this `plan.md` with pointers.

Tests stub `OPENSPEC_BIN`. `install-kit.sh` stays Node-free. Real CLI is a
gated-command dependency, not an install-time dependency.

## Work breakdown

Done-when for each step: the listed files exist with the stated behavior, and
the named tests pass.

1. **Baseline.** Write `work/openspec-governance-integration/baseline.md`
   covering the spec's comparison measures against this workstream's kit flow
   (Grill → Spec → Challenge → Spec Change → this Plan). Done when that file
   exists and names each measure.

2. **Pin + invoke helper.** Kit-owned `_ask/openspec-pin.yaml`: `package`,
   `revision: "1.13.0"`, `schema`, `profile`. Refuse `latest`. Helper (Python,
   called from bash) locates `OPENSPEC_BIN` or `PATH`, asserts version, runs
   only targeted `validate <id> --strict` and `status --change <id>` for gates,
   fail-closed on missing binary, mismatch, invalid JSON, `root: null`, or
   `status[].severity == error`, strips/relabels `nextSteps`. Re-measure 1.13.0
   field names and `openspec init` flags; record measured names in the helper
   comments or ADR. Test: pin refuses `latest`; stub CLI covers exit-0 error
   payload and empty-set `--all` (helper must not offer `--all`). Done when
   helper tests pass without Node.

3. **Cutover.** `openspec init` structure-only (re-measured flags; 1.12.0 used
   `--tools none --no-animation`). Create
   `openspec/changes/openspec-governance-integration/` with proposal, behavioral
   deltas copied from CURRENT, design, tasks from this breakdown, `.openspec.yaml`
   **without** `skip_specs`. Proposal records legacy source
   `specs/current/openspec-governance-integration.md`. Replace
   `specs/current/openspec-governance-integration.md`,
   `specs/proposals/openspec-governance-integration.md`, and this `plan.md` with
   pointers (Status + one link; no Goal / Behavior / Acceptance / Approach /
   Work-breakdown). After default setup, list `.cursor/commands` and
   `.cursor/skills` and confirm no OpenSpec-generated command or skill files.
   Park `.later/openspec-pilot-evaluation.md`. Done when targeted
   `openspec validate openspec-governance-integration --strict` is valid and
   `openspec status --change openspec-governance-integration` reports planning
   complete; kit pointer files have no meaningful duplicate content.

4. **`check-workstream`.** If `work/<id>/intent.md` matches
   `^Engine:\s*openspec\s*$`, require the matching OpenSpec change (verbatim
   work-id; fail closed on no-match or more-than-one), targeted validate/status
   via the helper, incomplete/invalid per spec (re-measured fields), pointer-form
   duplicates, and `skip_specs` only with a recorded proposal reason (this
   dogfood change must carry deltas). Pass path: this work-id on clean
   `agent/openspec-governance-integration` with valid complete change + kit
   governance files. Absence of the marker keeps today's behavior. After valid
   Accept plus openspec-archive, look up
   `openspec/changes/archive/<date>-<id>/` instead of failing missing-change.
   Tests: `_ask/tests/test-workstream-smoke.sh` unchanged-pass; new tests for
   marker, missing/incomplete/invalid, pointer duplicates, non-pilot without
   OpenSpec. Done when those tests pass.

5. **`status`.** Never check out another branch. Current checkout + marked
   pilot: targeted OpenSpec CLI for that id only; strip `nextSteps`. Other live
   refs: `git show <ref>:openspec/changes/<id>/` and `work/<id>/`. Stage:
   meaningful OpenSpec `design.md` or `tasks.md` counts as `planned`.
   `code-without-plan`: `openspec/` for that work-id is a recognized prefix.
   Direct openspec-archive without Accept SHA is a warning or fail per spec
   (detect; do not invoke CLI on a foreign worktree). Tests extend
   `_ask/tests/test-status.sh`. Done when a pointer-only kit `plan.md` plus
   OpenSpec tasks is `planned` and `openspec/` labor is not `code-without-plan`.

6. **`verify`.** `./ask verify --work-id <id>`: refuse dirty tree (same class as
   `record-run.sh`), write `work/<id>/verification.json` from
   `_ask/templates/verification.json`, record HEAD SHA, run configured project
   checks. Marked pilot also runs targeted strict validation. Keep
   `VERIFY_JSON` / `verification-result.json` for non-`--work-id` invocation so
   existing callers do not break. Help, `ask-complete.sh`, `_ask/tests/test-ask.sh`.
   Leave `specs/current/promote-kit-specs.md` schema drift unfixed. Done when
   dirty refuse and work-id evidence-path tests pass.

7. **openspec-archive.** New `./ask openspec-archive <work-id>` →
   `_ask/scripts/openspec-archive.sh`. Refuse unless `acceptance.md` contains an
   accepted commit SHA; then run pinned `openspec archive`. Detect out-of-order
   direct archive in `check-workstream` / `verify` / `status`. Help + completion.
   Done when refuse-without-SHA and detect-direct-archive tests pass.

8. **Ownership and contracts.** `_ask/OWNED-PATHS.md`: `openspec/` consumer-owned
   (same class as `specs/` and `work/`). ADR-0018: OpenSpec 1.13.0 dependency +
   top-level `openspec/` against ADR-0011. Update `ask` help, Build Spec
   `04-scripts-and-git.md` command map and §23.3 / §23.4 / §24, stage contracts
   `02-spec.md` / `05-plan.md` / `09-verify.md` / `10-accept.md` for the
   lifecycle mapping. `install-kit.sh` does not init OpenSpec and does not
   require Node. Existing install tests still pass.

Commit after each numbered step on `agent/openspec-governance-integration`.

## Escalation (human approval before 06)

Risk HIGH. Spec constraint: rewriting `check-workstream`, `status`, or `verify`
is an escalation point. Approve all four before Implement:

- Pin `@fission-ai/openspec@1.13.0` (not 1.12.0).
- Rewrite `check-workstream` for marked pilots as in step 4.
- Rewrite `status` stage, `code-without-plan`, and checkout-scoped CLI as in
  step 5.
- Rewrite `verify` (`--work-id`, dirty refuse, `work/<id>/verification.json`)
  and add `./ask openspec-archive`.

## Spec-change triggers

Stop and run 04 if 1.13.0 re-measure shows: init can no longer be structure-only
without generating commands/skills; targeted JSON fields named in the spec are
absent or renamed; archive path is not `openspec/changes/archive/<date>-<id>/`;
`openspec config` is no longer global-only in a way that breaks the pin file's
schema/profile fields.

## Risks

- Gate rewrite bugs fail non-pilot workstreams or `test-workstream-smoke.sh`.
- Cutover after helper-but-before-gates leaves a dual-spec window; keep CURRENT
  complete until the cutover commit, and do not enable pilot gates before that
  commit.
- Agents follow CLI `@latest` advice. Helper and ADR must fail closed instead.
- `live` `kit-talk-ai-team` is unrelated; do not touch it.

## Verification approach

`_ask/tests/test-workstream-smoke.sh`, `test-check-workstream-guidance.sh`,
`test-status.sh`, `test-ask.sh`, `test-install-kit-apply.sh`,
`test-install-kit-dry-run.sh`, plus new helper/gate/archive tests. Stub
`OPENSPEC_BIN` for unit tests. After machinery lands, `./ask verify --work-id
openspec-governance-integration` on a clean tree.

## Out of scope for this plan

- Two-or-three-change adopt / revise / abandon evaluation (parked later card).
- Custom OpenSpec schema.
- Migrating historical `specs/` other than this work-id's copy at cutover.
- Fixing `promote-kit-specs` verification schema drift.
- Requiring Node/OpenSpec in `install-kit.sh`.
- Promoting `/opsx-*` or generating OpenSpec commands/skills.
- Checking out another branch from `status`.
- Touching `agent/kit-talk-ai-team`.
- Naming the later evaluation's representative changes.
