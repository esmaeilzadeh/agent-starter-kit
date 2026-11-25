# Client acquisition and security

## Acquire and trust the client

Do not treat a mutable branch or tag as verified source. Clone the repository,
check out the full commit SHA you reviewed through a trusted channel, and pass
that same SHA as both `--ref` and `--expected-commit` to `askit self-install`.
The installer fetches that revision again, checks the full commit and clean
working tree, then publishes the cache. A checksum printed by the same
unverified download is not an independent trust source. The first execution of
the reviewed `askit` file is still an explicit user trust decision.

The installed launcher records its accepted commit outside the project. If the
cache is modified, or its revision differs from the recorded one, reinstall
from a reviewed full SHA using the same `askit self-install` command. The
previous cache is retained until the verified replacement is published. For
an existing consumer, run:

```sh
./ask upgrade --version <tag-or-sha> --expected-commit <full-sha>
```

The upgrade refuses a fetched revision mismatch and uses a write transaction
to preserve recoverable state. When migrating an older consumer to a new
install flow, use the target checkout's upgrader as described in
[Codex integration](codex-integration.md).

## Remove previously tracked kit files

Run the current installer or upgrader to add the `AskIt local installation`
block to `.gitignore`. Git continues to track files already in the index.
List the tracked paths matched by the AskIt block from the client repo root.

```bash
git ls-files --cached --ignored --exclude-from=<(sed -n \
  '/^# BEGIN AskIt local installation$/,/^# END AskIt local installation$/p' .gitignore)
```

Review the list and run `git rm --cached -- <path>` for each kit-owned file
you want to stop tracking. This stages its removal and leaves the working
copy on disk. Commit the staged removals and `.gitignore`. Run `askit` in each
new clone or worktree to install the kit there.

## Credentials

Review `.ask.env` before migration. Run `./ask credentials migrate`; it parses
assignments as data and never evaluates shell syntax. The supported
`TRACKER_TOKEN` alias maps to the configured GitHub or Jira credential and is
stored in a versioned private record. Only credential assignments are removed
from `.ask.env`; comments and public tracker settings remain. Existing
conflicting private credentials stop migration before the legacy file is
changed. Old private files containing only `TRACKER_TOKEN` are unbound to a
tracker URL: migration and MCP launch stop without changing them. Re-enter the
tracker URL and token with `./ask setup` to replace that file. The Git index and
history are never edited. If the old file was
tracked or staged, rotate the credential because its old value may remain in
history. See [issue tracker setup](agents/issue-tracker.md).

## Verification environment and logs

Verification commands inherit only a small base environment (`PATH`, home and
user identity, locale, timezone, and `TMPDIR`). A check or test runner can add
explicit `env_allow` names in `.agents/verification.yaml` or the test plan.
Names containing credentials, tokens, secrets, API keys, loader settings,
Python settings, or `ASK_` metadata are rejected; runner-owned metadata cannot
be overridden by an allowlisted value.

Raw logs and execution outputs are private: output directories use mode `0700`
and files use mode `0600`. Keep raw output out of source commits; commit useful
redacted summaries and review evidence with references or digests as needed.
If old traceability `.log` files are already tracked, ignore rules do not
untrack them; inspect and remove them from the repository in a reviewed
cleanup commit. Rotate any exposed credentials. This does not rewrite history.
Verification warns about tracked legacy logs.

## Local UI

`./ask ui` binds to `127.0.0.1` by default. To expose it on another interface,
pass an explicit Streamlit address, for example `./ask ui --server.address
0.0.0.0`. This is a deliberate network exposure choice; use the narrowest
address your workflow needs.

## Model decisions and existing records

Model selection is confirmed once during Grill as one complete role/stage
table. The user can accept the defaults or submit requested exceptions
together; stage transitions do not reopen routine model pickers. An explicitly
saved workstream choice takes precedence over ambient model environment
settings. See [Codex model routing](codex-model-routing.md) for this runtime's
defaults and overrides.

An existing workstream keeps its configured implementation model until an
authorized Grill or explicit user change records a new policy. Legacy records
reuse their configured choices; they are not treated as consent to a newer
"latest accessible" policy. At implementation entry, inspect the real
orchestrator identity. If the runtime cannot switch the current session and
verify the result, stop at the manual handoff and name the required model and
the runtime UI action. Do not infer a successful handoff from child-agent
startup flags or edited settings. For consequential uncertainty, consult the
active runtime's confidence ladder before asking the human; it never grants
authority, changes scope, replaces independent review, or waives verification.
See the [delegation policy](../policies/delegation.md) for configured ladders.
