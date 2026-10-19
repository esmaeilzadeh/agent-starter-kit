# Specification Challenge

## Model

model: `gpt-6.1-sol`  
runtime: `codex`  
parent_model: `gpt-6.1-sol`  
reasoning_effort: `medium`

## Specification

Reviewed `specs/proposals/status-template-stage-detection.md`, its canonical JSON criteria revision 1, the approved intent, stock plan/review templates, current status inference, and the canonical Grill contract.

## Ambiguities

“Populated task row” means a row with the table’s required shape and nonempty task ID and outcome. A first task may have no dependencies.

“Substantive verdict” means recorded outcome content under `## Review verdict`. The current free-text verdict remains valid, including a verdict that requests fixes.

## Missing failure cases

Test findings with an empty verdict, empty and incomplete plan rows, meaningful approach without rows, intent plus untouched later templates, and committed-ref behavior unaffected by uncommitted edits.

## Over-constraint risks

Requiring every task-row cell to be filled would reject valid first tasks. Requiring a fixed verdict vocabulary would add a restriction absent from the accepted intent.

## Under-constraint risks

Removing the Findings fallback fixes the review template, but the Work breakdown fallback also needs to distinguish populated task rows from table framing and guidance. Generic text detection would keep the plan false positive.

## Recommended clarifications

Keep plan and review recognition specific to their evidence: a meaningful Approach or populated task row for plans, and a meaningful verdict for reviews. Test separate stage outcomes through `./ask status` with committed temporary Git refs.

PAUSE-001 is suitable for review-only evidence from direct inspection of the canonical 01 Grill contract and generated runtime projection. The contract must require checkpointing both the first approval request and any revision before re-approval, while retaining exact-content approval and dedicated-branch commits.

## Challenge verdict

PASS for canonical spec revision 1 at commit `f1b1ecb` (digest `25d12bcc72365a30f460afc306344d5dc79c2e2ff07ed9b21c2bdb6d4a031468`). The digest-bound follow-up confirmed STATUS-001 excludes substantive earlier-stage content and result/acceptance evidence, preserving stage precedence. STATUS-002 covers meaningful approach, populated task rows, verdicts, and findings without verdicts. PAUSE-001 is approved for review-only verification. This decision does not approve the test plan.
