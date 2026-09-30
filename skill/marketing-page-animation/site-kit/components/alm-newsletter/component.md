# alm-newsletter

Captured verbatim from `component-library/components/alm-newsletter/`.

- Fields used by the template: 7
- Fields with a blueprint default: 0
- **Template reads fields with no blueprint default:** companyTypes, emailPlaceholderText, label, newsletterHeading, selectPlaceholderText, submitBtnTxt, value
- **Copy fields not in the translatable-key list:** emailPlaceholderText, selectPlaceholderText, submitBtnTxt. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
