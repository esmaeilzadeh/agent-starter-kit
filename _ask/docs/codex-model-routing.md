# Codex task model selection

Source: `.agents/ask/bindings/runtimes/codex.yaml`. Role/stage routing remains in `.agents/ask/bindings/models.defaults.yaml`; `./ask sync` generates the agent files. These defaults target task fit and cost, not maximum capability for every operation.

## Defaults

| Job | Default | Use |
| --- | --- | --- |
| Explore, Grill, Spec, Spec Change, Accept | `gpt-6.1-sol` | General reasoning and engineering judgment. |
| Plan, Implement, Refactor, Verify | `gpt-6-luna` | Clear, bounded work with an established contract; verification chiefly executes deterministic checks. |
| LOW/MEDIUM-risk Review | `gpt-6-luna` | Routine review of scoped changes. |
| Spec Challenge and HIGH/CRITICAL-risk Review | `gpt-6-astra` | Difficult counterexamples, consequential trade-offs, stronger review. |

Stage names are starting points, not a complexity classifier. A small configuration challenge can use a cheaper explicit override; a complex implementation should not remain on Luna just because its stage is Implement. Risk and complexity are separate; existing review-risk rules are unchanged. Model independence within GPT is not cross-family review diversity.

## Promote only the jobs that need it

For a complex implementation, put this existing override shape in `work/<work-id>/models.yaml`:

```yaml
codex:
  05-plan: gpt-6.1-sol
  06-implement: gpt-6.1-sol
  08-refactor: gpt-6.1-sol
```

For particularly difficult architecture or analysis, override just the relevant stage with `gpt-6-astra`. Leave routine verification on Luna. To run a simple specification challenge cheaply, override `03-spec-challenge` with `gpt-6-luna` for that workstream. Override `07-review` only deliberately; normal review otherwise follows the recorded risk.

Generate the workstream's assignments with:

```sh
ASK_WORK_ID=<work-id> ./ask sync
```

`./ask sync` without `ASK_WORK_ID` restores repository defaults. Precedence remains explicit environment, workstream overlay, consumer overlay, then portable defaults resolved through the runtime map. Consumer overlays live in `_ask/bindings/models.yaml` or `.agents/ask.local/bindings/models.yaml`. Neither override files nor reasoning settings are changed automatically by this refresh.

An already running Codex session can retain cached agent-role configuration. Inspect a spawned agent's effective model; if cached roles still use retired pins, use an explicit available model override or reload the client. Do not claim filesystem regeneration changes an already running agent.

## Selection basis

Verified on 2026-10-08 against [Codex model guidance](https://learn.chatgpt.com/docs/models) and [official model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection): Sol for complex coding/general work, Luna for focused repeatable tasks, Astra for the most demanding work. The per-stage defaults above are the repository's judgment; no comparative benchmark is claimed. The local Codex CLI 0.161.0 catalog advertised all three selected models at verification time.
