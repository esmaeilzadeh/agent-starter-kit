# Intent: status lists later inbox

## What

`./ask status` prints a later-inbox block after the workstream table. The block lists `.later/*.md` from the current checkout (`README.md` skipped). `--later-only` prints only that block. `--work-only` prints only workstreams. Tab completion offers both flags.

Explore skipped: destination already clear.

## Why

Parked work lives in gitignored files. People already run `./ask status` for open work. Later rows on that board make parked cards visible.

## Non-goals

- A `./ask later` command
- Issue-tracker sync
- Live workstream fields on cards (no stage, branch, or tip)
- `--later-id`, or `--work-id` matching a later slug
- Changing gitignore so cards get committed
- Finishing or merging `kit-talk-ai-team`

## Known assumptions

- Default output: workstreams first, then later. If `.later/` is missing, or only `README.md` is there, omit the later block.
- `--work-only` is today's workstream output.
- `--later-only` with no cards prints one line that says there are no later cards.
- `--later-only` and `--work-only` together exit 2.
- `--work-id` filters workstreams and omits later. `--later-only` with `--work-id` exits 2.
- `--json` adds `"later": [{ "slug", "title", "path" }]`. `--work-only` uses `"later": []`. `--later-only` uses `"workstreams": []`. Workstream objects stay as they are.
- Title comes from the first `# ` heading. Slug is the filename without `.md`. Sort by filename. A card whose slug matches a live or archived work-id still appears.
- Later reads the working tree. Workstreams still come from git refs (no checkout).
- Help text lists the new flags. Completion drops a flag once it is already on the line.
- Build Spec §23.4 and §30.1, ADR 0015, and `.later/README.md` change so they no longer say status ignores later.

## Open questions

None from the closed grill frontier.

## Human decisions

- Q1-B: `--work-id` stays a workstream filter and hides later. The inbox is `--later-only`.
- Answer `b` accepted that option and the assume-list above.
