# Marketing Page Animation Skill

A reusable Claude skill that lets marketing and customer-success staff, who have no access to the website's code, build **light, animated, multilingual marketing pages that look and are structured exactly like the company website**. It turns product screenshots and screen recordings into live HTML/CSS/JS scenes (never embedded images or video), replaces sensitive data with synthetic data, reuses the site's own localization, and ends with a **preview page** to review and a **handoff bundle** for the dev team, who integrate and publish. **The skill never pushes or publishes anything.**

Built for a hackathon by Srikanth. First reference site: Optmyzr (https://www.optmyzr.com). The skill itself is product-agnostic: nothing in the method is specific to one product.

> **Picking this up in a new Claude account or session? Read this file top to bottom, then `.claude/skills/marketing-page-animation/SKILL.md`, then `docs/consistency-report.md` section 4 (open decisions). Everything else loads on demand from `SKILL.md`. Do not restart or redesign; continue from "Current state" and "What is next".**

---

## 1. Who it is for and how it is used

- **Users:** marketing / customer-success people (and the maintainer himself) with **no repo access**.
- **Flow:** user gives a page brief (copy document), product screenshots/videos and the bundled **site kit** -> skill analyzes, storyboards, specs, privacy-replaces, builds, validates -> outputs **`preview/`** (shareable) and **`handoff/`** (for developers) -> **dev team integrates and publishes**. Users never push.
- **Intended distribution:** an organization-level Claude skill (Team/Enterprise; needs code execution), or copied into `.claude/skills/` for Claude Code.
- **Two modes:** **A** (default) site kit only, no repo; **B** inside a Hugo/Bookshop repo checkout (plugs into the dev team's Marketing-OS agents). Read-only repo access is only for building/refreshing the kit and for testing.

## 2. Non-negotiable rules (short list; full list in `SKILL.md`)

1. **Reconstruct, don't embed.** Screenshots/videos are inputs only. Product UI is rebuilt as live HTML/CSS/JS.
2. **Never hide real data, replace it.** No blur, no masks, no overlays. Sensitive values become random, format-preserving synthetic values, identical everywhere on the page. Originals live only in `.private/originals.json`. `leak_scan.py` is a gate.
3. **Never invent the website.** Header, footer, sections, classes and conventions come from the site kit. Missing pieces are flagged **kit gaps**; assumed ones **unverified**.
4. **Use the site's own localization.** Never a parallel i18n system. Shipped pages are per-language static pages (SEO); the bundle carries English source only.
5. **Final state first.** Every scene renders complete without JavaScript and with reduced motion.
6. **One markup, two homes.** Preview and bundle use the same scene markup.
7. **Images obey the slot, not the upload.** An uploaded image's own size is never used; it is cropped/padded to the site's slot and exported at the site's widths (`scripts/prepare_image.py`, `site-kit/image-specs.json`). Scenes obey the slot too (see 5).
8. **Never publish.** End state is preview + bundle. Pause at the **3 user checkpoints** (storyboard, scene spec, final review).
9. Originals / real customer data never appear in shared files, chat, reports or commits; refer to entity ids.

## 3. Current state (as of 2026-09-30)

| Area | State |
|---|---|
| Method: 14 phases, 3 checkpoints, 13 rules (`SKILL.md`) | Done |
| 17 reference files (one per topic) | Done, updated for slot fitting, zoom camera, smoothness, scroll reveal |
| Scene player (`runtime/scene-player.js` + `.css`) | Done: verbs, fit-to-slot, camera zoom, no-flash start, scroll-triggered play-once reveal |
| JSON Schemas, scripts (frame extraction, leak scan, scene validator, page checker, image prep, token normalizer) | Done |
| Site kit: tokens | Done (Figma export). Breakpoints and fonts now **verified from the repo** (`tokens/breakpoints-and-fonts.md`) |
| Site kit: page types | **Verified from the repo** (`c9ac095`, 2026-09-29). 21 page types catalogued with authoring models and a routing table (`site-kit/page-types.md`/`.json` v4, with section sequences for **every** composed page type) |
| Site kit: image slots | feature and hero-visual slots **verified from component code**; case-study and CTA slots still observed. **CTA art ships at 1x** (321px source at 321 CSS px) — soft on Retina, see `references/images.md` |
| Site kit: header/footer | **Verified.** The real header (62 KB, all mega menus, product switcher, mobile menu, language picker), footer, promo banner and the chrome's inline scripts captured verbatim (`scripts/capture_chrome.py`) |
| Site kit: component blueprints | **Verified.** All 90 captured with templates, fields and per-field localization status (`scripts/capture_component.py`), grouped in `components/CATALOGUE.md` |
| Localization discovery, translatable-field list | **Done and verified** — `site-kit/localization.md`. 306 translatable / 121 skip / 27 URL keys located |
| Component starter (`templates/page/`) | **Done.** Points at the repo's `claude-connector-hero` and lists the conventions to copy |
| **Product vertical theming** | **Documented and proved** (2026-09-30). `body[data-product="<key>"]` activates a per-product colour theme across **all** page types in that vertical — product pages, solution pages, landing pages, resource pages. Write teal Tailwind classes in HTML; a CSS override block in `build.py` maps them to the product palette at render time. Ecommerce purple scale fully documented, including: missing Tailwind utility classes to declare manually, nav token gotchas, footer card class distinction, Login button secondary-CTA rule, and localisation fix for `file://` previews. See `references/design-system.md` section on product theming. **Known gap:** `workspace/optmyzr-ecommerce/build.py` still missing `data-product="ecommerce"` — needs the same override block as `workspace/google-shopping/` |
| **Optmyzr AI test page** (`workspace/optmyzr-ai/`) | Built and previewable (see 4). Rebuilds cleanly on the Mac. Not yet verified under the real site stylesheet in a full render. **A real page already exists at `/solutions/optmyzr-ai/`** — see 7 |
| **Fidelity: does a kit-built page look like the live site?** | **Proved at 1440.** 108 computed properties across 18 elements, live `/solutions/monitoring/` vs the kit-built Explorer page: **108/108 identical, section sequence identical**. No repo, no Hugo. See `docs/fidelity-test-explorer.md`. Still untested: the other six breakpoints, and page types other than solution |
| **Shippable as an org skill** | **Yes.** Kit is self-sufficient: 90 components, full chrome, 21 page types, localization answers, cached stylesheet URL. Only `capture_component.py` needs a repo, and that is a maintainer tool. Zip the folder with `SKILL.md` at its root — 2.5 MB, 345 files |
| **End-to-end run on a real screen recording** | **DONE.** `workspace/optmyzr-explorer/` — a full solution page for Optmyzr Explorer built from a 5-minute recording: 4 live scenes, copy, case study, FAQ, preview + handoff bundle, privacy gate passed (0 blockers), all scene specs 0/0 |
| **Google Shopping solution page** (`workspace/google-shopping/`) | **DONE** (2026-09-30). Ecommerce vertical, 7 scenes from 7 screenshots, 0 privacy blockers, 0 scene validation errors, full ecommerce purple theming applied end-to-end, preview + handoff bundle. 3 designed sections (problem-answer, steps-cards, audience-tabs). Row 4 ships a placeholder (no screenshot supplied). Open: quote approvals, FAQ count (12 vs site norm 3–9), URL/folder confirmation. See section 4a |

## 4a. Google Shopping solution page: `workspace/google-shopping/`

An ecommerce-vertical solution page built from a copy doc and 7 product screenshots — **the first page built under a non-Search product vertical**. It proved the full ecommerce theme system end-to-end.

**Product vertical:** Ecommerce → `data-product="ecommerce"` on `<body>`, purple palette via the `ecommerce_theme` CSS override block in `build.py`.

**Page structure:** hero → trail banner → problem-answer section (designed) → features (8 rows, 7 live scenes + 1 placeholder) → steps-cards section (designed) → audience-tabs section (designed) → CTA → FAQ (12 items) → footer.

**Scenes (all 0 errors / 0 warnings):** `gs-campaign-structure`, `gs-campaign-type`, `gs-sync-schedule` (also hero), `gs-performance-buckets`, `gs-rule-engine`, `gs-sidekick-answer`, `gs-sale-day-command-center`.

**Outputs:** `preview/index.html` (self-contained, ecommerce-themed), `handoff/` bundle (page content, 3 new component files, 7 scene partials, assets), `spec/`, `reports/` (0 privacy blockers, 0 scene errors).

**What the ecommerce theming work discovered** (documented in `references/design-system.md` and the Claude memory files):
- Several purple Tailwind utility classes don't exist in the site's purged stylesheet and must be declared manually (`bg-colorPrimaryPurpleLight`, `bg-colorPrimaryPurpleNormal`, `text-colorPrimaryPurpleNormal`)
- `text-textonteallight1` internally resolves to `var(--product-dark)`, making nav items purple — must be reset to neutral
- `group-hover:text-teal` bare selector is always-on; must be scoped to `.group:hover .group-hover\:text-teal`
- Two CTA sections exist with different classes: mid-page "Connect your feed" uses `.bg-surface-dark-dark`; footer "Experience Optmyzr" card uses `.bg-tealdark3` inside `<footer>` — scope overrides accordingly
- `getInitialTab()` in the captured header appears 4 times; replace only the function body, not `this.selected = this.getInitialTab()` (which would hit all 4 instances and break Resources mega-menu)
- Localisation in `file://` preview: set `__translationMap={}` and define `showLangFallbackToast` to open the live site in a new tab instead

**Rebuild:** `cd workspace/google-shopping && python3 build.py`

**Open (need your answers before handoff):**
1. Row 4 "Fix feed issues" — no screenshot supplied; ships a placeholder
2. Customer quotes (Jørgen Schultz, Shae Cullum, Matthieu Tran-Van) — approved for publishing?
3. 12 FAQs — keep all or trim to the site's norm of 3–9?
4. URL (`/solutions/google-shopping/`) and content folder (`solutions-new/`) — confirm
5. Promo banner — is a promotion currently running?

---

## 4. The test page: `workspace/optmyzr-ai/`

A solution page built from an uploaded copy document (`input/copy.docx`) and three UI screenshots (`input/image1-3.png`, real data, git-ignored) to prove the method on the real site's structure.

**Solution-page structure (confirmed by the site owner, checked against live /solutions/monitoring/):** promo banner (optional) -> header -> hero (required) -> section breaker `c-animated-trail-banner` (required) -> features `c-features-section` with `feature-row`s, image per feature (required) -> case studies (optional, static thumbnails) -> CTA `c-cta-section-solutions` (required) -> FAQ `c-faq-section` (required) -> footer with its own CTA.

**Three scenes** (all validate 0 errors / 0 warnings; validate each with its own content file):
- `sidekick-copilot`: chat with typed question, loading dots, streamed answer (design 600x368)
- `rsa-ai-headlines`: RSA ad-copy suggestions with camera zoom to the ad preview (680x460)
- `shopping-ai-buildout`: shopping AI build-out with zoom to the text area (760x460)

Scene design widths are in `build.py` (`FIT_W`); the height they must fit into is `SLOT_H = 368`, a property of the slot, not the scene. Conflating the two is what made every scene render at half size.

**Layout decisions made:** all feature rows are **uniform** half-text/half-image, alternating, image box `lg:h-[400px]` (fixed height, verified from `features-section.hugo.html`), scene scaled *down* to fit the slot (never up, never cropped). Rows without a scene get a placeholder `Feature visual needed`. CTA text is the site-standard text (needs approval). FAQ is **test content borrowed from the monitoring page**.

**Outputs (regenerate with `cd workspace/optmyzr-ai && python3 build.py && python3 make_spec.py`, in that order):**
- `preview/index.html` and `preview/optmyzr-ai.single.html`: both self-contained (CSS+JS inlined). **The long-standing "index.html looks unstyled" bug is solved:** the captured stylesheet link carried a subresource `integrity` attribute, which browsers block cross-origin, silently unstyling the whole page. `capture_chrome.py` now strips it. Needs internet for the live site stylesheet, fonts and header images.
- `handoff/`: `page/main.html`, `scenes/*.html`, `assets/`, `content/`, README (includes "FAQ (test content)").
- `spec/`, `reports/privacy.md`, `reports/validation.md`.
- Sources: `build.py` (page generator: `rows()`, `fig()`, timelines, `faq_html()`), `scenes.css`, `page.css`, `make_spec.py`, `input/`.

**Artifacts published on claude.ai** (private): an approximate page preview (imitation; the artifact CSP blocks the site's stylesheet and images) and a status page ("Page Skill Status", https://claude.ai/artifact/4RuNya3g7zDjDKj576XT3J). **The status page is stale**: it does not mention zoom camera, uniform rows, fit-to-slot, smoothness fixes or scroll reveal. An older non-native artifact may be deleted if the maintainer agrees. These artifacts belong to the old Claude account; recreate them in the new one only if wanted.

## 5. How scenes work (must-know before editing)

- **Model:** final-state-first markup; `data-target` / `data-text` / `data-input`; timeline states with `visible` lists; verbs `enter-state, stream, type, click, cursor-moves, hide, zoom, zoom-out, ...`. Only `opacity` and `transform` animate. Recipes are preferred over raw verbs in docs.
- **Fit to slot:** `figure.product-ui.pu-fit[data-fit-from=1024][data-fit-width][data-fit-height]`. The player lays `.pu-stage` out at the design width and scales it down with a transform; controls and caption stay full size; below 1024 px the scene is responsive. `.pu-stage` is the container-query container (`container-type:inline-size`), text size `clamp(12px,1.9cqw,15px)`.
- **Camera zoom:** `.pu-cam` wrapper (only if the timeline has zoom). `zoom` frames a target (pad 0.06, capped by `scale`, skipped if under 1.25x), `zoom-out` returns to identity. Zoom only where it proves something (reading a small detail), never random, never cropping left/right. RSA and buildout have zoom; Sidekick has none.
- **Smoothness:** no per-frame DOM rebuilds (typing/streaming reuse two spans and update only when the count changes), `will-change` during moves, `geometricPrecision` text, `data-speed=1.35`, `START_DELAY 250`.
- **No flash:** text prims are rendered empty at start; `pu-js` is set on `<html>`; the scene gets `pu-ready` after setup; the stage is hidden until ready; the player loads in `<head>`.
- **Scroll reveal (latest feature):** below-the-fold `[data-reveal]` blocks (+`data-reveal-delay`) fade up **once** when scrolled into view (`pu-rv-pending` -> `pu-rv-in`); scenes inside start about 350 ms later and only when watched; scrolled past mid-run = pause and resume, not restart; replay only via the control; reduced motion = no reveal.
- **Host CSS resilience:** the site's Tailwind preflight makes svg block and removes list markers, so scenes set `.ic{display:inline-block}`, `list-style:decimal`, `.pu-how` inline-flex nowrap, and use a `.pu-slot` overlay for loading dots.
- **Validator:** `scripts/validate/validate_scene.py` (VERBS include zoom, zoom-out).

## 6. Known site facts (observed; verify with repo)

Hugo + Bookshop `c-*` components, one generated Tailwind stylesheet `https://www.optmyzr.com/websitecss/styles.min.<hash>.css` (hash changes each deploy; only classes already used live exist), Alpine + GSAP, global `toggleFaq(this)` for the FAQ. Fonts: DM Sans (headlines), Inter (body). Languages per dev docs: English + Spanish, German, French, Japanese (`jp`), Danish disabled.

**Image slots (observed):** feature = contain, aspect 1.2-2.0, widths 256/512/767 (shown up to about 549x400 at 1440); case-study thumb = cover 16:9, 542/1084; CTA side = cover 321:412, 321/642; hero visual = unverified.

## 7. Open decisions (waiting on Srikanth)

1. ~~Feature headings h2 or h3?~~ **Settled from code: section `h2`, feature headings `h3`.**
2. Real FAQ content for the **AI** page — available in `content/english/solutions-new/search/AI-in-Optmyzr.md`. Decide whether to adopt it. (The Explorer page has its own FAQ, written from the recording.)
3. Case studies — the live AI page uses **3** `casestudy-section` blocks, though v4 pages are dropping them. And whether a hero visual (Sidekick scene?) is wanted.
4. ~~Scaled scenes have small text (about 8px)~~ **Settled: shorter scene copy.** Design width = usable slot width / 0.85 (~600px for a feature slot). Recomposing took the Explorer scenes from 0.50 scale / 8px text to 0.86-0.90 / 13.5-16.3px. The player now warns below 0.8.
5. **Explore mode** design for scenes (autoplay then unlock exploring, or start ready with an optional demo).
6. CTA text approval — the live page's own CTA text is available to copy.
7. The items in `docs/consistency-report.md` section 4 (token naming `--site-*`, meaning of "verified", where copy lives in `scenes.json`, recipes vs generic verbs in examples, `privacy-map.json` in the bundle, shared persona across pages).
8. Delete the old non-native artifact?
9. **Google Shopping open items** — see section 4a above (quote approvals, FAQ count, URL, row 4 placeholder, promo banner).
10. **`workspace/optmyzr-ecommerce/`** — the ecommerce product page workspace has no `data-product="ecommerce"` and no `ecommerce_theme` override block yet. Apply the same theming checklist as `google-shopping/`. Confirm this is the next page to complete.

## 8. What is next

1. **Resolve Google Shopping open items** (section 4a) so the handoff bundle can go to the dev team. The page itself is complete; only approvals and confirmations are blocking.
2. **Apply ecommerce theming to `workspace/optmyzr-ecommerce/`** — add `data-product="ecommerce"` to `<body>` and the full `ecommerce_theme` CSS override block (checklist in `references/design-system.md`). This is the product page companion to the solution page.
3. **Run the fidelity test.** Still the biggest gap. Feed a live page's content through the kit and diff DOM and pixels at 360/376/640/768/1024/1280/1440/1540. Until this runs, "verified" in `MANIFEST.md` means *read from code*, not *proved to reproduce a page*. Needs Playwright (`pip3 install playwright && python3 -m playwright install chromium`).
4. **Decide the Explorer page's open questions** (`workspace/optmyzr-explorer/spec/storyboard.md`): positioning, availability, supported platforms, whether the table writes back, and real case-study content. Everything marked `[confirm]` in `spec/copy.md` rests on "assume yes" from the test run.
5. **Ship 2x images.** Site art is currently referenced at 1x with no `srcset`, so it is soft on Retina. Either capture the site's `<picture>` markup or route art through `prepare_image.py`.
6. **Mine what is left from the repo:** navbar/footer data files (playbook step 4), the image pipeline (step 6), Marketing-OS integration (step 8).
7. **Re-run the AI test page** on the corrected kit (h3 headings, `lg:h-[400px]`, design widths, real chrome) so both workspaces match the verified kit.
8. Implement `switch-tab` and `scroll` recipes, and explore mode.
7. Optional dev-team message: the 13 components whose templates read undefaulted fields, and the 45 with copy outside the translatable-key list.

## 9. Folder layout

```
README.md                          this file
docs/                              architecture.md, workflow.md, consistency-report.md,
                                   fidelity-test-monitoring.md, kit-from-repo.md
examples/optmyzr-slack/            raw Figma variables + normalized tokens
workspace/optmyzr-ai/              the test page (input/ is git-ignored, real data)
.claude/skills/marketing-page-animation/      <- THE SKILL
  SKILL.md                         orchestration: 14 phases, checkpoints, rules
  references/                      animation-system, images, responsive, ui-reconstruction, ui-scene-system,
                                   privacy-masking, localization, validation, handoff-bundle, site-kit, ...
  site-kit/                        MANIFEST.md, page-types.md/.json, image-specs.json, patterns/, captured/, tokens/
  runtime/                         scene-player.js/.css, README, demo/
  schemas/  scripts/  templates/
```

## 10. Environment and tooling notes

- **Locations:** cloud workspace `/mnt/user-data/outputs/marketing-page-animation-skill/`; maintainer's Mac `/Users/saisrikanth/Documents/websiteskill/`. On the Mac the skill lives at `skill/marketing-page-animation/` because the file-copy tool cannot write into a `.claude` folder. A symlink now bridges the two: `.claude/skills/marketing-page-animation -> ../../skill/marketing-page-animation`, so Claude Code loads the skill and `workspace/optmyzr-ai/build.py` (which hardcodes the `.claude` path) resolves. One source of truth, no copy to keep in sync. For an org skill, zip the real folder with `SKILL.md` inside.
- **Read-only repo checkout:** `~/Documents/marketing-website`, a sibling of this project. Cloned with `--depth 1 --single-branch --filter=blob:none` plus a sparse-checkout that excludes raster and video blobs, because a full clone stalled at 400 MB on a slow link. Auth is SSH as `srikanthoptmyzr` (`~/.ssh/id_ed25519_optmyzr`). **Never push, commit or modify anything there.**
- Files reach the Mac with `device_commit_files` (`stagedPath` under `/mnt/user-data/outputs`, at most 50 files per call). A new account starting from the Mac folder alone can work from those files directly.
- Cloud Playwright cannot load optmyzr.com CSS/fonts and `file://` cannot be opened in the browsers there; test with headless Playwright and injected resets. The real look must be checked on the Mac with internet.
- Artifact CSP blocks external stylesheets and images, so any shared artifact is an approximation.
- Requirements: Python 3, Playwright + Chromium, `ffmpeg`/`ffprobe`.

```bash
python3 .claude/skills/marketing-page-animation/runtime/demo/test_player.py --shots /tmp/shots
python3 .claude/skills/marketing-page-animation/scripts/validate/validate_scene.py \
  workspace/optmyzr-ai/spec/scene.sidekick-copilot.json --content workspace/optmyzr-ai/spec/content.sidekick-copilot.en.json
python3 .claude/skills/marketing-page-animation/scripts/validate/leak_scan.py \
  --originals .private/originals.json --map workspace/optmyzr-ai/spec/privacy-map.json \
  --scan workspace/optmyzr-ai/preview workspace/optmyzr-ai/handoff --exclude 'scene-player.*'
```

## 11. Working style Srikanth expects

- Follows his instructions literally. When he flags a visual problem (jitter, cropping zoom, mixed layout, text popping before typing), fix the cause in the runtime and the skill docs, not just the test page, and **update the matching `.md` files** in the same pass.
- Animation must be smooth, fast and purposeful; scenes must fit the section image slot; the whole features section must look uniform; recompose layouts compactly instead of shrinking a wide layout.
- Explain briefly, ask before big design choices, and always say what is untested.

## 12. When repo access is given (read this before touching the repo)

Follow the full playbook in `docs/kit-from-repo.md` ("Repo-access playbook"). In short, in order:

1. **Setup:** read-only, record repo/branch/commit hash. Never edit, commit, push or deploy in the repo.
2. **Inventory:** map folders (content, layouts, Bookshop component library, data, i18n, assets, config) and list every `c-*` component with its fields, template, CSS and scripts.
3. **Identify page types:** group real pages by layout/front matter (solution, homepage, pricing, product/tool, listing, blog, case study, demo request, comparison...), extract each type's ordered sections (required/optional, repeat rules, allowed components). Confirm the solution-page structure from code.
4. **Header and footer:** capture the complete versions (mega menu, product switcher, mobile menu, language picker, promo banner slot, footer CTA) and the data files that feed them; replace the simplified copies.
5. **Localization discovery** (`references/localization.md`): active languages/codes/URL prefixes, where English source lives, the translatable-key config, translation process and parity validator, language switcher, hreflang/SEO rules, helpers, CJK font coverage, RTL, terms not to translate. Decide where scene text and UI labels must live.
6. **Styles, tokens, images:** Tailwind config, breakpoints, missing tokens, class map, fonts, image pipeline and every section's image slot (including the hero visual); resolve the `--site-*` naming decision.
7. **Scripts and animation:** how Alpine/GSAP/page scripts load, existing scroll-reveal conventions (reuse them), how a component registers its script, where `scene-player` should live.
8. **Marketing-OS:** read the agents/commands/skills docs to learn how the dev team makes and reviews pages; define how Mode B plugs in and what the handoff bundle must contain.
9. **Fidelity tests:** for each page type feed a live page's content through the kit and compare DOM and pixels at 390/768/1024/1440; only then mark it `verified` in `site-kit/MANIFEST.md`.
10. **Re-run the Optmyzr AI test page** on the verified kit (real header/footer, correct localization fields, h2 vs h3 from code), then update MANIFEST, consistency report, and this README.

## 13. Which Claude tool to use once the repo is available

Use **Claude Code** (desktop app "Code" tab or terminal) opened in a local checkout of the repo, with this project folder added as a second working directory (or a sibling folder). Reasons: it reads the repo directly, can run Hugo/Node/Tailwind/Playwright locally with the real site CSS and internet (which the cloud session could not do), and can load this skill from `.claude/skills/`. Keep the repo read-only and write only into this project's `site-kit/` and `docs/`. Copy `skill/marketing-page-animation/` to `.claude/skills/marketing-page-animation/` first. Use Cowork/chat only for non-repo work (writing, reviewing, briefing). If the new account is a company (Team/Enterprise) account, the finished skill can later be uploaded as an organization skill.

## 14. Prompt to paste into the new Claude account

> I'm continuing the "Marketing Page Animation Skill" hackathon project (folder `websiteskill` / `marketing-page-animation-skill`). Read `README.md`, then `.claude/skills/marketing-page-animation/SKILL.md` and `docs/consistency-report.md`. The Optmyzr AI test page is in `workspace/optmyzr-ai/` (rebuild with `python3 build.py && python3 make_spec.py`). Follow the rules in README section 2 (never publish, replace not mask, originals stay private). If I give you the repo, follow README section 12 and `docs/kit-from-repo.md` (read-only). Otherwise work through README section 7 (open decisions) with me and section 8 (next steps), starting with: <your task>.

## Glossary

- **Scene:** one animated reconstruction of a product moment that proves one claim.
- **Site kit:** bundled snapshot of the website's tokens, patterns, header/footer, image slots and conventions, each with a status (verified, observed, unverified, missing).
- **Kit gap:** something the page needs that the kit lacks; listed for the dev team.
- **Handoff bundle:** what the dev team receives (content in the site's format, components, assets, spec, reports). English source only.
- **Entity (privacy):** one real thing (account, campaign, person) with one id and one replacement everywhere.
- **Slot:** a fixed image area on the site; uploads and scenes are fitted to it.

## Safety notes

- `input/`, `analysis/`, `.private/` and any OCR output contain real customer data. They are git-ignored and must never enter `preview/`, `handoff/`, reports, commits or chat.
- Do not paste real values from references into any file or message.
- The skill does not decide legal or compliance questions; have material reviewed before publishing or sharing the preview link.
