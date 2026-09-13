# Specification: per-stage model via generated subagents

## Status

CURRENT

## Goal

Each kit stage has a resolved **role** (and Review a **pool**). `_ask/bindings/` is the portable map and agent templates. `./ask sync` writes Cursor, Claude Code, and Codex stage agents using **that runtime’s** slug table. Challenge and Review spawn a child, the human picks a model from that runtime’s list, and the artifact records the pick. Other stages may spawn a child when their model is not the parent’s; the child returns questions or drafts into the parent chat.

## Non-goals

Switching the parent picker from `./ask`. Putting runtime slugs in `_ask/agents/*.md` or in the portable defaults file as if they were cross-runtime. Hand-editing generated `.cursor/agents`, `.claude/agents`, or `.codex/agents`. A hard spawn guarantee. A new `.agent/` root. Changing Verify from script-first. Treating one vendor’s cheap pool as a fact about the others.

## Behavior

### Resolution

Canonical values are roles (`thinking`, `typing`, `adversarial`) and Review pools (`cheap`, `diverse`). LOW/MEDIUM Review → `cheap`. HIGH/CRITICAL → `diverse`. Unset risk means LOW.

Slugs exist only under `_ask/bindings/runtimes/<runtime>.yaml` (kit-shipped defaults for that coding agent) and in consumer overlays / env / per-work files.

Precedence, first hit wins:

1. `work/<work-id>/models.yaml` (role, pool, or a runtime-keyed slug)
2. Process env / `.ask.env`: `ASK_MODEL_<STAGE>` (role or pool) or `ASK_MODEL_<STAGE>_<RUNTIME>` (slug for one runtime)
3. Consumer overlay `_ask/bindings/models.yaml` if present
4. Kit portable map `_ask/bindings/models.defaults.yaml` (roles and pools only)
5. Runtime table `_ask/bindings/runtimes/<runtime>.yaml` (role→slug, pool→slug)

An unqualified slug in env or overlay applies only to the runtime being generated, not to all three. Kit upgrade refreshes shipped runtime tables; it must not clobber consumer `models.yaml`.

### Portable stage map

| Stage | Role | Review pool |
| --- | --- | --- |
| 00 Explore | thinking | — |
| 01 Grill | thinking | — |
| 02 Spec | thinking | — |
| 03 Spec Challenge | adversarial | — |
| 04 Spec Change | thinking | — |
| 05 Plan | typing | — |
| 06 Implement | typing | — |
| 07 Review | — | cheap or diverse (from risk) |
| 08 Refactor | typing | — |
| 09 Verify | typing | — |
| 10 Accept | thinking | — |

Each runtime file also has: picker list, family prefixes for that vendor, and a short note on that vendor’s token pools. Family is defined **per runtime**, not globally.

**Risk** is `risk:` on `work/<id>/models.yaml` or in `intent.md`. Unset means LOW.

**Parent model** is whatever the parent records or the human states. If unknown: required spawn still runs; optional spawn runs only when the stage has an explicit override (work / env / consumer map).

**Picker list** is that runtime file’s model list. The human may type a slug that is not on the list; warn that it is unlisted.

### Spawn

- **Required:** `03 Spec Challenge`, `07 Review`. Before labor, present available models for the current runtime, default highlighted. Human confirms. If the pick is the same family as Implement (or as Spec, for Challenge) **on that runtime**, warn once; continue after a second confirm.
- **Optional:** any other stage when resolved slug ≠ parent slug, or when that stage has an explicit override (see parent-unknown rule). The child produces labor (expanded Grill questions, plan draft, …). The parent presents it, talks to the human, and writes `intent.md` / `plan.md` (or the stage artifact). The child must not close Grill or Accept.
- **Never required:** `09 Verify` as an LLM child. Scripts remain the evidence.

### Generation

`./ask sync` reads `_ask/bindings/` and writes:

- `.cursor/agents/kit-<stage>.md` (frontmatter `model`, Review `readonly: true` when the runtime allows)
- `.claude/agents/kit-<stage>.md`
- `.codex/agents/kit-<stage>.toml`

Stage contracts under `_ask/agents/` stay protocol. They say when to spawn and to record the model. They do not name vendor slugs.

Generated files are kit-owned projections. Consumers override through the resolution stack, not by editing the projection.

### Provenance

`work/<id>/review.md` and `work/<id>/spec-challenge.md` record `model`, `runtime`, and `parent_model`. Missing record is a warning in `./ask check-workstream`, not a hard fail.

## Interfaces

- `_ask/bindings/models.defaults.yaml` (roles, Review pools)
- `_ask/bindings/runtimes/{cursor,claude,codex}.yaml` (slugs, picker, families)
- Optional consumer `_ask/bindings/models.yaml`
- `./ask sync`
- `.ask.env.example` documents `ASK_MODEL_*` and `ASK_MODEL_*_<RUNTIME>`
- `_ask/agents/01-grill.md`, `03-spec-challenge.md`, `05-plan.md`, `07-review.md`
- `_ask/OWNED-PATHS.md`, `CONTEXT.md`
- `_ask/policies/risk.md` (which Review pool)
- Generated `.cursor/agents/`, `.claude/agents/`, `.codex/agents/`

## Constraints

- `_ask/bindings/` is the binding SoT. `.agents/skills/` stays Community Skills.
- Upgrade must not clobber consumer `models.yaml` or `*.local` overlays. Shipped `runtimes/*.yaml` may refresh.
- No live tokens in committed model files.
- Portable defaults and `_ask/agents/*.md` contain no runtime model slugs.

## Invariants

- Protocol text under `_ask/agents/` has no runtime model slugs.
- After `./ask sync`, each generated agent’s `model` comes from that runtime’s resolution, not from a global slug table.
- Parent chat remains the HITL surface for Grill, Spec, and Accept.

## Failure cases

- Parent writes `review.md` or `spec-challenge.md` without a spawn attempt or without recording a model.
- Grill or Accept is closed inside a child with no parent HITL.
- Sync writes slugs into `_ask/agents/*.md` or into `models.defaults.yaml`.
- LOW Review on a runtime resolves to that runtime’s `diverse` slug unless the human picked it.
- Consumer edits a generated agent file and `./ask sync` / upgrade overwrites it without a documented overlay path.
- One slug is applied to all three runtimes as if it were portable.

## Acceptance criteria

- `_ask/bindings/models.defaults.yaml` lists all `00`–`10` as roles and Review as pools; it has no vendor slugs.
- Each of `cursor`, `claude`, `codex` has a runtime file with role→slug, pool→slug, picker list, and family prefixes.
- `./ask sync` writes the three runtime agent trees from that resolution (plus overlay/env/work if present).
- Stage contracts for `03` and `07` require spawn + picker + same-family warn (family from the current runtime file).
- Stage contracts for `01` and `05` allow a child that returns into the parent chat when the stage model differs or is explicitly overridden.
- `.ask.env.example` lists `ASK_MODEL_*` and `ASK_MODEL_*_<RUNTIME>`.
- `OWNED-PATHS.md` / `CONTEXT.md` name `_ask/bindings/` and the generated runtime dirs.
- A kit test asserts Cursor Review output has a `model:` from `runtimes/cursor.yaml`, and that `_ask/agents/07-review.md` and `models.defaults.yaml` have no Cursor/Claude/Codex slugs.
- `./ask verify` passes.

## Open questions

None.

## Source intent

`work/stage-model-subagents/intent.md`

## Spec change

`work/stage-model-subagents/spec-change.md` (accepted A, 2026-09-13)
