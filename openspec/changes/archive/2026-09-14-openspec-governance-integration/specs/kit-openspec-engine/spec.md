## Purpose
Pinned OpenSpec CLI as the specification and planning engine for marked kit
pilots, with kit commands remaining the only promoted surface.

## ADDED Requirements

### Requirement: Pilot marker
A workstream SHALL be an OpenSpec pilot if and only if `work/<work-id>/intent.md`
contains a line matching `^Engine:\s*openspec\s*$`. Absence SHALL mean the
workstream is not a pilot. Non-pilot workstreams MUST keep today's
`check-workstream`, `status`, and `verify` behavior, including
`_ask/tests/test-workstream-smoke.sh`. `openspec-governance-integration` SHALL
be a marked pilot.

#### Scenario: Marked pilot
- **WHEN** `work/<id>/intent.md` contains `Engine: openspec`
- **THEN** kit gates evaluate the matching OpenSpec change for that id

#### Scenario: Non-pilot
- **WHEN** that line is absent
- **THEN** `check-workstream` does not require OpenSpec

### Requirement: Command surface
Kit commands and stage names SHALL remain the documented default entry points.
Default setup MUST leave the repo with no OpenSpec-generated command or skill
files. When kit commands print OpenSpec CLI output, they MUST strip or relabel
`nextSteps` and other fields that recommend `openspec …` as the next user
action. Direct OpenSpec CLI access SHALL remain possible as an advanced
interface.

#### Scenario: No generated commands after setup
- **WHEN** default OpenSpec setup has run (`init --tools none`)
- **THEN** listing `.cursor/commands` and `.cursor/skills` shows no
  OpenSpec-generated command or skill files

### Requirement: Artifact ownership
OpenSpec SHALL own the change directory `openspec/changes/<work-id>/` (including
`.openspec.yaml`). After deltas apply, `openspec/specs/` SHALL be the canonical
behavioral specifications for pilot scope. For a marked pilot, `work/<id>/plan.md`
MUST be a non-normative pointer to that change's `design.md` and `tasks.md`.
`specs/current/<id>.md` and `specs/proposals/<id>.md` MAY exist as pointers
(Status, one link, no Goal / Behavior / Acceptance criteria). Meaningful
duplicate requirements or plan content MUST be a failure. `openspec/` SHALL be
consumer-owned engineering state, same class as `specs/` and `work/`.

#### Scenario: Pointer plan
- **WHEN** a marked pilot has OpenSpec design and tasks
- **THEN** kit `plan.md` contains no meaningful Approach or Work-breakdown

### Requirement: Shared identity
The `./ask start-work` argument SHALL be used verbatim for `agent/<work-id>`,
`openspec/changes/<work-id>/`, and `work/<work-id>/`. Gates MUST fail closed when
no active OpenSpec change matches, or when more than one active change matches.
After openspec-archive, lookup SHALL use
`openspec/changes/archive/<date>-<work-id>/`. A missing active directory after
a valid Accept MUST NOT be reported as a missing-change failure.

#### Scenario: Verbatim work-id
- **WHEN** start-work is invoked with `openspec-governance-integration`
- **THEN** the OpenSpec change directory name is exactly that string

### Requirement: Targeted gates
`./ask check-workstream <work-id>` SHALL enforce OpenSpec gates for marked
pilots using targeted invocations only (`openspec validate <id> --strict` and
`openspec status --change <id>`). `--all` forms MUST NOT be used as gate
inputs. Invalid JSON, `root: null`, or any `status[].severity` equal to
`error` MUST be a failure regardless of process exit code. For a marked pilot,
`check-workstream` MUST fail when the matching change is missing, incomplete,
or invalid, even if unrelated specifications exist. Incomplete SHALL mean
`isPlanningComplete` false, or `isComplete` false, or any
`artifacts[].status` of `blocked`. Invalid SHALL mean targeted validate
non-zero or JSON `valid: false` on the matching item. A marked pilot on a
clean dedicated branch with a valid complete OpenSpec change and required kit
governance files MUST pass. `skip_specs: true` SHALL be allowed only with a
recorded reason in the change proposal, and MUST NOT be the evidence that
strict validation ran for a behavioral-delta pilot.

#### Scenario: Missing change fails
- **WHEN** a marked pilot has no matching OpenSpec change
- **THEN** `check-workstream` exits non-zero even if `specs/current/` has other files

#### Scenario: Non-pilot smoke still passes
- **WHEN** `test-workstream-smoke.sh` runs a work-id without `Engine: openspec`
- **THEN** it passes without an OpenSpec directory

### Requirement: Status checkout scope
`./ask status` MUST NOT check out another branch. For the current checkout, if
HEAD is `agent/<id>` or the tree contains that change and the work-id is a
marked pilot, status SHALL read OpenSpec machine-readable CLI for that id
only. Other live refs MUST use `git show <ref>:…` of `openspec/changes/<id>/`
and `work/<id>/`. A marked pilot with meaningful OpenSpec design or tasks
SHALL count as planned even when kit `plan.md` is only a pointer.
`code-without-plan` MUST treat `openspec/` for that work-id as a recognized
prefix, same class as `work/<id>/` and `specs/`. Surfaced CLI output MUST NOT
recommend OpenSpec commands as the default next action.

#### Scenario: Pointer plan is planned
- **WHEN** kit `plan.md` is a pointer and OpenSpec `tasks.md` is meaningful
- **THEN** `./ask status` reports stage `planned` for that work-id

### Requirement: Verify work-id
`./ask verify` SHALL take `--work-id`, write `work/<id>/verification.json`
using `_ask/templates/verification.json`, refuse a dirty tree, and record the
commit SHA it ran against. For a marked pilot, verification MUST include
targeted strict OpenSpec validation plus configured project checks.
Pre-existing schema drift in `specs/current/promote-kit-specs.md` MUST stay
unfixed here except that this workstream's evidence lands in
`work/<id>/verification.json`.

#### Scenario: Dirty refuse
- **WHEN** `./ask verify --work-id <id>` runs on a dirty tree
- **THEN** it exits non-zero and does not write a passing evidence file claiming a clean commit

### Requirement: openspec-archive
Kit-mediated openspec-archive SHALL refuse unless `work/<id>/acceptance.md`
contains an accepted commit SHA. Direct `openspec archive` remains possible.
After the fact, kit `status`, `verify`, and `check-workstream` MUST detect an
openspec-archived change with no matching Accept SHA and fail.
`./ask status` `life: archived` SHALL keep its current meaning. `04 Spec Change`
on a work-id whose change is already openspec-archived SHALL create a new
active `openspec/changes/<id>/` and record it in intent.

#### Scenario: Refuse before Accept
- **WHEN** `./ask openspec-archive <id>` runs and acceptance.md has no commit SHA
- **THEN** the command exits non-zero and does not move the change directory

### Requirement: Pin and install
The OpenSpec CLI SHALL be pinned like `_ask/skills/manifest.yaml`: explicit
revision, never `latest`, fail-closed version assertion before gated commands.
Agents MUST NOT act on the CLI's `npm install … @latest` advice. Schema and
profile SHALL be pinned (`spec-driven`, `core` on 1.13.0). `install-kit.sh`
MUST NOT require Node or OpenSpec. When a marked pilot is in play and the
executable is missing or the version does not match the pin, gated kit
commands MUST fail closed. An ADR SHALL record the dependency and top-level
`openspec/` path against ADR-0011.

#### Scenario: Missing binary
- **WHEN** a marked-pilot gated command runs and OpenSpec is missing
- **THEN** the command exits non-zero

### Requirement: Baseline and later evaluation
This workstream SHALL Accept on machinery plus a recorded pre-change baseline
of the current kit flow. The adopt / revise / abandon evaluation after two or
three later representative changes MUST be a separate workstream. Those later
pilots SHALL be serialized per `_ask/policies/worktree.md` when they touch
`openspec/specs/` or shared gates. If a marked pilot is dropped, or the later
evaluation returns abandon, canonical behavioral specs that exist only under
`openspec/specs/` MUST be copied back to `specs/current/` before OpenSpec is
removed from that scope, owned by the workstream that decides abandon.

#### Scenario: Accept does not wait on later pilots
- **WHEN** machinery plus baseline are recorded
- **THEN** this workstream may Accept without two or three evaluation pilots completing
