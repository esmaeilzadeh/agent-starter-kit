# Fix cryptic, over-compressed Grill questions in Codex

- **Status:** parked (not live; no new `agent/*`)
- **Found during:** `structured-agentic-environment`, modeling Grill, 2026-10-15
- **Tracker:** https://github.com/esmaeilzadeh/agent-starter-kit/issues/49
- **Start later:** new session, `./ask start-work codex-grill-expansion`
- **First stage:** 00 Explore: root cause and Cursor/Codex parity are unconfirmed.

## Why

During `structured-agentic-environment` modeling discussion (2026-10-15), the user requested all Grill questions in one shot. The response reduced ten load-bearing decisions to dense A/B/C summaries. The user reported that the questions had become cryptic and too compact again, and that this had previously been fixed in the Cursor bundle.

## Proposed What (unapproved)

Investigate whether the earlier Cursor fix is missing from the Codex bundle, whether protocol pointers/load paths fail to deliver it, or whether this is instruction-following failure despite loaded guidance. Do not assume bundle drift: `.agents/ask/stages/01-grill.md` already requires expanded alternatives, tradeoffs and failure modes; both generated runtime agents point to that contract, and the parent had read it in this session.

Proposed outcome (unapproved): preserve understandable explanations when presenting the entire question set. Each load-bearing question should explain the decision in plain language, concrete examples, alternatives, consequences and failure modes enough for an informed refusal. “All questions in one shot” controls batching, not explanation depth. Keep assumptions separate and do not infer approval.

Compare the prior Cursor fix, portable source, generated skills/commands/agents and Codex parent/child invocation. Reproduce the single-question and all-at-once paths, and validate the eventual fix at the correct loading or behavior seam without duplicating protocol sources or merely checking for matching strings.

Parked only; no implementation or new workstream authorized. Resume with 00 Explore if root cause is unclear, then bounded intent/spec amendment as appropriate.

## Note

Do not treat the reported earlier Cursor fix or suspected Codex bundle bug as verified. Preserve the existing workstream and its unresolved modeling decisions. This card authorizes no fix by itself.
