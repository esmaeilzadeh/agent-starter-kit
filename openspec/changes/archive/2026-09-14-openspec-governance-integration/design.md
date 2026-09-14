## Context

Kit scripts today ignore OpenSpec. This work-id is the dogfood pilot
(`Engine: openspec` in intent). CURRENT kit spec and this design exist until
cutover; after cutover this directory is the spec/plan source of truth.

Challenge measurements were 1.12.0. Plan pins 1.13.0. Re-measured 2026-09-14:
`init --tools none --no-animation --profile core` writes only `openspec/`;
`validate <id> --strict --json` uses `items[].id` / `items[].valid`;
`status --change <id> --json` uses `isPlanningComplete`, `isComplete`,
`artifacts[].status` (`ready`|`blocked`|`done`); `isComplete` is true once
the four planning artifacts exist (task checkboxes do not gate it);
`config` remains global-only; schema `spec-driven`; profile `core`.

## Goals / Non-Goals

**Goals:**
- Fail-closed targeted OpenSpec gates for marked pilots.
- One specification and plan source of truth after cutover.
- Non-pilot scripts and `test-workstream-smoke.sh` unchanged in behavior.

**Non-Goals:**
- Replacing kit Review, project verification semantics, or Accept.
- Requiring Node in `install-kit.sh`.
- Custom OpenSpec schema.
- The later two-or-three-pilot evaluation.

## Decisions

- Pin `@fission-ai/openspec@1.13.0` in `_ask/openspec-pin.yaml`.
- Shared helper `_ask/scripts/openspec_cli.py`; tests stub `OPENSPEC_BIN`.
- Cutover is one commit: init, this change directory, pointer files.
- Enable pilot gates only after that commit.
- `./ask openspec-archive` is the kit-mediated archive path.

## Risks / Trade-offs

- Gate rewrite bugs fail non-pilots.
- Dual-spec window if pointers land after gates.
- Agents follow `@latest` advice; helper refuses that pin and mismatches.
