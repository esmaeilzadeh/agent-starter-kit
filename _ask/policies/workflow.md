# Workflow guidance (not a lock)

The kit’s default feature path is Explore (when facts are missing) → Grill → Spec → Challenge → Plan → Implement → Review → Resolve findings (08 Refactor) → Verify → Accept.

## Request route gate

Run this gate after continuation recovery and before choosing any stage prompt,
slash command, or skill. Classify each independently deliverable outcome against
the accepted expected behavior. State the route and its evidence before any
stage-specific question or action; do not continue until every outcome has a
route:

- **Bug fix:** reported behavior violates an existing contract. Start from the
  reporter’s context and reproduce the fault.
- **Feature:** the request adds behavior or changes the existing contract. Use
  the feature path.
- **Investigation:** the requested outcome is evidence or an answer. Use Explore
  to inspect the system, read documentation, reproduce behavior, or experiment.
- **Review:** the requested outcome is an assessment of existing work. Use Review
  against the named revision, requirements, and project policy; report findings.
- **Maintenance:** the requested outcome preserves behavior, such as structural
  refactoring or documentation upkeep. Record the boundaries to preserve and use
  the scoped maintenance path below.
- **Mixed request:** separate independently deliverable outcomes by route, each with
  its own scope and evidence. Record dependencies and run overlapping work in
  sequence.

If expected behavior is needed for the requested outcome but unclear, investigate
the existing contract first; ask the human about unresolved behavior choices.
Do not force an evidence, assessment, or behavior-preserving outcome into a
feature or defect category. A direct stage
invocation does not bypass this gate. Do not make a reported defect enter the
feature path because the report mentions possible edge cases or because an
accepted guard has no historical Red.

That feature path is **guidance**. It must not feel like a lock, and it must not feel like optional paperwork you can omit while still “on the kit.” The request route gate remains mandatory for every path.

## Investigation, review, and maintenance

Record the requested question or deliverable, scope, exclusions, source revisions,
and completion evidence in the work record. The request authorizes that bounded
outcome; clarify missing goals or tradeoffs through Grill when needed. These
routes do not require a new feature spec, complete-intent approval, TaskGraph,
or manufactured Red test. `check-workstream`'s feature gates do not apply to them.

- **Investigation:** finish with findings, sources or experiment results, and
  remaining limitations. A standalone research request stops there; a feature
  investigation hands evidence and remaining human decisions to Grill.
- **Review:** finish with findings tied to the assessed revision and evidence.
  A review request alone does not authorize implementation of its findings.
- **Maintenance:** record the existing contract and invariants to preserve, make
  the scoped change, review it, and run applicable verification. Structural
  refactoring keeps existing checks green; use a TaskGraph's structural exemption
  if one is already active. Documentation upkeep checks accuracy and consistency.

Keep applicable clean-tree, branch, risk, commit, and evidence rules. Investigation
and review may inspect without creating an implementation scaffold; retain their
report in the requested destination. For maintenance implementation, use a work
branch and a concise work record instead of a new feature spec/plan. Standalone
maintenance starts on `maintenance/<work-id>` from `develop` with a scope record
under `work/<work-id>/`; `start-work` seeds an `agent/` feature scaffold instead.
Run repository-level `./ask verify` with no `ASK_WORK_ID` override: it executes
the CheckPlan and records the candidate SHA without feature traceability gates.
This route applies only to standalone maintenance. If an
Engineering Model or TaskGraph already governs the work, preserve its links and
evidence and its existing verification gates; branch or environment changes do
not remove that authority. Findings outside the requested outcome are proposals, not permission
to repair or implement. Route authorized follow-up work explicitly; behavior
changes require the feature path and defects require reproduction first.

## Explore and Grill entry

Ask two separate questions: **Are facts missing?** Use 00 Explore. **Are goals,
assumptions, or tradeoffs unresolved?** Use 01 Grill. Use either or both as needed;
an unclear goal alone does not require research, and a clear goal may still need
technical investigation. Direct stage requests retain the request route gate.

Explore records evidence about the existing system, technologies, external
constraints, prior solutions, and documentation or web sources. Its feature
handoff must name the evidence gathered, remaining gaps, and human decisions;
open preference questions belong in Grill and do not block that handoff. A
standalone investigation ends with its report. If a feature needs no Explore,
omit `explore-map.md` and record `Explore skipped: evidence sufficient for intent.`
in its intent. Existing skip records remain valid; do not rewrite approved intent.

## Intent approval and specification authority

Approval covers the stated What, Why, constraints, and assumptions, not every
possible detail of a later specification. Agents may derive details supported by
those approved statements and existing accepted contracts. Record the source or
reasoning for derived requirements in the spec. An engineering implementation
choice within those boundaries remains delegated work.

When materially different product behaviors remain possible, present the choice
to the human and wait before dependent work. For example, approval of “customers
can cancel orders” alone does not choose a cancellation deadline. Model confidence
or consultation cannot authorize that choice. Record an answer that elaborates
approved intent in the spec with its decision evidence. If it changes What, Why,
an approved assumption, or an established contract, use Spec Change and the
required revised-intent approval. Mark a prepared spec CURRENT only after its
behavior choices are supported or resolved; approval of intent is not a blanket
approval of agent-invented requirements.

## Reproduced bug fixes

When a request reports a defect, compare the observed behavior with the
existing accepted contract and reproduce the reported fault first. If it
reproduces, reuse that contract and record only the observed/expected behavior,
reporter reproduction, focused regression test, minimal fix, and verification.
Do not create a new feature spec/plan or tests for hypothetical failure modes.
Keep Red focused on the reproduced defect; existing accepted edge guards are
Green checks, not separate Red targets. Run the relevant broader suite at the
task's verification boundary.

If the fault does not reproduce, record what was tried and gather evidence
without inventing a Red or a fix. If expected behavior is undefined or the
requested correction changes it, use the feature path and its normal Spec and
Plan gates.

## On the path (default)

If the human is using the kit:

1. **Artifacts are not optional** on the feature path (`01`–`10`). Each next stage stands on the previous document (intent, spec, plan, …). A reproduced bug fix reuses the existing contract and a concise repair record instead of creating a new feature spec and plan.
   **00 Explore is the exception:** omit it when the evidence is sufficient for Intent. When 00 runs for a feature, `explore-map.md` is required and Handoff must be non-empty before 01. Follow the Explore and Grill entry rules above.
2. **Prepare, then continue.** The agent writes the artifact for the current stage and proceeds after its exit criteria, within the specification authority above. Route uncertainty by what is missing using the escalation rules below; human authority and preference questions go directly to the human. Once a gate passes, continue through the authorized work without asking that decision again. If a required gate is missing, stale, or declined, present that exact unresolved decision immediately and wait before dependent work; retain prior decisions.
3. **Skip = skip extra approvals, not documents.** Every required confirmation is a question with explicit selectable choices, such as **Approve complete intent and assumptions** / **Request changes**, plus an optional comment that can accompany a selected choice in the same response. A preselected option is not approval. Never ask the human to write or repeat a confirmation sentence. Use a native choice control only when callable for the current mode/question and capable of retaining both values; otherwise present numbered options and invite the selected number or label plus added text in the same reply. Accept concise affirmative text sent unsolicited for compatibility, record its exact text with `--response`, and never make the human restate it. Record intent approval with `./ask confirm-intent --work-id <id> --choice approve`. This confirmation authorizes later artifacts only within the specification authority above; unresolved product choices still need a human decision. Mark a spec CURRENT only when its behavior choices are supported or resolved and the human has not asked to stop. Do not re-ask a bless on Plan / Review / Refactor. When What, Why, or assumptions change, present the scope-change proposal and the complete revised intent together as one decision; a single submitted approval may authorize both the linked change and that exact intent. Record the approved intent and its digest, and never ask sequentially for those same approvals. Keep distinct choices separate when they authorize unrelated decisions.
4. **Second confirm: Accept.** Present **Accept workstream** / **Request changes** as selectable choices and close only after a submitted Accept choice, subject to delegation policy (evidence + commit SHA).
5. **Missing artifacts but still on the feature path:** prepare them from the accepted defaults, present a required choice only if its decision has not happened yet, then continue. Do not jump to feature implementation with an empty `plan.md` / no spec. A reproduced bug fix follows the short path above.

`./ask check-workstream <work-id>` is the machine check that the **default path is complete**. Exit non-zero means “incomplete,” not “forbidden.” On-path response: prepare what is missing.

### Model decisions

Grill records one complete model plan in `work/<work-id>/models.yaml`, including runtime, resolved stage roles/models, exact exceptions, and implementation update policy. This model choice is separate from approval of `intent.md` and from final Accept. Challenge and Review reuse the saved plan without routine model or same-family confirmation. A legacy workstream without the new policy keeps its configured implementor until its next authorized Grill or explicit policy change; do not infer historical consent.

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

`/off-path` (`.cursor/commands/off-path.md`, source `_ask/cursor-commands/off-path.md`) switches **only the current chat**. Warn once, then follow the requested implementation style. It does not bypass request routing, reproduction of a reported bug, or the separation of mixed work. Do not write `work/*/kit-path` or record off-path in `intent.md`.

A new chat is on-path again. Saying “skip the kit” / “just code” in an on-path session has the same session-only effect for feature-workflow artifacts (warn once, follow) without needing the slash command. The request route gate still applies.

## Still hard (safety, not ceremony)

- Dirty worktree without grilling (`_ask/policies/worktree.md`)
- Explicit Grill choice approving the complete intent and assumptions, recorded against the exact `intent.md` digest. `./ask check-workstream` refuses implementation when it is missing or stale; implementation permission or a broad direction choice is not a substitute.
- Silent stash/reset
- Claiming verify/accept without running checks or recording a commit SHA
- Changing What/Why or acceptance criteria without Spec Change (or a new defaults confirm that owns that change)

## Status

`./ask status` may flag `code-without-plan` on a **live** branch that changed files outside `work/<id>/` and `specs/` while stage is still `seeded` / `explored` / `intent`. Signal that labor left the path without artifacts — not a failure by itself.

Parked later-tasks in `.later/` are not live. `./ask status` reads committed cards from `develop` (or its remote-tracking ref) on every checkout.

## Model-confidence escalation

First identify what is missing, regardless of confidence:

- **Facts:** investigate documentation, code, observed behavior, or an experiment
  within the authorized scope. Record evidence and remaining gaps; if access or
  an environment is unavailable, record the blocker and seek the needed input.
- **Authority or preference:** present evidence and choices to the human and
  wait before dependent work. Consultation cannot supply this decision.
- **Technical judgment over sufficient evidence:** assess confidence as a
  supporting, subjective signal and use the configured consultation ladder below.

For consequential technical judgment, continue autonomously only when confidence
is **above 90%**, within authorized scope and with required checks. At **90% or below**, consult
the next distinct model/settings rung configured for the active runtime, once
per rung, before asking the human. Give each assessor the decision, scope,
evidence, uncertainty, and earlier assessments. Skip a rung already satisfied
by an earlier assessment of the same decision from that rung or a later rung
in the same configured ladder. Use the runtime's supported model-selection/
spawn mechanism and verify the actual model/settings; unavailable or
unverifiable rungs count as unavailable. Record the assessment, confidence,
and actual model/settings in the existing work artifact; confidence is not a
measured probability or verification evidence.

Use only the active runtime's configured `confidence_escalation` ladder. Each
runtime binding defines its native model names and optional effort settings;
project and workstream model settings may override that runtime's ordered list.
Do not infer a ladder from another runtime's role names or model defaults.
Current-session capability evidence must verify each selected model and effort
before dispatch. Report unverified or unavailable rungs as unavailable.

Model consultation cannot approve a scope or acceptance change, supply human
preference or authority, authorize destructive or production-impacting actions,
override explicit user model restrictions, replace an assigned independent
reviewer, or waive required verification. Ask the human when the configured
ladder is exhausted and uncertainty remains material, or when the decision
requires human authority or preference.

Use `model-decisions.py decide --work-id <id>` with a JSON request on stdin.
Bind each decision to its ID, material evidence digest and current session ID.
Supply current native tool metadata or an authenticated runtime-adapter catalog
with exact supported models/efforts. A binding entry alone proves no availability.
The result is `investigate`, `continue`, an exact `consult` request, or `ask-human` with a reason.
Execute consultation with the native agent tool, record returned model/effort,
confidence and assessment, then resubmit the same decision with that assessment.
The `consult` CLI operation supports an installed runtime adapter; a timeout,
permission failure or unverifiable returned identity records an unavailable rung.
Use existing work records for these assessments. Reuse only assessments of the
same material decision/evidence in the current session; consult each rung once.
Explicit authority decisions remain human decisions regardless of confidence.

Set `uncertainty_kind` to `facts` or `judgment` on decision requests. Missing facts
produce `investigate` before either continuation or consultation, even at high
confidence. Existing callers that omit this field retain `judgment` semantics;
new stage decisions must classify it explicitly. On `investigate`, gather and
record the missing evidence, update its digest, then reassess. Do not repeat
model assessments to fill a factual gap. A consultation that discovers missing
facts returns `uncertainty_kind: facts` and routes back to investigation.
