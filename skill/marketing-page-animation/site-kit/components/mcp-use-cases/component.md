# mcp-use-cases

Captured verbatim from `component-library/components/mcp-use-cases/`.

- Fields used by the template: 3
- Fields with a blueprint default: 8
- **Copy fields not in the translatable-key list:** cards. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: copyFailed, copyPrompt, promptCopied, promptLabel, tryThisPromptHint
- Depends on partials: mcp-prompt-copy.html
