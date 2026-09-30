# case-study-hero

Captured verbatim from `component-library/components/case-study-hero/`.

- Fields used by the template: 5
- Fields with a blueprint default: 8
- **Template reads fields with no blueprint default:** author, customerCompany
- **Copy fields not in the translatable-key list:** customer, customerCompany, customerTitle. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- Depends on partials: bookshop/shared/hugo/youtube-id.hugo.html
