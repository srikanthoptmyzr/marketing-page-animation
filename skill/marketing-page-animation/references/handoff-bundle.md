# Handoff bundle and preview

Used in phases 11 and 14 (the preview is built as the page is assembled, the bundle is packaged at the end). Goal: give the user a page they can review and share, and give the dev team everything they need to add it to the website without guessing.

## The preview page (`preview/`)

- A self-contained folder: `index.html`, styles, the scene player, and assets. Opens locally with no build step and no server dependencies.
- Uses the site kit's header, footer, tokens and patterns, so it looks like a page from the real site.
- Contains the same scene and section markup that goes into the bundle.
- May include a **preview-only language toggle** (see `localization.md`). It is clearly labelled as preview-only and is not part of the bundle, and neither are its drafted translations.
- Contains no reference screenshots, frames, videos, original data or analysis files.
- Sharing it (a local folder, or a hosted private link) is the user's decision. Do not publish it unprompted.

## The handoff bundle (`handoff/`)

```
handoff/
  README.md                 Start here (from templates/handoff-readme.template.md)
  page/
    content.en.md           Page content in the site's front matter format, English source
    strings.en.toml         Small UI labels, if any (English source)
  components/
    <scene-name>/           Scene component: blueprint, template, stylesheet
  assets/
    js/                     Scene player and timelines
    (images only if truly needed and non-sensitive)
  spec/
    scenes.json             Sanitized scene spec
    privacy-report.md       Privacy summary (content below). No originals
    storyboard.md
    design-mapping.md       How the design system and the kit were mapped to the page, with gaps and assumptions
  reports/
    validation.md
    privacy.md              Full privacy report (same rules as privacy-report.md)
    screenshots/            Screenshots of the rebuilt page only, never of a reference
  preview/                  English-only copy of the preview page, for reference
```

`spec/privacy-map.json` is deliberately not in the bundle: it holds the replacement values, which are already in the content files, and the bundle needs no more than the report. `.private/` is never included.

In Mode B there is no bundle to assemble, because the files are already in the repo. The validation and privacy reports are still produced and handed to the repo's review step.

### `spec/privacy-report.md`

The report says what was done, never what the values were. It contains:

1. **Counts by class** of entities replaced, using the classes in `privacy-masking.md` (for example "12 IDs, 5 names, 3 emails, 4 amounts").
2. **Result of each scan step** from `privacy-masking.md` section 7 (exact, normalized, encoded and reversed, fragments, unregistered patterns, runtime, media, localization), as pass or fail with file paths and entity ids for any finding, and the result of the map audit.
3. **Judgment calls** made and by whom: values kept as public, approved reference customers (and where the approval is recorded), amounts whose story was rewritten.
4. **Residual risks**, for example a phone number from a country with no reserved range, a company name that could not be checked against real businesses, or a possible coincidental match.
5. **Instructions for the dev team**: replacements are final and must not be regenerated, and translators receive the resolved values only.

It never contains an original value, a fragment of one, a hash of one, or a description that would let someone recover one.

### What the developer needs from the README

1. **What this is.** One paragraph: the page's purpose, audience and CTA.
2. **What to add where.** A table mapping each bundle file to its destination in the repo, and the block or page it binds to.
3. **How it was built.** Which existing components and patterns were reused, and which parts are new (the scene component and scripts). Point to `spec/design-mapping.md` for how the design system and the kit were applied.
4. **Kit gaps.** Sections or elements the kit lacked, and what was used instead.
5. **Unverified conventions.** Assumptions about field names, class names, file locations or script loading that a developer must confirm. Each one names what to check.
6. **Translatable fields.** The field names the scene uses. If any are not on the site's translatable list, say so, because the dev team must handle them.
7. **Localization.** English source only. Ask the localization step to mirror it into every active language. Any draft translations in the preview are for layout checks and are not included, or are clearly flagged if included.
8. **Animation and accessibility notes.** Reduced-motion behavior, controls, how the scene is described to assistive technology.
9. **Validation summary.** What passed, what was approximated, what needs human review, and a pointer to `spec/privacy-report.md`.
10. **Suggested next step.** For a Marketing-OS repo: run the bundle through the normal feature flow with the README as the request and the bundle files as inputs. Otherwise: the equivalent integration steps.

Keep it in plain English. A developer should be able to integrate the page in one sitting.

### Component files

- Follow the site's component shape from the kit (**verified against the repo, 2026-09-29**):

  | File | Goes to | Notes |
  |---|---|---|
  | `<name>.bookshop.yml` | `component-library/components/<name>/` | `spec` (label, `structures: [content_blocks]`), `blueprint` with a default for **every** field, `_inputs` for CloudCannon field types |
  | `<name>.hugo.html` | `component-library/components/<name>/` | The real markup. All text from fields, never hard-coded |
  | `<name>.css` | `static/websitecss/` | Scene styles. **Not** a component `.scss` — the live `claude-connector-hero` has no SCSS file at all |
  | `<name>.js` / `scene-player.js` | `static/websitejs/` | Plain static asset; reads everything from `data-*` attributes so it stays content-free |
  | Page front matter | `content/english/<section>/<page>.md` | `content_blocks` entries keyed by `_bookshop_name`; start from the matching `.cloudcannon/schemas/` template |

- Use the class names recorded in the kit's class map. Where a needed class or field is not confirmed, leave a clearly marked `TODO(dev)` comment rather than inventing.
- Name scene fields from the site's translatable-key list before inventing any; put numbers, ids and state flags in skip-key names so they are never translated (`localization.md` section 3).
- Mirror the existing `claude-connector-hero` component — same namespacing, accessibility shape and script convention (`hugo-bookshop-target.md`).
- All text is a field or string, never hard-coded.
- No inline scripts. Scripts live in `assets/js/`, and the README says how they should be loaded.
- No raw HTML embeds in content files.

### What never goes in the bundle

- Reference screenshots, videos, extracted frames, contact sheets.
- `analysis/`, `input/`, `.private/`, original sensitive values, or anything derived from them that could recover them.
- Credentials, internal URLs, or personal data.
- Machine translations presented as final.

## Notes the developer needs about the scenes

- Load `scene-player.js` early (head, or before the first scene) so `pu-js` is set and scenes never flash their final state.
- Feature scenes are wrapped for slot fitting (`pu-fit` with `data-fit-*` attributes in `page/main.html`). The standalone files in `scenes/` do not carry those attributes, because they belong to the page slot.
- The FAQ uses the site's own `toggleFaq()`. The preview ships a stand-in that the bundle does not include.
- List every feature row with a placeholder image slot as a missing input.

## Packaging checks

- Every file referenced by the README exists, including `spec/design-mapping.md` and `spec/privacy-report.md`.
- **Run the privacy leak scan** (`scripts/validate/leak_scan.py`, or the manual equivalent of `privacy-masking.md` section 7) over the final `preview/` and `handoff/` as they will be shared, after all copying. A single hit blocks packaging. Do not zip or hand over until it passes.
- The bundle contains no files from the excluded list, and `reports/screenshots/` shows only the rebuilt page.
- The `preview/` copy in the bundle is English-only and has no language toggle.
- The preview renders from a clean folder with no other files.
- Zip the bundle only if the user asks for a single file to send.

## After handoff

Tell the user plainly what to send and to whom: the `handoff/` folder, plus the preview folder or link. Explain that the dev team will integrate and publish, and that the page will be translated by the site's normal process. Offer to revise the page from developer feedback, and if the developers' changes reveal a wrong assumption, suggest updating the site kit so the next page benefits.
