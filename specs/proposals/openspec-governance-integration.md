# Specification: OpenSpec as an Internal Kit Engine

## Status

CURRENT

## Goal

Use a pinned OpenSpec CLI as the artifact and lifecycle engine for change
proposals, behavioral specifications, deltas, design, tasks, structural
validation, synchronization, and archive while preserving the kit as the only
promoted command surface.

Retain the kit's governance responsibilities: intent clarification, Git and
worktree safety, risk and delegation policy, independent review, finding
disposition, claim-appropriate verification, commit-linked provenance, and
explicit acceptance.

Validate the integration through two or three pilot changes before deciding
whether to adopt a custom OpenSpec schema or remove legacy kit machinery.

## Non-goals

- Replace the complete kit workflow with OpenSpec.
- Promote OpenSpec-generated slash commands or skills as a second default flow.
- Hide or prevent direct use of the OpenSpec CLI for advanced operation,
  diagnosis, or recovery.
- Treat structural OpenSpec validation as proof of semantic correctness,
  implementation quality, security, performance, or acceptance.
- Migrate every existing kit specification before the pilot.
- Maintain synchronized OpenSpec and kit copies of the same active
  specification or plan.
- Define a custom OpenSpec schema before standard artifacts are evaluated.
- Implement the integration during stages 01 or 02.

## Behavior

### Command surface

Kit commands and stage names remain the documented default entry points.
OpenSpec commands may be documented as an internal or advanced interface, but
must not appear as an equivalent recommended workflow.

Default setup must not generate OpenSpec tool-specific commands or skills.
OpenSpec remains callable as a CLI by kit stages and by a human who deliberately
uses the advanced interface.

### Artifact ownership

For each pilot work ID, OpenSpec owns:

```text
openspec/changes/<work-id>/proposal.md
openspec/changes/<work-id>/specs/
openspec/changes/<work-id>/design.md
openspec/changes/<work-id>/tasks.md
```

OpenSpec's main specifications under `openspec/specs/` are the canonical
behavioral specifications for pilot scope.

The kit continues to own governance and evidence artifacts:

```text
work/<work-id>/intent.md
work/<work-id>/spec-challenge.md
work/<work-id>/review.md
work/<work-id>/verification.json
work/<work-id>/acceptance.md
work/<work-id>/result.json
```

An active pilot change must not have a second specification under
`specs/proposals/` or `specs/current/`. Existing files there remain legacy
history during the pilot.

### Shared identity

The same normalized work ID identifies:

- `agent/<work-id>`
- `openspec/changes/<work-id>/`
- `work/<work-id>/`
- verification, acceptance, and result records

Kit status and precondition checks must evaluate the matching OpenSpec change,
not an unrelated accepted specification.

### Lifecycle mapping

The logical kit stages remain stable:

1. `00 Explore` and `01 Grill` remain kit-owned.
2. `02 Spec` creates or updates the matching OpenSpec proposal and behavioral
   delta, then runs strict OpenSpec validation.
3. `03 Spec Challenge` challenges the OpenSpec proposal and behavioral
   specification against intent.
4. `04 Spec Change` changes semantics through the active OpenSpec change and
   deltas; it does not silently rewrite canonical specifications.
5. `05 Plan` produces OpenSpec design and task artifacts.
6. `06 Implement` applies the OpenSpec tasks through the kit stage.
7. `07 Review` and `08 Refactor` retain kit finding and disposition semantics.
8. `09 Verify` combines OpenSpec structural validation with deterministic,
   project-specific checks against a clean commit.
9. `10 Accept` records the decision, evidence, unresolved findings, and exact
   commit.
10. OpenSpec archive occurs after kit acceptance. Earlier synchronization
    requires an explicit dependency reason and must not imply acceptance.

OpenSpec archive is lifecycle finalization, not an acceptance decision.

### Dependency and generated-file ownership

The OpenSpec CLI must be pinned to an explicit supported version. Setup and
automation must not silently upgrade that version.

Kit generation continues to own its existing `.cursor`, `.claude`, and `.codex`
projections. Default OpenSpec setup must use structure-only delivery so it does
not generate competing command or skill files.

If OpenSpec-generated adapters are evaluated later, each generator must have
disjoint owned paths and tests must prove that either update process preserves
the other's files.

### Pilot migration

Before a pilot change starts, copy only the existing behavioral specifications
that the change depends on into `openspec/specs/`. Record the legacy source and
the copied OpenSpec destination in the change proposal.

The pilot must not rewrite, delete, or bulk-convert unrelated legacy
specifications.

### Pilot evaluation

After two or three representative changes, compare the integrated flow with the
current kit flow using:

- time spent producing and maintaining artifacts
- duplicated or contradictory information
- missed or ambiguous requirements
- semantic-change handling
- agent adherence to the intended command surface
- review and verification quality
- merge conflicts
- readability of current specifications and archived history

The evaluation must produce an explicit adopt, revise, or abandon decision
before broader migration.

## Interfaces

- Existing kit stage commands and generated runtime bindings
- Pinned `openspec` executable
- OpenSpec machine-readable status, validation, and instruction output
- `openspec/changes/<work-id>/`
- `openspec/specs/`
- `work/<work-id>/`
- `./ask start-work`
- `./ask check-workstream`
- `./ask status`
- `./ask verify`
- `./ask record-result`

## Constraints

- The visible kit command surface must remain backward-compatible during the
  pilot.
- OpenSpec subprocess failures, invalid JSON, missing artifacts, and failed
  strict validation must be reported as failures rather than interpreted as
  successful state.
- Existing clean-tree, dedicated-branch, stepwise-commit, and no-silent-spec-
  change policies remain in force.
- A pilot must have one specification source of truth.
- Verification evidence must identify the clean Git commit it covers.
- Human authority requirements continue to follow kit risk and delegation
  policy.

## Invariants

- OpenSpec owns specification and planning state for a pilot change.
- The kit owns governance and acceptance state.
- No generated `/opsx-*` command is required for normal kit operation.
- Direct OpenSpec CLI access remains possible.
- OpenSpec validation never substitutes for Spec Challenge, Review, project
  verification, or Accept.
- Archive never precedes acceptance in the normal flow.
- Existing specifications outside pilot dependencies remain untouched.

## Failure cases

- Agents see kit and OpenSpec commands presented as competing default workflows.
- A pilot writes equivalent active requirements under both `specs/` and
  `openspec/`.
- `check-workstream` passes because an unrelated specification exists.
- An OpenSpec update changes generated kit bindings or silently upgrades the
  pinned CLI.
- A malformed or failed OpenSpec command is treated as success.
- OpenSpec archive is used as evidence of human acceptance.
- Verification records a commit while testing uncommitted code.
- The pilot migrates unrelated historical specifications.
- The integration keeps custom kit spec machinery without a demonstrated need.

## Acceptance criteria

- A clean consumer-repository installation exposes the kit's documented command
  surface and no promoted OpenSpec command surface.
- The pinned OpenSpec CLI remains directly callable.
- A pilot workstream creates one matching OpenSpec change and no duplicate kit
  specification or plan.
- Strict OpenSpec validation runs before implementation eligibility.
- `./ask check-workstream <work-id>` fails when the matching OpenSpec change is
  missing, incomplete, or invalid, even if unrelated specifications exist.
- `./ask status` reports state for the matching OpenSpec change through
  machine-readable CLI output.
- The kit's sync and OpenSpec setup/update operations preserve each other's
  owned files.
- Only specifications required by a pilot are copied from the legacy tree, and
  every copy records its source and destination.
- Review findings retain `FIX`, `ACCEPT WITH RATIONALE`, and `ESCALATE`
  disposition behavior.
- Verification runs strict OpenSpec validation and configured project checks
  against a clean commit, recording that commit.
- Accept retains unresolved findings and human-authority decisions.
- Normal archive is blocked until kit acceptance exists.
- Two or three pilot changes produce a recorded adopt, revise, or abandon
  evaluation using the specified measures.
- Existing kit tests pass, and new tests cover command visibility, source-of-
  truth exclusivity, work-ID matching, generator coexistence, validation
  failures, clean-commit verification, and archive ordering.

## Open questions

- Select the exact OpenSpec release during planning, then pin it.
- Select the two or three representative pilot changes.
- Decide after the pilot whether a custom OpenSpec schema should co-locate kit
  governance artifacts inside each OpenSpec change.

## Source intent

`work/openspec-governance-integration/intent.md`
