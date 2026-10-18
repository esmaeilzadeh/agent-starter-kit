# Specification: Verify candidate source stability

## Status

CURRENT

## Goal

Show that candidate verification preserves committed source while checking runtime agent synchronization, and reconcile the parked inbox card with evidence.

## Non-goals

- Weakening or removing candidate source-stability checks.
- Changing runtime model defaults or generated projection behavior.
- Repairing unrelated skill installer or Engineering Model intake issues.
- Merging or pushing without human direction.

## Behavior

The runtime-agent synchronization check must restore every generated runtime-agent projection to its original bytes after both successful execution and a forced post-sync failure. The candidate Git worktree must remain clean. If full CheckPlan verification reveals another source mutation, its cause must be fixed within this scope before the inbox item is closed.

## Interfaces

Existing test seam: `EntrypointTests.test_I09_runtime_agent_sync_preserves_candidate_tree`. Verification entrypoint: `./ask verify`. No public interface changes.

## Constraints

Preserve candidate immutability and the existing source-stability guard. Historical reproduction runs only in a disposable checkout.

## Invariants

- A successful test leaves candidate source unchanged.
- A failing test leaves candidate source unchanged.
- Real candidate mutations remain a verification failure.

## Failure cases

- Any modified or untracked candidate path after either sync path is a failure.
- Any nonzero required CheckPlan check is a failure.

## Acceptance criteria

- `STAB-001`: on the historical candidate, the original regression reproduces the four modified Codex files; on the current candidate, the normal and forced-failure paths restore exact projections and leave a clean worktree.
- Full `./ask verify` passes on the final committed candidate and its isolated checkout is clean.
- The later card is removed only after evidence is committed.

## Open questions

None.

## Source intent

`work/verify-candidate-source-stability/intent.md`

## E2E

Applicability: applies

Journey: run the existing cleanup regression against a disposable committed candidate, including its forced exit-97 path; inspect exact projection bytes and Git status before the checkout is cleaned up. The full CheckPlan then verifies the committed candidate in isolation. Historical candidate f761709 supplies the reproduction; the current candidate supplies the green comparison.
