# Specification: grilling skips trivia

## Status

CURRENT

## Goal

Kit grilling asks only load-bearing questions, states assumptions in a separate list, and surfaces hidden problem-space by proposing related Community Skills **after asking**, then pinning accepted skills in this repo’s manifest for later sessions.

## Non-goals

Auto-approve real decisions. Auto-download extra skills. Fork the pinned grilling skill. Ask the human for facts already in the repo.

## Behavior

### Frontier filter

A numbered question only if it is hard to reverse, is What/Why/non-goal, the recommendation might be wrong, or it blocks other decisions.

### Two blocks per round

1. Expanded decisions (alternatives, tradeoffs, failure modes).
2. Short “I’ll assume…” list. “Defaults OK” / “all recs” covers the assume-list. Only numbered questions need expansion.

Never treat “all ok” as valid if a **load-bearing** question was never expanded.

### Skill-before-grill

Before the first numbered question (Explore decision grilling and `01 Grill`):

1. Search for related Community Skills (skills.sh / find-skills / already in `.agents/skills`).
2. Propose at most a short list, and only if a skill would change What/Why.
3. Ask which to prepare. Do not download extras without a yes.
4. For each accepted skill: add/update `_ask/skills/manifest.yaml` with `source`, explicit `revision` (never `latest`), `skill`, `role`, `required: false` unless they say required; run `./ask prepare` for that pin.
5. Grill with those SKILL.md files in context.

If prepare fails (network), say so and grill anyway or stop — do not silently skip the ask.

Already-pinned **required** manifest skills still use `./ask prepare` as today (not a surprise extra).

### Depth

Grill destination, constraints, non-goals. Do not grow into implementation trivia.

## Interfaces

- `_ask/agents/01-grill.md`, `_ask/agents/00-explore.md`
- `_ask/spec/03-policies-skills-context.md` §15.1
- ADR 0007 (amended by 0016)
- `_ask/skills/manifest.yaml` (consumer-owned pins)

## Constraints

Never `revision: latest`. Do not vendor skill trees. Kit protocol overrides the Community grilling “ask everything” stance on kit stages.

## Invariants

A real decision is never auto-approved. An extra skill is never prepared without a human yes. An accepted extra skill is recorded in the manifest.

## Failure cases

- Agent asks ten obvious defaults as numbered Qs.
- Agent prepares a new skill without asking.
- Agent uses a skill once and does not pin it (next chat loses it).
- Agent asks the human for a fact that is in `CONTEXT.md` / an ADR.

## Acceptance criteria

- `01-grill.md` and §15.1 state the filter, two-block format, ask-before-prepare, and manifest pin.
- ADR 0016 exists and 0007 points at it.
- `00-explore.md` uses the same grilling rules for Explore decisions.
- `./ask verify` passes.
- `./ask sync` refreshes Cursor projections.

## Open questions

None.

## Source intent

`work/grilling-skip-trivia/intent.md`
