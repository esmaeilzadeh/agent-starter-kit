# Canonical protocol under `.agents/ask/` and Git-flow

Stage contracts, bindings, and verification core live under `.agents/ask/`.
`./ask sync` reads that tree. `_ask/agents/*.md` and `_ask/bindings/` (except
consumer `models.yaml`) are pointers. Consumer overlays: `.agents/ask.local/`.
Upgrade refreshes `.agents/ask/` as one kit-owned unit.

Git-flow: `develop` is the integration branch; `agent/<work-id>` starts from
`develop`; protected `main` is releasable (human merge, tag, push). Policy:
`_ask/policies/git-flow.md`. Optional in-workstream task worktrees: one writer,
fast-forward only — `_ask/policies/worktree.md`.

Supersedes the protocol-SoT claim in ADR 0005 (`_ask/agents/` as SoT).
