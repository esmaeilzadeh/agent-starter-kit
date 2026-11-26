# Client workflow startup hooks

## Status

CURRENT

## Goal

Load the AskIt workflow automatically in installed local Cursor and Codex sessions. Preserve the client's ownership of repository instructions.

## Acceptance criteria

- **CWH-001.** A fresh install registers both session hooks without creating root `AGENTS.md`. Hook output loads the same AskIt workflow on successful access preflight and surfaces a stop instruction with the blocked path on failure.
- **CWH-002.** First and repeated installs preserve the client's `AGENTS.md` and unrelated hook entries. Each editor gets one AskIt entry. Unreadable or unsupported hook configuration fails safely within the installation transaction.
- **CWH-003.** The documented upgrade from the preceding release registers both hooks and preserves existing client instructions and unrelated hooks.

## Constraints

Keep the workflow in kit-owned files. Cursor retains the kit rule for sessions where startup context is unavailable. Codex uses its runtime hook trust. The install does not remove legacy root instructions. Repository Git and CI admission and other editors are out of scope.

## E2E

Use disposable Git repositories to exercise fresh install, repeated install, and migration. Read the installed runtime configs and execute the registered commands against successful and failed access preflights. Use editor smoke checks where available. Dispose of fixture repositories afterward.

## Source intent

[Approved intent](../../work/client-workflow-hooks/intent.md).
