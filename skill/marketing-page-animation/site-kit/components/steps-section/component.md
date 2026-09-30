# steps-section

Captured verbatim from `component-library/components/steps-section/`.

- Fields used by the template: 7
- Fields with a blueprint default: 2
- **Template reads fields with no blueprint default:** image, kicker, name, platforms, steps
- **Copy fields not in the translatable-key list:** platforms. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
