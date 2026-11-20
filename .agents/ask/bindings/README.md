# Bindings

Portable stage roles and Review pools live in `models.defaults.yaml`. Vendor slugs live in `runtimes/<id>.yaml`. `./ask sync` writes `.cursor/agents`, `.claude/agents`, and `.codex/agents`.

Do not put slugs in `.agents/ask/stages/*.md` or in `models.defaults.yaml`.

## Overrides (first hit wins)

1. `work/<work-id>/models.yaml` — used at spawn time (set `ASK_WORK_ID` when you want sync to bake it)
2. Env / `.ask.env`: `ASK_MODEL_07_REVIEW=diverse` or `ASK_MODEL_07_REVIEW_CURSOR=claude-sonnet-5`
3. Project settings in `.agents/ask.local/bindings/models.yaml` (optional). If absent, AskIt reads the legacy `_ask/bindings/models.yaml`.
4. `models.defaults.yaml` (role or pool)
5. `runtimes/<id>.yaml` (slug)

An unqualified slug applies only to the runtime being generated.
The workstream overlay is checked before ambient model variables, so an exact
saved stage choice cannot be replaced by the environment. Grill records the
complete resolved table under `model_plan`; only exact stage exceptions belong
in the runtime-specific overlay. Role-based defaults stay dynamic.

## Consumer `models.yaml` example

```yaml
risk: LOW
07-review: cheap
cursor:
  01-grill: grok-4.6
```

## Workstream `work/<id>/models.yaml` example

```yaml
risk: HIGH
07-review: diverse
```
