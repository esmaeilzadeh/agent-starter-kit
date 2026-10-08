# Specification: Current Codex task assignments

## Status

CURRENT — user requested the scoped configuration fix on 2026-10-08.

## Goal

All generated Codex stage agents use current, locally advertised models appropriate to their existing workload roles.

## Behavior and interfaces

Update `.agents/ask/bindings/runtimes/codex.yaml`:

| Role or pool | Model | Reason |
| --- | --- | --- |
| thinking | `gpt-6-astra` | Ambiguous product/architecture decisions and acceptance judgment. |
| adversarial | `gpt-6-astra` | Consequential specification challenge. |
| typing | `gpt-6.1-sol` | Current recommended complex coding and sustained agentic work. |
| cheap | `gpt-6.1-sol` | Capable routine independent implementation review. |
| diverse | `gpt-6-astra` | Stronger high-consequence review; distinct model, same GPT family. |

Picker: `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-luna`. No retired GPT-5.4 models remain in active Codex bindings or generated agent files.

`./ask sync` generates all eleven Codex agents from this source. Preserve existing role/override resolution and risk behavior. Preserve all other runtime definitions and inherited reasoning settings.

## Acceptance criteria

- CM-001: Codex role/pool/picker configuration contains the assignments above; generated defaults use them, including high-risk Review escalation to Astra.
- CM-002: Existing explicit environment/consumer/work overrides and other runtime outputs remain compatible; the sync regression check passes after updating its old Codex expected default.

Both are review-only nonbehavioral configuration criteria. An independent reviewer must approve the exact contract and candidate; repository CheckPlan execution remains mandatory. No new behavior or claimed performance improvement is introduced.

## Evidence and sources

Official guidance fetched 2026-10-08: [Codex models](https://learn.chatgpt.com/docs/models), [model selection](https://developers.openai.com/api/docs/guides/model-selection). The former identifies GPT-6.1 Sol for complex coding, Astra for demanding work, Luna for scoped repeatable work, and retirement of GPT-5.4/mini on 2026-08-31. The exact workload assignments are engineering judgment, not a published per-kit-stage benchmark.

Local catalog: `/home/mohamad/.codex/models_cache.json`, fetched `2026-10-08T14:45:45.512971151Z`, Codex CLI `0.161.0`; all three chosen models have list visibility. Credentials and unrelated catalog content are not copied into the repo.

## Non-goals and failure cases

No model API calls, global configuration changes, new routing mechanics, reasoning pins, other-runtime upgrades, or historical artifact rewrites. Report unavailable models or stale loaded roles; do not silently claim a retired cached agent was upgraded during its run.

## Source intent

`work/codex-model-refresh/intent.md`

## E2E

Applies: existing sync shell check exercises generated files and override/risk behavior through public scripts, restoring default outputs afterward. No production data or external inference.
