# Building the site kit from the repo (one time, by the skill owner)

Goal: people who use the skill have **no repo access**, yet the page they get is **the same as an existing page on the site**. So the repo is mined once, and everything needed is baked into the kit that ships with the skill.

## What is mined, and what it becomes

| Mine from the repo | Becomes in the kit | Why users need it |
|---|---|---|
| Bookshop component library (each component: blueprint fields, Hugo template, styles) | `site-kit/components/<name>.html` (the rendered markup with placeholders) + `components.json` (name, fields, required/optional, sample values) | The page is assembled from the same components, so markup and classes match exactly |
| Page layouts and content front matter, plus real pages | `site-kit/page-types.json` (ordered sections per page type, required/optional, repeat rules, which components each section may use) | "A solution page is these sections in this order" is enforced, not guessed |
| Compiled CSS and Tailwind config (tokens, plugin classes, safelist) | `site-kit/css/` snapshot + class map with a used/unused flag | Previews render with the real styles; the skill only uses classes that exist |
| Fonts, icons, shared images (logo, badges, CTA art) | `site-kit/assets/` (or absolute URLs) | Header, footer, CTA look identical |
| Header, footer, language picker, mega menu data (menus come from data files) | `site-kit/chrome/` (full versions, not simplified) | Same navigation everywhere |
| Translatable-key config, language list, URL rules, i18n helpers | `site-kit/localization.md` | Bundle output follows the site's own localization (the discovery table in `references/localization.md`) |
| Script loading (Alpine, GSAP, animation scripts) | `site-kit/scripts.md` | Animated scenes load the way the site loads components |
| One real animated component | `templates/page/` starter | Shows how scene markup is registered |

## The rule that guarantees the same output

**Fidelity test.** For each page type, take an existing live page, extract its content (headings, copy, images, FAQ items), feed that content through the kit's components and page-type definition, and compare the result with the live page:

1. DOM comparison of the section tree (same components, same order, same classes on each element).
2. Visual comparison at 390, 768, 1024, 1440 px (pixel diff with a small tolerance, ignoring images and dates).

A page type is marked **verified** in `MANIFEST.md` only when its fidelity test passes. Users then build new pages with a structure that has already been proved to reproduce a real page. Re-run the tests whenever the kit is refreshed.

## Output stays repo-free for users

- Preview: assembled from `components/` + the CSS snapshot. No repo, no build.
- Handoff bundle: content in the site's field format (from `components.json`) plus the scene components. The dev team drops it into the repo.
- Keeping the kit fresh: the kit records the site commit it was built from. A refresh script (planned) re-runs the mining and the fidelity tests and reports drift, so the skill can warn "kit is N weeks old".

## What we need from the repo (read-only is enough)

Component library folder, layouts, `hugo`/Tailwind config and compiled CSS output, data files for menus/footer, i18n configuration, and one animated component. See also `docs/consistency-report.md` (dev-team message).

## Order of work once access is given

1. Inventory: list components, layouts, page types actually used by pages.
2. Extract components and page types into the kit format above.
3. Fidelity tests for solution, homepage, pricing, listing, demo-request pages.
4. Replace the "observed" statuses in `MANIFEST.md` with "verified" per item.
5. Re-run the Optmyzr AI page through the new kit and confirm it matches the site's structure exactly.
