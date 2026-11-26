# Bug fix: frozen dogfood checkout disappeared

## Reproduction

At continuation, the recorded frozen checkout `/tmp/askit-dogfood.0BXUZGWN` was absent. Recreating it at the exact recorded commit restored the required verifier. The `/tmp` location was the cause: it is temporary storage and did not survive the session boundary.

## Expected behavior

The pinned checkout has a stable, recorded location and can be recreated at the same commit from any clone with the Git object available.

## Change

Relocated the clean detached worktree from `/tmp` to `../ai-agent-start-kit-dogfood-0e303265`. Added `frozen-copy.md` with the exact SHA, path, and recreation command. The pin remains unchanged.

## Verification

- `git -C ../ai-agent-start-kit-dogfood-0e303265 rev-parse HEAD` returned `0e303265ceae1fbcdc9b2261bd922b003ab68924`.
- The worktree is clean and listed by `git worktree list` at the persistent sibling path.
- The old `/tmp/askit-dogfood.0BXUZGWN` registration was removed only after the new worktree was verified.
