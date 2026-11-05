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
  next step. It attempts cleanup and reports the exact path if cleanup fails.
- A successful check leaves no probe files.
- Project startup and resume instructions for Codex, Cursor, and OpenCode
  invoke the shared check; Cursor's session-start hook invokes it as well.
  `start-work` runs it before checkout/branch creation.
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

Git metadata or workspace probe cannot create or write its temporary file.
Report the location and stop. If cleanup fails, report the leftover path.

## Acceptance criteria

- ACC-001: Writable Git and workspace paths pass and leave no probe files.
- ACC-002: Denied Git metadata or workspace writes fail with a location and
  actionable message; cleanup failures report leftover paths.
- ACC-003: `start-work` fails before branch or workstream mutation when a probe
  fails.
- ACC-004: Tests verify Cursor's session-start hook runs the check and surfaces
  failure as a stop condition before project work.
- ACC-005: Project instructions require the check at session start and resume
  for supported runtimes, including those without a usable lifecycle hook.

## Open questions

None.

## Source intent

`work/start-work-access-preflight/intent.md`

## E2E

Applicability: `applies`

If `applies`: run the public CLI in isolated temporary Git repositories with
writable and denied probe paths; verify failure leaves branch/workstream state
unchanged; inspect and exercise startup/resume wiring for each supported bundle.
