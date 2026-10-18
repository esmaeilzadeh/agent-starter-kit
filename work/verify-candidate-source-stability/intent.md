# Intent: Verify candidate source stability

## What

Reproduce the historical candidate mutation, validate the cleanup fixes already present on develop, and reconcile `.later/verify-candidate-source-stability.md` with durable evidence. If verification exposes a remaining source mutation, fix its cause and add or extend a regression at the real check/verification boundary.

## Why

A passing static suite must not mutate its candidate checkout or be reported as successful when the source-stability guard rejects it. The later card predates cleanup fixes already in current source.

## Non-goals

- Change candidate immutability, weaken the source-stability guard, skip mandatory checks, or change model/effort policy.
- Repair unrelated installer or Engineering Model intake issues.
- Merge or push this branch.

## Known assumptions

- Use develop as the baseline and agent/verify-candidate-source-stability as the sole work branch.
- Preserve the existing runtime projection restoration fixes if they satisfy the requirement; a second code fix is unnecessary when tests already prove the behavior.
- Verification must cover successful and failed checks, exact projection restoration, clean candidate source, and the full CheckPlan.
- Historical reproduction belongs in an isolated checkout; never modify historical commits.
- Only close/remove the later card after recording sufficient evidence, and retain the history and root cause in workstream artifacts.
- Risk is LOW: local test cleanup and evidence, reversible commits, no external changes.

## Open questions

None about What/Why. Remaining technical validation is recorded in explore-map.md.

## Human decisions

Requested initialization and repair: "init and fix that". Access restoration: "access granted". These authorize initialization and investigation; complete-intent confirmation is pending.

## E2E

Applicability: applies

Journey: run the existing sync cleanup regression against a disposable committed candidate, including a deliberate exit-97 failure; verify exact projection bytes and clean Git status afterward. Run the full CheckPlan in an isolated checkout, inspect source status before cleanup, retain logs/results, and keep the source-stability rejection for real mutations. Existing historical candidate f761709 supplies the red reproduction; current committed source supplies the green comparison. Temporary checkouts are removed after evidence capture.
