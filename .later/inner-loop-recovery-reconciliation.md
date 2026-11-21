# Preserve recovery evidence and reconcile pending task attempts

- **Status:** included in current completion planning on `agent/client-security-hardening`; no separate workstream
- **Found during:** `client-security-hardening`
- **Next step:** finish `work/client-security-hardening/completion-implementation-plan.md`, then stop for Luna coordinator handoff
- **Tags:** recovery, inner-loop
- **Attribution:** `client-security-hardening`, CSH-10 recovery conflicts; Astra/high consultation; candidate `e889779`
- **Affected responsibilities:** recovery traceability validation for model-state projections; safe reconciliation when a pending task has source changes but no recorded attempt
- **Publication status:** planning authorized by the human; implementation has not started

## Why

The frozen runner blocks CSH-10 without a history-preserving state transition.
It also rejects otherwise compatible CSH-01–09 TaskResults because the
checkpoint comparison requires `traceability/model-state/current.json` to stay
byte-identical and disallows newly published model-state files and
`completion.json`. The current ledger's 80 rows correctly extend the checkpoint
77-row prefix and are not themselves a conflict.

## Scope

Design and implement recovery that preserves immutable prior results, reviews,
attempt history, accepted contract pins, and failed execution evidence while
supporting valid append-only model-state/completion projections and an explicit
pending-with-zero-attempt reconciliation. Never synthesize a past attempt or
rewind source to hide the mismatch. Plan this work with Sol-high alongside
milestone evidence and laddered escalation under the latest direction recorded
in `work/client-security-hardening/completion-scope.md`. Keep the current frozen
kit pin unchanged and conduct kit maintenance with dogfooding disabled.

## Note

The 279-file structured evidence snapshot is committed in
`work/client-security-hardening/inner-loop/evidence/recovery-evidence-bundle.tar.gz`.
Raw output logs are stored in the private archive documented in
`work/client-security-hardening/inner-loop/evidence/recovery-reconciliation-proposal.md`.
Do not modify CSH-10 state or checkpoint refs until this work is independently
reviewed and its recovery transition is proven safe.
