# Specification: later-inbox

## Status

CURRENT

## Goal

Agents can add a parked later-task during a running workstream without a new live `agent/*` and without committing the card on the active job’s branch.

## Non-goals

Status board for `.later/`. New `./ask` subcommand. Issue-tracker sync.

## Behavior

- Cards live under `.later/<slug>.md` (gitignored).
- `.later/README.md` is committed and explains: not live; start later with `./ask start-work`; copy `_ask/templates/later-work.md`.
- Mid-work: write a card, stay on the current job. Do not `start-work` the new id in the same session unless the human explicitly sequences another job.
- `./ask status` unchanged (live = unmerged `agent/*` only).

## Acceptance criteria

- `.gitignore` ignores `.later/*` except `README.md`.
- Template `_ask/templates/later-work.md` exists.
- `AGENTS.md` and `work/README.md` tell agents to park here.
- `./ask verify` passes.

## Source intent

`work/later-inbox/intent.md`
