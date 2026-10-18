# Inner task loop

This is the canonical lifecycle for each implementation task when a task graph
is active. The current task graph owns task order, dependencies, steering paths,
retry limits, and evidence transitions.

## Lifecycle

For each behavioral slice, capture the failing behavior at an immutable Red
revision, implement the smallest Green change, then Refactor while preserving
behavior and keeping the checks green. Once the task's slices are complete,
request an independent review of the current candidate. A structural cleanup
does not need a manufactured behavior test; explain its classification and keep
existing checks green. Record an explicit no-applicable-cleanup outcome when a
Refactor pass finds nothing useful to change; do not invent cosmetic edits.

Classify by task responsibility, not only by file ownership. A local suggestion
is code introduced or directly affected by this task, within its task outcome.
A broader suggestion concerns work beyond the task outcome, even when its files
match a wide `owned_paths` glob. If the boundary is ambiguous or a required fix
is unsafe, stop and escalate instead of treating it as local cleanup.

Resolve review findings by class:

- **Local structural suggestion:** complete every valid suggestion within the
  task's owned paths, then request fresh review of the changed candidate.
- **Existing-spec behavior defect:** add a failing regression and run another
  Red -> Green -> Refactor cycle before fresh review.
- **Broader horizontal refactor:** leave the implementation unchanged and keep
  an attributed `.later` draft tagged `refactoring` for coordinator review.
- **Meaning, behavior, or contract change required:** stop and use Spec Change;
  do not call it optional refactoring or expand the task silently.
- **Mistaken or withdrawn finding:** preserve evidence and the reviewer's
  evidence-backed withdrawal; do not describe unfinished local cleanup as
  complete.

After any candidate change, discard stale approval, rerun applicable checks,
commit the candidate, and obtain independent review bound to that exact
candidate. The coordinator integrates only after the current candidate has
approved review and passing checks. Failed checks, stale/rejected approval, or
exhausted retries block or escalate; they never authorize integration.

The reviewer records broader-refactor drafts in the candidate-bound runtime
review evidence at `work/<work-id>/inner-loop/evidence/`, including a stable
slug, source task, reviewer/finding identity, candidate SHA, affected task
responsibilities, proposed What/Why, and publication status. On interruption,
the coordinator recovers this handoff from the exact candidate review evidence,
deduplicates it against existing cards by slug and substance, and preserves its
status. Do not create or commit `.later` source cards while any writer or
resumable candidate remains. Only after all candidates integrate and no writer
remains may the coordinator materialize drafts from `_ask/templates/later-work.md`
and publish them through normal `develop` integration. Do not switch a task
writer's branch to publish a card.

The outer workflow still performs aggregate verification and Accept. It does
not add unconditional task Review or Refactor passes outside this loop.
