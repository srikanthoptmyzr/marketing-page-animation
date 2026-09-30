# Breakpoints and fonts

**Verified** from `themes/optmyzr-marketing-v2/assets/websitecss/tailwind.config.js`
(`Optmyzr-Engineering/marketing-website` @ `c9ac095`, 2026-09-29).

## Breakpoints

Tailwind `screens`, min-width, in order:

| Name | Min width | Notes |
|---|---|---|
| `below-360` | 360px | Narrow-phone escape hatch |
| `xss` | 376px | Custom. Used for the first type-size step up (`xss:text-mobileHeadlinesH3`) |
| `sm` | 640px | |
| `md` | 768px | **The mobile/desktop split** — feature rows go side by side, hero background switches off below it |
| `lg` | 1024px | **Scene fit threshold** (`data-fit-from="1024"`); hero's desktop image block appears |
| `xl` | 1280px | |
| `desktop-lg` | 1540px | Widest step |

The kit previously assumed only a 767/768 split. That assumption was right about `md`, but
the site has **seven** breakpoints, three of which the skill's viewport matrix never tested.

**Test at these widths:** 360, 376, 640, 768, 1024, 1280, 1440, 1540. The matrix in
`references/responsive.md` (320, 390, 768, 1024, 1440, 1920) misses `sm` 640, `xl` 1280 and
`desktop-lg` 1540, and 1920 is above the widest defined step.

## Fonts

| Tailwind family | Stack | Used for |
|---|---|---|
| `font-display` | `Inter, sans-serif` | |
| `font-body` | `Inter, sans-serif` | Body copy |
| `font-dm` | `DM Sans, sans-serif` | Headlines (`font-dm` on every `h1`/`h2`/`h3` in the components) |

Files ship from the repo at `static/websitefonts/inter/` and `static/websitefonts/dm-sans/`
as `.woff2`. Latin subsets are present; **CJK coverage is not** — Japanese is an active
language, so Japanese text falls back to a system font. Confirm with the dev team before
claiming Japanese renders in brand type.

**Previews served outside `optmyzr.com` cannot load these fonts**: the font files are served
without `Access-Control-Allow-Origin`, so a preview on `localhost` or `file://` falls back to
system fonts. Metrics differ slightly from live; do not judge fine typography from a local
preview.
