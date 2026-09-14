# Specification: install pinned OpenSpec CLI during kit setup

## Status

PROPOSED

## Goal

Human-only `./ask setup` ensures `$HOME/.local/bin/openspec --version` equals
the `revision` in `_ask/openspec-pin.yaml`, without requiring Node to finish
tracker and MCP setup.

## Non-goals

`askit` overlay, `askit self-install`, and `./ask install` installing OpenSpec.
`./ask openspec` as a dispatcher command. Changing marked-pilot fail-closed
gates. `revision: latest`.

## Behavior

`./ask setup` on a TTY runs an OpenSpec CLI stage in addition to today's
tracker, MCP, and issue-context stages. `askit setup` is the same dispatcher.

The stage reads `package` and `revision` from `_ask/openspec-pin.yaml`. It
refuses to install when `revision` is `latest` (case-insensitive). It never
passes `@latest` to npm.

When `$HOME/.local/bin/openspec --version` already equals the pin revision, the
stage reports that and does not run npm.

Otherwise, if `node` and `npm` are both executable, it runs:

```text
npm install -g --prefix "$HOME/.local" "<package>@<revision>"
```

Then `$HOME/.local/bin/openspec --version` must equal the pin revision for the
stage to report success.

When `node` or `npm` is missing, npm exits non-zero, the install exceeds 120
seconds, or the version still mismatches after npm, the stage prints a warning
that names the pin (`package` and `revision`) and continues. Setup exit status
stays 0 for those skip/warn paths. Tracker and MCP stages still run.

Non-TTY `./ask setup` still refuses before this stage (existing human-only
gate). `--help` states that setup installs the pinned OpenSpec CLI under
`~/.local` and skips that install when Node/npm is missing.

`./ask install`, `askit` confirm-to-add overlay, and `askit self-install` do
not install OpenSpec.

## Interfaces

- Command: `./ask setup` / `askit setup` (TTY wizard)
- Pin: `_ask/openspec-pin.yaml` (`package`, `revision`)
- Binary path: `$HOME/.local/bin/openspec`
- Helper callable without a TTY for tests (setup wizard remains TTY-only)

## Constraints

Install prefix is `$HOME/.local`, not the current npm global prefix. Agents must
not run `./ask setup`.

## Invariants

Marked-pilot gates keep failing closed when the binary is missing or the
version mismatches. Setup warn-and-continue does not count as a passing gate.

## Failure cases

- Pin file missing or `revision: latest` → helper exits non-zero; wizard warns
  and continues
- No `node` or no `npm` → warn, no npm, continue
- npm non-zero, timeout, or post-install version mismatch → warn, continue
- Non-TTY setup → refuse, no install, no `.ask.env` write (existing)

## Acceptance criteria

- TTY setup with Node/npm and a mismatch or missing `~/.local/bin/openspec`
  installs `<package>@<revision>` to `$HOME/.local` and then
  `$HOME/.local/bin/openspec --version` equals `revision`.
- TTY setup with no Node/npm prints a warning naming the pin and still
  completes tracker/MCP stages (exit 0).
- Already-correct `~/.local/bin/openspec` skips npm.
- Non-TTY `./ask setup` still refuses and does not invoke npm.
- `./ask setup --help` mentions the pinned OpenSpec install and the skip.
- `askit` overlay / `./ask install` / `askit self-install` do not install
  OpenSpec.
- Automated tests cover the helper: missing pin/`latest`, missing npm, already
  correct version, npm install with a stub, mismatch after install.

## Open questions

None.

## Source intent

`work/kit-setup-openspec-cli/intent.md`
