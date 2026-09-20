# Per-stage model via subagent (defaults + overrides)

- **Status:** parked (not live; no `agent/*`)
- **Found during:** free chat (Linus / vibe-coding comparison; Cursor + Claude Code + Codex model-switch investigation, 2026-09-13)
- **Start later:** new session, `./ask start-work stage-model-subagents`
- **First stage:** 01 Grill (dest is ownable: adapter-generated stage subagents + preference layers). Skip 00 unless Grill opens “do we become an orchestrator?”

## Why

Kit stages are roles. The same chat usually runs 01–10 on one model. Guide §16 says three agents on Model X are one reviewer; useful diversity is a **different review model** plus deterministic Verify.

Runtimes can pin a child model (Cursor `.cursor/agents/` `model:`, Claude `.claude/agents/`, Codex `.codex/agents/*.toml`). Skills and slash commands cannot. The parent chat picker cannot be flipped by `./ask`. Soft automation only: spawn a stage subagent; the parent can still write the artifact itself.

v1 forbids a bespoke multi-agent runtime and “eleven hand-maintained Cursor subagents.” Any design must stay an **adapter** that *generates* pins from portable preferences.

## Proposed What (unapproved)

- Generate **stage subagents** (start with `07 Review`, then `03 Spec Challenge`; do not clone 00–10 as a second SoT).
- Stage contract: do not author that stage’s artifact in the parent context; spawn the pinned subagent.
- Ship **Cursor-first defaults** below (performance vs Cursor two-pool cost, Sept 2026). Consumer can change them.
- **Preference layers** (later Grill must lock order; proposed most-specific wins):
  1. Per-workstream override (e.g. `work/<work-id>/models.env` or a small yaml next to intent)
  2. Global / repo env (e.g. `.ask.env` / `.env` keys, not committed secrets — model slugs only)
  3. Kit / adapter defaults
- Portable config stores **stage → role** (thinking / typing / adversarial), not raw Cursor slugs. Adapters map role → runtime id (Cursor vs Claude vs Codex).
- Record the model that wrote `review.md` / challenge / accept in the artifact. Optional later: `./ask check-workstream` fails Review if it shares Implement’s model.
- Do **not** promise a parent-chat model switch. Do **not** put Cursor slugs in `_ask/agents/*.md`.

### Suggested defaults (Cursor, 2026-09-13)

Token volume on **Cursor Models** pool (Composer / Grok). Other Models pool only for stages that must disagree with Implement. No Fast variants. No Fable unless Accept is CRITICAL.

| Stage | Default | High-stakes upgrade | Notes |
| --- | --- | --- | --- |
| 00 Explore | Grok 4.6 | stay Grok; Composer 2.5 for throwaway prototype code | |
| 01 Grill | Grok 4.6 | Claude Opus 5 or GPT-5.6 Sol | |
| 02 Spec | Grok 4.6 | Claude Sonnet 5 | |
| 03 Spec Challenge | Claude Sonnet 5 or GPT-5.6 Terra | Claude Opus 5 | **Not** the Spec model |
| 04 Spec Change | Grok 4.6 | Opus / Sol | same class as Grill/Spec |
| 05 Plan | Composer 2.5 | Grok 4.6 if architectural | |
| 06 Implement | Composer 2.5 | Grok 4.6 for design-heavy diffs | volume stage |
| 07 Review | Claude Sonnet 5 or GPT-5.6 Terra | Opus 5 or GPT-5.6 Sol | **different vendor from Implement** |
| 08 Refactor | Composer 2.5 | Grok only if Review found a design bug | same-model as Implement is OK |
| 09 Verify | Composer 2.5 (or almost no model) | same | scripts are the reviewer |
| 10 Accept | Grok 4.6 | Claude Opus 5 on HIGH / CRITICAL | |

If Implement is Composer, Review must not be Composer/Grok. If Other Models pool is empty: Review on Grok in a **new chat** + treat 09 as the real second opinion.

Example env shape (names unapproved):

```text
ASK_MODEL_06_IMPLEMENT=composer-2.5
ASK_MODEL_07_REVIEW=claude-sonnet-5
ASK_MODEL_03_SPEC_CHALLENGE=gpt-5.6-terra
```

Per-work file can override the same keys for one `work-id` only.

## Note

Local inbox card (gitignored). Soft spawn is not CI-grade: Cursor parent Task `model` can override frontmatter; Claude `CLAUDE_CODE_SUBAGENT_MODEL` overrides every child; Codex custom-agent attach has been buggy. Grill whether v1 is Review-only + provenance, or full stage map.
