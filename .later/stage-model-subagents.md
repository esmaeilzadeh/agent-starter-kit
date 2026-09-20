# Per-stage model via subagent (defaults + overrides)

- **Status:** parked (not live; no `agent/*`)
- **Found during:** stage-model research, 2026-09-13
- **Tracker:** https://github.com/esmaeilzadeh/agent-starter-kit/issues/47
- **Start later:** new session, `./ask start-work stage-model-subagents`
- **First stage:** 01 Grill unless the orchestrator boundary becomes foggy

## Why

Kit stages are roles, but one parent model commonly runs all stages. Independent
review needs a distinct context/model plus deterministic verification.

## Proposed What (unapproved)

Generate runtime-specific stage subagents from portable role and model
preferences. Begin with Review and Spec Challenge, preserve deterministic Verify
as the evidence gate, and record model provenance in artifacts.

## Note

Do not create a bespoke multi-agent runtime or runtime-specific source of truth.
