# Task 4 independent review — round 1

Reviewer: `/root/cont_review`, independent Codex Sol reviewer as assigned.
Runtime: Codex; exact inherited model and parent model identifiers not supplied.
Reviewed candidate: `6179122d671b40b2db650cb6dcee7de925a69f3a` (coordinator replaced initially requested 3b2b058 during review).
Task base: `16b699cbcc253d0873cd58aee6e773ab373a6f28`.
Accepted contract: `02ad31b6e5ef5130986a920f943788cbbe970631`.

## Scope and boundary

Reviewed complete project.py, impact.py and both Task 4 test modules, sealed specification/Task 4 plan, all accepted scenarios 4/1–4/7, current task graph and capture/decision interfaces. Current task 4 is the sole writer. Exact base-to-candidate changes are only `.agents/ask/workflow_refs/{project,impact}.py` and `_ask/tests/test_workflow_refs_{project,impact}.py`, all owned paths. Boundary **ok**. No extras or glob_too_narrow condition.

## Findings

### R1 — Existing-spec behavior defect: inventory is not complete committed dependency discovery

Locations: project.py _inventory/capture_project; impact.py _graph/assess_impact. Criteria SH-18/SH-15; cases 4/1, 4/5 and 4/6.

Capture inventories ref names and work directory names but never loads committed dependency declarations, integrity catalogs, source paths/items, profiles or exact input revisions from any owner. assess_impact accepts a caller-provided graph with no relationship to the captured owner vector; unresolved information defaults to success when node.resolved is absent. Known owners may have no declarations, and branch-only consumers may be omitted, while capture and analysis both claim complete. The project test's shared ref points at an arbitrary commit without a registered shared catalog/declaration and still captures complete.

Required correction: build and validate the graph from exact captured committed owner sources and registered integrity context, or require and verify a complete source-bound graph supplied by the discovery boundary. Missing known owner declarations/objects/profiles must be incomplete. Actual branch-only consumers and qualified paths must be discovered, not merely seeded as dictionary fixtures. Bind source/candidate contexts and recheck applicability before new-context clearance. A standalone validate_capture helper that callers may omit does not bind assess_impact to current applicable scope.

### R2 — Existing-spec behavior defect: ordinary owner catalogs conflict with live/archive ownership

Location: project.py:84–109. Criterion SH-18; case 4/1.

Every refs/ask/references/<owner> is classified as a separate shared owner. Task 2 creates exactly such a ref for ordinary workstream catalogs. Independent probe: adding refs/ask/references/live alongside refs/heads/agent/live makes capture incomplete with identity_conflict, even though these are the same legitimate owner and its catalog. Archived work with a retained catalog suffers the analogous conflict.

Required correction: associate catalog authority with its declared live/archive owner, and distinguish explicitly registered shared owners using their declaration rather than the existence of a catalog ref. Keep true conflicting owner registrations rejected. Add normal live+catalog and archived+catalog fixtures.

### R3 — Existing-spec behavior defect: unlogged inventory ABA still escapes capture

Location: project.py:33–51 and capture_project. Criterion SH-18; case 4/5.

6179122 correctly includes logged movement in the returned generation, fixing logged ABA after capture. However, reflogs are not guaranteed for refs/ask/references; unsupported writers may add then delete a ref without any reflog. Direct fixture probe added and removed refs/ask/references/transient inside during_scan: capture returned complete with retries=1. Thus the required intervening owner addition/removal was not detected.

Use a persistent cooperating publication generation covering inventory changes, and establish supported writer consistency or return incomplete for unsupported/unverifiable movement. Do not infer proof from optional reflogs. Add an unlogged shared-owner add/remove regression; retain logged ABA and post-capture stale checks. This is the planned generation/capture responsibility, not a new requirement.

### R4 — Existing-spec behavior defect: self-attested decisions can clear omitted paths and unrelated authority

Locations: impact.py:62–95 and :126–144. Criteria SH-15/SH-16; cases 4/3 and 4/6.

required_paths is supplied by the same unverified decision as examined_paths and is never checked against graph-derived affected paths. Exact new upstream may be nonexistent/unrelated, reviewer/coordinator may be identical or foreign, capture may be absent, and named downstream retained pins are not present. Boolean outward_equal/satisfies_new_inputs/reuse_allowed plus arbitrary evidence text then stop every outgoing propagation edge.

Independent probe using the existing test graph: decision(required_paths=['plan'], examined_paths={'plan':'resolved'}, reviewer='same', coordinator='same', new_upstream='z/spec/99@99') is retained with propagation_stopped True; assess_impact(... changed=[P], decision[T]) omits X entirely without any capture. The shared-policy input is omitted and the purported new source is not resolved.

Required correction: bind immutable review decisions to exact resolved old/new contexts, every graph-derived affected path, applicable owner-scoped independent reviewer/coordinator evidence and named retained consumer revisions/edges. Reject unavailable or mismatched source targets, incomplete comparison/authority and stale captures. A stop for one named consumer cannot automatically clear other consumers or unresolved inputs. Preserve old pins/runs; actual pin changes must publish a new revision. Cooperative attribution does not require authentication, but the accepted owner/independence and exact-context checks cannot be replaced by nonempty strings. Do not mutate caller decision dictionaries or expose them as mutable historical records.

### R5 — Existing-spec behavior defect: traversal loses converging affected paths

Location: impact.py:122–125, edge-only traversed marker. Criteria SH-16/SH-18; cases 4/2 and 4/6.

For roots A and B, both feeding C, which feeds D, C correctly records paths A→C and B→C. D records only A→C→D because marker (C,D) suppresses traversal of the second path. Independently reproduced with four qualified nodes. This omits an affected input chain needed for complete path review.

Required correction: retain every distinct relevant root/path (or an equivalent complete dependency representation) without unsafe duplicate suppression; the graph is already cycle-checked. Add converging-root and diamond-path assertions proving every relevant path survives and one decision cannot clear another path.

### R6 — Existing-spec behavior defect: deletion/retirement and revise outcomes are not implemented

Locations: impact.py record_decision/assess_impact; tests 4/4 and 4/7. Criteria SH-17 and SH-15/SH-16.

Retain may return retained, but revise and retire both unconditionally collapse to reassess. There is no representation/application of verified deletion, retired versus stale-active state, active shared obligations, reviewed dependency updates, new revised consumer pins or immutable retirement history. Deleted inputs can be marked satisfied by self-attested retain booleans because absence is never resolved against candidate source. The graph never loads source/candidate extraction results. This does not implement the accepted normative decision outcomes.

Required correction: use actual available-absent versus unavailable source results; implement the declared retain/revise/retire lifecycle and dependency consequences. Protect shared active tests until justified reviewed updates, preserve retired historical bindings/evidence and distinguish default active state. Scope retirement to consumers no longer serving active obligations, and propagate actual revisions through real dependencies.

## Required assertion corrections

These are task-local test suggestions accompanying R1–R6, not optional future work:

- 4/1 and 4/5 need committed branch-only dependency/catalog declarations and normal per-owner catalogs, true missing/conflicting declarations, real unlogged movement and source-bound stale clearance, rather than ref roster alone.
- 4/3 needs actual old/new dependent and named consumer pins, valid registered attribution, outward/inherited obligation change and revised-pin effects. Checking a dictionary's boolean stop is insufficient.
- 4/4 currently asserts retire returns reassess, that an untouched graph still contains its original shared edge, and propagation continues. It never deletes a requirement or applies retirement/shared dependency updates.
- 4/6 currently changes one string to unknown and blanks coordinator; it does not exercise independent authority per owner, multiple affected contexts, omitted paths, revisions or forbidden authority transfer.
- 4/7 merely sets node.resolved=False. It creates no Git history, available deletion, shared active test, retired historical binding or unavailable object.

Implement these accepted scenarios through genuine assertion regressions and exact-candidate execution; do not claim the full scenarios from the current minimal tests.

## Execution evidence and limitations

Inspected initial Green a8a4679cdc56494584027a26707594d5 for superseded 3b2b058: all seven mapped cases pass, collection succeeds, both runner exits zero and log digests match. That execution does not bind 6179122. Coordinator stated a new exact-candidate Green is running. No TaskResult 4.json or final 6179122 results were present when this review inspected runtime evidence, so no exact-candidate TDD/integration completion is claimed here.

Direct temporary-fixture probes confirmed normal live/catalog conflict, unlogged transient owner loss, unsafe self-attested stop and converging path loss. No source was modified, committed or independently run as a full test suite. Passing tests cannot clear the documented behavioral gaps.

## Classifications and verdict

R1–R6: existing-spec behavior defects within Task 4 responsibility, requiring Red → Green → Refactor and fresh review. Assertion corrections are task-local structural/test suggestions. No broader horizontal refactor or required spec redesign was identified; no parked handoff draft, withdrawal or unrelated implementation requested.

**REJECTED** for exact candidate `6179122d671b40b2db650cb6dcee7de925a69f3a`.
Boundary **ok**. Core capture/discovery, decision authority/path safety and normative retirement behavior remain incomplete.
