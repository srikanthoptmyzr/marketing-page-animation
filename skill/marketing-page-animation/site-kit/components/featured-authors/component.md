# featured-authors

Captured verbatim from `component-library/components/featured-authors/`.

- Fields used by the template: 3
- Fields with a blueprint default: 0
- **Template reads fields with no blueprint default:** authorsParams, bio, name
- **Copy fields not in the translatable-key list:** authorsParams. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
