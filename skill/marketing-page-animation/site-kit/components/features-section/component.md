# features-section

Captured verbatim from `component-library/components/features-section/`.

- Fields used by the template: 9
- Fields with a blueprint default: 10
- **Copy fields not in the translatable-key list:** benefit_1, benefit_2, benefit_3. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: alert_delivery_options
- Depends on partials: functions/resolve-image-path.html, image.html
