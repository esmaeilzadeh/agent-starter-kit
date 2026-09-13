# Intent: per-stage model via subagent

Explore skipped: destination already clear.

## What

(Proposed — Grill not closed.)

Give each kit stage a model preference. Ship Cursor defaults (Composer for high-token labor, Grok for first-party judgment, Claude or GPT for Challenge and Review). Let a human override per workstream and globally via env. For stages that must disagree with the parent (at least Review), generate a runtime subagent with that model pin. Do not switch the parent chat picker.

## Why

Same-chat 01–10 on one model is correlated review. The Guide already wants a different review model plus deterministic Verify. Runtimes can pin a child model; skills and slash commands cannot. Preferences must stay consumer-owned so defaults are not a lock.

## Non-goals

(Proposed — Grill not closed.)

- Parent-chat model switch
- Cursor slugs inside `_ask/agents/*.md`
- A custom multi-agent runtime or eleven hand-maintained subagents as source of truth
- Promising hard enforcement the runtime cannot deliver

## Known assumptions

- Adapter generates pins from a portable map
- Fast variants and Fable stay out of shipped defaults
- `09 Verify` stays script-first

## Open questions

- Which stages spawn as subagents in this work (Review only vs Review + Challenge vs all 00–10)
- Committed map vs gitignored env vs both; precedence
- Instruction-only spawn vs provenance vs check-workstream fail
- Cursor adapter only vs Claude/Codex files in the same work

## Human decisions

(none yet)
