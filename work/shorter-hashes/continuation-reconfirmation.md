# Bug: redundant complete-intent reconfirmation on continuation

## Symptom

After the user explicitly extended this workstream from Plan to final
acceptance, the agent rewrote `intent.md` to record the endpoint. That changed
the file digest, so `./ask check-workstream shorter-hashes` requested a new
complete-intent approval even though the user's direction and the prior intent
approval were already recorded.

## Cause

The intent validator correctly binds approval to exact intent bytes. The agent
put an execution-endpoint decision in the intent instead of recording it as a
scoped continuation authorization. The workflow guidance did not explain how an
explicit later direction supersedes an earlier stop while preserving the
approved intent.

## Fix

Restore the exact approved intent, record the user's endpoint direction in
`continuation-authorization.md` and `plan.md`, and update the workflow and
Implement-stage instructions to keep `intent.md` unchanged for execution-only
continuations. Genuine What, Why, or assumption changes still require a new
complete-intent decision.

## Reproduction and verification

The red command was `./ask check-workstream shorter-hashes`; before the fix it
reported `intent changed after confirmation`. After restoring the exact
approved intent, `./ask confirm-intent validate --work-id shorter-hashes` and
`./ask check-workstream shorter-hashes` must both pass.
