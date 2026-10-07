# Codex parity review

## Model

Runtime: codex. Reviewer: GPT-6.1 Sol, medium reasoning, user-confirmed override.
Parent model: GPT-6 (exact serving variant unavailable). Same-family disclosure
was followed by explicit human confirmation. Fresh independent context:
`/root/codex_parity_review`. Review commits nothing; parent records the report.

## Scope and boundary

`260ad4b..fba374c`. Approved Codex parity spec change and t14 task.
Boundary: ok; implementation fits t14 globs, with authorized coordinator spec
and work artifacts. Tree clean. Runner `no state` matches bootstrap Plan.

## Findings

### R1 — P2: first upgrade from previous version misses migration

`_ask/scripts/upgrade-kit.sh` refresh loop and final migration;
`_ask/tests/test-codex-skill-parity.sh` upgrade fixture.
The fixture runs the new upgrader with an old preparation script. A true older
consumer runs the old upgrader, whose running code never executes the new
migration logic. Reviewer reproduced an old-version upgrade with
`--skip-prepare`: exit 0, no generated Codex skills, blanket ignore unchanged,
and missing preparation namespace guard.

Provide and document an entrypoint that runs the target version's upgrade
logic against the consumer. Regression must start with the previous upgrader
and cover skipped dependency preparation.

### R2 — P2: install can report success with ignored generated skills

`_ask/scripts/sync-codex-skills.py` ignore migration and install invocation.
An unrelated ancestor `.agents/` ignore rule blocks skill tracking after the
known blanket rule is migrated. Reviewer reproduced install exit 0 with
`git check-ignore` still matching a generated stage skill.

Validate trackability using Git after generation. Preserve consumer rules;
fail clearly with the blocking rule. Cover ancestor-ignore install/upgrade.

## Verdict

REJECTED pending R1 and R2 fixes. Targeted parity suite passes but does not
currently cover these reproductions. Live discovery and current official docs
remain unverified as documented.
