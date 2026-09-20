# Review

## Model

- model: inherit (parent re-review; kit-07 Task spawn failed: usage limit)
- runtime: cursor
- parent_model: cursor-composer
- Same-family warning: same family as Implement/08; independence is spawn-separation only. Spawn unavailable this turn; evidence is test commands + file greps.

This re-review did not Implement F1–F7. Review commits nothing. Per-task `review.verdict` JSON remains PENDING.

## Scope

Re-review after 08 claimed F1–F7 FIX on `agent/inner-loop-hardening` (HEAD `67843e0`). Spec: `specs/current/inner-loop-hardening.md`. Plan: `work/inner-loop-hardening/plan.md`. Context audit: CE-01..CE-06 pass. Prior REJECTED review: `7edfdbc`.

Checked each FIX claim against code and re-ran: `_ask/tests/test-inner-loop.sh`, `test-verify-scaffold.sh`, `test-verify-fail-closed.sh`, `test-later-inbox-gitignore.sh`, `test-ask.sh`.

## Findings

None blocking. Prior F1–F7 verified closed:

| ID | Was | Now | Evidence |
| --- | --- | --- | --- |
| F1 | stubs | FIX | `driver.py` `run_until` / `resume_from_state` / `cancel`; `__main__.py` wires them; `test-inner-loop.sh` driver block PASS |
| F2 | no TDD gate | FIX | `check_integrable` refuses missing TDD and exemption without `reviewer_ack`; tests assert both |
| F3 | weak scaffold | FIX | `discover_workspaces`, `--wizard-preview`, `apply_with_rollback`; presets `typescript.yaml` / `python.yaml`; scaffold tests PASS |
| F4 | no isolation | FIX | `isolation.py` + `run.py` refuse `refuse_identifiers`; fail-closed test asserts leak |
| F5 | later gitignored | FIX | `.later/*.md` not ignored; ADR 0015 + git-flow; later-inbox test PASS |
| F6 | Accept no audit | FIX | `.agents/ask/stages/10-accept.md` refuses missing/open `context-audit.md` |
| F7 | help old SoT | FIX | `./ask --help` names `.agents/ask/` (`test-ask.sh`) |

## Suggested fixes

None for this re-review.

## Residual risks

- Per-task TaskResult `review.verdict: PENDING` (13 files); outer review folds that.
- Kit-07 required spawn failed (usage limit); this file is a parent re-review with command evidence.
- Later cards tracked on `agent/*` for check-clean; Git-flow still wants durable commit on `develop` + tracker issue.
- Wizard `--confirm` without `--preset` still needs a TTY; agents must not run it.
- `e2e: not_applicable` reason lives in the spec, not in `.agents/verification.yaml`.
- No `state.json` on this bootstrap workstream; driver exercised in fixtures only.

## Review verdict

APPROVED
