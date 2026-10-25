# Specification: Project access preflight

## Status

CURRENT

## Goal

Detect unavailable local write access before project work begins or resumes.

## Non-goals

Remote auth/network access, permission repair, or changing clean-tree and
branch-base rules.

## Behavior

- `./ask access-check` makes and removes temporary write probes in the Git
  worktree metadata directory, shared Git metadata directory, and nearest
  existing workspace directory.
- A failed probe exits non-zero, identifies the blocked location, and gives a
  next step. It removes any probes it created.
- Project startup and resume instructions for Codex, Cursor, Claude, and
  OpenCode invoke the shared check; native lifecycle hooks invoke it where the
  runtime supports them. `start-work` runs it before checkout/branch creation.
- A failed check prevents work from proceeding.

## Interfaces

CLI: `./ask access-check`, no arguments. Output goes to stderr on failure.

## Constraints

Probe real writes rather than relying on permission bits. Handle linked
worktrees through Git-reported metadata paths.

## Invariants

Success leaves no probe files. Failure occurs before `start-work` changes
`HEAD`, creates a branch, or writes workstream artifacts.

## Failure cases

Git metadata or workspace probe cannot create, write, or clean up its temporary
file. Report the location and stop.

## Acceptance criteria

- ACC-001: Writable Git and workspace paths pass and leave no probe files.
- ACC-002: Denied Git metadata or workspace writes fail with a location and
  actionable message.
- ACC-003: `start-work` fails before branch or workstream mutation when a probe
  fails.
- ACC-004: Session start and resume run the same check for each supported
  bundle, using native lifecycle hooks where available and portable project
  instructions otherwise.

## Open questions

None.

## Source intent

`work/start-work-access-preflight/intent.md`

## E2E

Applicability: `applies`

If `applies`: run the public CLI in isolated temporary Git repositories with
writable and denied probe paths; verify failure leaves branch/workstream state
unchanged; inspect and exercise startup/resume wiring for each supported bundle.
