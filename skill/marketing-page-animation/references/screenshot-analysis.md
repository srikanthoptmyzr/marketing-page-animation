# Screenshot analysis

Used in phase 4 (and on video keyframes in phase 5). Goal: turn a product screenshot into a **structured analysis record** that describes what is visible precisely enough to be rebuilt as HTML/CSS later, without looking at the image again. This document defines the method. It does not implement any UI.

## Principles

1. **A screenshot is one moment.** It shows one state. Other states, and any motion, are *inferred*, never observed. Mark every inference, and prefer a video to confirm interactions.
2. **Describe, then classify, then decide.** First record what is there. Then classify each element. Only then say how it should be built.
3. **Colors and layout are measured, not estimated.** Before recording anything else, scan the image
   (`reference-scanning.md`): `scripts/scan_reference.py` for one screen's palette, page background,
   section bands and column gutters, and `scripts/extract_palette.py` across **all** the screenshots at once and build the scene theme from
   its output. Colour read by eye is the one estimate that is never good enough: an accent that is
   close but wrong makes every scene read as a generic app, and it does not look broken, so it
   survives review. Measurements and fonts remain estimates — label those with a confidence.
   A colour that appears across several screenshots is the product's own; one that appears in a
   single shot may be that screen's content. Platform marks keep their own brand colours.
4. **Never invent.** Unreadable or cropped text is recorded as unreadable, and becomes an open question.
5. **Sensitive data is registered, not copied.** The first time a sensitive value is seen, register it as an entity in `.private/` and refer to it by entity id, category and location from then on. Never write the value into the record (see `privacy-masking.md`).
6. **Product versus site.** You are describing the product's own UI. Do not mix in the marketing site's styling.
7. **Stay generic.** Use the shared component vocabulary, not names tied to one product.

## Step 0: Intake

Record before analyzing:

- File, pixel size, and display scale (a 2x screenshot has twice the pixels). If unknown, infer from text size and say so.
- Theme (light or dark), UI language, and whether any device or browser frame is included.
- What the screenshot is **for**: which page claim it supports, and which scene it feeds.
- Whether it contains real customer or account data (nearly always yes).
- Image quality: blur, compression, cropping, overlays that hide content.

Give the screenshot an id (kebab-case, describing the moment, for example `assistant-answer-with-chart`).

## The passes

Work through the passes in order. Each pass adds to the record.

### Pass 1: Structure

Identify, from outermost to innermost:

- **Overall container.** The frame the product UI sits in: window, card, panel, phone frame, or borderless crop. Its shape, border, radius, shadow, and whether it is the whole app or a cropped region.
- **Background.** The container's fill, any gradient or pattern, and the page or surround behind it. Distinguish product background from the screenshot's own canvas.
- **Regions.** Header, navigation, sidebar, main content, secondary panels, footer, overlays (modal, menu, tooltip, toast), floating elements. Their arrangement (rows, columns, grid), proportions, and stacking order.
- **Layout model.** How the regions divide the space, which regions are fixed, which scroll, which are flexible. Alignment axes that repeat (left edges, baselines, centers).

### Pass 2: Components

List every distinct element and give it a type from the shared vocabulary (see below). For each, record what applies:

- **Header:** title, breadcrumbs, actions, search, user menu.
- **Navigation:** tabs, sidebar items, breadcrumbs, steppers. Which item is active.
- **Cards:** structure (media, title, body, footer), grouping, layout.
- **Buttons:** label, variant (primary, secondary, ghost, icon-only), size, icon, state.
- **Inputs:** type (text, select, checkbox, toggle, composer), placeholder, value, focus or error state.
- **Text hierarchy:** levels in use (title, heading, subheading, body, caption, label, code), with size, weight, color and line spacing ranked from largest to smallest.
- **Icons:** style (outline, filled), approximate size, meaning. Note whether a standard glyph or custom artwork.
- **Images:** what each is (photo, avatar, illustration, logo, screenshot within the screenshot), size, crop, radius.
- **Charts:** type (line, bar, donut, sparkline), axes, series count, legend, labels, gridlines, approximate data shape and values.
- **Tables:** columns, header style, row count, alignment per column, row states, cell types (text, number, badge, bar).
- **Badges and chips:** label, color role, shape.
- **Status indicators:** dots, pills, progress bars, spinners, trend arrows, and what they mean.
- **Product-specific UI:** anything particular to this product that the vocabulary does not cover (a custom widget, a domain-specific control). Record what it is, how it behaves, and give it type `custom` with a description.

Record parent and child relationships so the nesting can be rebuilt.

### Pass 3: Visual properties

For the container and each component group, record:

- **Spacing.** Padding inside components, gaps between siblings, section spacing. Identify the underlying rhythm (often a 4 or 8 unit grid).
- **Borders.** Presence, width, color, style, and where used (dividers, card outlines, input outlines).
- **Radius.** Per element class (container, card, button, input, chip, avatar). Note pill and circle shapes.
- **Shadows.** Which elements have them, and whether they are subtle, medium or strong, with approximate offset and blur.
- **Alignment.** Text alignment, vertical alignment in rows, alignment of columns, optical alignments that are intentionally off-grid.
- **Color roles.** Background, surface, text primary, text secondary, border, accent, semantic colors. Hex values estimated, or sampled (see measurement).
- **Typography.** Family (best guess), weights, sizes per level, letter spacing if obvious.
- **Density.** Compact, comfortable or spacious.

### Pass 4: Dimensions

Choose a **design width** for the scene: the width of the screenshot in design pixels (physical pixels divided by the display scale). Record:

- Design width and aspect ratio.
- Approximate width and height of each major region and component, as pixels in design units, with a confidence.
- Proportions that matter more than absolute size (for example a sidebar is roughly a quarter of the width).

### Pass 5: Classification

Classify every element into exactly one primary class, with a reason.

| Class | Meaning | Decision rule |
|---|---|---|
| **Static UI** | Structure and chrome that never changes in the scene | Labels, frames, icons, dividers, backgrounds, fixed navigation |
| **Dynamic content** | Text or values that would differ per user or over time | Names, numbers, messages, dates, chart data, list items |
| **Interactive element** | Something a user can act on | Buttons, links, tabs, inputs, toggles, menus, rows |
| **Animation candidate** | Something that should move or change to tell the story | The element that carries the claim: a message that appears, a chart that draws, a number that counts, a result that highlights |
| **Real image asset** | Something that must remain an actual image | See rules below |

An element can be static and interactive, or dynamic and an animation candidate. Record a primary class and any secondary ones.

**Animation candidates** are chosen by the story, not by what could move. Ask: does the page claim depend on watching this change? If yes, it is a candidate. Mark whether the change is **observed** (visible in this image, for example a half-typed input or a loading spinner) or **inferred** (a plausible sequence). Inferred animations need confirmation from a video or the user.

**Real image assets** stay images only when reconstruction is not sensible:

- Photographs and illustrations with no reasonable vector or CSS form.
- Brand logos, which must come from the supplied official asset, never redrawn.
- Third-party maps or embedded content.

Everything else is rebuilt: icons as inline SVG, avatars as initials or neutral shapes, charts as SVG. **Real people's photos and customer logos are never used**: they are sensitive, and are replaced. Record the reason for each asset.

### Pass 6: Content, sensitivity and translation

Build a text inventory. For each text item record:

- **Role:** product chrome (labels, buttons, headers, placeholders) or data (names, numbers, messages, sample content).
- **Sensitivity class:** `none`, or one of the classes in `privacy-masking.md` section 1 (`account-id`, `campaign-id`, `entity-name`, `person-name`, `email`, `phone`, `company`, `url`, `secret`, `amount`, `address`, `search-term`, `other-pii`). For sensitive items record the class, the entity id and the location, not the value.
- **Translate:** whether it should be localized (see `localization.md`).
- **Legibility:** readable, partly readable, or unreadable.
- **Expansion risk:** whether the space around it would break if the text grew 40 percent.

### Pass 7: States

- Record the **observed state** of the screenshot (for example: response shown, input empty).
- List **other states** the scene needs to tell its story (initial, typing, loading, response, selected, hover, error), each marked observed or inferred.
- Note states needed for interactivity even if not part of the story (hover, focus, disabled), so the rebuilt UI is complete.
- Flag what a video or the user must confirm.

### Pass 8: Responsive considerations

Decide how the scene should behave at other widths (see `responsive.md`):

- **Legibility.** Estimate the smallest text at the design width. If it would fall below about 11 pixels when scaled to a phone, a compact variant is needed.
- **What matters most.** The part of the UI that carries the claim, which must survive on mobile.
- **Compact strategy.** Crop (drop a sidebar or panel), stack (columns to one column), simplify (fewer rows or columns), or shorten the sequence.
- **Fixed proportions.** Elements that must scale together (a chart with its labels) versus elements that can reflow.
- **Text expansion.** Where longer translations would overflow.

### Pass 9: Semantics and accessibility

- Map components to the right native elements (lists, tables, buttons, headings), noting where the screenshot suggests a different one.
- Draft a one or two sentence description of the scene for assistive technology.
- Estimate color contrast of key text and status colors, and flag pairs that look weak.
- Note focus order and any interaction that needs keyboard support.

### Pass 10: Reuse check against the site kit

- Identify anything that matches an existing site pattern (a card, a button style, a section shell). Product UI is not site chrome, so most of a scene will be new.
- Record parts of the surrounding page the scene will sit in (see `site-kit.md`), and flag kit gaps.

### Pass 11: Confidence and open questions

Give an overall confidence (high, medium, low) and per-area confidence where it varies. List open questions: unreadable text, unclear states, ambiguous components, unknown fonts, anything to confirm with a video or the user.

## Measurement method

- **Calibrate.** Find something whose size you can trust, such as body text (commonly 13 to 16 design pixels) or standard controls, and scale other measurements from it.
- **Work in design pixels**, and snap to the underlying grid (4 or 8) unless something clearly is not on it.
- **Sample colors** with a script (read pixel values at chosen coordinates) when the image file is available. Otherwise estimate and mark them as estimates. Never present an eyeballed color as exact.
- **Fonts.** Identify the family from letterforms if possible, otherwise give the closest class (geometric sans, humanist sans, monospace) and record a substitution.
- **Relative before absolute.** When unsure of exact pixels, record ratios (a card is twice as tall as it is wide).
- **Zoom.** Inspect small regions closely (icons, badges, borders) rather than judging from the full image.

## Component vocabulary

Use the vocabulary defined in `ui-scene-system.md`: primitives (`frame`, `header`, `sidebar`, `tabs`, `list`, `list-item`, `card`, `table`, `chart`, `message`, `composer`, `input`, `button`, `chip`, `badge`, `status`, `avatar`, `icon`, `toggle`, `menu`, `tooltip`, `modal`, `notification`, `cursor`, `image`, `text`) and patterns (`message`, `chat`, `dashboard`, `metric`, `chart`, `table`, `notification`, `recommendation`, `change-request`, `approval`, `success-state`, `loading-state`, `cursor`, `tooltip`). Use `custom` for product-specific UI, with a description and behavior. Use variants (`variant: user`, `variant: assistant`) instead of new types. Add a new type only when nothing fits.

## The analysis record

The output of this method is one YAML record per screenshot, saved as `analysis/screenshots/<id>.yaml`. It is an intermediate document for Claude, not something to show the user as code. In phase 7 the records for screenshots and video scenes are merged into `spec/scenes.json`, the single source of truth. Field names are chosen so the merge is direct.

```yaml
analysis:
  id: assistant-answer-with-chart
  source: { file: input/references/images/example.png, pixels: [1440, 1080], scale: 2, theme: light, ui_language: en }
  purpose: "Shows the assistant answering a question with a chart"   # the claim it supports
  confidence: medium

scene:
  name: assistant-answer                # becomes the scene id
  stage:
    design_width: 720
    aspect_ratio: "4 / 3"
    product_theme:                      # estimates
      fonts: { family: "geometric sans (closest match)", weights: [400, 600] }
      colors: { background: "#ffffff", surface: "#f6f7f9", text: "#1d1f24", accent: "#2a6df4" }
      radius: { container: 12, card: 8, button: 6, chip: 999 }
      shadow: { container: "subtle" }
      density: comfortable

container:
  kind: app-window                      # window | card | panel | phone | borderless-crop
  border: { width: 1, color: "#e3e5e8" }
  crop: "cropped to main pane; sidebar hidden"
background: { fill: "#ffffff", surround: "transparent" }

regions:
  - { id: header, kind: header, bounds: { x: 0, y: 0, w: 720, h: 56 } }
  - { id: thread, kind: main, bounds: { x: 0, y: 56, w: 720, h: 520 }, scroll: true }
  - { id: composer-area, kind: footer, bounds: { x: 0, y: 576, w: 720, h: 104 } }

components:
  - id: title
    type: header
    parent: header
    text: { role: chrome, translate: true, sensitivity: none, legible: true }
    class: static
  - id: q1
    type: message
    variant: user
    parent: thread
    bounds: { x: 96, y: 88, w: 528, h: 44 }         # estimated
    text: { role: data, translate: true, sensitivity: other-pii, legible: true }
    class: [dynamic, animation-candidate]
    reason: "The question the story starts from"
  - id: a1
    type: message
    variant: assistant
    parent: thread
    class: [dynamic, animation-candidate]
    reason: "The answer is the payoff of the scene"
  - id: sales-chart
    type: chart
    parent: a1
    detail: { kind: line, series: 2, legend: true, axes: "x dates, y currency", shape: "rising then flat" }
    class: [dynamic, animation-candidate]
  - id: composer
    type: composer
    parent: composer-area
    class: [interactive, animation-candidate]
    text: { role: chrome, translate: true, sensitivity: none }
  - id: send
    type: button
    variant: primary-icon
    parent: composer
    class: interactive
  - id: avatar-user
    type: avatar
    parent: q1
    class: static
    build: initials-on-circle            # never the real photo

states:
  - { id: initial,  observed: false, description: "Empty thread, empty composer" }
  - { id: typing,   observed: false, description: "Question being typed in the composer" }
  - { id: response, observed: true,  description: "Answer and chart visible; this screenshot" }

animation_candidates:                    # verbs from animation-system.md
  - { target: composer, type: type,   basis: inferred }
  - { target: send,     type: click,  basis: inferred }
  - { target: a1,       type: stream, basis: inferred }
  - { target: sales-chart, type: draw, basis: inferred }

assets:
  - { id: brand-mark, why: "official logo, must not be redrawn", source: "supplied brand asset" }

sensitive_values:                        # entity id, category and location only, never values
  - { entity: person-1, category: person-name, where: "header user menu, avatar tooltip" }
  - { entity: amt-1, category: amount, where: "chart axis and answer text" }

responsive:
  min_text_px_at_design_width: 12
  compact_needed: true
  strategy: crop                         # crop | stack | simplify | shorten
  keep: [q1, a1, sales-chart]
  expansion_risks: [send, title]

accessibility:
  description: "A user asks a question and the assistant replies with a short answer and a chart."
  contrast_flags: ["secondary text on surface looks low"]

reuse:
  site_patterns: []                      # product UI is new; note surrounding page patterns separately
  kit_gaps: []

open_questions:
  - "Is the chart's second series a forecast or a comparison?"
  - "Confirm typing speed and cursor use from the video."
```

Keep the record complete but plain. Omit fields that do not apply rather than filling them with guesses.

## Handing the record on

- **Phase 5 and 6** add interactions from videos and confirm or correct the inferred states and animations.
- **Phase 7** merges the records into `scenes.json`: `scene` and `components` carry over, `states` become the final state and timeline anchors, `animation_candidates` become timeline steps with times, and `open_questions` must be resolved or accepted as labelled defaults.
- **Phase 8** uses `sensitive_values` and the sensitivity class on each text item to drive replacement.

## Checklist before finishing

- Container, background and every region are recorded.
- Every visible component has a type, a parent and a class.
- Every text item has a role, sensitivity, translate flag and legibility.
- Measurements are in design pixels and marked as estimates.
- Colors are sampled or marked as estimates.
- The observed state is identified, and every other state is marked inferred.
- Animation candidates are tied to the page's claim, not to whatever could move.
- Every real image asset has a reason, and no real person's photo or customer logo is kept.
- Responsive strategy and minimum text size are stated.
- Open questions are written down.

## Common mistakes

- Treating one screenshot as if it showed an animation.
- Recording sensitive values in full in the notes instead of their entity ids.
- Copying the product's look into the site styling, or the reverse.
- Inventing text for anything unreadable.
- Marking everything an animation candidate. Animate only what carries the claim.
- Keeping an image asset because redrawing looks like work.
- Using product-specific type names instead of the shared vocabulary.
