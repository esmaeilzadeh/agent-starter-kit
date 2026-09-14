# Kit Protocol: 10 Accept

Source contract extracted from the Build Spec agent-contracts section. Portable SoT for this stage.

Acceptance artifact from `_ask/templates/acceptance.md`; record commit SHA.

## 15.10 10 Accept Agent

Purpose:

```text
Assemble evidence and decide whether the work is eligible for acceptance under policy.
```

Possible outcomes:

```text
AUTO_ACCEPT_ELIGIBLE
HUMAN_APPROVAL_REQUIRED
REJECT
```

The agent must explain the outcome and cite evidence.

Human approval remains mandatory where delegation policy requires it.

---

## Kit path

See `_ask/policies/workflow.md`. **Accept is the second on-path confirm** (after defaults-OK). Do not auto-close the workstream without it unless delegation says AUTO_ACCEPT_ELIGIBLE **and** policy allows.

Kit-mediated `./ask openspec-archive <work-id>` runs after Accept (SHA recorded). It is not the acceptance decision.
