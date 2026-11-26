# Client workflow hooks acceptance

## Decision and authority

Accepted through the highest-priority source self-development rule, with the
kit workflow disabled. The human requested “check and if you are certain >90
accept it”, then “fix them”. Confidence after correction and verification is
95% (subjective engineering judgment, not a measured probability).

Accepted implementation: `91ba897c472a70a79ee165d67561eaa0da88c8dd`.
Specification: `specs/current/client-workflow-hooks.md`, revision 1.
The approved `intent.md` is unchanged.

## Evidence

- All 41 CheckPlan checks pass at `996823277433505318b41b3fad9cf905055e6f52`,
  including the five hook journeys, five access checks, 48 recovery tests,
  43 reliability tests, and traceability cases.
- The only subsequent implementation delta repairs access-test cleanup in
  linked Git worktrees. All five access checks pass at the accepted SHA in
  primary and linked checkouts, leaving no probe files.
- Three transaction safety cases pass: unsafe paths, late conflicts preserving
  client files, and consumer ignore ownership.
- See `work/client-hooks-release-repair/verification.json`,
  `followup-verification.json`, and this workstream's `review.md`.

## Historical workflow limitation

The previous coordinator cache/checkpoint is missing. The rejected historical
completion remains rejected; no coordinator state, adoption, or passing formal
workflow receipt was fabricated. This decision accepts the current source under
the source self-development exception, using fresh checks and the human's
explicit delegation. The original accepted-tests ref remains preserved remotely.

## Residual risks

Installed hook commands were exercised in disposable repositories; interactive
Cursor and Codex startup was not smoke-tested. Codex project hook execution
still depends on runtime trust and the documented local prerequisites.
