# Intent: per-stage model via subagent

Explore skipped: destination already clear.

## What

Give each kit stage a model preference. `./ask sync` generates Cursor, Claude Code, and Codex stage agents from `_ask/bindings/`. A stage whose model is not the parent’s may run as a child and return its work into this chat (Grill questions, Plan draft, and the same pattern for other HITL stages). Challenge and Review must spawn, then confirm a model from the runtime’s list. Review’s default follows workstream risk so a small change does not spend Other Models unless the human picks that. Same-family pick: warn once, then continue if the human confirms.

## Why

One model for 01–10 makes Review a self-grade. A smarter Grill or Plan is useful when the child writes the questions or the plan and the parent keeps the conversation with the human. Token cost is the price of the pin, not a reason to forbid the child. Cheap Review defaults keep simple work on the Cursor Models pool.

## Non-goals

- Switching the parent chat’s model picker from `./ask`
- Cursor slugs inside `_ask/agents/*.md`
- Hand-maintained agent files under `.cursor/agents`, `.claude/agents`, or `.codex/agents` as source of truth
- Promising the runtime will spawn when the parent ignores the contract
- A new singular `.agent/` folder next to `.agents/skills/`

## Known assumptions

- Fast variants and Fable stay out of shipped defaults
- `09 Verify` stays script-first
- Generated runtime trees are `.cursor/`, `.claude/`, `.codex/` (coding agents, not one folder per LLM)
- Kit protocol files stay under `_ask/`; bindings are the portable map and templates only

## Open questions

None.

## Human decisions

- **Q1:** Generate agent files for all `00`–`10`. Required spawn (confirm + picker): Spec Challenge and Review. Other stages: optional child when that stage’s resolved model differs from the parent (smarter Grill/Plan included). Child returns into the parent chat; the parent stays the human surface.
- **Q2:** Committed portable map + env slug overrides + per-work file. Precedence: work → env → consumer map → kit defaults.
- **Q3:** Confirm and pick from available models before a required spawn. Same family: warn, then proceed on confirm. Record the model on the artifact.
- **Q3b:** Risk-tiered Review default: LOW/MEDIUM → Composer or Grok; HIGH/CRITICAL → Claude Sonnet 5 or GPT-5.6 Terra. Picker always open.
- **Q4:** Cursor + Claude Code + Codex in this work. Canonical binding SoT: `_ask/bindings/`. Sync writes each runtime tree.
