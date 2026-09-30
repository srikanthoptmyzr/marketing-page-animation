# Homepage, pricing, listing, demo-request

Status: **observed** from fetched page structure; class-level details only for what is listed. Treat anything not stated here as unknown.

## Homepage `/`
Sections in order: hero (H1 "Worry-free account management for the AI and automation era", platform badges, Start Trial + Book A Demo, dashboard screenshot carousel), logo strip, case-study cards, features grid, AI section, migration CTA, getting-started 3 steps, product line cards (Social, Amazon), awards, partners, by-the-numbers, team use-case cards, testimonials (G2, Capterra), final CTA, footer.
Classes seen: `c-cta-section-1`, `c-trail-banner`, `c-testimonial-section`, `c-reviews-section`, `c-features-section`, `c-perks-section`, `c-cta-section-solutions`, `c-steps-section` (twice), `c-animated-trail-banner`, `c-awards-section`, `c-bynumbers-section`, `c-teams-section`. Internals of these not read yet.

## Pricing `/pricing/`
No `c-` classes. Darker teal top with ad-spend slider, Monthly/Annual toggle (30% off annual), three tier cards (Essentials, Premium, Enterprise), expandable comparison table, `c-testimonial-section` + `c-reviews-section`, "There's More From Optmyzr", "Advanced Features", pricing FAQs on a light grey background.

## Case-study listing `/case-studies/`
Featured spotlight hero, "Filter By" dropdown, card grid (category tag, headline, description, "Read Full story"), numbered pagination, CTA. Detail pages at `/case-studies/<slug>/` not read.

## Demo-request landing `/demo-request`
Full header and footer, hero "The PPC platform that puts marketers back in control", G2 badge + testimonial, logo strip, four benefit sections, CTA block. The form was not visible in the fetched text: **unknown**.

## Not surveyed
`/compare/`, `/products/social/`, `/products/amazon/`, `/products/ecommerce/`, `/about/`, `/contact`, blog.

## URL map (for links and breadcrumbs)
`/pricing`, `/demo-request`, `/solutions/{optmyzr-ai, optmyzr-mcp, optmyzr-on-slack, monitoring, automation, budget-management, ppc-audits, optimizations, reporting, digital-marketing-agencies, freelancers, marketing-teams, enterprises}`, `/products/social/`, `/products/amazon/`, `/products/ecommerce/`, `/case-studies/`, `/compare/`, `/about/`, `/contact`, `/blog`.
