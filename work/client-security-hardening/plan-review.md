# Independent implementation plan review

Decision: **REJECTED**. Three small contract corrections are needed before planning acceptance. No new human scope decision is requested.

Reviewer: `gpt-6-astra/security-plan-review`, runtime `codex`, independent child context. Existing submitted Astra selection applies. Parent model: GPT-6; exact variant unavailable.

## Exact reviewed contract

- `contract_sha`: `7e7e5f66fe33801929a037d62027714c85197547`
- `spec_digest`: `664778e240718fadd15f40f9bd23a10d2664b8d3d7d1fc3942426dfc4ad5e8cc`
- `plan_digest`: `133e42874472d10b8288669b4f2e6d81ce6b169c2c5307853fc0f2eef6b6d775`
- `graph_digest`: `3d736ccafdc00c370092499474074a11cee7a8aa99ce7c6091bdff855d68d181`
- `plan_markdown_sha256`: `5de58deda486a52ab5313a236c56f5f28104f4daf025cadec596a085ff27039b`
- `frozen_contract_sha`: `88035127763fb1436775c13c941fbcba7484d581`

## Required corrections

### PR-01: inner-loop/tasks.yaml: CSH-01 owned_paths; test-plan.json: CSH-T04

CSH-01 must propagate mandatory preparation failure through public install, but install-kit.sh is not owned until CSH-03 and currently swallows preparation failure with || true. The first task cannot satisfy its assigned E2E obligation within ownership.

Minimum correction: Add _ask/scripts/install-kit.sh to CSH-01 owned_paths; retain sequential ownership in CSH-03. Include bootstrap propagation in the focused caller check.

### PR-02: test-plan.json: CSH-T07; plan.md: Verification approach

CSH-T07 is classified as a passing regression but includes launcher help and no startup writes. Current askit automatically invokes completion installation for completion/help and delegates help to an existing project dispatcher. That combines new CSH-001 behavior with the existing --complete guard and would bypass required Red for the new portion.

Minimum correction: Keep a narrow --complete completion guard as regression; move launcher help and startup-edit refusal into the new-behavior T08 or another explicitly new case. Establish the actual old guard baseline during authorized implementation; do not claim it has passed now.

### PR-03: plan.md: CSH-10 and Verification approach; test-plan.json: CSH-T38/CSH-T39

The two composed journeys are marked new and authored only in the last task after all relevant behavior has been implemented by CSH-01 through CSH-09. The plan requires Red at each owning task but supplies no way to obtain genuine preimplementation Red for these final journeys. A successful earlier implementation would make those new tests Green on arrival.

Minimum correction: Define an executable baseline capture strategy for these exact journey assertions before earlier production changes, with coordinator/TaskGraph ownership and accepted-contract evidence preserved, or redesign test/task placement so their genuine behavior Red precedes the relevant implementation. Do not relabel new aggregate feature behavior as regression merely to bypass Red, weaken assertions, or introduce artificial failure.

## Coverage and scope assessment

All twelve criteria have executable cases and the required test types. The 40 cases each belong to one of ten sequential tasks, so shared source ownership is serialized. Frozen structural contract validation passes. The engineering model records 12 requirements, 10 tasks and exact identities for 40 scenarios/tests. The source contract remains within the approved security and model-flow scope.

The plan supplies concrete trust keys, full write inventory, durable recovery, private credential migration, verifier environment construction, scalar serialization, loopback precedence and model handoff boundaries. It preserves account-local verification limitations and independent review. Exact dependency pins are task outputs reviewed before package execution; missing provenance blocks use rather than permitting a floating fallback. That is an executable plan choice and does not itself block planning acceptance.

Model tests distinguish the orchestrator from a spawned child, test verified automatic switching and manual resume, preserve old workstream choices without invented consent, and stop plan-only work before model discovery/switch dispatch. Runtime capability probes remain future implementation evidence, with unknown/unsupported states explicit.

CSH-T11 is appropriately a preservation regression subject to actual baseline evidence. PR-02 corrects the mixed new/regression T07; PR-03 supplies the missing evidence sequence for the final new journeys. Per-criterion assessments are in `traceability/plan-review.json`.

## Limits and endpoint

No behavior tests, exploit reproduction, dependency audit or runtime switching checks ran. Source inspection is not proof of a passing or failing behavioral test. This decision concerns the implementation contract only. Correct the findings, commit the revised contract, and obtain a new digest-bound independent review. Stop when Plan is ready; product implementation and acceptance remain unauthorized.
