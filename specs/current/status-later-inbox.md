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
- Recursing into `.later/` subdirectories

## Behavior

Workstream rows stay as today: live = unmerged local `refs/heads/agent/<work-id>`; archive = `work/<work-id>/` on the default branch with no unmerged `agent/<work-id>`. That inventory still does not check out other branches.

Later rows come from the current checkout only.

Git repository check runs before the later scan. Non-git: `status: not a git repository` on stderr, exit 2, including `--later-only` and `--json`.

### Later scan

If `.later` is missing, is a file, or cannot be listed, the scan is empty (do not abort the workstream table).

List immediate children of `.later/` (no recursion, skip names that start with `.`). Keep regular files whose basename ends in `.md` and is not exactly `README.md` (case-sensitive). Skip non-regular files (FIFO, device, directory).

Sort remaining names bytewise (UTF-8 bytes, `LC_ALL=C` order).

For each remaining file:

| Field | Source |
| --- | --- |
| `slug` | basename without `.md` |
| `title` | first line in the file that matches `^# ` at column 0; `title` is the rest of that line, trimmed; `""` if none. `##` / `###` do not count. Unreadable file: `title` `""`. Decode with UTF-8, replace errors; strip CR. |
| `path` | POSIX repo-relative `.later/<filename>` with `/` (including on Windows) |

A card whose slug matches a live or archived work-id still appears. Later rows have no stage, branch, tip, warnings, or artifacts.

### Default (no inventory flags)

Print the workstream table first (today’s columns) when there is at least one workstream row.

If the later scan is non-empty, print a blank line, then:

```text
later:
SLUG                         TITLE
<slug>                       <title>
```

Slug column width is 28 (same as `WORK-ID`). One output line per card. Do not truncate slug or title; the title may make the line longer than the header.

If the later scan is empty, print nothing extra.

If there are zero workstream rows and the later scan is non-empty: print today’s empty-workstream one-liner (`status: no live agent/* branches; no archived work/* on <branch>`, or `status: no workstream '<id>' …` when `--work-id` would have applied), then a blank line, then the later block. `--work-id` still omits later (Q1-B), so that case stays today’s missing-workstream one-liner only.

`--work-id <id>` filters workstreams as today and sets the later scan used for output to empty.

### `--work-only`

Print workstreams only. Same as today’s output, including `--work-id` and the empty-workstream messages.

### `--later-only`

Print the later block only: no `status: default=` line, no workstream empty one-liner, no `LIFE` / `WORK-ID` header.

If the scan is empty, print this line on stdout and exit 0:

```text
status: no later cards in .later/
```

`--later-only` with `--work-id` is invalid (see Failure cases).

### `--json`

Top-level object always has:

- `default_branch` (string, as today)
- `workstreams` (array of today’s workstream objects, unchanged fields)
- `later` (array of `{ "slug", "title", "path" }`)

`--work-only` or `--work-id` (without `--later-only`): `later` is `[]` even when cards exist on disk.
`--later-only`: `workstreams` is `[]`; `later` is the scan (possibly `[]`).
Combined default: both arrays filled; `later` may be `[]`.

Empty later under `--later-only --json` still exits 0 and prints the object (`later: []`). The human one-line empty message is for non-JSON `--later-only` only.

### Flags together

Check combinations after parse, order-independent. Messages on stderr, prefix `status:`, exit 2.

| Combination | Result |
| --- | --- |
| `--later-only` and `--work-only` | `status: --later-only and --work-only are mutually exclusive` |
| `--later-only` and `--work-id` (including `--work-id` with no value) | `status: --work-id does not apply to later` |
| `--work-only` and `--work-id` | allowed |
| `--json` with `--later-only` or `--work-only` | allowed |
| unknown flag | `status: unknown arg …` as today |

### Help and completion

`./ask` usage for `status`, and `status.sh -h`/`--help`, list `--work-id`, `--json`, `--later-only`, `--work-only`.

`ask-complete.sh` / `./ask --complete` offers `--later-only` and `--work-only` for `status`. Already-used flags are omitted. These flags take no value. Completion may still offer illegal combinations; runtime rejects them.

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
- `--work-only` human output matches today’s human output.
- `--work-only --json` and `--work-id --json` include `"later": []` and keep today’s `workstreams` objects.
- Default with an empty later scan matches today’s human workstream output.

## Failure cases

- `--later-only` with `--work-only`: exit 2 (message above).
- `--later-only` with `--work-id`: exit 2 (message above).
- Unknown argument: exit 2 (today).
- Unreadable card file: row with empty title; do not abort the workstream table.
- Unreadable `.later/` directory or `.later` is a file: empty later; do not abort the workstream table.
- Non-git repo: `status: not a git repository`, exit 2.

## Acceptance criteria

- `./ask status` in a repo with `.later/foo.md` (`# Title here`) prints a `later:` block whose row is slug `foo` and title `Title here`, after the workstream table.
- `.later/README.md` plus `.later/foo.md` → one later row `foo` (README skipped).
- Only `.later/README.md` → no `later:` block.
- Zero workstream rows and `.later/park.md` → today’s empty-workstream one-liner, blank line, then the later block.
- `./ask status --work-only` with later cards present prints no `later:` block.
- `./ask status --later-only` prints the later block and no `LIFE`/`WORK-ID` header and no `status: default=`.
- `./ask status --later-only` with no cards prints `status: no later cards in .later/` and exit 0.
- `./ask status --later-only --work-only` exits 2; stderr contains both flag names.
- `./ask status --later-only --work-id anything` exits 2; stderr contains `--work-id`.
- `./ask status --work-id <live-id>` omits later even when cards exist (human and JSON `later: []`).
- `./ask status --json` includes `"later"`; `--work-only --json` has `"later": []`; `--later-only --json` has `"workstreams": []`.
- A card whose slug matches a live work-id still appears in later (default / `--later-only`).
- Title: `#NoSpace` → empty title; first heading `## Why` then `# Real` → title `Real`; H1 on line 3 still used.
- Workstream JSON objects keep today’s fields.
- `./ask --complete` for `status` lists `--later-only` and `--work-only`.
- `_ask/tests/test-status.sh` covers the cases above that are machine-checkable in a temp git repo.
- Build Spec §23.4 / §30.1, ADR 0015, `.later/README.md`, `workflow.md`, and `ask` status help describe the later block.

## Open questions

None.

## Source intent

`work/status-later-inbox/intent.md`

## Spec change

`work/status-later-inbox/spec-change.md`
