# Header, promo banner and footer

Status: **observed** (rendered pages). Dropdown DOM, mobile menu and language-picker behavior are **not yet read**.

## Promo banner
Fixed above the header, teal gradient: `bg-gradient-to-r from-colorPrimaryTealDarkActive to-colorPrimaryTealDarkHover`. It carries an id (`#bfcm-banner` seen). **Optional.** The site runs promotions and turns it on or off; ask whether a promotion is running and leave it out by default; `main` offsets are `mt-18 lg:mt-20`.

## Header
- Container: `header fixed top-0 left-0 right-0 lg:h-[80px] bg-white xl:px-[48px]`, bottom border `border-bordergrey`.
- Two bars: desktop `hidden xl:flex`, mobile `block xl:hidden` (switch at 1280px).
- Nav: `flex flex-row flex-nowrap items-center gap-x-8`. Logo, then menus, then Pricing link, language selector, Log In, Start Trial.
- Menus and groups:
  - Products: Use Cases, Capabilities, Roles
  - Solutions: Monitoring, Automation, AI, Budget Management, Audits, Optimizations, Reporting
  - Resources: Blog, Academy, PPC Town Hall, Case Studies
  - Company: About, Contact, Affiliate Program
  - Pricing: plain link
- Languages: English, Español, Deutsch, Français, 日本語.
- Buttons: Log In `text-teal-dark rounded-xl font-medium bg-teal-light w-[91px] h-[48px]` (bg #E6F5F6, text #05747A, radius 12px). Start Trial `rounded-xl font-medium bg-teal-dark text-textonteal w-[125px] h-[48px]` (bg #05747A). Start Trial links to `https://tools.optmyzr.com/info/signup?lang=en-US`; Book a Demo to `https://www.optmyzr.com/demo-request`.

Never rebuild the header by hand: the preview reuses the kit's captured header; the bundle omits it (the site provides it).

## Footer
- `footer relative bg-black`.
- Top CTA card: `bg-tealdark3 rounded-2xl w-11/12 mx-auto p-[40px] md:py-[48px]`; H5 (`font-dm text-3xl xl:text-[36px]`) "Experience Optmyzr for yourself for 2 full weeks", line "14-day free trial, no credit card", Start Trial + Book a Demo.
- Link grid: `grid-cols-2 md:grid-cols-6 lg:grid-cols-4`, column titles `h6` (`text-sm text-surface-dark-light`): Products, Company, Use Cases, Resources. Social links, partner badges, language picker (`c-language-picker`; a second copy for mobile at the bottom).
- Bottom bar `bg-tealdark2`: legal links (Data Processor Agreement, Privacy Policy, Terms of Use) and "©2013-2026 Optmyzr".
- Copyright year is live text: do not hard-code a different year.

## Capturing the header: start above `<header>`, not at it

The line immediately above `<header>` in a live page is:

```html
<div class="overlay fixed inset-0 bg-gray-400 bg-opacity-50 z-30"></div>
```

The site's own `showSection()` captures this element at parse time
(`overlayEl = document.querySelector(".overlay")`) and writes to it as the *second*
statement inside its `requestAnimationFrame`. If the overlay is not in the page, that
line throws — **after** the popover has already been given its `open` class. The visible
result is a nav link that highlights on hover with no panel behind it, and a single
`TypeError: Cannot read properties of null` that is easy to mistake for noise.

Capture the header slice from the overlay div, not from the `<header>` tag.

## Ecommerce theme: three places the `data-product` override misses

Verified on the live Ecommerce pages, so these are site-level gaps rather than anything a
new page introduces. Scope every fix to `[data-product=ecommerce]` and ship it with the
page; also worth raising with the dev team.

```css
/* 1. Product-switcher tab pills have vertical padding only, so the longest label
      ("Ecommerce") runs edge to edge and touches the container border. */
[data-product=ecommerce] [aria-label$="Toggle"]{max-width:470px}
[data-product=ecommerce] [aria-label$="Toggle"] [role=tab]{padding-left:14px;padding-right:14px;width:auto}

/* 2. #mobileDropdownLabel ("for Ecommerce" in the mobile header) is hard-coded to
      text-colorPrimaryTealNormal. The desktop label is themed; this one is not, so a
      purple page shows a teal label on a phone. */
[data-product=ecommerce] #mobileDropdownLabel{color:var(--product-dark,#8665c9)!important}
[data-product=ecommerce] #mobileDropdownLabel svg path{stroke:var(--product-dark,#8665c9)!important}

/* 3. The "for <product>" chevron inherits its label's colour, unlike every other nav
      chevron (#B3C0CF). Match it to the rest of the nav. */
[data-product=ecommerce] .dropdown-arrow{color:#B3C0CF!important}
[data-product=ecommerce] .dropdown-arrow path{stroke:#B3C0CF!important}
```

## The captured fix block loses the hover scope on one rule

A page's inline override block resets the nav's teal to the product colour. The text rule
is correctly scoped to hover:

```css
[data-product=ecommerce] .group:hover .group-hover\:text-teal{color:#8665c9!important}
```

The stroke rule on the very next line is not:

```css
[data-product=ecommerce] .group-hover\:stroke-teal{stroke:#8665c9!important}   /* wrong */
```

`group-hover:stroke-teal` is a *hover* utility, so dropping `.group:hover` recolours the
chevron permanently: every top-level nav item (Products, Solutions, Resources, Company)
shows a purple chevron at rest. Pair the two rules:

```css
[data-product=ecommerce] .group-hover\:stroke-teal{stroke:#B3C0CF!important}
[data-product=ecommerce] .group:hover .group-hover\:stroke-teal{stroke:var(--product-dark)!important}
```

Whenever you copy an override block from another page, check every `group-hover:` and
`hover:` utility it touches still has its state selector.
