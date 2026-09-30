# Consistency report

Result of the documentation pass over `docs/`, `SKILL.md`, `references/*.md`, `site-kit/MANIFEST.md` and `templates/*.md`. `SKILL.md`, `localization.md` and `privacy-masking.md` were treated as authoritative. Paths are relative to `.claude/skills/marketing-page-animation/` unless they start with `docs/` or `README.md`.

## 1. Files rewritten

| File | Change |
|---|---|
| `docs/architecture.md` | Rewritten to match the current design (preview plus handoff bundle, two modes, site kit, layers, mermaid data flow, `marketing-pages/<slug>/` layout, scene model, privacy, localization, unverified target stack, safety principles, implemented versus planned). Numbering keeps the scene spec at section 4.1 because `schemas/README.md` points there. Dropped ideas are only in section 14 |
| `docs/workflow.md` | Rewritten around the 14 phases and 3 checkpoints of `SKILL.md`, with phase inputs and outputs, roles, a mermaid flowchart, return paths and a dev-team integration section |

## 2. Patches to reference files

| File | Change | Why |
|---|---|---|
| `references/validation.md` | Section 5 (Privacy) rewritten to point at `privacy-masking.md` section 7 (entity ids, scan steps, map audit, blocker rule, `reports/privacy.md`) and to name `leak_scan.py`, `validate_scene.py`, `check_page.py` (being added); scripts bullet in Approach names all four scripts including `extract_frames.py`; report format points to `reports/privacy.md`; header notes the phase 8 gate | Section 5 duplicated part of the scan and lacked the entity workflow |
| `references/validation.md` section 1 | Reference frames must be viewed from `analysis/` and never copied into `reports/`, including side-by-side images | `reports/` is copied into the bundle, so a side-by-side image would ship original data |
| `references/handoff-bundle.md` | Added the content of `spec/privacy-report.md` (counts by class, scan results, judgment calls, residual risks, no originals); packaging check now runs the leak scan on the final folders and blocks on a hit; `spec/design-mapping.md` is referenced in the tree, README item 3 and the packaging check; `reports/privacy.md` and screenshots-of-rebuilt-page-only added to the tree; bundle `preview/` copy is English-only without the toggle; `spec/privacy-map.json` explicitly not bundled; Mode B note (no bundle, reports still produced); header lists phases 11 and 14 | Preview toggle and drafted translations were forbidden from the bundle yet the bundle contained a preview copy; Mode B behavior was only in SKILL.md |
| `references/screenshot-analysis.md` | Sensitivity classes now match the full list in `privacy-masking.md` (added `campaign-id`, `entity-name`, `secret`, `search-term`); principle 5, the example and the mistakes list use entity ids instead of "not copied in full" | Old text allowed partial copies and used a shorter class list than the privacy reference |
| `references/feature-analysis.md` | Ground rule and inventory item 8 now require entity ids and forbid writing values (was "do not repeat them in full where avoidable") | Contradicted the "originals only in `.private/`" rule |
| `references/video-analysis.md` | Principle 6 and checklist use entity ids and add the check of frames near every state change; example step `effect: slide-up` changed to `fade-up` | `slide-up` is not in the effect table of `animation-system.md` |
| `references/design-system.md` | Token scope wording no longer presents `--site-*` as the page's scheme: the page uses the site's own classes and kit tokens, the product UI uses `--product-*` | Matches the decision that pages use the site's class names (see open item 1) |
| `references/site-kit.md` | "Used in" lists phase 13; the `verified` label now includes the design team's own token export | The manifest marks the tokens verified from a Figma export, which the old definition did not cover (see open item 2) |
| `references/animation-system.md` | Runtime contract heading says "being added" instead of "planned" | Wording aligned with `SKILL.md` |
| `site-kit/MANIFEST.md` | Tokens row reads "verified (design team's export; not yet compared with the rendered site)"; fonts row changed from "observed from export names only" to "unverified" | "Observed" means read from the public rendered site, which is not the case for fonts |
| `templates/handoff-readme.template.md` | Added a "Design mapping" line pointing to `spec/design-mapping.md`; validation summary points to the two reports | Bundle references were inconsistent |
| `templates/brief.template.md` | Languages: the site kit lists the active languages, the brief lists only differences. Sensitive data: describe the kind of data, do not paste values | Old text implied a user-chosen language list and invited pasting originals |
| `SKILL.md` | Supporting files: runtime and schemas "being added"; scripts list names `extract_frames.py` and `validate/` scripts as being added and the kit builder as planned | Matched the state described for this pass |

Checked and left unchanged because they agree: phase numbers and names across all references, the `pu-` prefix and `.product-ui[data-scene]` scope, `--product-*` for product themes, the viewport matrix (320, 390, 768, 1024, 1440, 1920, in `responsive.md` and `validation.md`), the 767/768 and 1023/1024 breakpoint assumptions, motion tokens and loop timings (`animation-system.md`, the `ui-scene-system.md` example, `video-analysis.md` example, `feature-analysis.md` typing pace), the three checkpoints, and the Mode A and Mode B statements in `SKILL.md`, `site-kit.md`, `hugo-bookshop-target.md`, `marketing-os-integration.md` and `localization.md`.

## 3. Stale statements outside the files I may edit

| Location | Problem | Suggested action |
|---|---|---|
| `README.md` | Describes a 9-stage pipeline including "i18n (copy extracted to locale files)"; says the design system is "yes, supplied by the user" (now the bundled site kit, a supplied system is optional); repository layout shows `workspace/` and `build`-style output, while `SKILL.md` uses `marketing-pages/<slug>/`; still says foundation only | Update to the 14 phases, preview plus bundle, and `marketing-pages/<slug>/` |
| `.gitignore` | Ignores `workspace/*` and `**/.private/` only; `analysis/`, `input/` and OCR or frame output in `marketing-pages/<slug>/` are not ignored, though `privacy-masking.md` section 6 requires it | Ignore `marketing-pages/` or have the skill create a `.gitignore` inside each work directory (workflow.md tells Claude to do this) |
| `.claude/skills/marketing-page-animation/scripts/README.md` | Says the validators run "against `build/`" and lists frame extraction as `extract_frames` | Change to the preview and handoff folders and name `extract_frames.py`, `validate/validate_scene.py`, `check_page.py`, `leak_scan.py` |
| `.claude/skills/marketing-page-animation/schemas/README.md` | Says `ui-spec` shape is sketched in `docs/architecture.md` section 4.1 | Still true after this rewrite. Also add that the brief and privacy-map schemas follow `privacy-masking.md` section 2 (replacements only) |
| `.claude/skills/marketing-page-animation/runtime/README.md` | Says "Not implemented yet" | Flip when the runtime lands. Also update the "being added" wording in `SKILL.md`, `docs/architecture.md` section 5 and 12, and `validation.md` |
| `.claude/skills/marketing-page-animation/templates/locales/en.json` | An empty `{}` left over from the superseded `locales/*.json` idea | Delete it |
| `.claude/skills/marketing-page-animation/templates/page/README.md` | Fine, but describes the starter as "planned" | Update when the starter exists |
| `examples/optmyzr-slack/design-system/` | Contains `site-tokens.css`, whose variables are named `--site-*` | See open item 1 |

## 4. Contradictions needing a human decision

1. **Token stylesheet naming.** The normalizer emits `site-tokens.css` with about 236 `--site-*` custom properties, and `MANIFEST.md` and `site-kit.md` ship it as the preview's token stylesheet. The design decision is that pages use the site's own class names and no page-wide `--site-*` scheme. Decide whether `--site-*` variables stay as an internal source of values for the kit (and the docs say so), or the normalizer output is renamed or restricted to what the class map needs. Until then the docs do not present `--site-*` as a scheme.
2. **Meaning of "verified" for design tokens.** I widened the `verified` definition to include the design team's own export and flagged the tokens "not yet compared with the rendered site". If the owner prefers the strict definition (real code or developer-confirmed), the tokens row should become `observed` or `unverified` and the handoff should list them.
3. **Where copy lives in `scenes.json`.** `SKILL.md` says `spec/scenes.json` holds copy, while `ui-scene-system.md` section 3 and 12 keep content in a separate `content.<lang>.json` and forbid literal text in `scene.json`. `architecture.md` describes three layers without choosing. The schema author must decide: content embedded per scene in `scenes.json`, or a side file next to it.
4. **Recipes versus generic verbs in examples.** `animation-system.md` prefers recipes (`user-types`, `approval-clicked`), while the `ui-scene-system.md` and `video-analysis.md` examples use generic verbs (`type`, `click`) for the same interactions, and `architecture.md` uses recipes. All are valid, but the examples should agree with the stated preference. Left unchanged because it needs a choice about which example is canonical for the schema.
5. **`spec/privacy-map.json` in the bundle.** It is shareable by design (replacements only) but was never listed in the bundle. I kept it out and put a privacy report in instead. Confirm the dev team does not need the map (for example to keep the same demo persona across pages).
6. **Repeat pages of the same product.** `privacy-masking.md` says to reuse the map or a shared demo persona across pages of one product, but the work directory is per page and the map is not bundled. A place for a shared persona is undefined.
7. **Scripts not yet present.** Docs now describe `extract_frames.py`, `validate_scene.py`, `check_page.py`, `leak_scan.py`, the runtime and the schemas as "being added". If the other agents change any file name, update `validation.md` (Approach and section 5), `handoff-bundle.md` (packaging checks), `SKILL.md` (Supporting files) and `docs/architecture.md` (sections 5 and 12).
