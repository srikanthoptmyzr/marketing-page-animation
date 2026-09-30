# Solution page sections

Status: **observed** (computed from `/solutions/monitoring/` at 1440 px and the fetched structure of agencies and AI pages).

Shared container: `container mx-auto px-4 lg:px-12 max-w-1440`; `.px-lr` = 16px side padding.

## 1. Hero: `c-hero-solution`
- Background class `bg-solution` (image `/images/solutions/hero-bg.png`); padding `pt-[48px] lg:pt-[70px] lg:pb-[70px] px-[16px] lg:pl-[48px] lg:pr-0`.
- Layout: `max-w-1440 mx-auto flex flex-col-reverse lg:flex-row items-center justify-between gap-12` (image above text on mobile).
- Text half `lg:w-1/2`: H1 `text-mobileHeadlinesH2 md:text-desktopHeadlinesH1 font-dm font-bold`; subhead `text-colorSurfaceDarkNormalActive md:text-desktopSubHeadingsP2`; button row: primary "Start Trial", secondary "Book A Demo".
- Image half `lg:w-[48%] h-[615px]`: main screenshot with shadow `0_4px_32px rgba(0,0,0,0.16)` plus a blurred second image; mobile shows three pictures, the two side ones blurred.
- Scene use: the screenshot area is where an animated scene replaces the still image, when the brief asks for it.

## 2. Marquee: `c-animated-trail-banner`
`bg-teal-darker py-2`, scrolling text (`marquee`), `text-desktopSubHeadingsP2`. Must respect reduced motion (pause it).

## 3. Features: `c-features-section`
- Section padding `py-[61px] lg:py-[48px]`; heading left-aligned, `text-desktopHeadlinesH3`.
- Wrapper `flex flex-col gap-10 md:gap-20 lg:gap-28 max-w-[1140px] mx-auto`.
- Each `feature-row`: `relative flex flex-col md:flex-row md:items-center gap-6 lg:gap-10`, on mobile a bordered white card (`border rounded-lg bg-white p-6`), on md+ transparent (`md:border-0 md:rounded-none md:bg-transparent md:p-0`).
- `text-half`: H3 `font-dm font-bold text-desktopSubHeadingsP3 lg:text-desktopHeadlinesH4`; description `text-neutral-700`.
- `image-half`: `bg-surface-dark-lighter rounded-lg p-4`. Rows alternate with `md:order-1` / `md:order-2`.
- **This is the natural home for an animated scene**: put the scene inside `image-half`, keep the text half unchanged.

## 4. Case study: `c-casestudy-section`
White; `pb-[57px] lg:pt-[48px] lg:pb-[96px] px-lr`. Grid `grid grid-cols-1 lg:grid-cols-2 gap-x-[32px]`: left a "Case study" pill (`bg-colorSecondaryLimeLightActive text-colorSecondaryLimeDarker`), quote, primary "Learn More"; right an image.

## 5. CTA: `c-cta-section-solutions`
Outer `bg-surface-dark-darker-hover` (#191B1F) `py-[40px] lg:py-[130px]`; inner card `max-w-[1440px] bg-surface-dark-dark border rounded-lg` with a decorative image at each side; headline, text, primary + secondary buttons.

## 6. FAQ: `c-faq-section`
See `faq-accordion.md`.

## Buttons
- Primary: `rounded-lg font-bold text-desktopSubHeadingsP4 text-colorSurfaceLightWhite py-3 px-8 h-[48px] bg-teal-dark hover:bg-colorPrimaryTealNormalHover` (radius 8px, 16px/700).
- Secondary: `bg-teal-light text-colorSecondaryBlueDarker hover:bg-colorPrimaryTealLightHover`.
