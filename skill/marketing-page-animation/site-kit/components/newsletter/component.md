# newsletter

Captured verbatim from `component-library/components/newsletter/`.

- Fields used by the template: 4
- Fields with a blueprint default: 6
- **Copy fields not in the translatable-key list:** authorPageNewsletterTitle, bottomKicker. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: privacy_policy
- Depends on partials: newsletter-blog.html
