# Plan

## Specification

Exactly `specs/current/structured-agentic-environment.md`, with adjacent JSON criteria EM-001–006. Preserve the authorized model-first→UI sequence and original handoff authority distinctions.

## Approach

One deep module under `_ask/scripts/engineering_model/` owns schema validation, controlled revision/digest-bound edits and projections. Its interface is shared by a thin `./ask model` CLI and a native Streamlit workbench. Definitions remain Git JSON; criterion/test/code/execution/runtime facts are referenced, not duplicated. Reuse existing traceability evaluation read-only. No graph database or generic persistence adapter.

## Work breakdown

1. Resolve Explore/Intent and prepare spec/test obligations; independent Astra/high Challenge, then pin exact accepted contracts. Prepare isolated fixture helpers and public-interface assertion-red cases at immutable commits.
2. Implement broad model validation and semantic mutation (local lock, compare-and-swap, atomic replace, decision history and invalidation). Add read-only evidence adapter and deterministic JSON/Markdown projection, thin CLI and explicitly labeled harness-review pilot. Run core/CLI tests and commit a working model foundation before any real UI implementation.
3. Implement the local Streamlit work selector/inspection/attention/decision form through that interface. Pin displayed form digest across reruns. AppTest integration and real browser E2E use only temporary fixtures/server, never the committed pilot. Optional UI dependency declarations and clear startup instructions accompany it.
4. Independent Sol/high candidate review checks behavior, authority, tests and CE-01–06. Address concrete findings without weakening criteria; Spec Change for scope/semantic changes. Refactor only where useful, run full Verify and acceptance check, record exact result and prepare human Accept with commit SHA.

## Risks

Broader taxonomy may overfit the pilot; keep fields/edges explicit and reject unsupported kinds. A raw pass field or stale browser state can mislead; reuse evidence authority, label revision freshness and preserve displayed digest. Git-side histories and typed model history have different jobs. POSIX local locks do not provide distributed coordination or authentication. Same GPT-family separate reviews are independent contexts, not cross-family diversity. Complex model implementation/review uses Sol/high; challenge Astra/high; routine checks Luna/low and bounded UI/test work Luna/medium where delegated.

## Verification approach

Unit validation/mutation invariants, disposable repository integration for concurrency and real evidence/provenance tampering, public CLI end-to-end journey, Streamlit AppTest interaction and a real browser journey. Exact cases/types are in `test-plan.json`; all new behavior needs real assertion red and final green. Whole repository CheckPlan remains required. Core model/CLI needs Python standard library only; UI/test dependencies are optional for users not opening the workbench but required for its verification.

## Out of scope for this plan

Full product/IDE, database, multi-host/auth, deployment, new test framework adapters, autonomous execution from UI, existing completion policy changes, all-workstream migration, main/develop merges and pushes. No unmeasured productivity claim.

## E2E

Applies: disposable CLI journey validates/projects/resolves/reloads and refuses invalid edits. Real browser journey inspects scenario→assertion/evidence, resolves a pilot decision, reloads durable state and rejects a second session's stale form. AppTest integration covers error paths separately. Streamlit 1.59 and Playwright with available Chrome are local test tools; ephemeral localhost server only, no production data. Each case owns/reset its temporary directory and process/browser; no persistent preview is started without asking.

