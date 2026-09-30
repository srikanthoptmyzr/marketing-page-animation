# hero

Captured verbatim from `component-library/components/hero/`.

- Fields used by the template: 12
- Fields with a blueprint default: 19
- **Template reads fields with no blueprint default:** RelPermalink
- **Copy fields not in the translatable-key list:** benefit_1, benefit_2, benefit_3. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: hero_new
- Depends on partials: functions/resolve-image-path.html
