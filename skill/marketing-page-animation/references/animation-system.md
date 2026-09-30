# Animation system

Used in phase 10 (and referenced from phases 5, 7 and 14). Goal: replay the interaction observed in a feature video as a restrained, meaningful sequence, driven by one small shared player, with a solid reduced-motion path.

The system is **not** a collection of entrance animations. It exists to make a product interaction legible: something is asked, the product works, an answer arrives, a decision is made. Motion is used only where it explains that story.

## 1. Principles

1. **Reproduce, don't decorate.** The sequence comes from the video record (`video-analysis.md`). If the video shows it, animate it. If it doesn't, don't add it.
2. **Motion has a cause.** Every movement is either a user action or a product response, or it is a deliberate emphasis of a result. Nothing moves "for life".
3. **Interaction over decoration.** Product interaction motion comes first. Generic motion is the mechanics underneath it. Decorative motion is not part of scenes.
4. **Most things stay still.** Chrome, labels, frames and unchanging content are present from the start. Only elements whose change carries the claim move.
5. **One thing at a time.** One primary motion at a time, with a secondary one allowed to overlap when the video shows it overlapping.
6. **Final state first.** Every scene ends in, and is authored in, its complete final state. Animation is layered on top and can always be skipped.
7. **Restraint is a feature.** If removing a movement does not change what the visitor understands, remove it.

## 2. Two levels

```text
Product interaction motion   meaning     "the user types a question", "the answer streams in"
        │  expands into
        ▼
Generic motion               mechanics   fade, slide, type, count, highlight ...
        │  runs on
        ▼
The player                   timing, state, performance, reduced motion
```

- **Level 1, generic motion:** small, reusable mechanics with no product meaning.
- **Level 2, product interaction motion:** named, meaningful recipes that combine generic motion in the order and timing real products behave. A scene's timeline uses these wherever an observation matches one.

**Choosing what to use for a step** (in order):

1. What the video actually shows, with its observed timing and order.
2. The matching product interaction recipe, with the video's timing overriding the defaults.
3. A generic motion step, when no recipe fits.
4. Nothing, when the change carries no meaning.

## 3. Step format (recap)

Timelines use the step format from `ui-scene-system.md`: `id`, `at` or `after`/`with` plus `delay`, `do` (a verb from this document, or `enter-state`), `target`, `source`, verb settings, `essential`, `basis`. Relative timing is preferred. Times are in milliseconds.

## 4. Level 1: generic motion

### Motion tokens

Use named tokens so timing stays consistent and easy to tune.

| Duration token | Value | Use |
|---|---|---|
| `instant` | 0 to 100 ms | Reduced motion, state flips, press release |
| `fast` | 150 ms | Small changes, hover, hide |
| `base` | 250 ms | Most reveals and slides |
| `slow` | 400 ms | Larger areas, expand and collapse, checks |
| `deliberate` | 600 to 900 ms | Counting, drawing, cursor travel |

| Easing token | Curve | Use |
|---|---|---|
| `out` | `cubic-bezier(0.2, 0, 0, 1)` | Things arriving (default for reveals) |
| `in` | `cubic-bezier(0.4, 0, 1, 1)` | Things leaving |
| `in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | Things moving between two places |
| `linear` | linear | Typing, streaming, spinners, progress |

These tokens describe the **product's** feel inside a scene. Use them unless the video clearly shows a different feel. The site kit's motion tokens, if any, apply to the scene frame and page, not the product UI.

### Effects (used by `reveal` and `hide`)

| Effect | What it does | Defaults |
|---|---|---|
| `fade` | Opacity only | `base`, `out` |
| `fade-up` | Opacity plus a small rise (8 to 12 design px) | `base`, `out` |
| `slide` | Opacity plus movement from a direction (16 to 24 design px, `from: start | end | top | bottom`) | `base`, `out` |
| `scale` | Opacity plus scale from 0.96 to 1 | `base`, `out` |

Pick one effect per scene for ordinary reveals (usually `fade-up`) so it feels consistent. Use another only when the video shows it.

### Verbs

| Verb | Purpose | Key settings | Default |
|---|---|---|---|
| `reveal` | Show an element | `effect`, `duration` | `fade-up`, `base` |
| `hide` | Remove an element | `effect`, `duration` | `fade`, `fast`, `in` |
| `stagger` | Modifier: apply the step to several siblings one after another | `each`, `max`, `order` | see section 6 |
| `count` | Animate a number from one value to another | `from`, `to`, `duration`, `format` | `deliberate`, `out` |
| `type` | Add text a character at a time | `source`, `cps` or `duration`, `caret` | 20 to 33 characters per second |
| `stream` | Add text progressively by word or chunk | `source`, `unit`, `duration` | 30 to 60 ms per word |
| `draw` | Draw a line, bar, arc or check | `duration` | `deliberate`, `out` |
| `highlight` | Briefly emphasize an element (ring, background, pulse) | `style`, `duration`, `times` | `slow`, once |
| `expand` | Open a region to its full size | `duration` | `slow`, `out` |
| `collapse` | Close a region | `duration` | `base`, `in-out` |
| `press` | Pressed feedback on a control | `duration` | `instant` in, `fast` out |
| `move` | Move an element or pointer along a path | `to`, `duration`, `easing` | `deliberate`, `in-out` |
| `zoom` | Camera moves in on one element (zoom in) | `to`, `scale`, `duration` | `1.5`, `deliberate`, `in-out` |
| `zoom-out` | Camera returns to the full view | `duration` | `deliberate`, `in-out` |
| `wait` | Hold | `duration` | as needed |
| `loop` | Reset and repeat | `delay`, `count` | see section 8 |

Notes:

- `reveal` and `hide` animate opacity and transform only. Layout space is reserved in advance, so nothing shifts.
- `type` and `stream` add text to a container whose final size is already reserved (see section 9).
- `count` reads the final value from the content and formats it for the locale.
- `highlight` is emphasis. Use it once per result, on the thing the story is about.

### Camera: zoom in and zoom out

Scenes are often shown small (a 515 px wide slot on a marketing page), so text inside them is hard to read. The `zoom` verb is a virtual camera that moves in on the part of the scene where the story is happening and returns to the full view afterwards. It is the main way a scene stays readable at slot size, and it directs the eye.

```json
{ "id": "z1", "with": "a4", "do": "zoom", "to": "ans", "scale": 1.5, "duration": 800 }
{ "id": "z2", "after": "a9b", "delay": 1200, "do": "zoom-out", "duration": 900 }
```

When zoom makes sense:

- A result or preview appears in a part of the scene that is small at slot size (a preview card, a modal). Zoom in as it arrives.
- Text is typed into a field that would be unreadable at full view. Zoom in while it types.
- A result is the point of the scene. Zoom in for a reading pause, then out.

When it does not:

- The target fills most of the scene (a full-width card or chat answer), the scene is already readable, or the action spans the whole scene (the cursor crosses from one side to the other). Nothing to frame, so do not zoom.
- Two zooms would fire back to back. Zoom out first, or go straight from one target to the next.
- Purely decorative emphasis. Zoom has a cause, like every other motion (section 1).

Rules:

1. **Always finish zoomed out.** Every `zoom` is followed by a `zoom-out` before the scene's last step, so the loop, replay and final state all start from the full view. The player resets the camera when the scene finishes, so a missing zoom-out makes the end jump.
2. **The camera frames the target; it never crops it.** `scale` is a ceiling. The player zooms to the largest scale at which the whole target (plus a small margin) stays in view, up to `scale`. If the target is already large (fills most of the scene, like a full-width card), the gain would be under 1.25x, so the camera does not move. A zoom that cuts off part of what it is zooming to is a bug.
3. **Keep the action inside the frame.** While zoomed in, everything that happens (typing, the cursor, a result) must be inside the framed area. If the next step happens elsewhere, zoom out first. Never move the cursor out of view.
4. **Scale 1.3 to 1.8.** Above about 1.8 the image gets soft and the viewer loses context. Default 1.5. The zoom never shows outside the scene: the camera stops at the scene's edges.
5. **Target a component**, by id, the same way cursor moves do. The camera centres it as far as the edges allow.
6. **Zoom while something happens.** Start it together with the step that shows the change (`with`), not after a pause. A zoom into a static picture reads as a glitch.
7. **`in-out` easing, 700 to 900 ms.** Slower than a reveal, because the whole scene moves. Never longer than about 1000 ms.
8. **Hold at least 1 second zoomed in** on anything the viewer must read, then zoom out. Do not zoom out while text is still streaming.
9. **At most two zoom-ins per scene**, so it feels like a guided tour and not a shaky camera.
10. The cursor is part of the scene, so it zooms with it and keeps its position.
11. Reduced motion: no zoom. The final state is the full view.

Static page images (photos, case-study thumbnails) are not scenes and do not use the camera. If a hover effect is wanted, use a CSS transition on `transform: scale(1.03)` inside an `overflow: hidden` frame, 400 ms `out`, and disable it with `prefers-reduced-motion`. Never zoom a page image on scroll.

## 5. Level 2: product interaction motion

Each recipe is a named sequence of generic steps, with defaults that the video's observed timing overrides. Use a recipe only when the video **shows** that interaction.

### Recipes

| Recipe | Meaning | What it expands to | Evidence to look for |
|---|---|---|---|
| `user-types` | A person enters text into an input | Focus ring on the input (`highlight`, `fast`), then `type` at the observed pace with caret. Optionally `press` on send, then the entered text moves into the thread as a message (`reveal`, `fade-up`) and the input clears | Text growing in an input over time, caret, a send action |
| `cursor-moves` | A pointer travels to a target | `reveal` cursor if hidden, then `move` to the target with `in-out` easing over `deliberate`, ending with the target's hover state | A visible pointer at two or more positions |
| `click` | A pointer presses a control | `press` on the target (`instant` in, `fast` out) with a small ripple at the pointer, then the control's result | Pressed state, ripple, or a response right after |
| `hover` | A pointer rests on something and it responds | Hover style on the target (`fast`), optionally a tooltip (`reveal`, `fast`) | Style or tooltip change under the pointer |
| `select` | An item is chosen | Selected style on the item (`fast`), others unchanged | Highlighted or checked row, tab, or option |
| `switch-tab` | The visible view changes | Active tab indicator `move` (`base`), content `fade` (`fast` out, `base` in) | A tab bar with a new active tab and new content |
| `scroll` | A region scrolls | `move` of the content within its region (`slow`, `in-out`) | Content offset changing |
| `system-processes` | The product is working | Show a loading state (`reveal`, `fast`), keep it animating while active, then `hide` it and continue. Optionally update a status label | Spinner, dots, skeleton, progress, "thinking" text, or a pause with a visible cue |
| `response-streams` | An answer arrives progressively | `stream` the text by word at the observed pace, then let dependent elements follow | Text appearing progressively |
| `notification-arrives` | An event is announced | `reveal` with `slide` from the observed edge (`base`, `out`), hold, then `hide` if the video shows it leaving. A badge count changes by `count` if shown | A toast, banner or badge appearing |
| `recommendation-appears` | The product proposes something | `reveal` the card (`fade-up`, `base`), then its parts (rationale, change, actions) with `stagger` (short), then one `highlight` on the key result | A suggestion card appearing, usually after an answer |
| `approval-clicked` | A person approves a proposal | `cursor-moves` to the approve control, `hover`, `click`, then the control shows its confirmed or busy state, alternatives disable, and `success-state` follows | A pointer on an approve or confirm control, a state change after |
| `success-state` | The result of a completed action | `reveal` the confirmation (`scale` or `fade`, `base`), `draw` a check (`slow`), then one `highlight` on the outcome. No confetti | A confirmation, check, or changed status |
| `data-updates` | Numbers, charts or tables change | `count` for numbers, `draw` or grow for chart marks (`deliberate`), a brief `highlight` on changed table cells, and any trend indicator flips. Unchanged data stays still | Values or marks that differ between frames |

### Recipe rules

- **Evidence first.** A recipe appears in the timeline only if the video record shows the interaction. Do not add `hover`, `notification-arrives` or `success-state` because they would look nice.
- **Observed timing wins.** The defaults apply only to values marked `assumed`.
- **Recipes are readable.** In the timeline, write the recipe name (`user-types`) rather than its expansion. The player expands it. Reviewers can then read the story.
- **Parameters are content, not text.** Recipes refer to content keys (`source: "q1"`) and component ids.
- **Recipes may be overridden.** A scene can replace any expanded step (for example, a different reveal effect) when the video differs.
- **New recipes** are added only after a second scene needs the same sequence. Record the meaning, the expansion, the evidence to look for, and the reduced-motion behavior.

### What each recipe does in reduced motion

Every recipe ends in its result. With reduced motion, the result is applied instantly and the movement is skipped. Recipes that carry meaning (`approval-clicked`, `success-state`, `data-updates`) can still show their result as a state change, and their steps are marked `essential` (see section 10).

## 6. Rules

### Duration

- Use the tokens in section 4. Scale duration with distance and size: small changes fast, large changes slow.
- Motion should be **just long enough to be understood**. Entrances 150 to 300 ms, exits 100 to 200 ms, large regions up to 400 ms, counting and drawing up to about 900 ms.
- Typing: 20 to 33 characters per second with about 30 percent random variation, so it feels human. Streaming: 30 to 60 milliseconds per word. Faster for long answers, and never so fast the text cannot be read as it arrives.
- **Observed durations are ceilings.** Compress real-time waiting, but do not slow the product down.
- No single movement longer than about 900 ms, except cursor travel across a large scene, which may reach 1000 ms.

### Easing

- Arriving: `out`. Leaving: `in`. Moving between two places: `in-out`. Typing, streaming, spinners and progress: `linear`.
- One easing family per scene. Do not mix bouncy or elastic curves with the standard ones. No bounce, overshoot or spring unless the video shows it.
- If the video's easing cannot be judged, use the default and mark it `assumed`.

### Delays

- **Causal delay.** A system response starts 200 to 400 ms after the user action that caused it, or the observed latency if it is shorter. This gap tells the viewer "the product responded".
- **Between beats:** 400 to 800 ms.
- **Reading pause:** after an important result appears, hold 800 to 1500 ms so it can be read. Longer text earns a longer pause, up to about 2 seconds.
- **Start delay:** begin 300 to 500 ms after the scene becomes visible.
- **Loading delay:** show a loading state for at least 600 ms so it registers, and no longer than about 1.5 seconds unless the wait is itself the point.
- Do not add delays for rhythm. Every pause must be a reading pause or a causal gap.

### Staggering

- Use `stagger` only for **siblings of the same kind that appear together** (rows of a table, cards in a list, parts of a recommendation).
- Interval 40 to 80 ms between items. Total stagger no more than about 400 ms, so no more than 6 to 8 items. Beyond that, reveal the group together.
- One level of staggering at a time. Do not stagger the children of staggered items.
- Follow reading order.
- Do not stagger text that is typed or streamed, and do not stagger unrelated elements.
- If the video shows the items appearing together, they appear together.

### Scroll-triggered animation

- **Start when visible.** Begin when about half of the scene is in the viewport (IntersectionObserver with a threshold). If the scene is already visible on load, such as a hero, start after the start delay.
- **Play once by default.** A scene plays through when first seen. It replays only via the replay control, or by its loop rule.
- **Pause when off screen** and resume from where it stopped when it returns.
- **Looping and controls are a page-owner decision, and a recorded one.** By default a scene
  plays once and offers play/pause/replay, and a looping scene pauses on hover so a reader can
  study it. A page owner may instead ask for an uninterrupted loop with no controls
  (`data-loop="infinite" data-loop-gap="5000" data-no-hover-pause data-no-controls`). Implement it
  when asked, and then **write it into `reports/validation.md` and the handoff README as a
  deliberate WCAG 2.2.2 exception**: motion lasting more than five seconds with no mechanism to
  pause it. Never make that trade silently, and never apply it by default. Everything else still
  holds — reduced motion shows the final state, keyboard access is unchanged, and the scene still
  suspends off-screen and in a hidden tab, which is cost economy rather than a user control.

- **No scroll-linked scrubbing** and no scroll hijacking by default. The visitor's scrolling must never be slowed or steered.
- **One scene at a time.** If several scenes are visible, only the one most in view plays. Others wait.
- **Section by section, once.** As the visitor scrolls, each page section reveals in turn and then its image starts animating while the visitor is looking at it. A block that starts below the fold fades up (28 px, 600 ms, `out`) the first time it comes into view and is then released, so it never repeats. Blocks already visible on load are never hidden, so the first screen is complete.

  **Which reveal mechanism to use depends on where the markup lands** (verified against the repo, 2026-09-29):

  | Destination | Mechanism |
  |---|---|
  | **Preview** (`preview/`) | The player's own `data-reveal` (+ `data-reveal-delay="160"` on the image half). The site's GSAP is not loaded there, so the player must do it |
  | **Handoff bundle** (`handoff/`) | The **site's own convention**: `data-scroll="slide-left"` on the text half, `data-scroll="slide-right"` on the image half (alternating per row), plus `data-scroll-duration="0.7"` and `data-scroll-trigger=".feature-row"`. Driven by GSAP + ScrollTrigger, already loaded site-wide |

  Never ship both on the same element — a section marked with `data-reveal` *and* `data-scroll` animates twice. This is the one place where "one markup, two homes" (rule 5) needs a documented per-home difference; record it in the handoff README.
- **The scene waits for its block.** A scene inside a block that has not revealed yet stays paused, and starts about 350 ms after the block begins to reveal, so the visitor sees the image arrive and then move.
- **Once means once.** Reveals do not repeat when scrolling back up or down. A finished scene stays in its final state. If the visitor scrolls away mid-scene, it pauses and continues from that point when it returns; it does not restart. Only the replay control replays.
- **Reduced motion:** no reveal, everything is visible, scenes show their final state.
- **Only page sections, not every element.** Do not fade in individual paragraphs, buttons or icons; one reveal per section half.
- **Small screens.** Start conditions and thresholds adapt so a tall scene still starts.

### Looping

- Loop only when repetition helps the story: a short demonstration that a visitor may watch again. Otherwise play once and hold the final state.
- After the final state, **hold 2 to 4 seconds**, then reset. Reset with a quick fade (about 200 ms) back to the initial state, not a rewind.
- Stop after a few cycles (about 3), then rest on the final state. Never loop indefinitely on a page the visitor is reading.
- Pause on hover and on keyboard focus within the scene.
- Provide play, pause and replay controls for any scene that runs longer than about 5 seconds or loops, operable by keyboard.
- Never loop decorative motion. A pulsing badge that is not in the video does not exist.
- No looping with reduced motion.

### Smoothness

Motion should feel like a single continuous gesture, not a series of jumps.

- **Compositor only.** Animate `transform` and `opacity` only, and promote the moving layer (`will-change: transform`) for the duration of the move, then release it. The player does this for reveals and zooms.
- **Time, not frames.** Every position is a function of elapsed time, not of a frame count, so a slow device drops frames but never slows the story. The player clamps a stalled frame to 100 ms so a tab switch does not fast-forward.
- **Ease everything that has a start and an end.** Only typing, streaming, spinners and progress are `linear`. Cursor travel and zooms use `in-out`. Reveals use `out`. Never a hard start or stop.
- **Overlap, do not queue.** The next beat starts while the previous one settles (`with` plus a short delay), so nothing waits for a full stop. Use `after` only for a real causal gap.
- **One camera move at a time**, and no other large transform on the same layer.
- **No flash of the final state.** Text that types or streams starts empty the moment its element becomes visible (never full text for a few frames before the animation begins), and with JavaScript on, a scene's stage stays hidden until the player has set its first frame. Load the player early (in the head or before the first scene) so this holds; without JavaScript the final state is simply visible.
- **Whole pixels at rest.** Scaled layers should end at scale 1 with the transform removed, so text is crisp when idle. The player clears the inline transform when a step finishes.
- **Scale the stage, not the layout.** A scene fitted into a slot is scaled by one transform on the stage (`pu-fit`), with the camera layer inside it. They compose: fit first, zoom on top.
- **Check on a throttled CPU** (4x slowdown). If it stutters, remove motion, not quality.

### Performance

- Animate **`opacity` and `transform` only.** Never animate `width`, `height`, `top`, `left`, margins, `box-shadow` size, or filters such as blur.
- **Reserve layout.** The final size of every element is in place before it appears, so nothing shifts. Typed and streamed text is laid out at its final size with unrevealed characters hidden, not by growing a box.
- Prefer CSS transitions or the Web Animations API for individual effects, with one scheduling clock in the player. Avoid many independent timers.
- **Limit concurrency.** No more than about six elements moving at once.
- Use `will-change` only during an animation and remove it afterwards.
- Charts draw with stroke properties or transforms, not by rebuilding the DOM each frame.
- Numeric counting updates at most once per frame, and text nodes only.
- No layout reads inside animation frames.
- Pause and release everything when the scene is off screen or the tab is hidden.
- Check on a low-powered device and a throttled CPU. If it stutters, remove motion, not quality.

### Reduced motion

`prefers-reduced-motion: reduce` must be honored, in CSS and in the player, and it must be respected live if the setting changes.

- **Do not run the timeline.** Render the **final state** immediately.
- No looping, no cursor movement, no pulsing, no streaming or typing.
- **Essential steps** (`essential: true`) still apply their result, as an instant change or a cross-fade of 100 ms or less, but only where the story needs the change to be seen.
- **Step through option.** If the scene is a sequence whose order matters (question, answer, approval), provide labelled Previous and Next controls so the visitor can move through the states without motion.
- Emphasis that is not movement (a color change) is fine, instant.
- Nothing may flash more than three times per second, in any mode.
- Keep the scene's text description available.

## 7. Reproducing a video sequence

The animation is derived from the video record, not authored from scratch.

1. **Start from the record.** Take `animation_sequence` and the observation timeline from `analysis/videos/<id>.yaml` (see `video-analysis.md`).
2. **Match each observation** to a product interaction recipe. Use a generic step only where no recipe fits, and skip anything that carries no meaning.
3. **Keep order, causality and overlap.** Preserve which events caused which, and the overlaps that mattered (a chart drawing while text streams).
4. **Use relative timing** (`after`, `with`, `delay`) so each step hangs from the step that causes it.
5. **Apply observed timing.** Use the video's durations and paces. Fill only `assumed` values from the defaults in section 6.
6. **Compress dead time** and slow real waits. Record each compression and keep every reading pause.
7. **Remove decoration.** Strip any movement the video did not show and that does not carry the story.
8. **Check the motion budget** (below).
9. **Carry the basis** (`observed`, `inferred`, `assumed`) onto each step so reviewers can see what is fact and what is choice.
10. **Compare** the rebuilt sequence to the reference keyframes at the recorded times.

### Motion budget

- No more than one primary motion at a time, plus one secondary that the video shows overlapping.
- Only components whose change carries the claim move. If every element in the scene moves, something is wrong.
- Chrome (header, sidebar, frames, labels) never animates in. It is there in the initial state.
- A scene should run under about 15 seconds per loop. If it is longer, split it into beats or scenes.
- For each moving element ask: does this movement exist in the video, and would the visitor miss it if it were gone? If both answers are no, remove it.

### Example

For a scene where a user asks a question, the product works, answers with a metric and a recommendation, and the user approves it:

```json
[
  { "id": "s1", "at": 400, "do": "user-types", "target": "composer", "source": "q1", "cps": 26, "basis": "observed" },
  { "id": "s2", "after": "s1", "delay": 300, "do": "system-processes", "target": "load", "duration": 1000, "basis": "observed" },
  { "id": "s3", "after": "s2", "do": "response-streams", "target": "a1", "unit": "word", "basis": "observed" },
  { "id": "s4", "with": "s3", "delay": 900, "do": "data-updates", "target": "m1", "basis": "observed" },
  { "id": "s5", "after": "s3", "delay": 400, "do": "recommendation-appears", "target": "rec", "basis": "observed" },
  { "id": "s6", "after": "s5", "delay": 800, "do": "approval-clicked", "target": "appr", "essential": true, "basis": "observed" },
  { "id": "s7", "after": "s6", "do": "success-state", "target": "ok", "essential": true, "basis": "observed" },
  { "id": "s8", "after": "s7", "delay": 3000, "do": "loop", "count": 3 }
]
```

Eight steps tell the story. Compare this with a generic approach that fades every card, row and label in on scroll: it would move dozens of elements, none of them with a cause.

## 8. Playback behavior

- **Controls.** Play, pause and replay for scenes over about five seconds or that loop. Keyboard operable and labelled.
- **Speed.** The player accepts a speed factor so timelines can be reviewed slowly.
- **Seek.** The player can seek to a step or state, so validation can capture keyframes.
- **Cleanup.** Timers and observers are released when a scene is removed or hidden.
- **Missing targets** never throw. They log a warning in development.

## 9. Runtime contract (implemented in `runtime/scene-player.js`)

The scene player must:

- Read a scene's timeline from JSON in an asset file or a data attribute, and resolve `at`, `after`, `with` and `delay` into absolute times.
- Expand product interaction recipes into generic steps, using the observed values first and the defaults second.
- Rewind the final-state markup to the initial state on load, then play. Without JavaScript, the final state is what shows.
- Read typed, streamed and counted text from the rendered elements, so every language animates correctly, and compute durations from text length.
- Provide a single clock, `play()`, `pause()`, `replay()`, `seek(ms)`, and a speed factor.
- Apply the start, loop and reduced-motion rules in section 6.
- Provide the camera layer when the timeline contains `zoom`: wrap the stage content in `.pu-cam`, animate one `transform` on it, and reset it to identity when the scene finishes, resets or is in reduced motion.
- Fit scenes into their page slot (`pu-fit`), scaling the stage only.
- Contain no inline scripts and no dependencies.

## 10. Accessibility of motion

- Do not rely on animation alone to convey information. The final state and the scene description carry it.
- Hide animating internals from assistive technology (`aria-hidden`), and expose the description and the final text instead. Screen readers must not announce each typed character or streamed word.
- Provide play, pause and replay controls, and step-through controls with reduced motion.
- No content flashes more than three times per second.
- The cursor is decorative and never focusable.
- `essential` marks steps whose result must still be visible with reduced motion.

## 11. Adding to the system

- **New generic verb:** only when a recipe truly needs a mechanic that does not exist. Add it once, with defaults, properties animated, and reduced-motion behavior.
- **New recipe:** only after a second scene needs it. Record meaning, expansion, evidence and reduced-motion behavior in section 5.
- **Never** add one-off animation code inside a scene.

## 12. Checklist

- Each step traces to something the video shows, or is labelled `assumed`.
- Product interaction recipes are used wherever an observation matches one.
- Only elements that carry the claim move. Chrome does not animate in.
- Durations, easing and delays use the tokens and rules above.
- Staggering is limited to same-kind siblings, short and capped.
- The scene starts when visible, plays once or loops with a hold and a stop, and has controls.
- Only `opacity` and `transform` are animated, and layout is reserved.
- Reduced motion shows the final state, and `essential` steps are marked.
- The sequence ends in the final state and is under about 15 seconds.
- Zoom is used where the scene is small or dense, zooms in only while something happens, and always ends zoomed out.
- Motion is smooth: eased, overlapping, transform and opacity only.
- Compressions and assumptions are recorded.

## 13. Common mistakes

- Fading in every element as it scrolls into view.
- Adding motion the video never showed.
- Copying real waiting time, so the scene feels slow.
- Staggering unrelated elements or long lists.
- Looping forever, or with no way to pause.
- Animating layout properties, causing jank and shift.
- Typing by growing a box instead of revealing reserved text.
- Bounce or spring easing that the product does not have.
- Announcing animation to screen readers.
- Ignoring reduced motion, or making it look broken instead of complete.
- Zooming into a static picture, zooming past 1.8, or leaving the scene zoomed in at the end.
- Chained camera moves that make the scene feel shaky.
