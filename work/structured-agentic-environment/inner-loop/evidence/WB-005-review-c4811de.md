# WB-005 independent review — merged candidate

**Verdict: APPROVED. Boundary: ok. No blocking findings.**

- Candidate: `c4811dee08c4abe35028e570c04bdd49bb10ef4b`
- Task base / accepted-pin anchor: `ef2da7386e610cf07e01d09ecfba59625f49668d`
- Accepted contract / semantic inventory base: `dcae11d61c2b73745ba9f5b2187065792d84ac46`
- Complete Git tree: `b49608e729b28fa564df5a46364f64290e40e269`
- TaskResult: `wb005/submission-final-merge:work/structured-agentic-environment/inner-loop/results/WB-005.json`
- TaskResult revision: `beeb00e607d4055f05e094cd5029caf813fcdf18`
- TaskResult SHA-256: `f43b1782d33f85d133c98ada7f8f12c26a4fbd6ba04530f9574b3469731e90e4`
- Reviewer: `/root/review_wb001`; model `gpt-6-astra`; runtime `codex`; parent model `gpt-6-luna`.
- Intended recorded_by: `codex-coordinator`; no recording performed.

## Merge, authority and boundary

The merge parents are `06f2da8f3831b4926a0ec43f1a83645b23fcd207`, `2da7789398ecaee48eae260b2e7203cea5e4c13a`. Both complete tree IDs are identical for approved `06f2da8f3831b4926a0ec43f1a83645b23fcd207` and this merged candidate. No source, dependency, policy, contract, test or application-runtime drift is present. The genuine filter-red source `2c9d0587b51875e6c765530c897dca9e77ccd27c` and registered task base are ancestors. Accepted coordinator authority, exact candidate contracts, source inventory and all five implementation/test SHA-256 values were revalidated.

The task-base diff includes exactly five accepted owned source paths plus preserved reviewer/inner-loop runtime evidence. Boundary is ok. The semantic schema base remains the accepted contract revision; the registered task base is recorded separately.

## Prior findings and independent behavioral checks

- **R1 resolved:** Filter collection kinds now normalize to canonical route kinds. Assigned regression clicks blocked→build and independent checks also open decision and scenario filtered records successfully.
- **R2 resolved:** Related navigation prefers the alias under the active scenario and navigate pushes the prior route. Shared task from scenario-2 opens build@scenario-2; Back restores scenario-2. Overview filter context is also retained after the R4 fix.
- **R3 resolved:** The epic summary computes the union of story memberships and explicitly renders unassigned scenarios outside it. The new legal mixed-story fixture retains both scenario links without synthesizing stories or edges.
- **R4 resolved:** Opening a related record no longer clears the active overview filter. Assigned and independent nonempty filter→record→Back assertions preserve exact kind/IDs/work_id and restored row. Empty filter→scenario→Back retains its exact empty set and explanatory state; Back is disabled at initial and returned root, and explicit Clear removes the filter.

The earlier independent checks apply to the identical complete source tree: exact nonempty/empty kind/IDs/work_id survive record/scenario inspection and Back; returned rows/empty message are correct; root Back is disabled before and after; explicit Clear removes the filter. Shared-task alias selection, mixed story/unassigned navigation and app-entry routes remain correct. Guards observed zero eager evidence inspection and zero test-source read_text/read_bytes calls. This review attests unchanged-tree applicability; those probes were not rerun.

## Exact execution and TDD continuity

New final-green `4e556768cf0f4c6cafa9a4609d5e63ec` has candidate/source `c4811dee08c4abe35028e570c04bdd49bb10ef4b`, task scope WB-005, exact accepted spec/plan/source digests, collection ok and exit 0. Both WB-overview and WB-summary-links pass. The retained adapter JSON agrees with the report and actual log; duration is 6.979s. Log SHA-256: `30bcd09e656f26486ef7aa7e7d8e139ad2702dd568b20e429e161323c54a715a`.
Canonical report digest: `c682a96244afe1cdf0902f192f96f1ff9fa265a4b48927acb4bbe224f837afaa`. Report-file SHA-256: `72cd24b5c804706c063fd1d99d46cb9df7446c76d0d8ba8249b2beed815af67d`.

Prior genuine overview red aa8a402513634ddc8f93bb621b850f44 and filter red 93f292f55bc94834b80c97249c6bd0f4 retain verified report/log hashes. The latter fails the filter assertions while already-fixed overview passes. Red fails before the later empty-filter fixture; green executes it. TaskResult wording loosely attributes empty/back behavior to overview, but precise method ordering and retained reports supply the assessment. No TDD exemption.

## Individual semantic assessments

### EM-008 — APPROVED

This task now delivers app-routed overview/story/scenario details with explicit real versus missing story membership, shared-task ancestry, canonical task/test links and route/filter return context. The admitted mixed-story fixture preserves both direct and story-owned scenarios without synthetic relationships. Later selected task/test/result renderers remain separately assigned.

The actual app tests exercise no-story disclosure, mixed story/unassigned summaries, scenario-2→shared-task alias→Back and exact nonempty/empty summary filters through return navigation. Independent story round-trip and strengthened filter-return/root-Back checks corroborate the task slice.

### EM-010 — APPROVED

The assigned summary navigation captures stable task/decision/scenario IDs with work identity, opens the selected canonical record and now preserves the filtered set on return. Unknown results stay Not loaded; no metadata status or declared lifecycle is promoted to verified completion. Later task/decision/result detail work remains separately assigned.

The expanded summary case clicks blocked→Open build→Back, compares the exact filter during and after inspection, and checks the restored task row. It also covers an empty filter and disabled initial root Back. Independent checks verify disabled returned-root Back and explicit Clear for both empty/nonempty sets.

### EM-012 — APPROVED

The assigned overview/scenario surface remains lazy: it consumes captured metadata without evidence inspection or test-source reads. Independent text and byte guards pass across filter/record/Back journeys. This approves only the structural contribution; later browser/accessibility/latency requirements remain separately assigned.

The original eager-inspector assertion and test-source read counter are retained. Independent Path.read_text and Path.read_bytes guards observe zero reads of test_fixture.py while navigating both nonempty and empty filters, scenarios and return routes.

### WB-overview — APPROVED

Actual app routes expose purpose, task progress/readiness/lifecycle, attention and unknown results lazily, then canonical scenario details and recorded tasks/tests. The new admitted mixed-story fixture checks both story-linked and unassigned scenario overview controls, opens the shared task under scenario-2 and asserts correct alias, ancestry and Back restoration. Independent story→scenario→Back and zero text/byte source-read probes corroborate the task slice.

Counterexample: Removing unassigned-summary rendering leaves overview:scenario:scenario-2 absent; selecting the first task alias yields build instead of build@scenario-2; clearing route history disables Back. All three are collected in the new behavior-red fixture before its aggregate assertion.

TDD continuity: Genuine remediation red aa8a402513634ddc8f93bb621b850f44 at 16ba62d96c4648c33d56ba6a55a8dea9951daeee fails this case by behavior_assertion on unassigned summary row, shared task alias and Back history. Its complete overview test method AST is unchanged through current candidate 06f2da8f3831b4926a0ec43f1a83645b23fcd207. Latest filter-specific red 93f292f55bc94834b80c97249c6bd0f4 correctly passes this already fixed case. Final green 9de43ecfeca54b6d904914fbcec171f2 passes at the exact candidate. All reports/log/source bindings verified; no exemption. Merged exact candidate c4811dee08c4abe35028e570c04bdd49bb10ef4b has identical complete Git tree b49608e729b28fa564df5a46364f64290e40e269 to approved 06f2da8f3831b4926a0ec43f1a83645b23fcd207; genuine filter-red commit 2c9d0587b51875e6c765530c897dca9e77ccd27c is now an ancestor. New exact-candidate final-green 4e556768cf0f4c6cafa9a4609d5e63ec passes both assigned cases, with retained adapter results/log/source digests independently checked. No exemption.

### WB-summary-links — APPROVED

The case checks exact blocked/open-decision filter IDs and work identity, Clear behavior and honest unloaded results, then opens filtered build and verifies task detail. Its new aggregate assertions preserve the exact filter during inspection and on Back, restore the intended row, and cover an empty blocked set through scenario navigation/Back with an explicit empty message. Root Back is disabled. Independent checks additionally verify disabled Back after return and explicit Clear for both sets.

Counterexample: Clearing the filter before navigate returns to purpose with None and no restored row. The accepted red fails all three aggregate checks: filter discarded on opening, filter not restored on Back, and filtered task absent. Treating an empty list as no filter would also remove the explicit empty-set state asserted by the final test.

TDD continuity: Accepted filter-specific red 93f292f55bc94834b80c97249c6bd0f4 at 2c9d0587b51875e6c765530c897dca9e77ccd27c collects both cases and fails this case by behavior_assertion at its aggregate filter assertions. Exact final green 9de43ecfeca54b6d904914fbcec171f2 passes both at 06f2da8f3831b4926a0ec43f1a83645b23fcd207. Mapped test-file bytes are identical red/final. The red fails before the later empty-filter fixture; the final green executes it. Genuine prior reds also anchor initial summary/filter-kind behavior. No exemption. Merged exact candidate c4811dee08c4abe35028e570c04bdd49bb10ef4b has identical complete Git tree b49608e729b28fa564df5a46364f64290e40e269 to approved 06f2da8f3831b4926a0ec43f1a83645b23fcd207; genuine filter-red commit 2c9d0587b51875e6c765530c897dca9e77ccd27c is now an ancestor. New exact-candidate final-green 4e556768cf0f4c6cafa9a4609d5e63ec passes both assigned cases, with retained adapter results/log/source digests independently checked. No exemption.

## Source digests

- `_ask/tests/test_engineering_workbench_overview.py`: `0bf95fa1ea93286973128d52146bd6086582cbdf045d3e0ee5e99df4c763cc1e`
- `_ask/ui/streamlit_app.py`: `af953ad4b6c37ab3e37f777980e04172a060e3992d1c39b8a487e099cc450eae`
- `_ask/ui/workbench_overview.py`: `d05fb08decf043bf59d3b5380ad2e3489c950968fcbbf7115024a62cd096df59`
- `_ask/ui/workbench_scenarios.py`: `511630ba7bc02d9893643f0fcb5c937f8cfe3d670589f8821f7f24f8e852c694`
- `_ask/ui/workbench_stories.py`: `a369e10e0c0dfc930f9e14c1046efd31f8752a823c248aac55b581eb9ed9e40a`

## Semantic artifact

`work/structured-agentic-environment/traceability/review-input-WB-005-c4811de.json`
SHA-256: `4e24a9139286f42be5af208a11513388f1f6ce58c91fd1fd2fef6904f94b45b5`

Read-only review_errors: `[]`. Scope is the assigned WB-005 contribution; later renderers, UI checkpoints and overall acceptance remain separately assigned. No source/coordinator-state edits, commit, recording or integration.
