# Intent: per-stage model via subagent

Explore skipped: destination already clear.

## What

Give each kit stage a role (and Review a cheap/diverse pool). `./ask sync` generates Cursor, Claude Code, and Codex stage agents from `_ask/bindings/`, using **that runtime’s** slug table. A stage whose resolved slug is not the parent’s may run as a child and return its work into this chat. Challenge and Review must spawn, then confirm a model from that runtime’s list. Review’s pool follows workstream risk. Same-family pick (family defined per runtime): warn once, then continue if the human confirms.

## Why

One model for 01–10 makes Review a self-grade. A smarter Grill or Plan is useful when the child writes the questions or the plan and the parent keeps the conversation with the human. Token cost is the price of a pin **on that runtime**. Each coding agent has its own catalog and bill, so no model id is a kit-wide default.

## Non-goals

- Switching the parent chat’s model picker from `./ask`
- Runtime slugs inside `_ask/agents/*.md` or in portable `models.defaults.yaml`
- Hand-maintained agent files under `.cursor/agents`, `.claude/agents`, or `.codex/agents` as source of truth
- Promising the runtime will spawn when the parent ignores the contract
- A new singular `.agent/` folder next to `.agents/skills/`
- One cheap-pool story copied from Cursor onto Claude or Codex

## Known assumptions

- `09 Verify` stays script-first
- Generated runtime trees are `.cursor/`, `.claude/`, `.codex/` (coding agents, not one folder per LLM)
- Kit protocol files stay under `_ask/`; bindings hold the portable map plus per-runtime adapter tables
- Kit ships per-runtime default slugs (decision A). Those files are adapter data.

## Open questions

None.

## Human decisions

- **Q1:** Generate agent files for all `00`–`10`. Required spawn (confirm + picker): Spec Challenge and Review. Other stages: optional child when the stage slug differs or is explicitly overridden. Child returns into the parent chat; the parent stays the human surface.
- **Q2:** Committed portable map + env + per-work file. Precedence: work → env → consumer map → portable roles/pools → runtime slugs.
- **Q3:** Confirm and pick from that runtime’s list before a required spawn. Same family on that runtime: warn, then proceed on confirm. Record model, runtime, parent_model.
- **Q3b:** Review pool from risk: LOW/MEDIUM → `cheap`; HIGH/CRITICAL → `diverse`. Each runtime maps those pools to its own slugs.
- **Q4:** Cursor + Claude Code + Codex in this work. Canonical binding SoT: `_ask/bindings/`. Sync writes each runtime tree.
- **Spec change:** No cross-runtime default model ids. **A:** ship per-runtime default slugs as adapter data.
