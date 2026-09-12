# Intent: drop obsolete pek-cli workstream

## What

Remove `work/pek-cli/` from the kit. That workstream’s What was a root `pek` dispatcher; `rename-pek-to-ask` already replaced it with `./ask`.

## Why

`./ask status` still listed `pek-cli` as open intent even though the CLI name is gone.

## Non-goals

Changing `./ask`. Rewriting `work/rename-pek-to-ask`.

Explore skipped: destination already clear.

## Human decisions

Human: pek-cli is obsolete; remove it.
