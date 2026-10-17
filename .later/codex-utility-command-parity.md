# Expose Later and session-only off-path commands in the Codex bundle

- **Status:** parked (not live; no new workstream started)
- **Found during:** `revising-workbench` side conversation, 2026-10-16
- **Tracker:** pending; GitHub was unreachable during this session
- **Start later:** new session, `./ask start-work codex-utility-command-parity`
- **First stage:** 00 Explore; locate the existing Later command and establish the Codex projection gap before proposing changes

## Why

The human reports that a command for creating Ask Later cards has already been
built, and Cursor already exposes a command to disable the Ask workflow for the
current session. They cannot find these capabilities in the Codex bundle. When
asked to park work, Codex repeatedly reconstructs card creation and Git publication
instead of invoking the existing command.

Cursor's session command is present as `.cursor/commands/off-path.md`, sourced
from `_ask/cursor-commands/off-path.md`. In this session, neither the active
checkout's `./ask --help` nor the inspected `develop` dispatcher exposed a Later
creation command. This establishes a discovery or availability gap in the inspected
copies, not that the reported implementation does not exist elsewhere.

Users need the same utility capabilities to be discoverable and usable from
Codex, with one canonical implementation and consistent behavior across runtimes.

## Proposed What (unapproved)

- Locate the existing Later-card command, including its authoritative branch,
  installation, or runtime binding. Determine whether the gap comes from an
  unsynced bundle, missing packaging, absent command registration, or agent
  instructions that fail to route to it. Reuse that implementation; do not build
  a second command based solely on its absence from this checkout.
- Make Later-card creation discoverable and invocable in the Codex bundle through
  the runtime's supported mechanism. The agent must discover and invoke the
  canonical command when the human asks to add to the Later inbox, rather than
  manually reconstructing template, tracker, worktree, and Git operations.
- Keep creation, duplicate handling, tracker mirroring, integration-branch
  publication, and failure reporting owned by the existing Later command. Confirm
  its actual contract and preserve current work and unrelated uncommitted files.
  Report missing command availability directly instead of repeatedly improvising.
- Expose the existing session-only `/off-path` behavior to Codex. The human called
  it off-plan mode; confirm naming and aliases against the existing contract.
  Explicit invocation disables the normal Ask stage workflow for that chat only,
  while preserving the existing safety rules. Do not create a persistent repo
  flag, alter intent to encode the mode, or carry the opt-out into new sessions.
- Treat this request as parking a follow-up, not as an invocation of off-path mode.
- Maintain the canonical source and generate or reference runtime projections
  through the kit's existing packaging/sync process. Include utility commands in
  the runtime capability inventory so a bundle containing only stage agents or
  stage skills is not mistaken for complete command coverage.
- Document the exact Codex invocation and ensure entry instructions route common
  user requests to the installed utility. Account for runtime differences without
  inventing unsupported slash-command behavior or maintaining duplicate rules.

## Validation direction

- A fresh Codex bundle exposes both utilities with usable invocation instructions.
- A natural-language Later request invokes the canonical command and produces one
  durable card on the integration branch without starting a new workstream.
- Repeating the request follows the command's duplicate/update contract; it does
  not create duplicate cards or tracker issues.
- From an active work branch with unrelated uncommitted files, the command
  preserves that work and reports publication or tracker failures accurately.
- Explicit off-path invocation changes only the current chat's workflow mode;
  a new session starts on-path. Merely discussing the command does not activate it.
- Sync/install/upgrade preserve both utilities in supported runtime bundles, and
  agent instructions do not direct Codex back to handwritten publication steps.

## Note

The human requested this follow-up after observing repeated manual Git operations
for Later requests and missing utilities in the Codex bundle. This parks discovery
and parity work; it does not authorize implementing or changing runtime commands.

Related cards: `later-inbox-script`, `later-inbox-develop-routing`, and
`later-inbox-tracker-sync`. Reconcile their status with the reported existing
implementation rather than treating old parked proposals as proof it is absent.
