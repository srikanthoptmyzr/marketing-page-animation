# contact-form

Captured verbatim from `component-library/components/contact-form/`.

- Fields used by the template: 10
- Fields with a blueprint default: 17
- **Copy fields not in the translatable-key list:** fullName, message, optmyzrEmail, prefer_email, sendMessage. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: error_occurred, submitted_successfully, submitting
