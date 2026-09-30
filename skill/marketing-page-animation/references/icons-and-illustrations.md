# Icons and illustrations

Used in phase 11, when a designed section (see `new-sections.md`) needs imagery that is not a
product scene.

**Product UI always stays an HTML/CSS scene.** This file is about the other imagery a page
needs: the icon beside a statistic, the small illustration that anchors a section heading, the
star on a rating. Those are the site's own visual language, and the site is unusually
consistent about them — which makes matching it a checkable job rather than a matter of taste.

Everything below was measured from the 225 SVGs the live site ships. There are **zero raster
images** under the site's icon and illustration directories; everything is vector.

## 1. When a section needs imagery at all

Add imagery when it does one of these:

- **Gives a figure a handle.** A stats card row is a wall of numerals without one icon per card;
  the icon is what makes the row scannable.
- **Identifies a party.** A customer logo on a testimonial, a platform logo in an ecosystem row.
- **Encodes a value.** A star that means a rating, a check that means included.
- **Anchors a heading** that would otherwise sit on empty space.

Do not add imagery that restates the adjacent words. An icon of a chart next to the word
"Reporting" is decoration; if it is there, it should be `aria-hidden` and small, which is exactly
what the site does.

## 2. Icon house style

Measured from the icons the live site actually serves. The set has **three families**; pick the
one that matches the job, then follow its rules exactly.

Shared by all three: square-ish viewBox on a **20 or 24 grid** (`21x20` and `24x25` occur —
one unit of slack is normal), `fill="none"` on the root `<svg>`, 2-9 simple shapes, and **no
gradients, filters or shadows anywhere**.

### Family 1 — outline (the default for a marketing section)

Monoline, Feather-style, strokes only, **one colour per icon**.

| Property | Value |
|---|---|
| Stroke width | **1.6-2.4**, roughly 7-10% of the grid |
| Joins | `stroke-linecap="round"` and `stroke-linejoin="round"` on every open path |
| Colour | By role, see below |

| Role | Colour | Typical width |
|---|---|---|
| Content and accent icons — **what you generate** | **`#069BA2`** (brand teal, 593 occurrences) | 1.6 @24, 2 @20 |
| Content icon, darker variant | `#058C92` | 1.6 |
| Chrome affordances (close, hamburger) | `#2D3A48` | 2.4 |
| Occasional brand accent | `#66B205` | 1.92 |

`#2D3A48` means "chrome" on this site. A marketing section icon is teal.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
  <path d="M3 17.5 9.5 11l4 4L21 7.5" stroke="#069BA2" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M15.5 7.5H21v5.5" stroke="#069BA2" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### Family 2 — filled badge (state: included / excluded)

A solid disc in a **state colour** with a **white stroked glyph** over it. This is the site's
included/not-included indicator; use it in comparison tables, not as decoration.

```svg
<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="20" height="20" rx="10" fill="#058C92"/>
  <path d="M6 10.36 9 12.86 14.8 6.43" stroke="white" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

Disc colours: `#058C92` positive · `#AAB0B7` neutral or negative. The glyph is always white at
the same 1.6-2.4 stroke width.

### Family 3 — solid glyph (a value, not a picture)

One filled path, no strokes, in an accent colour. The rating star is the canonical case:
`#F29C07` on an `18x17` box.

> The star exists twice. The **file** `star-filled.svg` is `#F29C07` at `0 0 18 17`; the
> **inline** star in `testimonial-section` is `#E17F0E` at `0 0 20 21`. Match whichever context
> you are building into rather than assuming one.

### Two things that are easy to get wrong

- **`currentColor` is not the house style.** None of the file-based icons use it; the colour is
  literal. `currentColor` appears only in newer *inline* component SVG.
- **Stroke width scales with the grid.** `1.6` on a 40-unit icon looks visibly thin beside its
  24-unit neighbours.

Check generated icons before shipping:

```bash
python3 scripts/check_svg_style.py handoff/assets/icons/*.svg
```

It reports the family it detected, and **skips third-party brand marks** (partner and social
logos), which keep their own colours by definition and must never be recoloured to the palette.
Verified: it passes all 23 of the site's own sampled assets with no deviations.

## 3. Illustration house style

Larger decorative vector art. These are filled shapes, not strokes, and the set is **much less
uniform than the icons** — do not treat the numbers here as law the way §2's are.

What is verified across every illustration sampled on the live site:

| Property | Value |
|---|---|
| Format | Flat vector. **No gradients anywhere** — not one sampled asset uses one |
| Colour | Drawn from the teal ramp: `#069BA2` -> `#058C92` -> `#045D61` -> `#02393C`. Often a **single hue for the whole asset** |
| Opacity | Large decorative fields sit at **0.4-0.5**, which is what keeps them behind the copy |
| Warm accent | `#F29C07` (the same amber as the rating star), used for one or two elements at most |
| Canvas | **Sized to its slot**, not to a house grid. Observed: `188x533`, `524x920` for pricing hero art |

The pricing hero graphics are the clearest example of the house approach: thousands of small
shapes in one colour (`#045D61`) at `0.4` opacity, forming a texture rather than a picture. Depth
comes from stepping down the teal ramp and from opacity, never from a gradient.

> A lighter tint ladder (`#66AFAB`, `#B5D5D4`, `#EDF4F4`, `#E4EBEB`) and fixed card canvases
> appear in illustration sources in the repo but could not be confirmed on the live site. Treat
> them as **observed**, not verified: usable, but note the assumption in the handoff.

Because canvases are slot-sized, always set explicit `width` and `height` on the `<img>` so the
section does not reflow while the asset loads.

## 4. Deliver imagery as files

Generated icons and illustrations are written as **`.svg` files**, not inlined into the page
markup, so that the same asset can be swapped for a designer's version or replaced by a raster
image without touching the page.

```
handoff/assets/icons/<kebab-name>.svg
handoff/assets/illustrations/<kebab-name>.svg
```

Reference them as the site does, and mark them decorative when they are:

```html
<img src="/images/icons/accounts-managed.svg" alt="" aria-hidden="true"
     width="56" height="53" loading="lazy" class="w-auto h-[37px] md:h-[53px]">
```

Always set `width` and `height` so the row does not reflow while loading. Use `loading="lazy"`
below the fold and **omit it above the fold** — a lazy hero image is a visible pop-in.

List every generated asset in the handoff with its intended repo path, so a developer knows what
to copy into `static/images/`.

## 5. The two patterns worth copying exactly

### Stats card with a per-figure icon — from `team-bynumbers`

The only stats treatment on the site with imagery, and the model for any "at scale" section. The
icon deliberately **bleeds past the card's top-right corner**; that overhang is the whole
character of the pattern, and a neatly contained icon looks like a different site.

```html
<div class="bg-surface-dark-lighter rounded-[12px] border border-[#E8E8E8] flex flex-col
            py-[16px] md:py-[24px] px-[16px] md:px-[24px] flex-1 relative items-center gap-[12px]">
  <div class="flex justify-between w-full h-[31px] md:h-[40px]">
    <h3 class="font-dm font-bold text-mobileHeadlinesH3 md:text-desktopHeadlinesH3">…</h3>
    <img src="…" alt="" aria-hidden="true" width="56" height="53" loading="lazy"
         class="w-auto h-[37px] md:h-[53px] translate-y-[-11px] md:translate-y-[-15px]
                translate-x-[11px] md:translate-x-[15px]">
  </div>
  <p class="text-surface-dark-active text-desktopSubHeadingsP5 md:text-desktopSubHeadingsP4">…</p>
</div>
```

Note `bynumbers-section` is a *different*, text-only component — its `partner_images` field feeds
a separate floating "Partnering with the best" card, not the figures. Do not confuse the two.

### Proof block — from `testimonial-section`

Company logo at `max-w-[78px] max-h-[32px]`, then a **single amber star** with a numeric rating
beside it — not five stars:

```svg
<svg width="20" height="21" viewBox="0 0 20 21" fill="#E17F0E"><path d="…"/></svg>
```

A decorative pattern image sits behind the heading
(`/images/homepage/testimonial-pattern-1.webp`, `opacity-80`, `!w-[300px] !h-[300px]`).

> **Gotcha.** Both `testimonial-section` and `social-testimonials-section` read from
> `data/en/testimonialsMain.yaml` and **ignore their own front matter**. Content set in the page
> file will not appear. Either supply the data file or build the block as a designed section.

The site's only true five-star widget is `reviews-section`, which is a different mechanism
entirely: a grayscale star row with an absolutely-positioned clipped colour overlay whose width
is an inline `calc()` from the rating. Use it only if a real five-star display is required.

## 6. Animating imagery

Optional, and deliberately restrained. The site has **no Lottie and no SVG SMIL anywhere** —
introducing either would be conspicuous.

**Default: no individual animation.** Icons ride their parent's scroll reveal. Give the
container `data-scroll="fade-slide"` and stagger siblings with `data-scroll-delay` 0.1 apart.
This is what every animated icon row on the site does today.

**If a micro-animation is genuinely warranted**, the only precedent is
`claude-connector-hero.css`, and it is very small:

```css
@keyframes ozcl-bob { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-3px) } }
.c-<name> .icon { animation: ozcl-bob 1s ease-in-out infinite; }
.c-<name> .icon:nth-child(2) { animation-delay: .16s }
```

Movement ≤3px, 1s ease-in-out, siblings staggered .16s. Keep it to one element, or a short row.

Two hard requirements:

```css
@media (prefers-reduced-motion: reduce) { .c-<name> .icon { animation: none } }
```

and never animate a decorative icon in a way that draws the eye away from the section's copy. An
infinite animation next to text is a reading obstacle, which is why the site has almost none.

Marquees are the exception the site does use — the logo strip scrolls at `20s linear infinite`
on mobile and pauses on hover. Copy that markup wholesale rather than re-deriving it.
