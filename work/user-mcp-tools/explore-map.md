# Explore Map: user MCP + tracker wizard + existing-repo setup

## Destination

A **human-run setup wizard** that (1) can attach this kit to an already-built git repo using the existing overlay, (2) lets the human pick an issue tracker (`gitlab` / `github` / `jira` / `none`), (3) collects instance URL and credentials with per-tracker prefills (or skips those stages when `none`), and (4) installs memory MCP tools — without committing secrets.

## Notes

- Seed: `.later/user-mcp-jira-and-memory.md` (human expanded: multi-tracker + wizard + existing repo).
- Skills: wayfinder (file map), research, grilling.
- Facts: `work/user-mcp-tools/explore/facts-mcp-and-install.md`.

## Tracker map (optional)

None. This file is the Grill handoff.

## Decisions so far

Human confirmed Explore Q1–Q4 (2026-09-13):

- **Product split (Q1-C):** Kit ships the wizard and MCP stubs. Tokens and binaries stay on the machine.
- **Commands (Q2-C):** `./ask install` stays non-interactive (agent-safe). A separate human-only setup command may invoke install. Do not add `--interactive` to install.
- **Secrets and context (Q3-A + template):** Tokens only via env / global MCP (`${env:...}`). Per-repo current issue in a gitignored context file. Committed: tracker *type* + public URL only. **Also commit a template example for `.ask.env`** (live `.ask.env` gitignored; example has empty/placeholder keys, never live tokens).
- **Memory (Q4-B):** Optional menu of memory MCP servers; skip allowed. Default on this machine: `codebase-memory-mcp`.
- Tracker chosen by the user: GitLab, GitHub, Jira, none. `none` skips URL/key; remaining action is re-ask.
- Each tracker uses that tracker’s proper tooling.
- Existing-repo path uses today’s `./ask install` overlay.

Facts (not decisions): see `explore/facts-mcp-and-install.md`.

## Not yet specified

- Prefill URLs (Jira card default was `https://jira.partcorp.ir/`).
- GitLab: official OAuth MCP vs PAT-based server.
- Human command name (`./ask setup` vs another).
- Exact example filename (`.ask.env.example` vs committed empty `.ask.env`).

## Out of scope

- Storing live tokens in git, cards, or chat examples.
- Replacing `./ask install`’s non-interactive agent contract with a blocking wizard.
- Implementing in this Explore session.

## Handoff to Intent

**STILL_FOGGY** on prefills, GitLab auth, and setup command name. Product split, install/setup split, `.ask.env` template, and memory menu are owned.

Draft Why: humans must configure tracker + memory MCP without leaking tokens, and must be able to drop the kit onto a repo that already has product code.

Draft What: kit ships a human-only setup wizard plus `.ask.env` example; `./ask install` remains the existing-repo overlay; bind GitHub / GitLab / Jira / none; MCP config interpolates env from `.ask.env`; gitignored current-issue context; optional memory MCP (default `codebase-memory-mcp`).
