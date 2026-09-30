# Design system

Used in phases 3, 11 and 14. Goal: consume a website design system supplied by the user, map it onto the marketing page, and keep it strictly separate from the look of the product UI that the page demonstrates.

## 1. The core distinction

A marketing page built with this skill contains two different visual languages. They come from different sources, control different things, and must never be mixed.

| | **Marketing page design system** | **Product UI reference** |
|---|---|---|
| What it is | The website's brand and layout rules | How the product experience actually looks in the screenshots and videos |
| Supplied as | The design system the user provides (and the site kit) | The reference screenshots and videos |
| Controls | The page: layout, headings, copy, buttons, cards, navigation, header, footer, scene frames and controls | The reconstructed scene: everything inside the product window |
| Token scope | The site's own classes and tokens, from the kit | `--product-*` custom properties inside `.product-ui`, with `pu-` classes |
| Restyled to match the other? | Never restyled to match the product | **Not restyled to match the marketing brand**, unless the user explicitly asks for a branded recreation |

The product scene stays **visually faithful to its reference**. This applies to the company's own product and to any third-party product shown (for example a chat app, an ad platform or a CRM). Matching the marketing site's brand is not a reason to change how a product looks.

## 2. What a design system may contain, and where each part goes

Design systems vary. Use whatever is supplied and treat the rest as gaps. This table says where each part is used.

| Design system part | Marketing page | Scene frame and controls | Inside product UI |
|---|---|---|---|
| Brand colors | Yes, by role | Yes (frame, caption, controls) | **No** |
| Typography (families) | Yes | Yes (caption, controls) | **No** |
| Font sizes and scale | Yes, desktop and mobile | Caption and control text | **No** |
| Font weights | Yes | Yes | **No** |
| Spacing scale | Yes | Frame padding and gaps | **No** |
| Grid | Yes | Where the scene sits | **No** |
| Container widths | Yes | Width the scene receives | **No**. The product keeps its own design width |
| Border radius | Yes | Frame radius | **No** |
| Shadows | Yes | Frame shadow | **No** |
| Buttons | Yes (CTAs, controls) | Play, pause, replay | **No** |
| Cards | Yes | Frame styling where suited | **No** |
| Navigation, headers, footers | Yes, reused unchanged | No | **No** |
| Breakpoints | Yes | Container behavior at each breakpoint | **No**. Scenes use container-based rules |
| Existing components | Yes, reused for sections | Reused if suitable | **No** |
| Visual guidelines (imagery, icons, tone) | Yes | Yes | **No** |
| Motion guidelines | Page and frame entrance | Frame, controls | **No**. Product motion follows the video (`animation-system.md`) |

"No" means no by default. The only exception is an explicit branded recreation (section 6).

## 3. Sources and precedence

Up to three sources may be present in a run.

1. **The supplied design system**: what the user hands over for this page, in any format.
2. **The site kit** (`site-kit.md`): the bundled snapshot of the site, with its own verified class names and captured patterns.
3. **Optional product design system**: if the user also supplies the design system of the product being demonstrated. It is used only to help build the product theme, and only where the reference agrees with it.

Precedence when sources disagree:

- **Token values** (colors, sizes, spacing): the **supplied** design system wins over the kit, because it is what the user declared for this run. Report every difference and ask when it is material.
- **Class names, patterns, header and footer markup**: the kit wins when its status is verified or observed, because those come from the real site. Supplied names that the kit cannot confirm are marked unverified.
- **Product look**: the reference screenshots and videos always win over any design system. A product design system only fills in what the reference does not show.

If only the kit exists, use it. If only a supplied design system exists (no kit), treat everything except tokens as missing, and follow the gap rules in section 5.

## 4. The mapping process

Do this in phases 3 and 11. It produces a single mapping record, `spec/design-mapping.md`, used to build the page and included in the handoff.

### Step 1. Inventory the sources

List what was supplied and in what form. Recognized forms, with the handling for each:

| Form | Handling |
|---|---|
| Figma variables export (JSON) | Run `scripts/normalize_design_system.py` to get normalized tokens and a stylesheet |
| CSS custom properties or a stylesheet | Read the variables and classes; group them by category |
| Tailwind or theme configuration | Read the theme keys; the utility class names come from it |
| Design-token JSON (for example a standard token format) | Normalize categories and resolve aliases |
| Component library or Storybook | Record component names, variants and states |
| Style guide document, PDF or screenshots | Read it and extract values by hand. Mark them lower confidence |
| A link to the live site | Read the rendered pages for tokens and patterns. Mark them **observed** |

Record the source, date and format of each item.

### Step 2. Normalize into a design system profile

Write the supplied design system into one consistent profile (`spec/design-system.json`), whatever its origin:

```yaml
colors:      { roles: {...}, palettes: {...} }          # raw palettes and semantic roles
typography:  { families, weights, scale: { desktop, mobile }, lineHeights, letterSpacing }
spacing:     { scale }
layout:      { grid: {columns, gutter, margin}, containers, breakpoints }
shape:       { radius, borders, shadows }
components:  { buttons, cards, navigation, header, footer, ... }   # variants and states
patterns:    [ hero, feature-section, cta, faq, ... ]
motion:      { durations, easings, guidelines }
guidelines:  { imagery, iconography, tone, dos_and_donts }
status:      # per item: supplied | verified | observed | unverified | missing
```

Keep original names alongside normalized ones so nothing is lost and the dev team can trace a value back.

### Step 3. Gap and conflict analysis

- **Gaps.** List categories that are missing or partial.
- **Conflicts.** Compare with the kit and report differences in value or name.
- **Inconsistencies.** Duplicate values under different names, inconsistent naming, tokens with no role, scales missing a step.
- **Ambiguities.** Values that are not tied to anything (for example line heights not linked to type sizes).
- **Contrast.** Check the color pairs the page will use against WCAG 2.1 AA.

Resolve gaps using the rules in section 5. Present the important ones at the storyboard checkpoint in plain language ("The design system has no shadow style, so the scene frame will have a simple border instead. Is that okay?").

### Step 4. Map to semantic roles

Raw tokens are not used directly by the page. Map them to **roles** once, and let the page use roles.

| Role | Examples of what it maps to |
|---|---|
| Page background and surfaces | Light and dark surface tokens |
| Text primary, secondary, muted, inverse | Neutral text tokens |
| Accent and brand | Primary brand color and its hover and active states |
| Call to action | Button background, text, hover, active, focus |
| Borders and dividers | Neutral border tokens |
| Feedback | Success, warning, error, info |
| Scene frame | Frame background, border, radius, shadow, caption color |

The page and the scene frame use roles. If a role cannot be mapped, that is a gap.

### Step 5. Map typography

- Assign type scale steps to page roles: display, heading levels, lead, body, caption, eyebrow, button label, control label.
- Use the design system's separate desktop and mobile sizes, and switch at its breakpoint.
- Pair line height and letter spacing with each step. If the source does not tie them, ask or choose the closest documented pairing and mark it unverified.
- Record font loading (weights, formats) and fallback stacks. Check the fonts cover the scripts of the requested languages (`localization.md`).

### Step 6. Map layout

- Use the grid, container widths and spacing scale to build section rhythm: section padding, gaps, alignment.
- Map breakpoints to responsive behavior (`responsive.md`).
- Decide the **scene slot**: which column or container the scene sits in, and the width it receives. The scene scales to that width from its own design width.

### Step 7. Map components and patterns

For every section in the storyboard, find the matching design system component or pattern (header, hero, feature section, CTA band, cards, FAQ, footer). Then:

- **Reuse as supplied.** Use the component with its supplied variants and states.
- **Adapt within the rules.** Change content, not structure or style.
- **If nothing fits,** use the closest pattern and record a **kit gap**. Do not invent a new component or a new navigation, and do not restyle an existing one.
- Headers, navigation and footers come from the design system or kit unchanged.

### Step 8. Map the scene frame

The **scene frame** is the only place the marketing design system touches a scene. It is the container, caption, controls and surrounding space.

- Style the frame from roles: surface, border, radius, shadow, padding, caption typography, control buttons.
- The frame does **not** replace the product window's own container styling. The product's own border, radius and shadow (from the reference) remain inside it.
- Make sure the product UI is legible against the frame and page background. Add frame padding or a border if contrast between the two is weak. Do not tint the product UI.
- A light product UI on a dark page (or the reverse) is fine and expected. Do not invert the product.

### Step 9. Map motion

- **Page and frame:** follow the design system's motion guidelines for section and frame entrance, if it has any. Keep them restrained: the frame or heading may enter once. Do not animate every element (see `animation-system.md`).
- **Product scene internals:** follow the video, not the design system.
- If the design system's guidelines ask for motion the animation system forbids (for example animating every card on scroll), apply them to the frame only and record the difference.
- Use its duration and easing tokens for page-level motion and controls.

### Step 10. Accessibility check

- Contrast of role pairs used on the page and frame.
- Focus indicator style from the design system.
- Touch target size for controls.
- Reduced-motion behavior for page-level animation.

### Step 11. Record the mapping

Write `spec/design-mapping.md`: for each role, component and pattern, the source token or component, the class or variable used, its status, and any gap or assumption. The handoff bundle includes it, so the dev team can check every choice.

### Step 12. Audit

Before validation, scan the page for:

- Hard-coded colors, sizes, radii or fonts that are not tokens.
- Fonts outside the design system, on the page.
- Site tokens or classes inside the product UI.
- Product tokens or classes outside it.
- Invented components, navigation or footers.

Fix them at the owning step.

## 5. Handling gaps

Never present an invented value as part of the design system. Use these rules and record each in the mapping.

| Missing | Approach |
|---|---|
| Brand colors | Stop and ask. The page cannot be built without them |
| Font families | Stop and ask. Do not substitute a brand font silently |
| Type scale | Derive from body size and headings observed in kit patterns, or ask. Mark unverified |
| Spacing scale | Use the kit's or observed section spacing; otherwise a documented 8-point scale, marked as an assumption |
| Grid and container widths | Use the observed page container; otherwise a documented default, marked as an assumption |
| Breakpoints | Use the kit's; otherwise the defaults in `responsive.md`, marked as an assumption |
| Border radius | Use values observed in kit components; otherwise small, neutral radii, marked as an assumption |
| Shadows | Use none, and a border instead, unless the kit shows shadows |
| Buttons and cards | Use the kit's; otherwise build simple ones from tokens and mark a kit gap |
| Navigation, header, footer | Use the kit's. If absent, ask. Never invent |
| Existing components | Note the absence. If the brief genuinely needs a section no component covers, design it per `new-sections.md` and ship it as a Bookshop component with a rationale |
| Visual guidelines | Follow what exists. Generated icons and illustrations must match the measured house style in `icons-and-illustrations.md`, verified with `check_svg_style.py`. Never invent an icon *style* |
| Motion guidelines | Use the animation system defaults for the frame and controls |

## 6. Product UI reference policy

### Default: faithful

- Build the product theme from the analysis (`screenshot-analysis.md`): fonts, colors, radii, shadows, spacing, density, as `--product-*` on the scene root.
- Do not use marketing tokens, fonts or components inside the scene.
- If the product font is unavailable, use the closest available font and record a substitution. Do not switch to the site's font.
- The product theme is independent of the page's light or dark styling.

This applies to the company's own product and to third-party products alike.

### If a product design system is also supplied

Use it to fill in details the reference does not show (an unseen hover color, an exact radius) when it agrees with what the reference does show. Where they disagree, the reference wins. Record the source of each value.

### Branded recreation (only on explicit request)

A **branded recreation** restyles the product experience in the marketing brand. It is a deliberate choice, never a default, and never inferred from "make it match the site".

- **Recognize the request.** The user says the scene should be restyled, in brand, or should not look like the original. A general request to follow the design system is about the page. If it is unclear, ask: "Should the product scene look exactly like the recording, or be restyled in your brand?"
- **What changes:** surface colors, fonts, radii, shadows and icon style, drawn from the marketing design system.
- **What stays:** structure, layout, content, states and behavior, so the scene still shows the same interaction.
- **Record it.** Set `theme.mode: branded` in the scene definition, note it in `approximations`, and confirm it at the scene spec checkpoint.
- **Third-party products.** A branded recreation of a third-party product must not imply it is that product. Remove its name, logo and other marks, and present it as a generic interface. Otherwise keep the scene faithful. Trademarks and likenesses of third-party interfaces are a question for the dev team and legal review, so flag them in the handoff. This is not legal advice.
- **Own product.** Restyle only if the user confirms the marketing brand is meant to apply to the product UI shown.

### Ambiguous cases

| Situation | What to do |
|---|---|
| "Use our design system" | Apply it to the page and frame. Keep the scene faithful. Say so |
| "Make the demo match our brand" | Ask whether they mean the frame and page (yes) or the product UI too (only if explicit) |
| Reference is a third-party product | Faithful, with third-party marks handled as above |
| Reference product already shares the brand | Faithful anyway. It will match by fidelity |
| Reference is low quality and hard to reproduce | Ask. Do not solve it by switching to brand styling |

## 7. Keeping the two systems separate in code

- **Tokens.** The site's own classes and tokens (from the kit) outside the scene. `--product-*` custom properties inside it.
- **Classes.** The site's classes on page and frame markup. `pu-` prefixed classes inside the scene. Never mix them on one element.
- **Scoping.** Scene styles are scoped under `.product-ui[data-scene]`.
- **Isolation.** The scene root sets its own font family, size, line height, letter spacing, color and box model, so nothing is inherited from the page. This matters: page styles often set negative letter spacing on headings, or global text transforms, that must not leak into product text.
- **Containment.** The scene root uses layout containment and its own stacking context, so page styles and scene styles cannot affect each other's layout.
- **Assets.** Product icons and images are inline or scene-local. The site's icon set is not used inside the scene.
- **Frame API.** The frame gives the scene a width, and nothing more.

## 8. Using tokens in the preview and the bundle

- In the preview, load the kit's token stylesheet and use the kit's class names, so markup is identical to the bundle. See `site-kit.md`.
- In the bundle, use the site's classes as recorded, and mark unverified ones for the developer.
- Never write raw hex values, one-off pixel sizes or invented class names for the page. A class the kit does not record is not used.

## 9. Contrast and legibility

- Meet WCAG 2.1 AA: 4.5:1 for normal text, 3:1 for large text and UI components.
- If a pairing fails, choose a passing pair from the same color family and note it. Do not change token values.
- Report failing pairs in the design system to the user. They are the design system's issue, not something to hide.
- Light-only systems stay light. Do not invent a dark theme unless asked.

## 10. Product vertical theming (Optmyzr-specific)

Optmyzr's site has a **per-product-vertical colour system** driven by `body[data-product="<key>"]`. It must be set on **every page under that vertical**, not just solution pages — product pages, landing pages, resource pages and any other page type all receive the same theming.

### The four product keys

| Product | `data-product` | Primary | Dark | Light |
|---|---|---|---|---|
| Search | `search` | `#069ba2` teal | `#05747a` | `#e6f5f6` |
| Amazon | `amazon` | `#f29c07` amber | — | — |
| Social | `social` | `#0d9dee` blue | — | — |
| Ecommerce | `ecommerce` | `#b8a2ed` lavender | `#8665c9` | `#f4effb` |

Search is the default (`:root` shares its values), so a Search page needs no override block.

### The override-block pattern

HTML is written with **Search (teal) Tailwind classes** everywhere. A CSS override block in `build.py` re-maps them to the product colour at render time. This keeps the HTML clean and makes all product pages structurally identical.

For **Ecommerce**, the site's Tailwind sheet omits several purple utility classes that must be declared manually in the override block. Discovered while building `workspace/google-shopping/`:

| Class | Purpose | Fix |
|---|---|---|
| `bg-colorPrimaryPurpleLight` | Solutions mega-menu selected tab background | Declare → `var(--product-light)` |
| `bg-colorPrimaryPurpleNormal` | Solutions mega-menu selected tab fill | Declare → `var(--product-primary)` |
| `text-colorPrimaryPurpleNormal` | Unselected tab text colour | Declare → `var(--product-primary)` |
| `text-textonteallight1` | Resolves to `var(--product-dark)` — turns nav items purple | Reset to neutral `#2d3a48` |
| `group-hover:text-teal` bare selector | Always-on (class is always present); nav items always purple | Scope to `.group:hover .group-hover\:text-teal` |

### Ecommerce purple scale

Custom variables added to the ecommerce override block (`--product-deeper` and `--product-darker` are not in the site CSS):

| Step | Hex | Variable |
|---|---|---|
| `#f4effb` | lightest | `--product-light` |
| `#dfd6f9` | hover-light | `--product-light-hover` |
| `#b8a2ed` | mid | `--product-primary` |
| `#8665c9` | dark | `--product-dark` |
| `#6a36c1` | dark-hover | `--product-dark-hover` |
| `#4B288F` | deeper *(custom)* | `--product-deeper` |
| `#2e175b` | darkest *(custom)* | `--product-darker` |

CTA colours (dark theme): Start Trial `#6a36c1`, Book A Demo `#2e175b`. Hover: one step toward `#4B288F` for both. Hero: Start Free Trial `#4B288F`, Book A Demo `#dfd6f9` bg + `#2e175b` text.

### Two CTA sections — different classes

Two CTA sections appear on every solution page. They have **different HTML classes** and need separate CSS overrides:

| Section | Class on the card element | Ecommerce override |
|---|---|---|
| Mid-page "Connect your feed" (`c-cta-section-solutions`) | `.bg-surface-dark-dark` | Already dark grey — no change needed |
| Footer "Experience Optmyzr" (inside `<footer>`) | `.bg-tealdark3` | `footer .bg-tealdark3 → #22262b` (dark neutral, NOT purple) |

Scope to `footer .bg-tealdark3`, not the bare class — the generic rule maps `bg-tealdark3 → #2e175b` (dark purple) for header bars and other uses.

### Log In button (header)

The button carries `bg-teal-light text-teal-dark`. On ecommerce this naturally resolves to `#f4effb` bg + `#8665c9` text — a correct secondary CTA. **Never add `background-color:transparent`** to the login override; it strips the secondary-CTA appearance.

### `getInitialTab()` in the captured header

The Solutions mega-menu has `getInitialTab(){return this.tabs.findIndex(e=>e.key==="search")}` — this function body appears **4 times** (Solutions + Resources × desktop + mobile). To pre-select a different product, replace the **function body** only:

```python
h = h.replace(
    'getInitialTab(){return this.tabs.findIndex(e=>e.key==="search")}',
    'getInitialTab(){return this.tabs.findIndex(e=>e.key==="ecommerce")}')
```

Never replace `this.selected = this.getInitialTab();` — it appears 4 times and `str.replace()` hits all of them, breaking the Resources mega-menu state.

### Localisation in `file://` preview

`window.__translationMap` with relative paths (e.g. `/es/solutions/google-shopping/`) fails under `file://` because the browser resolves them against `file:///`. Fix: set `__translationMap = {}` and define `window.showLangFallbackToast(lang)` to open the live-site equivalent in a new tab. The `languagePicker` in `chrome-scripts.html` calls `showLangFallbackToast` automatically when a language has no mapping.

## 11. Reuse across brands and sites

Nothing brand-specific belongs in this skill. Everything brand-specific comes from a supplied design system and the site kit. For a new site: ingest its design system (steps 1 to 3), build or refresh its kit (`site-kit.md`), then run the same mapping.

## 12. Checklist

- Every supplied source is inventoried, with format and date.
- The profile is normalized, with a status per item.
- Gaps, conflicts and ambiguities are listed and, where material, confirmed with the user.
- Roles, typography, layout, components, frame and motion are mapped, and recorded in `spec/design-mapping.md`.
- The product UI is faithful to its reference, with `--product-*` styling and no site tokens inside it.
- Any branded recreation is explicit, confirmed, recorded, and handles third-party marks.
- Nothing is hard-coded, invented or leaking between scopes.
- Contrast passes, or failures are reported.

## 13. Common mistakes

- Restyling the product UI in the brand because "it should match the site".
- Letting page letter spacing or text styles leak into the scene.
- Using the site's font or button style inside the scene.
- Inventing a header, footer, navigation or component.
- Filling design system gaps with invented values and calling them the system's.
- Treating "use our design system" as a request for a branded recreation.
- Animating every page element because a motion guideline exists.
- Dropping the product's own container styling in favor of the frame's.
