# Intent: per-stage model via subagent

Explore skipped: destination already clear.

## What

(Grill in progress.)

Give each kit stage a model preference. Ship defaults (Composer for high-token labor, Grok for first-party judgment, Claude or GPT for Challenge and Review when diversity is worth the Other Models pool). Override per workstream and globally via env. Generate runtime subagents from a portable binding map. Do not switch the parent chat picker.

## Why

Same-chat 01–10 on one model is correlated review. The Guide already wants a different review model plus deterministic Verify. Runtimes can pin a child model; skills and slash commands cannot. Preferences must stay consumer-owned so defaults are not a lock.

## Non-goals

- Parent-chat model switch
- Cursor slugs inside `_ask/agents/*.md`
- Promising a spawn the runtime cannot force
- Hand-maintained eleven Cursor/Claude/Codex agent files as source of truth (generated copies are in scope)

## Known assumptions

- Fast variants and Fable stay out of shipped defaults
- `09 Verify` stays script-first
- Preference precedence (Q2): per-work file → process / `.ask.env` → committed consumer map → kit defaults

## Open questions

- Q1: generate/require spawn for which stages (HITL vs labor; see Grill round 2)
- Q3 remainder: cheap-task Review so simple work does not burn Other Models by default
- Q4 layout: `.agent` vs `_ask/` vs existing `.agents/skills/`; confirm “folder per runtime” not “folder per LLM”

## Human decisions

- **Q2:** Committed portable map (roles, not Cursor slugs) + env slug overrides + per-work file. Precedence: work → env → committed map → kit defaults.
- **Q3 (partial):** Warn is not enough. Before a diversity-stage spawn, confirm and let the human pick from available models. Same-family pick: warn once, then proceed if they confirm.
- **Q4 (partial):** Support Cursor, Claude Code, and Codex in this work. Canonical binding SoT in an `.agent` (or similar) folder; generate each runtime’s tree (`.cursor`, `.claude`, `.codex`) from that SoT. Exact path vs `_ask/` still open.
