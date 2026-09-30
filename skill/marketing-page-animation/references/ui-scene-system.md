# UI scene system

Used in phases 7, 9, 10 and 12, and as the vocabulary for phases 4 to 6. Goal: define one generic, reusable way to represent a product experience as a **UI scene** that can be rebuilt as HTML/CSS/JS, animated, translated, restyled, and reused across pages and products.

This is the authoritative definition of the scene format. Other references (`screenshot-analysis.md`, `video-analysis.md`, `ui-reconstruction.md`, `animation-system.md`) feed into it or build from it. Nothing here is specific to one product.

## 1. What a UI scene is

A **UI scene** is a small, self-contained, animated reconstruction of one product moment that proves one claim. Examples: a user asks an assistant a question and gets an answer with a chart; a proposed change is reviewed and approved; a dashboard updates after an action.

A scene is:

- **Self-contained.** It brings its own structure, styles and timeline, and depends on nothing on the surrounding page except a container.
- **Final-state-first.** Its markup is the complete finished UI. Motion is layered on top and can always be skipped.
- **Data-driven.** Text and numbers live in a content layer, apart from structure and presentation.
- **Themeable.** Its look comes from a product theme, which can be replaced.
- **Localizable.** Every visible string can be translated by the site's process.
- **Accessible.** It has a name, a description, controls and a reduced-motion path.
- **Reusable.** It can be placed on many pages, in many languages, with different content, without being rewritten.

A scene is **not** a screenshot, not a whole app, and not a page. It is one moment of the product told through a few components.

## 2. Anatomy

```text
Scene
 ├── Meta              id, claim, source, version
 ├── Theme             product look (fonts, colors, radii, shadows, density)
 ├── Components        what is on screen: a tree of vocabulary types
 ├── Content           all text, numbers and data, keyed, per language
 ├── States            named stable moments and which components are visible
 ├── Timeline          how the scene moves from state to state
 ├── Responsive rules  how it adapts to the space it is given
 └── Accessibility     name, description, semantics, controls, reduced motion
```

Three layers must stay separate:

| Layer | Holds | Changes when |
|---|---|---|
| **Structure** | Components, states, timeline | The story changes |
| **Content** | Text, numbers, chart and table data | The language, the example or the data changes |
| **Presentation** | Theme, primitive styles, responsive rules | The product look or the screen size changes |

## 3. How a scene is represented

A scene has one **scene definition** (JSON). During a page build, the definitions live in `spec/scenes.json` (one entry per scene). A scene worth reusing is also saved as a **scene package**:

```text
scenes/<scene-id>/
  scene.json          Meta, components, states, timeline, responsive, accessibility
  content.en.json     Content layer, source language
  theme.json          Product theme
  timeline.json       Timeline, if kept as its own file
  README.md           What it shows, what to parameterize
```

Top-level fields of `scene.json`:

| Field | Meaning |
|---|---|
| `id` | Kebab-case, describes what it shows. Unique in the library |
| `version` | Semantic version. Bump when structure or timeline changes |
| `claim` | The one thing this scene proves |
| `source` | Where it came from (video ranges, screenshot ids), kept for traceability. Never shipped |
| `theme` | Reference to a theme (`theme.json`) |
| `stage` | Aspect ratio and container behavior. The design width lives in `responsive.designWidth`, which is the authoritative value |
| `components` | The component tree |
| `content` | Reference to the content file and the content schema |
| `states` | The state machine |
| `timeline` | The animation sequence |
| `responsive` | Variants and rules |
| `accessibility` | Name, description, semantics, controls |
| `approximations` | Where the rebuild deliberately differs from the reference, and why |
| `uncertainties` | Assumptions carried over from the analysis |

### Compact example

A generic scene: a user asks an assistant a question, and it answers with a metric, a recommendation, and an approval.

```json
{
  "id": "assistant-recommendation-approval",
  "version": "1.0.0",
  "claim": "Ask in plain language, review a proposed change, and approve it in one click",
  "theme": "theme.json",
  "stage": { "aspectRatio": "4 / 3" },

  "components": [
    { "id": "chat", "type": "chat", "children": [
      { "id": "q1", "type": "message", "variant": "user", "content": "q1" },
      { "id": "load", "type": "loading-state", "variant": "dots" },
      { "id": "a1", "type": "message", "variant": "assistant", "content": "a1", "children": [
        { "id": "m1", "type": "metric", "content": "m1", "variant": "trend-up" },
        { "id": "rec", "type": "recommendation", "content": "rec", "children": [
          { "id": "chg", "type": "change-request", "content": "chg" },
          { "id": "appr", "type": "approval", "content": "appr" }
        ]}
      ]}
    ]},
    { "id": "composer", "type": "composer", "content": "composer" },
    { "id": "ok", "type": "success-state", "content": "ok" },
    { "id": "note", "type": "notification", "content": "note" },
    { "id": "cur", "type": "cursor" }
  ],

  "states": [
    { "id": "initial",  "visible": ["composer"] },
    { "id": "asked",    "visible": ["composer", "q1"] },
    { "id": "loading",  "visible": ["q1", "load"] },
    { "id": "answered", "visible": ["q1", "a1", "m1"] },
    { "id": "proposed", "visible": ["q1", "a1", "m1", "rec", "chg", "appr"] },
    { "id": "approved", "visible": ["q1", "a1", "m1", "rec", "chg", "ok", "note"], "final": true }
  ],

  "timeline": [
    { "id": "t1", "at": 400,        "do": "type",   "target": "composer", "source": "q1" },
    { "id": "t2", "after": "t1", "delay": 300, "do": "click", "target": "composer.send" },
    { "id": "t3", "after": "t2", "do": "enter-state", "state": "asked" },
    { "id": "t4", "after": "t3", "delay": 200, "do": "enter-state", "state": "loading" },
    { "id": "t5", "after": "t4", "delay": 1000, "do": "enter-state", "state": "answered" },
    { "id": "t6", "with": "t5", "delay": 100, "do": "stream", "target": "a1", "unit": "word", "duration": 1400 },
    { "id": "t7", "after": "t6", "do": "count", "target": "m1" },
    { "id": "t8", "after": "t7", "delay": 400, "do": "enter-state", "state": "proposed" },
    { "id": "t9", "after": "t8", "delay": 700, "do": "cursor-moves", "to": "appr.confirm", "duration": 700 },
    { "id": "t10", "after": "t9", "do": "click", "target": "appr.confirm" },
    { "id": "t11", "after": "t10", "do": "enter-state", "state": "approved" },
    { "id": "t12", "after": "t11", "delay": 3000, "do": "loop" }
  ],

  "responsive": {
    "designWidth": 720, "minTextPx": 11,
    "variants": [ { "name": "compact", "below": 520, "strategy": "simplify", "hide": ["note", "cur"], "timeline": "default" } ]
  },
  "accessibility": {
    "name": "Assistant recommendation demo",
    "description": "A user asks a question. The assistant answers with a metric and a recommended change, and the user approves it."
  }
}
```

The text itself is not in the scene definition. It is in the content file (see section 7).

## 4. How components are represented

A component is one node in the scene's tree.

| Field | Meaning |
|---|---|
| `id` | Unique within the scene. Timelines, states and content refer to it |
| `type` | A type from the vocabulary (section 5). `custom` only when nothing fits |
| `variant` | A named variation of the type (`user`, `assistant`, `trend-up`, `dots`). Prefer variants to new types |
| `children` | Nested components, in order |
| `content` | The key of its content block (section 7). Never literal text |
| `props` | Structural settings that are not text (size, columns, chart kind, row count) |
| `role` | Optional semantic role override |
| `priority` | Importance for responsive rules: `essential`, `normal`, `optional` |
| `a11y` | Optional per-component accessibility settings (hidden, label) |

Rules:

- **Composition.** Patterns are built from primitives. A pattern is expanded into primitive markup at build time and is a single node in the definition.
- **Stable ids.** The same id is used in the analysis records, the definition, the markup (`data-target`) and the timeline.
- **No presentation in components.** Colors, fonts and sizes come from the theme and the primitive styles, not from component fields.
- **Custom components** carry a description and their own styles, scoped to the scene, and are documented as product-specific. If two scenes need the same custom component, promote it to the vocabulary.

## 5. The vocabulary

Two levels: **primitives** (small building blocks) and **patterns** (product-level assemblies of primitives). Both are generic. Product-specific looks come from the theme.

### Primitives

`frame`, `header`, `sidebar`, `tabs`, `list`, `list-item`, `card`, `table`, `chart`, `message`, `composer`, `input`, `button`, `chip`, `badge`, `status`, `avatar`, `icon`, `toggle`, `menu`, `tooltip`, `modal`, `notification`, `cursor`, `image`, `text`.

A few names (`message`, `chart`, `table`, `notification`, `cursor`, `tooltip`) exist both as a primitive and as a pattern built on it. The vocabulary is the union of both lists, and a component of that type uses the pattern.

Each primitive has one shared style definition, scoped under the scene root and prefixed `pu-` (for example `pu-message`). Scenes compose primitives instead of restyling them.

### Patterns

| Pattern | What it is | Anatomy | Typical variants | Typical animation | Semantics |
|---|---|---|---|---|---|
| **Message** | One utterance or entry in a conversation or feed | avatar, author, body, timestamp, actions | `user`, `assistant`, `system` | `reveal`, `type`, `stream` | list item in a log |
| **Chat** | A conversation view: a scrolling thread plus a composer | header, thread of messages, composer | `panel`, `full` | messages `reveal`, `scroll` | region with a log and a form |
| **Dashboard** | A view of several metrics, charts and tables | header, filters, metric row, chart area, table | `overview`, `detail` | metrics `count`, charts `draw`, rows `reveal` | region with headings for each block |
| **Metric** | One key number with its label and change | label, value, unit, delta, trend | `neutral`, `trend-up`, `trend-down`, `alert` | `count`, `highlight` | term and value pair |
| **Chart** | A data visualization | title, axes, series, legend, annotations | `line`, `bar`, `area`, `donut`, `sparkline` | `draw`, `highlight` | image with a text alternative and a data table |
| **Table** | Rows and columns of data | header, rows, cells (text, number, badge, bar), footer | `plain`, `selectable`, `sortable` | rows `reveal`, `select`, `highlight` | real table |
| **Notification** | A transient message about an event | icon, title, body, action, dismiss | `info`, `success`, `warning`, `error` | `reveal` (slide), `hide` | status or alert region |
| **Recommendation** | A suggestion the product makes, with its reason | icon, title, rationale, impact, actions | `suggested`, `accepted`, `dismissed` | `reveal`, `highlight` | article or group with heading |
| **Change request** | A proposed modification, shown as before and after | target, before, after, diff, impact | `single`, `multiple` | `reveal`, `highlight` on the diff | description list or table |
| **Approval** | A decision control for a proposal | prompt, primary action, secondary action, note | `confirm`, `confirm-with-note`, `batch` | `hover`, `click`, `enter-state` | group of buttons with a label |
| **Success state** | Confirmation that something completed | icon, message, result summary, next action | `inline`, `banner`, `full` | `reveal`, `draw` (check), `highlight` | status |
| **Loading state** | Indication that work is in progress | indicator, optional label | `spinner`, `dots`, `skeleton`, `progress`, `thinking-text` | loop while active, then `hide` | busy status with a text alternative |
| **Cursor** | A pointer standing in for a user | pointer graphic, click ripple | `arrow`, `hand`, `text` | `cursor-moves`, `click`, `hover` | hidden from assistive technology |
| **Tooltip** | A small label attached to an element | target, text, arrow | `top`, `bottom`, `start`, `end` | `reveal` on `hover` | described-by relation to its target |

Guidance:

- Use a pattern where it fits, a primitive where it does not, and `custom` as a last resort.
- Patterns may contain other patterns (a recommendation contains a change request and an approval).
- Error, empty and disabled states belong to the components that show them (a `notification` with variant `error`, a `table` in an empty state). They are used only if the reference shows them.
- Add a new pattern only after a second scene needs it. Record it here with the same table columns.

## 6. How states are represented

A **state** is a named, stable moment in the scene. States are the source of truth for **what is on screen**. The timeline is the source of truth for **how the scene gets there**.

```json
{ "id": "proposed", "visible": ["q1", "a1", "m1", "rec", "chg", "appr"], "props": { "appr": { "focus": "confirm" } } }
```

| Field | Meaning |
|---|---|
| `id` | Kebab-case name |
| `visible` | Component ids shown in this state. Children of a hidden component are hidden with it |
| `props` | Per-component overrides for this state (a selected row, a focused button, a different variant) |
| `final` | `true` on exactly one state: the complete, resting state |
| `basis` | `observed`, `inferred` or `assumed`, carried over from the analysis |

Rules:

- **Visibility rule.** A component is visible in a state if it, or any of its descendants, is listed in `visible`, so containers need not be listed. A component listed in no state (for example the cursor) is hidden in every state and appears only through timeline steps.
- **Final state first.** The markup is written in the final state, which is what visitors see without motion or JavaScript. Other states are derived by hiding or changing components.
- Each state must be reachable from the one before it by the timeline.
- A scene has at least two states: a start and the final one. A single-screenshot scene may have only a final state, and then it is a static scene with no timeline.
- Do not add states the reference does not show or clearly imply.
- Coarse visibility is driven by the state on the scene root (`data-state`). Fine-grained effects such as typing or drawing are timeline steps.

## 7. How content is separated from presentation

**Content** is everything a visitor can read or count: text, numbers, labels, dates, chart and table data. It never appears in the structure or the styles.

### Content file

```json
{
  "q1":  { "text": "Which campaigns should I scale this week?", "role": "data", "translate": true, "sensitivity": "none" },
  "a1":  { "text": "Two campaigns are ready to scale. Here is the strongest.", "role": "data", "translate": true, "sensitivity": "none" },
  "m1":  { "label": "Conversions", "value": 1240, "delta": 18, "format": { "value": "number", "delta": "percent" }, "role": "data", "translate": { "label": true }, "sensitivity": "amount" },
  "rec": { "title": "Increase budget", "rationale": "Strong return with room to grow", "role": "data", "translate": true, "sensitivity": "none" },
  "chg": { "target": "Campaign A", "before": "50", "after": "65", "role": "data", "translate": { "target": false }, "sensitivity": "entity-name" },
  "appr": { "confirm": "Approve", "dismiss": "Not now", "role": "chrome", "translate": true, "sensitivity": "none" },
  "composer": { "placeholder": "Ask anything about your accounts", "send": "Send", "role": "chrome", "translate": true, "sensitivity": "none" },
  "ok":   { "message": "Budget updated", "role": "data", "translate": true, "sensitivity": "none" },
  "note": { "message": "Change applied to 1 campaign", "role": "data", "translate": true, "sensitivity": "none" }
}
```

Each entry carries: the strings or values, a `role` (`chrome` or `data`), a `translate` flag, a `sensitivity` class, and for numbers a `format`. Chart and table data are content too (`series`, `rows`, `columns`).

### Rules

- **Structure never contains literal text.** Components refer to content by key.
- **Content never contains presentation.** No colors, sizes or markup inside strings. Emphasis is expressed structurally or through a variant.
- **Sensitive values are already replaced.** The content file holds only the safe values from the privacy pass (see `privacy-masking.md`).
- **One content file per language.** `content.en.json` is the source. Other languages mirror its keys and are produced by the site's localization process, not by this skill.
- **Numbers are values plus a format**, so counters and charts animate the number and format it per locale.
- **Timelines refer to content by key** (`"source": "q1"`), and read the rendered text at run time, so durations follow the language.
- **In the handoff bundle,** content becomes the page's translatable fields and UI strings, using field names the site treats as translatable (see `localization.md` and `handoff-bundle.md`).

### Presentation

- **Theme** (`theme.json`): the product's look as `--product-*` custom properties: font families, weights, sizes, colors by role (background, surface, text, muted, border, accent, success, warning, error), radii, shadows, spacing unit, density.
- **Primitive styles**: shared, use only theme properties, scoped under the scene root.
- **Site styles** never enter a scene, and theme values never leave it (see `design-system.md`).
- Changing the theme restyles every scene using it, with no edits to structure or content.

## 8. How animation timelines are represented

A timeline is an ordered list of **steps** over a millisecond clock. It uses the two-level verb vocabulary in `animation-system.md` (product interaction recipes over generic motion) plus one structural verb, `enter-state`. Prefer recipes where the video shows the interaction.

| Field | Meaning |
|---|---|
| `id` | Step id, so other steps can refer to it |
| `at` | Absolute start in ms. Use for the first step or a fixed anchor |
| `after` / `with` | Start relative to another step: after it ends, or together with it |
| `delay` | Offset in ms from the anchor |
| `do` | A verb from `animation-system.md`. Both styles are valid in one timeline; recipes are preferred where the video shows the interaction. Either a product interaction recipe (`user-types`, `system-processes`, `response-streams`, `approval-clicked`, ...) or a generic motion (`reveal`, `type`, `count`, ...), plus the structural verb `enter-state` |
| `target` | Component id, or a sub-part (`appr.confirm`) |
| `state` | For `enter-state`: the state to enter |
| `source` | For `type`, `stream`, `count`: the content key to read |
| `duration`, `effect`, `easing`, `unit`, `cps` | Verb-specific settings |
| `essential` | `true` if the step carries meaning and must survive reduced motion as an instant change |
| `basis` | `observed`, `inferred` or `assumed` |

Rules:

- **Relative timing preferred.** `after` and `with` keep edits easy: change one duration and the rest follows.
- **`enter-state` changes what is visible** according to the state definition. Verbs like `type` and `draw` add the motion inside a state.
- **Each sequence ends in the final state**, then `loop` (with a hold) if it repeats.
- **Beats.** Long timelines are grouped into named beats so a page can play only some of them.
- **Variants.** A responsive variant may name a different timeline (`compact`) that is shorter.
- **Reduced motion.** The player skips the timeline, leaves the final state, and applies `essential` steps as instant changes only where the story needs them.
- **Storage.** Small timelines may live in the definition. Larger ones go in `timeline.json`, loaded by the player from an asset file. No inline scripts (see `animation-system.md`).

Camera steps: a timeline may contain `zoom` (`to`, `scale`, `duration`) and `zoom-out`. The camera frames the target and is skipped when the target already fills the scene. Rules in `animation-system.md`.

## 9. How scenes are reused across pages

A scene is reused by keeping structure and timeline fixed and changing the layers around them.

- **Parameterize, don't fork.** A page places a scene with overrides: a different **content** file (another example or language), a different **theme** (another product), a chosen **variant**, a chosen **start trigger** (on view, on click), and optionally a subset of **beats**.
- **One definition, many placements.** The same scene may appear on several pages, or twice on one page, without id collisions, because ids are scoped to the scene root.
- **Scene templates.** A generic structure such as "question, answer, approval" can be reused with different content to make many scenes. Save it as a template and record which content keys it expects.
- **Independence.** A scene depends only on its container, the shared primitive styles, the theme and the player. It never reads page styles or page scripts.
- **Embedding contract.** A scene is placed in any container that gives it a width. It reads its settings from data attributes on its root: `data-scene`, `data-theme`, `data-variant`, `data-trigger`, `data-loop`.
- **Library.** Keep reusable scenes as packages with a short index listing id, claim, product, version, languages and required content keys. Before building a new scene, search the library for one that can be parameterized.
- **When to fork.** Fork a scene only when its structure or story differs. If only words, numbers, theme or timing differ, parameterize.
- **Versioning.** Changing structure or timeline bumps the version. Pages record which version they use.
- **Cross-product reuse.** Scenes built for one product are reused for another by swapping the theme and content. Product-specific `custom` components are the exception and are named as such.
- **Privacy.** Reusable scenes contain only safe content. Never save a package with real values.

## 10. How scenes behave responsively

A scene is responsive by **scaling and by declared variants**, driven by the width of its container, not the viewport.

- **Design width.** Each scene has a design width. The scene scales proportionally with its container using container-relative units (see `responsive.md`).
- **Legibility limit.** `minTextPx` is the smallest text size allowed after scaling (about 11). When scaling would go below it, a variant takes over.
- **Variants.** A variant is declared in `responsive.variants` with a name, the container width below which it applies, a **strategy**, and the components it affects:

| Strategy | What it does |
|---|---|
| `scale` | Shrink proportionally (default, above the legibility limit) |
| `crop` | Show only part of the scene, dropping a sidebar or panel |
| `stack` | Reflow side-by-side regions into one column |
| `simplify` | Hide `optional` components and reduce rows, columns or series |
| `shorten` | Use a shorter timeline that keeps the essential beat |
| `swap` | Replace a component with a compact version of it (for example a table with a list) |

- **Priority.** Components are marked `essential`, `normal` or `optional`. Variants remove `optional` first, then `normal`, and never `essential`.
- **Text expansion.** Components that contain text must tolerate 30 to 40 percent longer strings. Do not fix text widths.
- **Touch.** Interactive parts shown in a scene are illustrations, but any real controls (play, pause, replay) meet touch-size rules.
- **Motion.** On small screens, avoid several scenes animating at once. Off-screen scenes pause.
- **Both directions.** Layout uses logical properties so a scene works right-to-left if a language needs it.
- **Declared, not improvised.** Each scene states its design width, legibility limit and at least one compact strategy before building.
- **Full rules.** Variant fields, the choice by scale, what to keep and drop, and transformations for common compositions are in `responsive.md`. A variant may also declare its own `aspectRatio`, `maxHeight` and compact content keys.

## 11. Accessibility rules

- **Name and description.** Every scene has an accessible name and a one or two sentence description of what it shows, taken from `accessibility`.
- **Internals hidden.** Animating internals are hidden from assistive technology (`aria-hidden`), and the description and final text are exposed instead. Assistive technology must not announce each typed character.
- **Semantics for the final state.** Primitives use native elements where they exist: real tables, lists and buttons. Charts have a text alternative and, where useful, a data table.
- **Controls.** A scene that animates for more than about five seconds, or loops, has play, pause and replay controls that are keyboard operable and labelled.
- **Reduced motion.** `prefers-reduced-motion` renders the final state, with no loop and no cursor motion.
- **Focus.** Nothing in the scene traps focus. The cursor pattern is never focusable.
- **Contrast.** Theme color pairs meet WCAG 2.1 AA for text and UI elements. Flag failures in the theme rather than hiding them.
- **Language.** The scene root carries the page's language so text is read correctly.
- **No flashing.** Nothing flashes more than three times per second.

## 12. Definition validity

A scene definition is valid when:

- Every component id is unique and every `children` reference exists.
- Every component type is in the vocabulary or is `custom` with a description.
- Every `content` key resolves in every content file.
- Every text entry has `role`, `translate` and `sensitivity`.
- Exactly one state is `final`, and every state's `visible` ids exist.
- Every timeline target, `source`, `after` and `with` reference exists, and the sequence ends in the final state.
- The responsive block has `designWidth`, `minTextPx` and at least one variant.
- The accessibility block has a name and a description.
- Assumptions and uncertainties from the analysis are carried in `approximations` and `uncertainties`.
- No literal text, color values or sizes appear in `scene.json`.

## 13. Where each part comes from

| Scene part | Produced from |
|---|---|
| Components, theme, content roles, sensitivity | `screenshot-analysis.md` records |
| States, timeline, timing, uncertainties | `video-analysis.md` records |
| Safe content values | The privacy pass (`privacy-masking.md`) |
| Site context around the scene | The site kit (`site-kit.md`) |
| Markup and styles | `ui-reconstruction.md` |
| Player behavior | `animation-system.md` |

## 14. Checklist

- The scene proves one claim, and the claim is stated.
- Components use the vocabulary. Custom types are justified.
- Structure, content and presentation are in separate layers.
- One final state, with earlier states derived from it.
- Timeline uses relative timing, ends in the final state, and marks `essential` steps.
- A scene could be placed on another page, in another language, or with another theme without edits to structure.
- A design width, a legibility limit and a compact strategy are declared.
- Accessibility name, description and controls are defined.
- No real data is anywhere in the package.

## 15. Common mistakes

- Putting text, colors or sizes inside component definitions.
- Modeling the screenshot's pixels instead of its components.
- Creating a new type for something a variant of an existing type covers.
- Building states that the reference never shows.
- Timelines in absolute milliseconds only, so any change means retiming everything.
- Scenes that reach into page styles or scripts, so they cannot be reused.
- Forking a scene when only content or theme changes.
- Compact variants that just shrink until text is unreadable.
- Announcing animation to screen readers.
