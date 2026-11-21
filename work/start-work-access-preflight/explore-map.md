# Explore Map: start-work access preflight

## Destination

Fail early when the project session cannot write to local Git metadata or its
workspace, including when starting work or resuming a workstream.

## Findings

- `start-work.sh` checks cleanliness and the `develop` base, then changes
  branches and writes workstream files; it has no write-access probe.
- Permission-bit checks are insufficient: a prior `.git/index.lock` write was
  denied by the environment while `test -w .git` said writable. Probe by
  creating and removing a temporary file.
- Cursor provides session lifecycle hooks, but its docs exclude `sessionStart`
  for Cloud Agents. Runtime hook support differs, so keep one shared CLI check
  and require it in portable project instructions as well as wiring supported
  startup/resume hooks for available bundles.

## Handoff to Intent

Add `./ask access-check` to probe the Git metadata location and nearest
existing workspace parent with temporary writes, cleaning probes immediately.
Run it on project session start and before resuming work across supported
bundles, and before `start-work` changes branches or writes files. On failure,
give an actionable message and stop. Do not test remote auth or repair
permissions. Retain current clean-tree and branch-base behavior.
