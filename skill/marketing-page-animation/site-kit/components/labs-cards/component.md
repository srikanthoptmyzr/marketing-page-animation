# labs-cards

Captured verbatim from `component-library/components/labs-cards/`.

- Fields used by the template: 4
- Fields with a blueprint default: 7
- **Template reads fields with no blueprint default:** comingSoonProjects, upcomingBtnText
- **Copy fields not in the translatable-key list:** comingSoonProjects, releasedProjects. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
