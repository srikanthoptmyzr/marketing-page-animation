# Responsive behavior

Used in phases 3, 7, 11, 12 and 14. Goal: the generated page works well on desktop, tablet and mobile, in every language, with readable text and an understandable product interaction at every size. The page is **restructured** for smaller screens, not scaled down.

## Below the fit threshold, a scene needs compact variants

`pu-fit` only scales at and above `data-fit-from` (1024). Below it the scene renders at the
column's real width, which on a two-up feature row is around 310px. A table that fits a 600px
design does not fit there, and every cell truncates.

`.pu-stage` is a container-query container, so the scene can adapt to **its own** width rather
than the page's:

```css
@container (max-width: 620px) { .pu-scope { display: none; } }
@container (max-width: 560px) { /* drop the owner column */ }
@container (max-width: 470px) { /* drop the status column and the header sub-labels */ }
```

Drop things in order of how little they carry, and keep the product's identity longest: the
navigation rail stays after the secondary panel goes, and data columns go before furniture.
Switch `table-layout` back to `auto` once columns are hidden, or the remaining ones keep the
percentages of a table that no longer exists.

Check every scene at the narrow end, not only at 1440. A cell whose `scrollWidth` exceeds its
`clientWidth` is truncating, and that is a fail.

## Design a scene at its slot's width, never wider

`pu-fit` scales a scene down to fit its slot. That is a safety net for the last few percent,
**not** a way to put a wide design into a narrow box. Scaling shrinks the text with everything
else, and the detail that made the scene worth building stops resolving.

Work out the design width from the slot before drawing anything:

```
design width  =  usable slot width / 0.85
```

The `features-section` image box is 549px wide with `p-4`, so the usable width is **517px** and
the design width is about **600px**. The hero's desktop block is 651px, so about **720px**.

| Scale | Text designed at 15px renders at | Verdict |
|---|---|---|
| 1.00 | 15px | ideal |
| 0.85 | 12.8px | fine — the working target |
| 0.80 | 12px | the floor |
| 0.70 | 10.5px | **under the 11px minimum; recompose** |
| 0.50 | 7.5px | unreadable |

**When a scene does not fit, take content out — do not turn the scale down.** Fewer table
columns, shorter labels, one row instead of three, a tighter chart. A scene proves one claim;
everything that does not serve that claim is what you remove first.

Height matters as much as width. A scene can be narrow enough and still be scaled down because
its natural height exceeds the slot, which is the same failure with the same fix.

The player checks this for you: below a 0.8 scale, at viewports of 1280px and up, it logs a
console warning naming the scene, the scale, the resulting text size and the width to
recompose at. Treat that warning as a build error. It is deliberately silent at narrower
viewports, where a smaller scale is the correct response to a genuinely narrower column.

Seen for real: the first Explorer build designed scenes at 760-900px for a 517px slot. Every
scene rendered at roughly half size with 8-9px text. Recomposing to 590-600px, with six table
columns instead of eight and a shorter popover, moved them to 0.83-0.90 and 13.5-16.3px with
no loss of meaning.

## 1. Principles

1. **Reflow and reprioritize, don't shrink.** A smaller screen gets a layout designed for it. Simply scaling the desktop composition down produces tiny text, tiny targets and a lost story.
2. **Readability and meaning come first.** When space runs out, drop or simplify things in a stated order, and never drop what carries the claim.
3. **Same content, different arrangement.** Mobile is not a cut-down page. Every section that carries the story stays. What changes is layout, density and how much of a scene is shown.
4. **Mobile first.** Build the smallest layout first, then add width. It forces the priorities to be decided.
5. **Design for the container, not just the viewport.** Page layout responds to the viewport. Scenes respond to the width of the space they are given.
6. **Reading order is DOM order.** Visual reordering must not break the order a keyboard or screen reader user gets.
7. **Test real sizes, in every language.** Layouts that only work in English are not finished.

## 2. Breakpoints and ranges

Use the design system's breakpoints (from the supplied system or the site kit, see `design-system.md`). If none are confirmed, use these and record them as assumptions:

| Class | Width | Layout stance |
|---|---|---|
| Mobile | up to 767 px | One column. Compact scene variants. Touch first |
| Tablet | 768 to 1023 px | One or two columns. Choose per section, and prefer stacking when in doubt |
| Desktop | 1024 px and up | Full layouts, side by side, zigzag sections |

Design decisions are made at three breakpoints, but layouts must hold at every width in between. Inspect narrow and wide extremes (320 and 1920 or wider). At very wide sizes, cap content at the container width instead of stretching.

**Type modes.** Design systems often define only desktop and mobile type sizes. Switch at the design system's breakpoint, and check tablet: use the mode that keeps headings from wrapping awkwardly, and record which one.

## 3. Page layout

### Section layouts

| Section | Desktop | Tablet | Mobile |
|---|---|---|---|
| Hero with a scene | Text and scene side by side | Stacked, or side by side only if both columns keep their minimum widths | Text first, then the scene |
| Feature section with a scene | Two columns, alternating sides | Stacked | Stacked, in one consistent order (text, then scene) |
| Card grid | 3 or 4 columns | 2 columns | 1 column |
| Stat or metric row | One row | 2 by 2 | 1 or 2 columns, by content width |
| Logo strip | One row | Wrapped rows | Wrapped rows, reduced count if it is decoration |
| FAQ | Two columns or wide single | Single column | Single column, larger targets |
| CTA band | Text and buttons side by side | Same, or stacked | Stacked, full-width button |
| Footer | Multiple columns | 2 columns | Stacked or collapsible groups, as the design system defines |

Rules:

- Use grid or flex and let content wrap. Avoid fixed widths and heights on containers.
- Section spacing steps down using the design system's spacing scale. Do not shrink spacing by arbitrary ratios.
- Keep a consistent side gutter. Content never touches the screen edge unless it is deliberately full-bleed.
- **Do not hide content that carries the story.** Hide only decoration and secondary material, and only if the design system allows it.
- Anchor targets account for a sticky header (`scroll-margin-top`).

### Side-by-side layouts

- Use side-by-side only when **each column keeps its minimum width**: a text column of about 320 px or more, and a scene column wide enough for its compact or full variant (see section 5).
- On tablet, choose stacked unless the width comfortably fits both columns. A cramped two-column tablet layout is worse than a single column.
- When space is tight, shift the ratio in favor of the scene (for example 40/60) before stacking, since the scene has a minimum legible width.
- Zigzag (alternating sides) is a desktop device. On tablet and mobile, use one consistent order so the page reads predictably.
- Columns align to the top of the text block. Do not vertically center a tall scene against short text in a way that leaves large gaps on tablet.
- Gaps follow the spacing scale. Do not let the scene overlap its neighbor.

### Product visual positioning

- **Order.** On stacked layouts, text first, then the scene it proves, so the claim precedes the demonstration. If the scene is the hero visual, keep it visible without a long scroll.
- **Contained or bleed.** On mobile, a scene may extend to the screen edges to gain width (within the container's negative margin), with the frame's radius removed at the bleeding edges. Never let it bleed horizontally beyond the viewport.
- **No collages.** Overlapping, floating or absolutely positioned compositions of several product visuals, decorative shapes or peeking screenshots collapse on small screens. Replace them with a single scene, or a simple stack, on tablet and mobile.
- **Height.** A scene should not take more than about one screen of height on mobile. Cap the compact variant's height and aspect ratio (for example 4 by 5 or 1 by 1).
- **Anchoring.** When cropped, anchor to the region that carries the claim, not the center.
- **Multiple scenes.** Stack them, each with its own caption. Do not place scenes side by side on mobile. Do not turn them into a horizontal carousel unless the design system has an accessible pattern for it.
- **Spacing around the scene.** Keep the frame's padding so the product is legible against the background. Do not remove it to fit.

### Typography

- Use the design system's desktop and mobile sizes, line heights and letter spacing, by step. Do not invent fluid sizes unless the system defines them.
- **Body text** on mobile is at least 16 px unless the design system's mobile body size is set lower and the text remains comfortably legible. Captions and labels may be smaller, but not below 12 px.
- **Line length.** Aim for about 45 to 75 characters on tablet and desktop, and about 35 to 55 on mobile. Cap text columns with a maximum width.
- **Headings** wrap freely. Use balanced wrapping where supported, and never fix a heading height. Check headings do not break into one long word per line at 320 px.
- **Letter spacing.** Negative letter spacing on large headings can hurt small sizes. Use the design system's mobile values, and check readability at 320 px.
- **Heading order** is the same at every size. Do not change heading levels for looks.
- Text scales with the user's text-size settings. Use relative units, and check 200 percent zoom.

### Navigation

- The header and navigation come from the design system or the site kit. Use its mobile pattern unchanged. Never invent a menu. If the kit has no mobile navigation, record a kit gap and ask.
- Touch targets in navigation are at least 44 by 44 px, with clear spacing.
- No hover-only menus. Every submenu must be reachable by touch and keyboard.
- An open mobile menu is keyboard operable, closes on Escape, and returns focus to its button.
- Sticky headers stay compact on mobile so they do not eat the screen. Account for their height in anchor scrolling.
- The language switcher, if the site has one, is reachable on mobile, usually inside the menu.
- Long translated labels wrap or move into the menu. They never overflow the header.
- The skip link works at every size.

### Buttons

- Minimum target 44 by 44 px on touch layouts, with at least 8 px between adjacent targets.
- A standalone primary call to action may be full width on mobile. Paired actions stack, with the primary first.
- Labels wrap to two lines instead of truncating or overflowing. Buttons have no fixed width and no fixed height.
- Icon-only buttons have an accessible name and a full-size target.
- Do not depend on hover to reveal an action. Focus and pressed states remain visible.
- Follow the design system's button variants, sizes and states, and do not restyle them.

### Cards

- Grids collapse as in the table above. Use grid so cards in a row stay equal without fixed heights.
- Horizontal cards (media beside text) become vertical on mobile, with the media above the text and a stable aspect ratio.
- Never truncate meaning. Clamp only optional excerpts, and only where the design system does it.
- The whole card is one target if it is a link, and the target stays at least 44 px tall.
- Card padding and gaps follow the spacing scale, stepping down on mobile.
- Avoid horizontal card carousels. If the design system has one, give it a visible peek, snap points, and keyboard and button controls.

## 4. Overflow

Goal: nothing forces horizontal scrolling, and nothing essential is clipped.

- The page never scrolls horizontally at any width.
- Give flex and grid children `min-width: 0` so long content can shrink.
- Images, video-like elements and inline SVG are `max-width: 100%` with intrinsic proportions.
- Long words and unbroken strings use `overflow-wrap` so they wrap. Use hyphenation with the correct `lang` for body text.
- **Tables** on the page are restyled for small screens (stacked rows, or key columns) where possible. A genuine data table may scroll inside its own labelled, focusable region, with a visible cue. The page itself never scrolls sideways.
- Avoid `100vw` for widths, since it includes the scrollbar. Use container widths or `100%`. Use dynamic viewport units for full-height sections on mobile.
- Negative margins used for bleed are bounded by the page gutter.
- Respect safe-area insets for fixed and edge-aligned elements.
- Fixed and sticky elements never cover content or focused controls.
- **Ellipsis is limited** to data-like strings inside a scene where the real product truncates. Never truncate headings, buttons, navigation or body copy.
- A scene root clips its own overflow by design, but never so that an essential component is cut off.

## 5. Product UI scenes

Complex desktop compositions must transform on mobile, and the transformation must preserve two things: **readable text** and **the meaning of the interaction**.

### Scaling model

- Each scene has a **design width** and sits in a container with `container-type: inline-size`.
- Sizes inside the scene use container units, so the whole UI scales together:

  ```css
  .scene { container-type: inline-size; }
  .product-ui { --u: calc(100cqw / 720); }   /* one design pixel */
  .product-ui .pu-message { padding: calc(12 * var(--u)); font-size: calc(14 * var(--u)); }
  ```

- Every scene declares a **legibility limit** (`minTextPx`, about 11 px, and 12 px for key content). Effective text size is design size multiplied by the scale.

### Fitting a scene into a page slot

- The scene's **stage** (`.pu-stage`) is the query container, not the outer figure. Layout and type then follow the width the stage is actually laid out at, including when the stage is scaled to fit a slot. A container on the outer figure makes a scaled scene fall back to its narrow layout (a single tall column) while still being drawn wide.
- At the page's desktop breakpoint, lay the stage out at its design width (`data-fit-width`) and scale it down with one transform to the slot (`data-fit-height`). Below the breakpoint, no scaling: the scene is responsive on its own. See `runtime/README.md`.
- **Compose for the slot, do not copy the reference's placement.** A slot is roughly 4:3 or 3:2. If the reference UI is tall or very wide, recompose it: use two columns instead of one long column, drop secondary rows (three of nine suggestions), tighten spacing, and keep what carries the claim. Record what was dropped in `approximations`.
- Check the effective text size after scaling (design size times the scale). If key text falls below about 8 px, simplify the scene rather than shrinking further, and use `zoom` (`animation-system.md`) for the moment that matters.

### Choosing a variant

Compute the **scale** as container width divided by design width, and act on it:

| Scale | Action |
|---|---|
| About 0.75 or more | Scale the full scene. Hide `optional` decoration only if needed |
| About 0.55 to 0.75 | Scale, and simplify: hide `optional`, then `normal` components until text meets the limit |
| Below about 0.55, or text below the limit | Use a **compact variant** built for the small width |

As an example, a 720 px scene in a 343 px mobile container has a scale of about 0.48, so it needs a compact variant. On a 768 px tablet it has a scale near 1.

Choose variants with **container queries**, so a scene adapts to the space it actually gets, in any layout.

### What to keep and what to drop

Components carry a priority (see `ui-scene-system.md`). Drop in this order, and stop as soon as the text is legible:

1. Decoration: shadows, backgrounds, patterns, badges with no meaning.
2. Secondary chrome: sidebars, navigation rails, breadcrumbs, footers, filter bars, toolbars.
3. Secondary detail: legends, gridlines, axes labels beyond the essential, timestamps, avatars, extra table columns, extra rows.
4. Secondary actions: secondary buttons and overflow menus.

**Never drop** the elements that carry the claim: the question, the answer or result, the recommendation, the approval control, the success state, and the numbers the story is about. If a compact variant cannot show them legibly, the composition needs a different transformation, not more shrinking.

### Transforming compositions

| Desktop composition | Mobile transformation | Strategy |
|---|---|---|
| Sidebar plus main area | Hide the sidebar, or reduce it to a single title strip that tells the visitor where they are | `crop` |
| Multi-column dashboard | Stack metrics in one or two columns, keep the one chart that matters, drop secondary widgets | `stack`, `simplify` |
| Wide table | Keep the identifying column and the key columns, or turn rows into compact cards | `simplify`, `swap` |
| Chat with a side panel | Chat only. Show the panel's content as an inline card after the answer arrives | `crop`, `stack` |
| Long conversation thread | Show the last two or three messages, cropped from the top with a soft fade at the cut | `crop` |
| Modal over an app | Show the modal filling the width, and drop the dimmed app behind it | `crop` |
| Before and after side by side | Before above after, or a toggle between them if the animation makes that clear | `stack` |
| Multi-step flow across panels | One panel that changes through the steps, with a shortened timeline | `shorten` |
| Toolbar with many actions | Primary action plus overflow, or only the action used in the story | `simplify` |
| Chart with legend | Chart with direct labels on the marks | `simplify` |
| Tooltips and popovers | Inline caption or callout under the element | `swap` |
| Toast or notification | Full-width banner at the top of the scene, or inline | `swap` |
| Cursor across a large screen | Keep the cursor only if the click is the story (approval). Otherwise show the result state | `simplify` |
| Dense list or feed | Fewer items, larger rows | `simplify` |

### Cropping rules

- Crop at component boundaries. Never cut through a line of text or a control.
- Anchor to the region that carries the claim.
- A soft edge fade is allowed at a crop to imply continuation, never to hide content that the story needs.
- Keep a one-line title strip when it tells the visitor which part of the product they are seeing.
- Do not pan or scroll the scene internally on mobile as a way to fit it. Nested scrolling traps touch users.

### Swapping structure

- Prefer restyling the **same markup** with container queries (for example, a table row becoming a card by changing its display and layout). One structure means one set of content.
- If different markup is truly needed, render both from the **same content** and show one at a time, so the hidden one leaves the accessibility tree.
- A compact variant may use **short labels** for the same meaning, provided as separate content keys with the same translate flags. The compact text must mean the same thing.

### The interaction survives

- The compact variant must show **the same story**: the same states in the same order, with the essential steps intact. It may use a shortened timeline (for example, fewer messages, a shorter loading time), but the cause and effect must remain visible.
- States keep the same names across variants, so the player switches variant without restarting.
- The final state of the compact variant makes sense on its own, since it is what reduced-motion visitors see.
- Test by the **meaning test**: look only at the compact variant's final state and its caption. Can someone say what happened and why it matters? If not, the compact variant has dropped the wrong things.

### Shape and size

- A compact variant declares its own aspect ratio (for example 4 by 5 or 1 by 1) and maximum height.
- Text in the scene is at or above the legibility limit. Key content is at or above 12 px.
- Interaction controls belonging to the page (play, pause, replay, step) meet the 44 px target size and sit outside the product UI.
- The scene does not depend on hover. Pointer effects inside it are illustrations.

### Orientation, zoom and text size

- Landscape phones are wide but short. Check that a scene does not exceed the viewport height, and let a compact variant limit its height.
- At 200 percent zoom, the container narrows, so a compact variant appears through the container query. Confirm it works there.
- Larger default text sizes must not break the frame or its controls.

## 6. Animation behavior across sizes

- **Start threshold.** Start when about half of the scene is visible. For tall scenes on mobile, a lower threshold (about a third) prevents a scene that never quite reaches half.
- **One at a time.** On every size, only the scene most in view plays. On small screens this matters most.
- **Compact timeline.** A compact variant may name a shorter timeline. Same states, same order, fewer or shorter steps.
- **Less concurrent motion** on small screens. Do not add motion because there is space.
- **No hover motion.** Touch devices have no hover, so hover-driven effects belong only inside the scripted sequence.
- **Resize while playing.** When the container width crosses a variant threshold, keep the current state and switch layout. Do not restart the timeline. Debounce the observer, and avoid layout work in animation frames.
- **Page-level motion** stays restrained on all sizes: a frame or heading may enter once. No per-element entrance animation on scroll.
- **Reduced motion** always shows the final state, in every variant. The step-through control appears where the order of states matters.
- **Controls stay reachable.** Play, pause and replay are visible and usable at every size.

Full rules for timing and playback are in `animation-system.md`.

## 7. Long translated text

Translated strings are often much longer than English, and some scripts change line height and breaking. Assume it will happen and design for it.

| Language family | Expect |
|---|---|
| German, Dutch, Finnish and other compounding languages | 30 to 40 percent longer, with long unbreakable words |
| French, Spanish, Portuguese, Italian, Russian | 15 to 35 percent longer |
| Japanese, Chinese, Korean | Shorter in width, but taller lines and different line breaking |
| Arabic, Hebrew | Right to left, with mirrored layout |
| Very short English strings (buttons, labels) | Can double or triple in length |

Rules:

- **No fixed widths or heights** on text containers, buttons, tabs, chips, table headers or cards.
- **Buttons and labels wrap** to two lines. They never truncate and never overflow.
- **Headings** use balanced wrapping and are checked at 320 px for long words.
- **Long words** use hyphenation with the right `lang` attribute, and `overflow-wrap` as a backstop.
- **Navigation** items wrap or move into the menu. The header never overflows.
- **Tabs and chips** wrap to a second row or scroll inside a labelled region, chosen per the design system.
- **Scenes:** text containers inside scenes tolerate 40 percent growth. Rows, chips and headers wrap or grow. If a compact variant uses short labels, each language has its own short label, and any language whose label still does not fit is flagged.
- **CJK:** allow more line height, follow the site's line breaking, and do not add letter spacing.
- **Right to left:** logical properties everywhere (`margin-inline`, `inset-inline-start`, `text-align: start`), mirrored layout and arrows, logos and most numerals unmirrored.
- **Numbers and dates** may be longer in some locales, so reserve room for them.
- If a string still does not fit after wrapping, first re-layout (widen the container, stack). Do not reduce the font size below the design system's scale. If needed, flag the string for shortening by the translation process.

**Testing.** Test with **pseudo-localization** (a string expanded by about 40 percent and with accents) and with the longest real languages at mobile and tablet widths. See `localization.md`.

## 8. Testing viewport sizes

### Required set

Test every page at these viewports. Sizes are CSS pixels, width by height.

| Class | Viewport | Represents |
|---|---|---|
| Small phone | 320 × 568 | Narrowest realistic screen, and 400 percent zoom equivalent |
| Phone | 390 × 844 | Common modern phones |
| Tablet portrait | 768 × 1024 | Standard tablet, and the breakpoint edge |
| Tablet landscape or small laptop | 1024 × 768 | Second breakpoint edge |
| Laptop | 1440 × 900 | Common desktop |
| Wide desktop | 1920 × 1080 | Large monitors, to check the container cap |

### Extended set

Where time allows, also test:

| Viewport | Represents |
|---|---|
| 360 × 800 | Common Android phones |
| 412 × 915 | Large Android phones |
| 430 × 932 | Large iPhones |
| 820 × 1180 | iPad Air |
| 1024 × 1366 | iPad Pro portrait |
| 1280 × 800 | Small laptop |
| 1366 × 768 | Common budget laptop |
| 2560 × 1440 | Very wide |
| 844 × 390 | Phone landscape |

### Edge widths

Test one pixel below and at each breakpoint (for example 767 and 768, 1023 and 1024), to catch layouts that break exactly at the switch.

### Conditions

For the required viewports, also test:

- 200 percent browser zoom, and a larger default text size.
- Landscape on the phone sizes.
- Reduced motion on, and JavaScript off.
- The longest language and one pseudo-localized run.
- A right-to-left language, if any is active.
- Touch emulation, so hover-only behaviors show up.
- A throttled CPU, for animation smoothness.

### Procedure

For each viewport and language:

1. Capture a full-page screenshot, top to bottom.
2. Check for horizontal scroll: the document's scroll width must not exceed its client width. To find offenders:

   ```js
   [...document.querySelectorAll('*')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
   ```

3. For every scene: capture the final state and the key states of the active variant. Confirm which variant is active.
4. Measure the smallest computed text size inside each scene, and compare it with the legibility limit.
5. Confirm every `essential` component is visible in each variant.
6. Apply the meaning test to each compact variant.
7. Check touch target sizes for buttons, controls and navigation.
8. Resize across variant thresholds while a scene is playing: the state is kept and nothing restarts or jumps.
9. Check text expansion in the longest language: no clipped, overlapping or overflowing text.
10. Check nothing is hidden behind sticky or fixed elements, including anchor targets.

Name screenshots so they are traceable: `reports/screenshots/<page>-<width>x<height>-<lang>-<state>.png`.

### Pass criteria

- No horizontal scroll at any tested width.
- No clipped or overlapping text.
- Scene text at or above its legibility limit, and key content at or above 12 px.
- Every compact variant passes the meaning test.
- All touch targets are at least 44 by 44 px.
- Reduced motion shows the complete final state in every variant.
- Layout holds in the longest language and, if active, right to left.
- The design system's breakpoints and type modes are applied correctly on either side of each edge.

## 9. Declaring responsive behavior in the scene definition

Every scene declares, before it is built (see `ui-scene-system.md`):

- `designWidth` and `minTextPx`.
- Component `priority` (`essential`, `normal`, `optional`).
- At least one compact variant, with a name, the container width it applies below, its strategy, the components it hides, stacks or swaps, its aspect ratio and maximum height, an optional shorter timeline, and optional compact content keys.

A scene with no declared compact strategy is not ready to build.

## 10. Checklist

- Mobile, tablet and desktop layouts are designed, not scaled.
- Every section has a defined transformation for each breakpoint.
- Side-by-side layouts only where each column keeps its minimum width.
- Product visuals are positioned per the rules, with no collages on small screens.
- Type, navigation, buttons and cards follow the design system and the touch rules.
- Every scene has a legibility limit, priorities and a compact variant that passes the meaning test.
- Animation adapts: one scene at a time, compact timelines, state kept on resize.
- No horizontal overflow. Ellipsis used only where allowed.
- Layout survives the longest language, and right to left if active.
- The viewport matrix, edge widths and conditions were tested and the results recorded.

## 11. Common mistakes

- Scaling the desktop scene down until the text is unreadable.
- Hiding the element that carries the story to make things fit.
- Two-column layouts on tablets that are too narrow for either column.
- Fixed widths on buttons and labels, which break in German or Finnish.
- Collages of overlapping visuals that collapse into a mess on mobile.
- A compact variant that changes the story, not just the density.
- Hover-only navigation or hover-only reveals.
- Nested scrolling inside a scene on touch devices.
- Restarting the animation when the window is resized.
- Testing only English at desktop and mobile widths.

## Below `data-fit-from` a scene is NOT scaled — it must carry a compact variant

This is the single most common cause of a page that reviews well on a laptop and is a
mess on a phone, and it is easy to miss because the desktop view gives no hint.

`pu-fit` only applies at or above `data-fit-from` (1024 in practice). The runtime says so
directly: *"Below `data-fit-from` the scene stays fully responsive."* So on a phone a
scene is not shrunk — it is **reflowed** into whatever width the slot gives it, typically
~260–300 px inside a feature card. A dense table laid out for 600 px does not scale into
that; its columns collapse, every cell wraps to three or four lines, and one card ends up
three times the height of its neighbour. Measured on a real build before the fix:

| Scene | Height at 375 px |
|---|---|
| strategies | 254 px |
| attributes | 426 px |
| buckets | 510 px |
| preview table | **856 px**, and 138 px of horizontal overflow |

The fix is not a smaller scale — that pushes text under the 11 px floor. It is **less
content**, expressed as container queries on the stage, which already sets
`container-type: inline-size`, so the query responds to the slot rather than the viewport:

```css
@container (max-width: 420px){
  /* drop the columns that are not part of the claim */
  .sc1-tbl th:nth-child(3),.sc1-tbl td:nth-child(3){display:none}
  /* stack an action bar instead of letting a long button overflow */
  .sc2-actions{width:100%;flex-direction:column}
  .sc2-actions button{width:100%;white-space:normal}
  /* cap repeated elements: 12 chips read the same as 25 */
  .sc6-tags .sc6-tag:nth-child(n+13){display:none}
  /* show fewer rows */
  .sc2-tbl tbody tr:nth-child(n+6){display:none}
}
```

Same build after: 254–501 px and no overflow anywhere.

**Decide per column what the claim needs.** In a performance table, the share, the label
and the one metric the copy names earn their place; a second and third metric do not.
Dropping them is a `simplify` variant, which is what `scenes.json` should declare — not
`scale`, which is what the desktop path does.

**Inline styles cannot be reached from a container query.** Scene markup lifted from an
earlier build often carries `style="display:flex;justify-content:space-between..."` on
exactly the chrome a compact variant needs to restack. Give those elements real class
names first; positional selectors like `.pu-stage > div:first-child` break as soon as the
markup moves.

**Check it by measuring, not by looking.** For every scene at 375 px, assert the stage's
right edge is inside its slot and record the heights; a spread of more than roughly 2× is
the signal that one scene needs more trimming.
