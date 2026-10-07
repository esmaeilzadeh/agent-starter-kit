# Acceptance

## Workstream

`inner-loop-hardening` on `agent/inner-loop-hardening`.
This decision covers the approved Codex parity continuation (t14). Earlier
t1–t13 evidence remains in its historical artifacts.

## Specification

`specs/current/inner-loop-hardening.md`, including approved
`spec-change-codex-parity-2026-10-07.md`.

## Evidence

Reviewed and verified implementation commit:
`ab8268e57db6fbb99577a427d660f56240889bb2`.

- Eleven Codex stage skills, shared Cursor bodies/overlays and deterministic
  sync. Generated skills committed; unrelated prepared skills preserved.
- Independent GPT-6.1 Sol medium Review: APPROVED, R1/R2 resolved, boundary ok;
  `review-codex-parity.md` and `refactor-codex-parity.md`.
- `./ask verify`: all 34 mandatory checks pass at that SHA;
  `verification-codex-parity.json`.
- Sequential RED/GREEN and sync evidence: `codex-parity-evidence.md`.
- Result recorded via `./ask record-result` against the verified SHA.

## Residual risks

Full dependency installation and current official documentation retrieval were
unavailable due network failures. Existing prepared skills were used; pin-only
validation passed. Live Codex skill discovery and agent spawning unverified.
First migration from an old installed kit uses the documented target-checkout
`upgrade-kit.sh --target` entrypoint. Consumer ignore rules that hide generated
skills cause migration to fail clearly and require an explicit rule adjustment.

## Context-engineering audit

`work/inner-loop-hardening/context-audit.md`, independently rechecked at
ab8268e: CE-01..CE-06 pass, none open.

## Acceptance decision

ACCEPTED by the human in chat on 2026-10-08: "approve".
Approval covers the Codex parity continuation (t14) and its recorded limitations.
Merge, push, tag and release remain separate human-authorized actions.

## Accepted commit SHA

`ab8268e57db6fbb99577a427d660f56240889bb2` (reviewed and verified implementation).
Subsequent commits record review, verification and human acceptance evidence.
