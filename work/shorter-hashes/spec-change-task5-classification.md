# Specification Change Proposal

## Current specification

The accepted workstream spec and all acceptance criteria remain unchanged. The
accepted test plan classifies cases `5/1`, `5/2`, and `5/3` as `new`. On Task 5's
base revision `d5b8b002796830e33115dac394ad071d08165e9e`, cases `5/1` and `5/2`
already pass; only `5/3` demonstrates a behavior failure before its fix.

## Proposed change

Keep the spec and every test scenario, assertion, source binding, and task scope
unchanged. Reclassify only `5/1` and `5/2` in `work/shorter-hashes/test-plan.json`
from `new` to `regression`. Keep `5/3` as `new`.

## Why the change is needed

The current classifications claim that `5/1` and `5/2` introduce behavior that
was absent at the task base. The recorded Red run at
`2969973555adf490f6ea690a91d674c0f52460f4` shows both mapped cases passing
there, while `5/3` fails with a behavior assertion. The integration gate
correctly rejects the missing Red evidence for the two baseline-existing cases.
Calling them regressions matches their observed behavior and preserves the
existing acceptance criteria.

## Impacted artifacts

- `work/shorter-hashes/test-plan.json`: two `change_kind` values change.
- `work/shorter-hashes/traceability/plan-review.json`: independent review must
  approve the revised exact plan digest.
- `work/shorter-hashes/traceability-accepted.json` and its coordinator ref:
  issue a new accepted pin after that review.
- Task 5 execution, semantic-review, and completion evidence: rerun under the
  new accepted plan. Cases `5/1` and `5/2` still require current Green evidence;
  `5/3` still requires recognized Red and current Green.
- Final workstream verification and acceptance evidence: rerun under the new
  accepted plan.

Tasks 1–4 remain valid historical integrations at their recorded candidates;
they do not require reintegration. The canonical spec and TaskGraph do not
change.

## Impacted workstreams

`shorter-hashes` only.

## Migration / transition notes

The current accepted plan pin remains authoritative unless this proposal is
approved and independently reviewed. No new task candidate should be integrated
against the revised classifications before the new pin is recorded. Preserve
the current Task 5 candidate and its existing evidence as history; collect fresh
Task 5 evidence after the revised plan is accepted.

## Acceptance criteria for the change

- The spec digest, criteria, scenarios, expected assertions, source paths,
  runner bindings, task scopes, and TaskGraph are byte-for-byte semantically
  unchanged.
- Only cases `5/1` and `5/2` change from `new` to `regression`.
- An independent reviewer approves the exact revised plan digest.
- The coordinator records a new accepted pin for that reviewed plan.
- Fresh Task 5 completion passes with valid Green evidence for all three cases,
  and Red plus Green evidence for `5/3`.
- Final workstream verification passes under the new accepted pin.

## Decision

**Approved by the user on 2026-10-21** with the submitted response “approved”.
The user also directed completion through final acceptance with “go till and all
accepted”. The proposal's impact steps are now authorized, subject to independent
review of the revised test plan and a new coordinator accepted-tests pin.
