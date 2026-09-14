# Specification Challenge

## Model

- model: inherit (grok-4.6)
- runtime: cursor
- parent_model: grok-4.6
- kit_default: kimi-k3 (not spawnable in this parent Task session; parked as `.later/cursor-spawn-slugs.md`)
- human: continue with default models

## Specification

`specs/current/status-later-inbox.md`

## Ambiguities

Empty workstream inventory plus a non-empty later scan: today’s zero-row stdout is a one-liner, not a table, so “print the workstream table first, then later” does not compose. Title grammar (`# ` vs any ATX, line 1 vs first in file). README skip case. JSON `later` “always” vs “may”. Exclusive-flag I/O vs today’s one-token unknown-arg. Sort locale. `path` separators on Windows. Completion vs illegal flag pairs.

## Missing failure cases

Unreadable `.later/` directory. Non-regular `*.md` (FIFO hang). Decode failure. `.later` is a file. Dotfiles. Non-git `--later-only`. `--later-only --work-id` with no value.

## Over-constraint risks

JSON always adding `later`. No recursion into `.later/` subdirs. `--work-id` hiding later (Q1-B, closed). Golden-space snapshots of the later table.

## Under-constraint risks

Default empty-workstream + later. Title parser. Shallow tests that only grep `later:`. README plus cards. Long titles. CRLF. stderr vs stdout for exclusive flags.

## Recommended clarifications

See `work/status-later-inbox/spec-change.md`. Empty-board human stdout = today’s no-workstream one-liner, blank line, then the later block (challenge option 1). Title = first column-0 `# ` in the file. README skip is exact `README.md`. JSON always has `later`; `--work-id` / `--work-only` set it to `[]`. Exclusive flags checked after parse, stderr, exit 2.

## Challenge verdict

PASS after those clarifications are written into the spec (option 1 for empty workstreams + later). Spawn-path / kimi-k3 is out of scope (parked).
