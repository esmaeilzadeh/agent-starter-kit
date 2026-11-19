# Plan: client security and model decision flow

## Specification

Exactly one accepted specification: `specs/current/client-security-hardening.md`
with canonical registry `specs/current/client-security-hardening.json`, revision 2.
CSH-001–008 retain revision-1 behavior; CSH-009–012 are the approved model-flow
extension. The exact human response `approved` binds the complete revised intent.
The proposed-draft title and historical pending sentence inside the byte-preserved
intent are superseded by the approval record, not another approval request.

## Authorization and execution boundary

The plan-ready endpoint was reached, then the human explicitly directed
`implement`; that later direction extends execution authority and is recorded in
`continuation.md`. What, Why, assumptions, accepted intent bytes and intent
confirmation are unchanged. Execute the reviewed TaskGraph in order. CSH-01 must
first author and independently review the CSH-T38/T39 test-only Red baseline;
production edits begin only after that approval. Preserve the remaining task,
review, verification and final acceptance evidence required below.

### Authorized implementation amendment — 2026-11-19

The human's explicit `implement` direction supersedes the earlier plan-only
endpoint. The CSH-01 test baseline is committed at
`371e4a5741f34afb0b2c37401fc847dc14309664`; frozen run
`01ba1187a3584c9184579b9af66fdc07` collected CSH-T38 and CSH-T39 and recorded
behavior-assertion Reds. Independent reviewer `gpt-6-astra/security-plan-review`
approved that exact baseline. CSH-10 remains pending; this early evidence does
not advance its task state. Continue implementation from CSH-01.

## Approach

One branch, `agent/client-security-hardening`; one writer. Ten bounded tasks run
in the order below. The dependency chain serializes every shared source and
generated path; no parallel conflicting branches. Reuse current shell dispatch,
Git, Python standard library, runtime bindings and model overlay. Add small shared
helpers only for the trust, write-transaction, environment and model capability
boundaries that genuinely have multiple callers. No framework, sandbox service,
UI redesign or new general dependency manager.

Frozen planning authority stays at commit
`88035127763fb1436775c13c941fbcba7484d581`, location
`/tmp/askit-security.e0Qyvz/frozen`. Never upgrade the pin from this product checkout
during execution. Source observations and local CLI help are planning evidence,
not exploit proof, live availability, package safety or runtime switch evidence.

## Work breakdown

Owned paths are exact in `inner-loop/tasks.yaml`; the abbreviated column names
the same surfaces. Each task has executable cases and immutable candidate evidence.
Shared owned paths occur only across explicitly ordered tasks.

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| CSH-01 | Verified distribution and dependency approvals | none | askit, _ask/scripts/askit-bootstrap.sh, _ask/scripts/upgrade-kit.sh; remaining exact globs in TaskGraph | CSH-T01, CSH-T02, CSH-T03, CSH-T04 | Reviewed candidate, mapped case results and task integration record |
| CSH-02 | Launcher trust and completion opt-in | CSH-01 | askit, _ask/scripts/ask-complete.sh, _ask/scripts/install-user-completion.sh; remaining exact globs in TaskGraph | CSH-T05, CSH-T06, CSH-T07, CSH-T08 | Reviewed candidate, mapped case results and task integration record |
| CSH-03 | Complete write preflight and durable recovery | CSH-02 | _ask/scripts/install-kit.sh, _ask/scripts/upgrade-kit.sh, _ask/scripts/copy-project-config.sh; remaining exact globs in TaskGraph | CSH-T09, CSH-T10, CSH-T11, CSH-T12, CSH-T13, CSH-T14 | Reviewed candidate, mapped case results and task integration record |
| CSH-04 | Private tracker credentials and migration | CSH-03 | _ask/scripts/setup.sh, _ask/scripts/tracker-config.py, _ask/scripts/tracker-mcp.py; remaining exact globs in TaskGraph | CSH-T15, CSH-T16, CSH-T17, CSH-T18 | Reviewed candidate, mapped case results and task integration record |
| CSH-05 | Allowlisted verifier environments and private outputs | CSH-04 | .agents/ask/verification/run.py, .agents/ask/verification/plan.py, .agents/ask/verification/environment.py; remaining exact globs in TaskGraph | CSH-T19, CSH-T20, CSH-T21, CSH-T22, CSH-T23 | Reviewed candidate, mapped case results and task integration record |
| CSH-06 | Validated atomic runtime generation | CSH-05 | _ask/scripts/sync-runtime-agents.py, _ask/scripts/sync-cursor-binding.sh, _ask/scripts/sync-codex-skills.py; remaining exact globs in TaskGraph | CSH-T24, CSH-T25, CSH-T26 | Reviewed candidate, mapped case results and task integration record |
| CSH-07 | Explicit loopback workbench startup | CSH-06 | _ask/scripts/ui.sh, _ask/tests/test_client_workbench.py; remaining exact globs in TaskGraph | CSH-T27, CSH-T28 | Reviewed candidate, mapped case results and task integration record |
| CSH-08 | One Grill model decision and resumable stage reuse | CSH-07 | .agents/ask/stages/01-grill.md, .agents/ask/stages/03-spec-challenge.md, .agents/ask/stages/07-review.md; remaining exact globs in TaskGraph | CSH-T29, CSH-T30, CSH-T31, CSH-T32, CSH-T40 | Reviewed candidate, mapped case results and task integration record |
| CSH-09 | Runtime capability adapters and orchestrator handoff | CSH-08 | .agents/ask/stages/06-implement.md, .agents/ask/bindings/runtimes/**, _ask/scripts/model-decisions.py; remaining exact globs in TaskGraph | CSH-T33, CSH-T34, CSH-T35, CSH-T36, CSH-T37 | Reviewed candidate, mapped case results and task integration record |
| CSH-10 | Complete client journeys and migration guidance | CSH-09 | _ask/tests/test_client_journeys.py, _ask/tests/client_security_fixtures.py, README.md; remaining exact globs in TaskGraph | CSH-T38, CSH-T39 | Reviewed candidate, mapped case results and task integration record |

## Task designs

### CSH-01: Verified distribution and dependency approvals

Criteria: CSH-005. Initial authorship of the CSH-10 journey tests is also owned
here so their behavioral Red precedes all production changes; their execution
obligations and final completion remain exclusively CSH-10.

Before any production edit, author `test_client_journeys.py` and its shared
fixture with the exact CSH-T38/T39 assertions against existing public CLI entry
points. Commit that test-only baseline as an ancestor of all later candidates.
The coordinator runs the accepted contract with `--scope task --task-id CSH-10
--phase red --candidate-sha <baseline-sha>` and retains the actual results.
Both cases must collect and fail observable behavior assertions; missing imports,
helper modules, setup failures or artificial failure supply no Red. No CSH-10 task
start or state transition is implied by this early evidence capture. If baseline
assertions already pass, retain Green and resolve their classification through
independent contract review before implementing, without altering behavior to
manufacture Red. Review the baseline assertions before production starts.

Resolve a selected release to a full immutable commit before fetched kit code runs. Require an expected full commit from the trusted installed release record or an explicit user selection; verify fetched HEAD and working-tree contents against it. Never execute the downloaded install/upgrade helper before that check. A tag is only a lookup name, not independent proof. Preserve the direct checked-out-script explicit-action boundary. Use the installed launcher for bootstrap and recovery entry points.

Replace mutable bundled skill references with full commit pins in the existing manifest. Preserve each skill's existing upstream content selection: resolve the existing tag, review its exact commit/tree and record it, rather than upgrading to a new tag. Record exact skills CLI and mcp-atlassian versions in a small dependency pin record, with source revision and artifact integrity. Compare the locally cached skills 1.5.18 candidate (Node >=18) with the existing supported Node floor before selection; a newer CLI is not automatically compatible. No external package may run until the exact pin diff is reviewed. Resolve package/skill metadata as task data, using local source fixtures for tests; inability to obtain provenance or compatible versions blocks that dependency, not a floating fallback. This plan does not claim a dependency vulnerability audit.

Store approval for new project source+commit+skill path outside the repository; repository config cannot approve itself. Ask before any new-source fetch, including noninteractive refusal. Validate all manifest entries and destination paths first. Propagate mandatory prepare failures through install, upgrade and bootstrap instead of swallowing exit codes. Reuse standard-library hashing/JSON and existing Git/install commands; add no general package manager.

### CSH-02: Launcher trust and completion opt-in

Criteria: CSH-001.

Add an installed-launcher trust action and refusal before project delegation. Use the physical Git checkout root as the trust key: symlink aliases of that root share trust; a moved or different checkout requires trust again. The identity is a deterministic SHA-256 manifest of the dispatcher and every kit/runtime executable or executable configuration it can reach, including installed helper/module trees, verification commands, hooks and configured code-loading paths. Hash path, file kind, mode and content, not just ask or a Git HEAD. Reject escaping executable symlinks. Explicit trusted-project code can execute with the account's privileges; this is enrollment, not a sandbox.

Keep trust records in an owner-only user directory, bind them to checkout+identity and atomically replace them. Changes to execution-bearing overlays, helpers or upgrade content invalidate trust. Ordinary model/public metadata that cannot alter execution is excluded by an explicit classification and tests. Show the identity being trusted; the project cannot grant its own trust. Noninteractive daily commands require an existing matching record. Completion candidate lookup retains its focused Green guard (T07). Launcher help, completion snippet generation and their lack of implicit startup writes are new T08 behavior requiring real assertion Red. Completion and launcher help use installed code and never call the project dispatcher. Remove daily automatic completion installation; provide one explicit opt-in action with validated startup-file writes.

### CSH-03: Complete write preflight and durable recovery

Criteria: CSH-002, CSH-003.

Build one complete write inventory before the first mutation: kit files, generated runtime files, overlay migrations, ignore-file edits, launcher/completion outputs and prepare destinations. Classify ownership from the verified installed manifest and known generated outputs; a directory name alone proves nothing. Reject symlink components (including dangling links), path escapes, special files, unexpected types and unowned collisions. Force does not override those refusals. Treat a symlinked repo alias by canonicalizing the selected root once, then validate descendants. Existing project settings remain project-owned and trackable.

Use a small standard-library filesystem transaction shared by install, upgrade and sync: render/stage outputs, save prior bytes, modes and existence, fsync a journal/backups in private state before replacement, publish, then finalize. Recover caught failures before returning. After SIGKILL/process interruption, the installed launcher can recover before delegating to a partially replaced project dispatcher. Validate journal target identities and paths before recovery. Recovery is idempotent and retains backups on failure. If a client changed a path since the recorded transaction postimage, refuse destructive rollback of that path and name the conflict. Clean rollback preserves client state and a retry succeeds.

Stage prepare/sync filesystem outputs with the installation so later mandatory failure restores the earlier kit state. Shared cached downloads and remote side effects are outside filesystem rollback; no client output is published until required preparation succeeds. Keep the prior preservation repair at product base 11c95e9; a newly observed preservation violation must reproduce and receive a separate focused repair before overlapping installer changes. Do not rename failing old guards into new feature Red cases.

### CSH-04: Private tracker credentials and migration

Criteria: CSH-004.

Store secret JSON in $XDG_CONFIG_HOME/askit/projects/<sha256-of-canonical-root>/credentials.json (default ~/.config); create owner-only directories and files with 0700/0600 before writing. Validate owners, types and symlink components on read/replacement. Keep public tracker type/URL and local project settings in the repository overlay. Require HTTPS URLs with no userinfo; avoid echoing rejected secret-bearing inputs. Use a narrow data loader and an MCP-launch wrapper that injects only the configured tracker credentials into the selected pinned tracker process; never source an env file or place values in argv or generated project/user MCP configuration.

Provide explicit migration from the legacy assignment subset: blank/comment lines, known NAME=value and quoted literal assignments, optionally export. Parse as data without variable expansion, command substitution or eval; preserve literal token contents and reject unsupported syntax with a value-free diagnostic. Write and sync private storage before removing migrated secret values from the active worktree. Preserve non-secret settings, index and Git history. Inspect tracked and staged legacy paths without printing contents, warn about history and require rotation guidance even if the current file was cleaned. Never silently stage removals or rewrite history. Apply the transaction/path checks to public setup outputs and MCP configuration; user-wide MCP edits require explicit opt-in. Keep human-only setup interactive; tests drive a disposable PTY with dummy values, never a real account.

### CSH-05: Allowlisted verifier environments and private outputs

Criteria: CSH-006.

Use one environment builder at both static CheckPlan and instrumented-case subprocess boundaries. Base caller variables: PATH, HOME, USER, LOGNAME, LANG, LC_ALL, LC_CTYPE, TZ and TMPDIR. Validate names; do not inherit BASH_ENV, ENV, CDPATH, PYTHONPATH/PYTHONHOME, loader injection controls, shell functions, token variables or unrelated ASK_* state. PATH supplies user-installed tools in the approved trusted-local threat model. Invoke the command shell without login/rc startup.

Add an optional env_allow list to each CheckPlan check and traceability runner. It permits explicit named caller extras, not arbitrary expansion; preserve it when expanding preset globs. Runner-generated ASK_ROOT, PYTHONDONTWRITEBYTECODE, runtime-output location and candidate package paths are assigned after caller filtering and cannot be overwritten by extras. Construct Python collection paths from the candidate and declared test root, not an inherited PYTHONPATH. Preserve case selection, interpreter identity, roles and result lineage.

Keep source behavior tests and public summaries stageable, but create retained raw output/log directories privately (0700) and files privately (0600), including replacement under permissive umask. Exclude raw logs from ordinary Git add through precise ignore rules. For already tracked legacy logs, warn and require explicit cleanup; ignore rules cannot untrack them. State in verify help that checks remain trusted account-local code with filesystem/network access and that untrusted changes belong in isolated CI. Run the existing traceability runner/collection regressions at this boundary.

### CSH-06: Validated atomic runtime generation

Criteria: CSH-007.

Keep the existing model override sources and resolve all values before publishing any runtime output. Accept nonempty single-line strings without control characters; safely escape quotes and backslashes. Mapping-looking strings remain strings; do not restrict users to a hard-coded name catalog. Validate types and every selected runtime template. Render into memory/staging and round-trip each model field with its format parser (TOML and YAML/frontmatter) to exactly one original scalar.

Run validation before the earlier Cursor projections as well as the final agent files. Commit the complete rendered set with CSH-03's transaction, so an invalid value in a late runtime leaves every prior output untouched. Exercise project, workstream and environment overrides. Preserve generated review permissions and all existing stage behavior; generated files come from their canonical templates.

### CSH-07: Explicit loopback workbench startup

Criteria: CSH-008.

Pass --server.address=127.0.0.1 explicitly unless the invocation supplies an explicit server.address value. Accept that deliberate override once; reject malformed duplicate overrides rather than relying on ambiguous last-argument behavior. Ambient user/project Streamlit configuration or STREAMLIT_SERVER_ADDRESS must not widen the default listener. Preserve existing port and other valid UI arguments. Unit-test argv construction and use the installed optional UI requirements for a real listener integration smoke test. On Linux CI, inspect the child listener inode/address through /proc and check HTTP health; use an equivalent supported socket observer on other platforms. An argv-only stand-in cannot supply listener evidence. No application/UI redesign is needed.

### CSH-08: One Grill model decision and resumable stage reuse

Criteria: CSH-009, CSH-010, CSH-012.

Present one complete resolved model table in Grill, including role/default, concrete model, stage exceptions, reviewer relationships and implementation update policy. One Confirm model plan / Change selected models interaction accepts defaults or collects only requested overrides together. Resolve submitted complete exceptions without serial questions or a second defaults approval. Keep intent confirmation and final acceptance distinct. Record model consent and latest-accessible versus exact implementor policy alongside the existing work/<id>/models.yaml overlay, with runtime and evidence; use that overlay's existing precedence rather than introducing a resolver chain.

Stage prompts read the saved decision and launch the selected independent reviewer directly, including same-family selections. Remove routine Challenge/Review pickers and family consent loops from canonical sources; regenerate all runtime views. Reuse explicit prior choices and configured defaults for legacy workstreams, without asserting historical consent to the new latest policy. Collect that policy at the next authorized Grill or explicit user change; a legacy implementation entry retains its previous configured implementor until then.

Inspect all model resolver callers. The binding README says work overlay precedes env, while the current resolver checks concrete env slugs early. Pin the documented precedence for this feature's recorded exact overrides and test that ambient env cannot replace a saved choice. If this reveals an independently reproduced existing-contract defect, record its focused repair separately and serialize it before this task's overlapping resolver edits. Do not invent an unavailable-model gate from stale documentation alone. Genuine unavailable-model/capability/scope escalations request only the missing decision and retain prior choices.

### CSH-09: Runtime capability adapters and orchestrator handoff

Criteria: CSH-011, CSH-012.

Put runtime discovery, family/version ordering and in-session switch support in the existing runtime binding layer with a small adapter seam. Use a current authenticated runtime catalog or equivalent account capability evidence, not a static picker or an invented universal latest-model endpoint. Resolve the most recent accessible implementor in the configured family (currently Composer for Cursor and Luna for Codex) under Grill's policy. Preserve exact human overrides. If discovery cannot establish identity/order/access, report the concrete missing evidence rather than guessing a model from lexical ordering.

Check the real orchestrator identity only when implementation is the authorized next action. If it matches, continue. If the runtime exposes a supported current-session switch, request it and verify the resulting orchestrator identity before edits/task dispatch. With no supported switch API, give a single manual handoff naming the model and the runtime's actual UI/command, then stop. Resume after observation or explicit acknowledgment when introspection is unavailable, preserving its provenance; an unverifiable claim is not an automatic-switch success. Child spawn, startup --model flags and edited config files are not current-session switch evidence.

Local inspection establishes only that Codex exposes a startup --model option and a cached Luna entry; it does not establish an in-session switching API or current account access. Cursor discovery must be probed similarly. Mark capability unknown/unsupported explicitly. Never use an undocumented API to avoid the approved manual fallback. Reuse these checks in first-entry and resumed inner-loop routes so no worker can start before the authorized handoff. A plan-only stop returns before this gate. Tests use fake adapter events for all branches; retain real supported-runtime smoke evidence before claiming automatic capability.

### CSH-10: Complete client journeys and migration guidance

Criteria: CSH-001, CSH-002, CSH-003, CSH-004, CSH-005, CSH-006, CSH-007, CSH-008, CSH-009, CSH-010, CSH-011, CSH-012.

Use the CSH-01-authored CSH-T38/T39 journey tests and retain their early
coordinator-executed CSH-10 assertion Red against the same accepted spec/plan.
The baseline must be an ancestor of the final candidate; independent review
checks exact assertion continuity and final Green. Do not defer initial journey
test authorship until this task, relabel the new behavior as regression or
weaken assertions. Then run the full disposable client journeys and document the supported acquisition/trust boundary, install/upgrade recovery, source approval, credential migration/rotation, verifier environment extras, private-log cleanup, loopback override and one-time model decision/handoff. Replace mutable curl-pipe instructions that imply verified acquisition with explicit acquisition/expected-revision guidance; the initial trusted launcher remains a user trust decision. Include existing-client and legacy model-record migration without automatic Git index/history edits.

Map every changed entry point to a focused unittest case; reuse existing shell journeys as subprocess fixtures or Green regressions where they already protect accepted behavior. Keep raw outputs private. Finish independent semantic review and coordinator Verify only when later implementation is explicitly authorized. This task's contract is planned now; it is not executed in this planning session.

## Verification approach

`test-plan.json` is the canonical 40-case inventory. Every case has its explicit
unittest selector, runner, source path, Given/When/Then and per-criterion assertions;
every case belongs to exactly one task. Engineering Model Scenarios bind the
exact canonical case ID and plan digest, not merely a shared criterion. All twelve
criteria require executable evidence; none is review-only. Existing shell tests
are additional boundary regressions, not substitutes for instrumented cases.

At each later authorized implementation task, except the explicitly early-captured
CSH-T38/T39 journeys: inspect every caller, add the
focused cases, capture genuine assertion Red for new behavior, then implement,
refactor, commit and obtain independent review of the candidate and assertion
continuity. Collection/import/setup failures supply no Red. CSH-T07 (`--complete` candidate lookup only)
and CSH-T11 (client preservation) protect existing accepted behavior and are Green
regressions; establish their baseline without manufacturing failure. If a planned
new case already protects accepted passing behavior, retain it as Green and amend
the classification with independent review before accepting a new contract pin.
Never weaken its assertions to force Red. Do not invent historical results.

Use the frozen traceability unittest adapter for case execution. Reuse precise
existing shell regressions at their owning task boundary: self-install/prepare
for CSH-01; launcher/completion for CSH-02; install/upgrade for CSH-03; setup for
CSH-04; traceability contracts/runner/entrypoints for CSH-05; runtime sync for
CSH-06 and model routing for CSH-08/09. Run the broader repository CheckPlan once
at final implementation verification, repeating only for new changes/failures.
No behavior suite or product Verify is represented as run in this planning session.

## E2E

Applicability: applies. Python unittest cases launch actual CLI subprocesses in
disposable Git repositories with isolated HOME, XDG config/cache and launcher
prefix. Use local Git sources, fake package executables, dummy tokens, PTYs for
the human-only setup journey and fake coding-agent model catalogs/switch adapters.
Never use real tracker accounts, live tokens, paid model calls or production data.
Marker executables observe forbidden delegation. Snapshot full destination trees,
file modes, Git index and outside sentinels for write/recovery/migration assertions.
Abrupt-process tests kill only their owned child and recover through the installed
launcher. Each test cleans up subprocesses, temp repos, ports and user directories.

CSH-T28 observes a real Streamlit listener using installed optional UI requirements;
it is integration evidence, not a fake argv E2E. CLI install/upgrade/verification
and model-flow journeys are CSH-T38/T39, with focused E2E cases at earlier task
boundaries. Model-flow E2E uses the kit's public coordinator path with a fake
external runtime, and proves prompts, identity and dispatch ordering rather than
claims about vendor internals. Actual automatic runtime switching needs separately
retained capability smoke evidence when supported; unsupported switching uses the
specified manual journey. A missing optional dependency is a setup failure, not a
passing or silently skipped acceptance case.

## Risks and escalation

Risk: HIGH (code execution, credentials and client filesystem writes). Approval
covers the specified policy changes; independent review and focused tests remain
required. Local verification retains account filesystem/network access. The
transaction is a cooperative local filesystem mechanism, not a distributed or
third-party side-effect rollback. A concurrently edited client file must survive
recovery or produce an explicit conflict, never silent overwrite.

Escalate genuine changes to What/Why/criteria, loss of client-owned data, a wider
trust identity promise, unavailable immutable dependency provenance, incompatible
installer/runtime requirements, uncertain accessible model ordering, an unavailable
exact override or unverified automatic orchestrator switching. The approved manual
switch path handles unsupported capability without inventing an API. Documented
versus observed existing precedence/preservation defects need reproduction and a
separate focused repair before overlapping changes. Park unrelated findings.

## Contract and completion evidence

The accepted test pin authorizes the exact spec, plan, graph and mapped obligations.
Implementation authority is extended by the later explicit human direction
recorded above. Each task still requires candidate-bound Red/Green where
applicable, independent review, and coordinator integration evidence.

Later implementation completion requires candidate-bound semantic review, actual
Red/Green where applicable, full final coordinator Verify and human acceptance.
`acceptance.md`, `review.md` and `verification.json` seeded by start-work are not
populated as product completion evidence by this plan. Retain planning validation
and independent plan review separately. The frozen verifier may be invoked with
an explicit product root; do not accidentally validate its own frozen workstream.

## Out of scope for this plan

Managed execution of untrusted branches, hosted workbench access, broader workflow
redesign, automatic Git history/index rewriting, a new release signing service,
model-price optimization, and arbitrary child-model substitution for an
orchestrator.

## Endpoint

The plan-ready milestone is complete and its original stop has been superseded by
the recorded implementation direction. Finish the ten TaskGraph tasks in order,
run final coordinator Verify, and leave workstream acceptance for the human.
