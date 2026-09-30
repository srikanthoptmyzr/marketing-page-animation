# comparison-table

Captured verbatim from `component-library/components/comparison-table/`.

- Fields used by the template: 3
- Fields with a blueprint default: 9
- **Copy fields not in the translatable-key list:** competitors, tables. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: hide_common_features, highlight_differences
