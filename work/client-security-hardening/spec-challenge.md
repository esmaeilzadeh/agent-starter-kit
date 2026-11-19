# Specification Challenge: client-security-hardening

## Model

- Reviewer: independent Spec Challenge child, `gpt-6-astra`.
- Runtime: `codex`; parent_model: `GPT-6` (exact parent runtime variant unavailable).
- Submitted selection: “continue with astra for review”. This follows the explanation that Astra is the configured adversarial reviewer and that all available runtime models share the `gpt` family. The selection authorizes this independent context; no additional picker is needed.
- Binding: `03-spec-challenge → adversarial → gpt-6-astra`; the human selection controls the reviewer.
- Frozen contract: `88035127763fb1436775c13c941fbcba7484d581`, `/tmp/askit-security.e0Qyvz/frozen`. Its HEAD was checked and matched.
- Writing guidance: prepared product `.agents/skills/writing-for-agents/SKILL.md`, embedded mode. Frozen preparation was interrupted; this review does not claim it completed.

## Specification

Reviewed the approved combined intent, `spec-change-model-flow.md`, Markdown specification and canonical JSON registry, revision 2. This is the approved feature extension: CSH-009 through CSH-012 add model decisions and implementation-orchestrator handoff. Existing client-file preservation remains a separately reproduced repair, with shared installer changes serialized.

Compared CSH-001 through CSH-008 with the revision-1 registry at recovered source `853f37d310bf7dc9af50552d761ec5d97f3d5135`: the eight criterion objects are unchanged. The approved intent is byte-identical to the presented `intent-model-flow.proposed.md`; `intent-confirmation.json` binds those bytes and records the submitted response “approved”. The draft heading and its historical “pending” sentence remain in those approved bytes; the separate confirmation and approved change record establish current authorization. Preserve the original review at `spec-challenge-security-v1.md`.

Exact bindings:

| Contract | SHA-256 |
| --- | --- |
| Canonical sorted compact JSON specification | `664778e240718fadd15f40f9bd23a10d2664b8d3d7d1fc3942426dfc4ad5e8cc` |
| Markdown specification bytes | `f091c0bc398c77ae9e24d82223586011595396d93e077028d4d4a97dc79a60dc` |
| Approved intent bytes | `38106bb1ca9437cc0da5044e0fb5f0c7a5bf4e2835d743f7873fa1b2c5147115` |

All twelve criteria use `verification_mode: tests`. Markdown and JSON describe the same obligations. The changes address the stated Why: protecting client files, credentials and repository trust, preserving a usable upgrade path, and continuing to the authorized endpoint without repeated routine model decisions.

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
9. **CSH-009: one complete interaction.** Present resolved stage identities, exception provenance, same-family review information and the implementation update policy together. A complete replacement map submitted with Change settles the model decision; missing exceptions may be collected together, without restarting confirmation for every stage. Record defaults separately from exact human overrides so resolving a current default does not accidentally freeze the latest-accessible policy.
10. **CSH-010: continuation and authority.** Reuse prior submitted choices and configured defaults without manufacturing a historical confirmation. An older workstream without a confirmed latest-accessible policy keeps its prior configured behavior until the next authorized Grill or explicit model-policy change; absence of the new record alone is not a stage gate. Model confirmation never changes the intent approval, review independence, final acceptance or the recorded stop. Define resume behavior from a pending manual handoff so it requests only the unresolved action.
11. **CSH-011: actual orchestration.** Define the capability observation, catalog freshness and runtime-specific ordering used to identify the latest accessible implementor in the selected family. A static list or lexicographic slug sort cannot establish account access or release order. Exact overrides stay exact even when a newer accessible default exists. Store switch request and observed result distinctly; a worker spawn, configuration write or switch API success without identity verification cannot authorize implementation writes. Where identity is uninspectable, record the explicitly permitted human acknowledgment as such, without calling it observed verification. Check authorization before discovery/switch preflight so plan-only work never asks for a switch.
12. **CSH-012: portable authority and capability boundaries.** Extend the existing workstream model overlay and canonical runtime bindings, with explicit unknown/unsupported states. Inventory all generated projections and alternate command paths so a stale prompt cannot restore repeated questions. Keep runtime capability evidence separate from fake-catalog contract tests. Implementation must inspect actual supported runtime interfaces and record unavailable capabilities honestly; this review does not claim current automatic switching support.

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
| CSH-009 | Confirm defaults once, then separately submit a complete map changing only one stage. Observe one resolved decision, unchanged other defaults, preserved free text and no per-stage question loop. Same-family information is included in that interaction and independent review still uses a child context. |
| CSH-010 | Resume an old workstream with an explicit Astra choice and no new decision record. Preserve Astra and its stop without a new picker or fabricated confirmation. Resume a confirmed workstream through Challenge and Review: no routine prompts, while a genuine escalation and final acceptance remain required. |
| CSH-011 | A child runs Luna while the parent remains another model: implementation stays blocked. Cover already-matching parent, verified automatic switch, switch failure/mismatched result, unsupported switch, uninspectable identity with explicit acknowledgment, missing catalog and unavailable exact override. In every unresolved case, an implementation-write sentinel stays absent. A plan-only endpoint calls neither discovery nor switch. |
| CSH-012 | Fake runtime catalogs contain reordered versions, an inaccessible newest version and a newer model in another family. Resolve only the latest accessible selected-family model under the confirmed policy; retain an exact override. Unknown capability stays unknown. Regenerate all supported runtime projections and inspect both canonical and generated model-decision instructions. |

Source grounds for this coverage include `askit` (delegation and automatic completion installation), `_ask/scripts/install-kit.sh` (writes before sync and swallowed prepare failures), `_ask/scripts/upgrade-kit.sh` (tree replacement and preservation), `_ask/scripts/setup.sh` (legacy `.ask.env` and MCP settings), `_ask/skills/prepare-skills.sh` (manifest-driven installer execution), `.agents/ask/verification/run.py` and `traceability/adapters.py` (separate inherited environments), `_ask/scripts/sync-cursor-binding.sh` and `sync-runtime-agents.py` (multiple publications), and `_ask/scripts/ui.sh` (Streamlit launch). These were read as source; no exploit, dependency scan or behavior test was run.

Additional source grounds: `.agents/ask/stages/03-spec-challenge.md` and `07-review.md` each require a picker and same-family confirmation; `01-grill.md` defines the existing human decision flow; runtime YAML files contain static roles/pickers but no demonstrated live switch capability. `.agents/ask/bindings/README.md` documents workstream overrides before environment values, while `sync-runtime-agents.py:resolve_slug` checks concrete environment slugs first. The plan must include a focused reproduction of this discrepancy and reconcile the shared resolver with the documented precedence and new exact-choice guarantee. Do not add a competing resolver or silently let ambient environment values replace a confirmed human override.

## Over-constraint risks

- Preserve the approved trusted-local threat model. Git worktrees and environment allowlists provide no sandbox, and host compromise or malicious already-trusted project code is outside the promise.
- Use safe serialization for valid model strings; a restrictive model-name catalog would unnecessarily remove existing compatible overrides.
- Transaction recovery covers kit filesystem changes and generated outputs. It does not promise to undo arbitrary third-party network side effects or rewrite user Git history.
- Pins and source approvals need explicit supported update paths. Do not make harmless public setting edits invalidate unrelated trust when executable content is unchanged.
- One model question does not collapse intent approval or unrelated load-bearing Grill questions. The approved simplification concerns model selection only.
- Unknown runtime capability must not become an invented automatic-switch feature. The approved manual handoff and explicit acknowledgment fallback provide a bounded path where interfaces are absent.

## Under-constraint risks

The largest risks are checking only the dispatcher, checking only the first write, trusting a rollback trap to survive process termination, migrating secrets by sourcing their old file, filtering only one verifier path, and validating only the final generated runtime file. Each can look successful in a happy-path test while violating an existing criterion. The plan must make these cases explicit.

Fresh installation must also explain the initial trusted launcher acquisition. A later revision comparison cannot retrospectively authenticate a launcher the user already executed. Keep that trust boundary explicit in the supported installation instructions; do not describe mutable `curl | bash` instructions as verified delivery.

For model flow, the main risks are mistaking a displayed default for submitted consent, promoting every resolved default into an exact override, selecting a model solely from stale picker data, treating a child identity as the parent, and entering implementation preflight before checking the authorized endpoint. The required cases above distinguish each failure.

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
| CSH-009 | unit, integration, e2e | Decision/override persistence, canonical/generated interaction contract, one-question default and exception journeys. |
| CSH-010 | unit, integration, e2e | Resume rules, old-workstream compatibility, uninterrupted stages with preserved real gates and endpoint. |
| CSH-011 | unit, integration, e2e | Selection and handoff state, real parent versus child evidence, write-blocking automatic/manual journeys with fake runtime adapters. |
| CSH-012 | unit, integration | Runtime ordering/capability semantics, override precedence and complete projection generation. |

Use disposable Git repositories and disposable user config/cache directories. Keep each unittest case explicitly identifiable for the frozen traceability runner; shell journeys can be invoked and asserted by those cases. Preserve passing legacy guards as Green regressions. A preservation defect needs a demonstrated failing reproduction and separate repair scope before overlapping installer changes.

No criterion needs review-only authority. Documentation assertions can be checked alongside behavioral cases. No historical red, test results or accepted test-plan authority is inferred from this challenge. The eventual test plan and TaskGraph need a separate independent decision bound to their exact canonical digests before coordinator acceptance. A specification-only challenge cannot approve a plan that does not yet exist.

## Challenge verdict

**PASS** for combined specification revision 2 at the exact digests above. The original eight security criteria remain unchanged; the four new model-flow criteria match the explicitly approved extension. The criteria are observable, align with the approved Why and admit an implementation without changing scope. The planning details and counterexamples above must be carried into Stage 05 and checked by independent plan review. No additional human scope or reviewer-selection decision is required by this challenge.

This verdict authorizes progression through Spec Change disposition and planning only. The recorded human endpoint remains: finish the implementation plan, then stop before implementation, merge or publication.
