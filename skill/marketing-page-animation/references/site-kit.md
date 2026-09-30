# Site kit

Used in phases 3, 11, 13 and 14, and whenever a page needs something from the website. Goal: let someone with no repo access build pages that look and behave like the real site, by giving the skill a **snapshot of the site's design and conventions**.

The kit lives in `site-kit/` next to this skill. Its `MANIFEST.md` lists every item with a status. Read it before starting a page.

## Use the page type's own components, not a scaffold from another page

Every page type has its own hero and its own features block, and they are **not**
interchangeable. `hero-solution` is left-aligned with a right-hand image and teal buttons;
`social-hero` is centred, has blue buttons, a three-image band and a customer logo strip.
Pouring product copy into the solution components produces a solution page wearing the wrong
words — which looks plausible until someone who knows the site sees it.

This is easy to do by accident when reusing a build from a previous page. The check that
catches it takes one line: read the section class names out of the **built** page and compare
them with the sequence in `page-types.json`.

```
expected (product, social route): c-social-hero, c-social-features-section, ...
got:                              c-hero-solution, c-features-section, ...
```

Do that before reviewing anything else about the page. Content can be fixed later; the wrong
component set means rebuilding.

## What the kit contains

| Item | Purpose | Source |
|---|---|---|
| Design tokens | Colors, type sizes, spacing, font families and weights | Design-token export, normalized by the token script |
| Token class map | The site's utility class names for each token (for example the class used for a primary color or a headline size) | Existing components or the site's generated config |
| Fonts and breakpoints | Type families, responsive breakpoints | Public site CSS, or the dev team |
| Header and footer | Real navigation, links, labels, logo usage | Rendered public pages |
| Section patterns | Hero, feature section, CTA band, card grid, FAQ and similar, as markup with their token classes | Rendered public pages |
| Animated patterns | How existing animated sections behave and are marked up | Rendered public pages, or the dev team |
| Languages and tone | Active languages, URL prefixes, tone per language, brand names to keep untouched | Dev team or localization notes |
| Translatable field names | Field names the localization process treats as translatable | Dev team (configuration file) |
| Component blueprints | The field structure of existing components | Dev team |

## Page structures

Before proposing a storyboard, pick the closest page type in `site-kit/page-types.md` (solution page, demo-led solution page, homepage, pricing, listing, demo-request) and follow its section order, container, spacing, FAQ and CTA conventions. Section detail is in `site-kit/patterns/`. Deviations go in the handoff.

## Status labels

Every kit item carries one of:

- **verified**: taken from the real code, from the design team's own token export, or confirmed by a developer.
- **observed**: read from the public rendered site. Accurate for looks, not necessarily for how the code is structured.
- **unverified**: taken from documentation or inference. Use, but list it in the handoff.
- **missing**: not in the kit yet.

## Using the kit

1. **Read `MANIFEST.md`** and note anything missing or unverified that this page needs. Tell the user early if a needed item is missing.
2. **Assemble from kit patterns.** Header, footer and section shells come from the kit unchanged. Fill them with the page's content.
3. **Use the site's own classes and stylesheet.** Write page markup with the class strings recorded in `site-kit/patterns/` and `site-kit/captured/` (copied from the live pages), and load the site's real stylesheet in the preview (`captured/README.md` has the URL). Do not write your own CSS for the page, raw hex values or invented class names. Only the product UI inside a scene has its own scoped theme. A class that the site never uses is not in the stylesheet, so a page must reuse classes seen on live pages.
4. **Never invent the site's conventions.** Header, footer, navigation, menus, forms, legal text, the section order of a known page type and its hero all come from the kit unchanged. Do not make up navigation items, footer links, forms or legal text, and never "improve" a component that already exists.
   There is one bounded exception. When the brief needs a **content section** that no component covers, designing it is the job, not a workaround — work the decision ladder in `new-sections.md`, deliver it as a Bookshop component with a rationale, and record a **kit gap** in `spec/`. A new section may say something new; it may not say it in a new visual language.
5. **Stay current.** If the kit's snapshot date is old, say so and recommend a refresh before an important page. Real pages may have changed.

## Kit and a supplied design system

When the user also supplies a design system, `design-system.md` decides precedence: supplied **token values** win over the kit's, the kit's verified or observed **class names and patterns** win over supplied names, and the product look always comes from the references. Report differences, and record the result in `spec/design-mapping.md`.

## Building and refreshing the kit

The kit is maintained by the skill's owner, not by each user.

1. **Tokens.** Run the token script on the latest design-token export. It writes normalized tokens and a stylesheet.
2. **Rendered patterns.** Capture the header, footer and representative sections from the public site (rendered HTML, the CSS it uses, fonts). Record the source URL and capture date for each.
3. **Class map.** Record the class names for each token as they appear in the rendered pages. Mark a class **observed** until a developer confirms it.
4. **Developer items.** Ask the dev team for the items only they can give: the translatable field list, component blueprints, an animated component's source, the language tone rules. Mark them **verified**.
5. **Update `MANIFEST.md`** with statuses and the capture date.
6. **Confirm no private data.** The kit contains only public information and design assets. No customer data, credentials or internal URLs.

## Product line theming

The site has four product lines, each with its own color theme activated by setting `data-product` on `<body>`:

| Product | `data-product` | Primary | Secondary | Accent (scene) |
|---|---|---|---|---|
| Search | `search` | Teal `#069ba2` | Lime | `--product-primary:#069ba2` |
| Amazon | `amazon` | Yellow `#f29c07` | Fuchsia | `--product-primary:#f29c07` |
| Social | `social` | Blue `#0d9dee` | Orange | `--product-primary:#0d9dee` |
| Ecommerce | `ecommerce` | Purple `#b8a2ed` | Mustard | `--product-primary:#b8a2ed` |

When `data-product` is set, the site's stylesheet maps `--product-primary`, `--product-dark`, `--product-light`, `--product-darker`, `--product-btn`, `--product-btn-hover` and related variables to that product's palette. Utility classes like `product-btn-primary`, `product-text-primary`, `product-bg-light` then pick up the correct color automatically.

**In the preview page**, set `<body data-product="ecommerce">` (or the relevant product) so the header tab highlight, product dropdown and any `var(--product-*)` references render in the correct theme. The scene's own scoped accent palette (on `.product-ui`) is separate and comes from the reference measurements, not from `--product-*` — see `references/new-sections.md` for the namespace boundary.

**In the handoff**, note the `data-product` value so the dev team sets it on the live page's `<body>`.

## Known limits

- The public site shows what components look like, not how their fields are structured. Bundle output that depends on field structure is therefore a draft until a developer verifies it.
- Classes that appear in no rendered page may be missing from the site's stylesheet. Use only classes the kit records.
- The kit does not know about pages published after its capture date.
