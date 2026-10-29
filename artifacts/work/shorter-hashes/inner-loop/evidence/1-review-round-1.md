# Task 1 independent review

## Attribution and scope

Reviewer: `/root/cont_review`, independent Codex agent.
Runtime: Codex. Exact inherited model identifier and parent model were not supplied to reviewer.
Base: `813b971e387547248037ee972bbafd26e2110188`.
Candidate: `c5111d2c55d9cfddccf40f342d8ed1965e1ec75c`.

Reviewed canonical 07-review instructions, accepted plan, TaskResult, task graph, frozen manifest, complete implementation/test diff, cases 1/1 and 1/2 and their SH-11/SH-12 obligations, and recorded Red/Green evidence. Inner-loop status confirms task 1 as current writer.

## Boundary

`git diff --name-only` between the supplied revisions lists only `.agents/ask/workflow_refs/benchmark.py` and `_ask/tests/test_workflow_refs_baseline.py`. Both match task 1 owned_paths. Boundary: **ok**. No extras or required paths outside ownership.

## Finding R1: existing-spec behavior defect

Location: `.agents/ask/workflow_refs/benchmark.py:178`–`184`, and test assertions requiring each complete file text in transcripts.

The accepted frozen measurement contract (plan.md:139–141) requires baseline projections selecting every mapped case/obligation/runner needed for the frozen question, excluding arbitrary unrelated tasks. Necessary verification may be performed by tools without adding unrelated file text to agent inputs. Frozen resume/review questions target the first task scope; the manifest declares selective baseline projections and JSON serialization.

Instead, capture_baseline appends every complete corpus file to agent transcripts and tokenizes those whole files. The baseline_projection/projection_serialization descriptions are merely copied into the report. Including unnecessary unrelated tasks inflates baseline input tokens and can later produce misleading savings.

Counterexample: the review question targets WB-001 from the frozen structured-agentic-environment test plan. That file also contains WB-002's WB-inventory, WB-snapshot and WB-source-errors, plus unrelated WB-003 through WB-009 definitions. Current transcripts include all those definitions by appending the complete test-plan.json, contrary to the first-task projection contract.

Required fix: implement deterministic legacy projections and labeled lookup/context transcripts for the sealed questions. Keep full corpus bytes for integrity verification while selecting agent-visible context. Preserve the selected task's complete tests/obligations/assertions/runners, required authority/constraints, actual historical results and selected log bytes. Keep unique JSON metadata accounting distinct from transcript selection. Add a failing regression demonstrating unrelated definitions are excluded while complete required evidence remains; execute another Red → Green → Refactor and obtain fresh exact-candidate review.

## Assertion quality

Tests independently compare Git source bytes/hashes, frozen questions, selected log content and per-transcript tokenizer counts. However, full-file inclusion assertions encode R1 rather than proving selective question equivalence. Replace them with the required selective-projection assertions and independently assert total_input_tokens equals the sum of all journey counts. Mutated-manifest tests exercise the sealed manifest hash guard, not corrupted source reads; preserve the original manifest and substitute corrupt/missing blob data in focused regressions to exercise integrity refusal directly.

## Implementation inspection

Manifest/requirements full SHA-256 pins, frozen Git revision reads, file byte/hash checks, UTF-8 checks and path validation are sound on inspection. There is no checkout fallback. Tokenizer package version, encoding and encode_ordinary operation are checked. Per-journey counts use the pinned tokenizer. Metadata byte totals deduplicate JSON metadata paths and exclude YAML/prose/log bytes. These mechanics do not repair wrong transcript selection. Strict aggregate candidate savings remains task 10's obligation.

## Red/Green continuity

Red revision `e72f158586917d53d3dd7ec5c4ce500983e86ec0`, run `b215a8f5f8d04b71a09b9a4050b5defe`: both mapped cases collected and failed as behavior_assertion (0 versus 3 journeys; missing versus frozen baseline source). These are actual behavior failures, not import/setup errors.

Final Green revision is the reviewed candidate, run `a88644f03a194bf0a91eb2cd8710679f`: both cases passed with candidate/source identity and digest evidence. TaskResult accurately reports those outputs.

Between Red and Green, test changes correct PLAN_REVIEW_PATH from the current workstream to the actual frozen structured-agentic-environment decision and add a diagnostic assertion message. This aligns the fixture with frozen data without weakening the two Red behavior assertions. The unused PLAN_REVIEW_SOURCE constant supplies no provenance assertion.

No tests were independently run by this reviewer. Recorded case reports/logs were inspected. Passing tests do not resolve R1 because they require the incorrect whole-file inclusion.

## Other classifications

No broader horizontal refactor, required redesign or withdrawn finding. No parked handoffs. The reported no-applicable-cleanup refactor outcome is reasonable structurally but cannot clear the behavior defect. Correction stays within accepted behavior and owned paths.

## Verdict

**REJECTED** for candidate `c5111d2c55d9cfddccf40f342d8ed1965e1ec75c`.
Boundary: **ok**. Blocking finding: **R1**, existing-spec behavior defect.
