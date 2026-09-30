# Scripts

Deterministic helpers Claude calls so it doesn't do mechanical work by hand. Python 3, standard library only (ffmpeg/ffprobe, Pillow and Playwright are optional external tools).

**Run `preflight.py` first (phase 0).** It reports which optional tools exist and what degrades without each one. The skill never installs anything and never asks the user to — users of this skill may have no way to install software. `leak_scan.py` and `validate/validate_scene.py` use only the standard library, so the privacy gate and spec validation work in every environment. Every script has `--help`, a docstring, and the same exit codes: `0` ok, `1` findings or failure, `2` usage error or missing tool/input.

| Script | Status |
|---|---|
| `preflight.py` | done: phase 0 capability check (Pillow, ffmpeg/ffprobe, Playwright). Exit 0 all available, 1 something degraded |
| `resolve_site_css.py` | done: resolves the site's hashed stylesheet at build time and caches it in the kit. Never hardcode that URL — the hash changes on every deploy |
| `capture_chrome.py` | done: captures the real header, footer, promo banner and the chrome's inline Alpine scripts from the live site into `site-kit/captured/` |
| `capture_component.py` | done: captures Bookshop components from a read-only repo checkout into `site-kit/components/` with fields and localization status |
| `normalize_design_system.py` | done |
| `extract_frames.py` | done, tested (ffmpeg 6.1) |
| `validate/leak_scan.py` | done, tested on synthetic fixtures |
| `validate/validate_scene.py` | done, tested (valid fixture + 20 invalid variants) |
| `validate/check_page.py` | done, tested (Playwright 1.56 + Chromium) |
| `prepare_image.py` | done, tested (needs Pillow): crops/fits an image to a site slot, writes webp widths + `<picture>` |
| `check_classes.py` | done, tested: every class in a built page resolves against the live purged stylesheet. Pure stdlib. Exit 1 lists classes that render unstyled — the site's CSS is purged, so an unused class does not exist |
| `scan_reference.py` | done, tested (needs Pillow): measures one reference screenshot — size, **trimmed content aspect** (the number a fixed-slot scene's design width is set from), page background (ranked candidates, `--bg` to override), palette, horizontal section bands with hysteresis, vertical gutters per band, optional region grid. Run it before rebuilding any screen |
| `extract_palette.py` | done, tested (needs Pillow): derives the product-UI theme from the reference screenshots and verifies a stylesheet against them. Ranks the accent by saturation and spread, so a pale fill does not win on pixel count. Exit 1 lists theme colours the product never uses |
| `check_svg_style.py` | done, tested against the site's own 23 assets (0 deviations): generated icons/illustrations match the measured house style. Detects the three icon families, skips third-party brand marks. Pure stdlib |

Run all outputs of the scripts below under git-ignored work directories. None of them prints original sensitive values.

## normalize_design_system.py

`normalize_design_system.py <figma-variables.json> <out-dir>`: writes `design-tokens.json` and `site-tokens.css`. Reports anything missing (radii, shadows, breakpoints) instead of inventing it.

## extract_frames.py

Video to frames, `frames.json` and an optional contact sheet. Needs `ffmpeg` and `ffprobe` on PATH (exits 2 with an install hint if missing).

```bash
extract_frames.py demo.mp4 --out analysis/frames/demo --fps 2 --contact-sheet --timestamps
extract_frames.py demo.mp4 --out analysis/frames/demo --scene-threshold 0.3 --max-frames 40
```

- Interval mode (default): `--fps N`. With `--max-frames`, the rate is lowered so frames stay evenly spread.
- Scene mode: `--scene-threshold T` (0 to 1; first frame plus scene changes). Falls back to interval mode, and says so, when fewer than two frames are found.
- Writes `frames/frame_0001.png ...`, `frames.json` (`index`, `file`, `timestamp` in seconds, plus duration, resolution, fps, mode), `contact_sheet.png`, and a `.gitignore` containing `*`. Prints duration, resolution and fps.
- `--timestamps` burns times into sheet tiles; if ffmpeg lacks `drawtext` it warns and builds the sheet without them. Sheet is capped at `--sheet-max` tiles (default 48), evenly sampled.
- Exit codes: 0 ok, 1 ffmpeg failed or no frames, 2 usage error / tool or file missing.

## validate/leak_scan.py

Privacy gate from `references/privacy-masking.md` section 7.

```bash
leak_scan.py --originals .private/originals.json --map spec/privacy-map.json \
  --scan preview handoff --report reports/privacy.md
leak_scan.py --originals .private/originals.json --scan repo/content --json

# Skip shipped tooling (never content) so the player's own digits do not produce noise
leak_scan.py --originals .private/originals.json --scan preview handoff --exclude 'scene-player.*'
```

- Checks: exact; normalized (case, separators, NFKC, HTML entities, percent-decoding); encoded (base64 at any alignment, hex, URL-encoded, `\u` escapes, UTF-16 bytes); reversed; fragments (4+ char runs of originals of 6+ chars, which covers first-4/last-4 partial masks); unregistered patterns (emails outside reserved domains, phone-like numbers, 8+ digit runs, UUIDs, high-entropy tokens, URLs with numeric ids, IPv4 outside documentation ranges); media files and `data:` media; `input/`, `analysis/`, `.private/` directories; unresolved `{{entity}}` placeholders. File and directory names are scanned too. Binary files (read as latin-1) get exact/encoded/reversed checks only; files over 20 MB are reported as skipped.
- Map audit (`--map`): replacement differs from original, no shared run of 4+ characters (blocker), 3+ same-position characters (review), no collision with another entity's original or replacement, every original has a replacement.
- Severity: `blocker` (exact, normalized, encoded, reversed, forbidden dir, placeholder, map audit) or `review` (fragment, unregistered pattern, media, skipped).
- Output: file, line (or byte offset), entity id, check, severity. Never the matched text. A path component that itself matches an original is shown as `<redacted:hash>`. `--report` writes a markdown report suitable for `reports/privacy.md`; `--json` prints JSON.
- Not covered here: the runtime check (step 6, rendered text) and image contents. Run `check_page.py` and inspect media by eye.
- Exit codes: 0 no blockers, 1 blockers, 2 usage/input error.

## validate/validate_scene.py

Validates scene definitions against `references/ui-scene-system.md` section 12.

```bash
validate_scene.py scenes/my-scene/scene.json --content scenes/my-scene/content.en.json scenes/my-scene/content.de.json
validate_scene.py spec/scenes.json --content spec/content.en.json --json
```

- Accepts a scene object, `{"scenes": [...]}` or a list. Without `--content` it looks for `content*.json` next to each scene file and warns if none is found.
- Errors: duplicate ids, missing child/parent refs, unknown types (`custom` needs `description`), unresolved content keys or `source`, content entries without `role`/`translate`/`sensitivity`, literal text fields, color values or px sizes in components, states (exactly one `final`, visible/props ids exist), timeline (one anchor per step, refs exist, no cycles, targets/states exist, last `enter-state` is the final state), responsive block (designWidth, minTextPx, at least one variant with name/strategy/below), accessibility name and description.
- Warnings: verbs not in `animation-system.md` (generic motion, recipes, `enter-state`), unreachable states, unused content keys, missing `approximations`/`uncertainties`, looping scene without `accessibility.controls`. `--strict` fails on warnings.
- Exit codes: 0 valid, 1 errors, 2 usage/parse error.

## validate/check_page.py

Headless Chromium checks (Playwright; never runs `playwright install`, uses `PLAYWRIGHT_BROWSERS_PATH`).

```bash
check_page.py build/index.html --out reports/screens
check_page.py http://localhost:1313/ --reduced-motion --viewports 320,390,1440 --lang de
```

- Per viewport (default 320, 390, 768, 1024, 1440, 1920): no horizontal scroll, console/page errors, `<img>` without `alt`, text overflowing or clipped by its parent, visible text under 11 px (transform scale included), `<html lang>`, page weight against `--budget-bytes` (default 1 MiB). Full-page screenshots to `--out`.
- `--reduced-motion` emulates `prefers-reduced-motion: reduce` for the run and requires every `[data-scene]` to have `data-state` equal to `data-final-state`.
- Prints a JSON summary to stdout.
- Exit codes: 0 pass, 1 failed checks, 2 usage error, missing Playwright/Chromium, or unopenable page.

## Planned

- i18n completeness check (localization.md) and an axe accessibility scan, if a stage needs them.
