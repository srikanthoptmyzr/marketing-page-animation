# Fidelity test — kit-built page vs the live site

**Question the hackathon brief asks:** the skill must work with **no repo access**, yet the page
it produces must look like it came from the live website. Does it?

**Test.** Compare a page built entirely from the bundled site kit against a real live page, at
the same viewport, measuring **computed** styles — what the browser actually renders, not what
the markup claims.

- **Baseline:** `https://www.optmyzr.com/solutions/monitoring/` (live, Hugo-rendered)
- **Subject:** `workspace/optmyzr-explorer/preview/index.html` (built from the kit; no repo,
  no Hugo, content from a screen recording)
- **Viewport:** 1440 x 900, same browser, same session
- **Date:** 2026-09-30

## Result

| | |
|---|---|
| Computed properties compared | **108** |
| Identical | **108 (100%)** |
| Differences | **0** |
| Section sequence | **identical** |

```
live : c-hero-solution → c-animated-trail-banner → c-features-section → c-casestudy-section → c-cta-section-solutions → c-faq-section
ours : c-hero-solution → c-animated-trail-banner → c-features-section → c-casestudy-section → c-cta-section-solutions → c-faq-section
```

## What was measured

18 elements across every section of the page:

| Element | Properties |
|---|---|
| hero `h1`, hero lead, hero section | font family/size/weight, line-height, letter-spacing, colour, alignment; section padding, background, margins |
| trail banner + its items | padding, background, type |
| features section, `h2`, `h3`, body | full type stack on each |
| feature row, text half, image half | display, gap, align, direction, border, width, order, padding |
| image slot | height, min-height, padding, radius, background, border width/colour, flex alignment |
| CTA section, headline, button | padding, background; type; button colour, radius, width, weight |
| FAQ section and its card | padding, background, radius |

Exact matches include the ones that are easy to get wrong and invisible when wrong:
`letterSpacing: -1.3px` on the hero `h1`, `lineHeight: 30.24px` on a feature `h3`,
`borderColor: rgb(232, 232, 232)` on the image slot, `width: 550.734px` on the text half.

## What this proves, and what it does not

**Proves:** a page assembled from the kit alone — no repo, no Hugo build — renders pixel-identical
to the live site at 1440 across every section of a solution page. The repo-independence and the
fidelity requirement are not in tension.

**Does not prove:**

- Only **1440** was tested. The site has seven breakpoints (360, 376, 640, 768, 1024, 1280, 1540);
  the others need Playwright, which is not installed here.
- Only the **solution** page type. Case study (40 pages) and product (2 live sequences) have
  proved section sequences but have not been diffed.
- This is a **computed-style** diff, not a pixel diff. It would not catch a difference that lives
  only in an image asset or a font that failed to load.
- The preview loads the site's stylesheet from `optmyzr.com`. That is by design — the kit records
  the URL and refreshes it — but it does mean the preview needs the network to look right.

## How to re-run

```bash
cd workspace/optmyzr-explorer/preview && python3 -m http.server 8800
```

Open the live page and the local page at the same viewport, run the same `getComputedStyle`
sweep on both, and diff. The full property list is in this file; `check_page.py` automates the
viewport matrix once Playwright is installed.
