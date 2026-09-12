# Intent: real skip of 00 when destination is already clear

## What

1. On-path new task: the agent **finds out** whether kit **00 Explore** is required or a **real skip**, announces the call, and routes to 00 or 01.
2. **Real skip** = omit 00. Do not write or require `explore-map.md`. `intent.md` records `Explore skipped: destination already clear.`
3. **`/00-explore`** (or explicit “00-explore”) starts 00 immediately — no “do we really need Explore?”
4. **Free on-path chat:** agent proposes 00 vs 01 and **waits for confirm**, then proceeds.
5. **`/01-grill`** does not skip 00 when the destination is foggy.
6. **`./ask start-work`** does not seed `explore-map.md`. 00 creates that file when Explore runs.
7. Align `AGENTS.md`, `_ask/policies/workflow.md`, and `_ask/agents/00-explore.md`. No new policy file.
8. `01`–`10` keep ask-status meaning: skip extra *approvals*, not documents.

## Why

The kit already says skip 00 when What/Why is ownable, and also says do not skip the explore-map. Agents run 00 as ceremony or skip inconsistently. The human wants a real stage omit when the dest is clear, and a forced 00 when they invoke Explore.

## Non-goals

- Skill-pin bump (separate work-id).
- Later-inbox as committed kit product (separate work-id).
- `./ask fog` CLI.
- Durable off-path flag.
- Autoplay `/01`–`/10`.
- Parallel live branches for the parked jobs.

## Known assumptions

- “Continue this session till end including jobs found inside it” owns remaining Explore recs (Q1, Q4–Q8) after an expanded grill.
- Parked jobs run **after** this workstream, each via `./ask start-work`, not on `agent/skip-explore`.
- Pin commits mixed into this branch were reverted (`b9e7994`, `fbe3434`).

## Open questions

None from the closed Explore grill.

## Human decisions

- Free chat: propose + confirm (Q2-B, Q7-A).
- `/00-explore`: force 00, no double-check.
- `/01-grill`: fog wins.
- Real skip: omit map; note in intent.
- 00 is the exception to “don’t skip documents.”
- Stop seeding explore-map on start-work.
- Gate text in AGENTS + workflow + 00-explore.
