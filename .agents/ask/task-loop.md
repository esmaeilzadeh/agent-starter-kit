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
existing checks green.

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

The coordinator retains attributed later-card drafts and publication status
across interruptions. Publish those cards through normal `develop` integration
only after all task candidates have integrated and no writer or resumable
candidate remains. Do not switch a task writer's branch to publish a card.

The outer workflow still performs aggregate verification and Accept. It does
not add unconditional task Review or Refactor passes outside this loop.
