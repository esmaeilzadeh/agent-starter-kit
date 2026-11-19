# Spec Change proposal: decide models during Grill

Status: PROPOSED. This records the human's requested feature; it does not amend
the accepted security specification or authorize implementation.

## Current specification and reason

The accepted contract is `specs/current/client-security-hardening.{md,json}`,
revision 1. Its approved intent excludes reworking agent workflows. Adding model
selection and orchestrator handoff expands What, Why and that non-goal, so review
this proposal together with the complete `intent-model-flow.proposed.md` before
changing the canonical contract.

Human reason: once the user seals a specification, they need to rely on the flow
continuing to the authorized endpoint without repeated model questions at stage
transitions. Pause for a real escalation or a required manual model switch.

Current source: `.agents/ask/stages/03-spec-challenge.md` and `07-review.md`
each require a model picker and another same-family choice. Runtime bindings
already resolve defaults. Those repeated questions caused this workstream's
interruption even though its challenge model was already configured.

## Proposed behavior

### CSH-009: one model decision during Grill

Given a feature reaches Grill in a supported coding-agent runtime, when the
agent presents model selection:

- Show one complete model plan with resolved stage defaults, any existing
  overrides, and the orchestrator model to use for implementation.
- Ask one question: **Confirm model plan** / **Change selected models**. Allow
  accompanying free text and specific stage overrides in that same interaction.
- Accept all defaults with one submitted confirmation. When Change is selected,
  collect only the requested exceptions together; do not run a stage-by-stage
  questionnaire. A complete submitted replacement map resolves the decision.
- Explain any same-family reviewer relationship in this model plan. Preserve
  independent review contexts; a shared model family alone causes no later
  confirmation.
- Record the selected runtime, resolved model identities and overrides in the
  workstream using the existing model override precedence. Keep the complete
  model decision inspectable and resumable without embedding model slugs in
  portable stage prompts.

### CSH-010: stage transitions reuse the model decision

Given the model plan is confirmed, when a stage begins or the workstream resumes:

- Resolve and use the saved model choice automatically. Do not ask another
  routine model picker, defaults confirmation or same-family confirmation.
- Preserve the authorized endpoint and all existing scope, safety and acceptance
  decisions. Model confirmation does not approve the intent or implementation.
- Pause when a selected model is unavailable, capabilities cannot satisfy the
  agreed role, the user requests a change, or a genuine scope/policy escalation
  arises. Report the concrete cause and request only the missing decision.
- For existing workstreams, preserve explicit prior model choices and configured
  defaults; do not turn a missing new-format record into repeated stage gates.
  Collect a new model decision at the next authorized Grill, or when the user
  explicitly changes model policy. Do not infer a historical submitted choice.

### CSH-011: implementation orchestrator handoff

Given the authorized next action is implementation, when its preflight runs:

- Resolve the latest accessible implementor model for the active coding-agent
  runtime, subject to a specific human override recorded during Grill. The
  user's current family examples are Composer for Cursor and Luna for Codex;
  these are selection requirements/examples, not verified universal catalogs or
  permanent hard-coded version slugs.
- Check live runtime/account availability and the actual orchestrator identity.
  A static picker entry is insufficient evidence that a model is accessible.
  If newer accessible defaults differ from the confirmed plan, use the confirmed
  update policy; an explicit exact-model override remains fixed.
- If already using the selected implementation model, continue without a prompt.
  Otherwise change the current orchestrator model automatically when the runtime
  provides that capability and verify the result before implementation writes.
- Changing a spawned worker's model does not change the orchestrator. A config
  edit, recommendation, or successful child spawn is not switch evidence.
- If the runtime cannot switch the orchestrator automatically, stop before
  implementation and ask the user to change to the named model in their coding
  agent. Resume after observable verification, or an explicit human acknowledgment
  when identity cannot be inspected; record which evidence was available.
- An inaccessible selected model or unavailable catalog is a real escalation.
  Identify that condition and offer an accessible alternative; do not silently
  choose a different family or claim to have found the latest accessible model.
- A plan-only endpoint stops before this preflight and never asks for a model
  switch solely to finish planning.

### CSH-012: portable decisions and runtime capability evidence

Given Cursor, Codex, or another supported runtime, when model decisions and
implementation handoff are evaluated:

- Keep stage roles portable and model catalogs/capabilities in runtime bindings.
  Reuse the workstream model overlay instead of adding another precedence chain.
- During Grill, confirm the policy of selecting the latest accessible implementor
  at implementation entry; stage-specific exact overrides remain available.
- Verify each runtime's actual discovery/switch capability during implementation
  of this feature. Represent unsupported and unknown capabilities explicitly.
- Carry the revised behavior through canonical prompts, policies, generated
  runtime agents/skills/commands and user guidance so an old projection cannot
  reintroduce stage picker pauses.

## Impact, alternatives and sequencing

Affected canonical surfaces: `.agents/ask/stages/01-grill.md`, `03-spec-challenge.md`,
`06-implement.md`, `07-review.md`, `.agents/ask/bindings/`, workflow/delegation
policies, model resolution and runtime generation, workstream model records and
focused tests. Regenerate vendor projections from their canonical sources.
Inventory all callers before implementation; these are affected components, not
the final owned-path TaskGraph.

Recommended: include this bounded feature in a revised combined specification
and implementation plan, with separate model-flow tasks and tests. Serialize
shared sync/runtime paths with security hardening tasks. Keep the frozen kit pin
unchanged while developing its replacement behavior.

Alternative: keep the security specification unchanged and park this feature for
a separate workstream. It would remain unimplemented and the current frozen
stage rules would continue to apply. Do not silently switch branches or launch
the second workstream.

## Verification required in the revised plan

- Confirm defaults once in Grill, override only one stage, and inspect the saved
  map. Verify other stages retain their defaults.
- Continue through Challenge, Plan, Implement and independent Review without
  routine model questions, including same-family and resumed stages. Preserve a
  genuine escalation and the final acceptance decision.
- Exercise an already-correct orchestrator, a successful automatic switch, an
  unsupported switch requiring one manual handoff, failed verification and an
  unavailable model/catalog. Assert no implementation writes before handoff.
- Exercise runtime-specific Composer/Luna resolution with fake catalogs, exact
  overrides and changed availability. Test the orchestrator separately from a
  child reviewer/worker. Do not require paid live calls for these contract tests.
- Retain runtime capability smoke evidence where available; report unsupported
  capabilities without claiming a tested automatic switch.
- Verify plan-only work stops without entering the implementation switch gate.
- Verify regenerated projections contain the new decision flow and old
  workstreams keep their recorded choices and authorization endpoints.

## Decision and endpoint

Pending one submitted choice approving this proposal and the complete revised
intent together, or keeping the current security scope. CSH-001 through CSH-008
remain unchanged. These proposed IDs join the canonical registry only after
approval and renewed independent challenge of the amended contract.

The security-only Astra challenge remains valid for its exact revision-1 digest;
it does not approve the new model-flow criteria. Planning is paused for this
scope decision. After approval, revise Spec/Challenge/Plan, then stop when the
implementation plan is ready. No implementation, merge or publication is
authorized.
