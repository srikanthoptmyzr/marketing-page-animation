# reviews-section

Captured verbatim from `component-library/components/reviews-section/`.

- Fields used by the template: 6
- Fields with a blueprint default: 9
- **Copy fields not in the translatable-key list:** rating, review_title. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: view_all_reviews
