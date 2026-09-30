# Validation

Used in phase 14 (the privacy gate also runs in phase 8). Goal: prove the page meets the brief and the skill's rules before anyone sees it, and give the user an honest report.

## Approach

Run checks against the **preview page** and the **handoff bundle**. In Mode A use a headless browser (for example Playwright with Chromium) for the browser checks. In Mode B use the repo's own tools first:

- **Build:** the repo's build check (in Marketing-OS, `scripts/mktos/build-check.sh`; read its last line for green or red). Never publish drafts or edit configuration to make it pass.
- **Browser:** the live preview and its browser tools (start the preview, read console logs, read network requests, inspect elements, resize, screenshot, click). Use them for the visual, animation, responsive and accessibility checks.
- **Localization:** the repo's translation parity validator.
- **Scripts (present and tested on synthetic fixtures):** `scripts/validate/validate_scene.py` (spec checks: definition validity from `ui-scene-system.md` section 12, resolved entity references, sensitivity flags), `scripts/validate/check_page.py` (headless-browser checks on the preview and bundle: screenshots at the viewport matrix, reduced-motion emulation, horizontal overflow, smallest text size, visible and accessible text per timeline state), `scripts/validate/leak_scan.py` (the privacy scan, section 5) and `scripts/extract_frames.py` (frame extraction from the reference videos). Use a script when it exists. When it does not, do the same check by hand and say so in the report.

Record results in `reports/validation.md` in the work directory, with screenshots. Then hand the report to the repo's review step as evidence. This skill's report does not replace the review gate and never writes its approval marker.

Each check ends as **pass**, **fail** (must fix), or **warning** (accepted, listed). Fix failures at the phase that owns them, then re-run the affected checks. Do not present a report with unexplained failures.

## 1. Visual fidelity

**First: are these the right components?** Read the section class names out of the built page
and compare them with the sequence in `page-types.json` for the type you routed to. A page built
by reusing another page's scaffold will render beautifully and still be the wrong page type
(`site-kit.md`, "Use the page type's own components").

**Second: does every class actually exist?** The site's stylesheet is purged — a class it has
never used is not in the file, and markup using it renders **unstyled with no error**. This
cannot be caught by reading the markup, and it is the single most likely failure in any section
that was designed rather than copied.

```bash
python3 scripts/check_classes.py handoff/preview/index.html --ignore pu- sc-
```

Exit 1 is a build failure, not a warning. If the page has generated icons or illustrations,
check those against the house style too — it reports which of the three families it detected:

```bash
python3 scripts/check_svg_style.py handoff/assets/icons/*.svg
```

For any section that was designed rather than taken from a component, also confirm: it renders
correctly with JavaScript disabled (nothing stranded at opacity 0), it uses no colour that is
not a token or a `var(--product-*)`, and the handoff carries its rationale
(`new-sections.md` §5). Then read the page top to bottom and ask whether the section earns its
vertical space — if the page reads better without it, cut it.

**Third: is the product UI painted in the product's own colours?** Mechanical, and it catches
the fidelity failure that is hardest to see by eye:

```bash
python3 scripts/extract_palette.py input/references/images/*.png --check scenes.css
```

Exit 1 means a `--product-*` colour appears in none of the reference screenshots. A scene with
the right layout and the wrong palette reads as a generic SaaS app, and nothing about it looks
broken. Then confirm the **visual signature** survived — accent, icon language, colour-coded
state, density, supporting text (`ui-reconstruction.md`, "The visual signature"). Where a wide
table was reduced, the scene's `approximations` must say what was dropped.

**Fourth: did every supplied reference reach the page?** Count them. `N screenshots supplied
→ M scenes built → P rows still on a placeholder`, and put those three numbers in the report.
A page can pass every other check while quietly using a quarter of what the user gave you.

A placeholder that renders as ordinary text is how this goes unnoticed: the page looks finished,
the row looks deliberate, and only someone comparing against the source document spots it. Give
every placeholder a `data-placeholder` attribute so it is countable, and treat a non-zero count
as **incomplete**, not as a styling choice:

```bash
grep -c 'data-placeholder=' handoff/preview/index.html   # must be 0 before review
```

If a supplied reference genuinely has no home on the page, say so explicitly and name it — "five
screenshots map to no section, here they are" is a scope decision the user can make. Silently
dropping them is not.

**Rendering quality (measure, do not eyeball).** For every image: natural width ÷ CSS width
should be ≥ 2.0 for site art on a laptop; above-the-fold images must not be `loading="lazy"`.
For every scaled scene: the rendered height must be a whole number of pixels, and the effective
text size ≥ 11 px. All four are one console snippet and all four have been wrong in a build that
looked fine (`images.md`, "Rendering quality").

**Does it look like the product?** Put a scene's final frame beside the reference screenshot and
check the furniture, not the data: navigation, secondary panels, breadcrumb, both toolbars, row
decoration, footer, and the product's own link and status colours. A faithful table with none of
its surroundings is the commonest reconstruction failure (`ui-reconstruction.md`, "Rebuild the
chrome, not just the data").

**Check intermediate frames, not just the final state.** Use the runtime's `seek` to capture the
first frame and two or three mid-timeline frames of every scene, and ask of each: could this be a
screenshot of the real product? Fail the check for an empty titled container, a counter or total
that contradicts what is visible, or any badge or state that implies a step not yet taken
(`ui-reconstruction.md`, "Every frame must be a believable product state").


- In the live preview, capture each scene's **final state** and its key timeline moments (use the runtime's `seek`).
- Compare with the reference keyframes side by side. View the reference frames from `analysis/` (they were produced by `scripts/extract_frames.py` or by hand). Never copy a reference frame into `reports/`, `preview/` or `handoff/`, including inside a side-by-side image: the report's screenshots show the rebuilt page only. Check layout, proportions, type, color, spacing, radii and iconography, in that order.
- List each deviation as either an intentional approximation (already in the spec's `approximations`) or a defect to fix.
- Check the page around the scenes against the design system: tokens used, no hard-coded values, headings and buttons as specified.

## 2. Animation

- Each scene plays through its timeline, in order, and ends in its final state.
- Only elements whose change carries the claim move. Chrome does not animate in. Steps trace to the video or are labelled assumed (`animation-system.md`).
- Only one scene plays at a time. Loops hold, then stop after a few cycles.
- Only `opacity` and `transform` are animated, and there is no layout shift.
- Timing feels like the reference. Steps are not skipped or overlapping wrongly.
- Play, pause and replay work, by mouse and keyboard.
- Scenes start when visible and pause when off-screen.
- No console errors or warnings. No missing targets.
- **Smooth:** no visible jumps. Frame-sample the scene while it plays: text grows a little at a time and never jumps to full length, nothing flashes its final state before it starts, and there is no layout shift. Typing and streaming update in place (no per-frame rebuilds).
- **Zoom:** every zoom frames its whole target, keeps the action in view, holds long enough to read, and ends back at full view. No scene zooms on something that already fills it.
- **Fits its slot:** on desktop, each scene sits inside its section's image box, and its effective text size after scaling is legible (about 8 px or more).
- **Reduced motion:** emulate `prefers-reduced-motion: reduce`. Every scene shows its final state immediately. Nothing loops, pulses or moves.

Also run the page once with the host site's real stylesheet (or a reset that mimics it) to catch icons, lists and spacing that a reset changes.

## 3. Responsive

- Run the full procedure in `responsive.md` section 8: the required viewport set (320, 390, 768, 1024, 1440 and 1920 wide), the breakpoint edge widths, and the test conditions (zoom, landscape, reduced motion, longest language).
- No horizontal scroll, clipping, overlap or unreadable text.
- Compact scene variants activate where specified, and text in scaled scenes stays at or above the legibility minimum.
- Touch targets are large enough on mobile.
- The page works at 200 percent zoom.

## 4. Accessibility (WCAG 2.1 AA)

Automated:

- Run an automated accessibility scan (axe-core or equivalent) in the preview if it can be loaded there, on every language and viewport class. Zero serious or critical issues. If it cannot be loaded, say so and rely on the manual checks.

Manual:

- Landmarks, one `h1`, logical heading order, a skip link.
- Every interactive element is reachable and operable by keyboard, with a visible focus indicator and a sensible tab order.
- Scenes have accessible names and text descriptions. Animating internals are hidden from assistive tech, and the final text is available.
- Color contrast meets 4.5:1 for text and 3:1 for large text and UI components.
- No content flashes more than three times per second.
- Controls have labels. If a language toggle is present (the preview-only one, or the site's own), its options are labelled in their own language.
- Test with a screen reader spot-check if possible, otherwise inspect the accessibility tree.

## 5. Privacy

Required gate. The full procedure (scan steps 1 to 8, the map audit, the report contents and what to do on a finding) is defined once, in `privacy-masking.md` section 7. Run it as written. This section only says how validation uses it.

- **Inputs.** `.private/originals.json` (read by the scanner only, never printed) and `spec/privacy-map.json` (replacements only). They join through entity ids, so every finding is reported as an entity id plus a file path, never as a value.
- **Scope.** Every file in `preview/` and `handoff/`, including `reports/` and its screenshots. In Mode B, also every file added or changed in the repo, including each language's content, data and UI string files.
- **Tooling.** `scripts/validate/leak_scan.py` runs the text, normalized, encoded, fragment and unregistered-pattern steps. `scripts/validate/check_page.py` supplies the runtime step: visible and accessible text in every state the timeline can reach. `scripts/validate/validate_scene.py` supplies the map audit's spec side: no unresolved `{{entity}}` reference, a sensitivity class on every text item. The media step (no reference screenshot, frame, video or contact sheet; no text or EXIF in a shipped image) is checked by looking, not only by filename. If a script cannot run in the environment (for example no browser is available), perform the same step by hand and record that it was manual.
- **Consistency.** Confirm each replacement is the same across scenes, states and languages (the map audit covers this).
- **Blocker rule.** Any hit is a **blocker**: the page is not complete and the packaging step does not run. Fix the map and spec, regenerate the affected scenes from the resolved spec (never patch output), and re-run the whole scan. Also check whether an original reached a shared place (a commit, a chat message, a shared preview link) and tell the user if so.
- **Output.** `reports/privacy.md` in the work directory, and a derived `spec/privacy-report.md` in the bundle (contents in `handoff-bundle.md`). Neither contains an original value.

## 6. Localization

- **Mode A:** the bundle contains English source only. Check that every field name and string is translatable in the form the kit records, and that unverified field names are listed in the handoff. In the preview, use the preview-only language toggle and a pseudo-localized run (about 40 percent longer) to check layout. Drafted translations are labelled preview-only.
- **Mode B:** the repo's translation parity validator passes for all active languages, each language's page shows translated text, alt text and ARIA labels, `lang` is correct, and links carry the language prefix.
- Capture the longest language and one right-to-left language (if any). No overflow, clipping or broken alignment.
- Numbers and dates use the locale format.
- Machine translations are flagged for review.

## 7. Performance and code quality

- Total page weight within a sensible budget (target well under 1 MB excluding fonts, and state the number).
- No raster screenshots or videos of the product UI.
- Scripts live in asset files. No inline scripts, raw HTML embeds or inline event handlers in content (the review step flags these as security risks).
- No layout shift as scenes load or animate.
- Lighthouse or equivalent: note performance, accessibility and best-practice scores if available.
- Code: consistent formatting, meaningful names, scoped styles, no inline styles beyond dynamic values, no dead code or commented-out blocks, no leftover reference filenames.
- No console errors. Works without JavaScript in the default language (static final states visible).

## Report format

`reports/validation.md` contains:

1. Summary: overall status, counts of pass, fail, warning, and a pointer to `reports/privacy.md`, which is kept as its own report.
2. A table per check area with results.
3. Failures found and how they were fixed.
4. Remaining warnings with reasons.
5. Approximations from the spec, restated.
6. Items needing human review: fidelity judgment, translations, legal or compliance wording.
7. Links to screenshots.

When presenting the report, lead with the outcome and the few things the user must decide. Do not bury blockers in detail.

## Definition of done

- No failing checks and no privacy hits.
- All warnings are explained and accepted.
- The user has seen the report and screenshots.
- The handoff note is written.
