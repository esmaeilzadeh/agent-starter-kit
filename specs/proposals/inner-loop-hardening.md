# Specification: Inner-loop hardening

## Status

PROPOSED

## Goal

Preserve ASK as the human-governed outer protocol (Grill → Spec → Challenge →
Plan → Verify → Accept) while adding:

1. A deep inner-loop runner for stages 06–08: spawned implement / review /
   debug contexts, **one committing task at a time**, steering-shaped
   boundaries, bounded retry.
2. Language-neutral verification that materializes committed TypeScript and
   Python checks.
3. Canonical protocol under `.agents/ask/` with generated Cursor, Codex, and
   OpenCode projections.
4. Human-controlled Git-flow (`develop` integration, protected `main` release).
5. Durable later-work cards on `develop` plus the issue tracker.
6. An independent context-engineering audit before Accept.

Source intent: `work/inner-loop-hardening/intent.md`. Spec Change:
`work/inner-loop-hardening/spec-change.md` (accepted 2026-09-20).

## Non-goals

- Replacing ASK outer stages, OpenSpec when present, or human Accept.
- Importing cc-sdd, Spec Kit, Learn Harness Engineering, or another SDLC.
- Concurrent Git writers, cherry-pick/rebase onto the coordinator, or
  merge-conflict recovery.
- Per-file path census at Plan; filesystem lock of the whole tree to
  `owned_paths` (blocks test runners).
- Unbounded reviewer/implementer retry.
- A custom model runtime, centralized state database, transcript database, or
  unbounded autonomous debugger.
- Languages other than TypeScript and Python.
- Per-task checks substituting for outer `./ask verify`.
- Compatibility shims for `_ask/agents/`, `_ask/bindings/`, or
  `.starter-kit/verify.conf`.
- Upgrade paths that overwrite consumer-owned verification or later cards.
- Agent-authorized merge, tag, push, or deploy to protected `main`.
- Generic in-memory production-database substitutes (parked later work).

## Behavior

### Canonical sources and generated projections

Kit-owned protocol lives at:

```text
.agents/ask/stages/          # 00–10 contracts (moved from _ask/agents/)
.agents/ask/bindings/        # roles, pools, runtime slug tables, templates
.agents/ask/verification/    # language-neutral core + TS/Python presets
```

Prepared Community Skills remain at `.agents/skills/` (generated, gitignored).

`./ask sync` is the single generator. It reads `.agents/ask/` and writes:

| Runtime | Projection |
| --- | --- |
| Cursor | `.cursor/skills`, `.cursor/commands`, `.cursor/agents` |
| Claude | `.claude/agents` |
| Codex | `.codex/agents` (TOML; spawn may stay best-effort) |
| OpenCode | `.opencode/agents` |

Stage contracts call the inner-loop module; they do not inline a DAG.

Consumer overlays live at `.agents/ask.local/{stages,bindings}/` (same relative
paths as kit-owned files). `./ask sync` merges overlay after kit source.
Upgrade replaces `.agents/ask/` as one kit-owned unit. It leaves
`.agents/ask.local/`, `.agents/verification.yaml`, `.later/*.md` except
README, product manifests, and `.agents/skills/` bodies untouched.

`_ask/` remains the dispatcher/scripts/tests/docs package. After this change,
stage-contract and binding SoT is `.agents/ask/`, not `_ask/agents` or
`_ask/bindings`.

### Inner-loop runner (stages 06–08)

The runner is a deep module. Callers pass a work-id, plan/TaskGraph, spec
pointer, and coordinator branch. Hidden: scheduling, retry, resume, evidence
fold.

**TaskGraph** is committed under `work/<work-id>/inner-loop/tasks.yaml`.
**State** is coordinator-owned at `work/<work-id>/inner-loop/state.json`.
Workers never edit `state.json`. They emit `TaskResult` files; the coordinator
applies versioned compare-and-swap updates.

**One writer.** At most one task may have unintegrated commits. Implement,
review, and debug are separate spawned contexts for that task (role trio).
Disjoint `owned_paths` and `(P)`-style markers are Plan notes; the runner does
not start a second writer.

**Checkout.** Default: the coordinator worktree `agent/<work-id>`. An optional
task worktree/branch is Plan-ok if integrate is **fast-forward only** (task
branch is a descendant of `coordinator_sha`). Cherry-pick and rebase onto the
coordinator are forbidden.

Each writing task:

1. Declares seam/module `owned_paths` globs (not a file list) and `depends_on`.
2. Starts from a recorded coordinator SHA on a clean coordinator tree
   (`./ask check-clean`). Optional task worktree spawn is runner-owned (empty
   of uncommitted files); that is not a human dirty-tree grill.
3. Runs implement → task-local review (see retry). Records TDD evidence or a
   typed exemption.
4. Commits only paths inside the expanded globs. Does not mutate coordinator
   state files.

**Scheduling**

- Ready set is the tasks whose `depends_on` are integrated.
- The runner starts **one** ready task (order: topological `depends_on`, then
  stable `task-id`).
- `validate_graph` refuses cycles. Overlapping `owned_paths` with no covering
  `depends_on` edge → `path_conflict` (Plan must declare order). No auto-edges.

**Integrate**

- After APPROVED review, task commits are already on `agent/<work-id>`, or
  fast-forwarded from the task branch.
- CAS `revision` increments only when HEAD equals the new `coordinator_sha`.
- `resume()`: if the coordinator is dirty or a Git operation is in progress,
  abort that operation back to last `coordinator_sha` when it is an ancestor of
  HEAD; otherwise escalate. Then continue the next non-integrated task.

**09 Verify** and **10 Accept** stay outer-loop. Node checks are per-task
evidence only.

Amending `_ask/policies/worktree.md` for this in-workstream runner (optional
task worktrees; still one writer; still no cross-workstream overlap) is in
scope.

### Boundaries (steering-shaped)

`owned_paths` are seam/module globs declared at Plan. The harness expands them
at spawn. Files created **inside** the glob are allowed. Plan does not list
every path.

Three layers:

| Layer | What |
| --- | --- |
| Readable | Whole repository (typecheck, imports, tests). |
| Writable, never committed | Scratch: caches, tmp, coverage; gitignored. |
| Committable | Expanded `owned_paths` only. |

Test **source** lives in the glob and is committed. A production file edited
“for the test” and left uncommitted is forbidden.

**Harness (tested):** Git stage and commit reject any path outside the
expanded globs. The reviewer runs `git diff --name-only` and compares to the
globs. Policy prose alone is not the gate. The filesystem is **not** reduced
to `owned_paths` only.

Review commits nothing. Debug uses the same commit allowlist as that task’s
implementer. Review/debug may write scratch.

**Out of glob mid-task:** do not auto-expand. Classify:

- Extra files not required → revert; one remediation round.
- Files required but outside the glob → status `blocked`; escalate or queue a
  task that owns that glob. Do not re-dispatch implementer for the same miss.

### Retry (bounded)

Reviewer verdict is exactly `APPROVED` or `REJECTED` with typed `REMEDIATION`
when rejected.

- REJECTED rounds 1–2: re-dispatch implementer with that remediation.
- REJECTED a third time, or implementer BLOCKED: debug adapter in a **fresh**
  context (no failed-implementer history). Then a new implementer. Max **two**
  debug rounds.
- Still failing → task `blocked` / escalate. No further spawn for that task.

### TDD evidence

Behavior-changing tasks record, in `TaskResult`:

1. Confirmed seam (human-confirmed at Plan or task brief).
2. Failing command and captured output (`red`).
3. Passing command and captured output (`green`).
4. Implementation commit SHA (on `agent/<work-id>` or the task branch before
   FF).

Typed exemptions (documentation-only, generated projections, non-behavioral
config) require a reason field. Reviewer checks the reason. Unchecked
exemption → task not eligible for integration.

### E2E contract

Grill/Spec records whether E2E applies. If yes, the spec (or linked E2E
section) lists journeys, observable outcomes, environment, test data, and
reset rules; the human confirms with the specification. Plan maps those to
tooling and isolation. Implement builds them. Verify runs them.

`e2e: not_applicable` plus a reason is valid. Missing E2E section with no
reason refuses Plan/Implement.

**This kit repo:** `not_applicable`. Reason: journeys are `_ask/tests/test-*.sh`
under the `ask-kit` test preset, not a product E2E category. Isolation:
`no_production_datastore: true` and an empty production-engine adapter list in
`.agents/verification.yaml`. Consumer TypeScript/Python product repos still
use the full E2E and isolation rules.

### Verification

**Scaffolder** (language-neutral) inspects manifests, lockfiles, scripts, and
tool configs. It writes `.agents/verification.yaml` **only when absent**.
Explicit re-scaffold writes a candidate file; replacement happens only after
human confirmation.

**Brownfield:** discovered existing tools become the committed baseline. Missing
mandatory categories still require provisioning. `.starter-kit/verify.conf` is
ignored (no migration).

**Monorepo / mixed stack:** each workspace with a TypeScript or Python manifest
gets its own named section. Detect workspaces from `package.json` `workspaces`,
`pnpm-workspace.yaml`, Poetry/Hatch workspace tables, and sibling
`pyproject.toml` / `package.json` packages under a declared root.
Workspace-local tool config wins over repo-root. If both exist and disagree,
scaffold stops with a choice.

**Consumer-owned** `.agents/verification.yaml` is committed. Kit upgrade leaves
it in place. It records schema version, scaffolder/preset versions, concrete
commands, mandatory/optional tier, and isolation declarations.

**Mandatory categories** for every detected language: typecheck, lint, tests
(including TDD-capable unit/integration), and E2E unless `not_applicable`.

**Interactive provisioning** is a **human-only wizard** (TTY; same class as
`./ask setup`). Agent Verify and agent Implement do not run it. Missing yaml or
missing mandatory tool → Verify **fails** with a message that names the wizard.
Tests may use non-interactive `--preset <id>`; product agent labor may not.
Wizard apply: preview, confirm, rollback of mutated product files on failure.

**Fail-closed:** empty CheckPlan, zero mandatory checks, or a missing
mandatory tool at verify time → fail.

**TypeScript preset** (examples, not hard-coded in core): `tsc --noEmit` (or
project equivalent), eslint **or** biome (discover one), package-manager test
script, optional dependency-architecture check.

**Python preset:** pyright **or** mypy (discover one), ruff, pytest, optional
import-linter.

**Kit repo:** verification yaml lists kit shell tests via a named `ask-kit`
preset (not raw glob inlined as the only core path).

**Isolation (product repos):** unit tests use no database or an interface-level
fake. Integration and E2E use ephemeral isolated instances of the **production
database engine**. `.agents/verification.yaml` names test-only adapters and
namespace strategy. The runner refuses known development/production
identifiers and destructive commands outside the test namespace. Cleanup is
idempotent; leaks are recorded. In-memory production-engine substitutes are
out of this spec.

### Git-flow

| Branch | Role | Who advances |
| --- | --- | --- |
| `develop` | Integration and durable later-work | Agents prepare PRs; human or agreed merge to `develop` |
| `agent/<work-id>` | Workstream / inner-loop writer | `./ask start-work` from `develop` |
| `agent/<work-id>/task/<id>` | Optional isolated writer | Runner; FF only onto coordinator |
| `release/<version>` | Release prep | Agent prepares; human authorizes |
| `main` | Releasable | Human merge, tag, push |
| `hotfix/*` | Production fix | Starts from `main`; after human release, merge to `main` and `develop` |

`./ask start-work` creates `agent/<work-id>` from `develop` when that branch
exists; otherwise it fails closed with a message to create `develop`.

Later cards: commit `.later/<slug>.md` to `develop` and create/update a tracker
issue. Feature branches do not treat later cards as live workstreams.

Version source: Git tags `vMAJOR.MINOR.PATCH` on `main`. Agents draft
`CHANGELOG.md` (or the product’s existing changelog path) and
`work/<work-id>/release-evidence.md` with version, commit SHA, VerifyResult
path, and named human authorizer. Tag and push stay human-authorized.

### Context-engineering audit

Artifact: `work/<work-id>/context-audit.md` with stable checklist IDs covering
instruction hierarchy, context pointers, grilling expansion, and stage
contracts this workstream changed.

Independent: authored by a spawned challenge/review-class subagent that did not
Implement the same files. Closed: every ID is `pass` or linked to a Spec
Change. Accept refuses if the file is missing or any ID is `open`.

The audit must reproduce and repair compressed grilling/protocol pointers.
Findings that change What/Why escalate via Spec Change; pointer/wording fixes
land as ordinary implementation tasks.

## Interfaces

### TaskGraph node (`work/<id>/inner-loop/tasks.yaml`)

```yaml
id: string                 # stable, unique in the workstream
depends_on: [string]
owned_paths: [glob]        # seam/module globs this writer may commit
roles:
  implement: {}
  review: {}
  debug: {}                # spawned only on bounded failure
exemption: null | { kind, reason }
e2e: inherit | not_applicable
```

### Coordinator state (`work/<id>/inner-loop/state.json`)

```json
{
  "schema": "ask-inner-loop-state/v1",
  "work_id": "",
  "revision": 0,
  "coordinator_sha": "",
  "coordinator_branch": "agent/<work-id>",
  "tasks": {
    "<id>": {
      "status": "pending|ready|running|blocked|integrated|failed|cancelled|escalated",
      "base_sha": "",
      "task_branch": "",
      "result_path": "",
      "boundary_reject": "null|extras_reverted|glob_too_narrow",
      "review_round": 0,
      "debug_round": 0,
      "evidence": {}
    }
  }
}
```

`revision` increments on every successful CAS write. A worker never writes
this file.

### TaskResult (worker → coordinator)

```json
{
  "schema": "ask-task-result/v1",
  "task_id": "",
  "commit_shas": [],
  "tdd": null,
  "exemption": null,
  "owned_paths_touched": [],
  "review": {
    "verdict": "APPROVED|REJECTED",
    "remediation": null,
    "boundary": "ok|extras|glob_too_narrow"
  },
  "notes": ""
}
```

`tdd` is `{ seam, red: {command, output, exit_code}, green: {command, output, exit_code} }`
for behavior-changing tasks, and `null` when `exemption` is set. `exemption` is
`{ kind, reason, reviewer_ack: true }` or `null`.

### CheckPlan / VerifyResult

Language-neutral. Discover emits CheckPlan; run emits VerifyResult. Both carry
`schema`, `commit_sha`, and a `checks[]` list with `id`, `tier`
(`mandatory|optional`), `command`, `status`, `exit_code`, `evidence`.

`.agents/verification.yaml` is the committed CheckPlan for the product repo.

### Runner operations

```text
load_graph(work_id) -> TaskGraph
validate_graph(graph) -> ok | cycle | path_conflict
run_until(quiescent | escalated | cancelled)
cancel(task_id | all)
resume(from state.json)
integrate_ready() -> new coordinator_sha | escalate
```

Tests hit these operations, not stage-contract prose.

## Constraints

- Dirty-tree refusal, dedicated `agent/<work-id>`, commit-after-step, SHA
  evidence, and human Accept remain in force.
- Runtime adapters spawn implement / review / debug. They do not schedule.
- At most one committing task. Review/debug do not start a second writer.
- Review remediations: 2, then debug; debug rounds: 2, then block/escalate.
- TypeScript and Python only for verification presets.
- Codex custom-agent attach may fail; file-shape tests are mandatory; live
  spawn tests are best-effort and documented.
- ASK has no deployed clients: this workstream may break current layout.
  After launch, upgrades preserve consumer-owned files unless a named
  migration says otherwise.

## Invariants

- One portable protocol source: `.agents/ask/`.
- One generator: `./ask sync`.
- At most one task is `running` as a writer.
- A commit on the coordinator for a task is a subset of that task’s expanded
  `owned_paths`.
- Coordinator SHA in `state.json` matches `agent/<work-id>` HEAD after each
  successful integrate.
- `state.json` revision CAS: write fails if observed revision ≠ stored
  revision.
- Outer `./ask verify` fail-closed on empty or missing mandatory checks.
- Tests never target identifiers declared as development or production.
- Protected `main` changes require recorded human authorization.
- `glob_too_narrow` never consumes a remediation round.

## Failure cases

| Case | Required behavior |
| --- | --- |
| Cycle or overlapping `owned_paths` without `depends_on` | `validate_graph` error; no spawn |
| Second writer while one task is running | Refuse spawn |
| Cherry-pick / rebase onto coordinator | Forbidden |
| Git conflict during optional FF | Abort to last `coordinator_sha`; escalate (harness/plan bug) |
| `git diff` paths outside glob, extras only | REJECTED; revert; remediation round |
| `git diff` paths outside glob, files required | `blocked`; no implementer retry |
| Review REJECTED 3rd time | Debug (fresh context), not another implementer-only loop |
| Two failed debug rounds | `blocked`; escalate; no further spawn |
| Missing TDD evidence | Task not integrable |
| Exemption without reviewer check | Task not integrable |
| E2E omitted without reason | Plan/Implement refuse |
| Missing mandatory verify tool | Verify fail; message names human wizard |
| Zero checks | Verify fail |
| Worker writes `state.json` | Reject; protocol violation |
| `start-work` with no `develop` | Fail closed |
| Agent merge/tag/push `main` | Forbidden; escalate |
| Upgrade overwrites `.agents/verification.yaml` | Forbidden |

## Acceptance criteria

1. Canonical stage contracts and bindings exist under `.agents/ask/` and are
   the inputs to `./ask sync`. `_ask/agents` and `_ask/bindings` are no longer
   the protocol SoT (removed or reduced to pointers). Kit tests and docs match.
2. `./ask sync` emits Cursor, Claude, Codex, and OpenCode projections from that
   source. OpenCode files match the frontmatter keys in OpenCode’s public
   agent-file docs; Plan records that doc URL and version/date. File-shape
   tests are mandatory. Live OpenCode/Codex spawn is optional and documented.
3. Inner-loop module tests cover: graph validate (cycle, overlap without
   `depends_on`), single-writer (second spawn refused), commit-allowlist
   reject, reviewer `git diff --name-only` vs globs, `extras` vs
   `glob_too_narrow` (no retry on the latter), review/debug round caps then
   `blocked`, CAS updates, FF integrate (no cherry-pick), resume from
   `state.json`.
4. Two writing tasks never run concurrently. A commit that includes a path
   outside expanded `owned_paths` cannot land.
5. Behavior-changing TaskResult without red then green evidence cannot
   integrate. Typed exemptions require reviewer acknowledgment.
6. Spec/intent templates and 01/02/05/06/09 contracts require E2E
   applicability, journeys or `not_applicable`+reason, and Verify execution
   of confirmed E2E checks.
7. `./ask verify` reads `.agents/verification.yaml` when present. Empty plan
   or missing mandatory tool fails. Language-specific CLIs live only in
   presets, not in dispatcher core.
8. Scaffold creates `.agents/verification.yaml` only if missing. Re-scaffold
   writes a candidate and waits for human confirmation. Upgrade leaves
   `.agents/verification.yaml` and `.agents/ask.local/` in place. Mixed-stack
   workspaces each have a named section; workspace-local config wins, or
   scaffold stops on disagreement.
9. Missing typecheck/lint/test/E2E for a detected language: agent Verify
   fails closed and names the human wizard. Wizard preview + confirm +
   rollback are tested; agents do not run the wizard.
10. Isolation: this kit uses `no_production_datastore` + empty adapters.
    Product repos: named test-only adapters; runner rejects listed dev/prod
    identifiers; unit tests do not require a real DB; integration/E2E target
    ephemeral production-engine resources; leaks are recorded.
11. `./ask start-work` branches from `develop`. Later cards are committed on
    `develop` and linked to tracker issues. Agents prepare `release/*`
    artifacts; they do not merge/tag/push `main`. Hotfix policy is documented:
    from `main`, after human release, back-merge to `main` and `develop`.
12. Plan includes a context-engineering audit task. Accept is refused if
    `work/<id>/context-audit.md` is missing or any checklist ID is `open`.
    Independent spawn did not Implement those files.
13. Kit `./ask verify` on this repo uses the `ask-kit` preset plus any
    committed product yaml and fails if those tests fail.

## Open questions

Plan may choose concrete encodings without Spec Change if they satisfy the
interfaces above:

- Whether a given task uses the coordinator checkout or an optional FF-only
  task worktree.
- OpenCode frontmatter field names from the Plan-recorded doc version.
- Exact CLI verbs (`./ask inner-loop …` vs Implement-stage-only invocation).
- Changelog path when the product already has one (default `CHANGELOG.md`).
- Cross-runtime live-spawn matrix (file-shape is mandatory).

## Source intent

`work/inner-loop-hardening/intent.md`
