# Workbench redesign: authorized follow-up

Status: human-directed requirements accepted for planning on 2026-10-09; independently reviewed contract pin required before implementation. This stays within `structured-agentic-environment` on its existing branch.

Design authority is the current ten-part brief and latest clarification requiring one hierarchy; earlier tabular design choices do not constrain this plan. Authority: the human invoked `kit-05-plan` with the complete ten-part redesign brief and explicitly required a planning stop before switching to Luna. This directive supersedes the older table-only interaction choice and its navigation-redesign non-goal. The existing `intent.md` and `intent-confirmation.json` remain historical records of the earlier scope; their exact bytes and attributed approval are preserved. No approval for this newly written artifact is invented or requested.

The one current specification remains `specs/current/structured-agentic-environment.md` with its adjacent canonical JSON, now revision 3. Criteria EM-001–007 and their authority/guard requirements remain intact. EM-008–012 express the requested relationships, branch browsing, task/attention navigation, result/source fidelity, and design/performance outcomes.

Changes from the prior UI scope:

- Replace table-first navigation with one Epic → Story → Scenario → Task → Test → Result/Evidence hierarchy, with contextual detail, optional filters and actionable attention.
- Read local work inventory from refs and the default-branch archive; inspect other committed revisions without changing the working checkout. Unsupported/missing models remain visible limitations.
- Join the real task graph, reviewed test scopes, actual runtime results, and Engineering Model without inventing historical task completion.
- Retain lazy evidence evaluation; load selected test source rather than every source on Overview. Measure the actual UI before changing frameworks.
- Apply the pinned Anthropic frontend-design skill and installed Streamlit design/layout/performance references. Native theme/layout remains the first implementation; a framework replacement needs a measured justification and amended contract, not a silent switch.

Artifacts affected: current specification Markdown/JSON; this workstream's plan, design, task graph, test plan, independent plan review, accepted-contract pin, and planning measurements. Future production changes are assigned in the plan. No application implementation occurs during this planning turn.

Migration: preserve all old test IDs, change classifications, execution/review records and accepted-pin history. Add future test obligations and task scopes. A new accepted pin does not repair older missing red evidence, establish new task results, or certify existing feature completion. Keep those verification gaps explicit.

Stopping condition: complete and review the planning artifacts, commit them, pin the reviewed contract, and stop. Implementation begins only after the human says `continue` following the model switch.
