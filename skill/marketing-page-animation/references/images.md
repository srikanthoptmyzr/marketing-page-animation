# Images: fit the slot, never the upload

Uploaded images come in any size. The page never uses that size. Each image is assigned a **slot** from `site-kit/image-specs.json` and processed by `scripts/prepare_image.py`.

| Slot | Fit | Rendered (desktop / mobile) | Exported widths |
|---|---|---|---|
| `feature` | contain, aspect 1.2 to 2.0 (padded, not cropped) | up to 515x400 / 276 wide | 256, 512, 767 |
| `hero-visual` | contain | desktop region 48% of 1440 x **615 tall**, image capped at `max-h-[84%]` (~516px) and offset `top-[18%]`; below `lg` a separate composition, centre card `w-[68%]`, `h-[165px]`, `md:h-[240px]` | 512, 767 |
| `case-study-thumb` | cover, 16:9 | 542x305 / 358x201 | 542, 1084 (2x) |
| `cta-side` | cover, 321:412 | 321x412 | 321, 642 (2x) |

Steps:
1. Decide for each supplied image whether it is a **scene input** (UI screenshot: rebuild it, do not embed) or a **page image** (photo, logo, thumbnail). Only page images go through this tool.
2. Pick the slot from the page type in `site-kit/page-types.json`.
3. Run `prepare_image.py IMAGE --slot SLOT --out DIR --name NAME --alt "..." [--focus x,y]`. Ask the user for the focus point when a cover crop could cut off the subject (faces, key text).
4. Use the emitted `.picture.html` (srcset + sizes + width/height, lazy loading).
5. If the source is smaller than the slot's widest export, the tool skips that width and says so: ask for a larger file, do not upscale.
6. Record every crop/pad in the handoff notes. Case-study thumbnails are static and never animated.

**Slot classes verified from the repo** (`c9ac095`, 2026-09-29):

- `feature` — box `bg-surface-dark-lighter rounded-lg overflow-hidden md:border md:border-solid md:border-[#E8E8E8] p-4 flex items-center justify-center min-h-[220px] md:min-h-[340px] lg:h-[400px]`; image `object-contain w-full max-h-[280px] md:max-h-full`. Note `lg:h-[400px]` is a **fixed** height, so a taller scene is clipped by `overflow-hidden` rather than growing the row.
- `hero-visual` — desktop wrapper `w-full lg:w-[48%] relative hidden lg:block h-[615px]`; image `w-full z-20 absolute top-[18%] max-w-full h-full max-h-[84%]` with `object-contain`. The `isVerticalImage` field switches the image to `h-full w-auto`; a second boolean adds a drop shadow. Below `lg` the hero uses a different composition with two blurred one-third background images and a centre card — **not the same slot**, so a hero scene needs its own mobile treatment.
- **Section backgrounds belong to the component, not to an inline style.** `hero-solution` ships its own `<style>` block: `.bg-solution { background-image: url('/images/solutions/hero-bg.png'); background-repeat: no-repeat; background-size: auto; background-position: left center; }` and `background: none` below 768px. Writing an inline `background-size: cover` instead stretches the pattern across the whole hero and leaves it on mobile. Copy the component's rule verbatim; never re-specify a background by hand.
- Images resolve through `partial "functions/resolve-image-path.html"` then `partial "image.html"`; SVGs bypass the image partial and are emitted as a plain `<img>`.

Remaining values are `observed` from the live site (Hugo resizes to srcset 128/256/512/767/1023/1470 webp, so the bundle also ships source images the dev team can feed to Hugo). Requires Pillow. **If Pillow is unavailable** (see phase 0), do not fall back to using uploads at their own size — that breaks rule 2. Ask the user for images already at the slot's export widths, fit scenes with `pu-fit` as normal (the player is pure CSS/JS and needs no Python), and record every un-fitted page image as an approximation in the handoff.

## Scenes obey the slot too

A scene never grows past its section's image box. On desktop the feature image box is 400px tall, so scenes go inside `figure.pu-fit` with `data-fit-from="1024"`, `data-fit-width` (the width the scene is designed at) and `data-fit-height` (slot height minus the 45px of controls). The player lays the stage out at the design width and scales it down to fit the box; controls and caption stay full size. Below 1024px the scene stays responsive. **Size the design to the slot: usable width / 0.85.** For the feature slot that is about 600px, for the hero about 720px. A scene designed wider is not "fitted", it is shrunk, and its text falls under the 11px floor — the player warns in the console below a 0.8 scale. If a scene will not fit, take content out (fewer columns, shorter labels, fewer rows) rather than letting the scale drop. See `responsive.md`, "Design a scene at its slot's width". Slot sizes for the wide (full-width) rows are set per scene in the page build.

## Rendering quality: three things to check, with the evidence

**1. Serve 2x sources, or Retina looks soft.** Measured on a real build: `sol-cta-left.png` and
`sol-cta-right.png` rendered at **321 CSS px from a 321 px source** — a 1.0 ratio, which is half
the pixels a 2x display needs. The site's own pipeline emits `srcset` (the kit records
`cta-side: 321, 642` in `image-specs.json`); hand-written markup that points at the 1x file
drops that. Either reference the site's `<picture>` markup with its `srcset`, or run the image
through `prepare_image.py`, which emits the slot's widths. **Never hand-write a bare `<img>`
for site art.** Ratio under 2.0 against a design that will be viewed on a laptop is a fail.

**2. Above-the-fold art must not be lazy.** `loading="lazy"` on a hero image delays the largest
paint for no saving, because it is visible immediately. Hero art gets
`loading="eager" fetchpriority="high" decoding="async"`; everything below the fold stays lazy.

**3. A scaled scene must land on whole pixels.** `pu-fit` scales by an arbitrary factor, so the
stage ended 0.5-0.9 px tall at the bottom: the border antialiases into a grey smear and every
baseline sits off-grid. It reads as "blurry" even at a perfectly good scale. The player now
snaps the factor so the rendered height is an integer (using the **exact** fractional height,
not `offsetHeight`, which is already rounded and snaps against the wrong number). Measured
before: 6 of 6 scenes off-grid by 0.12-0.97 px. After: 0.

What NOT to do: do not put `will-change: transform` or a 3D transform on a scaled stage. It
promotes the layer and the text is then rasterised at the pre-scale size and stretched, which
is genuinely blurry rather than merely off-grid.
