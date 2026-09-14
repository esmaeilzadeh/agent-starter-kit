# Specification Change Proposal

## Current specification

`specs/current/status-later-inbox.md` (as written after Grill)

## Proposed change

Fold Spec Challenge clarifications:

1. Human default with zero workstream rows and a non-empty later scan: print today’s `status: no live agent/* …` (or the `--work-id` missing line), then a blank line, then the later block. JSON: `workstreams: []` and populated `later`.
2. Title: first line matching `^# ` at column 0; rest of line trimmed; else `""`. `##` does not count.
3. README skip: basename equals `README.md` (case-sensitive).
4. Later table: one line per card; slug column width 28; titles may extend the line; do not truncate.
5. `path`: repo-relative POSIX `.later/<filename>` with `/`.
6. Sort: bytewise filename (`LC_ALL=C` / UTF-8 bytes).
7. JSON always includes `later`. `--work-only` and `--work-id` set `later` to `[]`.
8. Exclusive flags: after parse, order-independent, stderr, `status:` prefix, exit 2. `--later-only --work-id` with no value is the same invalid pair.
9. `--later-only` human: no `status: default=`, no workstream empty one-liner, no `LIFE` header.
10. Non-git check before later scan.
11. Unreadable `.later/` directory: empty later, do not abort workstreams. Non-regular `*.md`: skip. `.later` as a file: empty later.
12. AC covers README+card, `--json --work-id` → `later: []`, overlapping slug, exclusive flag substrings, completion flags, `workflow.md` and dispatcher help.

## Why the change is needed

Challenge found the empty-board composition unspecified and several parsers/tests under-constrained. Option 1 keeps today’s zero-workstream message and still shows parked cards (Why).

## Impacted artifacts

`specs/current/status-later-inbox.md`, `specs/proposals/status-later-inbox.md`, tests, `status.sh`.

## Impacted workstreams

`status-later-inbox` only.

## Migration / transition notes

Additive JSON `later` key. Human `--work-only` unchanged. Default human output grows a later block when cards exist.

## Acceptance criteria for the change

Same as the updated spec AC, including empty-workstream + later (one-liner then later block).

## Decision

Accepted to continue `status-later-inbox` after Challenge. Empty-board = option 1. kimi-k3 spawn is not this change (`.later/cursor-spawn-slugs.md`).
