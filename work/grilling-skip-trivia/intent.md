# Intent: grilling skips trivia

Explore skipped: destination already clear.

## What

Tighten kit grilling (`01 Grill`, Explore decision grilling, and ADR 0007) so:

1. Numbered questions are only load-bearing.
2. Each round has an expanded-decisions block and a short “I’ll assume…” list. “Defaults OK” covers the assume-list.
3. Facts are not asked. Depth stops at destination, constraints, and non-goals.
4. Never auto-approve a real decision.
5. Before the first numbered question: search for related Community Skills that would change What/Why. Propose a short list. **Ask before preparing any extra skill.** Prepare only accepted ones. **Pin each accepted skill in `_ask/skills/manifest.yaml`** (explicit revision, never `latest`) so later work in this repo prepares and uses it.

Skip the propose step when no extra domain skill would change What/Why (well-bounded kit/repo change).

## Why

Grilling either asks everything obvious, or misses the real problem space because the griller lacks the domain method. Skills that matter should stick to the repo, not vanish after one chat.

## Non-goals

- Auto-approving real decisions
- Auto-downloading skills without asking
- Forking the pinned `mattpocock/skills` grilling tree
- Replacing `./ask prepare` for already-pinned required skills
- Implementation trivia

## Known assumptions

- Kit contracts only (01-grill, 00-explore, spec §15.1, ADR). Community grilling pin stays; kit wins on kit stages.
- Applies to Explore decision grilling and `01 Grill`.
- Required manifest pins still prepare without a per-session ask.

## Open questions

None.

## Human decisions

- Q1-A: kit files only.
- Q2-A + persist: ask, then pin accepted skills in the repo manifest for later requests.
- Defaults OK 2026-09-13.
