# Review

## Model

- model: inherit (grok-4.6)
- runtime: cursor
- parent_model: grok-4.6
- kit_default_review_pool: cheap (unset risk → grok-4.6)
- human: continue with default models
- kit_adversarial_kimi-k3: parked `.later/cursor-spawn-slugs.md`

## Scope

`agent/status-later-inbox` vs `specs/current/status-later-inbox.md`: `_ask/scripts/status.sh`, `_ask/tests/test-status.sh`, `ask` help, `ask-complete.sh`, Build Spec §23.4 / §30.1, ADR 0015, `.later/README.md`, `workflow.md`.

## Findings

1. `--work-id` with no value was order-dependent (`--later-only --work-id` vs `--work-id --later-only`). Spec: combinations after parse.
2. Tests missed default `--json` with cards, empty `--later-only --json`, valueless `--work-id` + `--later-only`, and `--work-id` missing with cards on disk.
3. `work/later-inbox/intent.md` still says status does not list parked cards. Frozen prior workstream; not this spec’s required doc list.

## Suggested fixes

1. FIX: mark `--work-id` present even without a value; after parse, `--later-only` + `--work-id` → `does not apply to later`; otherwise empty id → `requires an id`.
2. FIX: extend `test-status.sh` for those JSON and exclusive-flag cases.
3. ACCEPT WITH RATIONALE: do not rewrite archived `later-inbox` intent.

## Residual risks

Bytewise filename sort and non-git `--later-only` remain untested. Spawn-path / kimi-k3 is a parked later card, not this work.

## Review verdict

PASS with nits (items 1–2 fixed on this branch after review).
