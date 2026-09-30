# Runtime: the scene player

`scene-player.js` (about 900 lines, no dependencies, no inline scripts, no strings of its own) plus `scene-player.css` (mechanics only: hidden state, cursor, ring, loading dots, control visibility). It plays a scene's declarative timeline over markup that is authored in its **final state**. Status: implemented and tested (`demo/test_player.py`, headless Chromium, 24 checks).

In the handoff bundle the two files go to the site's asset folder, and the dev team loads them the way the site loads other component scripts (unverified until the repo is inspected; see `references/hugo-bookshop-target.md`).

## Markup contract

```html
<figure class="product-ui" data-scene="scene-id" data-final-state="approved"
        data-trigger="view"  data-loop="3"  data-speed="1"
        data-scene-config='{"states":[...],"timeline":[...]}'>   <!-- or data-scene-src="timeline.json" -->
  <div aria-hidden="true">                                      <!-- animating internals are hidden from assistive tech -->
    <div data-target="q1"> <p data-text data-content="q1">...</p> </div>
    <div data-target="load" data-hidden>...</div>               <!-- data-hidden = not visible in the FINAL state -->
    <span data-count-to="1240" data-count-from="0">1,240</span> <!-- rendered, localized final text -->
    <path data-draw d="..."/>                                   <!-- SVG stroke draw, or scaleX/scaleY for bars with data-draw="x|y" -->
    <div data-target="composer"><span data-input>placeholder</span> <button data-target="composer.send">..</button></div>
    <span class="pu-cursor" data-target="cur" data-hidden>...</span>
  </div>
  <figcaption class="pu-sr-only">Scene description</figcaption>
  <button data-action="toggle|play|pause|replay|next|prev">label rendered by the template</button>
</figure>
```

Hooks: `data-target` (component id; dotted ids like `appr.confirm` are sub-parts), `data-text` (text element for type/stream), `data-input` (input text), `data-content` (rendered source text for `type`/`stream`), `data-count-to|from|format|decimals|sign`, `data-draw`, `data-key` (element to highlight), `data-changed` (highlight after a data update), `data-alt` (alternatives disabled on approval), `data-action` (controls; labels come from the template, never from the player).

Rules the player relies on:

- **Final state first.** The markup shows the finished UI. With no JavaScript or with `prefers-reduced-motion`, that is what the visitor sees. The player warns in the console if the authored `data-hidden` set disagrees with the `final` state.
- **Layout is reserved.** Hidden components keep their space (`visibility: hidden`), and typed or streamed text is laid out at full size with unrevealed characters hidden. Design the final state knowing that the space of a component that disappears at the end stays.
- **Text is read from the DOM.** Typing and streaming durations come from the rendered text, so every language animates at a natural pace. Text is split with `Intl.Segmenter`.
- **Only `opacity` and `transform`** are animated (plus SVG stroke offset for `draw`). The player tracks everything it touches and restores the authored markup exactly when it finishes.
- **Visibility of a component** in a state: it, or any descendant, is listed in `visible`. A component listed nowhere (the cursor) appears only through timeline steps.

Slot fitting and camera:
- `figure.pu-fit[data-fit-from][data-fit-width][data-fit-height]` scales the `.pu-stage` down (never up) to its slot at viewports at or above `data-fit-from`. Controls and caption stay full size. `ProductScenes.fit()` re-measures.
- `zoom` and `zoom-out` steps move a camera layer (`.pu-cam`, created automatically) that wraps the stage content. The camera frames the target (never crops it) and does nothing when the target already fills the scene. Reset to full view when the scene finishes or resets.
- `data-speed` (default 1) multiplies the timeline clock.
- The player adds `pu-js` to `<html>` as soon as it runs and `pu-ready` to each scene after its first frame is set. With JavaScript, the stage stays hidden until `pu-ready`. **Load the player early** (in the head, or before the first scene) so the finished scene never flashes before it starts.
- `[data-reveal]` blocks below the fold fade up once when first scrolled into view (`data-reveal-delay` in ms). A scene inside a pending block waits for it. `ProductScenes.reveal(scope)` re-scans. Nothing repeats.
- Typed and streamed text starts empty the moment its element becomes visible.

## Supported timeline steps

Generic: `enter-state`, `reveal`, `hide`, `type`, `stream`, `count`, `draw`, `highlight`, `press`, `move`, `cursor-moves`, `click`, `hover`, `select`, `wait`, `loop`, `zoom`, `zoom-out`.
Recipes: `user-types`, `system-processes`, `response-streams`, `data-updates`, `recommendation-appears`, `approval-clicked`, `success-state`, `notification-arrives`.
Not implemented yet (the step is skipped with a console warning): `switch-tab`, `scroll`.

Timing is resolved from `at`, `after`, `with`, `delay`. Both styles (generic verbs with `enter-state`, or recipes) can be mixed in one timeline. Recipes that reveal things do not hide anything afterwards, so add `hide` or `enter-state` steps to leave a state.

## Behavior

Starts when about half the scene is visible (less for tall scenes), one scene at a time (the most visible), pauses off screen and in a hidden tab, plays once by default, loops with a hold and stops after `count` cycles, pauses on hover and focus when looping, honors `prefers-reduced-motion` live (final state at once, previous and next controls step through states).

## API

`ProductScenes.init(scope)`, `ProductScenes.get(idOrElement)` returns a scene with `play()`, `pause()`, `replay()`, `seek(ms)`, `setSpeed(x)`, `goToState(id)`, `step(±1)`, plus `total` (ms). A `scene:complete` event bubbles from the root when a run finishes. `seek(ms)` is deterministic, which validation uses to capture keyframes.

## Demo and tests

`demo/build_demo.py` generates `demo/index.html` (two synthetic scenes: states plus verbs, and recipes). `demo/test_player.py [--shots DIR]` runs the headless checks. The demo content is invented.

## Fit quality

`pu-fit` scales a stage down to its slot, and sets `data-scaled` on the stage while it does.
Below a 0.8 scale, at viewports of 1280px and up, the player logs a console warning naming the
scene, the scale, the resulting text size and the width to recompose at — a scene that needs
more than a 20% reduction is too wide or too tall for its slot and should be rebuilt smaller,
not squeezed (`references/responsive.md`).

`text-rendering: geometricPrecision` is applied only while a stage is scaled. It keeps advance
widths proportional so text does not reflow between scales; it is not a legibility aid, since
it disables hinting and softens small glyphs. Unscaled stages use `optimizeLegibility`.
