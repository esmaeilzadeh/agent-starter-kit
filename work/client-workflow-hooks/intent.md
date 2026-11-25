# Intent: Start the client AskIt workflow from editor hooks

## What

Register local AskIt startup hooks on fresh client installs and supported upgrades. Cursor and Codex sessions load the same kit-owned workflow and report the access preflight result. Keep Cursor's project rule as a fallback for supported sessions where the hook does not inject context. Stop installing or requiring a root client `AGENTS.md`. Preserve existing client instruction files and unrelated editor hooks.

Ship the verified work to AskIt `main` using the documented annotated release tag and README installer pin. The separate work to shorten AskIt's own agent entry points starts after this release.

## Why

Clients own their repository instructions. AskIt should load its workflow when a configured session begins even when the client already has its own `AGENTS.md` or has no such file.

## Non-goals

Repository-wide Git or CI enforcement, new bindings for other editors, and automatic deletion of files left by older installs.

## Known assumptions

- These hooks target Cursor and Codex local sessions. Codex project hooks require the runtime's trust choice and existing shell/CLI prerequisites.
- The hooks load instructions and check access. Git and CI admission remain separate.
- Existing hook configuration stays client-owned. If an existing hook file cannot be read or safely updated, install or upgrade fails without overwriting it.
- This is a standalone AskIt workstream with no external subject or tracker association. Workflow instructions and checks are pinned to `0e303265ceae1fbcdc9b2261bd922b003ab68924` in `/tmp/askit-dogfood.0BXUZGWN`.

## Open questions

No unresolved product scope questions.

## Human decisions

Explore skipped: destination already clear.

## E2E

Applicability: `applies`.

Use disposable Git client checkouts. Cover fresh installation without `AGENTS.md`, installation with client-owned instructions and existing editor hooks, and migration of an older install. Invoke the configured startup commands and verify that both load the workflow on success and report blocked access on failure. Check repeated application for duplicate hooks. Use runtime smoke checks where available. Reset by disposing of the fixture checkouts.
