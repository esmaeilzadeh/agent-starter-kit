# Independent plan review

## Attribution and exact target

Reviewer `/root/shorter_hashes_challenge_r6`, Codex independent subagent, saved model `gpt-6.1-sol` at `medium` effort; parent model not exposed. Applied `kit-05-plan` structured-test review and the existing traceability authority/runner contract.

Reviewed commit: `02ad31b6e5ef5130986a920f943788cbbe970631`.

- Sealed revision-7 spec canonical digest: `9bd9107a4d9490528178e2ac204c44926aa9b0e8675fd58f042e2a6fa2a77a3e`.
- Test-plan canonical digest: `40e2258c48f5e9dcfcaa55f0aa09808b8c2d3232b850db4752e852abaca3680b`.
- TaskGraph canonical digest: `e40e35263b303fc5926fa4ac96a29480614febd5b0679f2f88a269088d7f9ccb`.

Exact-byte hashes for the plan, inventory, baseline, tokenizer requirements and spec seal are recorded in `traceability/plan-review.json`. Both records bind this exact committed target; they supply no execution evidence.

## Decision

**APPROVED — zero open planning blockers for the exact committed contract above.**

The earlier CHANGES_REQUIRED assessment is superseded for this corrected source; its original records remain in Git at `850c168`/`8315ae4`. The sealed revision-7 specification is unchanged. This independent approval is an input to coordinator plan registration, not registration itself or permission to implement.

### P1 — producer inventory and publication ownership: closed

The inventory now explicitly classifies `_ask/scripts/record-run.sh` and `_ask/scripts/start-work.sh`, and task 8 owns both along with their affected shell regression expectations. New case 8/4 requires numeric run/revision references, separate full integrity data, preserved metric/notes/exact provenance, readable historical records, and unchanged dirty/missing-or-wrong-SHA/config refusals. The plan declares auxiliary identity grammar and the explicitly registered shared owner `repository-runs`, with its separate `results/references/integrity.json` and coordinator registration ref. Conflicting owner registration refuses rather than merging history.

This closes the counterexample where repeated new eval JSON/report hashes escaped all task ownership while the plan claimed complete coverage. Existing full-ID plumbing and immutable historical bytes retain their justified exceptions; ordinary new report repetition does not acquire an exception.

Case 8/5 additionally makes actual start-work owner creation join the common lock/generation protocol while preserving develop-base, clean-tree and optional Explore behavior. It requires capture serialization/retry/incomplete behavior and refuses successful dangling owner creation. Thus this known cooperating publisher cannot silently create an omitted owner during complete capture.

### P2 — declared test-input/source binding: closed

Every task-9 case now binds the shared `_ask/tests/workflow_refs_fixture.py`. Cases 1/* and 10/1 bind the frozen baseline manifest and tokenizer requirements. Later integration/e2e cases bind the concrete reference runtime and consumer modules already available by that task or prerequisites. Independently checked every declared path: it is committed already or owned by the current/prerequisite task; early cases do not depend on future task files.

This closes the counterexample where changing fixture/config/runtime inputs remained outside the declared per-case binding. Existing candidate SHA, coordinator source-digest and semantic continuity checks remain authoritative. The mapping is a concrete reviewed future contract; implementations discovering another actual input must amend it before claiming complete coverage.

## Assessment of the remaining contract

The ten tasks have concrete outcomes, exact case ownership and a linear dependency order. Shared paths in tasks 1/10 and 8/10 are explicitly serialized; one committing writer and scope-amendment rules preserve ownership. Task 9 is deliberately a tests/fixture deliverable; discovered production defects must amend the responsible task before edits. No behavior is hidden behind an unresolved design choice: numeric grammar, separate trust-anchored catalog, reviewed profiles, coherent capture, immutable decisions and migration/public interfaces are fixed within the sealed spec.

Read the current validators, `adapters.py`, `unittest_runner.py`, `evidence.py`, and the traceability documentation. All 14 declared module selectors use the supported unittest adapter; the named class/method IDs are suitable explicit future cases. Task filtering is supported. A module may contain only its mapped cases when collected for final workstream execution; unsupported subtests/extra unplanned cases cannot supply completion. Future tests still require behavior-assertion Red, not import/setup failure, followed by actual Green and independent continuity review. No planned test currently exists or has run.

The JSON obligations exactly match the specification's required types:

| Criteria | Required evidence types |
| --- | --- |
| SH-01, SH-02, SH-03, SH-06, SH-08, SH-09 | unit, integration |
| SH-04 | integration, e2e |
| SH-05, SH-07, SH-12, SH-13 | integration |
| SH-10, SH-11 | integration, e2e |
| SH-14 | e2e |
| SH-15, SH-16, SH-17, SH-18 | unit, integration, e2e |

All 18 have mapped meaningful positive/negative assertions. In particular, 3/* covers unknown fields, reviewed profiles and externally changed bindings despite equal blobs; 4/* covers direct versus potential impact, old-pin retention versus new revision, multiple inputs, inherited obligations, deletion and coherent capture including ABA/new owner refs; 5/* and 9/1 cover coordinator authority and exact approval/execution binding; 8/* covers explicit migration and interruption; 9/* covers actual CLI/worktree eligibility/completion outcomes. New formats are normalized before existing policy checks. Catalog authority cannot bootstrap accepted-tests authority from candidate data. Required full-value exceptions preserve plumbing, trust registration, exact checks and original historical bytes; they cannot justify ordinary report repetition without classification.

The frozen experiment contains all three questions and 14 real committed files, including historical reports and selected bound log bytes. Independently verified every byte length/hash against baseline source `9a3d25d035baafc23508f242020d46fae7ff5b14`. The tokenizer is pinned to `tiktoken==0.12.0`, `cl100k_base`, `encode_ordinary`; provisioning/version checking precedes measurement. No tokenizer execution or savings is claimed here. Question equivalence, complete needed lookups, unique generated JSON outputs, catalog/profile/index/decision overhead and retained original archives are counted. Strict aggregate token and JSON-byte reductions and disclosed per-journey regressions preserve SH-12. A failed benchmark cannot be accepted by changing thresholds.

Recovery and discovery are concrete obligations, not vague aspirations: common-directory persistent lock, generation/CAS and recoverable journal must preserve complete old/new observations, immutable targets and crash retries. Inventory capture covers local live/archive/shared owners; additions/removals/ABA and new-context freshness are explicitly tested. An unsupported external writer cannot silently produce complete clearance.

## Checks and boundaries

Loaded the exact committed spec/test-plan/graph through the existing `contracts_at` validator successfully. Independently checked 10 tasks, 39 cases, 14 runners, and exactly one responsible task per case. Independently checked task-time source-path availability and verified all 14 frozen corpus files. These are planning checks, not behavior executions. The coordinator's reported graph/path validation remains separate from this semantic assessment.

P1/P2 are closed; no further correction is required for plan sealing at these exact bindings. The coordinator must register this independent decision through the existing accepted-plan authority and retain the seal against all bound artifacts. This review grants no complete-intent approval, task-loop initialization, implementation authorization, execution review, final completion or acceptance. The authorized endpoint remains the sealed plan; implementation stops at its existing gates.
