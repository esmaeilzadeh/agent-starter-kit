# Separate unit and E2E verification to control suite cost

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `continuation-recovery` side conversation (2026-10-22)
- **Start later:** new session, `./ask start-work separate-unit-and-e2e-verification`
- **First stage:** 00 Explore; inspect the verification and inner-loop execution paths and establish where costly E2E checks are repeated
- **Tags:** workflow, verification, testing, e2e, unit-tests, cost
- **Publication status:** draft; pushed on a topic branch based on `origin/develop`, pending integration into `develop`

## Why

After inner-loop tasks have already run their task-scoped checks, the final project-wide verification can repeat a costly full test suite. Unit tests and end-to-end (E2E) tests have different execution cost and coverage roles. Running every E2E journey on every final verification adds time even when the work does not require those journeys.

The desired behavior is for the final verification's test run to execute unit tests by default, while E2E tests run when the work's acceptance criteria or assessed risk require them. The workflow must make that decision explicit and retain evidence explaining which checks ran or why E2E was not applicable.

## Proposed What (unapproved)

- Map the project-wide verification commands, inner-loop integration checks, test-plan entries, and existing E2E applicability rules. Identify where test suites are repeated and which checks are unit or E2E tests.
- Define separate, visible unit and E2E selections and results, so a routine final test run executes unit tests without implicitly launching the full E2E suite.
- Specify explicit conditions that require E2E execution, based on the accepted work and its acceptance criteria or risk. Do not silently omit E2E coverage when it is required.
- Record whether E2E checks ran and, when they did not, the applicable reason or accepted not-applicable evidence. Keep required non-test verification checks intact.
- Validate the behavior with examples where E2E is required and where it is not, including a workstream that already ran task-scoped tests before final project-wide verification.

## Note

This card proposes an investigation and workflow change. It does not authorize changing the current verification contract or skipping checks in active work.

Related card: `.later/agent-decision-clarity.md` addresses broader workflow and verification boundaries, but does not define the unit/E2E split or the conditional E2E rule.
