# Repo inventory (read-only mining)

**Repo:** `Optmyzr-Engineering/marketing-website` · **branch** `main` · **commit** `c9ac095442e6126f90ebcd75e6dfac6bbed97c6c` (2026-09-28)
**Checkout:** `~/Documents/marketing-website` (blobless sparse clone; raster/video blobs excluded). **Read-only — never edit, commit, push or build into it.**
**Date mined:** 2026-09-29. This file covers playbook steps 1–3 and 7 of `README.md` section 12.

## 1. Top-level map

| Path | What it is | Matters to the skill |
|---|---|---|
| `config/{_default,staging,production}/hugo.toml` | Hugo config, languages, outputs, taxonomies, permalinks | Languages, URL rules |
| `content/<lang>/…` | Page content, YAML front matter, `content_blocks` arrays | Page structure is **data**, not layout |
| `component-library/components/<name>/` | **Bookshop component library**, 90 components | The page is assembled from these |
| `themes/optmyzr-marketing-v2/layouts/` | Hugo layouts and partials (header, footer, head, hreflang, image) | Chrome and page shells |
| `data/{en,es,de,fr,jp,da}/` + shared root files | Navbar, footer, links, testimonials per language | Menus are per-language data |
| `i18n/{en,es,de,fr,jp,da}.toml` | Small UI strings, `{{ i18n "key" }}` | Chrome labels |
| `static/websitejs/`, `static/websitecss/` | Plain static JS/CSS assets, incl. per-component scene files | **Where a scene player would live** |
| `scripts/` | Build, translation, validation tooling | Translatable-key config, parity validator |
| `.claude/` | Marketing-OS agents, commands, skills, workflow | How the dev team builds and reviews pages |
| `.cloudcannon/`, `cloudcannon.config.yml` | CMS schemas and collections | How marketers edit; English-only |
| `evals/` | Eval suite incl. locale parity | Existing quality gates |

`layouts/` at the repo root is empty (`.gitkeep`); everything lives in the theme.

## 2. Page types (confirmed from code + content)

A page's structure is the ordered `content_blocks` list in its front matter. The newest solution layout
is fully component-driven:

```
layouts/solutions-new/v4-generic-solutions-page.html
{{define "main"}}
  {{ partial "bookshop_bindings" `.Params` }}
  {{ partial "bookshop_bindings" `.Params.content_blocks` }}
  {{ partial "bookshop_partial" (slice "page" .Params.content_blocks) }}
{{end}}
```

Solution-page layouts in use (English content): `generic-solutions-page` (34 pages),
`v4-generic-solutions-page` (29), `v2-generic-solutions-page` (5). Component frequency across them:

| Component | generic (18 pages w/ blocks) | v4 (29) | v2 (4) | Verdict |
|---|---|---|---|---|
| `hero-solution` | 18/18 | 27/29 | 4/4 | **required** |
| `animated-trail-banner` | 18/18 | 29/29 | 4/4 | **required** |
| `features-section` | 18/18 | 26/29 | 4/4 | **required** |
| `faq-section` | 18/18 | 29/29 | 4/4 | **required** |
| `cta-section-solutions` | 16/18 | 28/29 | 4/4 | **required in practice** |
| `casestudy-section` | 14/18 | 1/29 | 4/4 | **optional**, and being dropped in v4 |

Order is stable: hero → trail banner → features → (case studies) → CTA → FAQ.
This **confirms the structure the kit already had**, now from code rather than observation.

Other layouts present: `compare`, `pricing-page-v2`, `generic-product-page`, `content-hub`,
`demo-request`/`demo-request-v2`, `case-studies`, `post`, `careers`, `research-hub`, `search`, `about`,
`labs`, `partners`, `thank-you`. Not yet mined.

## 3. Components

90 components in `component-library/components/`. Each is three files:

```
<name>/<name>.bookshop.yml    spec (label, structures, tags) + blueprint (default field values) + _inputs (CloudCannon field types)
<name>/<name>.hugo.html       the Hugo template — the real markup and classes
<name>/<name>.scss            usually a one-line stub; styling is Tailwind utilities in the template
```

`spec.structures: [content_blocks]` is what makes a component selectable as a page section.

### `features-section` — the slot the skill's scenes go into

Read from `features-section.hugo.html`:

- Section heading is **`h2`**; each feature heading is **`h3`**. *(Settles README section 7 open decision 1: h3.)*
- Rows alternate automatically: `$isEven` swaps `md:order-1`/`md:order-2` on the text and image halves. Layout is always half/half — **uniform rows are correct**.
- Image half:
  `bg-surface-dark-lighter rounded-lg overflow-hidden md:border md:border-solid md:border-[#E8E8E8] p-4 flex items-center justify-center min-h-[220px] md:min-h-[340px] lg:h-[400px]`
  and the image itself `object-contain w-full max-h-[280px] md:max-h-full`.
  **The kit and the test page used `lg:min-h-[400px]`; the real class is `lg:h-[400px]` — a fixed height.** Fix before the fidelity test.
- Mobile rows are bordered cards (`border border-solid border-[#E8E8E8] rounded-lg bg-white p-6`), desktop drops the border (`md:border-0 md:rounded-none md:bg-transparent md:p-0`).
- Fields: `heading`; `features[]` of `feature_title`, `subtext` (markdownified), `benefit_1..3` (all three required to render), `anchor_text`, `url`, `image`.
- Images resolve through `partial "functions/resolve-image-path.html"` then `partial "image.html"`; SVGs bypass the image partial.

### Scroll animation convention (replaces the skill's own)

The site already has a scroll system, declared in markup:

```
data-scroll="slide-left|slide-right"  data-scroll-duration="0.7"  data-scroll-trigger=".feature-row"
```

driven by GSAP + ScrollTrigger (`static/websitejs/gsap.min.js`, `ScrollTrigger.min.js`, `gsap-main.js`).
The skill's `data-reveal` / `pu-rv-*` is a **parallel system** and must be reconciled with this before handoff.

## 4. Precedent: the site already ships an animated product-UI scene

`component-library/components/claude-connector-hero/` is a reconstructed Claude-plus-Optmyzr chat UI —
built the way this skill says to build scenes, by the dev team, already in production:

- Namespaced `ozcl-` on every class and id "so nothing collides with site styles" (the skill uses `pu-`).
- Styles and script are **plain static assets**, not inline: `static/websitecss/claude-connector-hero.css`, `static/websitejs/claude-connector-hero.js`.
- All copy and data come from bookshop fields and reach the script through `data-*` attributes — the script stays static and content-free.
- Final-state markup with `role="img"` and a descriptive `aria-label` (field `animation_alt`), the animated frame `aria-hidden="true"` and `data-nosnippet` so invented demo figures stay out of search.
- Demo numbers live in **skip-keys** (`spend`, `uncheck`, `currency_prefix`, `match`) so they are never translated; words live in translatable keys.
- Toggleable per page with `show_animation`.

**This is the template to follow** for playbook step 7 and for `templates/page/`: a scene ships as a
Bookshop component + one CSS file + one JS file under `static/`, with copy as translatable fields.

## 5. Localization

Fully answered — see `site-kit/localization.md`. Headlines: five active languages (en, es, de, fr, jp),
Danish disabled, English at the root with no prefix, Japanese key is `jp`; content mirrors path per
language; 306 translatable keys / 121 skip keys / 27 URL keys in
`scripts/translation-scripts/translation/config.js`; translations produced by the Marketing-OS
localization agent and checked by `scripts/validateTranslations.js`; language switcher is the
`language-picker` component fed by `data/languages.yaml`; hreflang is generated by a partial.

## 6. Discovered during mining — decisions this changes

1. **A live page already exists at `/solutions/optmyzr-ai/`** — `content/english/solutions-new/search/AI-in-Optmyzr.md`, layout `v2-generic-solutions-page`, blocks: hero-solution → animated-trail-banner → features-section → casestudy-section ×3 → cta-section-solutions → faq-section. The test page in `workspace/optmyzr-ai/` targets the same URL. This supplies the **real FAQ content**, the **real CTA text** and the **case-study answer** that README section 7 items 2, 3 and 6 were waiting on, and makes a true fidelity diff possible.
2. **Feature headings are `h3`** (open decision 1 — settled from code).
3. **Image slot height is `lg:h-[400px]`**, not `min-h`. The test page must be corrected.
4. **The site's scroll-reveal is `data-scroll` + GSAP/ScrollTrigger.** The skill's own reveal must defer to it.
5. **Scene text field names already exist** in `translatableKeys` from the connector hero. Reuse before inventing.

## 7. Not yet mined

Tailwind config and design tokens (`themes/…/assets/websitecss/tailwind.config.js`, `marketing_tokens.json`),
full header/footer partials and navbar data, the remaining page types, the image pipeline
(`partials/image.html`, `responsive-img.html`, `scripts/image-compressor.js`), Marketing-OS workflow
(`MKTOS-SDLC.md`, `.claude/`), and the `marketing-edit` skill already in the repo.
