# Workflow guidance (not a lock)

The kit’s default feature path is Explore (if foggy) → Grill → Spec → Challenge → Plan → Implement → Review → Refactor → Verify → Accept.

That path is **guidance**. It must not feel like a lock, and it must not feel like optional paperwork you can omit while still “on the kit.”

## Reproduced bug fixes

When a request reports a defect, compare the observed behavior with the
existing accepted contract and reproduce the reported fault first. If it
reproduces, reuse that contract and record only the observed/expected behavior,
reproduction, focused regression test, minimal fix, and verification. Do not
create a new feature spec/plan or tests for hypothetical failure modes. Keep
Red focused on the reproduced defect; existing accepted edge guards are Green
checks, not separate Red targets. Run the relevant broader suite at the task's
verification boundary.

If the fault does not reproduce, record what was tried and gather evidence
without inventing a Red or a fix. If expected behavior is undefined or the
requested correction changes it, use the feature path and its normal Spec and
Plan gates.

## On the path (default)

If the human is using the kit:

1. **Artifacts are not optional** on the feature path (`01`–`10`). Each next stage stands on the previous document (intent, spec, plan, …). A reproduced bug fix reuses the existing contract and a concise repair record instead of creating a new feature spec and plan.
   **00 Explore is the exception:** it is an optional on-ramp. When the destination is already clear enough for Intent, **omit 00** (real skip). That is not “on-path with a missing explore-map.” When 00 *runs*, `explore-map.md` is required and Handoff must be non-empty before 01. See `AGENTS.md` item 1 and `.agents/ask/stages/00-explore.md`.
2. **Prepare, then continue.** The agent writes the artifact for the current stage and proceeds to the next. Auto-continue in the same conversation after exit criteria; stop for human judgment at the required choice questions below (and escalation). Once a gate passes, continue through the authorized work without asking that decision again. If a required gate is missing, stale, or declined, present that exact unresolved decision immediately and wait before dependent work; retain prior decisions.
3. **Skip = skip extra approvals, not documents.** Every required confirmation is a question with explicit selectable choices, such as **Approve complete intent and assumptions** / **Request changes**, plus an optional comment that can accompany a selected choice in the same response. A preselected option is not approval. Never ask the human to write or repeat a confirmation sentence. Use a native choice control only when callable for the current mode/question and capable of retaining both values; otherwise present numbered options and invite the selected number or label plus added text in the same reply. Accept concise affirmative text sent unsolicited for compatibility, record its exact text with `--response`, and never make the human restate it. Record intent approval with `./ask confirm-intent --work-id <id> --choice approve`. This one confirmation covers later prepared artifacts (spec marked CURRENT unless the human chose to stop, plan, review). Do not re-ask a bless on Plan / Review / Refactor. When What, Why, or assumptions change, present the scope-change proposal and the complete revised intent together as one decision; a single submitted approval may authorize both the linked change and that exact intent. Record the approved intent and its digest, and never ask sequentially for those same approvals. Keep distinct choices separate when they authorize unrelated decisions.
4. **Second confirm: Accept.** Present **Accept workstream** / **Request changes** as selectable choices and close only after a submitted Accept choice, subject to delegation policy (evidence + commit SHA).
5. **Missing artifacts but still on the feature path:** prepare them from the accepted defaults, present a required choice only if its decision has not happened yet, then continue. Do not jump to feature implementation with an empty `plan.md` / no spec. A reproduced bug fix follows the short path above.

`./ask check-workstream <work-id>` is the machine check that the **default path is complete**. Exit non-zero means “incomplete,” not “forbidden.” On-path response: prepare what is missing.

When continuing an identified workstream, first inspect its branch, artifacts,
inner-loop state, and recent commits. If an authorized next action is blocked by
a missing or stale confirmation, present that exact confirmation as selectable
choices with an optional same-response comment. If the accepted plan explicitly
stops before the next action, report that authorized scope as complete; do not
present a later-stage gate as currently missing.

An explicit later human direction can extend a previously recorded execution
endpoint. When What, Why, and assumptions stay the same, record the direction in
the plan or a scoped authorization artifact and preserve the approved
`intent.md` bytes and confirmation. Do not edit `intent.md` only to update the
authorized endpoint or progress. Request a new complete-intent choice only when
the human changes What, Why, or an assumption, and bundle it with the
scope-change decision as described above. A generic continuation request
does not override an explicit stop; an explicit endpoint direction does.

## Off the path (this session only)

Every new Cursor session starts **on-path**. There is no durable off-path flag in git.

`/off-path` (`.cursor/commands/off-path.md`, source `_ask/cursor-commands/off-path.md`) switches **only the current chat**. Warn once, then follow. Do not write `work/*/kit-path` or record off-path in `intent.md`.

A new chat is on-path again. Saying “skip the kit” / “just code” in an on-path session has the same session-only effect (warn once, follow) without needing the slash command.

## Still hard (safety, not ceremony)

- Dirty worktree without grilling (`_ask/policies/worktree.md`)
- Explicit Grill choice approving the complete intent and assumptions, recorded against the exact `intent.md` digest. `./ask check-workstream` refuses implementation when it is missing or stale; implementation permission or a broad direction choice is not a substitute.
- Silent stash/reset
- Claiming verify/accept without running checks or recording a commit SHA
- Changing What/Why or acceptance criteria without Spec Change (or a new defaults confirm that owns that change)

## Status

`./ask status` may flag `code-without-plan` on a **live** branch that changed files outside `work/<id>/` and `specs/` while stage is still `seeded` / `explored` / `intent`. Signal that labor left the path without artifacts — not a failure by itself.

Parked later-tasks in `.later/` are not live. `./ask status` reads committed cards from `develop` (or its remote-tracking ref) on every checkout.
