# Specification: per-stage model via generated subagents

## Status

PROPOSED

## Goal

Each kit stage has a resolved model. `_ask/bindings/` is the portable map and agent templates. `./ask sync` writes Cursor, Claude Code, and Codex stage agents. Challenge and Review spawn a child, the human picks a model from that runtime’s list, and the artifact records the pick. Other stages may spawn a child when their model is not the parent’s; the child returns questions or drafts into the parent chat.

## Non-goals

Switching the parent picker from `./ask`. Putting runtime slugs in `_ask/agents/*.md`. Hand-editing generated `.cursor/agents`, `.claude/agents`, or `.codex/agents`. A hard spawn guarantee. A new `.agent/` root. Changing Verify from script-first. Fast or Fable as shipped defaults.

## Behavior

### Resolution

Precedence, first hit wins:

1. `work/<work-id>/models.yaml` (or the same keys in that workstream)
2. Process env / `.ask.env` (`ASK_MODEL_00_EXPLORE` … `ASK_MODEL_10_ACCEPT`)
3. Consumer overlay `_ask/bindings/models.yaml` if present
4. Kit defaults `_ask/bindings/models.defaults.yaml`

The portable map names **roles** (`thinking`, `typing`, `adversarial`) and optional per-stage role or slug overrides. Each runtime adapter maps a role to a model id for that runtime. Kit defaults (Cursor names, 2026-09-13):

| Stage | Role | Default Cursor id |
| --- | --- | --- |
| 00 Explore | thinking | Grok 4.6 |
| 01 Grill | thinking | Grok 4.6 |
| 02 Spec | thinking | Grok 4.6 |
| 03 Spec Challenge | adversarial | Claude Sonnet 5 |
| 04 Spec Change | thinking | Grok 4.6 |
| 05 Plan | typing | Composer 2.5 |
| 06 Implement | typing | Composer 2.5 |
| 07 Review | adversarial, then risk | see Review defaults |
| 08 Refactor | typing | Composer 2.5 |
| 09 Verify | typing | Composer 2.5 |
| 10 Accept | thinking | Grok 4.6 |

HIGH/CRITICAL Review default: Claude Sonnet 5 (Cursor / Claude) or GPT-5.6 Terra (Codex). LOW/MEDIUM Review default: Composer 2.5 or Grok 4.6 (same Cursor Models pool as Implement).

### Spawn

- **Required:** `03 Spec Challenge`, `07 Review`. Before labor, present available models for the current runtime, default highlighted. Human confirms. If the pick is the same vendor family as Implement (or as Spec, for Challenge), warn once; continue after a second confirm.
- **Optional:** any other stage when resolved model ≠ parent model (including a smarter Grill or Plan). The child produces the stage labor (expanded questions, plan draft, …) and the parent applies it in this chat. The human stays with the parent.
- **Never required:** `09 Verify` as an LLM child. Scripts remain the evidence.

### Generation

`./ask sync` reads `_ask/bindings/` and writes:

- `.cursor/agents/kit-<stage>.md` (frontmatter `model`, Review `readonly: true` when the runtime allows)
- `.claude/agents/kit-<stage>.md`
- `.codex/agents/kit-<stage>.toml`

Stage contracts under `_ask/agents/` stay protocol. They say when to spawn and to record the model. They do not name Cursor slugs.

Generated files are kit-owned projections. Consumers override models through the resolution stack, not by editing the projection.

### Provenance

`work/<id>/review.md` and `work/<id>/spec-challenge.md` record `model` and `parent_model` (or Implement/Spec model). Missing record is a warning in `./ask check-workstream`, not a hard fail.

## Interfaces

- `_ask/bindings/` (defaults, optional consumer `models.yaml`, templates)
- `./ask sync` (existing command, extra emitters)
- `.ask.env.example` documents `ASK_MODEL_*` (placeholders only)
- `_ask/agents/01-grill.md`, `03-spec-challenge.md`, `05-plan.md`, `07-review.md` (spawn / return-to-parent)
- `_ask/OWNED-PATHS.md`, `CONTEXT.md`
- `_ask/policies/risk.md` (Review default tier)
- Generated `.cursor/agents/`, `.claude/agents/`, `.codex/agents/`

## Constraints

- `_ask/bindings/` is the binding SoT. `.agents/skills/` stays Community Skills.
- Upgrade must not clobber consumer `models.yaml` or `*.local` overlays.
- No live tokens in committed model files.

## Invariants

- Protocol text under `_ask/agents/` has no runtime model slugs.
- Generated agent files match the resolved map after `./ask sync`.
- Parent chat remains the HITL surface for Grill, Spec, and Accept.

## Failure cases

- Parent writes `review.md` or `spec-challenge.md` without a spawn attempt or without recording a model.
- Sync writes slugs into `_ask/agents/*.md`.
- Review default for LOW workstreams is an Other Models id unless the human picked it.
- Consumer edits a generated agent file and `./ask sync` / upgrade overwrites it without a documented overlay path.

## Acceptance criteria

- `_ask/bindings/models.defaults.yaml` exists and lists all `00`–`10` roles/defaults.
- `./ask sync` creates the three runtime agent trees from that map (plus overlay/env/work if present).
- Stage contracts for `03` and `07` require spawn + picker + same-family warn.
- Stage contracts for `01` and `05` allow a child that returns into the parent chat when the stage model differs.
- `.ask.env.example` lists `ASK_MODEL_*` keys.
- `OWNED-PATHS.md` / `CONTEXT.md` name `_ask/bindings/` and the generated runtime dirs.
- Review defaults follow the risk table unless overridden.
- A kit test asserts sync output contains `model` for Review and does not put Cursor slugs in `_ask/agents/07-review.md`.
- `./ask verify` passes.

## Open questions

None.

## Source intent

`work/stage-model-subagents/intent.md`
