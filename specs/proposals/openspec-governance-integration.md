# Specification: OpenSpec as an Internal Kit Engine

## Status

CURRENT

## Goal

Use a pinned OpenSpec CLI as the artifact and lifecycle engine for change
proposals, behavioral specifications, deltas, design, tasks, structural
validation, synchronization, and openspec-archive while preserving the kit as
the only promoted command surface.

Retain the kit's governance responsibilities: intent clarification, Git and
worktree safety, risk and delegation policy, independent review, finding
disposition, claim-appropriate verification, commit-linked provenance, and
explicit acceptance.

This work-id (`openspec-governance-integration`) is a marked OpenSpec dogfood
pilot of that split. Accept this workstream on the machinery plus a recorded
baseline of the current kit flow. The adopt / revise / abandon evaluation after
two or three later representative changes is a separate workstream.

## Non-goals

- Replace the complete kit workflow with OpenSpec.
- Promote OpenSpec-generated slash commands or skills as a second default flow.
- Hide or prevent direct use of the OpenSpec CLI for advanced operation,
  diagnosis, or recovery.
- Treat structural OpenSpec validation as proof of semantic correctness,
  implementation quality, security, performance, or acceptance.
- Treat openspec-archive as an acceptance decision.
- Migrate every existing kit specification before the first marked pilot.
- Maintain synchronized OpenSpec and kit copies of the same active
  requirements or plan.
- Define a custom OpenSpec schema before the later evaluation workstream
  decides.
- Require Node or OpenSpec on `install-kit.sh` for non-pilot consumers.
- Block this workstream's Accept on two or three future evaluation pilots.
- Check out another branch from `./ask status` in order to run the OpenSpec
  CLI.

## Behavior

### Pilot marker

A workstream is an OpenSpec pilot if and only if `work/<work-id>/intent.md`
contains a line matching:

```text
^Engine:\s*openspec\s*$
```

Absence means not a pilot. Non-pilot workstreams keep today's
`check-workstream`, `status`, and `verify` behavior, including
`_ask/tests/test-workstream-smoke.sh`.

`openspec-governance-integration` is a marked pilot.

### Command surface

Kit commands and stage names remain the documented default entry points.
OpenSpec commands may be documented as an internal or advanced interface, but
must not appear as an equivalent recommended workflow.

Default setup must leave the repo with no OpenSpec-generated command or skill
files (end-state listing, not a forever-asserted init flag). OpenSpec remains
callable as a CLI by kit stages and by a human who deliberately uses the
advanced interface.

When kit commands print OpenSpec CLI output, strip or relabel `nextSteps` and
other fields that recommend `openspec …` as the next user action.

### Artifact ownership

OpenSpec owns the change **directory** for each marked pilot:

```text
openspec/changes/<work-id>/
```

That directory includes `.openspec.yaml`, `proposal.md`, `specs/`, `design.md`,
`tasks.md`, and any other files the pinned CLI writes there.

OpenSpec's main specifications under `openspec/specs/` are the canonical
behavioral specifications for pilot scope after the change's deltas apply.

The kit continues to own governance and evidence artifacts:

```text
work/<work-id>/intent.md
work/<work-id>/spec-challenge.md
work/<work-id>/plan.md
work/<work-id>/review.md
work/<work-id>/verification.json
work/<work-id>/acceptance.md
work/<work-id>/result.json
```

For a marked pilot, `work/<work-id>/plan.md` is a non-normative pointer to
`openspec/changes/<work-id>/design.md` and `tasks.md`. Meaningful Approach or
Work-breakdown content in that file is a duplicate.

For a marked pilot, `specs/current/<work-id>.md` and
`specs/proposals/<work-id>.md` may exist as non-normative pointers (Status, one
link to the OpenSpec change, no Goal / Behavior / Acceptance criteria).
Meaningful requirements there are a duplicate.

An active marked pilot must not carry a second copy of the *requirements* under
`specs/proposals/` or `specs/current/`. Existing files there remain legacy
history for non-pilot work, and pointer files for marked pilots.

`openspec/` is consumer-owned engineering state, same class as `specs/` and
`work/` in `_ask/OWNED-PATHS.md`.

### Shared identity

The `./ask start-work` argument is the work ID, used verbatim for:

- `agent/<work-id>`
- `openspec/changes/<work-id>/`
- `work/<work-id>/`
- verification, acceptance, and result records

No extra normalization. Fail closed when no active OpenSpec change matches, or
when more than one active change matches.

After openspec-archive, the active path `openspec/changes/<work-id>/` is gone.
The lookup path is `openspec/changes/archive/<date>-<work-id>/` (date from the
tool). A missing active directory after a valid Accept is not a missing-change
failure.

`04 Spec Change` on a work-id whose change is already openspec-archived creates
a new active `openspec/changes/<work-id>/`. The archived copy stays under
`archive/`. Record the new change in intent.

Kit status and precondition checks for a marked pilot evaluate the matching
OpenSpec change, not an unrelated accepted specification.

### Lifecycle mapping

The logical kit stages remain stable:

1. `00 Explore` and `01 Grill` remain kit-owned.
2. `02 Spec` creates or updates the matching OpenSpec proposal and behavioral
   delta, then runs targeted strict OpenSpec validation.
3. `03 Spec Challenge` challenges the OpenSpec proposal and behavioral
   specification against intent.
4. `04 Spec Change` changes semantics through the active OpenSpec change and
   deltas; it does not silently rewrite canonical specifications.
5. `05 Plan` produces OpenSpec design and task artifacts. Kit `plan.md` is the
   pointer described under Artifact ownership.
6. `06 Implement` applies the OpenSpec tasks through the kit stage.
7. `07 Review` and `08 Refactor` retain kit finding and disposition semantics.
8. `09 Verify` combines targeted OpenSpec structural validation with
   deterministic, project-specific checks against a clean commit.
9. `10 Accept` records the decision, evidence, unresolved findings, and exact
   commit.
10. Kit-mediated openspec-archive occurs after kit acceptance. Earlier
    synchronization requires an explicit dependency reason and must not imply
    acceptance.

openspec-archive is lifecycle finalization, not an acceptance decision.

### This workstream's cutover

Until a named cutover commit, this work-id may keep a complete CURRENT kit spec
under `specs/` so the workstream is not spec-less mid-change.

Cutover steps:

1. Initialize OpenSpec structure-only in this repo.
2. Create `openspec/changes/openspec-governance-integration/` and copy the
   behavioral requirements from the CURRENT kit spec into OpenSpec proposal,
   deltas, design, and tasks.
3. Replace both kit spec copies with pointer files.
4. Replace `work/openspec-governance-integration/plan.md` with a pointer.

After cutover, OpenSpec artifacts are the specification and planning source of
truth for this work-id.

### Dependency and generated-file ownership

The OpenSpec CLI is pinned like `_ask/skills/manifest.yaml`: explicit revision,
never `latest`, fail-closed version assertion before gated commands. Agents
must not act on the CLI's `npm install … @latest` advice. Pin schema and
profile as well as version when the pinned release still has global-only
`openspec config`.

`install-kit.sh` does not require Node or OpenSpec. Non-pilot consumers stay
bash/python. When a marked pilot is in play and the executable is missing or
the version does not match the pin, gated kit commands fail closed.

Kit generation continues to own its existing `.cursor`, `.claude`, and `.codex`
projections. Default OpenSpec setup must result in no competing command or
skill files.

If OpenSpec-generated adapters are evaluated later, each generator must have
disjoint owned paths and tests must prove that either update process preserves
the other's files.

Record an ADR for the OpenSpec dependency and the new top-level `openspec/`
path against ADR-0011.

### Pilot migration

Before a marked pilot change starts, copy only the existing behavioral
specifications that the change depends on into `openspec/specs/`. Record the
legacy source and the copied OpenSpec destination in the change proposal.

The pilot must not rewrite, delete, or bulk-convert unrelated legacy
specifications.

If a marked pilot is dropped, or the later evaluation returns abandon,
canonical behavioral specs that exist only under `openspec/specs/` are copied
back to `specs/current/` before OpenSpec is removed from that scope. Owner:
the workstream that decides abandon.

### Gates

Enforced in `./ask check-workstream <work-id>`, not only in prose.

Gating uses targeted per-work-id invocations only:

```text
openspec validate <work-id> --strict
openspec status --change <work-id>
```

`--all` forms are forbidden as gate inputs.

Treat as failure regardless of process exit code: invalid JSON, `root: null`,
or any `status[].severity` equal to `error`.

For a marked pilot, `check-workstream` fails when the matching OpenSpec change
is missing, incomplete, or invalid, even if unrelated specifications exist.

Incomplete and invalid are machine fields from those targeted invocations
(re-measure names on the pinned release):

- invalid: targeted `openspec validate <id> --strict` non-zero, or JSON with
  `valid: false`
- incomplete: `isPlanningComplete` false, or `isComplete` false, or any
  `artifacts[].status` of `blocked`

Empty-set success (bulk validate with zero items, or list with `root: null`)
is a failure if used as a gate input.

Pass path: a marked pilot on a clean dedicated `agent/<work-id>` branch, with a
valid complete OpenSpec change and the required kit governance files, reaches
implementation eligibility.

`skip_specs: true` in `.openspec.yaml` is allowed only with a recorded reason
in the change proposal. It must not be the evidence that strict validation ran
for a pilot whose purpose includes behavioral deltas.

### Status

`./ask status` must not check out another branch.

- **Current checkout:** if HEAD is `agent/<work-id>` or the tree contains that
  change, and the work-id is a marked pilot, read OpenSpec machine-readable CLI
  for that id only.
- **Other live refs:** `git show <ref>:…` of `openspec/changes/<id>/` and
  `work/<id>/`. Do not invoke the OpenSpec CLI against a foreign worktree.
- **Stage:** a marked pilot with meaningful OpenSpec design or tasks counts as
  planned even when kit `plan.md` is only a pointer.
- **`code-without-plan`:** `openspec/` for that work-id is a recognized prefix,
  same class as `work/<id>/` and `specs/`.

### openspec-archive

Kit-mediated openspec-archive refuses unless `work/<work-id>/acceptance.md`
contains an accepted commit SHA.

Direct `openspec archive` remains possible. After the fact, kit `status`,
`verify`, and `check-workstream` detect an openspec-archived change with no
matching Accept SHA and fail.

`./ask status` `life: archived` keeps its current meaning (work-id on the
default branch, no unmerged `agent/*`). Do not reuse the bare word "archive"
for the OpenSpec operation in this specification.

### Verify

`./ask verify` takes `--work-id`, writes `work/<work-id>/verification.json`
using `_ask/templates/verification.json`, refuses a dirty tree (same class as
`record-run.sh`), and records the commit SHA it ran against.

For a marked pilot, verification includes targeted strict OpenSpec validation
plus configured project checks.

Pre-existing verification schema drift recorded in
`specs/current/promote-kit-specs.md` stays unfixed here except that this
workstream's evidence lands in `work/<work-id>/verification.json`.

### Baseline and later evaluation

Before the switch, record a baseline of the current kit flow using:

- time spent producing and maintaining artifacts
- duplicated or contradictory information
- missed or ambiguous requirements
- semantic-change handling
- agent adherence to the intended command surface
- review and verification quality
- merge conflicts
- readability of current specifications and archived history

This workstream Accepts on machinery plus that baseline.

After two or three later representative marked-pilot changes, a **later**
workstream compares the integrated flow with that baseline and records adopt,
revise, or abandon. Those later pilots are serialized per
`_ask/policies/worktree.md` when they touch `openspec/specs/` or shared gates.
This dogfood work-id is not one of those evaluation changes unless that later
workstream says so.

Park the evaluation workstream at cutover if it is not already in `.later/`.

## Interfaces

- Existing kit stage commands and generated runtime bindings
- Pinned `openspec` executable
- OpenSpec machine-readable status, validation, and instruction output
- `openspec/changes/<work-id>/`
- `openspec/changes/archive/<date>-<work-id>/`
- `openspec/specs/`
- `work/<work-id>/`
- `./ask start-work`
- `./ask check-workstream`
- `./ask status`
- `./ask verify --work-id`
- `./ask record-result`

## Constraints

- The visible kit command surface must remain backward-compatible during the
  dogfood pilot and for non-pilot workstreams.
- OpenSpec subprocess failures, invalid JSON, missing artifacts, failed strict
  validation, `root: null`, and `status[].severity: "error"` must be reported
  as failures rather than interpreted as successful state.
- Existing clean-tree, dedicated-branch, stepwise-commit, and no-silent-spec-
  change policies remain in force.
- A marked pilot must have one specification source of truth for requirements
  and plan (OpenSpec), with kit pointer files allowed.
- Verification evidence must identify the clean Git commit it covers.
- Human authority requirements continue to follow kit risk and delegation
  policy. Rewriting `check-workstream`, `status`, or `verify` is an escalation
  point in 05 Plan.
- Direct OpenSpec CLI access remains possible; kit-mediated openspec-archive
  is the normal path, detection covers the direct path.

## Invariants

- OpenSpec owns specification and planning state for a marked pilot change.
- The kit owns governance and acceptance state.
- No generated `/opsx-*` command is required for normal kit operation.
- Direct OpenSpec CLI access remains possible.
- OpenSpec validation never substitutes for Spec Challenge, Review, project
  verification, or Accept.
- Kit-mediated openspec-archive never precedes acceptance in the normal flow.
- Existing specifications outside a marked pilot's dependencies remain
  untouched.
- Non-pilot workstreams do not require OpenSpec.

## Failure cases

- Agents see kit and OpenSpec commands presented as competing default
  workflows, including via unfiltered CLI `nextSteps`.
- A marked pilot writes equivalent active requirements under both `specs/` and
  `openspec/`.
- `check-workstream` passes because an unrelated specification exists.
- `check-workstream` fails a non-pilot because OpenSpec is absent.
- An OpenSpec update changes generated kit bindings or an agent follows
  printed `@latest` upgrade advice.
- A malformed OpenSpec command, empty-set `--all` success, or exit-0 JSON with
  `severity: "error"` is treated as success.
- openspec-archive is used as evidence of human acceptance.
- Direct openspec-archive without Accept SHA is not detected.
- Verification records a commit while testing uncommitted code.
- A marked pilot migrates unrelated historical specifications.
- The integration keeps custom kit spec machinery without a demonstrated need.
- `./ask status` checks out another branch to run the OpenSpec CLI.
- A compliant marked pilot is reported as `code-without-plan` because
  `openspec/` is unrecognized.
- After valid Accept and openspec-archive, kit gates fail because the active
  change directory is gone.
- `skip_specs: true` is used as the proof that strict validation ran for a
  behavioral-delta pilot.

## Acceptance criteria

- A clean consumer-repository installation exposes the kit's documented command
  surface and no promoted OpenSpec command surface. After default setup, no
  OpenSpec-generated command or skill file is present.
- The pinned OpenSpec CLI remains directly callable. Gated commands fail closed
  on missing executable or version mismatch for a marked pilot. `install-kit.sh`
  does not require Node or OpenSpec.
- A marked-pilot workstream creates one matching OpenSpec change directory.
  Kit `plan.md` and optional `specs/` files for that id are pointers with no
  meaningful duplicate requirements or plan.
- Targeted strict OpenSpec validation runs in `check-workstream` before
  implementation eligibility for marked pilots.
- `./ask check-workstream <work-id>` for a marked pilot fails when the matching
  OpenSpec change is missing, incomplete, or invalid, even if unrelated
  specifications exist. Non-pilots, including `test-workstream-smoke.sh`, keep
  today's behavior.
- A marked pilot on a clean dedicated branch with a valid complete OpenSpec
  change and required kit governance files passes `check-workstream`.
- `./ask status` reports OpenSpec CLI state only for the current checkout's
  matching marked-pilot change. Other live refs use `git show`. Stage and
  `code-without-plan` recognize OpenSpec artifacts. Surfaced CLI output does
  not recommend OpenSpec commands as the default next action.
- The kit's sync and OpenSpec setup/update operations preserve each other's
  owned files.
- Only specifications required by a marked pilot are copied from the legacy
  tree, and every copy records its source and destination.
- Review findings retain `FIX`, `ACCEPT WITH RATIONALE`, and `ESCALATE`
  disposition behavior.
- `./ask verify --work-id <id>` refuses a dirty tree, writes
  `work/<id>/verification.json`, runs targeted strict OpenSpec validation and
  configured project checks against that commit, and records the commit.
- Accept retains unresolved findings and human-authority decisions.
- Kit-mediated openspec-archive is refused until kit acceptance exists.
  Out-of-order direct archive is detected. Post-openspec-archive lookup uses
  `openspec/changes/archive/<date>-<id>/`.
- This workstream records a pre-change baseline and Accepts on machinery plus
  that baseline. The two-or-three-change adopt / revise / abandon evaluation is
  a later workstream.
- `_ask/OWNED-PATHS.md` lists `openspec/` as consumer-owned. An ADR records the
  dependency and the top-level path.
- Existing kit tests pass, and new tests cover command visibility, source-of-
  truth exclusivity, work-ID matching, generator coexistence, targeted
  validation failures, empty-set and exit-0-with-error payloads, clean-commit
  verification, openspec-archive ordering and detection, the intent marker,
  pointer-form duplicates, and non-pilot backward compatibility.

## Open questions

- Select the exact OpenSpec release during planning, then pin it.
- Name the later evaluation workstream and its two or three representative
  changes when that workstream starts.

## Source intent

`work/openspec-governance-integration/intent.md`

## Source challenge

`work/openspec-governance-integration/spec-challenge.md`

## Source spec change

`work/openspec-governance-integration/spec-change.md`
