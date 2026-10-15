# Intent: Understand the promise, its delivery tasks, and its evidence

## Status and scope

PROPOSED amendment, 2026-10-16. Continue `structured-agentic-environment` on
`agent/structured-agentic-environment`. Human answers to the expanded Grill
questions are recorded in `explore-map.md`; explicit approval of this complete
intent and assumptions is pending. Earlier confirmations do not approve this
amendment. The previous intent remains recoverable at commit `9f9b6bd`.

Explore ran for this amendment and handed off to Grill. The original session
stop was 02 Spec. The human subsequently explicitly requested `store the spec
start the spec challengar agent in separate clean context`. This authorizes
storing a PROPOSED draft and independent challenge now, without complete-intent
approval or promotion. Stop after reporting that challenge; do not advance to
Plan, implementation, or acceptance.
Preserve the current accepted specification and its authority while proposing
this semantic change.

## What

Distinguish the execution workstream from the product work it delivers. A new
chat or plan does not automatically create an Epic: it may continue an existing
Epic, Story or Task, or introduce bounded standalone work. Resolve available
work identity and relationships from the prompt, repository records and any
referenced tracker item/later card. Reuse established identities and explain
the inferred scope; ask only when missing or conflicting context materially
affects scope/ownership. Do not invent ancestors or force a complete hierarchy.
Task and Story entry must restore surrounding known context without requiring
the human to start from or create an Epic.

Define an Epic for this engineering environment with a concrete intended user,
purpose, promised outcome, scope, and completion conditions. Demonstrate one
complete representative user Story grounded in the existing main specification.
A Story expresses an observable user outcome; its Scenarios describe separate
concrete flows. Features describe capabilities linked to Stories rather than
requiring exclusive Story containment. Use only concepts that carry useful
meaning, drawing on established software engineering practice.

Tasks are explicit units of delivery work, visible from the related Story and
Scenario. A Task can support multiple Stories or Scenarios without duplicated
identity or contradictory status. Ask's relationship behavior must work across
supported records, not only through hard-coded links for the chosen example.
One complete Story bounds demonstration coverage; it does not reduce the
relationship behavior to a demonstration-only special case.

The intended user is the human returning to their own work. Opening the Epic,
Story, Scenario or Task must restore enough context to understand what the work
means and why it exists. Show the relevant passage of the main specification
and the related plan task/entry in context, with source links and identity.
Titles, IDs, cryptic summaries and links alone are insufficient. Preserve
context while moving from the promise to its delivery and evidence.

Support a connected inspection journey: Epic purpose -> Story outcome ->
Scenario flow -> related Tasks -> Tests -> actual results and evidence. Tasks
must be visible and meaningful participants in that journey. Shared Tasks and
related capabilities are relationships, not fabricated exclusive ownership.

Tests and evidence must be human-readable and explicitly connect to the
Scenario and Task. A human must be able to understand the setup, action,
expected behavior, actual recorded result, and what the assertion establishes.
Helpers and globals remain acceptable; expose the relevant definitions and
provide explanatory comments/context where their role would otherwise be
opaque. Generic pass labels, unexplained fixture values, and decontextualized
function excerpts do not establish comprehensible evidence. Preserve genuine
missing, stale, failed, historical and unavailable states without inventing runs.

Story membership remains optional everywhere, including the pilot. Keep genuine
missing memberships visible. Remove the older harness-review example from the
main pilot presentation while preserving its original records and evidence.
Show relevant specification text inside the detail view with its source;
new inline specification-authoring workflows are outside this correction.

## Why

The human should not have to discover routine scope and entry-point omissions
for Ask. During clarification and specification drafting, Ask must test its
assumptions with concrete counterexamples instead of merely asking the human
to refine an assumed hierarchy. Findings are in `spec-gap-notes.md`.

The current Epic and sparse model do not help the human understand what was
promised or how the displayed work relates to it. Previous evidence demos were
too vague and depended on unexplained helpers/globals. The human must recover
the work's context without reconstructing chat history, and inspect a concrete
behavioral claim through its delivery work and understandable evidence.

## Observable acceptance direction

- A request referencing existing work reuses its identity and scope; an
  existing Story/Task is a valid entry point, and no automatic Epic is created.
- Missing/ambiguous work context is distinguished from a known relationship;
  questions address material ambiguity rather than demand invented parents.
- The Epic has a meaningful definition and scoped connection to the main spec.
- One real representative Story has understandable flow(s), related Tasks,
  Tests and inspectable actual evidence or explicit evidence limitations.
- From a Task, the human can read the relevant main-spec passage and plan entry
  and understand its relationship to the Story/Scenario without using chat.
- Shared Task relationships preserve one identity/status and are navigable from
  each related context. Missing Story membership remains legal and visible.
- The human can explain what a selected Test does, what behavior it asserts,
  and what its recorded outcome supports; necessary helper/global context is
  understandable. Automated structural checks alone do not prove readability.
- The older harness example is absent from the main pilot presentation, with
  historical records preserved.

These are intended outcomes, not claims about current implementation. The
specification will turn them into observable criteria with concrete examples.

## Non-goals

Modeling every workflow or reconstructing all historical work; mandating an
Agile framework or every possible model concept; mandatory Story membership;
rebuilding historical harness-review; changing completion/evidence authority;
new decision-resolution or inline specification-editing flows; new frontend
framework; unrelated latency benchmarks; automatic test execution/acceptance;
deployment, multi-user infrastructure, merge or push. No product implementation
or planning changes in this session.

## Known assumptions to confirm

1. The phrase `maybe a user story have only single story` is interpreted as:
   a Story may have just one Scenario. Multiple Scenarios represent its
   distinct flows; optional Story membership remains as explicitly selected.
2. Features remain available as related capabilities, without adding a
   mandatory navigation tier or an additional compulsory authoring burden.
3. The specification will propose the exact representative Story, concrete
   flow(s), Tasks and test/evidence examples from this workstream. Existing
   evidence limitations must be recorded; no new execution is implied here.
4. Relevant spec and plan passages are shown in context and linked to their
   source revision; preserve existing snapshot/staleness protections. Avoid
   dumping entire unrelated documents or compressing meaning into identifiers.
5. Existing decision forms remain available with their existing safeguards;
   this correction does not redesign decision resolution.
6. Preserve canonical criterion identities and historical attribution. Newly
   authored Stories and links are identified as current modeling work.
7. Retain local repository use, current UI technology and shared validation
   authority. Exact schema fields and presentation are specification decisions
   constrained by these outcomes, not permission to replace the architecture.
8. Source/content integrity recorded by the skill installer is retained; the
   domain-modeling skill has no manifest version pin, as the human requested.
9. Engineering definitions and their code/test relationships remain in the
   versioned repository. The workbench is their inspection interface, not an
   independent backlog database. A tracker can supply coordination and linked
   work identity; Jira adoption/integration is not part of this session.
10. Workstream execution ownership is distinct from the Stories/Scenarios a
    shared Task supports. Navigation exposes available context without making
    the full Epic-to-result chain compulsory.

## Open questions

No additional product choice is inferred from the letter answers. The complete
intent and every listed assumption await human confirmation. Short research on
established Story/Scenario/Task conventions informs the specification without
turning one tool's hierarchy into a universal software engineering requirement.

## Human decisions

Subsequent discussion identified Story/Task entry and existing tracker/later
item reuse as missed scope cases. The human questioned duplication of Jira
and emphasized retaining documentation and its code relationships in the repo.
They stated Ask should discover these omissions instead of relying on them to
surface them. The proposed repository-first boundary and updated assumptions
remain subject to complete-intent confirmation.

On 2026-10-16 the human selected 1A, 3A, 4B, 5A, 6C, 7C, 8B, 9C, 10B and
identified themself as the user, requiring enough context to remember the work,
including the related main-spec passage and plan task. They explicitly required
visible Tasks, potentially shared across Stories, separate Scenario flows,
minimal useful concepts, and human-readable Tests/evidence with comprehensible
helper/global context. They instructed `stop at defining spec step`.
The complete response is represented by the ten decision entries in
`explore-map.md`; it is not recorded as intent approval.

## E2E

Applicability: `applies` to the proposed behavior; no E2E execution is authorized
by this specification-only session.

Journeys: open Epic and understand purpose -> select Story and concrete Scenario
-> inspect related Task and matching spec/plan passages -> inspect readable Test
and relevant helper/global context -> inspect actual outcome and applicability.
Also navigate a shared Task from multiple Story/Scenario contexts and inspect
legal missing Story membership. Verify historical harness records survive its
removal from the main pilot view. Existing stale/historical guards stay intact.

Observable outcomes: correct contextual passages and relationships, stable
shared Task identity, understandable behavior/assertion/result context, honest
evidence limitations, and preserved historical records. Human inspection is
needed for comprehensibility in addition to automated relationship checks.

Environment/data/reset: disposable local repository/model/spec/plan fixtures,
existing local Streamlit/browser testing setup, and retained evidence snapshots
where available. Future tests own their temporary server/browser processes and
fixture directories and remove them on teardown. Do not mutate committed pilot
or historical evidence as test data. Define exact examples in the proposed spec.
