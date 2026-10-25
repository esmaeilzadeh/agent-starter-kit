# Enforce continuation and mid-work intake routing before starting new work

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `continuation-recovery`, 2026-10-25
- **Start later:** new session, `./ask start-work mid-work-intake-routing`
- **First stage:** 01 Grill (the failure is clear; enforcement details need review)
- **Tags:** workflow, continuation, intake
- **Attribution:** user-reported workflow failure in this session
- **Affected responsibilities:** continuation recovery, request routing, Later publication, workstream creation
- **Publication status:** published to `develop`; parked

## Why

While resuming the explicitly named `continuation-recovery` workstream, the
agent treated a discovered access-check requirement as an immediately authorized
new feature. It entered Explore and created `agent/start-work-access-preflight`
from `develop` instead of first resuming the named handoff, parking the discovery,
or asking whether to sequence separate work. The repository instructions already
required continuation recovery before task intake and said to park mid-work
discoveries, but the agent applied the feature route first. No workflow guard
prevented `start-work` from creating a second branch while another workstream was
active.

## Proposed What (unapproved)

- Make continuation recovery the first intake step whenever a session resumes
  work or the user adds a request during an active workstream.
- When the request is a mid-work discovery, prepare a `.later/<slug>.md` card
  from the template and keep working on the authorized workstream. Do not create
  a second `agent/*` branch unless the user explicitly sequences it.
- For an explicitly urgent interrupt, require the user to select the new
  workstream's base (`current branch`, `develop`, or `main`) before creating an
  isolated branch; preserve the interrupted workstream and its authorized stop.
- Add workflow or CLI checks that refuse to enter Explore/Grill or run
  `start-work` for a second workstream until continuation and sequencing have
  been resolved.
- Add end-to-end cases for: a named handoff plus a newly discovered request;
  a mid-work discovery that is parked; an explicitly sequenced interrupt with
  each base choice; and an ordinary new task when no workstream is active.

## Note

This concerns whether new work may start during continuation. Related parked
work, [continue-current-branch-priority](continue-current-branch-priority.md),
covers choosing the checked-out workstream when the user says “continue.” Keep
the scopes linked and avoid duplicating that card's branch-selection behavior.
