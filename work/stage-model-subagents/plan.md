# Plan

## Specification

`specs/current/stage-model-subagents.md` (includes accepted spec-change A)

## Approach

Keep `_ask/agents/*.md` as protocol (spawn rules, no slugs). `_ask/bindings/models.defaults.yaml` is roles and Review pools only. Each `_ask/bindings/runtimes/<id>.yaml` holds that vendor’s slugs, picker, and families. `./ask sync` resolves per runtime and writes `.cursor/agents`, `.claude/agents`, and `.codex/agents`.

## Work breakdown

1. Add `_ask/bindings/models.defaults.yaml` (stage→role, Review risk→pool). No vendor slugs.
2. Add `_ask/bindings/runtimes/{cursor,claude,codex}.yaml` (role→slug, pool→slug, picker, families, pool notes).
3. Document consumer overlay `_ask/bindings/models.yaml` and `work/<id>/models.yaml` / `ASK_MODEL_*` / `ASK_MODEL_*_<RUNTIME>`.
4. Extend `sync-cursor-binding.sh` (or a sibling called from `./ask sync`) to emit the three agent trees from `_ask/bindings/templates/`.
5. Update stage contracts `01`, `03`, `05`, `07` (optional vs required spawn, return-to-parent, picker, provenance).
6. Update `OWNED-PATHS.md`, `CONTEXT.md`, `.ask.env.example`, review/challenge templates.
7. Kit test: Cursor Review `model:` comes from `runtimes/cursor.yaml`; `07-review.md` and `models.defaults.yaml` have no vendor slugs; consumer `models.yaml` is not clobbered on upgrade.
8. `./ask verify`.

## Risks

- Runtime slug lists go stale (accept; bump that runtime file).
- Parent model unknown (spec: optional spawn only on explicit override).
- Codex TOML vs Cursor/Claude markdown (three emitters, one portable map).
- `./ask sync` already regenerates `.cursor/skills` and commands; agent emit must be additive.

## Verification approach

`./ask verify` plus the new sync contract test in `_ask/tests/`.

## Out of scope for this plan

Parent picker switch. Live vendor model catalog. Hard fail in `check-workstream` for missing Review model. Claude/Codex end-to-end spawn in this repo’s Cursor-only CI.
