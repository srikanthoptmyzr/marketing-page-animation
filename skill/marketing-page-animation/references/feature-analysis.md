# Feature analysis

Used in phases 4 to 6. Goal: describe exactly what the references show, in enough detail that the UI can be rebuilt without looking at the source again, and without inventing anything.

## Ground rules

- Describe what is visible. Mark anything inferred as inferred.
- If text is unreadable, blurry or cropped, record it as unreadable and ask. Never fill in plausible text.
- Register each sensitive value as an entity in `.private/` the first time it is seen (see `privacy-masking.md`) and refer to it by entity id, category and location. Never write the value into a record, note or chat.
- Keep the product's own visual language separate from the marketing site's. You are documenting the product here.

## Analyzing screenshots (phase 4)

Follow `screenshot-analysis.md`. It defines the passes and the YAML analysis record written to `analysis/screenshots/<id>.yaml`. Video keyframes are analyzed with the same method.

## Analyzing videos (phase 5)

Follow `video-analysis.md`. It defines frame extraction, scene boundaries, events, states, text, loading, cursor, transitions, timing and the uncertainty rules, and the YAML record written to `analysis/videos/<id>.yaml`.

## Identifying interactions and transitions (phase 6)

For every scene, produce a sequence of **cause, effect, transition** entries:

| Cause | Effect | Transition |
|---|---|---|
| User types a question into the composer | Text appears character by character | Typing at ~40ms per character |
| User presses send | Message moves into the thread, composer clears | Slide up and fade, ~250ms |
| Product responds | Answer streams in, then a chart appears | Streamed text, chart fades in |

Also record:

- **States** each component passes through.
- **Attention cues:** cursor movement, highlights, badges, focus rings.
- **Loops:** does the demo reset? What is the start and end state?
- **Dependencies:** which effects need an earlier one to have happened.

## Output: `analysis/inventory.md`

One section per scene containing:

1. Source (file, time range, keyframes).
2. Purpose and the claim it supports.
3. Layout and design width.
4. Component inventory, with hierarchy.
5. Text inventory, marked as chrome or data, translatable or not.
6. Product tokens (fonts, colors, radii, shadows, spacing), marked as estimated.
7. Interaction table (cause, effect, transition, timing).
8. Sensitive values found, by entity id, category and location (never the value).
9. Ambiguities and open questions.

Do not move on until every interaction has a described cause and effect and every open question is either answered or accepted as a labelled default.

## When a reference cannot be rebuilt

Photos, maps, third-party embeds, video content inside a video, and highly custom illustration may not be reconstructable. For these, decide with the user: simplify, crop, replace with an original illustration, or use a raster asset. Record the decision and reason in the inventory.
