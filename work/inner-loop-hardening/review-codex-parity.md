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

## Remediation re-review (2026-10-08)

Independent agent `/root/codex_parity_review`, GPT-6.1 Sol medium reasoning,
re-reviewed commits 49227d1 and ab8268e and ran the targeted parity suite.

- R1 resolved: target-checkout `--target` entrypoint performs first migration
  with `--skip-prepare`. Regression fixture byte-matches the previous upgrader.
- R2 resolved: install/upgrade check Git trackability, report blocking rules
  and preserve unrelated consumer rules.
- Boundary: ok, including the approved additional fixture glob.
- No remaining findings. Reviewer modified no files; tree clean.

## Verdict

APPROVED at `ab8268e57db6fbb99577a427d660f56240889bb2`.
Outer Verify subsequently passed all 34 checks at this exact SHA.
Live discovery and current official docs remain unverified as documented.
