# Captured site chrome

The real header, footer and promo banner, copied **verbatim from the live site** so a
preview looks exactly like the website. Refresh with:

```
python3 scripts/capture_chrome.py                     # default: /solutions/monitoring/
python3 scripts/capture_chrome.py --page <any page>   # e.g. to pick up a running promo banner
```

Never hand-write or simplify chrome. A hand-made copy drifts from the site the moment
anything changes, and the difference is exactly what a reviewer notices first.

| File | What it is |
|---|---|
| `header.html` | The full header, ~62 KB: product switcher, Products / Solutions / Resources / Company mega menus, Pricing, language picker, Log In, Start Trial, mobile menu |
| `footer.html` | The full footer, ~25 KB: trial CTA card, product and resource columns, social links, language picker, legal bar |
| `banner.html` | The promo banner, when one is running on the captured page |
| `chrome-scripts.html` | The **inline** scripts the chrome depends on — both the Alpine data providers and the non-Alpine mega-menu driver |
| `chrome-extras.html` | Elements the chrome scripts need that are **siblings** of `<header>`, not children (the mega-menu overlay) |
| `head-links.html` | Render-critical head resources: the site stylesheet, GSAP, the site animations and Alpine |
| `head-links.excluded.html` | What was deliberately left out, and why |
| `site-css.json` | The current stylesheet URL and when it was seen (`scripts/resolve_site_css.py`) |
| `chrome-meta.json` | Which page it came from, when, and what each part contains |
| `cta-section.html`, `trail-banner.html` | Section markup captured earlier from live pages |
| `header.simplified.html` | The old hand-made header. Kept only as a fallback; do not use it for fidelity |

## Three things that will bite you if changed

**1. No subresource integrity.** The live page serves the stylesheet with
`integrity="sha256-..."`, which is fine same-origin. A preview loads it **cross-origin**
(`file://`, `data:`, or a preview host), and a browser blocks an integrity-checked
cross-origin resource unless the server sends CORS headers. The page then renders
completely unstyled with no obvious error. `capture_chrome.py` strips the attribute for
this reason. **Do not put it back.**

**2. The menus need `chrome-scripts.html` AND `chrome-extras.html`.** The header's Alpine expressions call
`getCompanyData()`, `getMobileMenuData()`, `getSearchSolutionsData()` and friends, which the
live page defines in *inline* scripts further down the document — not in any `.js` file. Ship
the markup without them and the header renders but every menu throws `ReferenceError` and
never opens.

The **desktop mega menu is not Alpine at all**: a separate inline script attaches
`mouseenter` handlers to `.nav-link`, shows a popover, and toggles
`<div class="overlay ...">` — which is a **sibling of `<header>`, not a child**. Extract the
header alone and that script finds `null`, so the dropdowns silently never open. That is what
`chrome-extras.html` is for, and it must be emitted *beside* the header, not inside it.

The capture script therefore looks for two kinds of inline block: ones that define an
identifier the chrome's Alpine attributes reference, and ones that query at least two of the
chrome's own ids or class hooks (`nav-link`, `popover`, `overlay`, `data-nav`).

**3. Analytics is excluded on purpose.** Pagesense, Sentry, Partytown and chat widgets are
dropped (`head-links.excluded.html` lists them). A preview is not a visit: loading them would
send real telemetry from a page nobody asked for and pollute the site's own metrics.

## Two capture bugs worth not reintroducing

- **Attribute values in the live HTML are unquoted** (`x-data=getMobileMenuData()`), because the
  output is minified. A regex that only matches `="..."` finds nothing and ships a broken header
  while reporting success. Match quoted and unquoted forms.
- **Do not filter inline scripts by brand words.** An early version dropped analytics by looking
  for `facebook` / `linkedin` anywhere in a block — which silently removed the menu-data script,
  because the navigation contains links to those sites. Filter by analytics **domains**
  (`googletagmanager.com`, `browser.sentry`, `pagesense`, …) instead.

## Known preview-only artefacts

- **Fonts fail CORS over `file://` / `data:`** (`origin 'null'`), so the preview falls back to
  system fonts. Serve the preview over `http://` to see the real typefaces.
- The site's `animations.js` logs `Cannot read properties of null (reading 'classList')` for
  elements that only exist on the live page. Harmless, and gone once the page is in the repo.

## The handoff bundle has no chrome, on purpose

`handoff/page/main.html` contains the page sections only. Hugo's own base layout supplies
the header and footer in the repo, so shipping a copy would duplicate them.

## Refresh the parts together

`footer.html` was found stale on 2026-09-30 while `header.html` had been refreshed the
same day. The stale footer's Products column predated the Ecommerce product line, so
every page built from the kit shipped a footer missing "Optmyzr For Ecommerce" — and the
symptom appeared on two finished previews rather than at build time, because nothing
compares a captured part against the live site.

Two habits that catch it:

- **Refresh header, footer, scripts and banner in one run.** A per-part refresh leaves the
  set internally inconsistent, and the inconsistency is invisible in the file names.
- **After a refresh, check the product lists.** The nav and footer product columns are the
  parts that change when the company adds a product line, and they are the parts a stale
  capture gets wrong:

  ```bash
  grep -oE '>(Optmyzr [Ff]or [A-Za-z ]+)<' footer.html | sort -u
  grep -c 'Ecommerce' header.html footer.html chrome-scripts.html
  ```

  Every currently shipping product should appear in both the header and the footer. If one
  part disagrees with another, the capture is half-refreshed.

`chrome-meta.json` now carries a `refreshed` date and a note per part where one applies.
