# AskIt — demonstration guide

## How to use this guide

This is the rebuilt facilitator guide for an approximately 90-minute technical
session. It is intentionally shorter than the former 40-slide transcript.
The eight internal timings add to exactly 90 minutes; cue cards do not need to
show duration.

The audience is developers and technical decision-makers who want a practical
answer to one question:

> How can an AI agent do useful engineering work while a teammate can still
> reconstruct what was decided, changed, checked, and accepted?

Each section has four parts:

- **Cue card** — the short message to put on a slide or keep visible.
- **Presenter notes** — what to say, show, and ask.
- **Timing** — the facilitator budget, not a promise about discussion length.
- **Outcome** — what the audience should be able to do next.

Evidence labels used below:

- `LIVE` — an instruction to perform during the session; it is not a claim
  that the command has already run.
- `SAVED` — an existing repository artifact that can be inspected.
- `OPTIONAL` — useful follow-up material outside the main path.

The PowerPoint files in this repository are historical assets. This Markdown
guide is the source for the rebuilt demonstration flow; the deck is not
claimed to remain slide-for-slide aligned.

## Session map

| ID | Section | Internal time | Audience job |
| --- | --- | ---: | --- |
| ORIENT | Why reconstructable work matters | 8 min | Name the handoff problem |
| MODEL | Intent, labor, evidence, acceptance | 12 min | Separate execution from judgment |
| ROUTE | Repository and request routing | 10 min | Choose the right starting path |
| WALKTHROUGH | One bounded AskIt lifecycle | 20 min | Follow a change from request to handoff |
| EVIDENCE | Claims, sources, and provenance | 12 min | Test whether a result is supportable |
| RECOVERY | Refusal, drift, and continuation | 10 min | Respond safely when evidence changes |
| ADOPT | First-use exercise | 10 min | Apply the model to one real change |
| CLOSE | Reconstruct the work | 8 min | State the next bounded action |
| **Total** |  | **90 min** |  |

## ORIENT — Why reconstructable work matters

**Cue card**

> Delegate the labor. Keep the judgment. Leave a trail another engineer can
> inspect.

**Presenter notes**

**Say:** AskIt is not a promise that an agent is always right. It is a working
model for making delegated engineering work legible: the human owns the
consequential intent and acceptance decision; the agent performs authorized
labor; the repository retains the contracts and evidence.

**Show:** `README.md` and the session map above. Do not start with a command
tour. Start with the reconstruction problem: a chat message saying “I
improved it” does not identify the goal, source revision, checks, or authority
to accept the result.

**Ask:** “What would you need before trusting a handoff from an agent?”
Collect two answers, then group them as purpose, source identity, evidence,
and acceptance.

**Timing:** 8 minutes.

**Outcome:** Participants can name at least three facts that a useful handoff
must preserve beyond the agent's prose.

## MODEL — Intent, labor, evidence, acceptance

**Cue card**

> AskIt separates four things: **intent**, **labor**, **evidence**, and
> **acceptance**.

**Presenter notes**

**Say:** Intent answers What and Why. Labor is the scoped work an agent may
perform. Evidence says what actually happened and where it can be checked.
Acceptance is the human authority decision. These are related, but none
substitutes for another.

**Show:** The repository's `AGENTS.md` route gate and
`_ask/policies/delegation.md`. Point out that autonomy operates inside an
authorized scope and that consequential changes to What, Why, invariants, or
acceptance are escalation points.

**Ask:** “Which of these can a passing test replace?” The answer is: none.
A test can support an evidence claim; it cannot invent intent or grant
acceptance authority.

**Timing:** 12 minutes.

**Outcome:** Participants can classify a statement as intent, labor, evidence,
or acceptance and identify where human judgment remains required.

## ROUTE — Repository and request routing

**Cue card**

> Route the request before choosing the workflow.

**Presenter notes**

**Say:** AskIt distinguishes a bug fix from a feature and from a mixed
request. A reported defect starts with reproduction against the existing
expectation. A changed expectation follows the feature path. Foggy feature
destinations may use Explore before Intent; clear destinations can skip it.

**Show:** `AGENTS.md`, `_ask/policies/workflow.md`, and the repository layout.
Explain that `.agents/ask/` is the canonical stage source and `_ask/` contains
the guide, policies, templates, and scripts. Runtime projections are not a
replacement for the source contract.

**Ask:** Route three short examples:

1. “The command now rejects a valid file.” → bug fix, reproduce first.
2. “Add a provenance record to every experiment.” → feature.
3. “The old flow is broken, and we also want a new approval step.” → mixed;
   separate the reproduced defect from the expectation change.

**Timing:** 10 minutes.

**Outcome:** Participants can route a request and name the evidence needed
before implementation starts.

## WALKTHROUGH — One bounded AskIt lifecycle

**Cue card**

> Request → route → intent → contract → plan → implement → review → verify →
> accept.

**Presenter notes**

This is the main demonstration. It is a **LIVE** command walkthrough when run
in a disposable repository. It is not a claim that these commands ran while
this guide was written.

1. **Start clean.** Show `./ask check-clean`. A refusal protects existing
   work; it is not an inconvenience to bypass.
2. **Create the workstream.** Use `./ask start-work <work-id>` from the
   approved base. The branch and seeded artifacts make the work locatable.
3. **Make intent explicit.** Record What, Why, non-goals, assumptions, and
   the E2E applicability decision. Ask for the complete intent approval.
4. **Specify observable behavior.** Put acceptance criteria and stable
   criterion IDs in `specs/current/`. Keep implementation preferences out of
   the requirement.
5. **Plan evidence before code.** Bind tasks to owned paths and verification.
   Review the exact plan before implementation.
6. **Implement in bounded steps.** The agent may make routine changes inside
   the approved scope. Meaning changes require the appropriate decision.
7. **Review and verify independently.** Review is not acceptance. Verification
   must use current source and current evidence.
8. **Accept or refuse.** `record-result` records the workstream result; the
   submitted acceptance decision remains the authority boundary.

**Show:** `_ask/docs/demo/end-to-end-plan.md` for the facilitator's canonical
demo sequence. Use `./ask --help` for the current command surface rather than
copying a stale command list into the presentation.

**Ask:** At each step, “What becomes reconstructable here?” Keep the answer
concrete: a branch, a document, a criterion, a test, a review record, or an
acceptance decision.

**Timing:** 20 minutes.

**Outcome:** Participants can trace one bounded request through the major
AskIt artifacts and explain why each artifact exists.

## EVIDENCE — Claims, sources, and provenance

**Cue card**

> A result is only as strong as its source, identity, and authority.

**Presenter notes**

**Say:** Evidence is not a confidence score. It is a claim tied to a source
path, a source revision, and an observation that another person can inspect.
Saved artifacts preserve history; they do not become current merely because a
guide mentions them.

**Show:** `_ask/docs/spec-test-traceability.md` and
`_ask/docs/workflow-references.md`. Contrast:

- “The check should pass” — a **LIVE** instruction.
- “This saved report records a pass at commit X” — **SAVED** evidence.
- “Try the optional experiment later” — **OPTIONAL** material.

**Ask:** “What would make this claim fail?” Accept answers such as a missing
path, stale commit, unsupported citation, changed source after review, or a
review that did not inspect the relevant behavior.

**Timing:** 12 minutes.

**Outcome:** Participants can challenge a result by asking for its path,
revision, observation, and authority instead of accepting a bare assertion.

## RECOVERY — Refusal, drift, and continuation

**Cue card**

> Refuse unsafe continuation. Resume authorized work, not a guess.

**Presenter notes**

**Say:** A clean-tree refusal, stale review, changed destination, failed
verification, or missing evidence is a meaningful state. The safe response is
to preserve the evidence, identify the exact conflict, and route the decision;
not to relabel failure as success.

**Show:** `_ask/policies/worktree.md`, `_ask/policies/workflow.md`, and
`AGENTS.md` continuation guidance. Explain the difference between:

- continuing the named workstream at its authorized endpoint;
- starting a new feature from a clean base; and
- changing the accepted What/Why, which requires a scope-change decision.

**Ask:** “Review passed, then the code changed. What do you do?” The answer
is to re-establish current evidence and review continuity. Do not claim that
the old review covers the new source.

**Timing:** 10 minutes.

**Outcome:** Participants can describe a safe response to stale evidence or a
changed destination without silently widening scope.

## ADOPT — First-use exercise

**Cue card**

> Choose one bounded change. Make its purpose, evidence, and acceptance
> visible.

**Presenter notes**

Give each participant one small change from their own repository. Ten minutes
is enough for a paper or terminal sketch; a full production implementation is
not required.

Ask them to write:

1. the request route: bug, feature, or mixed;
2. the What and Why;
3. one non-goal and one assumption;
4. one observable criterion;
5. the source or test that would support it; and
6. the human decision that would accept or refuse the result.

Invite two people to read their route and criterion. Correct only the
boundary: an implementation detail is not a requirement, and a test result
is not acceptance authority.

**Timing:** 10 minutes.

**Outcome:** Each participant leaves with a bounded first workstream proposal
that another engineer could understand without the original chat.

## CLOSE — Reconstruct the work

**Cue card**

> Could a teammate reconstruct the work from the repository?

**Presenter notes**

Return to the opening question. Ask the audience to reconstruct the
walkthrough in six sentences: purpose, route, authorized labor, observable
evidence, review/verification status, and acceptance authority.

Close with the adoption rule: start with one bounded change, keep the kit's
canonical documents close to the work, and preserve uncomfortable facts such
as refusal, failure, and stale evidence. The goal is not more ceremony. The
goal is a handoff that survives the absence of the original conversation.

**Timing:** 8 minutes.

**Outcome:** Participants can state the next bounded adoption step and the
minimum evidence they will require from it.

## Evidence inventory

The inventory is the authority for demonstration status. Each key occurs once.
`LIVE` means an instruction, not completed execution.

| Key | Label | Item | Path or evidence |
| --- | --- | --- | --- |
| E-01 | LIVE | `./ask check-clean` walkthrough | Current command surface |
| E-02 | LIVE | `./ask start-work` walkthrough | Current command surface |
| E-03 | LIVE | Intent/spec/plan lifecycle | `_ask/docs/demo/end-to-end-plan.md` |
| E-04a | SAVED | Route and continuation source | `AGENTS.md` at `8f39ecd5f58c9c38def247007c1365c4036052bd` |
| E-04b | SAVED | Canonical stage sources | `.agents/ask/stages/` at `bc0f332cc7f7ea952a48a2cab9394ef59d0d47bb` |
| E-04c | SAVED | Delegation and workflow policy | `_ask/policies/delegation.md` and `_ask/policies/workflow.md` at `336133642b08440a5fbc33f1863699febbb6bb16` and `bc0f332cc7f7ea952a48a2cab9394ef59d0d47bb` |
| E-05 | SAVED | Traceability contract | `_ask/docs/spec-test-traceability.md` at `a3e2c6932dad29faf44ec6cbce13770f51d460ec` |
| E-06 | OPTIONAL | Two-moons experiment | `_ask/docs/demo/end-to-end-plan.md` at `10816d39c1c2ce3fdc9f703394bbf7e3be11e588`; not executed for this guide |
| E-07 | OPTIONAL | Historical shorter-hashes evidence clinic | `work/shorter-hashes/` at `8d96ffd`; not the primary path |

## Citation inventory

Every workflow claim cited in this guide is reviewed against a path and
passage. `SUPPORTED` is the only passing support value.

| Claim group | Source path | Passage to inspect | Decision |
| --- | --- | --- | --- |
| Kit purpose and command entry point | `README.md` | AskIt overview and command surface | SUPPORTED |
| Routing and continuation | `AGENTS.md` | Request route and continuation rules | SUPPORTED |
| Feature/bug workflow | `_ask/policies/workflow.md` | Request route gate and on-path flow | SUPPORTED |
| Delegated authority | `_ask/policies/delegation.md` | Autonomous and escalation boundaries | SUPPORTED |
| Demo lifecycle | `_ask/docs/demo/end-to-end-plan.md` | Facilitator sequence | SUPPORTED |
| Evidence and traceability | `_ask/docs/spec-test-traceability.md` | Contract and completion evidence | SUPPORTED |
| Workflow references | `_ask/docs/workflow-references.md` | Reference and provenance commands | SUPPORTED |
| Worktree safety | `_ask/policies/worktree.md` | Clean-tree and preservation boundaries | SUPPORTED |
| Stage source of truth | `.agents/ask/stages/` | Stage contracts | SUPPORTED |

## Parity record

The Persian guide must contain one `MATCH` or `MISMATCH` decision for each
dimension below before release. Natural Persian wording is expected; meaning
parity is not line-by-line translation.

| Dimension | Expected | Decision |
| --- | --- | --- |
| Section IDs and order | ORIENT → MODEL → ROUTE → WALKTHROUGH → EVIDENCE → RECOVERY → ADOPT → CLOSE | MATCH |
| Audience outcomes | Same eight section outcomes | MATCH |
| Internal timing | Eight numeric timings total 90 minutes | MATCH |
| Lifecycle | Request through acceptance | MATCH |
| Evidence labels | LIVE, SAVED, OPTIONAL | MATCH |
| Ownership boundary | Human intent/acceptance; delegated scoped labor | MATCH |
| Primary/optional status | Walkthrough primary; clinics optional | MATCH |

## Baseline and compression record

Baseline source commit:
`2e5ea92989c48c10e4829bc22c325643443a38b3`.

Count physical lines with `wc -l`, including blank lines:

```text
English baseline: docs/AskIt-demonstration-notes.md at baseline commit
Persian baseline: docs/AskIt-demonstration-notes-fa.md at baseline commit
Reduction rule: (baseline_lines - rebuilt_lines) / baseline_lines >= 0.35
```

The rebuilt guide preserves the safety boundary checklist: core model, human
ownership, evidence discipline, recovery/refusal, and failure boundaries.
