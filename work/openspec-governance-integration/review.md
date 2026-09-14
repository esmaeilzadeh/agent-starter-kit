# Review

## Model

- model: grok-4.6
- runtime: cursor
- parent_model: grok-4.6

Human confirmed grok-4.6 after the same-family warning (Implement was also grok-4.6). Kit HIGH/diverse default `kimi-k3` was not spawnable in this session.

## Scope

Independent inspect of `openspec-governance-integration` on `agent/openspec-governance-integration` against:

- Canonical change: `openspec/changes/openspec-governance-integration/`
- Intent / challenge / change under `work/openspec-governance-integration/`
- Kit policies and the scripts/tests listed in the 07 prompt
- `git log main..HEAD` commits: plan, baseline, pin/helper, cutover, gates, status, verify, openspec-archive, OWNED-PATHS/ADR

Child reviewer could not run git in Ask mode; parent confirmed a clean tree after those commits. Tests were read by the child; parent had run the new stub tests during Implement.

This review is not Accept.

## Findings

Load-bearing machinery matches the OpenSpec requirements and Spec Change decisions. Non-pilot smoke still has no OpenSpec dependency. No generated OpenSpec commands under `.cursor/commands/`. `install-kit.sh` does not require Node or OpenSpec.

### should-fix: `verify` does not detect openspec-archive without Accept SHA

**Location:** `_ask/scripts/verify.sh` (pilot branch); `_ask/spec/04-scripts-and-git.md` §24.1.

**Evidence:** Spec requires kit `status`, `verify`, and `check-workstream` to detect an openspec-archived change with no Accept SHA and fail. `check-workstream.sh` calls `preflight`. `status.sh` has `archived_without_accept()`. `verify.sh` only runs `validate` for a marked pilot. `_ask/tests/test-verify-work-id.sh` has no archive case.

### should-fix: `status` archive-without-accept is a warning on other live refs

**Location:** `_ask/scripts/status.sh` rows loop.

**Evidence:** Spec says kit status must fail. On `HEAD == agent/<id>`, status exits 1. On other live refs it appends `openspec-archive-without-accept` and exits 0. No test covers that path.

### should-fix: upgrade does not refresh the kit-owned pin

**Location:** `_ask/scripts/upgrade-kit.sh` refresh list; `_ask/OWNED-PATHS.md` lists `_ask/openspec-pin.yaml` as kit-owned.

**Evidence:** `install-kit.sh` rsyncs `_ask/`. `upgrade-kit.sh` copies named `_ask/` subtrees, not `_ask/openspec-pin.yaml`. A consumer upgrade gets the helper and no pin.

### should-fix: 04 contract omits post-archive recreate

**Location:** `_ask/agents/04-spec-change.md`; spec requirement `openspec-archive` last paragraph.

**Evidence:** Spec: `04 Spec Change` on an already openspec-archived work-id shall create a new active `openspec/changes/<id>/` and record it in intent. Helper `lookup_change` prefers active over archives. The stage contract was not updated. `01-grill.md` and `_ask/templates/intent.md` never mention `Engine: openspec`.

### should-fix: layout SoT still treats only `specs/` + `work/` as engineering state

**Location:** `_ask/spec/01-layout-and-concepts.md`; `.cursor/rules/workstream-scope.mdc`.

**Evidence:** `_ask/OWNED-PATHS.md` and ADR-0018 list `openspec/` with `specs/` and `work/`. The layout diagram has no root `openspec/`. The workstream-scope rule does not glob `openspec/**`.

### nit (withdrawn): cutover gitkeeps

Child reported missing `openspec/specs/.gitkeep` and `openspec/changes/archive/.gitkeep`. Those files are tracked on this branch. Withdrawn.

### nit: coverage holes on archive lookup through kit CLIs

`cmd_preflight` implements archive lookup. Tests hit it via `test-openspec-archive.sh`, not via `check-workstream.sh` or `verify.sh`.

### nit: `verify` without `--work-id` skips OpenSpec on a marked pilot

Pilot validation is gated on `--work-id`. Plan kept the unscoped invocation for callers. Optional to infer id from `agent/<id>`.

## Suggested fixes

1. In `verify.sh`, for a marked pilot call `preflight` before `validate`. Treat archive-without-Accept as fail. If `run_gate` is false (valid Accept + archive), skip active validate.
2. Make `status` fail (exit 1) on openspec-archive without Accept for any listed live row, matching MUST fail. Add a test.
3. Add `_ask/openspec-pin.yaml` to `upgrade-kit.sh` kit-owned copy list.
4. Document post-archive 04 recreate on `_ask/agents/04-spec-change.md`. Document optional `Engine: openspec` on the intent template / 01-grill.
5. Put `openspec/` on the layout diagram. Add `openspec/**` to workstream-scope globs.
6. Optional: if HEAD is a marked pilot, `./ask verify` without `--work-id` infers the id.

## Residual risks

- Pin assert is exact `openspec --version` == `1.13.0`.
- Schema/profile are recorded in the pin, not asserted against global `openspec config`.
- Marked-pilot gates fail closed without the pinned binary. Specified.
- `openspec/specs/` stays empty until apply/archive.
- Later evaluation pilots must serialize; parked later card states that; nothing enforces it in code.
- 09 Verify still has to run `./ask verify --work-id openspec-governance-integration` on a clean tree with the pinned CLI.

## Review verdict

**ACCEPT WITH RATIONALE**

The named Spec Change machinery is present and tested on the happy path (marker, targeted validate/status, non-pilot unchanged, pointers, checkout-scoped CLI, stage/`code-without-plan`, dirty `verify --work-id`, kit-mediated archive refuse, pin fail-closed, OWNED-PATHS/ADR-0018, baseline + parked evaluation). Remaining issues are archive-adjacent detection in `verify`/`status`, upgrade packaging of the pin, and stage/layout docs. They should be fixed in 08; they do not make Accept-on-machinery false. No What/Why conflict.
