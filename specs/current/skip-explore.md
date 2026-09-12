# Specification: real skip of 00 when destination is already clear

## Status

CURRENT

## Goal

Agents on the kit path decide whether **00 Explore** must run or is a **real skip**, announce that call, and route to 00 or 01 without pretending Explore ran when it did not.

## Non-goals

- Changing `01`–`10` “skip extra approvals, not documents.”
- A `./ask fog` command or new policy file.
- Skill-pin or later-inbox product (other work-ids).
- Off-path session behavior (already specified).

## Behavior

### Fog test

**Foggy** if any of: What/Why cannot be written without inventing; several plausible destinations; R&D / wayfinding required; the destination itself is in conflict.

**Clear** if the human already stated a concrete What/Why sufficient for Intent (bugfix, well-bounded add, demo Path A).

### Routing

| Entry | Behavior |
| --- | --- |
| `/00-explore` or explicit “00-explore” | Start 00 immediately. Do not ask whether Explore is needed. Create `work/<id>/explore-map.md` from the template if missing. |
| Free on-path new task | Agent announces foggy vs clear (short rationale). **Wait for confirm.** Then 00 or real skip to 01. |
| `/01-grill` while foggy | Do not skip 00. Run 00 or stop and say the dest is foggy. |
| Real skip | Omit 00. Do not create or fill `explore-map.md`. `intent.md` contains `Explore skipped: destination already clear.` |

### Documents

- If 00 **runs**, `explore-map.md` is required and `## Handoff to Intent` must be non-empty before 01.
- If 00 is **omitted**, there is no explore-map. That is not “on-path with a missing artifact.”
- `01`–`10` still require their artifacts; skip means extra approvals only.

### start-work

`./ask start-work` must **not** copy `explore-map.md`. Explore creates it when 00 runs.

## Interfaces

- `AGENTS.md` checklist item 1: decide, announce, `/00-explore` force, free-chat confirm, real skip vs 00.
- `_ask/policies/workflow.md`: 00 is the optional on-ramp exception to “artifacts are not optional.”
- `_ask/agents/00-explore.md`: real skip; create map only when Explore runs.
- `_ask/scripts/start-work.sh`: do not seed `explore-map.md`.

## Constraints

- No new `_ask/policies/explore-gate.md`.
- No `./ask` subcommand for the fog call.
- Do not persist a skip-explore flag in `intent.md` beyond the one-line skip record when skipped.

## Invariants

- `explore-map.md` exists only when Explore ran.
- `/00-explore` never becomes a confirm-the-gate conversation.
- Pipeline skip-approvals meaning unchanged.

## Failure cases

- Agent real-skips a foggy dest → thin Intent; return to 00.
- Agent writes a stub map on skip → looks like Explore ran.
- `start-work` seeds a stock map → looks like Explore started.

## Acceptance criteria

- Free on-path task: agent states 00 vs 01 and waits before starting either (except `/00-explore`).
- `/00-explore` starts 00 with no “is Explore needed?”
- `/01-grill` on a foggy dest does not omit 00.
- Real skip: no `explore-map.md` required; intent records the skip line.
- `./ask start-work <id>` does not create `work/<id>/explore-map.md`.
- `workflow.md` and `00-explore.md` no longer say to prepare the explore-map when 00 is omitted.
- `./ask verify` passes.

## Open questions

None.

## Source intent

`work/skip-explore/intent.md`
