# Specification Challenge

## Model

- model: inherited GPT-6 Codex; exact backend revision is not exposed to this child agent.
- runtime: Codex agent tools, independent child-agent context.
- parent_model: GPT-6 Codex (parent-provided provenance).
- Limitation: the configured generated-role model, gpt-5.4, was unavailable on this account. The parent requested this independent-context fallback under the user's instruction to proceed without further permission questions. This provides a separate review context, not a different model family. No picker confirmation or second same-family confirmation was obtained.

## Specification

Reviewed `specs/current/harness-review.md`, workstream Intent, Plan, Explore Map and reliability handoff against current `inner_loop/state.py`, `driver.py`, `integrate.py`, the canonical verification runner/plan/isolation modules and delegation/worktree policies. Applied the prepared writing-for-agents skill in embedded mode. The checkout passed `./ask check-clean` before writing this artifact.

R1/R2 address the stated Why. Current integration trusts reported result fields, and current state writes lack process serialization and atomic replacement. The specification supplies a bounded replacement: coordinator-run candidate verification, attributable review records, local advisory locks and complete state-file replacement. It does not claim protection from hostile repository writers or multi-host coordination.

## Ambiguities

The following details can be resolved within the accepted scope; they do not require a new human product decision.

1. CheckPlan identity includes more than `.agents/verification.yaml`: `expand_plan()` reads preset files and expands executable globs. Bind the effective ordered checks and relevant plan/preset inputs, so evidence identifies the commands actually executed.
2. Runtime-path exceptions need a precise allowlist. Limit them to this workstream's state, results and execution/review evidence. A broad exclusion of `work/` would hide changes to committed intent, graph or review inputs.
3. Coordinator review is protocol attribution in a cooperative process model. A record containing a reviewer string is not an authentication mechanism. Keep the implementation/docs consistent with this boundary.

## Missing failure cases

These are concrete implementation tests of existing requirements, rather than proposed acceptance-criteria changes.

| Counterexample | Required handling |
| --- | --- |
| The candidate passes, but its check rewrites the TaskResult or review artifact in the coordinator checkout. | Recheck the bound bytes after execution and before Git/state advancement; reject changed inputs. |
| Detached verification runs the existing runner with its default output path, creating `verification-result.json` inside the candidate worktree. | Put runner output outside the candidate worktree. Preserve the clean-worktree check instead of exempting arbitrary generated source. |
| The candidate check changes a tracked file, creates an untracked source file, or changes detached HEAD. | Reject verification even if every check reports zero. |
| Git FF succeeds, the process dies before the fold, and only runtime files are dirty on resume. Current `git_resume()` treats any dirt as a reason to hard-reset to the old state SHA. | Resume under the lock, distinguish runtime changes from source changes, recognize the exact candidate and revalidate it before folding. Preserve the FF candidate rather than applying the old unconditional reset path. |
| A second process cancels while verification is running. | Cancellation waits for the integration transaction; it cannot mark the same task cancelled between validation and fold. Check both serial orderings. |
| Two initializers supply different task lists while one already persisted valid state. | Return the stored document without resetting revision, tasks or coordinator SHA. |
| A malformed result supplies `true`, a numeric string or a missing value as an exit code. | Enforce actual integer exit codes, excluding booleans; return a useful refusal rather than treating coercion as evidence. |
| Verification has a successful top-level status but missing, duplicate or malformed check entries. | Validate the execution record against expected check identities/results and mandatory-check presence. |

## Over-constraint risks

Holding the state lock through verification can delay cancellation and other callers. This is explicitly accepted by the Plan; do not add timeouts that release the transaction before its fold. Atomic rename and file fsync provide the specified file visibility guarantee, without promising a cross-resource transaction or universal power-loss durability.

The clean candidate requirement can expose checks that modify the checkout. Evidence belongs outside that checkout; changing the cleanliness requirement to accommodate a fixture would weaken the specification.

## Under-constraint risks

An advisory lock works only if every state mutation and relevant resume path uses the same persistent lock inode. Replacing or unlinking the lock file can split mutual exclusion. Invariant validation must inspect the mutated document while locked, including public `cas_apply()` callers, rather than only `spawn_writer()` preflight.

Checks must run through coordinator-owned runner code and imports. Executing the runner from the candidate, or importing its verification modules through a candidate-controlled path, would recreate reliance on candidate-reported evidence. This requirement still allows project test commands and the committed CheckPlan to come from the candidate under the documented cooperative execution boundary.

Keep Git changes pinned to the resolved candidate SHA. A branch ref that moves while checks run must not cause a different commit to integrate. Check coordinator HEAD/tree again before the fold, and reject non-FF/ref/source drift with an actionable reason.

## Recommended clarifications

Carry the cases above into the R2/R1 public-operation tests. Prefer externally visible assertions: exactly one successful same-revision update, at most one running task, complete JSON for readers, no integrated state on verification failure, and exact candidate lineage after recovery. Use real subprocesses and synchronization to force overlap; sequential stale-revision tests do not demonstrate serialization.

Keep old v1 results archived and reject them on future integration. Update canonical TaskResult/review instructions and affected fixtures with the v2 migration so runtime agents can produce the required identity and request coordinator review.

## Challenge verdict

PASS — the specification is internally consistent and supports implementation within R1/R2. No unresolved What/Why choice or new human decision was identified. The implementation concerns above are applications of its existing identity, verification, locking and recovery requirements. This verdict is source/spec review, not executed evidence of a fix. The model fallback limitation remains recorded above.
