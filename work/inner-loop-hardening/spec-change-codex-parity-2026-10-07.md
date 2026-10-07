# Specification Change Proposal: Codex stage skill parity

## Current specification

`specs/current/inner-loop-hardening.md` is CURRENT. It defines Codex agent
projections under `.codex/agents/` and treats all `.agents/skills/` as ignored
prepared Community Skills. Preserve that specification until this proposal
is approved. Starting HEAD: `9602217d6e0f7d63dc9251ba8bd1673eb7d8f694`.

## Proposed change

Extend `./ask sync` to generate eleven repository-local Codex skills,
`kit-00-explore` through `kit-10-accept`, under `.agents/skills/`. Each has
valid, concise name/description metadata and the same canonical stage body
and selected local overlay as its Cursor counterpart. Keep generated Codex
stage agents under `.codex/agents/`.

Reserve direct child names `kit-*` for ASK-generated skills. Check those
projections into Git. Other child directories remain Community Skills or
consumer-owned skills; sync leaves their contents untouched. Preparation must
reject a Community Skill destination in the reserved namespace before writing.

Use selective ignore rules: ignore `.agents/skills/*` and allow `kit-*/` and
its generated contents. Install and upgrade replace the kit's legacy blanket
ignore rule with these selective rules while preserving unrelated ignore
rules. Check trackability with Git rather than assuming a generated file is
visible.

Sync removes stale ASK-generated skill directories only when their generated
marker identifies kit ownership. An unmarked reserved directory or symlink
collision causes a clear failure before overwrite or deletion. The generator
owns only generated stage projections, not arbitrary consumer content.

## Why the change is needed

The handoff records the human decision to expose Codex-native stage skills.
Agent TOML projections alone do not supply the requested skill invocation
surface. Sharing canonical stage bodies keeps runtime behavior aligned.

## Impacted artifacts

After approval, update the canonical spec, plan and task graph; extend binding
generation, preparation namespace validation, install/upgrade ignore handling,
focused tests, generated projections and runtime invocation documentation.
Preserve the older accepted `spec-change.md`.

## Impacted workstreams

Continue only `agent/inner-loop-hardening`. No additional workstream or branch.
Existing outer workflow, verification and human Accept gates still apply.

## Migration / transition notes

Keep `.agents/ask/` as protocol source and `.agents/ask.local/` as overlay source.
Install/upgrade regenerate ASK projections rather than copying prepared skill
bodies. Preserve unrelated Community Skills and consumer configuration.
Detect reserved-name collisions explicitly; require relocation or an explicit
ownership decision rather than adopting existing content silently.

Alternative: place stages in another directory. Rejected because it would not
provide the repository-skill surface described by the handoff. Alternative:
track every prepared skill. Rejected because it changes dependency ownership
and vendors Community Skills. Alternative: maintain separate Codex stage
bodies. Rejected because it introduces a second protocol source.

## Acceptance criteria for the change

1. Sync emits all eleven Codex skills with valid unique metadata; Cursor and
   Codex use identical canonical stage and overlay bodies.
2. Repeated sync is deterministic. Tests cover all stages, overlay selection,
   stale generated cleanup, unmarked collisions and symlink protection.
3. Git tracks generated ASK stage skills while unrelated prepared skills stay
   ignored. Tests exercise both this repo and installed/upgraded consumers.
4. Preparation rejects reserved Community Skill names. Sync, install and
   upgrade preserve unrelated skill contents and consumer-owned configuration.
5. Existing Codex agent projections retain required custom-agent fields.
6. Docs describe Codex `$kit-*` invocation and Cursor stage commands. Verify
   current official product documentation before implementing metadata or
   promising UI discovery; live invocation remains a documented manual check.
7. Capture failing then passing parity tests, commit meaningful steps, run
   required Review/Refactor/Verify, record result against a commit SHA, and
   request human Accept. Existing acceptance criteria remain in force.

E2E remains `not_applicable`: isolated kit shell integration tests cover these
CLI flows; this change introduces no product application journey.

## Decision

APPROVED by the human in chat on 2026-10-07 ("yes"). Authorizes the ownership
convention, acceptance criteria, spec/plan updates and implementation.
