# Specification: user MCP + tracker wizard + existing-repo setup

## Status

CURRENT

## Goal

Humans can run `./ask setup` to choose an issue tracker, store secrets locally, bind the matching MCP, optionally install a memory MCP, and overlay this kit onto an already-built git repo — without committing tokens.

## Non-goals

Interactive `./ask install`. Agents running `setup`. Live tokens in git. Jira tools for GitHub/GitLab.

## Behavior

- `./ask setup` is human-only: refuse when stdin/stdout is not a TTY (except `--help`).
- `./ask install` stays non-interactive. Setup may call it when the human gives another repo path.
- Tracker menu: `gitlab` | `github` | `jira` | `none`. `none` skips URL/key; the next action is go back and choose again.
- Prefills: Jira `https://jira.partcorp.ir/` (clearable); GitHub `https://github.com/` or `git remote`; GitLab `https://gitlab.com/`. All editable.
- GitLab: official MCP `https://<host>/api/v4/mcp` + browser OAuth. URL only.
- GitHub: official hosted MCP + `GITHUB_TOKEN` via `${env:GITHUB_TOKEN}`.
- Jira: `mcp-atlassian` + `JIRA_URL` / `JIRA_PERSONAL_TOKEN` via env.
- Commit `.ask.env.example`. Write live values to gitignored `.ask.env`.
- Write gitignored `.ask/tracker-context.md` for current epic/story.
- Write `.ask/tracker.md` (type + public URL only) for the human to commit.
- Merge server stubs into `~/.cursor/mcp.json` without writing token values into that file.
- Memory menu: `codebase-memory-mcp` (default path `~/.local/bin/codebase-memory-mcp`), skip, or custom command.

## Interfaces

- `./ask setup` → `_ask/scripts/setup.sh`
- `./ask install <repo>` (unchanged)
- `.ask.env.example`, `.ask.env`, `.ask/tracker.md`, `.ask/tracker-context.md`
- `~/.cursor/mcp.json`

## Constraints

Never commit `.ask.env` or tracker-context. Do not print secrets. Do not add `--interactive` to install.

## Invariants

Agents cannot complete `setup` without a TTY. Install remains usable from scripts.

## Failure cases

- Agent runs `./ask setup` → exit 2, message says human-only.
- `none` then stop without re-ask → violates the loop.
- Token written into `mcp.json` or a committed file.

## Acceptance criteria

- `./ask setup --help` works without a TTY.
- `./ask setup` with stdin not a TTY exits non-zero and does not write `.ask.env`.
- `.ask.env.example` exists and contains placeholder keys only.
- `.gitignore` ignores `.ask.env` and `.ask/tracker-context.md`.
- `./ask --help` lists `setup`.
- `./ask install` tests still pass.
- `./ask verify` passes.

## Open questions

None that block implementation. Extra memory servers: discover or skip.

## Source intent

`work/user-mcp-tools/intent.md`
