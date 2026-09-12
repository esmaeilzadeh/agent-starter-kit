# Review

## Scope

`specs/current/skip-explore.md` vs AGENTS, workflow, 00/01 contracts, start-work, tests.

## Findings

- Gate text matches spec routing table.
- start-work no longer seeds explore-map; smoke creates the map as 00 would.
- Guidance test now reaches the missing-spec path (clean temp repo).

## Suggested fixes

None required for this slice.

## Residual risks

- Agents may still write a stub map out of habit. The texts now forbid it.
- Accept and merge to main are still human.

## Review verdict

Pass. Ready for verify SHA `0be09a1` and human Accept.
