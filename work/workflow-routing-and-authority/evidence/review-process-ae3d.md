# Independent review: workflow-routing-and-authority

- Candidate: `ae3d2d73ace24e48e640d9a16c34f7df012c8479`
- Comparison base: `72441577^`; fix-specific review also inspected changes since `4c525115`
- Route: reproduced bug-fix repair, under frozen kit `0e303265ceae1fbcdc9b2261bd922b003ab68924`
- Requested/resolved reviewer model: `gpt-6-luna` (frozen resolver output and supplied native spawn parameter)
- Self-reported backend identity: unavailable
- Runtime: Codex
- Parent model: GPT-6
- Verdict: **APPROVED**

## Findings

No blocking or non-blocking findings.

## Review basis

Reviewed the workflow and verification policy changes, model confidence routing, maintenance inventory/status behavior, committed UI capture, focus styling, and relevant added/changed tests. Checked the user’s six reported workflow issues against the route definitions and authority limits: investigation versus consultation, Explore facts versus Grill goals, non-feature entry paths, approval of intent versus unresolved product choices, Refactor as resolution of Review findings, and verification failure diagnosis. Confirmed that review/investigation do not authorize implementation; standalone maintenance has a concise scope record and repository CheckPlan verification; existing Engineering Model/TaskGraph gates are retained; factual gaps override confidence and stale-evidence assessments are not reused. The captured committed view now retains normalized documents and references and fails closed on malformed committed JSON. Test fixture changes preserve client hook data, retain provenance checks, and increase the deadline only for the slow lifecycle case.

The generated stage/skill pair has the expected projection-only front matter difference, and `git diff --check 72441577^..ae3d2d73` is clean. I did not execute tests independently. The coordinator-provided evidence reports targeted workflow, UI, navigation, detail, client-write, context integration, lazy, keyboard, and browser checks passing; expanded Python discovery had 20 failures and 4 errors at baseline, and its final rerun was still pending. No claim is made that the complete expanded suite passes.

## Review scope and limits

The reviewed product diff contains 91 changed paths, including canonical process guidance, client projections, generated skills/commands, status/model/UI code, tests, and the repair record. Repetitive generated projections were checked for consistency at the stage pair and reviewed through their canonical sources; the complete 91-path diff was not exhaustively line-audited. This review makes no acceptance decision for the workstream and does not replace Verify.
