# Intent: install pinned OpenSpec CLI during kit setup

Risk: MEDIUM

## What

`./ask setup` (and therefore `askit setup`) installs the OpenSpec CLI pinned in
`_ask/openspec-pin.yaml` onto the human's machine at `$HOME/.local`, so
`openspec --version` matches the pin. Node is not a setup requirement: missing
Node/npm warns and the tracker/MCP stages still run. A missing or mismatched
binary is overwritten to the pin. `install-kit` and `askit` overlay/self-install
stay Node-free.

## Why

Marked-pilot gates fail closed without the pinned binary. Humans who run kit
setup should get that binary without a separate npm incantation, and without
blocking Python-only tracker setup.

## Non-goals

- Wrapping the OpenSpec CLI as `./ask openspec …`
- Installing OpenSpec during `askit` overlay, `askit self-install`, or
  `./ask install`
- Changing marked-pilot fail-closed gates
- `revision: latest` or following CLI `@latest` advice
- Making this workstream an OpenSpec marked pilot

## Known assumptions

- Explore skipped: destination already clear.
- Pin file remains the source of truth for package and revision (`1.13.0` today).
- Install prefix is `$HOME/.local` (`$HOME/.local/bin/openspec`).
- Agents still must not run `./ask setup`.
- Branch base is `agent/openspec-governance-integration`, not `main`.

## Open questions

None. Grill Q1–Q3 accepted as recommended (setup-only, warn-and-continue
without Node, overwrite pin under `~/.local`).

## Human decisions

- Q1-A: `./ask setup` / `askit setup` only.
- Q2-B: warn and continue when Node/npm is missing.
- Q3-A: install/overwrite exact pin under `~/.local`.
- Defaults OK / all recs 2026-09-14.
