# CR-3 narrow plan amendment proposal

Purpose: route the reviewed reconciliation lifecycle correction from
`CR-3-result-review-08339eb.md` through the accepted plan and ownership path.
This proposal does not edit `plan.md`, `tasks.yaml`, `test-plan.json`, or the
accepted contract. It is a concrete decision proposal, not accepted authority.

## Proposed task-graph change

Add `_ask/scripts/inner_loop/attempts.py` to the CR-3 `owned_paths` list. CR-2
remains its original owner; CR-3 is downstream and serialized after CR-2. The
addition permits the narrow lifecycle correction required to make a consumed
reconciliation receipt historical rather than a blocker for the next valid
reopen.

The implementation should bind each receipt to its transition identity and
keep receipts immutable. Use an attempt-specific receipt path (for example,
`reconciliation-CR-3-attempt-1-to-attempt-2.json`) and validate only the
receipt whose `previous_attempt_id` and `new_attempt_id` match the current
interrupted attempt and proposed reopen. On interrupt, preserve the current
receipt identity in that attempt's history; on the next reopen, record the
new receipt separately. A stale newly submitted receipt must fail identity
validation. This leaves earlier approved evidence intact and supports
interrupt → reopen → interrupt → reopen.

## Proposed CR-T13 clarification

Retain CR-T13's selector, criteria, type, and existing assertions. Clarify its
scenario and expected assertions to require:

- a valid reviewed-plan reopen after the first interrupted attempt;
- a second interrupt and reopen with a distinct attempt identity;
- preservation of each consumed reconciliation receipt as immutable history;
- refusal of a stale newly submitted reconciliation request.

This directly exercises the R2 regression sequence in the existing CR-T13
attempt-history outcome. Keep CR-T13 as `new`; the new repeated transition must
have a valid Red before its implementation. Preserve all previous run phases.

## Proposed case-specific TDD resolution

The provenance audit supports two exact classifications and one unresolved
exception:

- Change CR-T12 from `new` to `regression`. The immutable test-only candidate
  `3196a59` introduced its mapped assertion while leaving `_ask/scripts/inner_loop`
  unchanged from task base `2c508ff`; the registered Red-phase run
  `b50dd24e0ef04a2aacff4c4a26db4dd5` shows that assertion passed against that
  production. Keep run `6a96d09a0d4c4394951b47fa33a14dd7` recorded as a failed
  `final_green` run.
- Keep CR-T13 `new` and extend only its mapped assertion with the repeated
  interrupt/reopen sequence and stale-request refusal. Its older mapped
  assertions passed at the initial test-only candidate and do not supply Red
  for the newly exposed reconciliation lifecycle.
- Keep CR-T21 as `new`. Its implementation changes followed task base, but its
  assertion was added later by test-only commit `ae31e20`. The available
  Red-phase report `517f864631a845e082f9a73fa888ef30` passed all eight cases,
  so it does not establish Red. The proposed contract amendment is a narrow
  TDD exception for CR-T21 only: preserve the behavioral assertions and require
  current exact-candidate Green, independent semantic review, and this explicit
  provenance limitation; do not claim Red→Green for T21. Do not reclassify it
  as a regression.

This exception changes the TDD evidence obligation for one mapped case. It
does not alter CR-01–CR-08 behavior, remove CR-T21 assertions, or authorize
integration without fresh review and passing checks. Human acceptance is
required before the amended contract can be pinned. The remaining mapped cases
retain their existing TDD obligations, including the new CR-T13 sequence.

## Required path before implementation

The amended plan and graph must be reviewed against their exact canonical
digests, validated, and accepted through the normal `traceability accept-plan`
coordinator operation. The TDD exception for CR-T21 additionally requires the
human choice described above. Only after those gates may CR-3 be reopened with
the new accepted plan reference. Preserve both interrupted attempts and their
original plan-bound evidence.
