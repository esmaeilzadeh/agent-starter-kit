# Shorten AskIt source entry points

## Intent and authority

Reduce always-loaded source instructions while retaining their rules behind
explicit context pointers. This is the follow-on feature named in CWH's approved
intent. The human requested “fix them” and delegated acceptance above 90%
confidence. The destination is clear; source self-development keeps the kit
workflow disabled. CWH was accepted and released as v2.0.2 before this work began.

## Scope

- Keep the highest-priority self-development rule byte-identical in `AGENTS.md`.
- Keep startup access, continuation, request routing/reproduction, clean-tree,
  commit/verification, progress, and human-only setup instructions at the entry.
- Move the complete previous detailed checklist to `_ask/docs/source-workflow.md`.
  Adapt its relative links, preserving its text and decisions.
- Trim Cursor's bootstrap to source/client entry pointers. The installed client
  still falls back to `.agents/ask/session.md`.
- Update the README starting point and release installer pin.

## Verification and acceptance

Accepted implementation: `d826d1a86bc818e3502f82179eac80a64b8165ad`.
Decision: accepted under the human's >90% confidence delegation and the source
self-development rule. Confidence: 95% (subjective engineering judgment).

The self-development rule is byte-identical and the complete old checklist is
retained with only relative links adjusted. All local pointers resolve. Source
entry context fell from 1,433 to 374 words. Projection sync leaves the committed
source unchanged. Five access tests and all five installed client hook journeys
pass. Canonical-source sync and document rules pass. See `verification.json`.

Runtime scripts, shared session instructions, hook configurations, and CheckPlan
are unchanged from v2.0.2. Cursor's bootstrap pointer text is the only client
binding change. The baseline full CheckPlan passed all 41 checks; focused checks
cover this documentation delta. The published v2.0.2 README installer also passed
in an isolated cache.

No new permanent tests were added for this document relocation. Interactive
editor startup remains untested. Reproduce on a clean clone at v2.0.3 with
`./ask verify`; the pinned frozen checkout can be recreated using its tracked
instructions.
