# Captured components

All 90 Bookshop components from the site repo, captured so a page can be assembled
in **Mode A with no repo access**. Refresh with:

```
python3 scripts/capture_component.py --repo <checkout> --all
python3 scripts/capture_component.py --repo <checkout> --used-by content/english/solutions-new/search/monitoring.md
```

Source: `Optmyzr-Engineering/marketing-website` @ `c9ac095` (2026-09-29), read-only.

Each `<name>/` holds:

| File | What it is |
|---|---|
| `template.hugo.html` | The component's real Hugo template, **verbatim**. The authority for markup and class names |
| `fields.json` | Every field: whether the template reads it, whether the blueprint defaults it, its CloudCannon input type, and its localization status |
| `component.md` | A short summary, including anything that needs care |

## Reading `fields.json`

`localization` is one of:

- `translatable` — in the site's `translatableKeys`. **Prefer these names for any scene copy.**
- `skip` — in `skipKeys`. Never translated, and nothing nested inside is either. Correct for numbers, ids, image paths and state flags.
- `url-prefixed` — in `urlReplaceKeys`. Internal links get the language prefix.
- `unlisted` — in none of the lists.

## What `unlisted` really means

The **script** translator (`scripts/translation-scripts/translation/processor.js`) matches a
field's own key exactly, case-insensitively. Its `isParentTranslatable` flag is honoured only for
bare strings sitting directly inside an array — **not** for strings nested in an object, so a field
like `features[].benefit_1` is skipped even though `features` is itself listed.

The **LLM localization agent** (`.claude/agents/mktos-localization.md`) translates whole files as a
localization expert and in practice does translate these — `content/es/_index.md` has
`benefit_1` in Spanish today.

So the two paths disagree, and parity for an unlisted copy field depends on which one runs.
**65 distinct copy fields across the library are unlisted**, most commonly `client_name`, `stars`
and `benefit_1..3`. For new scene copy, choose a listed field name. If a component you reuse has
unlisted copy fields, note it in the handoff for the dev team rather than editing the config.
