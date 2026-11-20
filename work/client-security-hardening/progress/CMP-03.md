# CMP-03: compact milestone publication

Implemented the deterministic retained-checkpoint publisher and CLI, exact
precommit/postcommit retries, index/source guards, publication receipts, driver
integration/next-writer hooks, narrow retained-runtime clean checker and explicit
inventory migration. Pending tasks can be summarized without inventing attempts.
Public summaries use structured outcomes and digest references; private prose,
commands and captured output are excluded. Full checkpoint retention is unchanged.

Focused checks: nine milestone cases, shell clean-gate checks and the three
updated integration/crash cases pass. The first reliability run had 26 passes,
two old HEAD-identity expectations and one crash case requiring a fix. Recovery's
selected-ref ancestry check now accounts for integrated source preceding progress
publication; this narrow cross-module adjustment was reproduced by that case.

Next: independent review of this exact source candidate, then CMP-04. Live
adoption/backfill remains deferred until both components are reviewed. No accepted
artifact or authority pin was changed. No live proposal was regenerated.
