# Specification Change Proposal: bind accepted cases to implemented test selectors

## Current specification

The accepted test plan at contract `18c3c34c74e620b46588ff8d0b0e27089b40ecd3`
defines the existing seven EM criteria and 26 required test obligations. Three
UI entries still point at placeholder test module/class names that do not exist
in the implementation. A clean `./ask verify` therefore stops before tests with
`candidate changed accepted obligations; reviewed amendment required` when the
correct implementation selectors are supplied.

## Proposed change

Change only the `case_id` and `source_paths` bindings for `UI-inspect`,
`UI-conflict`, and `UI-browser` in `work/structured-agentic-environment/test-plan.json`
to name the implemented AppTest/browser cases and their actual source files.
Keep criterion IDs, test types, scenarios, assertions, runner definitions,
obligations, and all feature acceptance criteria unchanged.

## Why the change is needed

The accepted bindings refer to nonexistent selectors (`test_engineering_browser`
and UI methods absent from the repository). The implementation now has matching
real journeys, but Verify correctly refuses to treat a changed plan as accepted
without independent review and a new accepted pin. Restoring the obsolete names
would make the browser/UI obligations unexecutable and conceal rather than solve
the mismatch.

## Impacted artifacts

- `work/structured-agentic-environment/test-plan.json` — three selector/path
  bindings only.
- `work/structured-agentic-environment/traceability-accepted.json` and the
  coordinator-owned `refs/ask/accepted-tests/structured-agentic-environment`
  pin — new reviewed digest if approved.
- Candidate Verify/result evidence must be rerun against the resulting exact
  commit.

## Impacted workstreams

Only `structured-agentic-environment`. No other workstream, criterion, test
obligation, policy, implementation interface, or product behavior changes.

## Migration / transition notes

Retain the current accepted contract and rejected Verify attempt as history.
If approved, independently review the binding-only plan revision, record a new
accepted pin through the traceability coordinator, validate the plan, then rerun
the full exact-candidate Verify. Do not edit the accepted ref directly.

## Acceptance criteria for the change

1. Independent review confirms the three selectors exist and exercise the same
   already-accepted assertions and behavior.
2. A coordinator operation accepts the revised digest without changing the
   seven EM criteria, 26 obligations, case assertions, or runner policy.
3. Full Verify collects and executes every accepted case on the exact candidate.

## Decision

PENDING HUMAN CONFIRMATION. No revised accepted-plan pin has been written.
