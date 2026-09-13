# Grilling is load-bearing questions plus ask-before-prepare skills

Kit grilling (`01 Grill`, Explore decision grilling) was reading ADR 0007 as “expand every frontier item” and the Community grilling skill as “nothing left silently assumed.” That produced long rounds of obvious questions and still missed problem-space the griller could not see without a domain skill.

## Decision

- Number a question only if it is load-bearing (hard to reverse, What/Why/non-goal, recommendation might be wrong, or it blocks other decisions).
- Each round: expanded numbered questions + a short “I’ll assume…” list. “Defaults OK” covers the assume-list.
- Do not ask facts already in the repo. Cap depth at destination, constraints, non-goals.
- Never auto-approve a real decision. “All ok” is invalid if a load-bearing question was never expanded.
- Before the first numbered question: propose extra related Community Skills that would change What/Why; **ask before prepare**; pin accepted skills in `_ask/skills/manifest.yaml` (explicit revision, never `latest`) so later sessions in this repo use them.
- Do not fork the pinned Community `grilling` skill. Kit contracts override it on kit stages.

ADR 0007 still applies to **numbered** questions only.

## Consequences

- `_ask/agents/01-grill.md`, `00-explore.md`, spec §15.1, and Guide grilling-expansion text follow this rule.
- Extra skills become repo pins, not chat-only downloads.
