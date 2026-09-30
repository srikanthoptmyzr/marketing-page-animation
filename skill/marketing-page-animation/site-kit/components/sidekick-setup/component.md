# sidekick-setup

Captured verbatim from `component-library/components/sidekick-setup/`.

- Fields used by the template: 7
- Fields with a blueprint default: 10
- **Copy fields not in the translatable-key list:** platforms, platformsLabel. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
