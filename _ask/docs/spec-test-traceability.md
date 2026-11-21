# Spec-to-test completion

Normal workstream completion requires canonical JSON criteria, reviewed test obligations,
actual case execution and independent semantic review. `.agents/verification.yaml`
continues to own static checks. The Python package
`.agents/ask/verification/traceability/` owns validation and completion policy.

## Prepare and pin

1. Spec creates `specs/current/<work-id>.json` (`ask-spec/v1`), with stable
   criterion IDs and observable Given/When/Then. Review-only criteria require a
   reason and an attributable APPROVED decision under the delegation policy.
2. Plan creates `work/<work-id>/test-plan.json` (`ask-test-plan/v1`). Map every
   testable criterion to explicit required types (`unit`, `integration`, `e2e`),
   case IDs, scenarios, per-criterion assertions and source paths. Task scopes
   match the accepted TaskGraph exactly. Review-only tasks may have empty cases.
3. Independently challenge test types and scope. Commit the contracts. Write a
   JSON plan-review decision with `decision: APPROVED`, reviewer, `spec_digest`
   and `plan_digest`. Digests use canonical sorted compact JSON, not file bytes.
   The coordinator records that decision with:

   ```sh
   ./ask traceability accept-plan <work-id> --revision <contract-sha> \
     --reviewer <independent-reviewer> --recorded-by <coordinator> \
     --evidence work/<work-id>/traceability/plan-review.json
   ```

4. Commit `traceability-accepted.json`. The coordinator operation also writes
   `refs/ask/accepted-tests/<work-id>`, an authority commit outside the candidate
   tree; a candidate source commit cannot advance it. Source-only transfers require
   reviewed registration of that local ref before new completion. It pins the spec, plan, TaskGraph and
   delegation policy. A task candidate cannot change these obligations. Revise
   them through Spec Change, independent review and a new accepted pin before
   spawning a new task. `validate-plan <work-id> --revision <sha>` checks contracts.

Use `_ask/templates/{spec,test-plan,test-review,test-results,completion}.json`
for shapes. EXAMPLE values are explanatory; they are never execution evidence.

## Implement and review

Before production changes, commit the failing behavior test and run:

```sh
./ask traceability run <work-id> --candidate-sha <red-sha> --phase red
```

Use one of the instrumented adapters:

- `unittest` accepts `["python3", "-m", "unittest", "module.Class.test_case"]`
  or unittest discovery with `-s`, `-p` and `-t`. Case IDs are the dotted
  unittest test IDs.
- `node-test` requires Node.js 22.18 or later and accepts
  `["node", "--test", "test/render.test.cjs"]` with one or more explicit
  repository-relative `.js`, `.cjs` or `.mjs` files. Use a unique top-level test
  name per file. Set `case_id` to `test/render.test.cjs::renders uppercase`
  and include the file in `source_paths`. The adapter recognizes
  `node:assert` failures inside tests as Red. A change to a mapped test file
  requires a behavior-change review for each mapped case in that file.
- `jest` accepts `["npm", "run", "test", "--", "src/app.service.spec.ts"]`
  or a named Jest script such as `test:e2e`. Declare explicit test file paths
  after `--`. Use the file path and the full Jest name, including any
  `describe` names, as the case ID. For example,
  `src/app.service.spec.ts::AppService returns uppercase`. Include the
  test file in `source_paths`. The adapter uses the project's Jest
  configuration, including TypeScript transforms, and instruments the configured
  environment for one `jest-circus` project. Use the project-level environment
  for the selected files. A case requires an assertion failure in the test body
  to supply Red.
- For Jest, commit the root `package.json` and `package-lock.json`, and ignore
  `node_modules/`. AskIt installs the locked dependencies in the candidate
  checkout with `npm ci --ignore-scripts`. The npm cache or registry must be
  available. Mapped JavaScript and TypeScript test files are reviewed at file
  granularity.

Declare every collected case. Nested Node tests, dynamic Python subtests and
unsupported runners cannot supply completion evidence. The report records
declared selectors, actual arguments and the interpreter used. Setup, import
and runtime errors cannot supply Red.

Existing unchanged regression tests need current execution; new or changed
behavior requires red and final green. The independent reviewer examines actual
assertion continuity whenever source changes between those revisions. A changed
test may carry a typed `tdd_exemption` in its independent review decision only
for documentation, generated projections or nonbehavioral configuration, with
reason, reviewer acknowledgment and APPROVED decision. Changed behavior cannot
use that exemption or a regression label; exemption and recognized red history
are mutually exclusive. New behavior always needs executed red.

After implementation, commit the candidate. Independent review writes
`ask-test-review/v1` JSON bound to candidate, spec/plan/source digests, inventory
base (`contract_sha`), inspected sources, mapped changed test IDs and explained
exclusions for unmapped cases. Each criterion needs explicit
coverage and per-required-type decisions; each test needs an assertion assessment,
counterexample and continuity assessment. `inventory()` and `source_digests()`
in the evidence module provide deterministic inventory/binding data, not semantic
approval. The coordinator records the reviewed decision:

```sh
./ask traceability record-review <work-id> --candidate-sha <candidate-sha> \
  --recorded-by <coordinator> --evidence work/<work-id>/traceability/review-input.json
```

Worker approval fields alone have no authority. Attribution is cooperative;
repository access is not authentication or a security sandbox.

## Verify and complete

`./ask verify` on `agent/<work-id>` executes committed candidate source in
isolated worktrees, runs every static check and every planned behavior case,
and reevaluates reviewed coverage/TDD/execution. A process exit code cannot
stand in for case evidence. Identical static commands share execution but keep
all check identities; an exact equivalent declared unittest command can reuse
the instrumented run. Opaque shell commands never supply case evidence.

```sh
./ask traceability check-completion <work-id>
./ask check-workstream <work-id> --acceptance
./ask record-result --work-id <work-id> --commit-sha <candidate-sha> --result pass
```

Each command reloads underlying contracts, coordinator records, sources and logs.
Changing `completion.json` to pass cannot authorize completion. Task checks use
accepted task scopes and cannot satisfy final workstream evidence. A failed
preflight replaces stale completion/Verify results with a fresh failure. Historical
red attempts with collection failures or unsupported/unmapped cases remain retained
and are listed as rejected attempts; they supply no TDD evidence. Later valid
assertion red and final green can complete the same accepted case.
Detached integration pins verifier tooling to the task's recorded coordinator
base and checks accepted obligations against the immutable candidate pin and
coordinator authority. This allows a separately reviewed contract amendment
accepted after task start while still rejecting candidate-only obligation
changes. Missing runner capability is `migration_required`.
The existing FF-only, state-lock, review and postexecution lineage checks remain.

Candidate-bound records and locks live only under `work/<work-id>/traceability/`.
That subtree and the exact legacy `work/<work-id>/result.json` result artifact are
runtime output exceptions for source-cleanliness checks. Contracts, accepted pins,
implementation plans and other workstream files remain source. Commit source before
running checks; archive runtime evidence afterward, citing its tested source SHA.
Verification without a workstream branch runs static repository checks only; it
cannot authorize a workstream pass. Use explicit work IDs for completion commands.

## Migrate

`./ask traceability migrate <work-id>` creates missing metadata scaffolds without
overwriting history or consumer YAML. It returns `migration_required` until criteria,
obligations and independent decisions are populated and pinned. It invents no
historical red, test results or semantic approvals. Upgrade an old coordinator
runner before accepting new tasks; old unlinked evidence remains readable history.
