# Marketing-OS integration

> **Modes.** This file applies in Mode B (working inside the repo), and to the dev team's use of a handoff bundle. In Mode A the user has no repo. The bundle's README suggests that the dev team run it through the normal feature flow, with the README as the request and the bundle files as inputs.

Used when the repo runs the Marketing-OS pipeline: agents named `mktos-*`, commands such as `/feature` and `/ship`, `scripts/mktos/`, `.mktos-artifacts/`. If none of these exist, skip this file.

The pipeline already handles requirements, design, implementation, localization, review and shipping. This skill is a **specialist** inside it for one job: pages whose product story is told through animated, reconstructed product UI. It does not replace the pipeline and must not duplicate it.

## Who does what

| Pipeline stage | Normal job | With this skill |
|---|---|---|
| Product manager | Requirements document | Skill phases 1 to 3 feed it: brief, objective, audience, storyboard. Requirements should name the scenes and the references that feed them |
| Design lead | Component mapping, tokens, responsive, accessibility, i18n inventory | Skill phases 4 to 7 and 11 to 12 inform it: scene spec, reuse-versus-new decisions, compact variants, translatable strings |
| Lead developer | English-source implementation | Skill phases 8 to 10: privacy-safe spec, scene components, timelines |
| Localization | es, de, fr, jp from the English change | Unchanged. Skill phase 13 only prepares the English so it translates cleanly |
| Reviewer/QA | Council review, writes the review marker | Unchanged. Skill phase 14 runs first and supplies evidence. It never writes the marker |
| DevOps/Git | PR via the human's `/ship` | Never invoked by this skill |

When invoked directly, do the same work in order, but write outputs to the same places the agents would.

## Entry points

- **Through `/feature` or the automated queue:** the request text carries the brief. Screenshots and videos may need to be referenced by path. If the references are missing, ask.
- **Directly:** the marketer asks for a page with animated product scenes. Start a work item first, the way `marketing-edit` and `/feature` do: check for unfinished work, then resume or start a new one, and keep it on its own branch. Never mix two pieces of work.
- After each round, record a checkpoint on the work item (status and a one-line note), so any session can resume.

## Editable areas

Only these may change: `content/`, the theme layouts, `component-library/`, `i18n/`, `data/`, `static/`, `assets/`. Never touch configuration, the CMS config, module files, pipeline files, non-marketing scripts, the design-token file, or the generated Tailwind config. If a scene needs one of those (for example a new translatable field name, or a new build step), stop and escalate to the dev team with a clear description.

## Voice

The person is a marketer. Follow the repo's output style:

- Talk about the page, the story, the words, the look and the languages.
- Do not show code, diffs, file paths, JSON or logs unless asked.
- Present checkpoints as a plain description plus a picture of the result. For the scene spec checkpoint, describe each scene as "what the visitor sees happen", step by step.
- Never claim a thing works unless it was verified in the browser.

## Hard boundaries

- Never merge. Never push to a protected branch. Never ship on the user's behalf. The run ends **awaiting the user's review** with the change visible in the preview.
- Never publish drafts to satisfy a build.
- Never put analysis material (frames, contact sheets, original values) anywhere the ship step stages. Keep it in `.mktos-artifacts/` or an untracked folder.
- New content is `draft: false` unless the user says otherwise.
- Do not offer any way for the user to publish directly. Everything goes through the review step.

## Overlap with `marketing-edit`

`marketing-edit` handles changes to existing pages: copy, layout, images, navigation. This skill handles building a new page or section around animated product scenes. If a request is only a tweak to an existing scene's copy or spacing, hand it to `marketing-edit`. If it needs a new scene or a new page, use this skill.

## Artifacts

Store requirements-style notes and the storyboard where the pipeline expects them (`.mktos-artifacts/`) so the design lead can pick them up. Keep the scene spec, privacy map and inventory in this skill's own subfolder there.
