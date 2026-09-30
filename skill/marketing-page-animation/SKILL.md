---
name: marketing-page-animation
description: Build a new marketing or sales page, or a page section, that tells a product story with animated product UI and looks native to the company website. Takes a page brief and feature screenshots or videos, uses the bundled site kit for design, layout and conventions, rebuilds the product UI as live animated components instead of embedding screenshots, replaces sensitive data with synthetic values instead of blurring, and produces a shareable preview page plus a handoff bundle for the dev team. Needs no repo access. For edits to existing pages, use marketing-edit instead.
---

# Marketing Page Animation

Build a **product story**, not just a landing page. A visitor should understand what the product does by watching it work, in scenes that are light, animated, translatable and safe to publish.

Core rule: when a reference (video or screenshot) shows an interaction, **recreate that interaction as an animated HTML/CSS/JS scene**. Do not embed the screenshot or video. Fall back to a raster asset only when a UI genuinely cannot be reconstructed, and record why.

## Who this is for and how it ends

The user is on the marketing or customer-success team. They do not have, and do not need, access to the website's code. They build a page with this skill, review it, and **hand it to the dev team**, who integrate and publish it. This skill never pushes, merges or publishes to the live site.

Every run produces two outputs:

1. **Preview page.** A self-contained page that looks and animates like the real site, with the site's header, footer, tokens and layout patterns. The user reviews it and can share it with stakeholders.
2. **Handoff bundle.** Everything a developer needs to add the page to the site: the scene as a site-style component, the page content in the site's format, UI strings, assets, the scene spec, a plain-language note, and the validation report. See `references/handoff-bundle.md`.

## Two modes

- **Mode A (default): site kit.** No repo access. The bundled **site kit** (`site-kit/`) supplies the site's tokens, fonts, header and footer, section patterns and conventions. Output goes to a folder the user chooses. Read `references/site-kit.md`.
- **Mode B: inside the repo.** Only when the user is working in a checkout of the site (a `component-library/` folder and a Hugo config are present) and says so. Write directly into the repo's editable areas, following `references/hugo-bookshop-target.md`, and in a Marketing-OS repo also `references/marketing-os-integration.md`. The bundle is then not needed, but the report still is.

If unsure which mode applies, use Mode A.

## Never invent the website

Menus, navigation, header, footer, forms, cookie banners, the section order of a known page type and its hero come from the site kit, never from imagination. Never "improve" a component that already exists. Conventions that come from documentation rather than the real code are marked **unverified** and listed in the handoff.

**The one exception is a content section.** The component catalogue was built from pages making other arguments, so a brief that says something new may need a section that says it. When no component fits, work the decision ladder in `references/new-sections.md` — the honest answer is often an existing component, two components side by side, or cutting the section — and only then design one, delivered as a Bookshop component with a rationale and recorded as a **kit gap**. A new section may say something new; it may not say it in a new visual language.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Page brief | yes | Product or feature, objective, audience, key messages, CTA. Starter: `templates/brief.template.md` |
| Feature screenshots | at least one of images or videos | Key states of the product UI |
| Feature videos | at least one of images or videos | Screen recordings showing interactions |
| Site kit | bundled | Design, layout and conventions. Check its status first |
| Languages | from the kit | The kit lists active languages. Never hard-code a list |

If a required input is missing or unusable, ask before starting. Never invent product UI that is not in the references.

## Working directory

Ask where to work if it is not obvious. Analysis material contains real customer data, so it stays out of anything that gets shared.

```
marketing-pages/<slug>/
  input/        brief, references/{images,videos}
  analysis/     frames, contact sheets, inventory.md
  spec/         storyboard.md, scenes.json, design-system.json, design-mapping.md, privacy-map.json (replacements only, no originals)
  preview/      the preview page (shareable)
  handoff/      the handoff bundle (shareable)
  reports/      validation report, privacy report (no original values), screenshots
  .private/     originals.json, OCR output, frame notes: original sensitive values (never shared, git-ignored)
```

Never put `input/`, `analysis/` or `.private/` into `preview/` or `handoff/`. In Mode B, keep this work directory outside the shipped areas (for example in the repo's untracked artifacts folder) so it is never staged.

## Phases

Work through the phases in order, starting at phase 0. Load the reference file named in each phase when you reach it, not before. Later phases may send you back; fix things at the earliest artifact they affect.

**Phase 0. Check the environment (before asking the user for anything).**
Run `scripts/preflight.py`. It reports which optional capabilities exist here: image fitting (Pillow), video frame extraction (ffmpeg/ffprobe) and the headless browser (Playwright). If anything is unavailable, say so **in plain language at the start**, name what it affects, and take the documented fallback — do not discover it at phase 5 or 14 after the user has done work. **Never ask the user to install anything**; they may have no way to. The privacy gate and the scene validator are pure Python and always run, so the safety gate never degrades.

**Phase 1. Understand the brief.**
**Unpack the inputs first.** Whatever the user supplied — chat, `.docx`, PDF, deck — extract every embedded image into `input/references/images/`, name each for what it shows, and **count them**. That count is the denominator for the rest of the job: every one must either reach the page or be listed as deliberately unused (`references/reference-scanning.md`). An image sent in chat supersedes an older one of the same screen in a document; if they differ, say so.

**Determine the product line.** Ask which Optmyzr product the page belongs to if the brief does not state it. The four products are **Search**, **Amazon**, **Social** and **Ecommerce**. Product selection determines:

- The `data-product` attribute on `<body>`, which activates the site-level color theme (`--product-primary`, `--product-dark`, `--product-light`, etc.).
- The header tab that appears selected and the product dropdown highlight.
- The scene accent palette (teal/lime for Search, blue/orange for Social, yellow/fuchsia for Amazon, purple/mustard for Ecommerce).
- The content path routing (solutions, resources, blog categories).

Record the product in the brief restatement. If the user says "Ecommerce", set `data-product="ecommerce"` on `<body>` and use the purple/mustard palette for scene accents.

Restate the brief in a few lines. **Route the brief to a page type** using the routing table in `site-kit/page-types.md`: the user's words ("landing page", "solution page", "resources page", "case study", "blog post") map to one of 21 catalogued types. Then check `site-kit/page-types.json` for that type's **authoring model**, because it decides what is possible:

- `blocks` / `blocks-in-template` / `hybrid-legacy` — buildable, scenes go in directly (in the blocks region only, for the middle one).
- `params` or `body` — the page's structure is owned by a template, so a scene needs a dev-team change. Say so before starting, and offer the nearest buildable type instead.
- If no row matches the brief, say so and ask. Never invent a page type.

**How much the kit actually knows about the type you routed to** — say which of these you are in:

| Confidence | Types | What it means |
|---|---|---|
| **Proved** | solution (70 pages), case study (40, fixed 4 sections), product (both live sequences) | The structure repeats across many real pages. Build it |
| **One example** | homepage, about, contact, demo-request, partners, labs, research hub, thank-you | The "sequence" is one page's block list. Read that page and copy it; do not treat it as a rule |
| **Barely authorable** | pricing (2 blocks; tables and plan logic are template-owned), careers (4 pages, 4 different shapes) | Say so before starting. Most of the work is a dev-team change |

Two traps that lose work silently, both recorded in `site-kit/page-types.md`:
`product-page-template` and `content-page-template` declare `content_blocks` that their layouts
never render. And before authoring any component, check its `fields.json` in
`site-kit/components/` for fields the template reads but the blueprint does not default —
13 components have them, including two used on 40 case studies each.

Then check the type's required sections; every required section without supplied content is a missing input to ask for now (for a solution page: FAQs, hero visual, and whether case studies apply). Ask whether a promo banner is running. List gaps and assumptions. Ask about anything that changes the outcome. Reference: `references/page-storytelling.md`, `site-kit/page-types.md`.

**Phase 2. Identify the marketing objective and target audience.**
Name one primary objective and one primary audience. Decide what a visitor should believe and do by the end. Reference: `references/page-storytelling.md`.

**Phase 3. Propose the page structure and storyboard.**
Write `spec/storyboard.md`: narrative arc, each section's job, which reference feeds which scene, the claim each scene proves, and which kit patterns each section uses. Start from the closest page type in `site-kit/page-types.md`. For any section with no matching component, **name its archetype** (stats, social proof, audience split, process, comparison…) and the house pattern that archetype already has, before thinking about layout — a section whose archetype you cannot name is a section whose purpose is not yet clear. Flag it in the storyboard as designed, so approval covers it. Present it in plain language. **Pause for approval.** Reference: `references/page-storytelling.md`, `references/site-kit.md`, `references/new-sections.md`.

**Phase 4. Analyze feature screenshots.** **Scan before you build** (`references/reference-scanning.md`). Extract every image from whatever the user supplied — chat, `.docx`, PDF, deck — count them, look at each at full resolution, then run `scripts/scan_reference.py` for its palette, page background, section bands and column gutters, and `scripts/extract_palette.py` across all of them to build and verify the scene theme. Measure, then build: a reconstruction made from an impression of an image looks finished, so nobody catches it. Then produce one structured analysis record per screenshot. Register every sensitive value as an entity in `.private/` the first time it is seen and refer to it by entity id from then on. Reference: `references/screenshot-analysis.md`, `references/feature-analysis.md`.

**Phase 5. Analyze feature videos.** Extract frames, find scene boundaries, build an observation timeline with timing and confidence, and list every uncertainty. Check frames near every state change for brief or hover-only sensitive values, and register them the same way. Reference: `references/video-analysis.md`, `references/feature-analysis.md`.

**Phase 6. Identify components, content, states, interactions and transitions.**
Consolidate phases 4 and 5 into `analysis/inventory.md`. Flag anything unreadable or ambiguous. Do not invent text you cannot read.

**Phase 7. Convert observations into a UI scene specification.**
Write `spec/scenes.json`: the single source of truth for each scene's components, copy, sensitivity classes, timeline, final state and description. Summarize in plain language. **Pause for approval.** Reference: `references/ui-scene-system.md`, `references/ui-reconstruction.md`.

**Phase 8. Privacy-safe data replacement (required gate, before any code).**
Every sensitive value found in the references is replaced by a randomly generated, format-preserving synthetic value, the same everywhere on the page. Never blur, partially mask (`••••7890`), overlay or hide with CSS or scripts. The replacement is generated from the value's format, never derived from the original. Originals live only in `.private/`; the spec, code, content, data, translations and assets get the resolved values. Phases 9 to 14 may not start until the privacy map exists and every entity reference in the spec is resolved. Reference: `references/privacy-masking.md`.

**Phase 9. Reconstruct the product UI as HTML/CSS/JS.**
Build each scene **once** as a portable component from the sanitized spec, authored in its final state, so the same markup serves both the preview and the bundle. Reference: `references/ui-reconstruction.md`.

**Phase 10. Create animation timelines.**
Turn observed interactions into declarative timelines played by the shared scene player, with a reduced-motion path. Motion is smooth and quick, text never pops before it types, and `zoom` is used only where it helps (`animation-system.md`). Reference: `references/animation-system.md`.

**Phase 11. Apply the website design system.**
Map the supplied design system and the site kit onto the page: header, footer, tokens, section patterns. Every page image (not scene inputs) is cropped/fitted to its slot with `scripts/prepare_image.py`; the uploaded size is never used, and scenes are scaled to fit their slot (`pu-fit`). Reference: `references/images.md`. Keep the product UI faithful to its reference, in its own scoped theme, unless a branded recreation is explicitly requested.

Build any section flagged as designed in phase 3 now. Product UI stays an HTML/CSS scene; other sections may need an icon or a small illustration, generated to the measured house style. Entrance animation is the site's own `data-scroll` convention only. Two checks are mandatory before phase 14, both of which catch failures that are otherwise **silent**:

```bash
python3 scripts/check_classes.py handoff/preview/index.html --ignore pu- sc-
python3 scripts/check_svg_style.py handoff/assets/icons/*.svg
python3 scripts/check_markup.py handoff/preview/index.html --baseline <the captured page>
```

The third is new and catches the quietest failure of the three: assembling a page by
substituting into copied markup, and emitting one closing tag too many. Nothing errors —
the browser closes an ancestor early and every absolutely positioned child inside it
re-anchors somewhere else on the page. Compare against the page the chrome came from, not
against zero: the site's own markup is not perfectly balanced.

The site's stylesheet is purged: a class it has never used does not exist, and markup using it renders unstyled with no error. Reference: `references/design-system.md`, `references/site-kit.md`, `references/new-sections.md`, `references/icons-and-illustrations.md`.

**Phase 12. Build responsive behavior.**
Desktop, tablet and mobile, restructured rather than scaled, with compact scene variants that keep text readable and the interaction meaningful. Test the viewport matrix in every language. Reference: `references/responsive.md`.

**Phase 13. Integrate with the website's localization (integration phase, not a build phase).**
The mechanism is **already answered** in `site-kit/localization.md` (verified from the repo): five active languages (en, es, de, fr, **jp**), Danish disabled, English at the root with no prefix, YAML front matter, and the authoritative translatable / skip / URL key lists. Read it first, then plug the page into that mechanism: English source in the site's format and **field names taken from the translatable-key list**, the site's own language switcher and URL rules, and every visible string, including product UI text, as real editable content. Put numbers, ids and state flags in skip-key names so they are never translated. Never create a parallel i18n system, never write other-language files, never hand-write hreflang. A field name the list does not contain is a dev-team configuration change: flag it, do not edit the config. Then check text expansion, responsive behavior and animation in **German** (longest) and **Japanese** (CJK). Optionally add a preview-only language toggle so reviewers can see other languages. Reference: `references/localization.md`, `site-kit/localization.md`.

**Phase 14. Validate and package.**
Visual, animation, responsive, accessibility, localization and the **final privacy scan** (required; any leak of an original value blocks completion) on the preview and the bundle. Fix at the owning phase and re-run. Assemble the handoff bundle. **Pause for review.** Reference: `references/validation.md`, `references/handoff-bundle.md`.

## Rules that always apply

1. **Story first.** Every section advances the product story. Every scene proves one claim.
2. **Reconstruct, don't embed.** Screenshots and videos are inputs, not page assets. Page images are always resized to their slot (`references/images.md`), never used at upload size.
3. **Spec before code.** Change the spec and regenerate rather than patching generated markup.
4. **Native to the site, from the kit.** Use kit tokens, header, footer and patterns. Never invent site elements. Flag kit gaps and unverified conventions.
5. **One markup, two homes.** The scene and page markup in the preview is the same markup that goes in the bundle. Do not build a preview that cannot be handed off.
6. **Faithful product, native page.** Product UI matches the reference in its own scoped theme. The page follows the site's design system. They never leak into each other.
7. **Never hide real data, replace it.** No blur, partial masks, overlays or CSS/JS masking. From the moment a sensitive value is read from a reference, work with its entity id, not its value. Replacements are random, format-preserving and consistent across the page, and originals never appear in any shared file, in chat or in reports.
8. **Complete final state.** Every scene renders fully without JavaScript. It is what `prefers-reduced-motion` and no-JS visitors see. Two corollaries the validator now enforces or the runtime will punish: a target the timeline animates must appear in some state's `visible` list, or the player hides it for the scene's whole life; and because the player runs **one scene at a time**, a scene that is not currently playing shows its *initial* state — so a single-panel scene whose initial state hides its only content reads as an empty card until its turn comes.
9. **Copy is data, localized by the site's own mechanism.** No hard-coded strings anywhere. Text lives in fields or string files the site's localization already handles. Never build a parallel i18n system. Never assume English text lengths.
10. **Accessible by default.** Reduced motion, keyboard access, contrast, names and descriptions are part of done.
11. **Never publish.** Do not push, merge, or deploy to the live site. The end state is a preview and a bundle for the dev team. Sharing the preview link is the user's decision.
12. **Do not guess.** Unreadable text, a missing token, or an unknown convention means ask, or flag it. Record approximations for the handoff.
13. **Keep it light.** No frameworks, no large media, no inline scripts.

## Checkpoints

Pause for the user exactly three times: after the storyboard (3), after the scene spec (7), and after validation with the packaged bundle (14). Keep everything else moving. Present checkpoints in plain business language: what the visitor sees, not files or code, unless the user asks.

## Handoff

End by telling the user what to send the dev team (the `handoff/` folder and the preview link or folder), summarizing what was built, what was approximated, kit gaps and unverified conventions, and which translations need human review. Do not push anything anywhere.

## Supporting files

- `site-kit/` : the bundled snapshot of the site's design and conventions, with a status manifest. `page-types.md`/`.json` route a brief to one of 21 page types and state its authoring model; `localization.md` is the verified localization mechanism.
- `references/` : detailed rules per topic, loaded per phase.
- `examples/` : worked examples. `sale-day-command-center.html` is a dense dashboard rebuilt from one screenshot with the scanning method — 28 KB, no libraries, and its README names the three rendering bugs it contains the fix for.
- `templates/` : brief template and the handoff README template.
- `runtime/` : the shared scene player (`scene-player.js`, `scene-player.css`), a synthetic demo and a headless test. Done and tested.
- `schemas/` : JSON Schemas for the scene, content layer, privacy map and originals register. Done. A brief schema is not planned; the brief is a template.
- `scripts/` : `preflight.py` (phase 0 capability check), token normalizer, `extract_frames.py`, `prepare_image.py`, `check_classes.py` (every class resolves against the live purged stylesheet), `check_markup.py` (tag balance against the captured chrome — an extra close tag re-parents absolutely positioned children with no error), `check_svg_style.py` (generated icons match the measured house style), `scan_reference.py` (palette, page background, section bands and gutters from one screenshot), `extract_palette.py` (derives the product theme across screenshots and verifies a stylesheet against them), and `validate/` (`validate_scene.py`, `check_page.py`, `leak_scan.py`), all done and tested — the two new checkers against the site's own assets. A kit builder is planned.
