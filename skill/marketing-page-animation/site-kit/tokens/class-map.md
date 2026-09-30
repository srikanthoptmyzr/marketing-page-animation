# Token class map

Status: **observed** (computed styles and class names on live pages, 2026-09-29). Values not printed by the browser are marked "?".

## Fonts
Body: Inter 16px/24px, 400. Headings: DM Sans 700 (class `font-dm`), letter-spacing about -0.5px. Buttons: Inter 16px, 500 to 700.

## Layout
Container `container mx-auto px-4 lg:px-12 max-w-1440` (1440px). `.px-lr` = 16px sides. Tailwind container steps: 360, 376, 640, 768, 1024, 1280, 1540. Header switches to desktop at `xl` (1280px). Media queries also seen: 320-580, 581-767, 768-1024, 1025+, 1300, 1500.

## Colors (class suffix, hex)
Use as `bg-<name>` / `text-<name>`.
| Name | Hex |
|---|---|
| colorPrimaryTealDark (alias `teal-dark`) | #05747A |
| colorPrimaryTealNormal | #069BA2 |
| colorPrimaryTealDarker (alias `teal-darker`) | #023639 |
| colorPrimaryTealDarkActive | #034649 |
| colorPrimaryTealLight (alias `teal-light`) | #E6F5F6 |
| colorSecondaryBlueDarker | #053753 |
| colorSurfaceDarkDark (`surface-dark-dark`) | #22262B |
| colorSurfaceDarkDarkHover (`surface-dark-darker-hover`) | #191B1F |
| colorSurfaceLightLight | #F3F3F3 |
| textonteal | #FFFFFE |
| bordergrey | #CFD9E2 |
Also present: secondary lime, yellow, red, orange, green scales; plain gray and neutral scales. Full values are in `design-tokens.json`.

## Type sizes (px)
| Class | Size |
|---|---|
| text-mobileHeadlinesH1..H5 | 51 / 38 / 28 / 21 / 16 |
| desktopHeadlinesH3 / H5 | 36 / 20 |
| desktopHeadlinesH1 / H2 / H4 | ? |
| mobileBodyB1..B7 | 20 / 18 / 16 / 14 / 12 / 11 / 10 |
| desktopSubHeadingsP2..P7 | 20 / 18 / 16 / 14 / 13 / 11 (P1 ~22, unconfirmed) |
Line-height ladders `leading-desktopLineHeight*` and `leading-mobileLineHeight*` (for example 5xl = 53px desktop, 31px mobile); letter-spacing `tracking-desktopLetterSpacing*` / `tracking-mobileLetterSpacing*` (negative values).

## Radii and shadows
`rounded-lg` 8px, `rounded-xl` 12px, `rounded-2xl` 16px; arbitrary 10/12/14/16px used. Shadows `shadow-sm/md/lg/3xl/xxs`; hero image `0 4px 32px rgba(0,0,0,0.16)`.

## Section spacing seen
Hero solution `pt-[48px] lg:pt-[70px] lg:pb-[70px]`; features `py-[61px] lg:py-[48px]`; case study `lg:pt-[48px] lg:pb-[96px]`; CTA `py-[40px] lg:py-[130px]`; FAQ `pb-[130px] md:pb-[264px]`; trail banner `py-2`.

## Caveat
Tailwind may purge classes not used on existing pages. A class in this table is known to exist only if the site's own pages use it; the dev team must confirm before a new page relies on rare ones.
