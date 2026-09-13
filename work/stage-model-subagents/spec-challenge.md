# Specification Challenge

## Specification

`specs/proposals/stage-model-subagents.md`

## Ambiguities

- **Same family** is undefined. Composer Review after Composer Implement is the correlated case. Grok Review after Composer Implement is the cheap diversity default. Treating all Cursor Models as one family would warn on the cheap path we wanted.
- **Parent model** is not exposed by Cursor, Claude Code, or Codex as a file the kit can read. Optional spawn (“when ≠ parent”) cannot be decided by a script if parent id is unknown.
- **Available models** have no stable repo API. A picker that scrapes the live Cursor dropdown will rot. A shipped list will go stale when Cursor adds slugs.
- **Risk** for Review defaults has no required field today. If unset, LOW vs MEDIUM changes the default.

## Missing failure cases

- Overlay and env name a slug the runtime does not have. Sync can still write it; spawn fails at the vendor.
- Two workstreams with different `models.yaml` on one checkout: resolution must use the active `work-id`, not a merge of all `work/*/models.yaml`.

## Over-constraint risks

- Requiring a live model catalog blocks the work on a vendor API the kit does not own.

## Under-constraint risks

- Optional Grill/Plan child with no “return into parent” acceptance check: agents will finish Grill inside the child and skip HITL.
- `check-workstream` as warn-only for missing `model:` will be ignored the same way fake verify was, unless the contract text is blunt.

## Recommended clarifications

- Family = slug prefix: `composer`, `grok`, `claude`, `gpt`, `gemini`, `muse` (and later prefixes in the defaults file). Same prefix → same-family warn. Composer vs Grok is different family.
- If parent model is unknown, required spawn still runs; optional spawn runs only when the stage pin is an explicit override (work/env/consumer map), not when it merely differs from an unknown parent.
- Picker list = `_ask/bindings/runtimes/<runtime>.models.yaml` shipped with the kit, refreshed when we bump defaults. Human may type a slug not on the list (warn: unlisted).
- Risk defaults to LOW when the workstream does not set `risk:` in intent or `models.yaml`.
- `01` / `05` contracts: child output is material for the parent; the parent asks the human and writes `intent.md` / `plan.md`.

## Challenge verdict

PASS after the clarifications above are written into the spec.
