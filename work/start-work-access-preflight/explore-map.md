# Explore Map: start-work access preflight

## Destination

Make `./ask start-work <work-id>` detect missing local write access before it
creates or switches to an `agent/<work-id>` branch or writes workstream files.

## Notes

- Existing clean-tree and `develop` checks remain part of the entry flow.
- Explore is limited to local Git metadata and the repository path needed to
  create `work/<work-id>/` and copy templates.
- Do not test remote credentials or network push access; `start-work` does not
  publish branches.
- Use a temporary probe that is removed immediately so an access failure leaves
  no branch, workstream, or probe artifact behind.

## Tracker map (optional)

- No external tracker is configured; this file is the local Explore map.

## Decisions so far

- The existing entry point is `_ask/scripts/start-work.sh`; it checks for a
  clean worktree and a `develop` base, then changes branches before seeding
  `work/<work-id>/`.
- Current behavior has no explicit write-access preflight for Git metadata or
  the workstream destination.
- An earlier Git write in this session failed with `Read-only file system` at
  `.git/index.lock`, while `test -w .git` now reports writable. Permission-bit
  checks alone can miss access restrictions enforced by the execution
  environment; the preflight needs to attempt and clean up a real temporary
  write at each required location.

## Not yet specified

- Which precise Git metadata paths need a write probe for normal and linked
  worktrees.
- Whether the workspace probe should target `work/` or the nearest existing
  parent when `work/<work-id>/` does not exist.
- Exact error wording and exit code for each failed probe.

## Out of scope

- Remote authentication, network access, push permissions, and credential
  discovery.
- Repairing or changing filesystem permissions.
- Changing the clean-worktree, branch-base, or template-seeding rules.

## Handoff to Intent

Proposed scope: before any branch checkout/creation or workstream-file write,
probe write access to the Git metadata used by `start-work` and to the existing
workspace parent where `work/<work-id>/` will be created. On failure, exit with
an actionable message and leave no branch or workstream changes. Keep existing
clean-tree and `develop` checks. The acceptance test seam is the public
`./ask start-work <work-id>` CLI in a temporary Git repository.
