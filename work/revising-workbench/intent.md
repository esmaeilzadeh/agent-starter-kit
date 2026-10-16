# Intent: Understand work, its delivery and its evidence

Status: PROPOSED.
Explore skipped: destination already clear.

## What

Build a repository workbench for the developer returning to their own work.
Opening an Epic, Story, Scenario or Task restores enough context to understand
its purpose, promised behavior, delivery work and evidence without chat history.

An existing Story or Task is a valid starting point. Resolve the subject from the
request and known repository context before creating execution work. Reuse known
identities, explain the bounded contribution and ask about material conflicts.
A new chat or branch does not automatically create an Epic. Missing ancestors
remain visible; the developer does not have to invent a hierarchy to inspect work.

Define an Epic with a user, purpose, outcome, scope and completion conditions.
Stories express user outcomes; Scenarios express concrete flows. Tasks are visible
delivery units and can support several Stories or Scenarios through one identity.
Features represent related capabilities without requiring another navigation tier.

At each entry, show meaningful definitions and the relevant specification passage
and plan entry in context. Preserve the initiating route while navigating shared
work. From a concrete Scenario, show its actual Test coverage, understandable
setup/action/assertion and necessary helper or fixture context. Show genuine
recorded outcomes with their source, revision and applicability. Make missing,
failed, stale and historical evidence explicit.

Demonstrate one complete representative Story through a real Task, concrete
flow, selected Test and genuine retained result, alongside a successful human
readability exercise. Relationship and entry behavior must work generally.

## Why

The returning developer needs to remember what the work promises, why it exists
and what remains to do. Titles, IDs, links and generic pass labels leave them
reconstructing meaning from chat, source files and logs. Connected context and
understandable evidence let them assess progress and choose the next action.

## Non-goals

Mandatory Epic/Story membership; reconstructing all historical planning; an
external backlog database or tracker API integration; changing evidence or
acceptance authority; automatic test execution or acceptance; inline specification
editing; replacing the frontend; deployment, merge or push. This task stops at
preparing the specification and does not implement the product.

## Known assumptions

1. The intended user is the developer returning to their own repository.
2. A Story may contain one or multiple concrete Scenarios. Optional containment
   and shared support relationships remain distinct from execution ownership.
3. Concrete flows select canonical case definitions; shared criterion identity
   alone does not establish that a Test covers a particular flow.
4. Product, execution and external-reference identities remain distinct. Definition
   lifecycle cannot overwrite recorded execution or verified completion.
5. Context references are revision-bound. Invalid paths/selectors block admission;
   safe missing or ambiguous passages remain inspectable limitations and block
   only actions that require those passages.
6. Definitions and their code/test relationships remain versioned in the repository.
   The workbench inspects those sources and existing evidence authorities.
7. The representative journey requires a genuine retained result and successful
   candidate-bound comprehension. Missing evidence or failed comprehension leaves
   the demonstration incomplete; relevant changes invalidate its review.
8. Existing guarded mutations, decision forms and historical inspection safeguards
   remain in force. Future schema adoption needs explicit reviewed migration.

## Open questions

The proposed specification defines the concrete behavior and representative
example. Complete-intent confirmation and independent review of the revised
specification remain pending before planning or implementation.

## Human decisions

The human requested a fresh specification with the challenge corrections applied
inside its requirements, in `work/revising-workbench/`, on `revising-workbench`.
They required the intent to describe the product rather than file relocation or
inherited workstream history. No product implementation is requested here.

## E2E

Applicability: applies to future product behavior.

Journeys: direct Story/Task entry; standalone records; shared Task navigation and
Back; two concrete flows sharing a criterion; subject conflicts; spec/plan context
and missing/ambiguous passages; helper-dependent Test inspection; a genuine result
and its applicability; successful human comprehension without chat assistance.

Use test-owned temporary repositories, fixtures and browser/server processes with
teardown. Preserve genuine committed pilot and historical evidence. Automated
checks and a candidate-bound human readability exercise are both required.
