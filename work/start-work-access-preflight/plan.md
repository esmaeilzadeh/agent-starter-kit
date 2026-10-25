# Plan

## Specification

`specs/current/start-work-access-preflight.md` (CURRENT).

## Approach

Implement one shared probe command, call it before `start-work` mutations, and
wire session start/resume entrypoints for supported bundles with a portable
instruction fallback.

## Work breakdown

Break implementation into reviewable tasks before coding. Use one row per
cohesive outcome; one task is valid when the work is a single deliverable, with
the reason recorded. Keep IDs aligned with `inner-loop/tasks.yaml` and
`test-plan.json`'s `task_scopes`.

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| ACCESS-1 | Shared local write preflight and start/session wiring | none | `_ask/scripts/access-check.sh`, `_ask/scripts/start-work.sh`, `./ask`, `.cursor/**`, `.codex/**`, `.claude/**`, `.opencode/**`, `AGENTS.md`, `_ask/tests/test_access_check.py` | ACC-T1, ACC-T2, ACC-T3, ACC-T4, ACC-T5 | focused Red → Green → Refactor, independent review, `./ask verify` |

One task is appropriate because the command and its entrypoint adapters form
one user-visible guard; splitting them would leave the check unavailable or
unwired between commits.

Assign every planned test case to its responsible task. Give tasks without an
executable test a specific verification rationale. Create
`work/<work-id>/inner-loop/tasks.yaml` from `_ask/templates/inner-loop-tasks.yaml`.

## Risks

Runtime lifecycle hooks differ in whether they can block; adapters must expose
failure as a clear stop condition, with portable instructions as fallback.

## Verification approach

Run the five mapped unittest cases through the public CLI/runtime config seams,
then run `./ask verify`.

## Out of scope for this plan

Remote credentials, network checks, and permission repair.

## E2E

Map the spec’s E2E contract to tooling and isolation, or `not_applicable` plus reason.
Missing E2E with no reason refuses this plan.

Applicable: temporary Git repositories and isolated config fixtures; remove
all temporary repositories and fixtures after each case.
