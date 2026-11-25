# Client workflow hooks specification challenge

## Model record

- Reviewer: `kit-03-spec-challenge`, `gpt-6-astra` per the child runtime and frozen model resolver.
- Runtime: Codex.
- Parent model: GPT-6. The exact parent variant was unavailable.
- Reviewed commit: `e557b0ad09312a18671406d4f12aa84f55ba3691`.

## Verdict

PASS. All three criteria are observable and align with the approved intent. Use end-to-end coverage for first install, repeated installation, and upgrade, with an integration case for transactional rejection of malformed hook configuration.

Pin the migration fixture to the preceding release and use the documented entry point. Invoke both commands with native output envelopes and test the Cursor always-on fallback. Run the Codex hook from a nested working directory and use the project root for Cursor, as its project-hook contract specifies. Check that unrelated handler entries and their order survive updates and that repeating the upgrade leaves one AskIt hook per editor. Report actual editor smoke checks separately.
