# Explore Map: Concurrent inner-loop hardening

## Destination

Define an ownable change that adds a resumable, concurrent subagent implementation
inner loop; deterministic TypeScript and Python verification presets; and OpenCode
and Codex bindings generated from one portable source of truth.

## Notes

- Human authority, worktree safety, evidence provenance, and Accept remain outer-loop constraints.
- Explore should borrow mechanisms from cc-sdd and Learn Harness Engineering without importing a second SDLC.
- `codebase-design` is approved for locating the inner-loop seam.
- Comparison context: ASK is the outer governance/evidence protocol; OpenSpec is its
  specification engine; cc-sdd contributes task-local implement/review/debug dispatch;
  Learn Harness Engineering contributes instructions/state/verification/scope/lifecycle checks.

## Tracker map (optional)

- No external tracker map yet; this file is canonical.

## Decisions so far

- Keep ASK as the outer governance protocol.
- Keep pinned OpenSpec as the specification/change engine.
- Add borrowed mechanisms inside the Implement-to-Verify inner loop.
- Support TypeScript and Python project hardening first.
- Generate Cursor, Codex, and OpenCode runtime bindings from one portable source.
- Concurrent subagents must preserve task isolation and deterministic aggregation.

## Not yet specified

- The exact inner-loop module interface and persistent task state.
- Concurrency policy, conflict prevention, cancellation, retry, and resume semantics.
- Whether concurrency uses worktrees, non-overlapping paths, or both.
- TypeScript and Python check discovery, baseline adoption, and failure policy.
- Canonical `.agents/` layout and generated runtime-specific projections.
- Compatibility and migration for existing `_ask/agents/`, bindings, and generated files.
- Acceptance criteria and test matrix across Cursor, Codex, and OpenCode.

## Out of scope

- Building a custom model runtime.
- Supporting languages beyond TypeScript and Python in this workstream.
- Replacing OpenSpec or weakening existing worktree, verification, or acceptance gates.
- Automatically deploying or merging product changes.

## Handoff to Intent

Pending Explore decisions. Do not enter `01 Grill` yet.
