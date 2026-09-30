# Worked examples

## `sale-day-command-center.html`

A dense product dashboard rebuilt from a single screenshot, following
`references/reference-scanning.md` end to end. **28 KB, one file, no libraries, no images.**

Read it when you need to see the method applied rather than described:

| Technique | Where to look |
|---|---|
| Theme built from a measured palette, not from memory | the `:root` block and its comment |
| Authored at the reference's own size, scaled as a whole | `.sdc-frame` + the `ResizeObserver` block |
| Charts drawn as inline SVG paths, no chart library | `spark()` |
| Values counting to their settled figure | `countTo()`, with a completion callback |
| Donut sweep and gauge needle | `#ring` `stroke-dasharray`, `#ndl` rotation |
| Live behaviour the product really has | the countdown and the realtime session ticker |
| Play on view, hold, replay; pause off-screen and in a hidden tab | `cycle()` / `begin()` / `resume()` |
| Forcing a reset to commit before re-attaching transitions | the `getComputedStyle` flush in `resetVisuals()` |
| Reduced-motion path that renders the settled state | `RM` branches, plus the `@media` block |

### Three bugs it contains the fix for

1. **A selector caught more than it was written for.** `.donut svg { transform: rotate(-90deg) }`
   was meant for the ring and silently rotated the emoji SVG inside it too. Scoped to
   `.ring-svg`.
2. **Two writers on one element.** The count-up animation and the live session ticker both wrote
   to the same node, so the number visibly jumped backwards. The ticker now starts from the
   count-up's completion callback.
3. **A reset that never painted.** Setting `transition:none`, assigning the zero value and
   re-attaching the transition in one tick lets the browser coalesce them into a single recalc:
   the counters replayed and the donut and needle silently did not. Fixed by reading a computed
   style from each animated element before re-attaching.

All three look correct in the markup and only show up rendered — which is why
`reference-scanning.md` §6 insists on measuring `getComputedStyle`, not `getAttribute`.

### Tuning

`LOOP`, `DWELL` and `CYCLE` at the top of the script control replay. `LOOP = false` plays once.
