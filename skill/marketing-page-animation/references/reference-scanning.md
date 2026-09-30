# Scanning a reference before rebuilding it

Used in phases 2 and 4, on **every** image the user supplies — screenshots sent in chat, images
pulled out of a `.docx`, `.pdf` or slide deck, video keyframes, anything.

The rule this file exists to enforce: **measure the image, then build. Never build from an
impression of the image.**

That sounds obvious and is routinely skipped, because a reconstruction built from an impression
looks finished. It has the right boxes in roughly the right places with roughly the right
colours, and nothing about it appears broken — so it survives review, and the person who knows
the product is the one who notices. By then the scene has been copied into other pages.

## 1. Get the images out first

A brief in a `.docx` or PDF carries its screenshots as embedded files. Extract them before
reading the prose, and put them somewhere stable:

```bash
mkdir -p input/references/images
cd input/references/images && unzip -o ../docs/brief.docx 'word/media/*' && mv word/media/* . 
```

Then **count them, and keep counting them**. Eleven screenshots supplied and three used is a
defect, not a style choice (`validation.md`, "did every supplied reference reach the page?").
Name each file for what it shows, not `image7.png` — the name is what makes a gap visible later.

If the user sends an image in chat rather than in the document, treat it as authoritative over
anything with the same name already in the workspace. Product UIs change; a screenshot sent
today is newer than one extracted from a document written last month. Say so if they differ.

## 2. Read the image at full resolution

Open it. Actually look at it, at its native size, before any script runs. Write down:

- every panel, and what each one is for;
- every number, label and unit, verbatim;
- the state of every control (selected tab, checked box, sort arrow, disabled button);
- what is cut off at the edges — a reference is often a crop, and a faithful rebuild keeps the
  crop rather than inventing what lies beyond it.

This is the step that catches content a script never will: that the status card says
"2 /29" and not "2/29", that the pacing gauge reads 101% while the donut reads 68%, that the
subtitle under the title is a sentence and not a label.

## 3. Measure it

```bash
python3 scripts/scan_reference.py shot.png --regions
```

It reports, from the pixels:

| Output | What it is for |
|---|---|
| size and aspect | The size to author at (§4) |
| page background, with ranked alternatives | Everything else keys off this; if the bands look wrong, re-run with `--bg` |
| palette, most used first | The theme. Never pick a colour by eye |
| horizontal bands | The section rhythm: card edges and the gutters between them |
| vertical gutters per band | How many columns each band has, and where they split |
| region palette (`--regions`) | Which tint belongs to which card |

Across several screenshots of the same product, use `extract_palette.py` instead — a colour that
appears in several is the product's own; one that appears in a single shot may be that screen's
content. Then verify the theme you wrote:

```bash
python3 scripts/extract_palette.py input/references/images/*.png --check scenes.css
```

### What the numbers are worth

Two failures that measurement removes entirely, from a real build:

- A theme shipped `--product-accent:#4F63E7` under a comment reading *"Faithful to the tool
  screenshots"*. The product's accent was `#4B288F`, dominant in 10 of 11 shots; `#4F63E7`
  appeared in none. Every scene read as a generic SaaS app.
- A dashboard's section rhythm was estimated by eye. Scanning gave the real band edges —
  y=149, 157, 243, 253, 314, 323, 524, 532 — and the layout stopped drifting.

### Two traps in the measurement itself

- **Do not read the page background off the top edge.** A dashboard usually opens with a white
  header, so the top edge returns the header's white and every band boundary comes out inverted.
  Screenshots also often carry a white margin, so the side gutters lie too. `scan_reference.py`
  ranks candidates by coverage instead, and prints the runners-up so a wrong guess is visible.
- **A single pixel is not a colour.** Sampling one point lands on antialiasing and gives a value
  that appears nowhere in the design. Always take the dominant colours of a *region*.

## 4. Author at the reference's own size, and scale the whole thing

This is what keeps geometry honest. Build the scene at the reference's exact pixel size and
scale it as a single unit:

```css
.fit{width:100%;overflow:hidden}
.frame{width:1794px;height:877px;transform-origin:0 0}
```

```js
var s = fit.clientWidth / 1794;
frame.style.transform = "scale(" + s + ")";
fit.style.height = Math.round(877 * s) + "px";
new ResizeObserver(/* re-run the two lines above */).observe(fit);
```

Every padding, radius and font size is then written in the reference's own pixels, straight off
the measurements, and the proportions **cannot** drift. Sizing each element independently in
relative units is the alternative, and it compounds: each element is individually defensible and
the composition is wrong everywhere.

Trade-off worth stating: a scaled frame reflows nothing, so below roughly 0.7 scale the type
gets small. For a wide console in a narrow slot, author a genuinely compact variant
(`responsive.md`) rather than scaling further down.

### When the scene goes into a fixed slot: set the design width from the reference's aspect

The section above scales a whole frame to whatever width it is given. A scene dropped into a
marketing page's **feature slot** is the other case: the slot width is fixed (~517px here) and
you re-render the UI at a chosen *design width*, then `pu-fit` scales that down into the slot.
The lever that controls the scene's shape is therefore the **design width**, and picking it by
eye is what leaves a scene the wrong proportions.

Set it from the reference's own aspect. `scan_reference.py` prints the **trimmed content
aspect** — the number to match, not the raw image aspect, which includes whatever margin the
crop happened to capture:

```
content box (margin trimmed): 2784x750   aspect 3.712 ← match a fixed slot to THIS
```

The scene's rendered aspect is `design_width / natural_content_height`, so the width that
reproduces the reference is:

```
design_width = reference_aspect × natural_content_height
```

Measure `natural_content_height` from the built scene (set the stage to the design width,
`transform:none`, read `getBoundingClientRect().height`), then iterate: content that wraps
differently at the new width changes its own height, so re-measure after each change rather than
solving once.

**The legibility cap.** `pu-fit` scales the design width down to the slot, and that scale must
stay at or above the 0.8 floor in `responsive.md` or text drops below ~11px. So:

```
max_design_width = slot_width / 0.8        # ≈ 646 for a 517px slot
```

A reference wider than this floor allows — a 16-column console at 3.7:1 in a half-width slot —
simply cannot be reproduced at its true aspect without illegible text. Cap the width, accept the
squarer result, and **record the residual in the scene's `approximations`** ("rendered aspect
~2.0 vs the reference's 3.71; design width at the 646px legibility cap"). A stated deviation is
fidelity; a silent one is a defect.

**Density is per scene, not one global knob.** When a table scene comes out too *tall* for its
reference, tighten its row padding and line-height — but scope those rules to that scene
(`[data-scene="..."] .pu-tbl td { … }`). A blanket density rule that also hits the scenes which
were already correct, or too *wide*, makes them worse. Verified: on one page a global tighten
fixed three scenes and pushed two others from +21% to +42% aspect error.

## 5. Animate what the product actually does

Animate the things that move in the real product, and nothing else:

- values counting to their settled figure,
- charts drawing along their own path,
- a donut sweeping to its share, a gauge needle swinging to its reading,
- anything the product itself updates live — a countdown, a realtime counter, a pulsing status
  dot.

Keep it dependency-free. `examples/sale-day-command-center.html` is a dense dashboard rebuilt this
way: 28 KB of HTML, CSS and plain JavaScript, no libraries and no images.

**Replay.** A scene that plays once is missed by anyone who arrives after it finished. Play on
view, hold the final state long enough to read (about 5s), then reset and replay. Replay the
*data* only — re-running the cards' entrance every cycle reads as a glitch. Stop the loop when
the scene scrolls off-screen or the tab is hidden, and resume on return; a loop running for
nobody burns battery and drifts out of step with any live counter. Honour
`prefers-reduced-motion` by rendering the settled state and never looping.

## 6. Verify what rendered, not what is in the DOM

The last trap, and it caught this skill's own test harness.

Reading back an animated value gives the **target**, not what is on screen: `getAttribute` and
`element.style` both return what you set, so a chart that never actually animated reports as
correct. Read the rendered value:

```js
getComputedStyle(ring).strokeDasharray   // animating value
ring.getAttribute("stroke-dasharray")    // the target you assigned — proves nothing
```

The same applies when replaying. Setting `transition:none`, assigning the reset value and
re-attaching the transition in the same tick lets the browser coalesce all three into one style
recalculation: the zero state is never painted and the chart simply stays where it was, while
the counters — which are driven by JavaScript, not CSS transitions — replay correctly. Force the
reset to commit by reading a computed style from each animated element before re-attaching:

```js
[ring, needle].concat(paths).forEach(function(el){ void getComputedStyle(el).opacity; });
```

A checklist for the end, all of which have been wrong in a build that looked right:

1. `extract_palette.py --check` exits 0.
2. Every settled figure equals the reference exactly.
3. The scene's rendered aspect is within a few percent of the reference's trimmed content
   aspect, or the residual is recorded in `approximations` (§4, fixed-slot case). A scene the
   wrong shape reads as wrong before anyone reads a single value in it.
4. Nothing is left stranded at `opacity: 0` with JavaScript disabled.
5. On replay, each animated element visibly returns to its start — measured with
   `getComputedStyle`, not `getAttribute`.
6. A selector written for one element has not caught its siblings. `.donut svg { transform:
   rotate(-90deg) }` was meant for the ring and silently rotated the emoji inside it too; scope
   to a class.
