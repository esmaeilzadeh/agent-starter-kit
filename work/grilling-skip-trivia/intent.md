# Intent: grilling skips trivia

Explore skipped: destination already clear.

## What

Tighten kit grilling (`01 Grill`, Explore decision grilling, and ADR 0007) so numbered questions are only load-bearing; each round has an expanded-decisions block and a short “I’ll assume…” list; “defaults OK” covers the assume-list; facts are not asked; depth stops at destination, constraints, and non-goals. Never auto-approve a real decision.

## Why

Grilling treats “nothing left silently assumed” as “ask everything,” then ADR 0007 expands every item. That is rigor for a load-bearing choice and a tax on repo defaults.

## Non-goals

- Auto-approving real decisions
- Deleting the grilling primitive
- Growing the tree into implementation trivia
- A later-inbox or tracker change

## Known assumptions

- Card `.later/grilling-skip-trivia.md` is the source What/Why.
- Applies to Explore decision grilling as well as `01 Grill`.
- Community `grilling` skill stays pinned; kit contracts override it for kit stages unless Grill says otherwise.

## Open questions

- Whether we only amend kit files (01-grill, spec §15.1, ADR 0007 / successor) or also overlay/fork the pinned Community Skill.

## Human decisions

Pending one load-bearing Grill question (where the rule lives).
