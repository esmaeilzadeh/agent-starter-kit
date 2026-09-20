# Intent: Concurrent inner-loop hardening

## What

Own one workstream that:

- Adds a deep, resumable concurrent runner for ASK stages 06–08.
- Coordinates a TaskGraph with dependency-aware scheduling, isolated writing
  worktrees, coordinator-owned state, deterministic integration, bounded
  implement/review/debug adapters, and conflict escalation.
- Requires vertical RED→GREEN evidence for behavior-changing tasks, with
  reviewer-checked typed exemptions for non-behavioral work.
- Replaces shell-overlay verification with a language-neutral
  CheckPlan/VerifyResult module and committed consumer-owned TypeScript/Python
  verification.
- Carries a human-confirmed E2E contract from Grill/Spec through Plan,
  Implement, and Verify.
- Enforces isolated test state through machine-checkable resource, namespace,
  cleanup, and leak rules.
- Moves canonical protocol sources to `.agents/ask/{stages,bindings,...}` while
  keeping `.agents/skills/` separate.
- Generates Cursor, Codex, and OpenCode projections from that canonical source.
- Strengthens Codex projections, tests, and documentation while retaining
  documented best-effort spawn limits.
- Adopts human-controlled Git-flow: `develop` is the integration branch;
  protected `main`, releases, tags, pushes, hotfix release, and final Accept
  remain human-authorized.

Preserve ASK's outer Grill→Spec→Challenge→Plan→Verify→Accept governance and its
dirty-tree, branch, evidence-SHA, and human-authority gates.

## Why

The current inner loop is sequential and chat-orchestrated. It lacks task
ownership, dependency scheduling, resumable state, deterministic evidence
aggregation, bounded recovery, and safe concurrent writing.

Verification is incomplete and nondeterministic: language discovery is
hard-coded in the core, missing tools can silently skip checks, empty plans can
pass, and the implementation does not reliably enforce typecheck, lint, E2E,
and state-isolation requirements.

Runtime projections lack a unified portable seam: OpenCode is absent, Codex
support is incomplete, and the current source layout does not cleanly separate
kit-owned protocol from prepared Community Skills and consumer-owned state.

## Non-goals

- Replacing ASK's outer protocol, OpenSpec when present, or human Accept.
- Importing cc-sdd, Spec Kit, Learn Harness Engineering, or another SDLC.
- Building a custom model runtime, centralized state database, transcript
  database, or unbounded autonomous debugger.
- Supporting languages other than TypeScript and Python.
- Allowing task branches to mutate coordinator state or silently resolve
  integration conflicts.
- Treating per-task checks as a substitute for outer `./ask verify`.
- Preserving compatibility with `_ask/agents/`, `_ask/bindings/`, or
  `.starter-kit/verify.conf`.
- Overwriting consumer-owned verification or state during future upgrades.
- Automatically merging, tagging, pushing, deploying, or modifying protected
  branches.
- Implementing generic in-memory production-database substitutes.

## Known assumptions

- ASK has no deployed clients, so this workstream may break the current layout
  without compatibility shims.
- Future upgrades preserve consumer-owned state and configuration unless an
  explicit migration says otherwise.
- Writing tasks use distinct Git worktrees and branches; read-only agents may
  share a checkout.
- Parallel-ready tasks own disjoint source paths. Overlapping tasks are
  serialized through the dependency DAG.
- Integration order is dependency order, then stable task ID. Unexpected
  conflicts stop and escalate.
- The coordinator exclusively owns versioned state transitions.
- Missing verification tools require human-selected interactive provisioning
  before product manifests, tool configuration, or lockfiles change.
- OpenCode format details use primary documentation during Spec/Plan.
- Codex spawning may remain best-effort where the runtime cannot reliably attach
  custom agents.

## Open questions

The accepted What/Why is closed. Spec and Plan must resolve:

- TaskGraph, coordinator state, task-result, and evidence schemas.
- Retry, cancellation, resume, stale-base invalidation, and bounded debugging.
- Generator entrypoints, overlays, install, upgrade, and migration mechanics.
- CheckPlan/VerifyResult schemas, preset provenance, brownfield baselines,
  fail-on-empty behavior, and mixed-stack/monorepo detection precedence.
- Interactive provisioning rollback.
- E2E journey, environment, data, reset, and isolation representation.
- OpenCode projection format and the cross-runtime acceptance matrix.
- Version source, changelog, release evidence, and tag convention.
- Context-engineering audit procedure before Accept.

## Human decisions

- Preserve ASK as the outer governance protocol and borrow inner-loop mechanisms
  without importing another SDLC.
- Use TaskGraph plus `work/<work-id>/inner-loop/state.json` as the runner
  interface; scheduling belongs to the runner and spawning to runtime adapters.
- Use isolated worktrees for every writer; serialize overlapping paths and
  integrate deterministically.
- Keep coordinator state single-writer and versioned.
- Keep stages 09 Verify and 10 Accept outside the concurrent runner.
- Require vertical RED→GREEN evidence with typed reviewed exemptions.
- Confirm E2E behavior with the specification before implementation.
- Use test-only ephemeral production-engine resources for integration/E2E and
  machine-check every mutable-state adapter.
- Commit consumer-owned `.agents/verification.yaml`; scaffold only when absent;
  explicit re-scaffold produces a reviewable candidate.
- Require human-selected interactive provisioning for missing tools.
- Move canonical kit sources to `.agents/ask/`; keep `.agents/skills/` separate;
  generate Cursor, Codex, and OpenCode projections.
- Use human-controlled Git-flow with `develop` for integration and protected
  `main` for releases.
- Require an independent context-engineering audit before Accept.

