# Workbench baseline and technology decision

Measured 2026-10-09 against source `48bc7e95806e645bd25a196d9e50c394278a9d64`, before application changes. Raw samples: `planning/performance-baseline-backend.json` and `planning/performance-baseline-browser.json`.

## Environment and workload

Linux x86_64, Python 3.10.12, Streamlit 1.59.2, Playwright 1.63.0, Chromium 153.0.8010.12, local loopback, no network/CPU throttling, browser viewport 1440×1000. Shared development machine; CPU load was not controlled. The actual pilot has 12 model nodes, 12 edges and 9 captured files, linking this workstream and harness-review. Results do not establish large-workload performance or comparative framework speed.

Backend measurements use `time.perf_counter()` around `validate_current(root, work_id)` and `project(snapshot, root, include_evidence=...)`. Ten iterations for validation/light projection, five for full projection. `cProfile` of one full projection attributes about 152ms of 154ms to the two evidence inspections, including 32 Git-related subprocess calls. Current missing-history/authority errors are part of this real workload; successful complete evidence may cost more.

Browser measurement started a fresh test-owned Streamlit process on a free loopback port using the real model root. It performed five page sessions and navigated Objects → Scenarios → Evidence → Overview, then loaded results. Each navigation ended when its new section heading appeared; result loading ended at its loaded-results message. Browser/server were stopped afterward. This measures current UI, not a redesign prototype. The existing user-owned servers were left alone.

## Observations

| Operation | Samples | Median | Nearest-rank p95 |
| --- | --- | --- | --- |
| Capture + validation | 10 | 14.90ms | 20.05ms |
| Projection without evidence | 10 | 1.29ms | 2.02ms |
| Projection with evidence | 5 | 138.68ms | 150.62ms |
| New browser session to epic heading | 5 | 1133.32ms | 2507.08ms |
| Open Objects | 5 | 487.92ms | 613.10ms |
| Open Scenarios, including first evidence load | 5 | 412.69ms | 451.07ms |
| Open already-cached Evidence | 5 | 212.85ms | 237.31ms |
| Return to Overview | 5 | 375.06ms | 498.31ms |
| Request Overview results | 5 | 819.52ms | 1030.86ms |

Fresh process HTTP readiness took 1315.82ms. The first browser session on that process took 2507.08ms. These were separate measurements; a reliable start-to-usable benchmark must measure one interval including all startup stages. At five samples, p95 is the maximum, not a stable tail estimate. A second preflight on the already-running server observed 438–1208ms for first-view readiness and is not combined with the fresh-server sample set.

The recorded Refresh samples use an already-visible readiness control, so they are optimistic lower bounds and are excluded from conclusions. After implementation, measure Refresh with a generation-specific completion marker or changed content assertion. Heading visibility is also only a first-view readiness proxy, not proof all content/paint is finished.

Code inspection identifies eager AST parsing/source reads for every test rendered on Overview, unconditional full evidence projection on Scenarios entry, duplicate Overview/other-view evidence caches, and branch subprocess discovery on every whole-script rerun. These are optimization candidates, not measured individual speedups. Profiling shows correctness-critical evidence/Git work dominates the backend full projection; cache only with reliable integrity invalidation.

## Recommendation and checks

Retain Streamlit initially, replace type tabs with one hierarchy, render only selected node detail, move source/evidence to lazy reads, and avoid duplicate identical evaluations. Do not cache verdicts solely by commit SHA or TTL; accepted refs, review/run/log bytes and captured definitions must remain part of freshness/integrity checks. No cache may authorize a stale form.

New pilot targets are defined in the design and plan. Validate with 20 warm samples and five cold restarts on the same environment, and structural checks at 100/1,000 tasks with recorded relationships/tests/files. Budget misses remain visible. No improvement has been measured yet.

Migration trigger: after bounded native optimization, repeated pilot-budget failure or inability to meet the hierarchy/accessibility requirements justifies comparing a FastAPI read/action adapter plus React/TypeScript/Vite client. Reuse Python validation, guards and evidence inspection. The added API/build/client state and E2E migration likely add 3–5 implementation tasks; this is a task-count estimate, not an elapsed-time promise. A lower-level language is warranted only if profiling identifies a CPU-bound backend bottleneck that it can actually reduce.

## Skill sources applied

Anthropic frontend-design was discovered through the [skills directory](https://skills.sh/anthropics/skills/frontend-design) and read at [pinned revision 41bbe19](https://github.com/anthropics/skills/blob/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/frontend-design/SKILL.md). Its contribution is a deliberate information-led visual direction, a compact token system and wireframe review before building. The subject and audience are already explicit in the human brief.

The Streamlit skill discovery selected the installed 1.59.2 package references for design, layout, selection widgets and performance. Applied guidance: native theming, labeled controls, conditional detail rendering, explicit session identities, forms and appropriately bounded caching. Community skill trees are not vendored. GitHub cloning intermittently failed during `./ask prepare`; already-installed pinned skills were available, and the exact design skill was retrieved/read outside the repository.
