# Intent: Check project write access before agent work

## What

Add a shared `./ask access-check` that probes local Git metadata and the
workspace with temporary writes. Run it at project session start and before
resuming work in supported runtime bundles, and before `start-work` changes
branches or writes workstream files. On failure, stop with an actionable
message and leave no probe artifacts.

## Why

Detect inaccessible project locations before an agent spends time on work it
cannot save.

## Non-goals

Remote authentication, network/push access, permission repair, or changing
existing clean-tree and branch-base rules.

## Known assumptions

- Supported bundle startup hooks call the shared CLI where available; portable
  project instructions require the check at session start and resume elsewhere.
- A real temporary write-and-cleanup probe is needed; `test -w` alone is not
  reliable in restricted environments.

## Open questions

None; runtime-specific hook wiring can follow existing bundle capabilities.

## Human decisions

Expanded from `start-work` preflight to session start and resume across
available bundles, as requested.

## E2E

Applicability: `applies`

If `applies`: exercise the public CLI in temporary Git repositories: writable
Git/workspace paths pass and leave no probes; denied Git or workspace writes
fail before branch/workstream mutation. Verify session-start/resume wiring for
each supported bundle.
