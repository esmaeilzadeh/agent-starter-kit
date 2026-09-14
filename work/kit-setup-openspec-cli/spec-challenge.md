# Specification Challenge

## Model

gpt-5.6-sol-medium / cursor / parent_model grok-4.6

Cursor adversarial default `kimi-k3` is not spawnable in this session. Challenge
used GPT-5.6 Sol (different family from Spec).

## Specification

`specs/current/kit-setup-openspec-cli.md`

The proposed behavior aligns with the intent: setup provides the pinned binary
needed by marked-pilot gates without making Node a prerequisite for tracker and
MCP configuration.

## Ambiguities

- “Setup exit status stays 0” is too broad. Existing tracker or MCP stages can
  fail independently. OpenSpec skip/failure paths must not themselves make an
  otherwise-successful setup fail.
- OpenSpec stage ordering is unspecified.
- “Executable” should mean discoverable through `command -v` and runnable.
- Pin validation is incomplete for missing or empty `package`/`revision`,
  malformed content, and version-command failure.
- The 120-second timeout does not say whether npm and its descendants are
  killed.
- Success output from `openspec --version` must be the revision after trimming
  surrounding whitespace.

## Missing failure cases

- `$HOME/.local/bin/openspec` exists as a regular file or symlink from another
  install (`npm` can fail with `EEXIST` instead of overwriting).
- `$HOME/.local` cannot be created or written.
- Installed binary exists but is not executable.
- `openspec --version` hangs, writes to stderr, or exits non-zero.
- npm succeeds but leaves no binary.
- Timeout facility unavailable.
- Setup interrupted during npm, leaving a partial prefix install.

Concrete counterexample: a user-created executable already exists at
`$HOME/.local/bin/openspec`. The specified npm command can fail with `EEXIST`.
That conflicts with overwrite-to-pin.

Concrete counterexample: Node is missing, MCP JSON is malformed. OpenSpec warns
correctly, then MCP setup fails. Unconditional “setup exit 0” would mis-blame
the OpenSpec stage.

## Over-constraint risks

- Mandating the exact npm argv without an overwrite mechanism conflicts with
  guaranteed overwrite.
- A strict 120-second bound needs a portable timer; GNU `timeout` is not
  standard on macOS.
- Warnings that echo pin text assume the committed pin is trusted.

## Under-constraint risks

- Helper path, arguments, and exit-status contract are unspecified.
- Version checks must use the fixed `$HOME/.local/bin/openspec` path, not PATH.
- Automated helper tests alone do not prove the TTY wizard invokes the helper.

## Recommended clarifications

1. OpenSpec skip/failure records a warning and returns control to setup; setup
   exits zero when remaining stages complete successfully.
2. All version checks invoke exactly `$HOME/.local/bin/openspec`.
3. `package` and `revision` must be non-empty scalars; `revision` must not be
   `latest` case-insensitively.
4. Permit an overwrite mechanism; only prefix `$HOME/.local`.
5. Timeout kills and reaps npm, then warns.
6. Tests cover wizard wiring, fixed-path validation, unwritable prefix,
   conflicting binary, and timeout.
7. `askit setup` may overlay then run `./ask setup`; overlay/self-install
   remain Node-free.

## Challenge verdict

PASS

Findings are technical clarifications. Grill Q1–Q3 already decide product
behavior. No additional human product decision is required before implement.
