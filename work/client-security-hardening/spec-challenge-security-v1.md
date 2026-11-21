# Specification Challenge: client-security-hardening

## Model

- Reviewer: independent Spec Challenge child, `gpt-6-astra`.
- Runtime: `codex`; parent_model: `GPT-6` (exact parent runtime variant unavailable).
- Submitted selection: “continue with astra for review”. This follows the explanation that Astra is the configured adversarial reviewer and that all available runtime models share the `gpt` family. The selection authorizes this independent context; no additional picker is needed.
- Binding: `03-spec-challenge → adversarial → gpt-6-astra`; the human selection controls the reviewer.
- Frozen contract: `88035127763fb1436775c13c941fbcba7484d581`, `/tmp/askit-security.e0Qyvz/frozen`. Its HEAD was checked and matched.
- Writing guidance: prepared product `.agents/skills/writing-for-agents/SKILL.md`, embedded mode. Frozen preparation was interrupted; this review does not claim it completed.

## Specification

Reviewed the approved intent, Markdown specification and canonical JSON registry, revision 1. This is the feature route already recorded in `continuation.md`. Existing client-file preservation remains a separately reproduced repair, with shared installer changes serialized.

Exact bindings:

| Contract | SHA-256 |
| --- | --- |
| Canonical sorted compact JSON specification | `bb74b09e29c9715685c48b9128506ff0cefbb54bb6a6c83ca63a67e5b964e424` |
| Markdown specification bytes | `0d80c30d643e7aa6c6e19dba154cab9220337039d664257226c556096a367c1b` |
| Approved intent bytes | `16067684cb4705dffbe627c935edd4901628f317edf5102ef3d057bc635d1814` |

All eight criteria use `verification_mode: tests`. Markdown and JSON describe the same obligations. The changes address the stated Why: protecting client files, credentials and repository trust, while preserving a usable upgrade path.

## Ambiguities

The following are implementation choices explicitly left to Plan. Resolve them in the plan and test contracts before accepting those contracts; none requires changing the approved What or Why.

1. **CSH-001: executable identity.** Define the canonical checkout identity and the executable kit files included in trust. Hashing only `ask` permits a changed helper behind an unchanged dispatcher. Source evidence: `askit` delegates to project `ask`, which dispatches helpers. Trust must cover executable kit content actually used; a checkout move, symlink alias, helper edit or upgrade must have a documented result. Keep approval records outside project control and make refusal observable with a marker dispatcher that must never run.
2. **CSH-002: complete destination set.** Enumerate kit files, generated runtime files, ignore-file edits and preserved overlays before writes. Existing directories are not sufficient ownership evidence. Resolve symlink components, dangling links, unexpected file types and unknown collisions consistently, including under `--force`. Compare the full destination fixture and an outside sentinel before/after each refusal.
3. **CSH-003: interruption recovery.** Distinguish a caught copy failure, which restores before returning, from abrupt termination, which recovers on restart. Plan durable recovery state and an entry point that still works if interruption affected the project dispatcher. Record metadata needed to preserve executable bits and existence as well as bytes. Exercise recovery failure and repeated recovery without deleting client changes.
4. **CSH-004: migration.** Specify the private location, project association, owner-only creation and handling of an existing unsafe private path. Parse a defined legacy assignment subset as data; unsupported shell syntax gets a value-free diagnostic. Remove migrated secret values from the active worktree only after durable private storage. Preserve public settings and do not silently rewrite the Git index or history. Tracked/staged legacy values require rotation guidance because moving a file does not remove existing exposure.
5. **CSH-005: verified selection and source approval.** Define the immutable identity selected before fetched kit code runs, its comparison with the fetched tree, and the failure result for a mismatch or dirty cache. Bind new-source approval to the source and immutable revision; a project manifest must not grant itself approval. Exact reviewed installer versions and bundled skill commits belong in the plan. This criterion does not imply a new release-signing service or a claim that a matching revision is benign.
6. **CSH-006: execution environment.** List the base allowlist and the existing check configuration field that grants extras, or the smallest compatible field addition. Keep coordinator-generated instrumentation variables separate from caller-supplied values. Define retained output locations, private creation and exclusion from ordinary staging, including existing tracked legacy logs. Environment filtering does not prevent trusted code from reading the account's files or network.
7. **CSH-007: scalar grammar and publication.** Define accepted model values for every generated runtime format. Valid strings must decode to exactly the original value; quoting characters may be escaped rather than arbitrarily rejected. Invalid values must be detected before any runtime output changes, including earlier Cursor projections in the sync command.
8. **CSH-008: effective listener.** Bind the default explicitly to a loopback address. Specify precedence for an intentional non-loopback option versus inherited user/global Streamlit settings, so an ambient configuration does not silently defeat the default.

## Missing failure cases

These cases belong in Stage 05 test design. They are counterexamples to incomplete implementations, not claims of reproduced exploits.

| Criterion | Concrete counterexample and required observation |
| --- | --- |
| CSH-001 | Completion and help encounter an executable project dispatcher that writes a marker. No marker appears before trust. Trust one kit, change a helper without changing `ask`, then invoke a daily command: delegation is refused. Noninteractive refusal and completion opt-in leave shell startup files unchanged. |
| CSH-002 | A late destination is a symlink outside the repo or an unknown owned-looking file. Earlier outputs remain byte-identical and the outside sentinel is untouched, with and without force. Fresh install, reinstall, upgrade and standalone sync each exercise their write boundaries. |
| CSH-003 | Inject failure after an early write and termination before final publication. Restore previous files, remove newly created kit files, preserve client settings and modes, restart recovery twice, and successfully retry. A recovery error retains the backup and identifies the unresolved path. |
| CSH-004 | Migrate a synthetic value containing shell substitution syntax: it remains data and creates no marker. Reject HTTP and credential-bearing URLs without printing values. A staged legacy secret still produces rotation guidance. Denied MCP opt-in leaves user configuration unchanged. Private-file creation and replacement remain private under a permissive umask. |
| CSH-005 | Fetch a local source that resolves differently from the requested immutable revision: no fetched executable marker runs. A changed project source/revision gets no fetch before approval. A mandatory skill installer failure makes prepare and its install/upgrade callers fail. |
| CSH-006 | Export dummy secrets and inherited Python/shell startup controls, then run static CheckPlan and instrumented checks. Observe only the approved environment, retained runner metadata, explicit extras and private logs. Existing valid case collection and result recording continue to work. |
| CSH-007 | Supply quotes, backslashes, newline/control input and mapping-like content through supported overrides. Valid values decode as one exact scalar; invalid values leave all generated runtime outputs unchanged. |
| CSH-008 | Start with default arguments in a disposable configuration environment and inspect the actual listener. Repeat with an explicit non-loopback override. Verify generated argv alone only as a lower-level check. |

Source grounds for this coverage include `askit` (delegation and automatic completion installation), `_ask/scripts/install-kit.sh` (writes before sync and swallowed prepare failures), `_ask/scripts/upgrade-kit.sh` (tree replacement and preservation), `_ask/scripts/setup.sh` (legacy `.ask.env` and MCP settings), `_ask/skills/prepare-skills.sh` (manifest-driven installer execution), `.agents/ask/verification/run.py` and `traceability/adapters.py` (separate inherited environments), `_ask/scripts/sync-cursor-binding.sh` and `sync-runtime-agents.py` (multiple publications), and `_ask/scripts/ui.sh` (Streamlit launch). These were read as source; no exploit, dependency scan or behavior test was run.

## Over-constraint risks

- Preserve the approved trusted-local threat model. Git worktrees and environment allowlists provide no sandbox, and host compromise or malicious already-trusted project code is outside the promise.
- Use safe serialization for valid model strings; a restrictive model-name catalog would unnecessarily remove existing compatible overrides.
- Transaction recovery covers kit filesystem changes and generated outputs. It does not promise to undo arbitrary third-party network side effects or rewrite user Git history.
- Pins and source approvals need explicit supported update paths. Do not make harmless public setting edits invalidate unrelated trust when executable content is unchanged.

## Under-constraint risks

The largest risks are checking only the dispatcher, checking only the first write, trusting a rollback trap to survive process termination, migrating secrets by sourcing their old file, filtering only one verifier path, and validating only the final generated runtime file. Each can look successful in a happy-path test while violating an existing criterion. The plan must make these cases explicit.

Fresh installation must also explain the initial trusted launcher acquisition. A later revision comparison cannot retrospectively authenticate a launcher the user already executed. Keep that trust boundary explicit in the supported installation instructions; do not describe mutable `curl | bash` instructions as verified delivery.

## Recommended clarifications

Record the choices above in Plan and Stage 04's disposition without changing intent or weakening any criterion. Route an actual change to trust policy, preservation guarantees, compatible CLI behavior, or a requested review-only exemption through Spec Change.

Minimum required test types for the future `test-plan.json`:

| Criterion | Required types | Purpose |
| --- | --- | --- |
| CSH-001 | unit, integration, e2e | Identity comparison, dispatcher refusal, installed launcher journey. |
| CSH-002 | unit, integration, e2e | Path/ownership classification, complete preflight, client install/upgrade preservation. |
| CSH-003 | integration, e2e | Injected failure and restart across real filesystem operations. |
| CSH-004 | unit, integration, e2e | Data/URL parsing, permissions and migration, setup/MCP journey with dummy credentials. |
| CSH-005 | unit, integration, e2e | Selection/approval rules, fetched-code refusal, distribution/prepare journey using local stand-ins. |
| CSH-006 | unit, integration, e2e | Environment construction, both runners and private output, actual trusted verify CLI journey. |
| CSH-007 | unit, integration | Format round-trip/rejection and atomic behavior across the sync pipeline. |
| CSH-008 | unit, integration | Argument precedence and observed loopback listener. |

Use disposable Git repositories and disposable user config/cache directories. Keep each unittest case explicitly identifiable for the frozen traceability runner; shell journeys can be invoked and asserted by those cases. Preserve passing legacy guards as Green regressions. A preservation defect needs a demonstrated failing reproduction and separate repair scope before overlapping installer changes.

No criterion needs review-only authority. Documentation assertions can be checked alongside behavioral cases. No historical red, test results or accepted test-plan authority is inferred from this challenge. The eventual test plan and TaskGraph need a separate independent decision bound to their exact canonical digests before coordinator acceptance. A specification-only challenge cannot approve a plan that does not yet exist.

## Challenge verdict

**PASS** for specification revision 1 at the exact digests above. The criteria are observable, align with the approved Why and admit an implementation without changing scope. The planning details and counterexamples above must be carried into Stage 05 and checked by independent plan review. No human scope decision is required by this challenge.

This verdict authorizes progression through Spec Change disposition and planning only. The recorded human endpoint remains: finish the implementation plan, then stop before implementation, merge or publication.
