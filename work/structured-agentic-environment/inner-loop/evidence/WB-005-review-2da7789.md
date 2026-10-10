# Independent WB-005 review — 2da7789

- **Decision:** REJECTED
- **Boundary:** ok (writer source; coordinator metadata attribution below)
- **Reviewer:** /root/review_wb001
- **Model/runtime:** gpt-6-astra / codex
- **Parent model:** gpt-6-luna
- **Candidate:** `2da7789398ecaee48eae260b2e7203cea5e4c13a`
- **Task and accepted-contract base:** `dcae11d61c2b73745ba9f5b2187065792d84ac46`
- **Spec digest:** `f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb`
- **Plan digest:** `4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8`
- **Graph digest:** `ad8e3e6a647d83b6b699fbe5c15e13a2ae8c0bc880be686e1cc9e5cc91a8664d`
- **TaskResult:** `work/structured-agentic-environment/inner-loop/results/WB-005.json`
- **TaskResult SHA-256:** `bd54dd33edd276aec4cdd87fdef89c77f47ae19f5949bcf522e56c403f0d6828`

## Findings

### R1 — high — `_ask/ui/workbench_overview.py:179`

Filtered record buttons pass collection/filter kinds (blocked, tasks, scenarios, decisions) to a route matcher that requires singular canonical kinds (task, scenario, decision). All such Open record buttons silently return without navigation. Normalize filter kind to canonical record kind or carry an explicit resolved route with the stable ID.

**Reproduction:** Open the assigned fixture; click overview:summary:blocked, then overview:filter:open:blocked:build. The filter state correctly names build, but route remains purpose and detail remains Purpose. streamlit_app.py:64 finds no outline entry of kind blocked. The same mismatch applies to decisions/scenarios/tasks.

### R2 — high — `_ask/ui/streamlit_app.py:63`

Related navigation chooses the first alias for a canonical ID and uses route_to, losing the current parent context and clearing Back history. Prefer the route alias under the current ancestry and navigate while preserving history/filter context.

**Reproduction:** Use an admitted story with two scenarios and one task owned by both; open scenario-2 then scenario:scenario-2:task:build. The app selects build under scenario (the first scenario), not build@scenario-2. Breadcrumbs show Canonical behavior instead of Second behavior, route history is [], and Back is disabled.

### R3 — medium — `_ask/ui/workbench_overview.py:68`

The overview exposes unassigned scenarios only when there are no stories at all. With mixed recorded membership it renders only story-linked scenarios and omits remaining scenarios from the overview delivery summary. Render an explicit unassigned group for scenarios outside the union of recorded story memberships, while retaining the existing model relationships.

**Reproduction:** Create an admitted model with story→scenario and a second canonical scenario directly under the epic. Projection stories contains only scenario, while projection scenarios contains scenario and scenario-2. Overview has only overview:scenario:scenario, with no overview:scenario:scenario-2. The left outline still contains route:scenario-2 and its grouping; the omission is specifically in the epic delivery summary.

## Verified implementation and assertion limits

The actual `streamlit_app.py` dispatches epic, story and scenario routes to the owned overview/story/scenario renderers, satisfying the amended ownership/wiring boundary. The no-story pilot exposes its real canonical scenarios without inventing a story. Purpose, separate task graph/runner status, declared lifecycle, dependency readiness, attention and unloaded results are visible. Scenario details consume captured canonical G/W/T and recorded mappings.

The exact candidate's two assigned tests pass in a disposable checkout of candidate blobs: **2 tests, 3.677s**. Independently reproduced failures above use the same candidate source bytes; the checkout HEAD differed only by the subsequent TaskResult recording commit. The mixed-story fixture is admitted: its recorded story contains scenario, while scenario-2 is directly under the epic. The outline still exposes scenario-2 and its gap grouping; the missing summary row is specifically the overview detail omission, not disappearance from the entire navigator.

The lazy-evidence test raises if the projection inspector is called. An additional independent probe guarded both `Path.read_text` and `Path.read_bytes` for test_fixture.py while opening overview and scenario: **zero source reads, no evidence inspection**. This structural requirement passes. No execution evidence is invented from task/status counts, and unknown results remain Not loaded.

The current tests check filtered state and the existence of relationship controls but do not follow filtered Open record or scenario→shared-task links. They also lack a recorded story/mixed membership fixture, a known failed-result set and shared-test counter assertions. Those missing adversarial journeys explain why genuine green execution coexists with the reproduced failures.

## Scope and boundary attribution

Task base remains the explicitly recorded amended contract `dcae11d61c2b73745ba9f5b2187065792d84ac46`; this reviewer changed no base or coordinator state. The raw diff includes five owned implementation/test files plus coordinator registration metadata and runtime state. Commit `d334bb2` registered `traceability-accepted.json` and the amendment review Markdown before WB-005 test/implementation commits; `ef2da73` started the writer. Those preimplementation coordinator files are not writer source edits. All writer implementation/test changes are within WB-005's amended owned paths. The companion JSON enumerates the raw diff and attribution explicitly. Boundary is **ok** for the writer source.

## Genuine red/green evidence

- **red:** `1be0d48ad30d4af29abc47ec84e7886a` at `54aa9b32dcc3595a0fd066377fa823fafeced0cf`; canonical report digest `853d247ba96f83d40b06a0acf857742a241281eb8246964125528b3a81353e72`; report-file SHA-256 `7351045fcb70b960f7d9c7dd01be57351ccaad5802ee4843fa904718d430b45a`; log `work/structured-agentic-environment/traceability/runs/1be0d48ad30d4af29abc47ec84e7886a/75c33e9abe45464895d530fa2c14d49e.log`, SHA-256 `fedf5b31c36f07bc84db3a31bf04d0788a09abede4be40622f1698b033a19859`.
- **green:** `9bc371ff4aff4536941825ff64a90911` at `2da7789398ecaee48eae260b2e7203cea5e4c13a`; canonical report digest `084f127d1e55f5d6083abe146008748df9c05f1fd79932f385f403733d453b65`; report-file SHA-256 `bf45662d434e9d94489dbdd4286c360bca4f648b1e078cfe3b056f11fc0b89e0`; log `work/structured-agentic-environment/traceability/runs/9bc371ff4aff4536941825ff64a90911/a564b6216d024a60a6eb5a67fa5ddb89.log`, SHA-256 `e3dc8442df5fffb6b1a8a36e4cfa60266aeec63d8ff48a212b8c5eb7854d6d0f`.

Both task cases collected successfully and failed by behavior assertion in the accepted red (missing purpose and summary navigation controls). Both pass in the exact-candidate green; retained final-green duration is 3.582s. Ledger canonical report digests, accepted contracts, task/scope, exact case IDs, source-blob digests and log bytes were verified.

The red→green test diff adds import plumbing, metric inspection, dependency-readiness and relationship-control assertions, and work identity in expected filters. It preserves the original failing purpose/summary checks. No TDD exemption is used. Genuine continuity does not cover the omitted counterexamples in this review.

## Semantic decisions

- **EM-008 / integration:** REJECTED for lost many-to-many/Back context and mixed-membership summary omissions.
- **EM-010 / integration:** REJECTED for inert filtered record navigation.
- **EM-012 / integration, this task's lazy-loading slice:** APPROVED; no eager evidence/source work was observed.
- **WB-overview:** REJECTED for missing adversarial story/relationship journeys.
- **WB-summary-links:** REJECTED because filter state checks stop before opening the intended records.

## Exact owned-source digests

- `_ask/tests/test_engineering_workbench_overview.py`: `0023706e2ada4e2c830b76746196c8199814f2c941c28c6a105d5b36817dd064`
- `_ask/ui/streamlit_app.py`: `3240da9d8c488041a171db95a32627991348592ce16aa974ac5739ebe46530b7`
- `_ask/ui/workbench_overview.py`: `95eeb6f60a18e12d6928288ac032dcb979f5d91386152bc98d707fa8258a7358`
- `_ask/ui/workbench_scenarios.py`: `511630ba7bc02d9893643f0fcb5c937f8cfe3d670589f8821f7f24f8e852c694`
- `_ask/ui/workbench_stories.py`: `a369e10e0c0dfc930f9e14c1046efd31f8752a823c248aac55b581eb9ed9e40a`

Companion semantic artifact: `work/structured-agentic-environment/traceability/review-input-WB-005-2da7789.json`. Read-only semantic validation reports the expected rejected criteria/tests and no candidate/source/inventory binding errors. The post-integration UI checkpoint is not claimed or used as a rejection reason.

No source edits, coordinator decisions/state changes, recording, acceptance, integration or commits were performed.
