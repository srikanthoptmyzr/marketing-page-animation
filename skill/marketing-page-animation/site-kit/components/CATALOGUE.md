# Component catalogue by section type

All 90 Bookshop components grouped by the kind of section they build, so a brief that
says "add a case-studies section" or "a cards grid" maps to real components instead of
something invented. Full markup and fields per component are in `<name>/`.

Source: `Optmyzr-Engineering/marketing-website` @ `c9ac095`. Refresh with
`scripts/capture_component.py --repo <checkout> --all`.

## Case studies & customer stories (4)

| Component | Fields | Use for |
|---|---|---|
| `casestudy-section` | 6 | The standard solution-page case study: pill, quote, Learn More, thumbnail. Repeat one block per study |
| `casestudies` | 8 | Multi-card case-study listing |
| `comparison-casestudy-carousel` | 0 | Carousel on comparison pages; pulls studies itself |
| `about-customer-section` | 5 | Customer profile block on a case-study page |

## Blog, articles & content (5)

| Component | Fields | Use for |
|---|---|---|
| `research-hub-highlights` | 4 | Featured research entries |
| `ppc-youtube-section` | 3 | Video/webinar strip |
| `featured-authors` | 3 | Author spotlights |
| `newsletter` / `alm-newsletter` | 4 / 7 | Subscribe blocks |

Blog **listings** are not components — the blog hub is a template (`post/list.html`,
`blocks-in-template`) and a post is prose (`post/single.html`). See `page-types.md`.

## Card / grid / tile sections (8)

`products-section` (9) · `partners-cards` (7) · `grid-images` (7) · `teams-section` (6) ·
`values-section` (5) · `labs-cards` (4) · `comparison-pricing-cards` (2) · `perks-section` (2)

## Testimonials, reviews & social proof (17)

`testimonial-section` · `testimonials-solutions` · `testimonials-solutions-2` ·
`social-testimonials-section` · `comparison-testimonial` · `demo-testimonial` ·
`connector-testimonial` · `reviews-section` · `awards-section` · `awards-about` ·
`bynumbers-section` · `team-bynumbers` · `results-section` · `founders-section` ·
`founders-slider` · `conferences-section` · `social-features-section`

## Feature & capability sections (15)

`features-section` (9, **the scene host** — see `page-types.md`) · `steps-section` ·
`timeline-section` · `sidekick-demos` · `sidekick-setup` · `mcp-features` ·
`mcp-use-cases` · `mcp-compatible-tools` · `connector-quality` ·
`connector-data-coverage` · `amazon-features-section` · `amazon-pricing` ·
`animated-trail-banner` · `trail-banner` · `animated-images`

## Heroes (19)

One per page family: `hero-solution`, `hero`, `hero-about`, `hero-alm`, `hero-bloghub`,
`hero-careers`, `hero-comparison`, `hero-comparison-indv`, `hero-contact`, `hero-demo`,
`hero-labs`, `hero-partners`, `amazon-hero`, `social-hero`, `sidekick-hero`,
`claude-connector-hero` (**the animated precedent**), `case-study-hero`,
`comparison-hero-slim`, `lwo-hero`.

## Comparison (11)

`comparison-benefits` · `comparison-built-for` · `comparison-buyer-fit` ·
`comparison-features` · `comparison-migration-section` · `comparison-only-on-optmyzr` ·
`comparison-pros-cons` · `comparison-steps-section` · `comparison-table` ·
`comparison-table-accordion` · `optmyzr-alternatives-section`

## CTA (4) · FAQ (1) · Forms (4) · Chrome (1)

`cta-section-solutions` · `cta-section-1` · `cta-section-2` · `thankyou-section` |
`faq-section` | `contact-form` · `contact-offices-section` · `demo-benefits` ·
`open-roles-section` | `language-picker`

## Other (1)

`result-details-section` (6) — results detail on a case-study page.


## Coverage, measured

Every component the site's English content actually uses is captured: **83 used, 90 captured,
0 missing** (counted from `_bookshop_name` across all of `content/english`). Seven captures are
unused by content — `language-picker`, `hero-bloghub`, `featured-authors`, `alm-newsletter`,
`open-roles-section`, `comparison-steps-section`, `testimonials-solutions` — because they are
pulled in by layouts and partials rather than by `content_blocks`.

### The components that actually carry the site

| Component | Pages using it |
|---|---|
| `faq-section` | 67 |
| `animated-trail-banner` | 54 |
| `cta-section-solutions` | 53 |
| `features-section` | 51 |
| `hero-solution` | 51 |
| `case-study-hero`, `results-section`, `result-details-section`, `about-customer-section` | 40 each |
| `casestudy-section` | 20 pages, 34 blocks |
| the `comparison-*` family | 11 each |

The **case-study set** is the second-biggest family after the solution set and is worth reading
before building anything in that area.

## Two hazards the captures expose

**1. Thirteen components read a field the blueprint never defaults.** The CMS will not prompt
for it, so the section renders with a hole unless the author knows to set it. Check
`fields.json` for `usedInTemplate: true, inBlueprint: false` before authoring one of these:

`about-customer-section` (authorCompany) · `alm-newsletter` (7 fields) · `amazon-pricing` (10) ·
`case-study-hero` (author, customerCompany) · `comparison-migration-section` (anchor_url,
link_text, text) · `featured-authors` · `grid-images` (7) · `hero` · `hero-bloghub` ·
`labs-cards` · `language-picker` · `open-roles-section` · `steps-section` (5)

Two of those — `about-customer-section` and `case-study-hero` — are on 40 pages each, so this
is not a corner case.

**2. Half the library has copy outside the translatable-key list.** 45 of 90 components carry
at least one copy field the script translator skips, most often `client_name`, `stars` and
`benefit_1..3`. The LLM localization agent usually catches them, so parity depends on which
path runs. Prefer a listed field name for new scene copy, and flag the component's unlisted
fields in the handoff rather than editing the config. See `README.md` in this folder for why
the two paths disagree.

## Picking one

1. Match the brief's words to a group above.
2. Read that component's `fields.json` before writing content: field names decide what gets
   translated (`localization: translatable | skip | url-prefixed | unlisted`).
3. Check `page-types.json` that the page type allows it — a component existing does not mean
   a given page type uses it.
4. Nothing fits? That is a **kit gap**. Say so; do not invent a component.

## Read the template, not the rendered page

Copying markup from a live page is the only way to get classes that survive the purged
stylesheet, but rendered HTML cannot show you a loop's conditions. Two things are
invisible in it and cost real review cycles:

- **Conditional pieces.** `faq-section` emits its separator only between items
  (`{{ if ne (add $index 1) (len $.faqs) }}`), so the card does not end on a rule. A page
  rebuilt from rendered HTML puts one after every item, and the extra line at the bottom
  is the first thing a reviewer notices.
- **Real field names.** The same component's heading field is `faq_title`, not `heading`,
  and it takes `headingLevel`, `emitFaqSchema`, `startClosed` and `addExtraBottomPadding`.
  None of that is visible in output.

Where a component has a `template.hugo.html` here, read it before authoring the section
and before writing the front matter. Use the live page for the classes, the template for
the structure and the fields.
