# Review

## Model

- model: inherited GPT-6 Codex; exact backend revision is not exposed.
- runtime: Codex independent child-agent context, `/root/spec_challenge_fallback`.
- parent_model / implementation model: GPT-6 Codex, parent-provided provenance.
- Fallback: the generated Review role's configured gpt-5.4-mini model was unavailable on this account. The user directed continuation without further permission/model-picker questions. This reviewer implemented none of the source. It previously challenged the specification, so this is independent of implementation, but shares the model family and prior specification-review context. No model-picker or second same-family confirmation was obtained.

## Scope

Reviewed `ed6fa62..a7944f0` against `specs/current/harness-review.md`, Intent, Plan, Explore Map, handoff and repository policies. Inspected the state/coordinator/evidence/CLI implementations, canonical and generated stage instructions, evidence documentation and reliability tests. Applied the prepared writing-for-agents skill in embedded mode. Initial tree at `a7944f0` was clean. Only this review and the context audit are reviewer-owned outputs; no source/spec changes or commits.

## Findings

### F1 — P1: source repair can erase tracked coordinator state and review history

Location: `_ask/scripts/inner_loop/driver.py:163` invokes `git_resume()`; `_ask/scripts/inner_loop/integrate.py:41` runs `git reset --hard coordinator_sha` without preserving runtime paths.

The new runtime-only dirty handling protects the FF-before-fold case when there is no other source dirt. When source is dirty or Git is in progress, repair still resets every tracked path. If state was committed after the stored coordinator SHA, reset removes it; `run_until()` then recreates state and starts the first task with a lower revision and no review. A tracked snapshot present at the stored SHA is instead restored to historical bytes. The state lock does not prevent this data loss because the Git operation itself rewrites the state file while holding that lock.

Executed reproduction through public operations, using the existing disposable `IntegrationTests` fixture:

1. Initialize/start task `a` with `run_until()` as in fixture setup.
2. Force-add `work/w/inner-loop/state.json` and commit a runtime snapshot; update the submitted v2 candidate SHA to that commit.
3. Record APPROVED review with `record_review()`; revision is 2 and review is present.
4. Modify tracked `src/value`, then call `resume_from_state()`.

Observed output:

```json
{
  "before_revision": 2,
  "before_review": true,
  "outcome": "aborted\nrunning=a",
  "after_revision": 1,
  "after_review": false,
  "head_is_candidate": false
}
```

This violates acceptance criterion 7: resume must preserve revisions and task invariants. Runtime paths are explicitly permitted to change; the contract does not require them to be ignored/untracked. The fixture's `.gitignore` masks this failure in existing resume coverage.

## Suggested fixes

F1: preserve state/results/evidence bytes and the persistent lock inode across source/Git repair, or use a repair operation limited to source paths. Restore state with the same atomic visibility guarantees and without exposing historical/removal state to unlocked readers. Keep the same lock held for the full operation. Add a public resume regression with tracked runtime state and an attributable review, and exercise an in-progress Git repair if that shares the destructive path. Do not narrow the accepted contract to ignored runtime paths merely to bypass this case.

## Residual risks

The coordinator executes project checks under delegated authority; review attribution and environment role flags are cooperative protocol controls. This review makes no security sandbox, multi-host or performance claims.

Five targeted tests executed and passed: successful in-place lineage, successful FF, result drift during checks, competing same-revision CAS, and complete-JSON readers. The tracked-state resume reproduction above failed its preservation expectation. The parent reports full `./ask verify` passing at `a7944f0` (35 mandatory shell checks, including 26 reliability unittest cases); this reviewer did not rerun the full suite. Preset/malformed-output validation and coordinator-owned runner imports were inspected, but additional direct runtime fault injection for those paths was not performed.

Other inspected mechanisms align with the spec: result/review hashes bind full identity, worker fields alone cannot authorize integration, checks run through coordinator-owned verification modules with external evidence output, result/review/ref/source are revalidated before pinned FF, and state mutations are locked and atomically replaced. These observations do not close F1.

## Review verdict

REJECTED — F1 requires correction and targeted rerun before approval. Context-engineering pointer audit is separately recorded in `work/harness-review/context-audit.md`; passing pointer checks do not establish runtime recovery correctness.
