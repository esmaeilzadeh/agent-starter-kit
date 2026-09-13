# Plan

## Specification

`specs/current/stage-model-subagents.md`

## Approach

Keep `_ask/agents/*.md` as protocol (spawn rules, no slugs). Add `_ask/bindings/` as the map and emitter input. Extend `./ask sync` to write `.cursor/agents`, `.claude/agents`, and `.codex/agents` from resolved roles plus the shipped runtime slug tables.

## Work breakdown

1. Add `_ask/bindings/models.defaults.yaml` (roles, Cursor defaults, family prefixes, Review risk defaults).
2. Add `_ask/bindings/runtimes/{cursor,claude,codex}.models.yaml` picker lists and role→slug maps.
3. Document consumer overlay `_ask/bindings/models.yaml` and `work/<id>/models.yaml` / `ASK_MODEL_*`.
4. Extend `sync-cursor-binding.sh` (or a sibling called from `./ask sync`) to emit the three agent trees from templates under `_ask/bindings/templates/`.
5. Update stage contracts `01`, `03`, `05`, `07` (optional vs required spawn, return-to-parent, picker, provenance fields).
6. Update `OWNED-PATHS.md`, `CONTEXT.md`, `.ask.env.example`, review/challenge templates.
7. Kit test: sync writes Review `model:`; `07-review.md` has no Cursor slugs; consumer `models.yaml` is not clobbered by a dry upgrade check if one exists.
8. `./ask verify`.

## Risks

- Runtime slug lists go stale (accept; bump with defaults).
- Parent model unknown (spec: optional spawn only on explicit override).
- Codex TOML vs Cursor/Claude markdown (three emitters, one map).
- `./ask sync` already regenerates `.cursor/skills` and commands; agent emit must be additive.

## Verification approach

`./ask verify` plus the new sync contract test in `_ask/tests/`.

## Out of scope for this plan

Parent picker switch. Live vendor model catalog. Hard fail in `check-workstream` for missing Review model. Claude/Codex end-to-end spawn in this repo’s Cursor-only CI.
