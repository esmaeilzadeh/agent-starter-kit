# Specification: install pinned OpenSpec CLI during kit setup

## Status

CURRENT

## Goal

Human-only `./ask setup` ensures `$HOME/.local/bin/openspec --version` equals
the `revision` in `_ask/openspec-pin.yaml`, without requiring Node to finish
tracker and MCP setup.

## Non-goals

`askit` overlay, `askit self-install`, and `./ask install` installing OpenSpec.
`./ask openspec` as a dispatcher command. Changing marked-pilot fail-closed
gates. `revision: latest`.

## Behavior

`./ask setup` on a TTY runs today's tracker, MCP, and issue-context stages, then
an OpenSpec CLI stage, then finish notes. `askit setup` execs that dispatcher
once the repo is ask-based. If `askit setup` first overlays the kit, OpenSpec
install happens in the subsequent `./ask setup`, not in overlay itself.

The OpenSpec stage invokes `_ask/scripts/ensure-openspec.sh` (no TTY required).
Helper exit 0 is success (already correct or install succeeded). Exit 1 is
skip/warn. Exit 2 is a bad pin. The wizard prints a warning on 1 or 2, naming
`package` and `revision` when those scalars exist, and continues remaining
setup. Those exits do not themselves make setup fail; setup exits zero when
the other stages complete successfully.

The helper reads `package` and `revision` from `_ask/openspec-pin.yaml`. Both
must be non-empty scalars. `revision` must not be `latest` (case-insensitive).
The helper never passes `@latest` to npm. Missing pin file or invalid pin is
exit 2.

`node` and `npm` count as present only when `command -v` finds them.

Version identity is trimmed stdout of exactly `$HOME/.local/bin/openspec
--version` (not PATH lookup). Surrounding whitespace is stripped. That command
must exit 0. If the trimmed stdout already equals the pin revision, the helper
exits 0 and does not run npm.

Otherwise, if `node` and `npm` are present, the helper may replace a
conflicting `$HOME/.local/bin/openspec` (file or symlink) and then installs
with prefix `$HOME/.local` only:

```text
npm install -g --prefix "$HOME/.local" "<package>@<revision>"
```

`--force` is allowed. No other prefix is written. A portable 120-second timer
kills and reaps npm and its descendants; GNU `timeout` is not required. After
a successful install, the same fixed-path version check must equal the pin
revision (helper exit 0).

When `node` or `npm` is missing, `$HOME/.local` is unwritable, npm exits
non-zero, the timer fires, the binary is missing or not executable, or the
version check fails or mismatches, the helper exits 1.

Non-TTY `./ask setup` still refuses before any stage (existing human-only
gate) and does not invoke the helper. `--help` states that setup installs the
pinned OpenSpec CLI under `~/.local` and skips that install when Node/npm is
missing.

`./ask install`, `askit` confirm-to-add overlay, and `askit self-install` do
not install OpenSpec.

## Interfaces

- Command: `./ask setup` / `askit setup` (TTY wizard)
- Helper: `_ask/scripts/ensure-openspec.sh` (0 success, 1 skip/warn, 2 bad pin)
- Pin: `_ask/openspec-pin.yaml` (`package`, `revision`)
- Binary path: `$HOME/.local/bin/openspec`

## Constraints

Install prefix is `$HOME/.local`, not the current npm global prefix. Agents must
not run `./ask setup`.

## Invariants

Marked-pilot gates keep failing closed when the binary is missing or the
version mismatches. Setup warn-and-continue does not count as a passing gate.

## Failure cases

- Pin missing, empty `package`/`revision`, or `revision: latest` → helper 2;
  wizard warns and continues
- No `node` or no `npm` (`command -v`) → helper 1, no npm
- Unwritable `$HOME/.local`, conflicting binary that cannot be replaced, npm
  non-zero, 120s kill, missing/non-executable binary, version on stderr-only or
  mismatch → helper 1
- Non-TTY setup → refuse, no helper, no `.ask.env` write (existing)

## Acceptance criteria

- TTY setup with Node/npm and a mismatch or missing `$HOME/.local/bin/openspec`
  installs `<package>@<revision>` to `$HOME/.local`; then that exact path's
  `--version` trimmed stdout equals `revision`.
- TTY setup with no Node/npm prints a warning naming the pin and still runs
  tracker/MCP/issue-context; OpenSpec skip does not force a non-zero setup
  exit.
- Already-correct `$HOME/.local/bin/openspec` skips npm.
- A conflicting file or symlink at `$HOME/.local/bin/openspec` is replaced so
  the pin version wins, or the helper exits 1.
- Non-TTY `./ask setup` still refuses and does not invoke npm or the helper.
- `./ask setup --help` mentions the pinned OpenSpec install and the skip.
- `askit` overlay / `./ask install` / `askit self-install` do not install
  OpenSpec.
- `_ask/scripts/setup.sh` invokes `_ask/scripts/ensure-openspec.sh`.
- Automated tests cover the helper: missing pin/`latest`/empty fields, missing
  npm, already-correct version, stub npm install, mismatch after install,
  unwritable prefix, conflicting binary, timeout kill.

## Open questions

None.

## Source intent

`work/kit-setup-openspec-cli/intent.md`

Spec change: `work/kit-setup-openspec-cli/spec-change.md`
