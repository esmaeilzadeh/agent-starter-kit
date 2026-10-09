# Intent: Refresh Codex task models

## What

Replace retired Codex stage model assignments and picker entries with current, locally available models. Preserve the portable role map, risk-based review selection, override precedence, and other runtimes. Regenerate Codex agent definitions.

## Why

Before continuing the Engineering Model and UI work, the human requested that every task use the best suitable current Codex model. Existing bindings name retired GPT-5.4 models.

## Non-goals

Change model prompts, reasoning effort, account configuration, other runtime assignments, authentication, or workflow authority. No model performance benchmark or paid inference probe.

## Known assumptions

Task-fit defaults retain a lower-budget execution tier: Luna for clear scoped execution and routine review, GPT-6.1 Sol for general reasoning, Astra for difficult challenges and high-risk review. Existing workstream overrides promote complex implementation/planning to Sol or exceptional analysis to Astra.

## Open questions

None blocking this scoped configuration refresh.

## Human decisions

The human explicitly sequenced this fix before the Engineering Model/UI work and delegated selection to current Codex guidance. This authorizes the configuration update and independent review with current models; the obsolete pending GPT-5.4 picker question is superseded.

The human corrected the initial expensive proposal: use the best fit for each job, including lower-budget models for simple tasks. The initial proposal was not implemented; its unfinished challenge is superseded by this corrected contract.

Explore skipped: destination already clear.

## E2E

Applicability: `applies`

Journey: execute the existing sync command and inspect generated Codex definitions, risk selection, and environment overrides. Environment: disposable/local repository files; no inference or production service. Reset: existing sync test restores default projections.

Risk: LOW. Changes are nonbehavioral runtime configuration and expected-output maintenance for an existing test.
