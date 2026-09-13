# Intent: grilling skips trivia

Explore skipped: destination already clear.

## What

Tighten kit grilling (`01 Grill`, Explore decision grilling, and ADR 0007) so numbered questions are only load-bearing; each round has an expanded-decisions block and a short “I’ll assume…” list; “defaults OK” covers the assume-list; facts are not asked; depth stops at destination, constraints, and non-goals. Never auto-approve a real decision.

**Also:** before grilling starts, the agent must try to surface problem-space that would otherwise stay hidden — by finding related Community Skills and **asking the human before preparing/downloading any of them**, then grilling with those skills in context.

## Why

Two failure modes:

1. Grilling treats “nothing left silently assumed” as “ask everything,” then ADR 0007 expands every item. Tax on obvious defaults.
2. The griller cannot see the real problem space (missing domain method), so questions look shallow or wrong even when few.

## Non-goals

- Auto-approving real decisions
- Auto-downloading skills without asking
- Deleting the grilling primitive
- Growing the tree into implementation trivia
- Forking the pinned `mattpocock/skills` grilling tree (Q1-A)
- A later-inbox or tracker change

## Known assumptions

- Card `.later/grilling-skip-trivia.md` plus this session’s “hidden from the griller” note.
- Applies to Explore decision grilling as well as `01 Grill`.
- Kit contracts only (01-grill, spec §15.1, ADR 0007 / successor). Community grilling pin stays; kit wins on kit stages.
- `./ask prepare` for **already pinned, required** manifest skills stays as today (not a surprise download). The ask-first rule is for **additional** related skills proposed at Grill time.

## Open questions

- How the agent finds and proposes related skills, and when a proposal is required vs skipped.

## Human decisions

- Q1-A: kit files only; do not overlay/fork the pinned grilling skill.
