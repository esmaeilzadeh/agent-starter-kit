# Specification Change: task-fit reasoning effort

## Current specification

Revision 2 refreshes model pins only and preserves inherited effort. Its verified candidate is `31ad549f3fdfd9bbb49e3dfdb7f82745a2ead5de`.

## Proposed change and reason

Add CM-004 for explicit Codex effort generation. The human asked “with which effort?” and on 2026-10-08 authorized continuing with the proposed task-fit efforts, then the main Engineering Model/UI plan. Model-only routing leaves every child inheriting this session's high effort.

## Contract

Runtime `reasoning_effort.models` maps known slugs to defaults: Luna medium, Sol medium, Astra high. `reasoning_effort.stages` overrides stage defaults (Verify low). A work/consumer `reasoning_effort` mapping uses the same stage/runtime shapes as model overlays. Precedence: runtime-specific `ASK_EFFORT_<STAGE>_CODEX`, generic `ASK_EFFORT_<STAGE>`, work overlay, consumer overlay, runtime stage default, resolved-model default, otherwise inherit. Literal `inherit` omits the TOML field. Allowed explicit values are low, medium, high, xhigh, max; these are supported by all three locally advertised selected models. Availability remains model/account dependent. Invalid values fail before writing any runtime outputs. An unknown slug without an explicit effort override inherits, even for a stage with a configured default.

## Impact and alternatives

Update canonical Codex binding, TOML template, generator, generated Codex agents, guidance, criterion contract and behavioral test plan. Other runtime files and existing model precedence remain unchanged. Global Codex configuration remains unchanged. Alternative: keep effort inherited and document manual edits; rejected because regeneration would not encode the user's requested task fit.

## Transition and acceptance

Keep CM-001–003 and their independent review authority. CM-004 requires public-generator integration and end-to-end tests, actual assertion-red then final green, independently challenged contract, candidate review, full Verify. Prior verification remains historical, not evidence for the extension.

## Decision

APPROVED BY HUMAN — “ok continue and then continue the main plan” after the task-fit effort proposal. Challenge may still escalate a concrete conflict; do not invent a new approval for changed goals.
