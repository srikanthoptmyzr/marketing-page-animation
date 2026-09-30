# Designing a new section

Used in phases 3 and 11, whenever the brief asks for something the component catalogue has no
match for.

The catalogue was built from pages that were making *other* arguments. A brief that says
something new will eventually need a section that says it. Reaching for the nearest existing
component and pouring the wrong content into it is how a page ends up looking plausible and
reading wrong. When nothing fits, designing the section is the job — not a workaround.

This is a narrow licence. Read "What this never licenses" at the bottom before using it.

## 1. The decision ladder

Work down it. Stop at the first rung that holds.

| Rung | Test | Action |
|---|---|---|
| 1. Exact | A component exists whose fields match the content | Use it. Nothing else to decide |
| 2. Adapt | A component's *structure* fits but its labels or field count don't | Use it, change the copy, leave the markup alone |
| 3. Recompose | Two existing components, side by side, say it | Use both. Two honest sections beat one invented one |
| 4. Design | None of the above, and the content genuinely carries the brief | Design it, per this file |
| 5. Cut | The section restates something the page already said | Cut it and say so in the handoff |

Rung 5 is real and under-used. Before designing anything, check the storyboard for a section
that already makes the same point. Two sections arguing the same thing weaken each other.

## 2. Step one — name the archetype

Do not start from layout. Start from what kind of section it is. Almost everything a marketing
page needs is one of a dozen archetypes, and the site already has a house treatment for most of
them. Using the house treatment is what makes a designed section look like it belongs.

| Archetype | The job it does | House precedent to follow |
|---|---|---|
| Scale / stats proof | A few figures that establish size or maturity | `team-bynumbers` — card row, **one icon per figure**, icon bleeding past the top-right corner |
| Social proof | One named customer vouching, with a rating | `testimonial-section` — company logo, single amber star + number, pattern image behind the heading |
| Trust strip | Logos that borrow credibility, no claim attached | The strip inside `hero` (§6) |
| Capability grid | The product's main abilities, each with a visual | `features-section` / `social-features-section` |
| Audience split | "Who this is for", 3–5 named roles | `teams-section` |
| Process | Ordered steps where the order carries meaning | `animated-trail-banner` |
| Outcome / result | What changed for one customer, with numbers | `results-section`, `result-details-section` |
| Objection handling | Questions that block a decision | `faq-section` |
| Ecosystem | What it connects to | Partner logo treatment in `bynumbers-section` |
| Conversion | The ask | `cta-section-solutions` |

If the content maps to an archetype, you are **not designing from scratch** — you are rebuilding
a known treatment with new content. That is rung 4 at its safest, and it is where most of these
land. Genuinely novel archetypes are rare; suspect yourself when you think you have one.

Write the archetype name into the storyboard. A section whose archetype you cannot name is a
section whose purpose is not yet clear, and no amount of layout will fix that.

## 3. Step two — choose the representation

Two questions decide the form, in this order:

1. **What is the reader meant to do with this?** Scan it, compare within it, or read it through?
2. **What is the one thing they should still remember two sections later?**

Then match the shape of the content to the shape of the section:

| The content is | Represent it as | Because |
|---|---|---|
| 3–6 short figures with units | A card row, one icon per card | Figures are scanned, not read; the icon gives each a handle |
| 3–5 named audiences | Columns or tabs, one per audience | The reader self-selects; they should find their own row fast |
| An ordered sequence | A numbered trail | Order is the content. A grid destroys it |
| Two states compared | Side by side, same row | Comparison needs adjacency, not proximity |
| One strong quote | A single block with logo and rating | One quote at full size outperforms four at quarter size |
| Many quotes | A carousel | |
| A capability with a UI | Copy beside a scene | This is the page's main job — see `scene-composition.md` |
| One idea with no data | A sentence in the neighbouring section | Not every paragraph in a brief is a section |

**Anti-patterns**, each of which has shipped on somebody's marketing page:

- A row of equal-weight cards where one item actually matters more than the rest.
- An illustration that restates the headline instead of adding to it.
- Six cards because the brief had six sentences.
- A section whose entire content is one claim, given a full band of vertical space.

## 4. Step three — style it from the design system

This is where designed sections break, and it breaks silently.

### The constraint

The site ships **one generated stylesheet, purged to the classes its own templates use**. A class
the site has never used is not in the file. Markup that uses it renders with **no styling and no
error**. Verified on the live sheet:

| Exists | Does not exist |
|---|---|
| `gap-8` | `gap-16` |
| `rounded-[12px]` | `rounded-[20px]` |
| `h-[615px]` | `min-h-[400px]` |
| `hover:scale-105` | `animate-pulse` |

Arbitrary values exist only where that exact value is already used somewhere. You cannot reason
about which ones those are. You have to check.

### The two legitimate routes

**Route A — reuse classes the site already ships.** Always the first choice. Take the class
strings off a captured component that solves a similar layout problem and rebuild with them.
Verify before review:

```bash
python3 scripts/check_classes.py handoff/preview/index.html --ignore pu- sc-
```

Exit 1 lists every class that will render unstyled. Treat it as a build failure.

**Route B — a scoped stylesheet for the component.** For anything the site has no class for.
This is what the site itself does: `claude-connector-hero.css` is a component stylesheet in
`static/websitecss/`, loaded only by the page that needs it.

Rules for Route B, all of which matter:

- **Scope every rule** under the component's own root class (`.c-<name> …`). A bare `.card` rule
  will collide with something; the site is one stylesheet and there is no isolation.
- **Use the site's variables and token values, never fresh colours.** §5 lists what is real.
- **Never redefine a token.** Consume `var(--product-primary)`; do not set it.
- **No `@apply`, no Tailwind directives.** The page is built as static HTML against the shipped
  stylesheet; nothing compiles your CSS.
- **Layout only, plus token-valued paint.** If you find yourself inventing a colour, a font size
  or a radius, the section is drifting away from the site rather than extending it.

### The site's real variable theme

The stylesheet defines a live theme on `<body data-product="…">`:

```css
:root, [data-product=search] { --product-primary:#069ba2; --product-dark:#05747a;
  --product-dark-hover:#045d61; --product-light:#e6f5f6; --product-light-hover:#daf0f1;
  --product-darker:#02393C; --product-btn:#05747a; --product-btn-hover:#058c92 }
[data-product=amazon]    { --product-primary:#f29c07; … }
[data-product=social]    { --product-primary:#0d9dee; … }
[data-product=ecommerce] { --product-primary:#b8a2ed; --product-dark:#8665c9;
  --product-dark-hover:#6a36c1; --product-light:#f4effb; --product-light-hover:#dfd6f9;
  --product-darker:#2e175b; --product-btn:#8665c9; --product-btn-hover:#9578d1 }
```

with utilities already in the sheet: `product-btn-primary`, `product-btn-dark`,
`product-btn-light`, `product-text-primary`, `product-text-dark`, `product-border-primary`,
`product-bg-light`.

**Use these in a designed section.** A section painted with `var(--product-primary)` re-themes
itself correctly on a search, Amazon, social or ecommerce page; one painted `#069ba2` is teal forever and
will be wrong the first time it is reused. Every live page currently ships
`data-product=search` on `<body>`; a product page should set its own value.

> **Namespace warning.** The scene runtime also uses `--product-*` names
> (`--product-head`, `--product-accent`, `--product-border`, …). They do not collide with the
> site's today, and they must not be allowed to. A scene that used `--product-primary` without
> declaring it would silently inherit the *site's* brand teal rather than failing visibly —
> which is precisely the mix of the two visual languages that `design-system.md` §1 forbids.
> Keep scene variables to the scene's own names, declared on `.product-ui`.

### Brand token values

Teal `#069ba2` · blue `#0d9dee` · lime `#7fde06` · yellow `#f29c07` · green `#17c687` ·
violet `#613feb` · red `#e72c64` · orange `#f95f1d` · purple `#b8a2ed` · mustard `#f2dc51`.
Surfaces `#626c7a` / `#22262b` / `#0b0c0d`.
Prefer the variable over the hex wherever a variable exists.

## 5. Step four — deliver it as a component

A designed section is a component, not a slab of markup in one page's build script. Deliver the
full Bookshop triplet so a developer can drop it in, and so the next page can reuse it:

```
component-library/components/<name>/<name>.bookshop.yml   # field structure + preview defaults
component-library/components/<name>/<name>.hugo.html      # template, ranging over the fields
static/websitecss/<name>.css                              # Route B styles, if any
```

Plus a short **rationale** in the handoff, which is what turns "Claude invented a section" into
a reviewable proposal. Four lines is enough:

- the archetype, and why no existing component covered it;
- the representation chosen, and what was rejected;
- which classes are reused and which are new CSS, with the `check_classes.py` result;
- any field a developer must wire up.

Mirror the conventions of the captured components: `_bookshop_name` matching the directory,
fields defaulted in the template (`{{ .x | default "…" }}`), `alt=""` plus `aria-hidden="true"`
on decorative imagery, `loading="lazy"` below the fold.

## 6. The logo strip

Do not build one. The site has exactly one, inside the `hero` component, and it is already
copy-pasted verbatim into `social-hero` and `hero-demo` — that repetition is the convention.
The markup is captured at `site-kit/patterns/logo-strip.html`; `images.md` has the details that
are easy to get wrong (no grayscale, no opacity, `h-[24px] w-auto object-contain`, the mobile
marquee duplicated for a seamless loop, `position: sticky` at the bottom via `.bottom-sticky`).

## 7. Step five — animate the entrance

Entrance only, through the site's own convention. Nothing bespoke:

```html
<div data-scroll="fade-slide" data-scroll-delay="0.1">
```

`fade-slide` · `slide-left` · `slide-right`, with `data-scroll-delay`, `data-scroll-duration`,
`data-scroll-trigger`. The site's `main.js` sets the starting opacity through `gsap.set`, never
in CSS, so content stays visible when JS does not run, and it honours
`prefers-reduced-motion`. Stagger a card row by giving each card a delay `0.1` apart.

`animation-system.md` governs anything inside a scene. The two do not mix.

## 8. Verify

1. `check_classes.py` exits 0.
2. The section renders correctly with JavaScript disabled (nothing stuck at opacity 0).
3. Nothing inside it uses a colour that is not a token or a variable.
4. At 375px it does not overflow; at 1440px it matches the page's container width.
5. The rationale is in the handoff.
6. Read the page top to bottom and ask whether the new section earns its vertical space. If the
   page reads better without it, cut it.

## What this never licenses

Designing a content section does not extend to the site's structure or conventions.
`site-kit.md` §4 still holds absolutely for:

- header, footer, navigation, menus, legal copy, forms;
- the section order of a known page type, and its hero;
- any component that already exists — an existing component is used as-is, never "improved";
- brand colours, type scale, spacing scale, breakpoints, radii.

The line is: **a new section may say something new; it may not say it in a new visual language.**
