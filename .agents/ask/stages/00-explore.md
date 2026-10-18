# Kit Protocol: 00 Explore

Source contract extracted from the Build Spec agent-contracts section. Portable SoT for this stage.

Canonical artifact: `work/<work-id>/explore-map.md` (from `_ask/templates/explore-map.md`). Prepare Explore skills via `./ask prepare`.

## 15.0 00 Explore Agent

Purpose:

```text
When the destination is foggy, chart decisions (and run research/prototypes)
until What/Why can be owned — then hand off into Intent / 01 Grill.
```

## Continuation recovery (before new-task intake)

When the human says “continue,” “resume,” or equivalent, first inspect the
current branch, workstream artifacts, inner-loop state, and recent commits. If
those sources identify one active authorized workstream, resume its exact stage
and task; retain prior approvals and do not restart new-task intake. If multiple
active workstreams remain plausible, ask only which one to resume after checking
the available evidence. Apply the Explore/Grill entry gate only after establishing
that the request starts a genuinely new task.

## Adopted subject intake

Before choosing or creating execution work, recording intent, or admitting a
delivery, resolve the request through the shared read-only subject context:

```sh
./ask stage-intake --stage 00-explore --work-id <work-id> --request <request.json>
```

The JSON request may contain explicit qualified `explicit_subjects`, a
`tracker_context` reference, or parked `later_cards`. Treat `resolved`,
`needs_clarification`, `chooser`, and `unavailable` as distinct outcomes. An
explicit subject takes precedence over a recorded association; conflicting
qualified owners require human clarification. A branch is only an execution
locator. This command inspects context and does not create branches, nodes,
intent, assignments, or delivery state.

Must:

```text
treat Explore as decision work, not implementation
keep a durable map (explore-map artifact and/or tracker map)
separate human decisions from research facts
prepare Community Skills declared for Explore via Skill Preparation
before Explore decision grilling: propose extra related skills that would change What/Why; ask before prepare; pin accepted skills in the repo manifest
expand only load-bearing Explore decisions (Grilling Expansion: two-block + assume-list)
stop and hand off when the destination is clear
```

Must not:

```text
silently start Implement to "figure it out"
vendor skill bodies instead of pinned prepare
pretend fog is cleared while material decisions remain open
reimplement a full community wayfinder stack when a pinned skill suffices
```

Bind (via Skill Manifest), do not copy by default:

```text
wayfinder / research / prototype / grilling (and related)
discovery: skills.sh as a starting index
```

Output:

```text
work/<work-id>/explore-map.md (and/or tracker map pointer)
handoff notes sufficient for 01 Grill
```

Gate:

```text
DESTINATION_CLEAR → eligible for Intent / 01 Grill
STILL_FOGGY → continue Explore (or escalate to human)
```

---

## Kit emphasis

- Do **not** stuff R&D / destination discovery into `06 Implement`.
- Non-empty `## Handoff to Intent` on the explore-map is required before `01 Grill`.
- Run Skill Preparation for Explore-bound Community Skills before labor. Extra related skills: ask first, then pin in `_ask/skills/manifest.yaml` (never `latest`).
- Explore decision grilling uses the same filter as `01 Grill` (load-bearing numbered Qs + “I’ll assume…”). See `_ask/docs/adr/0016-grilling-load-bearing-and-skill-before.md`.
- Never start Explore on a dirty worktree; if dirty, grill the human per `_ask/policies/worktree.md`.
- Kit path: `_ask/policies/workflow.md`. **If 00 runs**, create `work/<work-id>/explore-map.md` from `_ask/templates/explore-map.md` when missing, and do not skip that artifact. **If 00 is a real skip** (dest already ownable, and the human did not invoke `/00-explore`), do not create the map; record the skip in `intent.md` and go to 01 after confirm. `/00-explore` always runs this stage — do not ask whether Explore is needed. Off-path only if the human explicitly leaves the kit.
