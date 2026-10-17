# Specification gaps: entry scope, context and authority

Status: drafting findings, 2026-10-16. These findings inform a proposed amendment;
they are not formal 03 Spec Challenge, accepted criteria or implementation proof.
Stop remains 02 Spec. Current accepted specification is unchanged.

## Root mistake

The agent treated Epic-first entry as a settled product premise and asked the
human to refine the hierarchy inside it. The human supplied the missing
counterexample: a session may continue an existing Story or Task, including one
already recorded in a tracker or later inbox. Ask should have raised that case
while clarifying scope, without relying on the human to discover it.

## Observed omissions and drafting obligations

| Gap | Current source | Counterexample and proposed obligation |
| --- | --- | --- |
| Entry level assumed from workstream | Current spec, Interactive UI and EM-009, opens branch work; design, One hierarchy, describes the Epic root as overview | A referenced existing Task begins the session. Distinguish execution workstream from product scope; reuse the existing item, recover its context and open its detail without manufacturing an Epic. |
| Intake relationship unresolved | Current spec defines navigation/validation but no mapping from a new request to existing work | A later card or tracker item already identifies the work. Resolve available identity and relationships from the prompt and records; explain interpretation; ask only when ambiguity changes scope or ownership. |
| Optional relationships versus fixed path | EM-008 permits missing Stories; design requires Epic/story ancestor context | A standalone Task or Scenario has no recorded parent. Render known relationships and honest absence; do not require a complete chain or fabricate ancestors. |
| Support versus execution ownership | Design distinguishes task-owned tests, but intake scope is absent | One Task benefits two Stories. Keep one Task and distinguish supported behavior from accountable execution; no duplication or false proof for both Stories. |
| Documentation authority at product boundary | Spec assumes revisioned definitions; no Jira adoption boundary is defined | Code and documents differ across branches. Keep engineering definitions/relationships repository-owned and inspect a coherent revision. Tracker use is coordination/references; migration or integration is not authorized here. |
| Presence versus comprehension | EM-010/011 require task/test details and source, but not recovery of necessary helper/spec/plan context | A test calls an unexplained helper with opaque global fixture values. Showing source and a pass is insufficient: contextual definitions/comments must explain setup/action/assertion and result applicability. |
| Demonstration versus general behavior | Pilot data has one intent root and sparse Stories | One complete Story proves the example only. Specify Task- and Story-entry cases, shared Tasks and missing parents without modeling the entire backlog. |

## Drafting method

For each proposed requirement identify its assumptions, exercise a concrete
counterexample, and distinguish repository facts from product choices. Check
entry, missing/ambiguous context, shared relationships and source revision.
Present remaining human choices with enough explanation to decide; do not ask
the human to invent routine edge cases or approve architecture merely because
existing code implements it.

## Authority and limits

The human challenged workbench/Jira overlap and emphasized the cost of moving
documentation and code relationships into third-party software. Repository-first
inspection with optional tracker coordination is the proposed boundary, not a
decision to deploy Jira or remove the workbench. Intent approval remains pending.
No code, schema, runtime state or accepted specification was changed.
