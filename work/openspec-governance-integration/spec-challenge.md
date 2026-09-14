# Specification Challenge

## Model

- model: claude-opus-5
- runtime: cursor
- parent_model: grok-4.6

## Specification

- Specification: `specs/current/openspec-governance-integration.md` (Status CURRENT)
- Source intent: `work/openspec-governance-integration/intent.md` (Risk: HIGH)
- Branch at challenge time: `agent/openspec-governance-integration`, clean tree

Challenged against kit machinery as it exists, not against OpenSpec claims:
`_ask/scripts/check-workstream.sh`, `status.sh`, `verify.sh`, `record-result.sh`,
`start-work.sh`, `sync-cursor-binding.sh`, `_ask/tests/`, `_ask/OWNED-PATHS.md`,
`_ask/policies/{workflow,worktree,verification,delegation}.md`,
`_ask/agents/{05-plan,09-verify,10-accept}.md`.

CLI behavior below was measured, not assumed. Reproduction: `openspec 1.12.0`
(global npm install; 1.13.0 already published), scratch git repo, `openspec init
--tools none --no-animation`, then `openspec new change openspec-governance-integration`.
Every CLI claim in this document is version-scoped to 1.12.0 and must be re-measured
against the release that 05 Plan pins.

Measured CLI facts that the challenge rests on:

| Invocation (1.12.0) | Exit | Payload |
| --- | --- | --- |
| `openspec list --json` outside any root | 0 | `root: null`, `status[0].severity: "error"`, `code: "no_openspec_root"` |
| `openspec validate --all --strict --json` with zero changes | 0 | `totals.items: 0`, `failed: 0` |
| `openspec status --all --json` with zero changes | 0 | `"No active changes."` |
| `openspec status --change <fresh-id> --json` | 0 | `isPlanningComplete: false`, `isComplete: false` |
| `openspec validate <id> --strict --json` on artifact-less change | 1 | `valid: false`, "must have at least one delta" |
| `openspec status --change missing-id --json` | 1 | `severity: "error"`, `code: "change_error"` |
| `openspec archive <id> -y --json` on artifact-less change | 0 | `archivedAs: "2026-09-14-<id>"`, `specsUpdated: false` |
| `openspec init --tools none` | 0 | writes only `openspec/config.yaml`, `openspec/specs/.gitkeep`, `openspec/changes/archive/.gitkeep`; root `AGENTS.md` and `.cursor/` untouched |
| `openspec update --force` with no configured tools | 0 | writes nothing; prints `npm install -g @fission-ai/openspec@latest` |

Two spec assumptions are confirmed by that table: structure-only delivery exists
(`--tools none`), and the four owned artifact paths match schema `spec-driven`
(`openspec templates` resolves `proposal.md`, `specs/**/*.md`, `design.md`, `tasks.md`).
The rest of the table contradicts the specification's constraints.

## Ambiguities

### A1. No definition of "pilot", so acceptance criterion 5 is unsatisfiable

Acceptance criteria require `./ask check-workstream <work-id>` to fail when the
matching OpenSpec change is *missing*, while the Constraints require the visible
kit command surface to stay backward-compatible and the criteria require existing
kit tests to pass. The specification never says how a script decides that a
work-id is a pilot. Both available mechanisms break something:

- **Presence-based** (pilot ⇔ `openspec/changes/<work-id>/` exists): a missing
  change means "not a pilot", so the gate passes. The "fails when the matching
  OpenSpec change is missing" branch can never execute. The criterion is dead code.
- **Unconditional** (every work-id needs an OpenSpec change): `_ask/tests/test-workstream-smoke.sh`
  fails. That test installs the kit into a fresh repo, writes `specs/current/demo.md`,
  runs `start-work.sh smoke-demo`, then asserts `check-workstream.sh smoke-demo`
  exits 0 — with no `openspec/` directory anywhere. Backward compatibility for
  non-pilot workstreams is also lost.

Counterexample: run `./ask check-workstream promote-kit-specs` (an accepted,
non-pilot workstream) after implementation. Under presence-based detection it
behaves exactly as today, including the defect listed in Failure cases. Under
unconditional detection it fails for a workstream that was already accepted.

A pilot marker (explicit registry, a field in `work/<id>/intent.md`, or `.openspec.yaml`
metadata) is load-bearing machinery that the specification omits.

### A2. "No duplicate kit specification or plan" has no testable meaning, and the kit creates the duplicate itself

`_ask/scripts/start-work.sh:52` unconditionally seeds `work/<id>/plan.md` from
`_ask/templates/plan.md`. `_ask/scripts/check-workstream.sh:62` then requires that
file to exist. So:

- `./ask start-work <pilot-id>` creates a kit plan file before any agent acts.
- Deleting it to satisfy "no duplicate plan" makes `check-workstream` fail, so the
  pilot can never reach implementation eligibility.

The escape is a definition: `status.sh:105 meaningful()` already distinguishes
template boilerplate from real content, so "duplicate" can mean *meaningful
content* rather than *file presence*. The specification does not say which, and the
Artifact ownership block omits `plan.md` from the kit-owned list entirely — which
reads as "the file must not exist".

This workstream demonstrates the collision on disk right now: `work/openspec-governance-integration/plan.md`
exists (template), and both `specs/proposals/openspec-governance-integration.md`
and `specs/current/openspec-governance-integration.md` exist.

### A3. Is the integration workstream itself a pilot?

The specification requires that an active pilot change have no second specification
under `specs/proposals/` or `specs/current/`, and no duplicate kit plan. The
canonical specification for this work *is* `specs/current/openspec-governance-integration.md`,
with a second copy under `specs/proposals/`. If this work-id is a pilot, it violates
its own Behavior section at the moment 05 Plan starts. If it is not a pilot, then
the integration is built under kit-owned spec and plan artifacts and the pilots are
two or three *other* workstreams that must be named.

05 Plan cannot pick an artifact layout for its own work without this answer.

### A4. "Strict OpenSpec validation runs before implementation eligibility" — enforced where, and bypassable how

Two gaps:

- **Where.** `check-workstream` is the machine gate before delegated implement,
  review, and refactor; `_ask/agents/06-implement.md` is prose guidance. The criterion
  names neither, so a test could assert only the prose.
- **Bypass.** Measured: 1.12.0 supports `skip_specs: true` in a change's
  `.openspec.yaml`, documented by the validator itself for "pure refactor, tooling,
  docs" changes. The integration's own work is exactly tooling and scripts. With
  `skip_specs: true` a change validates strictly with zero behavioral deltas, so
  "strict validation ran" carries no information about specification quality. The
  specification does not govern that flag.

Counterexample: a pilot sets `skip_specs: true`, `openspec validate <id> --strict`
exits 0, the gate opens, and `openspec/specs/` never becomes canonical for anything —
while the specification asserts it is "the canonical behavioral specifications for
pilot scope".

### A5. `./ask status` reading OpenSpec CLI output contradicts how status works

`status.sh` deliberately avoids a checkout: it enumerates `refs/heads/agent/*`,
skips refs already merged into the default branch, and reads artifacts with
`git show <ref>:<path>` (`status.sh:83 blob()`). The help text states it: "Live
workstreams are inferred from local refs/heads/agent/* (no checkout)."

Measured: OpenSpec resolves its root from the current directory (`root.source: "nearest"`),
and outside a root `openspec list --json` returns `root: null`. The CLI has no way to
read `openspec/changes/<id>/` on a branch that is not checked out.

Counterexample: three live `agent/*` branches, HEAD on `main`. `./ask status` prints
a stage for all three today. The OpenSpec CLI can only see `main`'s working tree,
where no pilot change directory exists. The criterion "`./ask status` reports state
for the matching OpenSpec change through machine-readable CLI output" is therefore
unsatisfiable for exactly the branches status exists to report on, unless status
starts checking out branches — which collides with `_ask/policies/worktree.md`
(never operate on a dirty or borrowed tree) — or the criterion is scoped to the
current checkout.

### A6. "Archive" names two different things

`status.sh` prints `life: archived` for a work-id whose `work/<id>/` is on the
default branch with no unmerged `agent/*` ref. OpenSpec archive moves a change
directory to `openspec/changes/archive/<date>-<id>/`. The specification uses the
bare word "archive" for the second meaning in Lifecycle mapping, Invariants, Failure
cases, and Acceptance criteria, in a document that also drives `./ask status` work.
Two accepted meanings of one term in one lifecycle is a misread waiting to happen.

### A7. "Verification evidence must identify the clean Git commit it covers" — no named mechanism

Today `verify.sh` records `git rev-parse HEAD` with no clean-tree check, takes no
`--work-id`, and writes `verification-result.json`, which `.gitignore` lists. The
seeded `work/<id>/verification.json` (from `_ask/templates/verification.json`) is
never written by any script, and `status.sh:127 artifacts()` does not read it.

So "clean commit" is ambiguous between a state claim and an enforced refusal, and
the evidence file the specification lists as kit-owned is an unpopulated stub while
the only real output is untracked. `record-run.sh` already has the refuse-on-dirty
behavior (`_ask/tests/test-record-run-refuses-dirty.sh`), so the precedent exists;
the specification does not say whether `verify` adopts it.

Note for later stages: `specs/current/promote-kit-specs.md` records the
verification artifact-schema drift as a known, deliberately unfixed issue. This
specification's criteria sit on top of that drift without acknowledging it.

## Missing failure cases

### F1. A vacuous green from a bulk validation flag

Measured: `openspec validate --all --strict --json` exits 0 with `items: 0` when no
change exists. `openspec status --all --json` exits 0 with "No active changes."
`openspec list --json` outside a root exits 0 with `root: null` and an error object
in the payload.

`09 Verify` and the eligibility gate both want "validate everything", so `--all` is
the natural implementation. A pilot whose change directory was never created, or a
consumer repo where `openspec init` never ran, then produces a passing strict
validation. The listed failure case "A malformed or failed OpenSpec command is
treated as success" covers malformed output; it does not cover **well-formed output
that reports success over an empty set**. Add it, and require targeted
per-work-id invocations for gating.

### F2. Exit code 0 on an incomplete change

Measured: `openspec status --change <fresh-id> --json` exits 0 with
`isPlanningComplete: false`, `isComplete: false`, and `artifacts[].status` of
`ready`/`blocked`. Acceptance criterion 5 requires the gate to fail on an
*incomplete* change. An exit-code-driven implementation passes. The kit must read
named fields, and the specification should say which fields mean "incomplete".

### F3. The tool's own output promotes the unpromoted surface

Measured: `openspec status --change <id> --json` returns
`nextSteps: ["Run openspec instructions proposal --change \"<id>\" --json before writing that artifact."]`.
`openspec update` prints "Run \"openspec init\" to set up tools."

Acceptance criterion 6 requires `./ask status` to surface OpenSpec machine-readable
output. Doing so injects OpenSpec command instructions into agent context, which is
the listed failure case "Agents see kit and OpenSpec commands presented as competing
default workflows" arriving through data rather than through generated command files.
`--tools none` does not prevent it. The specification needs a stance: filter or
relabel `nextSteps` when surfacing OpenSpec output through kit commands.

### F4. The pin is defeated by advice, not by automation

Measured: `openspec update --force` prints `npm install -g @fission-ai/openspec@latest`.
The installed CLI here is a *global* npm install at 1.12.0 while 1.13.0 exists, and
the repo has no `package.json`, so no repo-local pin mechanism exists today.

The Constraints forbid setup and automation from silently upgrading. They do not
cover an agent following the tool's printed remediation, or two developers with
different global installs. Same-version determinism is also not guaranteed: `openspec
config` is global-scope only (`--scope global`, profile `core|custom`), and `openspec
schema` (experimental) can fork project-local schemas. Two machines on the identical
pinned version can resolve different artifact templates.

Counterexample: developer A on 1.12.0 and developer B on 1.13.0 ("run openspec
update again to pick up new workflows") produce different validation outcomes for
the same change, and both record verification evidence claiming a clean commit.

### F5. Archive succeeds unconditionally, so the block must be kit-side

Measured: on a change with zero artifacts (only `.openspec.yaml`), `openspec archive
<id> -y --json` exited 0 and moved the directory to
`openspec/changes/archive/2026-09-14-<id>/` with `specsUpdated: false` — in a repo
with no kit acceptance and no passing validation, moments after
`openspec validate <id> --strict` had exited 1.

Since the Non-goals preserve direct CLI access, "Normal archive is blocked until
kit acceptance exists" cannot be enforced at the tool boundary. Missing failure
case: archive ran directly and the kit only detects it afterward. The available
mechanism is `openspec validate --archived` (documented for pre-commit linting of
archived task completion) plus a kit check that `work/<id>/acceptance.md` carries a
commit SHA — a detection rule, not a block. The specification should say which it means.

### F6. The shared-identity path stops holding at archive

Measured: archive renames to `<YYYY-MM-DD>-<id>`, from the machine clock. The
Shared identity invariant binds `openspec/changes/<work-id>/`, and the Constraints
say missing artifacts must be reported as failures.

Counterexample: an accepted and archived pilot. `openspec/changes/<work-id>/` is
gone, so a kit status lookup finds a missing change and must report failure for a
workstream that completed correctly. Two spec rules combine to fail on the success
path. The lookup key after archive is also not the work-id alone, and the date
prefix varies by machine timezone.

### F7. OpenSpec absent, and the new install-time dependency

The kit is bash and python with no Node dependency. Criterion 1 covers a clean
consumer installation but not whether `install-kit.sh` now runs `openspec init`, nor
what `./ask status` and `./ask verify` do when the executable is missing. If install
requires the binary, `_ask/tests/test-install-kit-apply.sh` and
`test-install-kit-dry-run.sh` gain a Node prerequisite and consumer repos gain a
hard dependency — against the backward-compatibility constraint. Pinning via
`npx openspec@<version>` also adds a network dependency per invocation, which
breaks offline and air-gapped consumers.

### F8. A pilot abandoned mid-flight, and the abandon decision for the integration

The evaluation may return `abandon`, and an individual pilot may be dropped. If a
pilot's canonical behavioral specification lives only in `openspec/specs/` (as the
Behavior section requires), abandoning means migrating specifications *back* into
`specs/current/`. No return path, owner, or state definition exists for either case.

### F9. Two pilots at once

`_ask/policies/worktree.md` forbids parallel related branches that touch common
files. Two pilots both write `openspec/specs/` main specifications and both mutate
the same gates. So the two or three pilots must be serialized — which the
specification never states, while listing "merge conflicts" as an evaluation measure.

### F10. Pilot stage regression in `status.sh`

`status.sh:164 stage()` derives stage from `work/<id>/` content only, and
`status.sh:192 warnings_for()` flags `code-without-plan` when a live branch at stage
`seeded`/`explored`/`intent` changed files outside `work/<id>/` and `specs/`.

Counterexample: a compliant pilot with no meaningful `work/<id>/plan.md` and a real
`openspec/changes/<id>/tasks.md` sits at stage `intent` forever and raises
`code-without-plan` on every commit, because `openspec/` is neither prefix. Every
correct pilot looks like it left the kit path. No acceptance criterion covers the
stage machine or the warning heuristic.

## Over-constraint risks

### O1. Forbidding any file under `specs/current/` for a pilot

The rule is stricter than its own purpose. The purpose (one source of truth) is
served by forbidding a second copy of the *requirements*. Forbidding any file
breaks `check-workstream`'s existing spec gate for pilots (A1, A2). A non-normative
pointer file — no requirements, one link to `openspec/changes/<id>/` — preserves
exclusivity and keeps the existing gate meaningful. The specification should decide
between the strict and the pointer form rather than leave the gate broken.

### O2. "Default setup must not generate OpenSpec tool-specific commands or skills" stated at the tool boundary

For 1.12.0 the constraint is satisfiable (`--tools none`, verified). Stated as an
absolute property of the tool, it makes the kit hostage to a future release's flag
surface; stated as a property of the repo end-state ("no OpenSpec-generated command
or skill file is present after setup"), it is testable by listing files and survives
a release that drops or renames `--tools`.

### O3. Version pinning without a resolution strategy

"Pinned to an explicit supported version" with no named mechanism, combined with no
`package.json` and a global-install CLI, over-constrains toward either introducing a
Node manifest into a bash/python kit or per-invocation `npx` network resolution.
The kit already has the right precedent: `_ask/skills/manifest.yaml` pins explicit
revisions and `_ask/tests/test-prepare-skills-refuses-latest.sh` refuses `latest`.
Naming that precedent costs nothing and removes the guesswork from 05 Plan.

### O4. `openspec/specs/` canonical for pilot scope, in the kit's own repo

This repo develops the kit, and `specs/current/` holds 18 accepted specifications
plus the `.cursor/rules/workstream-scope.mdc` rule pointing agents at the accepted
specification there. Making `openspec/specs/` canonical for pilot capabilities
creates two rules for agents in the same repo with no marker to tell them apart (A1).

### O5. Acceptance of this workstream depends on future workstreams

"Two or three pilot changes produce a recorded adopt, revise, or abandon evaluation"
makes `10 Accept` for `openspec-governance-integration` wait on two or three other
workstreams, each with its own Accept, serialized per F9. The comparison measures
also need a baseline of the *current* kit flow ("time spent producing and maintaining
artifacts"), and no such baseline is recorded before the switch. Either split the
evaluation into its own workstream or state that this one accepts on machinery plus
a recorded baseline, with the evaluation tracked separately.

## Under-constraint risks

### U1. Only failure criteria for the gates

Every gate criterion states a failure condition. No criterion states that a valid
pilot *passes*. A gate that always fails satisfies criteria 4, 5, and 11 literally.
Add the pass path: a pilot with a valid, complete OpenSpec change on a clean
dedicated branch reaches implementation eligibility.

### U2. "Incomplete" and "invalid" are undefined in machine terms

Per F2 they map to named JSON fields (`isPlanningComplete`, `isComplete`,
`applyRequires`, `artifacts[].status`) and to targeted `validate --strict` exit
codes, not to bulk exit codes. Unstated, the implementer will use exit codes.

### U3. No rule that OpenSpec output is trusted only after shape checks

The Constraints cover invalid JSON. They do not cover well-formed JSON carrying
`status[].severity: "error"` alongside exit 0 (measured for `list` outside a root).
Required rule: `root: null` or any `status[].severity == "error"` is a failure
regardless of exit code, and gating uses targeted per-work-id invocations only.

### U4. `openspec/` is unclassified in the ownership registry

`_ask/OWNED-PATHS.md` splits kit-owned from consumer-owned, and `./ask upgrade`
refreshes kit-owned paths. `openspec/` appears in neither list, so upgrade and
install behavior for it is undefined. It belongs with `specs/` and `work/` as
consumer engineering state. The generator-coexistence criterion tests file
preservation without requiring the registry to say who owns what.

Related: ADR-0011 (kit namespaced / no collision) is the standing decision about
top-level paths, and the repo carries 17 ADRs. A new top-level directory plus a new
external dependency is ADR-class; no criterion requires one.

### U5. The change directory holds files the ownership block omits

Measured: `openspec new change` writes `openspec/changes/<id>/.openspec.yaml`
(and `--description` writes a `README.md`). The Artifact ownership block enumerates
four paths. Own the directory, not a file list — otherwise `.openspec.yaml`, which
carries `skip_specs` (A4), is governed by nobody.

### U6. `04 Spec Change` after archive breaks shared identity

Post-acceptance, a semantic change on the same work-id finds its OpenSpec change
archived (F6). A new change directory needs a new id, so
`openspec/changes/<work-id>/` no longer identifies the work. The Lifecycle mapping
does not say how 04 behaves in that state.

### U7. Work-id normalization is asserted, never defined

"The same normalized work ID identifies…" names no normalization function.
`start-work.sh` applies none — it uses `$1` verbatim for both `agent/<work-id>` and
`work/<work-id>/`. OpenSpec change ids follow their own conventions (the tool's own
examples are verb-prefixed, e.g. `add-<capability>`). Unhandled states: an OpenSpec
change with no kit work directory, more than one change plausibly matching a
work-id, and a change id that diverges from the branch name by convention.

### U8. No criterion binds verification output to the work-id

Per A7, `verify.sh` has no `--work-id` and its output is gitignored. The criteria
can be satisfied while evidence stays untracked and unattached to the workstream.
State the destination (`work/<id>/verification.json`), the schema, and whether
`verify` adopts it.

### U9. Gate changes are delegation-escalation class, with no named approval point

`_ask/policies/delegation.md` escalates architecture-boundary and acceptance-criteria
changes. This work rewrites the kit's own safety gates (`check-workstream`, `status`,
`verify`) at Risk HIGH. The Constraints defer to policy generically; 05 Plan should
carry explicit human approval points for each gate it modifies.

## Recommended clarifications

Items 1–6 change or reinterpret acceptance criteria and therefore need `04 Spec Change`.
Items 7–12 are plan-time additions that do not touch What/Why.

1. **Define the pilot marker** and state whether non-pilot workstreams keep today's
   gate behavior unchanged. Rewrite criterion 5 so its failure branch is reachable
   under that marker, and confirm `_ask/tests/test-workstream-smoke.sh` still passes
   as written (A1).
2. **Define "duplicate"** as meaningful requirement or plan content rather than file
   presence, and decide the pilot's `work/<id>/plan.md` form — absent (requires
   changing `start-work.sh` and `check-workstream.sh`) or a non-normative pointer
   (requires neither). Add `plan.md` to the ownership block explicitly, in whichever
   form is chosen (A2, O1).
3. **State whether `openspec-governance-integration` is itself a pilot.** If yes,
   state how its existing `specs/current/`, `specs/proposals/`, and `work/.../plan.md`
   files are reconciled. If no, name the pilot candidates (A3).
4. **Rescope criterion 6** to OpenSpec state for the current checkout, and keep
   ref-based reporting for branches that are not checked out — or drop the
   machine-readable-CLI requirement for non-checked-out branches. Add a criterion for
   the `status.sh` stage machine and the `code-without-plan` heuristic recognizing
   OpenSpec artifacts (A5, F10).
5. **Replace "archive is blocked" with the mechanism**: kit-mediated archive refuses
   without `work/<id>/acceptance.md` carrying a commit SHA, and a check detects
   out-of-order direct archive after the fact (`openspec validate --archived` is
   available). State the post-archive lookup path `openspec/changes/archive/<date>-<id>/`
   so shared identity and "missing artifacts are failures" stop contradicting on the
   success path (F5, F6, A6). Rename the OpenSpec sense to `openspec-archive`
   throughout to separate it from `status.sh`'s `life: archived`.
6. **Decide the evaluation's home**: either accept this workstream on machinery plus
   a recorded pre-change baseline and track the two-or-three-pilot evaluation as its
   own workstream, or keep it here and state that Accept blocks until the pilots
   finish, serialized per `_ask/policies/worktree.md` (O5, F9).
7. Require targeted per-work-id invocations for all gating
   (`openspec validate <work-id> --strict`, `openspec status --change <work-id>`),
   and forbid `--all` forms as gate inputs. Treat `root: null` or any
   `status[].severity == "error"` as failure regardless of exit code. Map "incomplete"
   to `isPlanningComplete` / `isComplete` / `artifacts[].status`. Add tests for
   exit-0-with-error-payload and for empty-set strict validation (F1, F2, U2, U3).
8. Govern `skip_specs` in `.openspec.yaml`: allowed only with a recorded reason, and
   never as the route by which "strict validation ran" is claimed for a pilot chosen
   to exercise behavioral deltas. Own the change *directory* rather than four files
   (A4, U5).
9. Pin using the existing kit precedent (explicit revision, refuse `latest`, mirroring
   `_ask/skills/manifest.yaml` and `test-prepare-skills-refuses-latest.sh`), add a
   fail-closed version assertion, decide the offline story for `npx`, and pin the
   schema and profile as well as the version — `openspec config` is global-scope and
   `openspec schema` is experimental, so version alone does not give determinism.
   Add a rule that agents do not act on the CLI's `npm install ... @latest` advice
   (F4, O3).
10. Specify `verify`: take `--work-id`, write `work/<id>/verification.json` in the
    template schema, refuse a dirty tree as `record-run.sh` already does, and record
    the commit. Note the pre-existing schema drift that
    `specs/current/promote-kit-specs.md` left open (A7, U8).
11. Add `openspec/` to `_ask/OWNED-PATHS.md` as consumer-owned engineering state, and
    record an ADR for the dependency and the new top-level path against ADR-0011
    (U4). State the repo end-state form of the no-generated-commands constraint so it
    is testable by file listing (O2).
12. Add the missing states: OpenSpec CLI absent or version-mismatched (including
    whether `install-kit.sh` requires it), pilot abandoned mid-flight with its
    specifications only in `openspec/specs/`, abandon-decision return path for the
    integration, work-id normalization plus the no-match / multi-match cases, and
    `04 Spec Change` on an already-archived change (F7, F8, U6, U7).

## Challenge verdict

**ESCALATE.**

Alignment with Why holds: reusing a mature artifact engine while the kit keeps
governance, Git safety, independent review, verification, provenance, and acceptance
is coherent, and the two assumptions most likely to sink it — structure-only delivery
and the four artifact paths — are confirmed for OpenSpec 1.12.0. Nothing here argues
against the What or the Why.

The blockers are acceptance criteria that cannot be implemented as written, so 05 Plan
would have to invent policy to proceed:

| # | Blocker | Effect on 05 Plan |
| --- | --- | --- |
| A1 | No pilot marker; criterion 5 is unsatisfiable either way | Cannot choose gate semantics without breaking a named existing test or the criterion |
| A2 | Kit seeds the plan file the criteria forbid | Cannot choose the pilot artifact layout |
| A3 | Unknown whether this workstream is a pilot | Cannot choose its own layout |
| A5 | Criterion 6 contradicts ref-based `status.sh` and OpenSpec's cwd root resolution | Cannot implement without a checkout, against worktree policy |
| F5 | Archive is unconditionally permitted (measured), and direct CLI access is a Non-goal | "Blocked" has no implementable meaning |
| O5 | Acceptance depends on two or three future workstreams with no baseline | Cannot define this workstream's Accept |

Each resolution edits acceptance criteria, which `_ask/policies/workflow.md` keeps
hard without Spec Change. Recommended clarifications 7–12 are plan-time work and need
no human decision; 1–6 need one.

**Gate: ESCALATE → human decision required. `04 Spec Change` before `05 Plan`.**
