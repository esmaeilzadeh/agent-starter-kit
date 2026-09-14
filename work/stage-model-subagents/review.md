# Review

## Model

- model: grok-4.6
- runtime: cursor
- parent_model: grok-4.6
- same_family: yes (warned; human said continue, then “its good”)
- spawn: Task subagent was interrupted; findings below are from a second pass on the same model. Residual: Review is same-family as Implement.

## Scope

`main...HEAD` on `agent/stage-model-subagents` against `specs/current/stage-model-subagents.md`.

## Findings

1. **Med — Review role override ignored.** In `_ask/scripts/sync-runtime-agents.py`, `slug_from_role_or_pool` treats every `07-review` resolve as the risk pool after cheap/diverse. `ASK_MODEL_07_REVIEW=thinking` or `07-review: adversarial` still maps to `cheap`/`diverse` from risk, not `roles.thinking`. Spec: overlay may set a role or pool.

2. **Nit — unused import.** `import re` in `sync-runtime-agents.py` is unused.

3. **Nit — no test for HIGH / `diverse`.** `test-sync-runtime-agents.sh` only checks LOW → `grok-4.6`. Cursor `diverse` is now `kimi-k3`; a regression there would pass CI.

Acceptance criteria that hold: portable defaults have no slugs; three runtime files exist; sync writes three agent trees; `03`/`07` require spawn + picker; `01`/`05` allow return-to-parent; `.ask.env.example` documents `ASK_MODEL_*`; `OWNED-PATHS.md` / `CONTEXT.md` name bindings; install leaves consumer `models.yaml`; `./ask verify` passed at `deea6c5` (later K3 commits not re-verified in this file).

## Suggested fixes

- Use the risk pool only when the token is `review`. Honor `thinking` / `typing` / `adversarial` / `cheap` / `diverse` on Review.
- Drop `import re`.
- Assert `ASK_RISK=HIGH` Cursor Review is `kimi-k3`.

## Residual risks

- Same-family Review on this workstream (accepted).
- Runtime slug lists will go stale.
- Codex custom-agent attach remains best-effort.
- `upgrade-kit` preserve of `models.yaml` is not exercised by a live clone test (install-kit overlay is).

## Review verdict

PASS. Finding 1 and the unused import are fixed on this branch; HIGH/`diverse` and `thinking` override are covered by `test-sync-runtime-agents.sh`.
