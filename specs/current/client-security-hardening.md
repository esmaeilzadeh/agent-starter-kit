# Specification: AskIt client security hardening

## Status

CURRENT

## Goal and scope

Protect client files, credentials, and repository trust during AskIt setup, upgrade and use. Preserve project settings in Git and keep familiar CLI entry points. The existing upgrade preservation defect has its own repair record. Local verification is for trusted code. Managed execution of untrusted code and hosted workbench access are outside scope. Revision 2 also includes the approved upfront model decision and implementation-orchestrator handoff; existing security criteria are unchanged.

## Interfaces and constraints

Apply these requirements to the supported install, upgrade, bootstrap, completion, setup, prepare, sync, verify and UI entry points. Store user trust and private settings outside the client working tree. Direct execution of a checked-out script remains an explicit user action. A local check runs with the user's filesystem and network access. Environment filtering is not a sandbox.

Use the current user account's private storage and the existing project overlay. Leave specific encodings, package versions and implementation choices to Plan unless they change an acceptance criterion.

## E2E

Applicability: `applies`. Use disposable Git repositories, user configuration directories, and synthetic credentials. Exercise fresh install, reinstall, and existing client upgrade with custom tracked settings. Observe explicit trust, preservation, migration, and transactional error behavior through the CLI. Reset the fixture between journeys. Use local stand-ins for tracker and dependency services.

## Acceptance criteria

### CSH-001 Launcher trust

Given an untrusted checkout contains a project dispatcher, when a client invokes completion or a daily command through the global launcher:

- Completion is resolved by the installed launcher without executing any project dispatcher.
- Daily commands refuse delegation until the user explicitly trusts the current checkout and executable kit identity.
- Noninteractive use refuses delegation without recorded trust, and replacing the trusted executable identity invalidates trust.
- Shell startup files change only when the client opts in to completion installation.

### CSH-002 Write boundaries

Given a fresh or existing client has an unsafe destination path, an unexpected file type, or a collision whose ownership is ambiguous, when install, upgrade, or sync prepares to write kit or generated files:

- The command identifies the conflicting path and stops before writing.
- Force cannot authorize an unsafe path or ambiguous ownership.
- An otherwise valid operation changes only known kit outputs and preserves trackable project settings.

### CSH-003 Recovery after interrupted writes

Given preflight succeeded and a client has independent project settings, when a kit copy or sync fails after writes begin:

- The operation reports failure and restores the prior kit file contents and existence without disturbing client files.
- Restart after interruption can finish recovery, and a retry succeeds on the recovered tree.

### CSH-004 Private tracker credentials

Given a developer configures a tracker in a fresh project or migrates synthetic legacy credentials, when setup or migration stores settings and the tracker client loads them:

- Credentials are stored outside the repo in an owner-only file and are parsed as data.
- The public tracker record and diagnostics omit credential values, and URLs require HTTPS and reject embedded credentials.
- User-wide MCP changes require explicit opt-in.
- Tracked or staged legacy credentials trigger a warning and rotation instructions without printing values.

### CSH-005 Pinned distribution and skills

Given a client selects a verified kit release or uses the bundled skills and tracker installer, when askIt installs, upgrades or prepares approved dependencies:

- Kit execution requires a verified match to the selected immutable revision.
- Bundled skill sources resolve to pinned commits and package installers use exact reviewed versions.
- New project skill sources require approval before fetch, and mandatory preparation failures propagate.

### CSH-006 Trusted local verification

Given a trusted project has a valid check and the caller exports synthetic credentials, when the client runs a CheckPlan or an instrumented test:

- Routine checks run with an explicit allowlist and receive extra variables only when explicitly configured for the check.
- Retained outputs use private permissions and are excluded from normal Git staging.
- Help states that local execution retains the account's filesystem and network access and directs untrusted changes to isolated CI.

### CSH-007 Generated agent configuration

Given a project supplies a valid model override or one that cannot be represented as a single model scalar, when sync generates runtime configuration:

- Valid input round-trips as one model value.
- Invalid input is rejected before existing outputs change.

### CSH-008 Workbench network default

Given a developer starts the workbench with the default settings, when the listener starts:

- The service listens only on loopback by default.
- Any non-loopback listener requires explicit user configuration.

## Approved model-flow extension (revision 2)

### CSH-009 One model decision during Grill

Given a feature reaches Grill in a supported coding-agent runtime, when the agent presents model selection:

- Present the complete resolved stage model plan, existing overrides, same-family reviewer relationships and implementation orchestrator policy in one Confirm model plan or Change selected models interaction.
- One confirmation accepts all defaults; collect only requested stage exceptions together, with accompanying free text and no per-stage questionnaire.
- Record the runtime and resolved identities using the existing workstream model precedence; retain independent review contexts.

### CSH-010 Automatic stage model reuse

Given a confirmed model plan or an existing workstream with recorded choices and configured defaults, when a stage starts or the workstream resumes:

- Reuse recorded choices automatically without routine model pickers, defaults confirmations or same-family confirmations.
- Preserve authorized endpoints, scope, safety and acceptance decisions; model selection does not authorize intent or implementation.
- Pause only for a requested model change, unavailable selected model, unmet runtime capability or genuine scope or policy escalation, requesting only the missing decision.
- Preserve existing explicit choices and configured defaults without inventing historical consent or requiring a new-format record at every stage; collect a model decision at the next authorized Grill or explicit policy change.

### CSH-011 Implementation orchestrator handoff

Given the authorized next action is implementation and Grill confirmed the implementor update policy or an exact override, when implementation preflight evaluates the actual orchestrator:

- Use the latest accessible implementor for the active runtime under the confirmed policy, retaining an exact human override; verify live runtime and account availability rather than treating a static catalog as availability evidence.
- Continue without prompting if the orchestrator already matches; otherwise automatically switch and verify the actual orchestrator when supported before implementation writes.
- When automatic switching is unsupported, stop before implementation and request the named manual model change; resume on observable verification or explicit human acknowledgment when identity is not inspectable, recording which evidence was available.
- A child-model change or config edit is not orchestrator-switch evidence; unavailable models or catalogs require a concrete escalation without silent family substitution.
- A plan-only endpoint stops before this preflight and never requests an implementation model switch just to finish planning.

### CSH-012 Portable model decisions and capability evidence

Given cursor, Codex or another supported runtime supplies model selection and handoff capabilities, when the model workflow resolves defaults and produces runtime instructions:

- Keep stage roles portable and model catalogs and capability information in runtime bindings; reuse the existing override precedence.
- Confirm during Grill the latest-accessible-implementor policy at implementation entry while retaining exact stage overrides; Composer for Cursor and Luna for Codex are current family examples, not permanent version slugs.
- Represent unknown and unsupported discovery or switch capabilities explicitly and obtain actual runtime capability evidence during implementation of this feature.
- Carry the decision flow through canonical prompts, policies, generated runtime agents, skills and commands and user guidance so old projections do not restore routine stage model questions.

## Source and change control

Approved source: `work/client-security-hardening/intent.md`. The criterion registry at `specs/current/client-security-hardening.json` controls test obligations. Changes to accepted behavior or criteria require Stage 04.
