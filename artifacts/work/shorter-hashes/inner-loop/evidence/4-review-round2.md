# Task 4 independent review — round 2

Reviewer: `/root/cont_review`, independent Codex Sol reviewer as assigned.
Runtime: Codex; exact inherited model and parent identifiers not supplied.
Candidate: `edec2b468f2bda4e7cadbab9e6dcb9732534d6a2`.
Task base: `16b699cbcc253d0873cd58aee6e773ab373a6f28`.
Accepted contract: `02ad31b6e5ef5130986a920f943788cbbe970631`.

## Scope and boundary

Fresh review inspected the full updated project/impact implementation and Task 4 tests against accepted cases 4/1–4/7 and prior R1–R6. Exact base-to-candidate paths remain only project.py, impact.py and their two declared test modules. Boundary **ok**; no extras or glob_too_narrow condition. Temporary Git fixtures were used for independent behavioral probes; no source edits or commits were made.

## R1 — Partly fixed; candidate dependencies and missing-source failure remain

Fixed: load_project_graph now reads authority-registered committed catalogs, verifies source digest/profile/item extraction, requires input declarations, discovers cross-owner catalog nodes and binds assess_impact to a repository-validated capture. Caller-supplied graphs cannot silently replace captured declarations.

Remaining R1a (SH-15/SH-18, cases 4/2, 4/5, 4/6): candidate binding changes are recorded in graph.changes, but graph.nodes and reverse traversal retain only old catalog payload.inputs. A new actual candidate dependency is missing from impact even while graph/analysis claim complete.

Exact fixture repro: instantiate the current test_workflow_refs_impact.ReferenceTests fixture. Use commit_owner_candidate('a', update) to change item p.inputs in work/a/items.json from S to `[{"reference":Q,"role":"shared-policy"}]`. load_project_graph returns complete and graph.changes includes P2. assess_impact(graph, [Q], capture=capture, repository_root=root) omits P2 from affected items.

Required correction/test: represent source and candidate dependency contexts separately. Candidate Q→P must produce direct reassessment and potential descendant impact. Preserve P2's old immutable inputs; do not silently rebind them. If the changed binding needs an unpublished revision, expose that unresolved candidate/revision state and refuse complete clearance. Add a new candidate input and eventual registered-revision test; checking graph.changes alone does not ensure impact traverses actual candidate paths.

Remaining R1b (SH-18, cases 4/1 and 4/7): _regular_file_at invokes git ls-tree outside its error translation. A missing pinned source object raises CalledProcessError rather than returning incomplete.

Exact fixture repro: create a parentless external commit with `git commit-tree HEAD^{tree} -m ...`, register U@2 against its work/c/items.json through register_revision, expire reflogs and run `git gc --prune=now`. Catalog authority remains reachable; the source commit does not. load_project_graph raises CalledProcessError. Wrap both metadata/read Git operations in the ProjectError boundary, and test actual pinned-object loss independently of a missing candidate file.

## R2 — Fixed

Ordinary live/archive owner catalogs are associated with their existing owner rather than misclassified as shared owners. Explicit shared owner registration remains separate; tests cover legitimate live+catalog and archive+catalog sources and a real shared constraint. No remaining R2 defect found.

## R3 — Partly fixed; selected integration/archive unlogged movement remains

Fixed: shared-owner loose-ref storage changes now detect the earlier unlogged transient add/delete probe, and logged movement participates in returned generation and validation.

Remaining R3 (SH-18, case 4/5): _ref_storage_generation fingerprints agent/catalog roots and packed-refs but omits selected integration/archive loose ref paths. Their ABA movement is invisible when reflogs are disabled.

Exact project fixture repro: set core.logAllRefUpdates=false and remove the existing .git/logs/refs/heads/develop before capture. In during_scan update refs/heads/develop to fixture.other and then back to fixture.sha. capture_project(retries=1, shared_owners={'shared'}) returns complete and no develop reflog exists. Include selected integration/archive ref storage and relevant parent storage metadata in movement checks, or return incomplete when movement cannot be established. Add this unlogged selected-ref regression alongside existing shared-ref/logged ABA tests.

## R4 — Partly fixed; stop still clears unnamed downstream consumers

Fixed: captured source graph/context are required, required input paths are graph-derived, reviewer/coordinator must differ, unsupported/mismatched targets/profiles refuse, registered new dependent revisions are checked and an authority_check seam defaults to no authorization. Input decisions are copied before validation. These are meaningful safety corrections.

Remaining R4 (SH-16, cases 4/3 and 4/6): eligible_consumers is checked for valid neighbors but never used to scope propagation. A retained decision still sets one stopped flag and prevents all outgoing traversal from the dependent.

Exact fixture repro: add and register `Y='b/spec/1/plan/1/task/3/test/1@1'` with inputs `[{'reference':T,'role':'task'}]` in owner b's committed source/catalog. Update agent/b, capture and load. Existing retain decision for T names only eligible_consumers=[X]. assess_impact(... changed=[P], decisions={T:decision}, authority_check=lambda ...:True) omits both X and Y. Y is registered/active but has no reviewed retained-edge eligibility.

Required correction/test: stop only the explicitly named consumer edge/pin; preserve reassessment and paths for Y and its descendants. Add at least two T consumers and a converging-path case so a valid stop cannot clear unrelated edges or inputs.

## R5 — Fixed

Traversal keys now include the full prior path rather than only an upstream/consumer pair. Current converging-root tests verify both input paths reach T and X. No remaining path-loss reproduction found in this correction.

## R6 — Partly fixed; explicit inactive state is overwritten

Fixed: decisions distinguish retained/revised/retired outcomes, revised versions must be registered, active downstream consumers block retirement, deleted versus unavailable source has distinct representations, and history stays in catalog nodes. Tests now exercise actual available-source deletion and missing candidate source.

Remaining R6 (SH-17, case 4/4): load_project_graph uses False both for a missing active declaration and explicit active:false, then sets every false latest entry active. Dependency closure can also reactivate explicit inactive targets. Retired/inactive historical state cannot reliably stay out of default active workflow.

Exact fixture repro: publish U@2 with the complete existing item u plus `active:false` through register_revision; update agent/c to that committed source, recapture and load. The node payload retains active:false, but node.active is True. assess_impact([Q]) includes U@2 in default active impact. This was independently executed.

Required correction/test: distinguish absent lifecycle state/default selection from explicit inactive/retired state. Historical reachability is not permission to reactivate retired items. Add inactive-latest and active-consumer-pins-retired-target regressions, preserving historical retrieval and explicit reassessment without silent reactivation.

## Test and execution evidence

Exact Green run `4afd1a9b1c4f44f1833c4c8f38c5d8a4` binds to edec2b4; all seven mapped cases pass, both runners collect successfully and exit zero, and both log digests match bytes. Tests are substantially stronger than round 1, but do not cover the exact remaining repros above. At review time TaskResult 4.json was still absent, so no complete TaskResult/TDD attestation is inferred. Coordinator must retain actual behavioral Red evidence for each correction and exact-candidate final Green after new changes.

## Classification and verdict

Remaining R1/R3/R4/R6 are existing-spec behavior defects within Task 4 ownership. Add genuine regression Red → Green → Refactor and obtain fresh exact-candidate review. R2/R5 are corrected, not withdrawn. No broader horizontal refactor, required Spec Change or parked handoff identified.

**REJECTED** for exact candidate `edec2b468f2bda4e7cadbab9e6dcb9732534d6a2`.
Boundary **ok**. Remaining fixes: candidate-context impact and missing-object refusal (R1), unlogged selected-ref ABA (R3), named-edge retain scope (R4), explicit inactive lifecycle (R6).
