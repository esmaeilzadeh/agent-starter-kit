# Runtime capability observation

Read-only observation on 2026-11-20: installed codex-cli 0.164.0 and cursor-agent 2026.09.26-dd393fe expose startup model flags. Those flags do not demonstrate that an already running parent orchestrator changed models. No authenticated inference, credential reads, or parent model switch was performed.

Official OpenAI references:
- [CLI developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli): manual `/model` and `/status` provide a human fallback and identity check. Their existence does not expose an automatic switch tool in this session.
- [App Server](https://learn.chatgpt.com/docs/app-server): model catalog RPC is available in that protocol.
- [Models and inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference): model/list may use a bundled or cached catalog. A list alone does not establish current account access.

Implementation therefore requires explicit runtime adapter provenance for current access, ordering, parent identity and switching; unavailable evidence must remain unknown. Fake-adapter tests demonstrate protocol behavior, not this session's native automatic-switch capability.
