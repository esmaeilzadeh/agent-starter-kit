# Route routine source and evidence inspection through internal helpers

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `continuation-recovery` (2026-10-24)
- **Start later:** new session, `./ask start-work ask-shell-source-evidence-inspection`
- **First stage:** 01 Grill (the repeated session probes and desired output are already clear)
- **Tags:** shell, agent-efficiency, evidence
- **Attribution:** user request in the `continuation-recovery` session
- **Affected responsibilities:** session continuation, source discovery, workstream and task evidence inspection, later-inbox entry
- **Publication status:** draft

## Why

Across sessions, the agent repeatedly launches many low-level shell commands to
inspect branch/workstream state, source files, task evidence, logs, and review
artifacts. The repeated `sed`, `rg`, `cat`, and status calls create noisy
transcripts and consume context tokens, including when the agent is only
creating a later-inbox card. These routine probes should be implemented as
dedicated helper scripts for agent workflows. Exposing them as public `./ask`
commands would add human-facing commands for operations that are not meaningful
to human users.

## Proposed What (unapproved)

- Inventory recurring read-only inspection sequences used during continuation,
  source exploration, verification, and evidence review.
- Add dedicated internal helper scripts that gather those facts and return
  compact, purpose-built summaries with paths and identities needed for the next
  action. Keep them out of the public `./ask` command list.
- Keep shell composition and file parsing inside these helpers; agents should
  invoke one relevant helper instead of issuing a series of raw probing commands
  for routine kit workflows.
- Include agent-internal support for creating later-inbox cards so the agent
  does not need a long sequence of shell probes and file-writing commands even
  when recording this kind of follow-up. Coordinate with
  `.later/later-inbox-script.md` and avoid adding a human-facing command for an
  agent-only operation.
- Preserve detailed evidence on disk and expose it on demand, while keeping the
  default output small enough to reduce transcript and token cost.

## Note

The later-inbox add/list work is separately parked in
`.later/later-inbox-script.md`; sequence or combine its implementation during
Grill, while keeping any new operation agent-internal unless a real human use
case supports a public command.
