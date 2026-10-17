#!/usr/bin/env bash
# Grill/Spec/Plan/06/09 require E2E applicability or not_applicable plus reason.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

for f in \
  _ask/templates/intent.md \
  _ask/templates/spec.md \
  _ask/templates/plan.md \
  .agents/ask/stages/01-grill.md \
  .agents/ask/stages/02-spec.md \
  .agents/ask/stages/05-plan.md \
  .agents/ask/stages/06-implement.md \
  .agents/ask/stages/09-verify.md
do
  grep -qiE 'e2e' "$f" || { echo "FAIL: $f missing E2E" >&2; exit 1; }
  grep -q 'not_applicable' "$f" || { echo "FAIL: $f missing not_applicable" >&2; exit 1; }
done

grep -qi 'decompose implementation into one or more reviewable tasks' .agents/ask/stages/05-plan.md \
  || { echo "FAIL: Plan stage must require an implementation task breakdown" >&2; exit 1; }
grep -q 'task_scopes' .agents/ask/stages/05-plan.md \
  || { echo "FAIL: Plan stage must map tests to tasks" >&2; exit 1; }
grep -q 'inner-loop/tasks.yaml' _ask/templates/plan.md \
  || { echo "FAIL: plan template must point to the task graph" >&2; exit 1; }
grep -q 'Completion evidence' _ask/templates/plan.md \
  || { echo "FAIL: task breakdown must define completion evidence" >&2; exit 1; }
grep -q 'accepted plan.s task graph' .agents/ask/stages/06-implement.md \
  || { echo "FAIL: Implement stage must execute planned tasks" >&2; exit 1; }

echo "PASS: E2E contract and plan-to-task/test breakdown required before implementation"
