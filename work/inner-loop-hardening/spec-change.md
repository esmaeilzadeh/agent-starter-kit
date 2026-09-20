# Specification Change Proposal

## Current specification

`specs/proposals/inner-loop-hardening.md` (PROPOSED). Challenge:
`work/inner-loop-hardening/spec-challenge.md` (ESCALATE). Intent and
explore-map What/Why stay unchanged.

## Proposed change

Nine encodings for the challenge must-fix list plus integrate/harness. Plan-ok
items stay Plan. Cherry-pick onto the coordinator is **removed**.

### 1. Dirty-tree vs inner-loop worktrees

- Runner start requires the **coordinator** checkout clean (`./ask check-clean`
  on `agent/<work-id>`).
- Task worktrees are runner-created from a recorded SHA. Spawn checks that
  worktree is empty of uncommitted files; that check is runner-owned, not a
  human `./ask check-clean` prompt.
- Failed integrate: abort the in-progress Git operation so the coordinator
  returns to the last successful `coordinator_sha`. Task branches stay intact
  (same commits, same parents). Escalate. Outer 09/10 still require a clean
  coordinator tree.
- `worktree.md` in this workstream: allow in-workstream
  `agent/<work-id>/task/<task-id>` worktrees. Cross-workstream parallel overlap
  stays forbidden.

### 2. Resume after partial integrate

On `resume()`:

- If a merge (or FF) is in progress, abort it back to last recorded
  `coordinator_sha` when that SHA is an ancestor of current HEAD; otherwise
  escalate (manual recovery).
- CAS `revision` increments only after integrate completes **and** HEAD equals
  the new `coordinator_sha`.
- Queued tasks whose `base_sha` is not the current `coordinator_sha` are
  requeued from the new SHA (same rule as cancelled running tasks).
- The runner never cherry-picks or rebases task commits onto the coordinator.

### 3. OpenCode acceptance

Replace AC 2’s “at implement time” hook:

- Mandatory: `./ask sync` writes OpenCode agent files under `.opencode/agents/`
  with the frontmatter keys named in OpenCode’s public agent-file docs. Plan
  records the doc URL and version/date used as the golden shape.
- File-shape tests are mandatory. Live OpenCode spawn is optional, documented.
- Open questions keep only live-spawn matrix, not whether files exist.

### 4. Interactive scaffold vs agent Verify

Provisioning is a **human-only wizard** (same class as `./ask setup`: needs a
TTY). Agent Verify and agent Implement **do not** run interactive provisioning.

If `.agents/verification.yaml` is missing or a mandatory tool is missing:
Verify **fails** with a message that names the wizard. Tests may invoke a
non-interactive `--preset <id>` path; product agent labor may not.

AC 9 observable: wizard preview + confirm + rollback on failed apply; agent
sessions observe fail-closed verify rather than a hidden skip.

### 5. Kit-repo E2E and isolation

For **this** repository (CLI/protocol kit, no product UI, no production DB):

- E2E applicability: `not_applicable`. Reason: product journeys are the kit
  shell suite `_ask/tests/test-*.sh`, executed as the `ask-kit` test preset,
  not as a separate E2E category.
- Isolation: empty production-engine adapter list plus explicit waiver
  `no_production_datastore: true` in `.agents/verification.yaml`.

Consumer TypeScript/Python product repos still follow the full E2E + isolation
rules in the spec. Stage templates still require an E2E section or
`not_applicable`+reason (AC 6). This item only classifies the kit consumer.

### 6. Overlap without `depends_on`

`validate_graph` returns `path_conflict` when any two tasks have overlapping
`owned_paths` and neither is reachable from the other via `depends_on`. The
runner does **not** insert edges. Plan must declare the order.

### 7. Integrate without replay; harness write-allowlist

**Git operation (preserves branch semantics):**

- Task branch is a descendant of `coordinator_sha` → **fast-forward**.
- Concurrent tasks from the same base with disjoint owned paths → **merge**
  (tree union). Both task branches keep their commits and parents.
- Cherry-pick, rebase onto coordinator, or any rewrite of task SHAs is
  forbidden.

**No conflict handling.** A merge conflict is a harness/plan failure, not a
recovery path. No mergetool, no marker editing, no agent resolve. Abort to last
`coordinator_sha`, leave task branches, escalate.

**Hard harness (not markdown-only):** the agent cannot make Git record files
outside that task’s expanded `owned_paths`. Dual enforcement, both tested:

1. **Filesystem:** the task worktree’s agent-writable set is exactly the
   allowlist (plus harness-owned `.git/`). Writes outside the allowlist fail
   before Git. Generated paths (`lock`, `.cursor/**`, `./ask sync` output) are
   on the allowlist or unwritable.
2. **Git:** stage and commit reject any path not in the allowlist. Integrate
   preflight: each task diff ⊆ `owned_paths`; concurrent diffs have empty
   name-only intersection. Then FF or merge. If Git still conflicts, that is a
   harness bug: abort and escalate.

Runner tests must demonstrate: write-outside-allowlist fails; commit-outside
fails; two running writers have disjoint writable sets. Policy prose alone
does not satisfy this item.

Plan may choose the mechanism (sparse-checkout, hooks, mount, sandbox) if those
tests pass.

### 8. Context-engineering audit done-state

Artifact: `work/<work-id>/context-audit.md` with stable checklist IDs covering
instruction hierarchy, context pointers, grilling expansion, and stage
contracts this workstream changed.

- Independent: authored by a spawned challenge/review-class subagent that did
  not Implement the same files.
- Closed: every ID is `pass` or linked to a Spec Change. Accept refuses if the
  file is missing or any ID is `open`.

### 9. Worktree policy in scope

Amending `_ask/policies/worktree.md` for the in-workstream task-branch carve-out
is in this workstream’s What (constraint clarification, not a new runner).
`./ask status` archive/default-branch wording vs `develop` is Plan unless it
changes live/archive meaning; if it does, include it in the same policy edit.

## Why the change is needed

Challenge found the spec’s direction matches intent, but several gates are not
falsifiable against today’s kit. Cherry-pick would rewrite task SHAs and break
branch semantics. Markdown `owned_paths` without a filesystem/Git allowlist
would make merge conflict “handling” a hidden disaster path.

These encodings do not change Why or the outer ASK stages.

## Impacted artifacts

- `specs/proposals/inner-loop-hardening.md` (Behavior, Failure cases, AC 2, 3,
  4, 6, 9, 10, 12, Constraints, Integration)
- Later, after Plan: `_ask/policies/worktree.md`, verify scripts, templates,
  inner-loop harness tests for the write-allowlist

## Impacted workstreams

`inner-loop-hardening` only. Later cards on `develop` unchanged.

## Migration / transition notes

None until Implement. Spec stays PROPOSED until this Decision is accepted and
the proposal file is updated. Then Challenge PASS is recorded by applying these
encodings; Plan may start.

## Acceptance criteria for the change

1. Spec text states coordinator vs task-worktree clean rules and abort of a
   failed FF/merge (no cherry-pick).
2. Spec text states resume abort + revision increment after successful integrate.
3. AC 2 names file-shape + Plan-recorded OpenCode doc version; live spawn optional.
4. Spec text states human-only provisioning wizard; agent Verify fail-closed.
5. Spec text classifies this kit’s E2E as `not_applicable` with the reason above.
6. Spec text states overlap-without-edge is `path_conflict`.
7. Spec text names `context-audit.md`, independence, and closed-state IDs.
8. Spec constraints include the `worktree.md` carve-out as in-scope.
9. Spec forbids cherry-pick/rebase onto the coordinator; integrate is FF or
   merge of disjoint trees; conflict aborts with no resolution path.
10. Spec requires a tested filesystem + Git write-allowlist for `owned_paths`;
    agent labor cannot commit paths outside it.

## Decision

Awaiting human:

1. Allowlist grill (round 2) — layers, glob granularity, roles, out-of-glob.
2. Then accept or amend round-1 encodings plus the grill outcome.
