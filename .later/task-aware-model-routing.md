# Route stage models by task difficulty and consequences

- **Status:** parked (not live; no new workstream started)
- **Found during:** `revising-workbench` side conversation, 2026-10-16
- **Tracker:** pending; GitHub issue creation failed because `api.github.com` was unreachable
- **Start later:** new session, `./ask start-work task-aware-model-routing`
- **First stage:** 01 Grill; destination is clear, routing thresholds and naming need confirmation

## Why

Current routing mixes responsibilities (`thinking`, `typing`, `adversarial`,
`review`) with budget and selection pools (`cheap`, `diverse`). Implementation,
refactoring, and review can require substantial reasoning, so a stage name alone
does not establish that its work is cheap or mechanical. Selecting another GPT
model also does not establish cross-family diversity or independent reasoning.

Always using Astra for Spec Challenge spends the premium budget even on clear,
bounded specifications. Conversely, routinely assigning Luna to both implementation
and substantive review can economize at the point where subtle mistakes need to
be detected. Verification needs a further distinction: running established checks
is different from diagnosing failures or judging whether those checks demonstrate
the requirements.

The desired outcome is a clear, configurable routing policy that balances quality,
latency, and total task cost, including retries and rework. The suggestions below
are hypotheses to evaluate, not demonstrated savings or approved configuration.

## Proposed What (unapproved)

- Separate task responsibility, difficulty/uncertainty, consequences of failure,
  and model budget. Stage defaults remain useful starting points, with explicit
  escalation criteria and existing runtime/workstream overrides.
- Reconsider the `thinking` and `typing` names so they do not imply that coding,
  refactoring, or reviewing requires little judgment. Clarify that `cheap` is a
  budget pool and that `diverse` does not guarantee independent or cross-family
  review. Decide the final vocabulary during Grill; do not rename keys without
  accounting for resolver, overlay, documentation, and runtime compatibility.
- Keep Spec Challenge as a separate challenge step. Default routine challenges
  to Sol/high; explicitly promote to Astra/high for difficult architecture,
  security boundaries, fundamental ambiguity, or unresolved contradictions.
  Review-risk routing must not be mistaken for automatic challenge escalation.
- Default substantive review to Sol/medium. Reserve Luna for small mechanical
  changes and Astra/high for particularly difficult or consequential reviews.
  Preserve independent reviewer context and existing confirmation requirements;
  a different model alone is not proof of independence.
- Keep established check execution on Luna/low. Route difficult failure diagnosis,
  verification design, and assessment of coverage to Sol/medium or high. Passing
  weak checks does not establish acceptance, regardless of the executing model.
- Use Luna/medium for bounded implementation and local refactoring with clear
  contracts. Use Sol/medium or high for interacting components, unfamiliar
  behavior, structural changes, or repeated unsuccessful attempts. Reserve Astra
  for selected demanding analysis rather than every task in a stage.

### Suggested starting defaults

| Task | Default | Escalation or cheaper exception |
| --- | --- | --- |
| Explore, Grill, Spec, Spec Change, Accept | Sol/medium | Promote demanding analysis as needed |
| Plan | Sol/high | Retain the current effective repository setting |
| Spec Challenge | Sol/high | Astra/high for the difficult or consequential cases above |
| Implement and local Refactor | Luna/medium | Sol/medium or high for complex or structural work |
| LOW/MEDIUM substantive Review | Sol/medium | Luna for trivial mechanical changes |
| HIGH/CRITICAL Review | Astra/high | Preserve existing evidence and acceptance gates |
| Verify: established check execution | Luna/low | Stronger model usually unnecessary for command execution |
| Verify: diagnosis or coverage judgment | Sol/medium or high | Escalate particularly demanding analysis explicitly |

### Binding direction to evaluate

- In `.agents/ask/bindings/models.defaults.yaml`, map `05-plan` to `thinking`
  rather than `typing`, matching the existing effective Sol override. Keep
  portable stage roles separate from vendor model slugs.
- In `.agents/ask/bindings/runtimes/codex.yaml`, retain `thinking: gpt-6.1-sol`
  and `typing: gpt-6-luna`; propose `adversarial: gpt-6.1-sol`,
  `cheap: gpt-6.1-sol`, and `diverse: gpt-6-astra`. The `cheap` pool would then
  mean cheaper than Astra, not the cheapest available model; clarify or revise
  that name as part of the design.
- Set stage reasoning defaults for `03-spec-challenge: high`, `05-plan: high`,
  and `09-verify: low`; retain model defaults of Sol/medium, Luna/medium,
  and Astra/high. Account for `_ask/bindings/models.yaml` precedence, including
  its existing Plan override.
- Check effects on other runtimes before changing the portable stage map.
  Preserve existing override semantics and record effective model/effort in
  evidence. Generated agent pins do not switch an already-running parent model.
- Evaluate representative simple and complex workstreams using defect detection,
  acceptance outcomes, retries, elapsed time, and total usage/cost. Do not assume
  equal token consumption or translate API unit prices directly into Codex
  subscription savings. Establish escalation triggers from observed results.

## Note

The human requested: "write it as a later inbox card and save it for later."
This parks the discussion and proposed defaults; it does not authorize changing
bindings, stage contracts, model pins, or the current workstream.

Related cards: `stage-model-subagents` covers stage-agent bindings and provenance;
`phase-coordinator-models` covers switching the parent coordinator separately.

Official model guidance consulted during the discussion:
[Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), and
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
Recheck availability, pricing, and task fit when this card is started.
