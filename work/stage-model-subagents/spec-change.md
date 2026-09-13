# Specification Change Proposal

## Current specification

`specs/current/stage-model-subagents.md`

The portable layer already has roles (`thinking`, `typing`, `adversarial`), then a **single Cursor-named default table** (Grok 4.6, Composer 2.5, Claude Sonnet 5) and Review defaults that name those slugs. Codex gets a special-case Terra line. Family prefixes are also global (`composer`, `grok`, `claude`, …).

## Proposed change

Canonical kit defaults are **roles and pools only**. No model id is canonical across runtimes.

- Portable map (`models.defaults.yaml`): stage → role; Review risk → **pool** (`cheap` | `diverse`).
- Each runtime file (`_ask/bindings/runtimes/cursor.yaml`, `claude.yaml`, `codex.yaml`) owns: role→slug, pool→slug, picker list, family prefixes, notes on that vendor’s token pools.
- Consumer overlay / env / per-work file may set a slug **or** a role/pool. A slug is runtime-specific; `./ask sync` applies it only to the runtime being generated (or to `ASK_MODEL_*_<RUNTIME>` if we split env keys).
- Drop the cross-runtime table that says Grill is Grok and Review is Sonnet.
- Cursor “Other Models” vs “Cursor Models”, Claude’s own pricing, and Codex’s own pricing stay inside that runtime file. The spec must not treat Composer-as-cheap as a fact about Claude Code.

Recommended env shape (names still implementable later):

```text
ASK_MODEL_07_REVIEW=diverse
ASK_MODEL_01_GRILL=thinking
ASK_MODEL_07_REVIEW_CURSOR=claude-sonnet-5
```

Unqualified slug overrides apply to the runtime that is syncing, not to all three.

## Why the change is needed

Cursor, Claude Code, and Codex each ship a different catalog and a different bill. A slug that is cheap on Cursor can be absent or expensive on Codex. The CURRENT spec’s default table is a Cursor opinion pasted onto the kit.

## Impacted artifacts

- `specs/current/stage-model-subagents.md` and `specs/proposals/stage-model-subagents.md`
- `work/stage-model-subagents/intent.md` (Q3b, Why “Cursor Models pool”)
- `work/stage-model-subagents/plan.md` (defaults file contents)

## Impacted workstreams

This workstream only (`stage-model-subagents`). No shipped bindings yet.

## Migration / transition notes

None in product repos; spec is not implemented.

## Acceptance criteria for the change

- CURRENT spec has no required cross-runtime model id.
- Kit defaults are roles + Review pools; slugs live only under `runtimes/<id>`.
- Acceptance criteria no longer require `models.defaults.yaml` to list Cursor ids for all stages.
- Intent Q3b is restated as cheap/diverse **pools**, resolved per runtime.

## Decision

**Needed:** confirm this change, and A vs B:

- **A (recommended):** kit ships per-runtime default slugs (Cursor: Grok/Composer/…; Claude: Sonnet/Opus/…; Codex: whatever that file says). Out of the box works on each vendor. Those slugs are adapter data, not protocol.
- **B:** kit ships roles and pools only. Sync fails or leaves `model:` empty until the consumer fills that runtime’s overlay.

Reply `A` or `B` (or edit the proposal). Current spec stays until you confirm.
