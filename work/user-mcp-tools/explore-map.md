# Explore Map: user MCP + tracker wizard + existing-repo setup

## Destination

A **human-run** `./ask setup` wizard that (1) can attach this kit to an already-built git repo by calling the existing non-interactive overlay, (2) lets the human pick an issue tracker (`gitlab` / `github` / `jira` / `none`), (3) collects instance URL (and credentials where that tracker needs them) with per-tracker prefills, or skips those stages when `none`, and (4) optionally installs memory MCP tools — without committing secrets.

## Notes

- Seed: `.later/user-mcp-jira-and-memory.md`.
- Skills: wayfinder (file map), research, grilling.
- Facts: `work/user-mcp-tools/explore/facts-mcp-and-install.md`.

## Tracker map (optional)

None. This file is the Grill handoff.

## Decisions so far

Human confirmed Explore Q1–Q8 (2026-09-13), all recommended answers:

- **Product split:** Kit ships the wizard and MCP stubs. Tokens and binaries stay on the machine.
- **Commands:** `./ask install` stays non-interactive (agent-safe). Human-only `./ask setup` may invoke install. Docs must say agents do not run `setup`.
- **Secrets and context:** Tokens only via env / global MCP (`${env:...}`). Per-repo current issue in a gitignored context file. Committed: tracker *type* + public URL only.
- **Env files:** Commit `.ask.env.example` (empty/placeholder keys, never live tokens). Gitignore `.ask.env`. Wizard writes the live file.
- **Memory:** Optional menu of memory MCP servers; skip allowed. Default on this machine: `codebase-memory-mcp`.
- **Tracker choice:** GitLab, GitHub, Jira, none. `none` skips URL/key; remaining action is re-ask (go back).
- **Prefills:** Jira `https://jira.partcorp.ir/` (labeled default, can clear); GitHub `https://github.com/` or `git remote`; GitLab `https://gitlab.com/`; all editable.
- **GitLab bind:** Official GitLab MCP (`https://<host>/api/v4/mcp`) + browser OAuth. Wizard asks URL only; no GitLab PAT in `.ask.env`.
- **GitHub bind:** Official GitHub MCP + PAT via env (from `.ask.env`).
- **Jira bind:** `mcp-atlassian` + URL + token via env.
- Existing-repo path uses today’s `./ask install` overlay.

Facts (not decisions): see `explore/facts-mcp-and-install.md`.

## Not yet specified

- Exact gitignored path for current epic/story context (Grill can pick a name).
- Which extra memory servers appear on the menu besides `codebase-memory-mcp` (Grill can keep “discover or skip”).
- Wizard stage copy and URL-open help text (implementation).

## Out of scope

- Storing live tokens in git, cards, or chat examples.
- Replacing `./ask install`’s non-interactive agent contract with a blocking wizard.
- `--interactive` on `./ask install`.
- Committing a live `.ask.env`.

## Handoff to Intent

**DESTINATION_CLEAR.**

**Why:** Humans must configure an issue tracker and optional memory MCP without leaking tokens, and must be able to drop the kit onto a repo that already has product code.

**What:** Ship kit-owned, human-only `./ask setup` (wizard). Keep `./ask install` as the existing-repo overlay and let setup call it. Tracker stages: GitLab / GitHub / Jira / none. Prefills as above. GitLab = official MCP + OAuth (URL only). GitHub/Jira credentials go in gitignored `.ask.env` (template `.ask.env.example` committed). MCP config uses `${env:...}`. Optional memory MCP menu (default `codebase-memory-mcp`). Gitignored per-repo current-issue context; committed tracker type + public URL only.

Ready for `01 Grill` to write `intent.md` from this handoff. No remaining human decisions block Intent; leftover naming is Grill/Spec detail.
