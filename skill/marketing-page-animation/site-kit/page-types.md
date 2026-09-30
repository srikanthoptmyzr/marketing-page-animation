# Page types: which structure to follow

Status: **verified** from the repository (`Optmyzr-Engineering/marketing-website`, `main`, commit `c9ac095`, read 2026-09-29). Section order and required/optional were derived from every English page's `content_blocks`; classes and field names come from the Bookshop component templates. Machine-readable: `page-types.json`. Full inventory: `docs/repo-inventory.md`.

**How structure is defined:** a page's sections are the ordered `content_blocks` array in its YAML front matter, each entry keyed by `_bookshop_name`; the layout only renders them. To add a section you add a block — never edit a layout. Header, footer and promo banners are not blocks; they come from the base layout.

Rule: a new page starts from the closest page type below and keeps its section order, container, spacing and header/footer. Deviate only for the story (extra scene sections), and record each deviation in the handoff.

### Route the brief to a page type

Match what the user asks for to a row. If nothing matches, say so and ask — never invent a page type.

| The user asks for | Page type | Authoring model | Can a scene go in? |
|---|---|---|---|
| a landing page, solution page, feature page | **Solution** (`v4-generic-solutions-page`) | blocks | **yes, direct** — the primary home for scenes |
| a comparison / "Optmyzr vs X" page | **Comparison** (`compare`) | blocks | yes, direct |
| the homepage | **Homepage** (`index`) | blocks | yes, direct |
| an about / team page | **About** (`about`) | blocks | yes, direct |
| a contact page | **Contact** (`contact-us`) | blocks | yes, direct |
| a demo-request / "book a demo" page | **Demo request** (`demo-request-v2`) | blocks | yes, direct — never touch form wiring |
| a thank-you / confirmation page | **Thank-you** (`thank-you`) | blocks | yes, direct |
| a partners page | **Partners** (`partners/list`) | blocks | yes, direct |
| a pricing page | **Pricing** (`pricing-page-v2`) | blocks-in-template | only inside the blocks region |
| a case study / customer story | **Case study** | blocks-in-template | only inside the blocks region |
| a resources page, guide or hub | **Resource hub** — 5 different variants, see below | mixed | varies by variant |
| a product page | **Product** | mixed (2 blocks, 3 params) | only on the amazon/social/ecommerce layouts |
| a free tool, calculator or labs entry | **Labs** | blocks (hub) + params (entry) | hub only |
| a careers page or job opening | **Careers** | blocks (hub) + params (opening) | hub only |
| a webinar or event page | **Event** | params + body | **no — kit gap** |
| a blog post or article | **Blog post** | body | **no — kit gap** |
| an author profile | **Author** | params | **no — kit gap** |
| a legal / policy page | **Legal** | body | **no** — route to the dev/legal team |

## Solution page standard (`/solutions/monitoring/`, `/solutions/paid-search`, `/solutions/digital-marketing-agencies/`, `/solutions/optmyzr-ai`)

Confirmed by the site owner (2026-09-29) and **verified from code**: the order below is what 51 English solution pages actually use. Current layout for new pages is `v4-generic-solutions-page`; `v2-generic-solutions-page` is also in use; `generic-solutions-page` is a legacy hybrid that falls back to a hardcoded template when a page has no `content_blocks` (16 of its 34 pages do) — never author that branch.

| # | Section | Class | Required | What it holds | Input the author must supply |
|---|---|---|---|---|---|
| 0 | Promo banner | `#bfcm-banner` (fixed, above the header) | **Optional** (only when a promotion is running) | Promotion text and button | Ask whether a promotion is running; never add by default |
| 1 | Header | `header` | Required, common | Site header | none (from kit) |
| 2 | Hero | `c-hero-solution` | Required | H1, short lead, Start Trial + Book A Demo, hero image (right) | H1, lead, hero image or scene |
| 3 | Section breaker | `c-animated-trail-banner` | Required | Marquee strip of short trust phrases | Site-standard phrases unless told otherwise |
| 4 | Features | `c-features-section` | Required | Optional section H2, then one `feature-row` per feature: H3 + description + one image (alternating sides) | Feature headings, copy, one visual each (screenshot, or a scene) |
| 5 | Case studies | `c-casestudy-section` | **Optional** (whole section) | 1 to 2 cards relevant to this page's topic: "Case study" pill, quote, Learn More, thumbnail image. Thumbnails do not animate | Which case studies fit the page, quote text, link, thumbnail |
| 6 | CTA | `c-cta-section-solutions` | Required | Headline, one line, Start trial + Book A Demo, illustration at each side | Site-standard text unless told otherwise |
| 7 | FAQ | `c-faq-section` | Required | H2 "<Topic> FAQs", 3 to 9 accordion items | The questions and answers for this page |
| 8 | Footer | `footer` | Required, common | Trial CTA card (part of the footer, identical on every page), link columns, legal bar | none (from kit) |

Feature rows (section 4), tested against the live monitoring page:
- **Every feature row has the same structure**: half text, half image slot, alternating sides. Never mix in full-width rows, stacked rows or text-only rows on the same page.
- The image slot is a box `bg-surface-dark-lighter rounded-lg overflow-hidden md:border md:border-solid md:border-[#E8E8E8] p-4 flex items-center justify-center min-h-[220px] md:min-h-[340px] lg:h-[400px]` (about 549 by 400 at 1440 px). Note `lg:h-[400px]` is a **fixed** height, not `min-h`. The image inside is `object-contain w-full max-h-[280px] md:max-h-full`. Everything shown in it, including animated scenes, is fitted to it (`references/images.md`, `runtime/README.md` `pu-fit`).
- A feature with no visual supplied still gets its slot. Show a plainly labelled placeholder ("Feature visual needed"), list it as a missing input, never leave the row text-only.
- Heading level (**settled from code**): the section heading is `h2`, each feature heading is `h3`. `features-section.hugo.html` renders `<h2>{{ .heading }}</h2>` once and `<h3>{{ .feature_title }}</h3>` per row.

Notes:
- The CTA in section 6 is a page section; the CTA card inside the footer is not, it is part of the footer and never edited per page.
- Animated scenes belong in hero and feature images. Case-study thumbnails stay static.
- A required section with no supplied content is a **missing input**: ask for it at checkpoint 1, never invent it, and list it in the handoff if still open.

## Demo-led solution page (`/solutions/optmyzr-on-slack/`)

1. `c-sidekick-hero` (text left, animated chat card right)
2. `c-animated-trail-banner`
3. `c-sidekick-demos` (3 feature demos)
4. `c-sidekick-setup` (3 step cards + "Platforms We Support" logo row)
5. `c-cta-section-solutions`
6. `c-faq-section` (9 FAQs)
7. Footer

Note: the Slack sections are one-offs with hard-coded hex values and custom classes (`skh-card`, `skp-card`, `skp-ring`). For a new demo-led page, use the **token** values from `tokens/class-map.md` instead of copying the hex values, and tell the dev team which shared section names are new.

## Reading order for a new page

1. Pick the page type above. 2. Read its pattern file. 3. Take colors, type and radii from `tokens/class-map.md`. 4. Add scenes only inside a feature or demo section, never in the hero unless the brief says so. 5. List every difference from the pattern in the handoff.

## Still unverified for page types

Resolved by the repo pass on 2026-09-29: landing/demo-request, `/compare/`, `/products/social/`, `/products/amazon/`, `/products/ecommerce/` and case-study detail pages are all catalogued below, with their authoring models.

**Still open:** the Bookshop field names behind 84 of the 90 components (only the solution-page set has been read in detail), and how Tailwind purge treats classes not used elsewhere on the site.

---

## Full page-type inventory (verified from the repo, 2026-09-29)

1117 English content files. 145 carry an explicit `layout:`; 135 of those are composed from `content_blocks`. The remaining 972 (596 blog posts, author, careers, case-study, event and research-hub entries) carry no layout key — Hugo picks their template from the section. Those are **content, not composed pages**, and are out of scope.

### The five authoring models

Every page on the site is authored in one of five ways. Which one applies decides what the skill can change and whether a scene can go in at all.

| Model | What it means | Scene placement |
|---|---|---|
| **blocks** | The whole page is an ordered `content_blocks` array. Any section can be added, removed or reordered from front matter | **Direct.** Add a scene component, or put the scene in an existing component's image slot |
| **blocks-in-template** | A fixed template (breadcrumb, listing, pricing tables, related items) with a `content_blocks` region inside it | Direct, **inside the blocks region only** |
| **hybrid-legacy** | Renders blocks when present, else falls back to a hardcoded legacy template (`heroTitle`/`benefits`/`faqList`) | Direct, **on the blocks branch only**. Never author the legacy branch |
| **params** | A fixed template driven by named front-matter fields. Structure is not changeable from content | **Not directly.** A scene can only replace an existing image field, and only if the dev team adds a component — a kit gap |
| **body** | A markdown prose page plus a little metadata | **Not directly.** A scene in prose needs a shortcode the dev team must add — a kit gap |

### Where each page type sits

| Page type | Layout(s) | Pages | Model |
|---|---|---|---|
| Solution / landing | `v4-generic-solutions-page` (29, **use this**), `v2` (5, hybrid), `generic-solutions-page` (34, hybrid; 18 composed), `custom-api` (2) | 70 | blocks / hybrid-legacy |
| Comparison | `compare` | 17 | blocks |
| Homepage | `index` | 1 | blocks |
| About, Contact, Partners, Labs hub, Careers hub, Events hub, Thank-you, Demo request | `about`, `contact-us`, `partners/list`, `labs/list`, `careers/list`, `events/list`, `thank-you`, `demo-request-v2` | 8 | blocks |
| Pricing | `pricing-page-v2`, `headless-pricing-page` (+ legacy `pricing-page`) | 3 | blocks-in-template |
| Case study | `company/case-studies/single` | 41 | blocks-in-template |
| Blog hub, Compare hub, Learn-with-Optmyzr hub, Research-hub entry, Search | `post/list`, `compare/list`, `learn-with-optmyzr/list`, `research-hub/single`, `search` | — | blocks-in-template |
| Blog post | `post/single` | 596 | body + params |
| Content hub / guides | `content-hub` | 4 | body |
| Event, Careers opening, Author, PPC Town Hall, Research hub listing | various | 200+ | params |
| Capabilities (5 bespoke templates) | `one-click-opt`, `opt-express`, `data-insights`, `campaign-automator`, `slack-integration` | 11 | params + body |
| Legacy platform pages | `google-ads`, `ms-ads`, `amazon-ads`, `fb-ads`, `yahoo-ads`, `online-ads`, `advertisers`, `data-integrations`, `custom-solution` | 13 | params |
| Legal / policy | `privacy-policy`, `dpa` | 6 | body |
| One-off campaign pages | `blaze`, `amazon-standlone`, `optmyzr-vs-wordstream`, `agency-partner`, `campaign-automator-demo`, `for-ai` | 6 | params |

**For anything new, prefer a v4 solution page.** The legacy platform pages, capability templates and one-off campaign pages are bespoke and must not be reused for a new brief.

### Two traps that silently lose work

1. **`product-page-template`** declares `content_blocks`, but its layout `generic-product-page` never renders them. Blocks added to a product page are silently dropped.
2. **`content-page-template`** declares `content_blocks`, but `content-hub` renders only `.Content`. It is a prose page with a table of contents, not a composed page.

In both cases use the template's own fields, or raise it with the dev team.

### What is not a composed page at all

972 of 1117 English files carry no `layout:` key — Hugo picks the template from the section or `type`. These are content entries: 596 blog posts, 140 PPC Town Hall entries, 47 events, 41 case studies, author profiles, archived job roles. A brief for one of these is a **writing task with metadata**, not a page-composition task.

### Creating a page the way the CMS does

23 CloudCannon creation schemas exist under `.cloudcannon/schemas/`. Start a new page from the matching one so its front matter has the fields the CMS expects:

| Page type | Schema |
|---|---|
| Solution (current) | `v4-solution.md` |
| Solution (older) | `v2-new-solution-page-template.md`, `new-solution-page-template.md`, `3-step-hero-template.md` |
| Scene-led solution | `slack-sidekick-template.md` |
| Comparison | `comparison-template-generic.md` |
| Case study | `case-study-template-new.md` |
| Blog post | `blog-post-template.md` |
| Product | `product-page-template.md` |
| Research hub | `research-hub-template.md` |
| Learn with Optmyzr | `learn-with-optmyzr.md` |
| Content hub / guide | `content-page-template.md` |
| Event | `event-template.md` |
| Labs / free tool | `labs-template.md`, `free-tools-template.md` |
| Careers opening | `career-opening-template.md` |
| Partners | `partners-template.md` |
| Author | `author-template.md` |
| Tracking / thank-you | `tracking-pages.md` |
| PPC Town Hall | `ppc-town-hall.md` |
| Masterclass | `automation-layering-masterclass.md` |

Editing in the CMS is **English-only** — no collection points at `content/es|de|fr|jp`. The translation pipeline produces the rest.

### Solution page: measured section frequency

| Section (`_bookshop_name`) | v4 (29) | generic (18 composed) | v2 (4) | Verdict |
|---|---|---|---|---|
| `hero-solution` | 27 (93%) | 18 (100%) | 4 (100%) | required |
| `animated-trail-banner` | 29 (100%) | 18 (100%) | 4 (100%) | required — on every solution page without exception |
| `features-section` | 26 (89%) | 18 (100%) | 4 (100%) | required |
| `casestudy-section` | 1 (3%) | 14 (77%) | 4 (100%) | **optional, and being dropped** on v4 pages |
| `cta-section-solutions` | 28 (96%) | 16 (88%) | 4 (100%) | required |
| `faq-section` | 29 (100%) | 18 (100%) | 4 (100%) | required |

The v4 pages that omit `hero-solution` or `features-section` replace them with a bespoke animated block (`sidekick-hero`, `claude-connector-hero`, `sidekick-demos`, `mcp-features`), which is the precedent for a scene-led page.

### Comparison page, dominant sequence (11 of 17 pages)

`comparison-hero-slim` → `comparison-buyer-fit` → `comparison-built-for` → `comparison-only-on-optmyzr` → `mcp-use-cases` → `mcp-compatible-tools` → `comparison-pricing-cards` → `comparison-migration-section` → `comparison-table-accordion` → `comparison-casestudy-carousel` → `faq-section`

The other 5 use: `hero-comparison-indv` → `comparison-benefits` → `comparison-pros-cons` → `comparison-table` → `comparison-testimonial`.

---

## Section sequences for every composed page type

Derived the same way as the solution page: from the `content_blocks` of every English page, not
from guesswork. Machine-readable in `page-types.json` v4.

### Case study — 40 pages, fully prescriptive

| # | Section | Frequency |
|---|---|---|
| 1 | `case-study-hero` | 40/40 |
| 2 | `results-section` | 40/40 |
| 3 | `about-customer-section` | 40/40 |
| 4 | `result-details-section` | 40/40 |

**As repeatable as the solution page**, and the second-largest family on the site. The template
owns the breadcrumb and the related-blogs strip around these four blocks (`blocks-in-template`).

Two authoring traps here: `case-study-hero` reads `author` and `customerCompany`, and
`about-customer-section` reads `authorCompany` — none of which the blueprints default. Set them
explicitly or the section renders with holes.

### Homepage — 15 blocks, one page

`hero` → `trail-banner` → `products-section` → `features-section` → `steps-section` →
`bynumbers-section` → `casestudies` → `testimonial-section` → `reviews-section` →
`awards-section` → `perks-section` → `teams-section` → `animated-trail-banner` →
`cta-section-1` → `cta-section-solutions`

Highest-traffic page on the site. Changes need site-owner sign-off.

### The rest

| Page type | Sequence | Pages |
|---|---|---|
| **About** | `hero-about` → `team-bynumbers` → `founders-section` → `founders-slider` → `grid-images` → `animated-images` → `awards-about` → `timeline-section` | 1 |
| **Contact** | `hero-contact` → `contact-form` → `contact-offices-section` | 1 |
| **Demo request** | `hero-demo` → `demo-testimonial` → `demo-benefits` | 1 |
| **Product (Amazon)** | `amazon-hero` → `amazon-features-section` → `amazon-pricing` → `ppc-youtube-section` → `faq-section` | 1 |
| **Product (Social)** | `social-hero` → `social-features-section` → `cta-section-solutions` → `social-testimonials-section` → `faq-section` | 1 |
| **Labs** | `hero-labs` → `labs-cards` → (`cta-section-solutions`, `faq-section` optional) | 2 |
| **Partners** | `hero-partners` → `partners-cards` | 1 |
| **Research hub** | `research-hub-highlights` | 3 |
| **Careers** | `comparison-features` (3/4), with `hero-careers`, `values-section`, `perks-section` optional | 4 |
| **Thank-you** | `thankyou-section` | 2 |
| **Pricing** | `testimonial-section`, plus `reviews-section` on v2 | 2 |

### What this tells you about building a non-solution page

- **Case study and solution are the only two types with a proved, repeated structure.** Both can
  be built from the kit with confidence.
- **Most other types exist on a single page.** Their "sequence" is that one page's block list, so
  treat it as an example rather than a rule, and read the page before building a sibling.
- **Pricing is barely authorable.** Only two blocks; the tables, plan logic and currency handling
  are template-owned. Anything beyond swapping a testimonial is a dev-team change.
- **Careers has no stable shape** — four pages, four different block sets.

## Can the kit build a product page? Yes — via the live route

Checked against the repo and the live site rather than assumed:

| Route | Layout | State | Buildable from the kit |
|---|---|---|---|
| **Amazon-style** | `amazon` | **live** at `/amazon/` | **Yes.** 5 components, all captured |
| **Social-style** | `social` | **live** at `/social/` | **Yes.** 5 components, all captured |
| **Ecommerce-style** | `ecommerce` | planned at `/products/ecommerce/` | **Yes.** Follow amazon/social block sequence; purple/mustard theme via `data-product=ecommerce` |
| `generic-product-page` | params, 26 fields | every page `draft: true` | No — and don't |
| `ca-product-page` | params, 32 fields | draft, url ends `/deprecated` | No — and don't |
| `product-demos` | params | draft | No — and don't |

**Every live product page is block-driven.** The three params-driven templates are used only by
unpublished drafts, one of them explicitly named deprecated. A new product page follows the
amazon or social sequence.

```
amazon:     amazon-hero → amazon-features-section → amazon-pricing → ppc-youtube-section → faq-section
social:     social-hero → social-features-section → cta-section-solutions → social-testimonials-section → faq-section
ecommerce:  (follows the amazon/social block pattern — sequence defined when the first page is created)
```

Two things to know before starting:

- **`amazon-pricing` reads 10 fields the blueprint never defaults** (`accountsAdSpendArray`,
  `adSpend`, `enterprise`, `heroTitle`, `heroTitleEur`, `pricingPeriod`, `savings`, `subTitle`,
  `title`, `value`). Set them explicitly or the pricing block renders empty. `social-testimonials-section`
  has 2 copy fields outside the translatable-key list. Everything else in both sequences is clean.
- **Do not start from `product-page-template`.** It declares `content_blocks` but points at
  `generic-product-page`, which never renders them — every block is silently dropped. Copy
  `content/english/products/amazon.md` or `social.md` instead. For Ecommerce, copy one of those
  and set `data-product: ecommerce` in front matter; the purple/mustard theme activates automatically.
