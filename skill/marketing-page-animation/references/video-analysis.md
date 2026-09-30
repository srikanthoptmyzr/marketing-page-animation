# Video analysis

Used in phases 5 and 6. Goal: understand the interaction shown in a screen recording well enough to rebuild it as an animated HTML/CSS/JS scene. The video is an **input to understanding**, never an asset on the page. The pipeline is:

```
video  →  frames  →  observation timeline  →  scene spec  →  animation sequence  →  HTML/CSS/JS scene
```

This document defines the first three arrows. It does not implement any scene.

## Principles

1. **Observe, then infer, then assume, and label each.** Every fact in the record is `observed` (seen in a frame), `inferred` (deduced from frames), or `assumed` (a default chosen because the video does not show it). Never present an assumption as an observation.
2. **Uncertainty is information.** If something cannot be reliably identified, say so and say what would resolve it. Never fill the gap with detailed invented behavior.
3. **Cause and effect.** Every change on screen is explained by an action or a system process. Unexplained changes are flagged, not smoothed over.
4. **Video effects are not product behavior.** Recording tools add zoom, pan, cursor smoothing, click highlights, cuts and speed changes. Separate them from what the product does.
5. **Story over exactness.** The page needs the moments that carry the claim. Timing is reproduced closely where it matters and compressed where it does not.
6. **The video contains real data.** The first time a sensitive value is seen, register it as an entity in `.private/` and refer to it by entity id from then on. Records name the category, entity id and location, never the value (see `privacy-masking.md`). Frames stay in the work directory's `analysis/`, and check the frames near every state change for brief or hover-only values.
7. **Reuse the screenshot method.** Analyze keyframes with `screenshot-analysis.md`, and keep component ids consistent between the two.

## Step 0: Intake

Record: file, duration, frame rate (and whether it is variable), resolution and display scale, whether audio or captions exist, and what the video is meant to prove.

- Run a probe (`ffprobe`) for duration, fps and dimensions. If the tools are not available in the environment, ask the user for still frames of key moments instead. Do not pretend to have watched a video that could not be read.
- If the video is longer than about a minute, ask which segments matter, or plan to analyze scene by scene.
- Ignore audio for behavior. A voiceover may help name features, but may also contain names or account details: never copy it into the spec.

## Step 1: Extract frames

Video is analyzed through frames, not watched continuously. Use more than one sampling pass.

1. **Overview pass.** Sample at a low fixed rate (for example 1 frame per second) into a timestamped contact sheet. Timestamps are printed on each tile and kept in filenames.
2. **Change pass.** Use scene-change detection to find frames where the picture changes substantially, and record their timestamps.
3. **Dense pass.** Around every event that matters (a click, an appearance, a loading start or end), sample densely, from 10 frames per second up to the native frame rate, over a short window. This resolves what happened and when.
4. **Difference pass.** Compare consecutive frames to find the regions that changed. This shows which elements are responding, even when the change is subtle.

Example commands:

```bash
ffprobe -v error -show_entries stream=width,height,r_frame_rate,duration -of default=nw=1 input.mp4
ffmpeg -i input.mp4 -vf "fps=1,scale=640:-1,tile=4x3" -frames:v 1 contact.png            # overview sheet
ffmpeg -i input.mp4 -vf "select='gt(scene,0.03)',showinfo" -vsync vfr changes_%04d.png    # change frames
ffmpeg -ss 3.0 -t 1.5 -i input.mp4 -vf "fps=15" dense_%03d.png                            # dense window
```

Rules:

- Keep the timestamp of every frame you rely on. Timing comes from timestamps, not from counting frames, especially for variable frame rate.
- Frame sampling limits precision. Record a **tolerance** for every time (for example ±0.1 seconds) and tighten it only with dense sampling.
- Look closely at cropped regions of small things (cursor, spinners, badges, carets).

## Step 2: Scene boundaries

A **scene** is a continuous stretch in which one layout stays in place and one idea is demonstrated. Start a new scene when:

- The layout changes substantially (a new page, a new view, a modal replacing the content).
- There is a cut, a fade, or a jump in the recording.
- The user's goal changes (finished one task, began another).
- A long pause or idle stretch separates two demonstrations.

Do not split for ordinary changes inside one view (a message appearing, a panel expanding). Record for each scene: id, time range, purpose, the claim it supports, and confidence in the boundaries.

Prefer fewer, clearer scenes. A page scene should be short enough to loop comfortably (see `animation-system.md`). If a scene runs long, note natural **beats** inside it where it could be split.

## Step 3: UI components

For each scene, take the first stable keyframe, the last stable keyframe and a keyframe for each significant change, and analyze them with `screenshot-analysis.md`. Produce one component inventory for the scene:

- Give each component a stable id and a type from the shared vocabulary.
- Note which components **appear**, **disappear**, **change** or **stay** during the scene. That is the basis for the animation.
- Include components that are only visible for a moment (a tooltip, a toast, a menu).
- Do not invent components that were never on screen. If a menu was opened for one frame and its items are unreadable, record the menu and its unreadable contents as an uncertainty.

## Step 4: Events: user actions and system responses

Build an **event list** by walking through the dense-pass evidence in order. For each change on screen, decide what caused it.

- **User actions:** typing, clicking, hovering, scrolling, dragging, selecting, pressing a key, opening a menu, switching a tab.
- **System responses:** loading begins, content appears, text streams in, a value updates, a chart draws, a panel expands, a notification shows.
- **Pairs.** Match each response to its action and record the **latency** between them. A response with no visible cause is marked `cause: unknown`.
- **Order and overlap.** Note when events overlap (a chart drawing while text streams).
- **Real versus marketing time.** Note stretches where the recording waits for a slow real system (a long spinner). These are candidates for compression.

## Step 5: UI state changes

Turn the events into a **state machine** for the scene:

- Name each stable state (`initial`, `question-typed`, `loading`, `response-visible`, `chart-visible`, ...).
- For each state, list which components are visible and their key attributes.
- For each transition between states, record the trigger (an action or a response) and the time.
- Mark states and transitions as observed, inferred or assumed.

Only include states the video shows or clearly implies. If the product obviously has an error or empty state that the video does not show, do not build it. Note it as not shown.

## Step 6: Text and content changes

For every piece of text that changes, record:

- What changes: appears, disappears, is replaced, updates in place.
- **How:** typed by the user (character by character), streamed by the system (by character or by word), or shown all at once.
- Start and end time, and the pace (characters or words per second).
- The first and final text, when legible. If not legible, record the length and structure, and mark the content unreadable. Never invent the text.
- Whether the text is product chrome or data, its sensitivity class, and whether it should be translated (see `localization.md`).
- Numbers that count or update: start value, end value, and duration.

Text that is typed, streamed or counted becomes an animation later. Text that simply appears becomes a reveal.

## Step 7: Loading states

For each loading state record:

- The kind: spinner, skeleton, progress bar, pulsing dots, "thinking" text, blank wait.
- Where it appears and how it looks (size, color, motion).
- When it starts and ends, and what ends it.
- Whether it is real waiting time in the recording. If it is long, note the shorter duration the page should use, and say the compression is a choice.

If a loading indicator is visible only in blurred or partial frames, record it as inferred and say which details are unknown.

## Step 8: Cursor interactions

If a cursor is visible, record:

- Its path as **waypoints** with times: start position, each stop, and the target under it at each stop. Positions are relative to the scene (design pixels or fractions of the width).
- Whether the cursor moves smoothly, in a straight line, or in an arc. Recording tools often smooth or animate the cursor, so treat its exact path as approximate.
- **Clicks:** the moment, the target, and the evidence (pressed state, ripple, highlight, a response that follows).
- **Hovers:** what changes under the cursor (highlight, tooltip, pointer style).
- Scrolls, drags and text selection.
- The typing caret, and whether it blinks.

If there is no visible cursor, do not add one to the scene unless the story needs it, and say the cursor is assumed.

## Step 9: Transitions

For each visual change, record the type and direction (fade, slide, expand, collapse, scale, cross-fade, instant), an estimated duration, and whether it is a product behavior or a **video effect**.

Video effects to recognize and exclude from the product behavior:

- Zoom, pan or focus effects added by the recording tool.
- Cursor smoothing and click ripples added by the recorder.
- Cuts, jump cuts and fast-forward or slow-motion segments.
- Cropping and window resizing done in editing.
- Overlays, captions and annotations.

When an effect helps the story (a zoom onto the answer), it may be recreated as a deliberate scene effect, but record it as `editorial`, not product behavior.

If easing cannot be seen, use the defaults in `animation-system.md` and mark the value `assumed`.

## Step 10: Timing

- Convert every event to seconds from the start of the scene, with a tolerance.
- Record durations for typing, streaming, loading, transitions and pauses.
- Note **meaningful pauses**: places where the video lingers so the viewer can read. Keep them.
- Note **dead time**: idle or slow stretches to compress.
- Compute the scene's total and the proposed marketing duration. Aim for a scene under about 15 seconds per loop.

## Step 11: Final state

Identify the **final state**: the last stable frame in which everything the scene shows is on screen. It is:

- What visitors see with reduced motion or without JavaScript.
- The frame the scene holds before it loops.
- What the screenshot analysis should agree with, if a screenshot of the same moment exists. Reconcile any difference.

Record which components are visible and what their final text and values are.

## Step 12: The observation timeline

The result of steps 2 to 11 is a **timeline of observations**. Times are in seconds. Each entry says what happened, what it was, and how sure we are.

Entry fields:

| Field | Meaning |
|---|---|
| `t` | Time in seconds from scene start |
| `tol` | Tolerance in seconds |
| `kind` | `state`, `action`, `response`, `loading`, `cursor`, `text`, `transition` |
| `what` | Short plain description |
| `target` | Component id, when applicable |
| `basis` | `observed`, `inferred` or `assumed` |
| `evidence` | Frame timestamps or filenames that support it |
| `note` | Anything unclear |

## Step 13: The animation sequence

Convert the observation timeline into an **animation sequence** using the verbs in `animation-system.md`. Where an observation matches a product interaction recipe (`user-types`, `system-processes`, `response-streams`, `notification-arrives`, `recommendation-appears`, `approval-clicked`, `success-state`, `data-updates`), use the recipe. Use generic motion only when none fits. This is a separate list, in milliseconds, that the scene spec will carry.

| Observation | Animation verb |
|---|---|
| User types text | `type` |
| System streams text | `stream` |
| Element appears | `reveal` |
| Element disappears | `hide` |
| Cursor moves | `cursor-moves` |
| Click | `click` |
| Hover | `hover` |
| Tab or view changes | `switch-tab` |
| Item selected | `select` |
| Region scrolls | `scroll` |
| Attention cue (ring, glow) | `highlight` |
| Number counts | `count` |
| Chart or line draws | `draw` |
| Deliberate hold | `wait` |
| End, then repeat | `loop` |

Rules:

- Convert seconds to milliseconds. Preserve order and the overlaps that mattered.
- Compress dead time and slow loading. Keep meaningful pauses. Record every compression.
- Carry the `basis` over: an `assumed` step stays marked so reviewers can see it.
- Refer to elements by id, and to text by the rendered element, never by literal strings (see `localization.md`).
- Every sequence ends in the final state.
- If the sequence is long, split it into beats or scenes.

## The analysis record

Save one YAML record per video as `analysis/videos/<id>.yaml`. It is an internal document. In phase 7 it is merged with the screenshot records into `spec/scenes.json`.

```yaml
video:
  id: assistant-question-flow
  source: { file: input/references/videos/example.mp4, duration_s: 12.4, fps: 30, variable_fps: false, resolution: [1920, 1080], scale: 2 }
  purpose: "Shows a user asking a question and the assistant answering with a chart"
  extraction: { overview_fps: 1, change_frames: 14, dense_windows: [[1.0, 3.5], [3.6, 5.5]] }
  editorial_effects: [ { kind: zoom, at: [8.0, 9.0], note: "recorder zoom onto the answer" } ]

scenes:
  - id: assistant-answer                 # becomes the scene id
    range_s: [0.0, 10.2]
    claim: "Ask a question in plain language and get an answer with a chart"
    boundary_confidence: high
    beats: [ { id: ask, range_s: [0, 3.4] }, { id: answer, range_s: [3.8, 10.2] } ]

    components:                          # ids match the screenshot analysis
      - { id: composer, type: composer, appears: initial, changes: [typing] }
      - { id: q1, type: message, variant: user, appears: "3.4" }
      - { id: loading-dots, type: status, appears: "3.8", disappears: "5.2" }
      - { id: a1, type: message, variant: assistant, appears: "5.2" }
      - { id: sales-chart, type: chart, appears: "7.0" }
      - { id: recommendation, type: card, appears: "8.5" }

    states:
      - { id: initial,         at: 0.0, visible: [composer], basis: observed }
      - { id: question-typed,  at: 3.4, visible: [composer, q1], basis: observed }
      - { id: loading,         at: 3.8, visible: [q1, loading-dots], basis: observed }
      - { id: response,        at: 5.2, visible: [q1, a1], basis: observed }
      - { id: chart,           at: 7.0, visible: [q1, a1, sales-chart], basis: observed }
      - { id: recommendation,  at: 8.5, visible: [q1, a1, sales-chart, recommendation], basis: observed }

    timeline:                            # observation timeline, seconds
      - { t: 0.0, tol: 0.1, kind: state,      what: "Empty scene, composer focused", target: composer, basis: observed, evidence: [f_0000] }
      - { t: 1.2, tol: 0.1, kind: action,     what: "User starts typing", target: composer, basis: observed, evidence: [f_0036, f_0042] }
      - { t: 1.2, tol: 0.2, kind: text,       what: "Question typed at about 12 characters per second, ending at 3.4", target: composer, basis: observed }
      - { t: 3.4, tol: 0.1, kind: action,     what: "User presses send", target: send, basis: inferred, note: "click not visible; message moves up immediately" }
      - { t: 3.8, tol: 0.15, kind: loading,   what: "Three pulsing dots", target: loading-dots, basis: observed }
      - { t: 5.2, tol: 0.15, kind: response,  what: "Answer text appears, streaming by word", target: a1, basis: observed }
      - { t: 7.0, tol: 0.2, kind: response,   what: "Chart lines draw left to right", target: sales-chart, basis: observed }
      - { t: 8.5, tol: 0.2, kind: response,   what: "Recommendation card slides up", target: recommendation, basis: observed }

    cursor:
      visible: false
      basis: observed
      note: "No pointer in the recording; do not add one unless the story needs it"

    loading_states:
      - { id: loading-dots, kind: pulsing-dots, start: 3.8, end: 5.2, real_wait: true, proposed_duration_s: 1.0 }

    text_changes:
      - { target: composer, how: typed, start: 1.2, end: 3.4, legible: true, sensitivity: none }
      - { target: a1, how: streamed-by-word, start: 5.2, end: 6.8, legible: partly, sensitivity: amount, note: "numbers unreadable in two frames" }

    final_state: { visible: all, at: 10.2, hold_s: 3, matches_screenshot: assistant-answer-with-chart }

    animation_sequence:                  # milliseconds, verbs from animation-system.md
      - { at: 0,    do: wait,   duration: 400 }
      - { at: 400,  do: type,   target: composer, source: question, cps: 26, basis: observed }
      - { at: 2000, do: click,  target: send, basis: inferred }
      - { at: 2200, do: reveal, target: q1, effect: fade-up, duration: 250, basis: observed }
      - { at: 2500, do: reveal, target: loading-dots, duration: 150, basis: observed }
      - { at: 3500, do: hide,   target: loading-dots, duration: 150, basis: observed }
      - { at: 3500, do: stream, target: a1, unit: word, duration: 1600, basis: observed }
      - { at: 5000, do: draw,   target: sales-chart, duration: 900, basis: observed }
      - { at: 6300, do: reveal, target: recommendation, effect: fade-up, duration: 300, basis: observed }
      - { at: 9000, do: loop,   delay: 3000 }
    compressions: [ "Loading shortened from 1.4 s to 1.0 s; typing sped from 12 to 26 characters per second" ]

uncertainties:                           # see the next section
  - { id: u1, about: "Whether pressing Enter or clicking a button sends", level: inferred-low, plan: "Show the send button pressed; confirm" }
  - { id: u2, about: "Answer numbers", level: unreadable, plan: "Use placeholder values from the privacy pass; do not claim they are real" }

open_questions:
  - "Was the send action a click or Enter?"
```

In the example, the pace was sped up on purpose and recorded as a compression. Omit fields that do not apply, and do not fill them with guesses.

## Handling uncertainty

### The three levels

- **Observed:** seen clearly in at least one frame.
- **Inferred:** not seen directly, but the frames before and after leave one sensible explanation. Record the reasoning.
- **Assumed:** the video says nothing, and a default is chosen so the scene can play. Record the default.

Add a **confidence** where it varies: high, medium or low.

### What may be defaulted, and what may not

May be defaulted (mark `assumed`):

- Easing curves, small transition durations, exact cursor paths.
- Hover and focus styling that was never shown, using a neutral style from the product theme.
- Micro-timing within the tolerance of the frame sampling.

Must not be invented. Record as unknown, then ask or leave it out:

- Text, numbers or names that are unreadable. Use privacy-pass placeholders and mark them as placeholders. Never present them as the product's real output.
- UI that never appears on screen: menu items, settings, error states, other tabs.
- The cause of a change that has no visible cause.
- Behavior the video does not demonstrate, such as what a button does beyond what was shown.
- Product claims. A scene must not imply a capability the video does not show.

### Resolving uncertainty before guessing

1. **Look harder.** Take a denser frame sample around the moment, or zoom into the region.
2. **Use context.** Check other frames, other videos, or screenshots of the same state.
3. **Check the brief and the kit.** The site kit or the brief may answer it.
4. **Choose the simplest faithful behavior**, and label it `assumed`.
5. **Ask.** For anything that changes what the scene claims, or that cannot be defaulted safely, ask the user.

### How to ask and how to record

- Collect the questions and ask them once, at the scene spec checkpoint (phase 7), not one at a time.
- Ask in plain language, in terms of what a visitor would see ("In the video the answer appears word by word. Should the page do the same?"), and attach the frame or a description of it.
- Give a proposed default with each question, so the user can simply approve it.
- Keep an **uncertainty register** in the record: what is unknown, its level (`inferred-low`, `assumed`, `unreadable`, `not-shown`), what would resolve it, and what the scene does meanwhile.
- Carry unresolved items into the handoff README, so the dev team and reviewers know which parts are assumptions.

### Do less, not more

When in doubt, build a simpler scene that is fully supported by the video, rather than a richer one that is partly invented. A scene that shows less but shows only what is true is better than an impressive one that misrepresents the product.

## Handing the record on

- **Phase 6** merges the video record with screenshot records into `analysis/inventory.md`, reconciling component ids, final states and text.
- **Phase 7** copies scenes, components, states, `animation_sequence` and `final_state` into `spec/scenes.json`. The observation timeline is kept in the analysis folder as evidence. Uncertainties and open questions must be resolved or accepted as labelled defaults at the checkpoint.
- **Phase 8** uses text changes and sensitivity classes to drive replacement. Frames and any audio stay in the work directory.
- **Phase 10** builds the timelines from `animation_sequence`.
- **Phase 14** compares the rebuilt scene's keyframes with the reference frames at the times recorded in the timeline.

## Checklist before finishing

- The video was actually read through frames, with timestamps kept. If not possible, say so.
- Scene boundaries are stated, with confidence.
- Every component that appears has an id and type, and matches the screenshot analysis.
- Every change on screen has a cause, or is marked `cause: unknown`.
- States form a clear sequence, each with visible components.
- Text changes state how (typed, streamed, instant), timing, and legibility.
- Loading states, cursor waypoints and transitions are recorded, or stated as absent.
- Video editing effects are separated from product behavior.
- Times are in seconds with tolerances. The animation sequence is in milliseconds, with compressions listed.
- The final state is identified and reconciled with any screenshot.
- Sensitive values are recorded by category, entity id and location only.
- Every assumption and unknown is in the uncertainty register.
- Nothing was invented that the video does not support.

## Common mistakes

- Treating recorder zoom, cursor smoothing or cuts as product behavior.
- Animating something because it could move, not because it carries the claim.
- Copying real waiting time into the page, so the scene feels slow.
- Reading a time off a frame count with a variable frame rate.
- Filling in unreadable text with plausible text.
- Adding hover states, menus or error states that were never shown.
- Losing the final state, so reduced-motion visitors see an incomplete scene.
- Keeping real names or numbers in notes, frames or the spec.
- Producing a beautiful sequence that no frame supports.
