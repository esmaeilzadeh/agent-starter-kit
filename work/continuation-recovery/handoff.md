# Isolated continuation-recovery planning handoff

## User objective and endpoint

Apply every finding in the recovery plan re-review, seal the corrected plan and
stop. No implementation, behavior tests, runtime bootstrap or product scheduling.
The user then directed that urgent interrupt work use a separate branch and
fresh context, with a required choice of base: current work branch, develop or
main. They selected the recommended current branch with “rec”. Persist this
rule in AGENTS.md using writing-for-agents, preserving unrelated instructions.

## Isolation

New branch: `agent/continuation-recovery`, created directly from the selected
`agent/shorter-hashes` at `d04b3a4e515105df8cdf703f2fa0a28895f1524d`.
`agent/shorter-hashes` has not advanced. The carried uncommitted planning changes
are being checkpointed here for the fresh-context agent. They are unfinished
design artifacts, not an accepted contract or implementation.

## Inputs and carried revisions

Original proposal/review: `work/shorter-hashes/continuation-recovery/`.
Authoritative findings: `plan-review-reevaluation.md`, R1–R4. Revision-2 edits
already present there propose real Git retention edges, coordinator-only run
finalization, a reviewed CAS bootstrap and exact test source bindings. Existing
canonical shorter-hashes spec/test/graph were edited before the isolation rule
arrived; do not accept those changes into the original product workstream.
Re-home the fix into `work/continuation-recovery/`, use its own canonical spec,
test plan, TaskGraph and accepted-tests authority, and restore shorter-hashes
canonical files and planning artifacts to the branch-point bytes where they
were changed by this unfinished interrupt. Keep copied useful design content.

The separate branch removes the need to insert CR tasks into the original
product scheduler to start the repair. Still fully address R2: define normal
repair-workstream initialization, preserve the product's blocked legacy state,
and specify a later explicit reviewed product adoption/integration handoff. A
fresh repair context is not permission to infer old tasks completed. Reassess
the carried combined-bootstrap design against the now-separate workstream.

## Formal sealing

Use current standard ask-spec/v1, ask-test-plan/v1 and graph contracts; obtain
fresh independent exact-artifact approval before existing traceability accept-plan
registers only `continuation-recovery`. Record a plan seal with source commit,
digests, reviewer, user authorization and the explicit stop. Do not move the
accepted-tests authority of shorter-hashes or mutate its runtime state. Approved
product intent remains byte-identical. Do not claim runtime passes from planning.

## Existing observations

Original product state revision 11: Task1 integrated, Task2 blocked, Tasks3–10
pending. Its code/history for Tasks1–5 predates the restarted queue. A baseline
snapshot is in the carried `bootstrap-baseline.json`. Its observed accepted-tests
ref and tracked pin may differ; preserve these observations without asserting
historical approval validity. The original approved intent digest is
`8784f3748505fe0ac51ccb9a7dfe78de0c04f79cd26dac58689fdee10cb084e6`.

Existing skills are prepared/readable; pin validation using
`SKIP_INSTALL=1 ./ask prepare` and binding sync completed. Do not install unrelated
skills or run setup. All labor and stepwise commits now belong to this branch.
