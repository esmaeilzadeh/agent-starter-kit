# Intent: confirm before adding ask to a repo

## What

`askit` only lists kit commands after the current folder is an ask-based git repo (`_ask/` and `./ask`).

- Non-git folder: refuse. Ask is not applicable. Do not overlay. Do not print the command catalog.
- Git repo that is not ask-based: ask whether to add ask capability. Overlay only after yes. Do not overlay silently. Do not print the command catalog before that confirm.
- Ask-based repo: `askit` is `./ask` (commands and flags).

Adding the kit is one `askit` confirm, not a separate `askit setup` first step. `askit setup` stays the tracker/MCP wizard on a repo that already has the kit.

Explore skipped: destination already clear.

## Why

Running `askit` in an ordinary git repo dumped kit subcommands and could overlay without asking. That is the wrong default for an irrelevant product repo.

## Non-goals

- Renaming `./ask`
- Changing overlay rules for `docs/`, `scripts/`, `tests/`, `src/`
- Auto-running setup after confirm

## Source

Human correction after `askit-global-cli` shipped.
