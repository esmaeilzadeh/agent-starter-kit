# Intent: global `askit` command

## What

Ship a PATH command named `askit`. You run it **inside** any git repo.

- **No `./ask` in cwd (first run):** run setup, then install, so the kit lands in this directory. The human does not clone the kit into an empty folder and pass a path.
- **`./ask` already present (later runs):** `askit` is a wrapper for the whole local dispatcher: `askit …` means `./ask …`.
- **Help:** `./ask` and `askit` with no args, `-h`, `--help`, or `help` print commands plus each command’s options and parameters.
- **Autocomplete:** both commands complete subcommands. After any subcommand, Tab lists that command’s options (flags and short descriptions). `./ask completion bash` / `./ask completion zsh` (and the same on `askit`) print a snippet to eval.

Explore skipped: destination already clear.

## Why

`./ask install <other-repo>` requires a kit clone first. `ask` is too generic to install globally. People want one kit-specific command from inside the app repo: bootstrap once, then the same command as `./ask`.

## Non-goals

- Renaming the in-repo dispatcher (`./ask` stays).
- Making `ask` itself the global command.
- `askit` as a setup-only alias after install.
- Vendoring Community Skill bodies into the product repo.
- Changing overlay rules: still do not touch product `docs/`, `scripts/`, `tests/`, or `src/`.

## Known assumptions

- Q1: name is `askit`.
- First-run payload and the installer you curl come from this repo’s `main` (Q2-C). After overlay, later `askit` calls do **not** re-fetch; they exec local `./ask`.
- First run is human/TTY because setup is. Agents in a repo that already has the kit keep using `./ask`.
- Cwd must be a git repo (same refuse as install).
- Extra args on first run: finish setup → install, then if args remain, forward them to the new `./ask`.
- `humanize-ask-docs-and-specs` stays on its own branch; this job starts from current `main`.

## Open questions

None that block Intent. Say “defaults OK” if the assume-list is fine.

## Human decisions

- Q2-C: bootstrap from `main` (curl | bash style), not a pinned cache and not npm/pip.
- Q3 (replaced): `askit` wraps **all** of `./ask` once the kit exists. First run (no `./ask`): setup → install. Second run: same as `./ask`.
- Help: no-args / `-h` / `--help` / `help` on `./ask` and `askit` list commands and their flags.
- Autocomplete on both commands (bash and zsh).
