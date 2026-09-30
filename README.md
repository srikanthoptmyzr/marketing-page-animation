# Marketing Page Animation

A Claude skill that turns a page brief and a handful of product screenshots into a shareable preview page plus a handoff bundle for the dev team — without needing access to the website's code.

When a screenshot or recording shows the product doing something, the skill does not put that image on the page. It rebuilds the interface in HTML, CSS and a small shared player, then replays the interaction. That keeps pages light, keeps every product-UI string translatable by the site's own pipeline, and keeps customer data off the page: sensitive values are replaced with format-preserving synthetic ones, never blurred or masked.

Built for marketing and customer-success staff. It never pushes, merges or publishes to the live site.

## What you need

| | |
|---|---|
| A page brief | Product, objective, audience, key messages, CTA. Start from `skill/marketing-page-animation/templates/brief.template.md` |
| Screenshots or a screen recording | Key states of the product UI |
| Python 3 | Required. The privacy gate and scene validator are pure Python |
| ffmpeg, Pillow, Playwright | Optional. Phase 0 reports what's missing and takes a documented fallback |

No repo access, and no site design files — the bundled site kit carries the design.

## Install

Clone and symlink the skill into your Claude Code skills folder:

```bash
git clone git@github.com:srikanthoptmyzr/marketing-page-animation.git
```

```bash
mkdir -p ~/.claude/skills && ln -s "$PWD/marketing-page-animation/skill/marketing-page-animation" ~/.claude/skills/marketing-page-animation
```

Check what's available in your environment before the first run:

```bash
python3 skill/marketing-page-animation/scripts/preflight.py
```

For an organization-level skill on Claude Team or Enterprise, zip `skill/marketing-page-animation/` with `SKILL.md` at its root and upload that.

## Use it

Ask Claude for the page in plain language — name the product line (Search, Amazon, Social or Ecommerce), attach the brief and the screenshots:

> Build a solution page for Smart Product Labeler under Ecommerce. Brief attached, plus six screenshots of the feature.

The run works through 15 phases and stops for you three times: after the storyboard, after the scene spec, and after validation with the bundle packaged. Two phases are hard gates — the environment check at the start, and the privacy replacement, which no code may be written before.

Each run produces:

- **`preview/`** — a self-contained page with the site's real header, footer and tokens. Open it, share it, mark it up.
- **`handoff/`** — the scenes as site-style components, page content in the site's format, UI strings, assets, the scene spec, a plain-language note and the validation report.

## What's here

| Path | |
|---|---|
| `skill/marketing-page-animation/SKILL.md` | The skill itself: phases, rules, checkpoints |
| `skill/marketing-page-animation/references/` | 20 topic files, loaded one phase at a time |
| `skill/marketing-page-animation/site-kit/` | Captured header, footer and stylesheet; 90 component blueprints; design tokens; 21 page types with a routing table; the verified localization mechanism |
| `skill/marketing-page-animation/scripts/` | Preflight, frame extraction, image fitting, palette scanning, and five validators — classes, markup balance, SVG house style, scene validity, leak scan |
| `skill/marketing-page-animation/runtime/` | The shared scene player, a synthetic demo and a headless test |
| `skill/marketing-page-animation/examples/` | A dense dashboard rebuilt from one screenshot: 28 KB, no libraries |
| `docs/` | Architecture, workflow, repo inventory, fidelity notes, and the project notes |

## Rules that always hold

1. **Reconstruct, don't embed.** Screenshots and recordings are inputs, not page assets. A raster fallback needs a recorded reason.
2. **Replace data, never hide it.** No blur, no partial masks, no overlays. Values become entity ids the moment they're read; originals never leave `.private/`.
3. **Never invent the website.** Header, footer, forms and known page structures come from the kit. Anything missing is flagged as a kit gap, anything assumed as unverified.
4. **One markup, two homes.** The preview can't contain anything the handoff bundle can't.
5. **Complete without JavaScript.** Every scene renders in full at rest — that's what reduced-motion visitors see.
6. **Copy is data.** No hard-coded strings anywhere, including inside the product UI.
7. **Never publish.** The end state is a preview and a bundle. Sharing either is the user's call.

The full list, with the reasoning, is in `SKILL.md`.

## Working on the skill

Project workspaces are deliberately untracked: they hold reference screenshots with real customer data and the `.private/` originals register. Keep them under `workspace/`.

Before committing anything built from real references, run the leak scan:

```bash
python3 skill/marketing-page-animation/scripts/validate/leak_scan.py --originals workspace/<slug>/.private/originals.json --map workspace/<slug>/spec/privacy-map.json --scan workspace/<slug>/preview workspace/<slug>/handoff --exclude 'scene-player.*'
```

Run the player's headless test after touching the runtime:

```bash
python3 skill/marketing-page-animation/runtime/demo/test_player.py --shots /tmp/shots
```

First reference site is [Optmyzr](https://www.optmyzr.com). Nothing in the method is specific to one product or one site — the site kit is the part that is.
