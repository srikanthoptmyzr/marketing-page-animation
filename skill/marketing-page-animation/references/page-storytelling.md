# Page storytelling

Used in phases 1 to 3. Goal: decide what story the page tells before touching any reference or code.

## Understanding the brief

Extract, and write down in your own words:

- **Product line:** which Optmyzr product — Search, Amazon, Social or Ecommerce. This sets the page's color theme (`data-product` on `<body>`) and the scene accent palette. If the brief omits it, ask.
- **Product and feature:** what it is, in one sentence a stranger would follow.
- **Problem it solves:** the pain, in the audience's language.
- **Outcome:** what changes for the user after adopting it.
- **Proof available:** real capabilities visible in the references, numbers the brief provides, customer evidence. Only claim what the brief or references support.
- **CTA:** the action, its label, its destination.
- **Constraints:** tone, banned words, legal or compliance wording, languages, deadlines.

List every gap as a question or a labelled assumption. Ask only about gaps that would change the page: the objective, the audience, the CTA, the languages.

## Objective and audience

Pick **one primary objective** (for example: request a demo, start a trial, understand a new feature, install an integration). Everything else is secondary. Then pick **one primary audience** and state:

- their role and what they are trying to get done,
- what they already know about the product category,
- their likely objections.

Write the visitor's journey as three sentences: what they believe on arrival, what they need to see to be convinced, what they do next.

## Product story, not a landing page

A landing page lists features. A product story shows the product doing something for someone. Build the page as a sequence in which each scene is a moment in that story.

A useful arc:

1. **Hook.** The situation the audience recognizes, and the promise. The hero usually contains the strongest scene, already animating.
2. **Show.** The core interaction, played in front of the visitor. This is the main proof.
3. **Deepen.** Two to four further scenes, each demonstrating one capability or one step of the workflow, ordered so the story escalates rather than repeats.
4. **Reassure.** Trust, security, integrations, results, whichever answers the audience's main objection.
5. **Act.** The CTA, restated with the payoff.

Not every page needs every beat. A short feature page may be hook, show, act.

## Storyboard

Write `spec/storyboard.md` with one block per section:

- **Section name and job:** what it must accomplish for the visitor.
- **Headline claim:** one sentence the scene proves.
- **Scene:** which reference feeds it, and what the visitor watches happen.
- **Supporting copy:** short, benefit-led, keyed later.
- **Transition to next section:** why the story moves on.

Rules of thumb:

- One idea per scene. If a video shows three things, it is three scenes or one scene with three beats, not one crowded scene.
- Put the animation where the claim is. Copy states the claim, the scene proves it.
- Prefer showing the result of an action over describing it.
- Keep the page short enough that the story never stalls. Cut any section that does not change what the visitor believes.
- Do not pad the page with generic sections (testimonials, feature grids) unless the brief supplies real content for them.
- Copy is written for translation: short sentences, no idioms, no puns that depend on English.
- Plan sections from the patterns in the site kit (see `site-kit.md`), plus the new scene components. Note any section the kit lacks.

## Check before presenting

- Can the objective, audience and CTA be stated in one line each?
- Does each section have a distinct job?
- Does every scene map to a supplied reference, or is it flagged as needing new material?
- Would the page still make sense with the copy removed and only the scenes playing?

Present the storyboard in plain business language and wait for approval. The storyboard also goes into the handoff bundle, so the dev team knows the intent.
