# Independent WB-005 remediation review — 238acc8

- **Decision:** REJECTED
- **Boundary:** ok
- **Reviewer:** /root/review_wb001
- **Model/runtime:** gpt-6-astra / codex
- **Parent model:** gpt-6-luna
- **Candidate:** `238acc80169ab7db809fb940794bc98d96c968a3`
- **Task/accepted base:** `dcae11d61c2b73745ba9f5b2187065792d84ac46`
- **Spec digest:** `f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb`
- **Plan digest:** `4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8`
- **Graph digest:** `ad8e3e6a647d83b6b699fbe5c15e13a2ae8c0bc880be686e1cc9e5cc91a8664d`
- **TaskResult Git blob:** `291dd1189690a0f57b7423f9d2d5ddead417258c:work/structured-agentic-environment/inner-loop/results/WB-005.json` (`wb005/submission`)
- **TaskResult SHA-256:** `43cbd2793d5ad580ed27e0b07611aa223ad179a2faae0452f6f91f99a58b9ae4`

## Remaining finding

### R4 — medium — `_ask/ui/streamlit_app.py:74`

`_open_related_route` still clears the overview filter before pushing the record route. Back restores only the epic ID and drops the exact filtered set. The accepted design says route state includes filters and Back restores context; the prior R2 also requested retaining filter context.

**Independent reproduction:** View blocked tasks sets `{"kind":"blocked","ids":["build"],"work_id":"pilot"}`. Open record correctly displays build. Click Back: route is `purpose`, `_engineering_overview_filter` is `None`, and `overview:filter:clear` is absent. Work/source identity has not changed. Preserve the filter through record inspection/return; clear it through explicit Clear or incompatible source/work change. Add a count→record→Back regression that checks the exact restored IDs/work context.

## Prior findings

- **R1 fixed:** Collection kinds normalize to canonical route kinds; blocked Open record now reaches task detail. Independent decisions/scenarios filter links also reach the correct routes.
- **R2 original reproduction fixed:** The current scenario ancestry chooses the correct task alias, and navigate preserves route history. The mixed fixture opens `build@scenario-2`, then Back restores scenario-2. The remaining filter-return portion is R4 above.
- **R3 fixed:** Mixed recorded story membership now exposes both the story-linked and unassigned scenario rows under an explicit gap label without inventing model records or edges.

The actual app still routes epic/story/scenario through the owned renderers. An independent recorded-story→scenario→Back journey passes. Purpose, progress dimensions, canonical scenario relationships, attention and Not loaded results retain their meaning.

## Independent execution and lazy loading

Both exact-candidate task tests pass independently: **2 tests, 5.265s**. Their new regression fixture is legally admitted and aggregates the three original failures. Independent filtered task/decision/scenario links and the recorded-story round trip pass. The final Back/filter check reproduces R4.

Evidence inspection was guarded to raise, and test-source reads were counted through both `Path.read_text` and `Path.read_bytes` across overview/summary/scenario navigation: **zero eager evidence inspections and zero test-source reads**. This structural task requirement remains approved.

## Exact red/green evidence

- **red:** `aa8a402513634ddc8f93bb621b850f44` at `16ba62d96c4648c33d56ba6a55a8dea9951daeee`; canonical report digest `2b993ae6454364553bdeb2b771c875fedc5b2d2b8566dc68681729d741dec3ea`; report-file SHA-256 `a26aa0fb1918900589feb7f6dac8d5ffa961f5acd1c70edaef775bff641775a3`; log `work/structured-agentic-environment/traceability/runs/aa8a402513634ddc8f93bb621b850f44/755ae5315b704f68aa54f83f2f6f659c.log`, SHA-256 `3f488004f888b85ee3e791327190e185521fcbaa7f4be131bbca6a3b4d54829d`.
- **green:** `301391f9c8a144709ad80891c4d8ca29` at `238acc80169ab7db809fb940794bc98d96c968a3`; canonical report digest `6e3260fa6b6fa356f71958837969506530912a042bfa7ecbc127f6cad4b9faa2`; report-file SHA-256 `18367e78e3497409492ae4fcd7a0170af6b05fb360179cc540a984dff795f983`; log `work/structured-agentic-environment/traceability/runs/301391f9c8a144709ad80891c4d8ca29/24dcb95d64d64258a7634895c147a4d3.log`, SHA-256 `a460ccf73cc1ef51639678fb913ed6b70cce759b5b940225830c6bcc50c8f09c`.

Both cases collect successfully and fail by behavior assertion in red. WB-overview reports the missing unassigned summary row, wrong shared-task alias and discarded Back history; WB-summary-links reports purpose != build after Open record. Exact-candidate final green passes 2/2 (retained duration 5.483s). Mapped test-file bytes are identical between the accepted red and final green. Ledger/report contract bindings, case/execution source identity, actual source digests and retained log bytes agree. No exemption is used. The newly remaining Back/filter return behavior is not asserted in these tests.

## Candidate/result boundary

The TaskResult was read from the exact side-ref Git blob identified above; this reviewer did not replace the older result in the candidate checkout. The five writer implementation/test paths are all owned under the accepted amended WB-005 plan. The raw accepted-base diff also contains coordinator registration metadata and preserved earlier review/runtime artifacts; their provenance is recorded separately in the semantic artifact. Boundary is **ok** for writer source, with no foreign implementation changes. No source or coordinator-state mutation was performed.

## Semantic decisions

- **EM-008 / integration:** REJECTED only for incomplete return filter context; original relationship/alias/overview regressions now pass.
- **EM-010 / integration:** REJECTED because the filtered set is lost on Back from its record.
- **EM-012 / assigned lazy-loading slice:** APPROVED.
- **WB-overview:** APPROVED for the expanded admitted mixed-story and shared-task regression plus preserved lazy assertions.
- **WB-summary-links:** REJECTED; it ends before the missing Back/filter assertion.

## Exact owned-source digests

- `_ask/tests/test_engineering_workbench_overview.py`: `55eaad2104663e65210e6d94defcb7eac301d24feee7b3675de832bf7772c82b`
- `_ask/ui/streamlit_app.py`: `5bff263129517f97dd9a18684762b6f8f9a87899ea486ffa9bd50881decfbabb`
- `_ask/ui/workbench_overview.py`: `d05fb08decf043bf59d3b5380ad2e3489c950968fcbbf7115024a62cd096df59`
- `_ask/ui/workbench_scenarios.py`: `511630ba7bc02d9893643f0fcb5c937f8cfe3d670589f8821f7f24f8e852c694`
- `_ask/ui/workbench_stories.py`: `a369e10e0c0dfc930f9e14c1046efd31f8752a823c248aac55b581eb9ed9e40a`

Companion semantic artifact: `work/structured-agentic-environment/traceability/review-input-WB-005-238acc8.json`. Read-only semantic validation has no candidate/source/inventory binding errors; its only errors are the intentional rejected EM-008/EM-010/WB-summary-links decisions. Earlier rejected review remains intact. No recording, integration or commits were performed.
