# Create fresh work from confirmed intent changes through an Ask command

- **Status:** parked (not live; no new workstream started)
- **Found during:** `revising-workbench`, 2026-10-16
- **Tracker:** https://github.com/esmaeilzadeh/agent-starter-kit/issues/50
- **Start later:** new session, `./ask start-work fresh-work-on-intent-change`
- **First stage:** 01 Grill; the outcome is clear, command interface and transition semantics need specification

## Why

When intent evolves, repeatedly amending one work directory accumulates obsolete
specifications, planning decisions, reviews and execution state. Creating another
directory by copying those artifacts carries the same confusion forward. The
developer needs a fresh, coherent statement of the current product intent and
specification, with challenge corrections incorporated into the requirements.

The successful outcome in `work/revising-workbench/` required both a new execution
boundary and an editorial rewrite. Its intent describes user needs, outcomes,
scope and assumptions. Its `spec.md` and `spec.json` contain the actual revised
requirements. Historical reports and a correction appendix are not copied into
the new directory. Make this complete process a reusable Ask operation rather
than relying on the agent to reconstruct it from chat.

## Proposed What (unapproved)

Add an Ask command, provisionally `./ask revise-work <new-work-id>`, that owns the
full transition to fresh work. Final naming and arguments belong to its Spec.
The agent workflow must invoke it whenever the user's intent changes, after
asking the user and receiving explicit confirmation for that transition. This
card requests future implementation; it does not enable automatic transitions now.

The process must cover:

1. Identify the actual change in What, Why, scope, assumptions or acceptance
   outcomes. Show the previous and proposed intent in useful product terms and
   ask whether to create fresh work. Do not create directories, branches or move
   artifacts on a preselected answer, silence or an unconfirmed inference. If
   the user declines, retain the existing work and resolve the change explicitly.
   Editorial rewording with unchanged meaning is not a new user intent.
2. Capture the confirmed source work, exact base commit, destination work ID,
   branch and requested stopping stage. Support the demonstrated case of starting
   from the current branch when confirmed, while making the relationship to the
   kit's normal develop/agent branch policy explicit. Check cleanliness, refuse
   conflicting destinations and preserve the active work without silent stash/reset.
3. Prepare required skills/bindings and decide clear versus foggy. A clear
   destination skips Explore without producing an empty map; a foggy destination
   gets an actual Explore handoff before Grill.
4. Write a fresh product intent describing user, purpose, behavior, outcomes,
   boundaries and assumptions. Keep file relocation, branch ancestry and old
   workstream administration out of What/Why. Present the complete intent and
   assumptions and record the user's real confirmation against its exact digest.
   Distinguish transition confirmation from complete-intent confirmation; existing
   approvals must not be transferred or invented.
5. Author `work/<new-work-id>/spec.md` and its criterion contract from the current
   intent. Apply available independent challenge findings inside the relevant
   behavior, interfaces, invariants, failures and observable criteria. Resolve
   contradictions in prose and JSON together. Do not copy the old specification
   and append a corrections section, or merely relocate unchanged artifacts.
6. Run the independent Spec Challenge process with its required model choice and
   confirmations. Apply resulting corrections to the spec, escalating material
   unresolved decisions. Bind any fresh verdict to the exact revised contract
   digests; do not relabel an old challenge as approval of new bytes.
7. Keep the new directory focused on its current intent/spec and genuinely needed
   artifacts. Preserve old plans, models, pins, reviews and runtime evidence at
   their original identities. Link precise historical sources only where necessary
   for a real example, inherited authority or evidence; never import obsolete scope,
   old approvals/completion state, copied reports or empty later-stage templates.
8. Set the source work aside with a small handoff, make the destination the active
   work and serialize overlapping implementation. Commit meaningful steps, verify
   the produced artifacts and record their actual result/commit. Respect the user's
   requested stopping stage; creating fresh specs does not authorize implementation.

## Acceptance direction

- A changed-intent interaction prompts for fresh-work confirmation; decline or
  absence of confirmation produces no transition writes. Unchanged-intent edits
  do not repeatedly create workstreams.
- A confirmed current-branch transition produces the requested branch at the
  captured base and a focused new directory, preserving unrelated files/history.
- The new intent stands on its own as a product statement. Spec corrections are
  integrated into the requirements and consistent JSON, with usable concrete
  examples and observable criteria, rather than deferred to an appendix or Plan.
- New intent approval and independent challenge authority bind the actual new
  bytes. Old runtime state, pins and verdicts cannot establish new completion.
- The command and agent entry instructions implement the same process; the agent
  uses the command on every actual intent change instead of hand-assembling it.
- Repeated invocation, existing destination, dirty-tree, interrupted transition,
  unresolved challenge and confirmation failures leave an explicit recoverable
  state without silently advancing stages or creating duplicate work.
- Record a representative end-to-end transition and an artifact-quality review
  that checks the meaning of the fresh intent/spec, alongside structural tests.

## Note

Use the final `revising-workbench` artifact shape as an example of the outcome,
not the initial copying/appendix attempts or temporary clone/import workaround.
Keep command mechanics and agent-authored semantic rewriting responsibilities
explicit: a filesystem scaffold alone does not fulfill the request.

Related parked work: `later-inbox-develop-routing` concerns inbox publication;
`later-inbox-script` concerns card creation. This item concerns fresh work after
confirmed intent changes and does not merge those jobs into its scope.
