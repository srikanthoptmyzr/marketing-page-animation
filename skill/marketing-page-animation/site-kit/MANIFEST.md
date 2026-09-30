# Site kit manifest

Snapshot of one website's design and conventions, used by the skill to build pages that look native without repo access. Status labels: **verified**, **observed**, **unverified**, **missing** (see `references/site-kit.md`).

Kit for: Optmyzr marketing website (first reference site)
Snapshot date: not yet captured for rendered patterns. Tokens taken from the Figma variables export supplied on 2026-09-29.

| Item | Status | Location | Notes |
|---|---|---|---|
| Design tokens (color, spacing, type sizes, fonts, weights) | verified (design team's export; not yet compared with the rendered site) | `tokens/design-tokens.json`, `tokens/site-tokens.css` | Single Light mode. No radii, shadows, breakpoints or motion tokens in the export |
| Line-height and letter-spacing pairing to type steps | missing | | Export gives t-shirt sizes not tied to a step. Confirm with design |
| Token class map (utility class per token) | observed (live computed styles; `tokens/class-map.md`) | | Examples known only from developer agent documentation, for instance classes for a teal primary background, a dark surface, a desktop H2 size, a headline font family, a 1440 max width and horizontal padding. Needs confirmation from rendered pages or code |
| Fonts (DM Sans headlines, Inter body) and font loading | **verified** | `tokens/breakpoints-and-fonts.md` | `font-dm` = DM Sans for headlines, `font-body`/`font-display` = Inter. Files at `static/websitefonts/`. **No CJK coverage** though Japanese is active; fonts are not CORS-enabled, so local previews fall back to system fonts |
| Breakpoints | **verified** | `tokens/breakpoints-and-fonts.md` | Seven: below-360, xss 376, sm 640, md 768, lg 1024, xl 1280, desktop-lg 1540. The old 767-only assumption was incomplete; the viewport matrix in `responsive.md` misses 640, 1280 and 1540 |
| Header and navigation | **verified** — the real header captured verbatim from the live site (~62 KB), with the product switcher, all mega menus, language picker and mobile menu, plus the inline Alpine data scripts it depends on | `captured/header.html`, `captured/chrome-scripts.html`, `captured/README.md` | Refresh with `scripts/capture_chrome.py`. The old `header.simplified.html` is kept only as a fallback |
| Footer | **verified** — the real footer captured verbatim (~25 KB), including the trial CTA card and the language picker | `captured/footer.html` | Refresh with `scripts/capture_chrome.py` |
| Site stylesheet | **verified** — resolved at build time, never hardcoded, and cached in the kit | `captured/site-css.json`, `scripts/resolve_site_css.py` | The hash changes on every deploy. Subresource integrity is stripped for the kit copy: an integrity-checked cross-origin stylesheet is blocked and silently unstyles the preview |
| Section patterns (hero, feature, CTA, case study, FAQ, marquee) | observed. Hero, feature row, marquee and CTA markup copied from live pages (see `patterns/solution-page.md` and `captured/`) | `patterns/solution-page.md`, `patterns/faq-accordion.md` | Homepage-only sections not read in detail (`patterns/other-pages.md`) |
| Logo strip | observed. Captured verbatim from the live homepage; 24 divs balanced, 18 `<img>` | `patterns/logo-strip.html` | Lives inside the `hero` component and is copy-pasted into `social-hero`/`hero-demo` — that repetition is the convention |
| Icon and illustration house style | verified against 23 live assets. Three icon families (outline / filled badge / solid glyph), colour by role, stroke 7-10% of grid | `references/icons-and-illustrations.md`, `scripts/check_svg_style.py` | Illustration canvases are slot-sized, not a house grid; the lighter tint ladder is observed-only |
| Page types and which structure to follow | **verified** (v4: section sequences derived for **every** composed page type, not only solution) (repo `main` @ `c9ac095`, 2026-09-29): all 80 layout templates classified by authoring model, section order and required/optional derived from every English page's `content_blocks`, creatable types cross-checked against 64 CloudCannon collections and 23 creation schemas | `page-types.md`, `page-types.json` (v3), `docs/repo-inventory.md` | 21 page types catalogued with a routing table from the brief's wording. Two silent traps recorded (product and content-hub schemas declare `content_blocks` their layouts never render) |
| Animated patterns (Slack solution page) | observed (layout and classes; animation code not read) | `patterns/demo-led-solution-page.md` | Hard-coded hex values on that page |
| Active languages, URL prefixes, tone rules, brand names to keep | **verified** | `localization.md` sections 1 and 4 | `config/_default/hugo.toml` confirms en/es/de/fr/jp active and `disableLanguages = ["da"]`. Per-language tone rules from `.claude/agents/mktos-localization.md` |
| Localization mechanism (discovery answers: language definition, content/data/i18n layout, translation process and parity check, language switcher, URL and SEO rules, helpers, font coverage, RTL) | **verified** (repo `main` @ `c9ac095`) | `localization.md` | Whole discovery table answered. Five active languages (en, es, de, fr, **jp**), Danish disabled, English at root with no prefix. CJK font coverage per weight is the one item still only observed |
| Translatable field names | **verified** | `localization.md` section 3 | `scripts/translation-scripts/translation/config.js`: 306 `translatableKeys`, 121 `skipKeys` (which also halt recursion), 27 `urlReplaceKeys`. Scene UI labels already exist in the list from `claude-connector-hero` — reuse before inventing |
| Component blueprints | **verified** — all **90** captured (83 used by content, 0 missing; coverage measured, see `components/CATALOGUE.md`) into `components/` with their real templates, field lists and per-field localization status | `site-kit/components/` (+ `README.md`) | Refresh with `scripts/capture_component.py --repo <checkout> --all`. Found 65 distinct copy fields outside the site's translatable-key list; see the README for why the script and agent translation paths disagree |


## Product vertical theming

| Item | Status | Location |
|---|---|---|
| `data-product` attribute system (Search / Amazon / Social / Ecommerce) | **verified** — read from live site CSS and proved in the Google Shopping build (2026-09-30) | `references/design-system.md` section 10 |
| Ecommerce purple scale + custom `--product-deeper` / `--product-darker` variables | **verified** | `references/design-system.md` section 10 |
| Missing Tailwind purple utility classes (must be declared manually in `build.py`) | **verified** — confirmed absent from the purged stylesheet by `check_classes.py` | `references/design-system.md` section 10 |
| Footer CTA card class distinction (`bg-tealdark3` vs `.bg-surface-dark-dark`) | **verified** | `references/design-system.md` section 10 |

**Rule:** theming applies to **all pages in a product vertical**, not just solution pages — product pages, landing pages, resource pages and any other page type all carry the same `data-product` attribute and override block.

## Shipping this kit as an organization skill

The kit is **self-sufficient**: a page can be built with no repo checkout and no internet.

| What a page build needs | Where it comes from |
|---|---|
| Component markup and fields | `components/` — all 90, captured |
| Header, footer, promo banner, chrome scripts | `captured/` — verbatim from the live site |
| Section order per page type | `page-types.json` (21 types) |
| Languages, key lists, URL rules | `localization.md` |
| Breakpoints, fonts, tokens | `tokens/` |
| The site stylesheet URL | `captured/site-css.json`, refreshed when online, cached when not |

**Exactly one script needs a repo checkout:** `scripts/capture_component.py --repo`. That is a
maintainer tool for refreshing the kit, never part of building a page. `capture_chrome.py` and
`resolve_site_css.py` need the internet but fall back to what is already captured.

Everything a user runs — `preflight.py`, `extract_frames.py`, `prepare_image.py`,
`validate/leak_scan.py`, `validate/validate_scene.py`, `validate/check_page.py` — runs from the
skill folder alone.

**Package:** zip this skill's folder with `SKILL.md` at its root. Currently 2.5 MB, 345 files.

**Refresh cadence.** The kit records the commit it was mined from (`c9ac095`). The site will
move on: re-run `capture_chrome.py` and `capture_component.py --repo --all` when the chrome or
the component library changes, and re-check `page-types.json` if new page types appear.

## Fidelity

A page built from this kit alone was compared with the live `/solutions/monitoring/` at 1440:
**108 of 108 computed properties identical, section sequence identical, 0 differences**
(`docs/fidelity-test-explorer.md`, 2026-09-30). That is what "verified" in the table above now
rests on for the solution page type.

Not yet diffed: the other six breakpoints, and the case-study and product page types.

## Refresh log

- 2026-09-29: tokens added.
- 2026-09-29: page types, header/footer, section patterns, FAQ, demo-led page and token class map added from live rendered pages (observed, not code).
- 2026-09-29: section sequences derived for every composed page type. Case study found to be as prescriptive as the solution page (4 sections, 40/40 pages). Component coverage measured: 83 used by content, 90 captured, 0 missing.
- 2026-09-29: real header, footer, promo banner and the chrome's inline Alpine scripts captured verbatim; `capture_chrome.py` added; previews no longer use a hand-simplified header.
- 2026-09-29: all 90 components captured into `components/`; `capture_component.py` and `resolve_site_css.py` added; the preview stylesheet is now resolved at build time instead of pinned.
- 2026-09-29: **read-only repo access granted.** Mined `Optmyzr-Engineering/marketing-website` @ `c9ac095`. Page types and localization flipped to verified; `localization.md` created; `page-types.json` rewritten to v3; inventory in `docs/repo-inventory.md`. Still to mine: Tailwind tokens, full header/footer and navbar data, image pipeline, Marketing-OS integration.
