# Codex task model selection

Source: `.agents/ask/bindings/runtimes/codex.yaml`. Role/stage routing remains in `.agents/ask/bindings/models.defaults.yaml`; `./ask sync` generates the agent files. These defaults target task fit and cost, not maximum capability for every operation.

## Defaults

| Job | Default | Effort | Use |
| --- | --- | --- | --- |
| Explore, Grill, Spec, Spec Change, Accept | `gpt-6.1-sol` | medium | General reasoning and engineering judgment. |
| Plan, Implement, Refactor | `gpt-6-luna` | medium | Clear, bounded work with an established contract. |
| Verify | `gpt-6-luna` | low | Primarily executing deterministic checks. |
| LOW/MEDIUM-risk Review | `gpt-6-luna` | medium | Routine review of scoped changes. |
| Spec Challenge and HIGH/CRITICAL-risk Review | `gpt-6-astra` | high | Difficult counterexamples and consequential trade-offs. |

Stage names are starting points, not a complexity classifier. A small configuration challenge can use a cheaper explicit override; a complex implementation should not remain on Luna just because its stage is Implement. Risk and complexity are separate; existing review-risk rules are unchanged. Model independence within GPT is not cross-family review diversity.

## Promote only the jobs that need it

For a complex implementation, put this existing override shape in `work/<work-id>/models.yaml`:

```yaml
codex:
  05-plan: gpt-6.1-sol
  06-implement: gpt-6.1-sol
  08-refactor: gpt-6.1-sol
reasoning_effort:
  codex:
    05-plan: high
    06-implement: high
    08-refactor: high
```

For particularly difficult architecture or analysis, override just the relevant stage with `gpt-6-astra`. Leave routine verification on Luna. To run a simple specification challenge cheaply, override `03-spec-challenge` with `gpt-6-luna` for that workstream. Override `07-review` only deliberately; normal review otherwise follows the recorded risk.

Generate the workstream's assignments with:

```sh
ASK_WORK_ID=<work-id> ./ask sync
```

`./ask sync` without `ASK_WORK_ID` restores repository defaults. Model precedence remains unchanged. Consumer overlays live in `_ask/bindings/models.yaml` or `.agents/ask.local/bindings/models.yaml`.

Effort resolves separately: runtime-specific `ASK_EFFORT_06_IMPLEMENT_CODEX`, generic `ASK_EFFORT_06_IMPLEMENT`, workstream `reasoning_effort`, consumer `reasoning_effort`, runtime stage default, resolved-model default, then inheritance. Substitute another stage name as needed. Effort overlays accept runtime mappings as above, flat stage keys, or a `stages` mapping. Explicit `inherit` omits `model_reasoning_effort`; unknown model slugs without an explicit effort override also inherit. Allowed explicit levels are `low`, `medium`, `high`, `xhigh`, `max`; use extra-high levels only when demonstrated necessary. Invalid levels reject generation before any runtime files change. Current model/account support still governs inference availability; this is not a capability discovery service.

For trivial edits use a Luna/low workstream override. For complex architecture/implementation use Sol/high, and Astra/high for particularly difficult reasoning. Global Codex settings are not changed. An explicit model override alone selects that model's configured effort default; it does not imply a complexity classification.

An already running Codex session can retain cached agent-role configuration. Inspect a spawned agent's effective model; if cached roles still use retired pins, use an explicit available model override or reload the client. Do not claim filesystem regeneration changes an already running agent.

## Selection basis

Verified on 2026-10-08 against [Codex model guidance](https://learn.chatgpt.com/docs/models) and [official model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection): Sol for complex coding/general work, Luna for focused repeatable tasks, Astra for the most demanding work. The per-stage defaults above are the repository's judgment; no comparative benchmark is claimed. The local Codex CLI 0.161.0 catalog advertised all three selected models at verification time.
