# Specification change proposal: keep generated Codex skills out of client Git

## Current specification

`specs/current/client-security-hardening.md` and its JSON criterion registry at `853f37d`. CSH-002 protects client settings and CSH-007 validates generated agent configuration. Neither defines whether generated Codex skills appear in client Git.

## Proposed change

Add CSH-009 for client installs and upgrades. Ignore AskIt-generated `.agents/skills/kit-*/` projections in client repositories. Continue to generate, refresh, and discover those skills locally. Keep the kit repository's own projection tracking policy separate. Preserve client ignore rules and keep `.agents/ask.local/` trackable.

## Why

The installer and upgrader currently maintain a negated ignore rule and require the projections to be trackable. Clients can therefore stage stock generated skills with an ordinary Git add. Generated skills can be recreated with `ask sync`.

## Migration

Remove known AskIt managed exceptions in clients without removing unrelated ignore rules. Preflight the effective ignore rules and report a clear conflict if a client rule keeps a generated skill visible. If an existing client already tracks generated files, report the affected paths and document how to remove them from the index while retaining local files. Install and upgrade never edit the client's index or delete tracked skills as part of this migration.

## Acceptance criteria

- Fresh client: install produces discoverable Codex stages. Git ignores the generated kit skills and accepts project settings under `.agents/ask.local/`.
- Existing client: reinstall and upgrade migrate the old kit exception, preserve unrelated ignore entries, and remain idempotent. Sync still regenerates the skills.
- Existing tracked skills: the migration explains which paths still need untracking and leaves the index unchanged.
- Kit development: the source repository can continue tracking its generated stage projections.

## Impact and decision

Update the security spec and its criterion registry, engineering model, and task plan after approval. Sequence this task with installer ownership changes. The separate upgrade preservation repair remains focused on preserving client-owned Cursor files.

Status: Proposed. The current intent and specification remain the basis for the pending Spec Challenge. Stage 04 will present this proposal with the complete revised intent in one choice.
