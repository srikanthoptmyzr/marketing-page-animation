# language-picker

Captured verbatim from `component-library/components/language-picker/`.

- Fields used by the template: 2
- Fields with a blueprint default: 9
- **Template reads fields with no blueprint default:** code
- **Copy fields not in the translatable-key list:** code. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: select_preferred_language
