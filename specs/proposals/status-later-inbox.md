# Specification: status lists later inbox

## Status

CURRENT

## Goal

`./ask status` shows parked `.later/` cards as a second inventory, with `--later-only` and `--work-only` to print one inventory. Tab completion offers those flags.

## Non-goals

- A later-inbox subcommand (`./ask later` or similar)
- Issue-tracker sync for cards
- Live workstream fields on later rows (stage, branch, tip, warnings, artifacts)
- `--later-id`
- `--work-id` matching a later slug
- Committing cards; `.later/*` gitignore (except `README.md`) stays
- Changing how live/archived workstreams are inferred from git refs

## Behavior

Workstream rows stay as today: live = unmerged local `refs/heads/agent/<work-id>`; archive = `work/<work-id>/` on the default branch with no unmerged `agent/<work-id>`. That inventory still does not check out other branches.

Later rows come from the current checkout only.

### Later scan

Read `.later/*.md` in the repo root working tree. Skip `README.md`. Ignore non-`.md` files and subdirectories. Missing `.later/` is an empty inbox.

For each remaining file, in filename sort order:

| Field | Source |
| --- | --- |
| `slug` | basename without `.md` |
| `title` | first Markdown ATX heading (`# `) in the file, trimmed; empty string if none |
| `path` | `.later/<filename>` |

A card whose slug matches a live or archived work-id still appears. Later rows have no stage, branch, tip, warnings, or artifacts.

### Default (no inventory flags)

Print the workstream table first (today's columns). If the later scan is non-empty, print a blank line, then a later block:

```text
later:
SLUG                         TITLE
<slug>                       <title>
```

If the later scan is empty, print nothing extra: the workstream table (or the existing "no workstreams" message) is the whole output.

`--work-id <id>` filters workstreams as today and omits the later block.

### `--work-only`

Print workstreams only. Same as today's output, including `--work-id` and the empty-workstream messages.

### `--later-only`

Print the later block only (header `later:` plus the slug/title table). If the scan is empty, print this line on stdout:

```text
status: no later cards in .later/
```

and exit 0. Do not print the workstream table.

`--later-only` with `--work-id` is invalid (see Failure cases).

### `--json`

Top-level object always has:

- `default_branch` (string, as today)
- `workstreams` (array of today's workstream objects, unchanged fields)
- `later` (array of `{ "slug", "title", "path" }`)

`--work-only` (and `--work-id` without `--later-only`): `later` is `[]`.
`--later-only`: `workstreams` is `[]`; `later` is the scan (possibly `[]`).
Combined default: both arrays filled; `later` may be `[]`.

Empty later under `--later-only --json` still exits 0 and prints the object (`later: []`). The human one-line empty message is for non-JSON `--later-only` only.

### Flags together

| Combination | Result |
| --- | --- |
| `--later-only` and `--work-only` | exit 2, unknown-arg style message naming both flags |
| `--later-only` and `--work-id` | exit 2, message that `--work-id` does not apply to later |
| `--work-only` and `--work-id` | allowed |
| `--json` with `--later-only` or `--work-only` | allowed |
| unknown flag | exit 2, as today |

### Help and completion

`./ask` usage for `status`, and `status.sh -h`/`--help`, list `--work-id`, `--json`, `--later-only`, `--work-only`.

`ask-complete.sh` / `./ask --complete` offers `--later-only` and `--work-only` for `status` (and the `status` alias path). Already-used flags are omitted, same as today's flag completion. These flags take no value.

### Docs that must match this contract

Update these files so they describe the later block. Later cards stay not-live. No later-inbox subcommand. No tracker sync.

- `_ask/spec/04-scripts-and-git.md` §23.4 and §30.1
- `_ask/docs/adr/0015-later-inbox.md`
- `.later/README.md`
- `_ask/policies/workflow.md`
- `ask` dispatcher `status` help line

## Interfaces

```text
./ask status [--work-id <id>] [--json] [--later-only] [--work-only]
```

Implementation: `_ask/scripts/status.sh`. Completion: `_ask/scripts/ask-complete.sh`.

## Constraints

- Later scan is working-tree only (cards are gitignored).
- Workstream scan stays ref-based (no checkout).
- `--work-id` never selects a later slug.

## Invariants

- Later cards are not live workstreams.
- Default with an empty inbox matches today's human workstream output (modulo an additive JSON `later: []` key).
- `--work-only` human output matches today's human output.
- `--work-only --json` may add `"later": []` and must keep today's `workstreams` objects.

## Failure cases

- `--later-only` with `--work-only`: exit 2.
- `--later-only` with `--work-id`: exit 2.
- Unknown argument: exit 2 (today).
- Unreadable card file: still emit a row (`slug` from the filename, `title` empty). Do not abort the workstream table.
- Non-git repo: same as today (`status: not a git repository`, exit 2).

## Acceptance criteria

- `./ask status` in a repo with `.later/foo.md` (`# Title here`) prints a `later:` block whose row is slug `foo` and title `Title here`, after the workstream table.
- The same command with only `.later/README.md` present prints no `later:` block.
- `./ask status --work-only` with later cards present prints no `later:` block.
- `./ask status --later-only` prints the later block and no `LIFE`/`WORK-ID` workstream header.
- `./ask status --later-only` with no cards prints `status: no later cards in .later/` and exit 0.
- `./ask status --later-only --work-only` exits 2.
- `./ask status --later-only --work-id anything` exits 2.
- `./ask status --work-id <live-id>` omits later even when cards exist.
- `./ask status --json` includes `"later"` array; `--work-only --json` has `"later": []`; `--later-only --json` has `"workstreams": []`.
- Workstream JSON objects keep today's fields.
- `./ask --complete` for `status` lists `--later-only` and `--work-only`.
- `_ask/tests/test-status.sh` covers later listing, empty inbox, exclusive flags, `--work-id` omitting later, and JSON shapes.
- Build Spec §23.4 / §30.1, ADR 0015, and `.later/README.md` describe the later block instead of saying status ignores later.

## Open questions

None.

## Source intent

`work/status-later-inbox/intent.md`
