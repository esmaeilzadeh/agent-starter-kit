# Plan for client workflow startup hooks

## Specification

[Accepted specification](../../specs/current/client-workflow-hooks.md), revision 1.

## Approach

Use one task for the shared runtime bootstrap, transactional hook registration, and migration. Both installers and both editors share these paths, so splitting the change would give intermediate clients inconsistent startup behavior. Keep editor-native hook payloads at the boundary. Use the existing install transaction, Git ignore ownership, and startup access check. Keep the source checkout's workflow disabled unless a frozen kit is in use.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| CWH-01 | Both client editors load the shared AskIt bootstrap with safe install and upgrade | none | Runtime scripts, Cursor binding, generated stage projections, client docs and tests listed in TaskGraph | CWH-T01, CWH-T02, CWH-T03, CWH-T04 | Executed Red and Green cases, independent candidate review, and integration receipt |

## Verification approach

Commit the four public-interface cases, elicit their behavior failures on the existing product, and then implement the smallest change that makes them pass. Run the relevant installer, client-write and access regressions. Run the full verification plan on the committed candidate. Include actual editor smoke results when the environment permits.

## E2E

Each journey uses a disposable Git repository. Invoke the startup commands from the installed configurations rather than calling a helper directly. Run Cursor hooks from the project root and Codex hooks from a nested directory. Assert the Cursor fallback is kit-owned. Use AskIt v2.0.1 at `6894d8dde1d8ee330ae891a3d8cb6415fa8095d8` as the migration fixture and repeat the documented upgrade against the pinned candidate. Dispose of fixtures after the run.

## Release

After acceptance, release on `main` following the root README. Keep the approved intent bytes intact. Begin the separate self-development documentation workstream after the hook release.
