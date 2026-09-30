# UI reconstruction

Used in phases 7 and 9. Goal: turn the inventory into a structured scene spec, then rebuild each scene as live, faithful, maintainable HTML/CSS/JS, delivered as a component in the site's stack (see `hugo-bookshop-target.md`).

## The scene spec (phase 7)

The spec is the intermediate representation between "what I saw" and "what I build". Its format, component vocabulary, states, content layer, timeline and responsive rules are defined in `ui-scene-system.md`, which is the authority. Follow it.

In summary:

- Merge the screenshot records (`screenshot-analysis.md`) and video records (`video-analysis.md`) into one scene definition per scene, written to `spec/scenes.json`.
- Structure, content and presentation stay in separate layers. Structure never contains literal text or style values.
- Every text item has a role, a translate flag and a sensitivity class.
- The timeline uses relative timing and ends in the single final state.
- Record `approximations` (where the rebuild deliberately differs from the reference, and why) and `uncertainties` carried over from the analysis.
- Decide reuse: which kit patterns and existing scenes apply, and which parts are new.

After writing the spec, summarize it in plain language for the user and wait for approval.

## Building the scene (phase 9)

Build from the **sanitized** spec as a **portable component**: markup, scoped styles and player hooks, written once and used unchanged in the preview and in the handoff bundle. In the bundle it takes the site's component shape (blueprint with defaults for every field, template, stylesheet) as described in `hugo-bookshop-target.md`. Reuse kit patterns first. Real sensitive values must not appear in code, comments, alt text, data attributes, content files or filenames.

Scene text is rendered from fields by the template, so each language gets its own text. Do not hard-code strings in the template or in scripts. Do not embed scenes as raw HTML in markdown, and do not add inline scripts.

### Structure

- Use **semantic HTML**: lists for lists, tables for tabular data, buttons for buttons, headings only where they are true headings. The scene is a picture of a product, but the markup should still make sense to a reader.
- Author every scene in its **final state**. The animation runtime rewinds it on load and replays it. Without JavaScript, or with reduced motion, the visitor sees the complete UI.
- Each scene is one root element: `<figure class="product-ui" data-scene="scene-id">`. Include a `figcaption` or an accessible description from the spec's `accessibility.description`. Primitive classes use the `pu-` prefix (see `ui-scene-system.md`).
- Give animatable elements stable hooks (`data-target="msg-2"`) that match spec ids. Do not target by tag or position.

### Styling

- Scope all product styles under `.product-ui[data-scene]` or a product theme class, in the scene component's stylesheet. Never style generic tags globally.
- Define the product theme as `--product-*` custom properties (colors, fonts, radii, shadows, spacing) taken from the analysis. Do not use the site's tokens inside the product UI. Add a short comment that these values reproduce the product's look.
- Lay out with flexbox and grid. Avoid absolute positioning except for overlays, cursors and badges.
- Size with container-relative units so the scene scales with its box (see `responsive.md`). Avoid fixed pixel widths on the root.
- Fonts: use the product's font if it is available and licensed, otherwise the closest system or web font, and record the substitution in `approximations`.
- Icons: inline SVG using `currentColor`. Keep them simple. Do not embed icon fonts or raster icons.
- Avatars: initials on a colored circle, or a neutral shape. Never use real people's photos.
- Charts: inline SVG or CSS built from spec data. Keep data values consistent with the privacy map.
- No raster screenshots inside a scene.

### Two collisions that silently break a scene

**Never reuse the variant class as a layout class.** A scene figure carries `pu-<variant>`
(`pu-ex`, `pu-chat`). If a rule in the scene's own stylesheet also targets that name — because
an inner wrapper was given the same class — the rule lands on the **figure** as well. Seen for
real: `.pu-ex{display:flex}` was meant for an inner div, hit the figure, made `.pu-stage` a flex
item, and because the stage is a container-query container (`container-type: inline-size`) it
could not size from its contents and collapsed to the width of its own borders — 2px. The scene
rendered as a sliver with no error anywhere. Prefix inner layout classes differently
(`pu-app`, not `pu-ex`), and give the stage `width:100%; min-width:0` so a host or a stray rule
cannot collapse it.

**Never let a heading break mid-word.** `overflow-wrap: anywhere` on a table header turns
"Health" into "Healt h" and "Budget Pacing" into "Budge t Pacin g" the moment a column is
narrow. Use `word-break: keep-all; overflow-wrap: normal` and solve the width instead.

### Surviving the host site's CSS

The scene is dropped into a page that has its own CSS reset (this site's stylesheet resets `svg`, lists and paragraphs). Never rely on browser defaults inside a scene:

- Set `display` explicitly on inline icons (`.ic { display: inline-block; vertical-align: -.2em }`). A reset that makes `svg` a block breaks any label-plus-chevron on one line.
- Put the icon and label in an `inline-flex` container with `white-space: nowrap` when they must stay together.
- Set list markers explicitly (`list-style: decimal outside`) and use `display: list-item` on items. Do not turn an `ol` into a flex container, which loses the markers.
- Set margins explicitly on paragraphs and headings. Set `box-sizing`.
- **Test the scene with the site's real stylesheet, or with a reset that mimics it**, not only on a blank page.

### Rebuild the chrome, not just the data

The commonest way a scene fails to look like the product is that it reproduces the **content**
faithfully and leaves out the **furniture**. A table with the right columns and the right
numbers, floating on white, reads as a generic spreadsheet. What makes a screen recognisable is
almost never the data — it is the frame around it.

Before drawing anything, list the product's identifying furniture from the reference and decide
which of it survives into the slot. From a real Explorer reconstruction, in the order that mattered:

1. **The app's own navigation.** A dark rail of icons down the left is the single strongest
   signal that this is *that* product. Keep it even when it costs width, and keep its colour.
2. **Secondary panels.** The scope tree with its checkboxes, segmented control and platform
   marks. Without them the table has no context and could be anyone's.
3. **Location.** Breadcrumb and page title. A product screen always tells you where you are.
4. **Toolbars on both sides.** Search / Filters / Columns on the left, view / date range /
   primary action on the right. The asymmetry is part of the look.
5. **Row furniture.** Stars, per-row platform marks, linked names in the product's link colour,
   status pills, avatar chips, the overflow kebab. These read as "a real row" at a glance.
6. **The footer.** Rows-per-page and a result count. Tables in products always have one.
7. **Header sub-labels.** Small qualifiers under a column name ("This budget cycle") are
   distinctive and cheap to include.

Colour matters as much as structure. Take the product's link blue, its nav navy, its status
greens and reds from the reference; a scene in the skill's default accent looks like a mockup
of the product rather than the product.

**If the slot is too narrow for all of it, cut data columns before you cut furniture.** A table
with five columns and its real navigation is recognisable; a table with nine columns and no
navigation is not.

### Every frame must be a believable product state

A scene is not "a screenshot that ends up correct". Someone will see it **mid-animation** — on
first paint, between loop cycles, in a screenshot taken by a colleague, in a social card. Every
intermediate frame has to look like a real screen a real user could be looking at. Check the
first frame and two or three middle frames the way you check the final one.

The three things that break this, in order of how often they do:

1. **A titled container with nothing in it.** A panel headed "Preview" holding an empty white
   box reads as a broken screenshot, not as a product. Give the container an **`empty-state`**
   component that is visible in every state before the content arrives, and hide it in the state
   where the content appears. Real products always say something there.
2. **Derived values that only animate at the end.** Counters, totals, "3 of 15", "2 selected",
   progress and summary numbers are computed from what is on screen. Bake one in as static text
   and every earlier frame contradicts itself: the counter claims three headlines while two
   fields are visibly empty. Either drive the value from the state model, or word it so it is
   true throughout (a slot count is true, a filled count is not).
3. **Chrome that implies a step already taken.** A "Saved" badge, an active tab, or a success
   banner authored into the final markup is a lie in every frame before it.

The rule: **if a value or element is true only at the end, it belongs to a state, not to the
markup.** Anything authored outside the state model must be true at time zero.

### Reserved space

Anything that appears and disappears (a loading indicator, a tooltip, a toast) must not leave a gap in the final state. Overlay it on the space the next thing will fill (`position: absolute` inside a wrapper around the element that follows) instead of giving it its own row.

> Before anything in this section: **scan the reference** (`reference-scanning.md`). It covers
> getting images out of a supplied document, measuring palette and layout bands, authoring at
> the reference's own size, replay, and verifying what actually rendered.

### Paint it in the product's own colours — measured, not remembered

**Do this before drawing anything.** A scene whose layout is right and whose palette is wrong
does not read as the product; it reads as "some SaaS app". This is the most common fidelity
failure and the easiest to miss, because nothing about it looks broken.

```bash
python3 scripts/extract_palette.py input/references/images/*.png
```

It prints the palette ranked by use, marks the colours that appear across several screenshots
(those are the product's own, not one screen's content), and names the **accent**: the saturated,
reasonably dark colour with the widest spread. Build `--product-*` from that output.

Then make it checkable, and keep it checkable:

```bash
python3 scripts/extract_palette.py input/references/images/*.png --check scenes.css
```

Exit 1 means a theme colour appears nowhere in the references. Treat it as a build failure.

> This is not hypothetical. A build once shipped `--product-accent:#4F63E7` under a comment
> reading *"Faithful to the tool screenshots"*. The product's actual accent was `#4B288F`, a
> purple dominant in 10 of 11 screenshots; `#4F63E7` appeared in none. Every scene was subtly
> wrong and the comment asserted the opposite. **Never write a fidelity claim you have not run a
> check for.**

Three rules the checker cannot enforce for you:

- **Platform and vendor marks keep their own brand colours.** Google blue `#4285F4`, Meta
  `#1877F2`, a star `#F4B400`. Repainting them to the accent destroys the thing that makes a
  multi-platform view instantly legible.
- **State colour is part of the palette**, not decoration: the success green, the warning amber,
  the pale tint each uses as a cell or chip background. Extract them too.
- **A pale tint is not the accent.** Large soft fills win on pixel count; the accent is the
  saturated colour the product uses for links, headings and primary buttons.

### The visual signature

Beyond the palette, every product screen has a few features that carry its identity. Losing them
is how a reconstruction becomes generic even when the numbers are right. List them from the
reference, then confirm each one survived:

| Signature | What it looks like | Why it matters |
|---|---|---|
| Accent colour | Links, primary button, headline figures | The single strongest identity cue |
| Icon language | Platform marks, star/favourite, expand carets, row action icons | Says *multi-platform account tool*, not *spreadsheet* |
| Colour-coded state | Green/amber dots, a tinted cell behind a good status, an amber count chip | Turns a table into a dashboard |
| Density | How many columns, how tight the rows | A 4-column table does not read like a 16-column console |
| Supporting text | The subtitle under the title, the footnote under the panel | Product screens explain themselves; marketing mockups do not |

### Reducing a wide table without making it generic

A 16-column console cannot render legibly in a 517px slot — a faithful copy would be unreadable,
so reduction is correct. Silent reduction to four plain columns is not. The rule:

1. **Keep the columns the claim needs**, plus enough neighbours that the row still looks like a
   row from that console. Six to eight beats four.
2. **Keep the signature before you keep data.** A star column, a platform icon and an expand
   caret cost almost no width and carry more recognition than two more numeric columns.
3. **Keep one instance of each visual treatment** that appears in the reference — one tinted
   status cell, one amber chip, one muted em-dash for "not applicable".
4. **Say what you dropped**, in the scene's `approximations`. "Reduced from 16 columns to 8;
   dropped Impressions, Clicks, Avg CPC, Quality Score, Conv, Cost/Conv" is reviewable. Saying
   nothing is not.

### Fidelity check

Run the palette check first — it is the only one of these that is mechanical, and it catches the
failure that is hardest to see. Then compare the final state with the reference keyframe side by
side and fix in this order:

1. **Palette** — `extract_palette.py --check` exits 0. Blocking.
2. **Signature** — every row of the table above is present, or its absence is recorded.
3. Layout, proportions and density.
4. Type size, weight and line height.
5. Spacing and alignment.
6. Radii, borders, shadows.

Fix obvious mismatches yourself. Leave subjective judgment calls for the validation review. The
goal is faithful and believable, not a pixel diff — but "faithful" is a claim, and items 1 and 2
are how you earn it.

### Code quality

- One component per scene (a Bookshop component in the handoff bundle), named after what it shows. Split into sub-components only when a scene grows beyond a few hundred lines.
- Meaningful class names (BEM-style or similar, consistent across the build). No utility soup, no inline styles except dynamic values.
- No dead code, no commented-out blocks, no leftover reference filenames.
- Keep a scene's markup short enough to read. If it exceeds a few hundred lines, split into sub-components.

## When not to reconstruct

Photos, maps, video within video, third-party embeds and complex illustration. Propose a simplification, crop or original illustration and get a decision. Mark it as an `asset` in the spec with the reason.
