# comparison-pros-cons

Captured verbatim from `component-library/components/comparison-pros-cons/`.

- Fields used by the template: 6
- Fields with a blueprint default: 6
- **Copy fields not in the translatable-key list:** cons, cons_text, pros, pros_text. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
