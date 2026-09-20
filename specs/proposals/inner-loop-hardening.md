# Specification: Concurrent inner-loop hardening

## Status

PROPOSED

## Goal

Preserve ASK as the human-governed outer protocol (Grill → Spec → Challenge →
Plan → Verify → Accept) while adding:

1. A deep concurrent runner for stages 06–08.
2. Language-neutral verification that materializes committed TypeScript and
   Python checks.
3. Canonical protocol under `.agents/ask/` with generated Cursor, Codex, and
   OpenCode projections.
4. Human-controlled Git-flow (`develop` integration, protected `main` release).
5. Durable later-work cards on `develop` plus the issue tracker.
6. An independent context-engineering audit before Accept.

Source intent: `work/inner-loop-hardening/intent.md`.

## Non-goals

- Replacing ASK outer stages, OpenSpec when present, or human Accept.
- Importing cc-sdd, Spec Kit, Learn Harness Engineering, or another SDLC.
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
| OpenCode | `.opencode/agents` (file format from OpenCode docs at implement time) |

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
pointer, and coordinator branch. Hidden: scheduling, worktree lifecycle, retry,
resume, evidence fold.

**TaskGraph** is committed under `work/<work-id>/inner-loop/tasks.yaml`.
**State** is coordinator-owned at `work/<work-id>/inner-loop/state.json`.
Workers never edit `state.json`. They emit `TaskResult` files; the coordinator
applies versioned compare-and-swap updates.

Each writing task:

1. Declares `owned_paths` (source globs) and `depends_on`.
2. Gets a Git worktree and branch `agent/<work-id>/task/<task-id>` from a
   recorded coordinator SHA.
3. Runs implement → task-local review. After two reviewer rejections or an
   implementer BLOCKED, a debug adapter runs at most two rounds, then
   escalates.
4. Records TDD evidence or a typed exemption (see TDD).
5. Commits on its task branch. Does not mutate coordinator state files.

**Scheduling**

- Ready tasks with disjoint `owned_paths` may run concurrently.
- Overlapping source paths are a dependency edge: the later task starts only
  after the earlier task is integrated, from the new coordinator SHA.
- Cycles in `depends_on` refuse the graph before any spawn.

**Integration**

- Order: topological dependency order, then stable `task-id`.
- Mechanism: cherry-pick of the task’s attributable commits onto
  `agent/<work-id>`.
- Unexpected overlap, stale-base semantic conflict, or cherry-pick conflict
  **stops**. Record escalation. No model-authored conflict resolution.
- After integration, still-running tasks whose owned paths intersect the
  integrated diff are cancelled and requeued from the new coordinator SHA.

Read-only review/debug agents may share a checkout. They do not write product
source.

**09 Verify** and **10 Accept** stay outer-loop. Node checks are per-task
evidence only.

### TDD evidence

Behavior-changing tasks record, in `TaskResult`:

1. Confirmed seam (human-confirmed at Plan or task brief).
2. Failing command and captured output (`red`).
3. Passing command and captured output (`green`).
4. Implementation commit SHA on the task branch.

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
`pnpm-workspace.yaml`, Poetry/Hatch workspace tables, and sibling `pyproject.toml`
/ `package.json` packages under a declared root. Workspace-local tool config
wins over repo-root. If both exist and disagree, scaffold stops with a choice.

**Consumer-owned** `.agents/verification.yaml` is committed. Kit upgrade leaves
it in place. It records schema version, scaffolder/preset versions, concrete
commands, mandatory/optional tier, and isolation declarations.

**Mandatory categories** for every detected language: typecheck, lint, tests
(including TDD-capable unit/integration), and E2E unless `not_applicable`.

**Interactive provisioning:** if a mandatory category has no unambiguous tool,
scaffold stops with choices. After the human selects a stack, setup may mutate
manifests, tool config, and lockfiles. Preview the diff; apply only after
confirm. Rollback restores those files if the apply fails mid-way.

**Fail-closed:** empty CheckPlan, zero mandatory checks, or a missing
mandatory tool at verify time → fail.

**TypeScript preset** (examples, not hard-coded in core): `tsc --noEmit` (or
project equivalent), eslint **or** biome (discover one), package-manager test
script, optional dependency-architecture check.

**Python preset:** pyright **or** mypy (discover one), ruff, pytest, optional
import-linter.

**Kit repo:** verification yaml lists kit shell tests via a named `ask-kit`
preset (not raw glob inlined as the only core path).

**Isolation:** unit tests use no database or an interface-level fake.
Integration and E2E use ephemeral isolated instances of the **production
database engine**. `.agents/verification.yaml` names test-only adapters and
namespace strategy. The runner refuses known development/production
identifiers and destructive commands outside the test namespace. Cleanup is
idempotent; leaks are recorded. In-memory production-engine substitutes are
out of this spec.

### Git-flow

| Branch | Role | Who advances |
| --- | --- | --- |
| `develop` | Integration and durable later-work | Agents prepare PRs; human or agreed merge to `develop` |
| `agent/<work-id>` | Workstream | `./ask start-work` from `develop` |
| `agent/<work-id>/task/<id>` | Isolated writer | Runner |
| `release/<version>` | Release prep | Agent prepares; human authorizes |
| `main` | Releasable | Human merge, tag, push |
| `hotfix/*` | Production fix | Starts from `main`; after human release, merge to `main` and `develop` |

`./ask start-work` creates `agent/<work-id>` from `develop` when that branch
exists; otherwise it fails closed with a message to create `develop` (do not
silently fall back to `main` for new work).

Later cards: commit `.later/<slug>.md` to `develop` and create/update a tracker
issue. Feature branches do not treat later cards as live workstreams.

Version source: Git tags `vMAJOR.MINOR.PATCH` on `main`. Agents draft
`CHANGELOG.md` (or the product’s existing changelog path) and
`work/<work-id>/release-evidence.md` with version, commit SHA, VerifyResult
path, and named human authorizer. Tag and push stay human-authorized.

### Context-engineering audit

Before Accept, run an independent audit of instruction hierarchy, context
pointers, grilling expansion, and stage contracts introduced by this
workstream. The audit must reproduce and repair the failure mode where an
expanded canonical frontier is compressed in chat. Findings that change
What/Why escalate via Spec Change; pointer/wording fixes land as ordinary
implementation tasks.

## Interfaces

### TaskGraph node (`work/<id>/inner-loop/tasks.yaml`)

```yaml
id: string                 # stable, unique in the workstream
depends_on: [string]
owned_paths: [glob]        # source files this writer may change
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
- Maximum two debug rounds per task, then escalate.
- TypeScript and Python only for verification presets.
- Codex custom-agent attach may fail; file-shape tests are mandatory; live
  spawn tests are best-effort and documented.
- ASK has no deployed clients: this workstream may break current layout.
  After launch, upgrades preserve consumer-owned files unless a named
  migration says otherwise.

## Invariants

- One portable protocol source: `.agents/ask/`.
- One generator: `./ask sync`.
- Writers never share a worktree. Overlapping source ownership is never
  concurrent.
- Coordinator SHA in `state.json` matches `agent/<work-id>` HEAD after each
  successful integrate.
- `state.json` revision CAS: write fails if observed revision ≠ stored
  revision.
- Outer `./ask verify` fail-closed on empty or missing mandatory checks.
- Tests never target identifiers declared as development or production.
- Protected `main` changes require recorded human authorization.

## Failure cases

| Case | Required behavior |
| --- | --- |
| Cycle or overlapping ready writers | Refuse graph; no spawn |
| Cherry-pick / unexpected overlap | Stop; escalate; leave task branches intact |
| Stale base after integrate | Cancel intersecting running tasks; requeue from new SHA |
| Missing TDD evidence | Task not integrable |
| Exemption without reviewer check | Task not integrable |
| E2E omitted without reason | Plan/Implement refuse |
| Missing mandatory verify tool | Verify fail; scaffold offers provisioning, does not skip |
| Zero checks | Verify fail |
| Worker writes `state.json` | Reject; treat as protocol violation |
| `start-work` with no `develop` | Fail closed |
| Agent merge/tag/push `main` | Forbidden; escalate |
| Upgrade overwrites `.agents/verification.yaml` | Forbidden |

## Acceptance criteria

1. Canonical stage contracts and bindings exist under `.agents/ask/` and are
   the inputs to `./ask sync`. `_ask/agents` and `_ask/bindings` are no longer
   the protocol SoT (removed or reduced to pointers). Kit tests and docs match.
2. `./ask sync` emits Cursor, Claude, Codex, and OpenCode projections from that
   source. OpenCode output matches OpenCode’s documented agent-file shape at
   implement time. Codex TOML is complete relative to the template and
   documented spawn limits.
3. Inner-loop module tests cover: graph validate (cycle, overlap), disjoint
   concurrent ready set, serialized overlapping paths, CAS state updates,
   cherry-pick order (deps then task-id), conflict → escalate, stale-base
   cancel/requeue, resume from `state.json`.
4. A writing task cannot start without a worktree/branch and recorded base
   SHA. Two tasks with overlapping `owned_paths` never run concurrently.
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
9. Missing typecheck/lint/test/E2E for a detected language triggers
   interactive provisioning with preview; no silent omit; failed apply rolls
   back mutated product files.
10. Isolation: verification config names test-only adapters; runner rejects
    listed dev/prod identifiers; unit tests do not require a real DB;
    integration/E2E target ephemeral production-engine resources; leaks are
    recorded.
11. `./ask start-work` branches from `develop`. Later cards are committed on
    `develop` and linked to tracker issues. Agents prepare `release/*`
    artifacts; they do not merge/tag/push `main`. Hotfix policy is documented:
    from `main`, after human release, back-merge to `main` and `develop`.
12. Plan includes a context-engineering audit task. Accept is refused if that
    task is missing or open. The audit addresses compressed grilling/protocol
    pointers introduced by this workstream.
13. Kit `./ask verify` on this repo uses the `ask-kit` preset plus any
    committed product yaml and fails if those tests fail.

## Open questions

Plan may choose concrete encodings without Spec Change if they satisfy the
interfaces above:

- OpenCode frontmatter field names (`mode`, `permission` vs `permissions`)
  from OpenCode docs at implement time.
- Exact CLI verbs (`./ask inner-loop …` vs Implement-stage-only invocation).
- Changelog path when the product already has one (default `CHANGELOG.md`).
- Cross-runtime live-spawn matrix (file-shape is mandatory; live Codex spawn
  may remain documented best-effort).

## Source intent

`work/inner-loop-hardening/intent.md`
