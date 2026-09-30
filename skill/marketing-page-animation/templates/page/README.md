# Page and scene component starter

**The starter is the repo's own animated component**, not a file invented here. Copy its shape:

`component-library/components/claude-connector-hero/` in `Optmyzr-Engineering/marketing-website`,
captured in this kit at `site-kit/components/claude-connector-hero/`.

| Part | Where it goes | Notes |
|---|---|---|
| `<name>.bookshop.yml` | `component-library/components/<name>/` | `spec.structures: [content_blocks]`, a `blueprint` default for **every** field, `_inputs` for CloudCannon |
| `<name>.hugo.html` | same folder | Real markup. All copy from fields, never hard-coded. No `.scss` file — the live animated component has none |
| `<name>.css` | `static/websitecss/` | Scene styles as a plain static asset |
| `scene-player.js` (+ any scene script) | `static/websitejs/` | Plain static asset; reads everything from `data-*` so it stays content-free |
| Page front matter | `content/english/<section>/<page>.md` | `content_blocks` entries keyed by `_bookshop_name`; start from the matching `.cloudcannon/schemas/` template |

Conventions to copy exactly, all verified from that component:

- Namespace every class and id (`ozcl-` there, `pu-` here) so nothing collides with site styles.
- Stage carries `role="img"` and a translatable `animation_alt`; the animated frame is
  `aria-hidden="true"` and `data-nosnippet`.
- Words go in translatable field names, numbers and flags in skip-key names, so demo data is
  never translated. See `site-kit/localization.md` section 3.
- Give the component a `show_animation` boolean so a page can turn it off.
- Use the site's scroll convention (`data-scroll`) for section reveal, not a parallel one.

Also here: `../example-scene/` is a valid scene definition and content file, checked by
`scripts/validate/validate_scene.py`; `../../runtime/demo/` shows final-state markup driven by
the player.
