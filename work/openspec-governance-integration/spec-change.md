# Specification Change Proposal

## Current specification

`specs/current/openspec-governance-integration.md` (Status CURRENT), challenged in
`work/openspec-governance-integration/spec-challenge.md` (verdict ESCALATE,
model claude-opus-5).

Human decisions recorded 2026-09-14 (picker + six challenge questions):

| ID | Decision |
| --- | --- |
| A1 | Pilot marker is a field in `work/<id>/intent.md`. Non-pilots keep today's gates. Criterion 5 applies only to marked pilots. |
| A2 | Duplicate = meaningful requirement or plan content. `work/<id>/plan.md` is a non-normative pointer to OpenSpec design/tasks. `specs/current/<id>.md` may exist as a pointer with no requirements. |
| A3 | This work-id **is** a marked pilot. Reconcile existing `specs/current/`, `specs/proposals/`, and `work/.../plan.md`. |
| A5 | OpenSpec CLI state for the current checkout only. Other live branches stay `git show`. Status stage and `code-without-plan` must recognize OpenSpec artifacts. |
| F5 | Kit-mediated openspec-archive refuses without `work/<id>/acceptance.md` commit SHA. Detect out-of-order direct archive. Post-archive lookup `openspec/changes/archive/<date>-<id>/`. Rename the OpenSpec sense to `openspec-archive`. |
| O5 | Accept this workstream on machinery plus a recorded pre-change baseline. Two-or-three-pilot evaluation is a later workstream. |

Challenge items 7–12 (targeted CLI, `skip_specs`, pin, verify, OWNED-PATHS/ADR, missing states) land in the same rewrite. They do not change What/Why.

## Proposed change

### Pilot marker

A workstream is an OpenSpec pilot if and only if `work/<id>/intent.md` records:

```text
Engine: openspec
```

Exact heading or field name: a line matching `^Engine:\s*openspec\s*$` in that file.
Absence means not a pilot. Non-pilot workstreams keep today's `check-workstream`,
`status`, and `verify` behavior, including `_ask/tests/test-workstream-smoke.sh`.

`openspec-governance-integration` is a marked pilot. Add the field to its intent
when this change is applied.

Work-id is the `./ask start-work` argument, used verbatim for `agent/<id>`,
`work/<id>/`, and `openspec/changes/<id>/`. No extra normalization. Fail closed
on no-match or more than one active OpenSpec change for that id.

### Duplicate means meaningful content

For a marked pilot:

- OpenSpec owns the change **directory** `openspec/changes/<work-id>/` (not a
  four-file list). That includes `.openspec.yaml`.
- `work/<id>/plan.md` remains a kit file because `start-work.sh` seeds it and
  `check-workstream.sh` requires it. For a pilot it is a non-normative pointer
  to `openspec/changes/<id>/design.md` and `tasks.md`. Meaningful Approach or
  Work-breakdown content in that file is a duplicate and a failure.
- `specs/current/<id>.md` and `specs/proposals/<id>.md` may exist as
  non-normative pointers (Status, one link to the OpenSpec change, no Goal /
  Behavior / Acceptance criteria). Meaningful requirements there are a
  duplicate and a failure.
- `openspec/specs/` remains the canonical behavioral specification for pilot
  scope after the change's deltas apply.

Kit-owned list becomes:

```text
work/<work-id>/intent.md
work/<work-id>/spec-challenge.md
work/<work-id>/plan.md          # pointer only, when Engine: openspec
work/<work-id>/review.md
work/<work-id>/verification.json
work/<work-id>/acceptance.md
work/<work-id>/result.json
```

### Reconcile this workstream

This work-id is a dogfood pilot of the ownership split, not one of the later
evaluation changes unless that later workstream says so.

Cutover (a named plan step, not a silent rewrite of CURRENT during 04):

1. Initialize OpenSpec structure-only in this repo.
2. Create `openspec/changes/openspec-governance-integration/` and copy the
   behavioral requirements from the CURRENT kit spec into OpenSpec proposal,
   deltas, design, and tasks.
3. Replace `specs/current/openspec-governance-integration.md` and
   `specs/proposals/openspec-governance-integration.md` with pointer files.
4. Replace `work/openspec-governance-integration/plan.md` with a pointer.

Until that cutover commit, the CURRENT kit spec remains the only complete
requirements document so the workstream is not spec-less mid-change.

### Status (criterion 6)

`./ask status` must not check out another branch.

- **Current checkout:** if HEAD is `agent/<id>` (or the tree contains that
  change) and the work-id is a marked pilot, read OpenSpec machine-readable
  CLI for that id only (`openspec status --change <id>`, never `--all`).
- **Other live refs:** keep `git show <ref>:…`. Read
  `openspec/changes/<id>/` and `work/<id>/` blobs from the ref. Do not invoke
  the OpenSpec CLI against a foreign worktree.
- **Stage:** a marked pilot with meaningful OpenSpec design or tasks counts as
  planned even when kit `plan.md` is only a pointer.
- **`code-without-plan`:** `openspec/` for that work-id is a recognized prefix,
  same class as `work/<id>/` and `specs/`.
- When kit commands print OpenSpec CLI output, strip or relabel `nextSteps`
  and other fields that recommend `openspec …` as the next user action, so
  kit commands stay the documented default.

### Gates (criteria 4, 5, and the missing pass path)

Enforced in `./ask check-workstream <work-id>`, not only in prose.

For a **marked** pilot, `check-workstream` fails when the matching OpenSpec
change is missing, incomplete, or invalid — even if unrelated specifications
exist. Incomplete and invalid are machine fields from a **targeted**
invocation, not from `--all`:

- invalid: targeted `openspec validate <id> --strict` non-zero, or JSON with
  `valid: false`
- incomplete: `isPlanningComplete` false or `isComplete` false or any
  `artifacts[].status` of `blocked` (re-measure names on the pinned release)
- shape failure: invalid JSON, `root: null`, or any `status[].severity` equal
  to `error`, regardless of process exit code
- empty-set success (`validate --all` with zero items, or `list` with
  `root: null`) is a failure if used as a gate input. `--all` forms are
  forbidden as gate inputs.

Pass path: a marked pilot on a clean dedicated `agent/<id>` branch, with a
valid complete OpenSpec change and the required kit governance files, reaches
implementation eligibility.

`skip_specs: true` in `.openspec.yaml` is allowed only with a recorded reason
in the change proposal. It must not be the evidence that "strict validation
ran" for a pilot whose purpose includes behavioral deltas.

### openspec-archive (criteria 13 and shared identity)

Rename the OpenSpec lifecycle operation to **openspec-archive** everywhere in
this spec, distinct from `./ask status` `life: archived`.

Kit-mediated openspec-archive refuses unless `work/<id>/acceptance.md` contains
an accepted commit SHA.

Direct `openspec archive` remains possible (advanced CLI). After the fact,
kit `status` / `verify` / `check-workstream` detect an openspec-archived change
with no matching Accept SHA and fail.

Post-openspec-archive lookup path:
`openspec/changes/archive/<date>-<id>/` (date from the tool). A missing
*active* `openspec/changes/<id>/` after a valid Accept is not a missing-change
failure; look in archive.

`04 Spec Change` on a work-id whose change is already openspec-archived
creates a new active `openspec/changes/<id>/`. The archived copy stays under
`archive/`. Record the new change in intent.

### Verify

`./ask verify` takes `--work-id`, writes `work/<id>/verification.json` using
`_ask/templates/verification.json`, refuses a dirty tree (same class as
`record-run.sh`), and records the commit SHA it ran against.

For a marked pilot, verification includes targeted strict OpenSpec validation
plus configured project checks.

Pre-existing schema drift in `specs/current/promote-kit-specs.md` stays
unfixed here except that this workstream's evidence lands in
`work/<id>/verification.json`.

### Pin, install, ownership

Pin OpenSpec like `_ask/skills/manifest.yaml`: explicit revision, refuse
`latest`, fail-closed version assertion before gated commands. Agents must not
act on the CLI's `npm install … @latest` advice. Pin schema/profile as well as
version if the pinned release still has global-only `openspec config`.

`install-kit.sh` does **not** require Node or OpenSpec. Non-pilot consumers
stay bash/python. When a marked pilot is in play and the executable is missing
or the version does not match the pin, gated kit commands fail closed.

`openspec/` is consumer-owned engineering state in `_ask/OWNED-PATHS.md`,
same class as `specs/` and `work/`. Record an ADR for the dependency and the
new top-level path against ADR-0011.

No-generated-commands constraint is a **repo end-state**: after default setup,
no OpenSpec-generated command or skill file is present. Test by listing files,
not by asserting a particular init flag forever.

### Evaluation (split)

This workstream's Accept is machinery plus a recorded baseline of the current
kit flow (the comparison measures in Pilot evaluation, captured before the
switch). It does **not** wait for two or three later pilots.

The adopt / revise / abandon evaluation is a later workstream. Park it at
cutover if it is not already in `.later/`.

Pilots of that later evaluation are serialized per `_ask/policies/worktree.md`
when they touch `openspec/specs/` or shared gates.

### Abandoned pilot

If a marked pilot is dropped, or the later evaluation returns abandon,
canonical behavioral specs that exist only under `openspec/specs/` are copied
back to `specs/current/` before OpenSpec is removed from that scope. Owner:
the workstream that decides abandon.

## Why the change is needed

The CURRENT spec's acceptance criteria cannot be implemented as written:

- Criterion 5 has no pilot marker, so it is either dead code or it breaks
  non-pilot workstreams and `test-workstream-smoke.sh`.
- The kit seeds `plan.md` that "no duplicate plan" appears to forbid.
- This workstream already stores its spec under `specs/`, so it cannot be a
  pilot without a reconcile rule.
- Criterion 6 requires OpenSpec CLI output for live branches that status
  never checks out.
- `openspec archive` succeeds with no kit Accept (measured on 1.12.0), so
  "archive is blocked" has no tool-side meaning while direct CLI stays allowed.
- Accept-on-future-pilots makes this workstream unbounded.

What/Why are unchanged: one kit command surface, OpenSpec as internal engine
for spec/plan lifecycle, kit keeps governance and safety, pilot before a
custom schema.

## Impacted artifacts

- `specs/current/openspec-governance-integration.md`
- `specs/proposals/openspec-governance-integration.md`
- `work/openspec-governance-integration/intent.md` (`Engine: openspec`)
- Later: `_ask/OWNED-PATHS.md`, new ADR, `check-workstream.sh`, `status.sh`,
  `verify.sh`, tests — implementation, not this rewrite

## Impacted workstreams

`openspec-governance-integration` only. Evaluation workstream is later, not
started here. `cursor-spawn-slugs` and `kit-talk-ai-team` are unrelated live
branches; do not touch them.

## Migration / transition notes

Do not rewrite CURRENT until this proposal is confirmed.

After confirm: rewrite both spec copies identically, add `Engine: openspec` to
intent. OpenSpec directories and pointer cutover wait for the named plan step
so 04 does not invent `openspec/` layout before Plan.

## Acceptance criteria for the change

- CURRENT spec defines the intent marker, pointer-form duplicates, this
  work-id as a pilot, checkout-scoped status CLI, openspec-archive mechanism
  and lookup, split evaluation, targeted gates with a pass path, verify
  `--work-id` + dirty refuse, pin/install/OWNED-PATHS/ADR rules, and the
  abandon return path.
- What/Why and Risk HIGH are unchanged.
- `test-workstream-smoke.sh` remains valid against the rewritten spec
  (non-pilots unchanged).
- Pointer files, if present before cutover, contain no requirements.

## Decision

Accepted 2026-09-14. Rewrite CURRENT from this proposal. Add `Engine: openspec`
to intent. OpenSpec directories and pointer cutover wait for the named plan
step.
