# Demo-led solution page (Optmyzr on Slack)

Status: **observed**. One-off page with custom `c-sidekick-*` sections; hex values are hard-coded on the live page (#E6F5F6, #05747A, #CFD9E2, #E8E8E8). New pages should use tokens instead (`tokens/class-map.md`).

Order: `c-sidekick-hero`, `c-animated-trail-banner`, `c-sidekick-demos`, `c-sidekick-setup`, `c-cta-section-solutions`, `c-faq-section`, footer.

## Hero: `c-sidekick-hero`
`bg-white py-[56px] md:py-[88px]`; two-column grid `lg:grid-cols-2 gap-[56px]`.
- Left: pill "Slack + Optmyzr", H1 (`md:text-[52px]`), paragraph `max-w-[520px]`, two buttons.
- Right: chat card `skh-card`, `max-w-[480px] rounded-[16px]`, animated typed question followed by an answer (`skh-answer`). **This is the animated product scene pattern**: the card is the scene stage.

## Demos: `c-sidekick-demos`
`py-[64px] md:py-[88px]`; three feature demos, each a text block plus a product UI card.

## Setup: `c-sidekick-setup`
`py-[64px] md:py-[80px]`, background #F9F8F6. Three step cards `skp-card rounded-[14px] p-[24px] min-h-[186px]`: numbered badge (40px square, #E6F5F6, `rounded-[12px]`, ring `skp-ring`), H3 19px, paragraph 14.5px. Below: "Platforms We Support" logo row.

## CTA and FAQ
Same as the solution page standard; FAQ has 9 questions.

## What to reuse when building another demo-led page
Two-column hero with a scene card, then one demo section per claim, then steps. Scene card sizing: about 480px wide on desktop, full width on mobile; keep text at readable size, restructure instead of scaling.
