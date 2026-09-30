# Hugo and Bookshop target

> **How this file is used.** In Mode A (no repo) this file defines the *shape* of the handoff bundle's component and content files. In Mode B (inside the repo) files are written directly into the repo.
>
> **Status: verified** against `Optmyzr-Engineering/marketing-website` @ `c9ac095` (2026-09-29). Concrete paths, the component triplet and the script convention below were read from the repo, not inferred. Where this file and a newer repo state disagree, the repo still wins.

Used in phases 7, 9, 11 and 13. Goal: deliver scenes and pages in the shape the site already uses, so the result is editable by the team, localizable, and passes the existing build and review gates.

Conventions below were read from the repo. Re-check them whenever the kit is refreshed; where this file and the repo disagree, the repo wins.

## Confirm the repo

Expect, and verified present:

| What | Where |
|---|---|
| Hugo config with the language list | `config/_default/hugo.toml` (also `staging/`, `production/`) |
| Bookshop component library, 90 components | `component-library/components/<name>/` |
| Theme layouts and partials | `themes/optmyzr-marketing-v2/layouts/` |
| Tailwind config | `themes/optmyzr-marketing-v2/assets/websitecss/tailwind.config.js`, tokens in `marketing_tokens.json` |
| Per-language content, data, UI strings | `content/<lang>/`, `data/<lang>/`, `i18n/<lang>.toml` |
| CMS schemas and collections | `.cloudcannon/schemas/` (23 creation templates), `cloudcannon.config.yml` (64 collections) |
| Static scripts and styles | `static/websitejs/`, `static/websitecss/` |
| Marketing-OS agents, commands, workflow | `.claude/` |

The repo root `layouts/` is empty on purpose — everything lives in the theme. If these are missing, stop and ask which stack to target.

## Reuse before you build

1. List `component-library/components/`. Read the blueprint and template of the closest candidates.
2. Read the existing animated components before building anything:
   - **`claude-connector-hero`** — a full reconstructed chat UI with a scripted animation. This is the precedent to follow (see "How the site already builds a scene" below).
   - `animated-trail-banner` — the looping marquee strip used on every solution page.
   - `animated-images` — simple image transitions.
   They may already provide typing, reveal or loop behavior you can reuse or extend.
3. Compose the scene from existing components where possible. Build a new component only for the product-UI scene itself, which is what the site does not have.
4. Record the reuse-versus-new decision per scene in `scenes.json`, and say why in the checkpoint summary.

## A scene is a Bookshop component

A component is a triplet in `component-library/components/<name>/`:

- `<name>.bookshop.yml`: CMS metadata, `spec` with a label and structure, a `blueprint` with a default for **every** field, and `_inputs` for field types.
- `<name>.hugo.html`: the Hugo template. Reads fields from the block context.
- `<name>.scss`: component styles. In practice almost every one is a one-line stub — styling is Tailwind utility classes in the template. Do not put scene CSS here; see below.

Rules:

- The folder name, the file names and the page's `_bookshop_name` must match exactly. A mismatch fails silently or breaks the build.
- Every field the template reads must exist in the blueprint.
- All visible text is a **field** (or an `i18n` key for small UI labels), never hard-coded in the template. This is what makes it translatable.
- Use existing field names for text wherever possible. Localization only translates fields whose names appear in the site's translatable key list, so an unusual field name is silently left untranslated. Read the list first (see `localization.md`). If a new field name is needed, that is a dev-team change to configuration: flag it, do not edit it.
- Name a new scene component after what it shows, and check the name does not collide with an existing component.
- Copy the naming, indentation and field-structure style of a sibling component.

## Binding to a page

A page uses the component through `content_blocks` in English front matter:

```yaml
content_blocks:
  - _bookshop_name: <component-folder-name>
    heading: "..."
```

- New pages start from the matching schema in `.cloudcannon/schemas/` when one exists, and mirror a sibling page's front matter.
- Front matter is YAML. Keep indentation and quoting valid.
- New content is publish-ready: `draft: false`, unless the user asked for it to be staged. Never flip a draft to make a build pass.
- Preserve shortcodes and template expressions exactly.

## Where files go

| What | Where |
|---|---|
| Scene component (template, blueprint, styles) | `component-library/components/<name>/` |
| Scene player and scene scripts | `static/websitejs/<name>.js` |
| Scene stylesheet | `static/websitecss/<name>.css` |
| Page copy and block content (English) | `content/english/<section>/...` |
| Small UI labels | `i18n/en.toml`, used as `{{ i18n "key" }}` |
| Structured lists and data | `data/en/...` |
| Images that must remain images (photos, logos) | `static/...` |

Never write scene work into configuration, the CMS config, module files, build scripts, or the design-token source and its generated Tailwind config.

## Scripts and security

- Put JavaScript in asset files, not inline in templates or markdown. Follow the existing pattern for loading component scripts. If none exists, ask the dev team how scripts should be wired rather than inventing one.
- The site allows raw HTML in markdown, which reviewers treat as a risk. Do not embed scenes as raw HTML, `<script>` tags or inline event handlers in content files. Scenes belong in components.
- Inline SVG inside a component template is fine.

## Localization interplay

Scene text lives in English fields and `i18n` keys, is rendered by Hugo, and is then translated by the site's normal per-language process. The animation reads the rendered text from the page. See `localization.md`.

## Design tokens interplay

Use the site's Tailwind token classes for the surrounding page. Only use classes already present in sibling components, because unseen classes can be purged and will not render. Product-UI colors that are not site tokens live in the component's scoped stylesheet. See `design-system.md`.

## Build and preview

The site's own build check and live preview are the authority. See `validation.md`.

## How the site already builds a scene (the precedent to copy)

`component-library/components/claude-connector-hero/` is a reconstructed Claude-plus-Optmyzr chat UI, built by the dev team and live on `/solutions/optmyzr-ppc-connector-for-claude/`. It follows the same method this skill describes, so **match it rather than inventing a parallel convention**:

| What it does | Why it matters here |
|---|---|
| Every class and id is namespaced `ozcl-` "so nothing collides with site styles" | The skill's `pu-` prefix serves the same purpose. Keep scenes fully namespaced |
| Styles and script are **plain static assets**: `static/websitecss/claude-connector-hero.css`, `static/websitejs/claude-connector-hero.js` | This is where `scene-player.js` and `scene-player.css` belong. No inline scripts, no component-level SCSS |
| All copy and data come from bookshop fields and reach the script through `data-*` attributes, so the script stays static and content-free | Exactly the skill's content/spec split. Never bake copy into the script |
| The component has only two files — `.bookshop.yml` and `.hugo.html`, no `.scss` | A scene component does not need a SCSS stub |
| The stage carries `role="img"` and a descriptive `aria-label` from a translatable `animation_alt` field | Use the same accessibility shape, with the same field name |
| The animated frame is `aria-hidden="true"` and `data-nosnippet` | Keeps invented demo figures out of search results and assistive tech |
| Demo numbers live in **skip-keys** (`spend`, `uncheck`, `currency_prefix`, `match`) while words live in translatable keys | Words translate, data does not. Split scene fields the same way — see `localization.md` section 3 |
| A `show_animation` boolean lets a page turn it off | Give scene components the same switch |

Its field names are already in the site's translatable-key list (`chat_title`, `greeting`, `composer_placeholder`, `reply_text`, `col_term`, `apply_label`, `done_title`, …). **Reuse those names before proposing new ones.**

## Reuse the site's scroll animation, do not add another

The site already reveals sections on scroll, declared in markup and driven by GSAP + ScrollTrigger (`static/websitejs/gsap.min.js`, `ScrollTrigger.min.js`, `gsap-main.js`):

```html
data-scroll="slide-left"  data-scroll-duration="0.7"  data-scroll-trigger=".feature-row"
```

`features-section` uses `slide-left` on the text half and `slide-right` on the image half, alternating per row. A handed-off scene must use this convention for its section reveal. The player's own `data-reveal` / `pu-rv-*` mechanism is for the **preview only**, where the site's GSAP is not loaded; it must never ship in the bundle alongside `data-scroll`, or a section animates twice.
