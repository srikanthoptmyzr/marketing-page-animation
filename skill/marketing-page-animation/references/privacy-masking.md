# Privacy-safe data replacement

Used from phase 4 onward (registering what is sensitive), in phase 8 (the required replacement gate, before any code), and phase 14 (final scan). Goal: no real customer, account, campaign or personal information appears anywhere in a generated page, while the product UI still looks like a real product in use.

## The vendor's own brand is never an entity

Register the values that identify **a customer, an internal account, a person or a sum of
money**. Do not register the brand name of the product the page is about.

It looks harmless — the recording shows accounts called "<Brand> Google Ads", so the brand
appears inside a sensitive value — but registering the bare word makes the leak scan block on
every heading, every paragraph and the page title, and the whole page fails the phase 8 gate
for saying the name of the thing it sells. Seen for real: 12 blockers, all of them the product
name in body copy.

Register the **full account name** (`"<Brand> USA - Ads Account"`), which is the thing that
identifies an account, and let the brand inside it raise a `review` on the fragment check. The
same applies to any ordinary word a sensitive value happens to contain: an entity has to be
distinctive enough that finding it in shared copy means something went wrong.

## Core principle

**Never hide real data. Replace it with synthetic data.**

Every sensitive value is fully replaced by a realistic, randomly generated one of the same visual format and about the same length, *before* the value is used by any scene, file or script. Nothing is hidden, blurred, masked or overlaid, because hidden data is still present.

Forbidden, without exception:

- Blur, pixelation or opacity tricks
- Partial masks such as `••••••7890`, `****7890`, `xxx-xx-7890`, or "first four, last four" keeps
- Redaction bars or overlay boxes, and screenshots placed under or over the scene
- CSS masking (`filter: blur`, `mask`, `clip-path`, `-webkit-text-security`, text colored to match its background) or JavaScript that swaps text at run time
- Hard-coded "demo" text such as `XXXX`, `John Doe`, `12345`, unless the brief asks for an obviously-demo look

Bad: `1234567890` → `••••••7890`. Good: `1234567890` → `8472916350`.

## 1. Sensitive data detection

Reconstructed UI is real text, so replacement is a data operation. That only works if every sensitive value is found. Look in **every** place a value can appear, not only in the main content.

### What to look for

| Class | Examples |
|---|---|
| `account-id` | Account, customer, workspace, manager and tenant IDs; invoice, order and billing numbers |
| `campaign-id` | Campaign, ad group, ad, keyword, asset, label, budget and audience IDs |
| `entity-name` | Campaign, ad group, ad, audience, report and rule names that contain customer, product, region or brand detail |
| `person-name` | Users, contacts, authors, assignees, approvers, chat participants |
| `email` | Any email address |
| `phone` | Phone numbers in any format |
| `company` | Customer, client, agency and business names; store or property names |
| `url` | Customer domains, landing pages, links with account or customer identifiers, tracking parameters, internal tool URLs |
| `secret` | API keys, tokens, session IDs, webhook URLs, license keys, anything credential-shaped |
| `amount` | Spend, revenue, budgets, balances, bids, conversions and any figure that is the customer's own business data |
| `address` | Street addresses, locations tied to a business, IP addresses |
| `search-term` | Keywords and search queries that reveal a customer's business |
| `other-pii` | Avatars and photos of real people, customer logos, signatures, anything else that identifies a person or account |

Classify by what the value is, not where it appears. When unsure, treat it as sensitive and ask.

### Where to look

- Body text, tables, chart labels, axis values, legends and tooltips
- Header bars, breadcrumbs, account switchers, sidebars, user menus, footers
- Browser chrome: address bar, tab titles, bookmarks, other open tabs, extensions
- Notifications, toasts, badges, chat messages, AI responses, emails and previews
- Text partly cut off, faint, tiny, or visible for only a few frames of a video
- Timestamps and dates only when they pin the material to a real event; otherwise keep
- Filenames, window titles, URLs in status bars, and metadata in the media files themselves (device name, path, EXIF)
- Images inside the UI: avatars, logos, thumbnails, ad creatives

### How to detect

1. **Read pass.** For each screenshot and frame, list every visible text item and classify it. Use OCR only as an aid, and keep OCR output in `.private/` because it contains originals.
2. **Pattern pass.** Scan the transcribed text for ID shapes, emails, phones, URLs, UUIDs, long digit runs, high-entropy strings and currency.
3. **Cross-reference pass.** Any entity found once is searched for everywhere else, in other frames, other states and derived forms (a name in a message and in an avatar; an ID in a URL and a label).
4. **Judgment pass.** Ask the user about doubtful items (see the end of this file).

### Business and personal names

Names are the hardest class, so use this rule:

- **Keep** public, generic or product names that are the subject of the page: the product itself, and widely known platforms the product connects to (a chat app, an ad platform), since these are needed for the story.
- **Replace** customer, client, agency, store and person names, and any campaign or entity names that embed them.
- **Keep** a customer name only when the user confirms it is an approved reference customer. Record the approval in the brief. When in doubt, replace.

## 2. Synthetic replacement strategy

### Entities, not strings

Work with **entities**. An entity is one real thing (one account, one campaign, one person) that may show up in many places and many forms. Each entity gets an id like `acct-1`, `camp-3`, `person-2` and exactly one replacement.

Keep originals and replacements in two files so a leak of one does not leak the other:

| File | Contents | Shareable? |
|---|---|---|
| `.private/originals.json` | For each entity id: class, the original value, every surface form seen, and where it was seen (asset and timestamp) | **Never.** Git-ignored. Used by the scanner only |
| `spec/privacy-map.json` | For each entity id: class, format template (length, grouping, character classes), and the **replacement** | Yes, contains no originals |

Because the two files join only through the entity id, the spec and the map can be shared without exposing originals.

### Replace at the moment of transcription

The replacement must happen **before the value is used by the page**, and ideally before it is used by anything else:

1. While reading a screenshot or video, the first time a sensitive value is seen, register it in `.private/originals.json` and give it an entity id.
2. From that moment, write only the entity id (for example `{{acct-1}}`) in analysis records, the inventory, notes and the draft spec. **Do not copy the original into `analysis/*.yaml`, `inventory.md`, `scenes.json` or chat.**
3. In phase 8, generate the replacements, write `spec/privacy-map.json`, and resolve every `{{entity}}` reference in the spec to its replacement.
4. Only then build (phase 9). Scenes are generated from the resolved spec.

If an original slipped into a working file before it was registered, register it now, remove it from that file, and treat it as a finding for the phase 14 scan.

### How replacements are generated

1. **Random, not derived.** Draw characters from a cryptographically secure random source. Never seed from, hash, shift, scramble, reorder or otherwise transform the original. Nobody, including someone holding the map, should be able to work backwards from a replacement to an original.
2. **Independent of the original's content, dependent only on its shape.** The generator receives the format template (length, grouping, character classes), not the value.
3. **No overlap.** Reject and regenerate if the candidate:
   - equals the original, or equals any other original in the project,
   - shares three or more characters in the same positions, or any run of four or more consecutive characters, with the original,
   - equals another entity's replacement.
4. **Realistic enough for a demo.** Avoid patterns that look fake (`12345`, repeated digits, sequences), leading zeros the original did not have, and words that draw attention. The reader should not think about the data at all.
5. **Generated once, then frozen.** After the map is written, replacements never change on a rebuild. Regenerate only when a replacement fails a check.

### Generic segments that may stay

A replacement may keep a segment that is a generic label and identifies nothing (for example the ` | Search` part of a campaign name). Declare it in the entity's `format.keep` in `spec/privacy-map.json`. The leak scanner and the map audit ignore declared segments, so they neither flag the overlap nor count them as leaks. Declare only what a reasonable person would call generic, and never a customer, product or place name.

### Safe ranges

Some values can accidentally belong to a real party, so use reserved space where it exists:

- **Email and URL domains:** `example.com`, `example.org`, `example.net`, or a `.test` or `.invalid` domain. Local parts are fictional and plausible (`alex.martin@example.com`).
- **Phone numbers:** ranges reserved for fiction where the country has them (for example the US 555-0100 to 555-0199 block, and the UK Ofcom drama ranges). Where a country has no reserved range, a random well-formed number can belong to a real subscriber. Say so in the handoff and let the user choose between a well-formed random number and a reserved-range one from another country.
- **Names:** fictional and culturally plausible for the market. Avoid celebrities and known public people.
- **Companies:** invented names, checked by search that they are not an obvious real business or trademark.
- **Secrets:** see the next section. Never use a real-looking credential of a real vendor's exact format.

## 3. Format-preserving replacement

Replacement keeps the same **visual structure**, so column widths, wrapping, alignment and the general look of the reference stay the same. It does not keep the same value, or any part of it.

| Kind | Original (illustrative) | Replacement | Rule |
|---|---|---|---|
| Numeric ID | `1234567890` | `8472916350` | Same digit count. First digit nonzero if the original's was |
| Grouped ID | `123-456-7890` | `847-291-6350` | Same grouping and separators |
| Prefixed ID | `ACC-839271` | `ACC-472918` | The prefix is a label, keep it. Replace only the variable part |
| Entity with number | `Campaign_984372` | `Campaign_261847` | Same prefix, separator and digit count |
| Hex / short code | `9f3a1c` | `b27e40` | Same length, same case, same alphabet |
| UUID | `3f2b8c1e-...` | a new random v4 UUID | Same layout. Keep version and variant bits valid |
| Token / API key | 40 mixed characters | 40 random characters of the same alphabet | Same length and character classes. **Do not copy vendor prefixes** that secret scanners recognize (for example well-known cloud, chat or code-host token prefixes): use a neutral prefix of the same length, so the dev team's secret scanning does not flag the page |
| Email | `customer@company.com` | `alex.martin@example.com` | Similar local-part length, reserved domain |
| Phone | `+91 98765 43210` | `+91 76428 19357` | Same country code, grouping and length (see safe ranges above) |
| URL with identifier | `.../accounts/839271/...` | `.../accounts/472918/...` | Replace the identifier and any domain; keep path shape. Same entity gets the same replacement as elsewhere |
| Domain | `acmeshoes.com` | `northwind-outfitters.example` | Similar length, reserved TLD |
| Person name | `Priya Raman` | `Maya Fernandez` | Similar length, same script, same number of words |
| Business name | `Acme Shoes GmbH` | `Harbor Lane Studio GmbH` | Keep legal suffix (it is not identifying). Similar length |
| Campaign / ad group / ad name | `US - Brand - Search - Q3` | `UK - Core - Search - Q1` | Keep the naming pattern and separators. Replace segments that identify the customer, product or place; generic segments (`Search`, `Brand`) may stay |
| Keyword / search term | `buy running shoes berlin` | `book studio classes chicago` | Similar length and intent, different business |
| Currency and amounts | `$12,480.55` | `$9,317.20` | Same currency symbol, separators, decimals and number of digits |
| Percent / ratio | `3.42%` | `2.87%` | Same precision |
| Dates | `Jan 14, 2026` | keep, unless it pins a real event | Do not shift to hide, only replace when identifying |
| Address | real street | invented street on a reserved or generic pattern | Same line structure |
| IP address | real IP | address in a documentation range (`192.0.2.x`, `198.51.100.x`, `203.0.113.x`) | |
| Card numbers | anything card-shaped | never reproduce | Use a payment processor's published test number only if a card must be shown |

### Amounts and charts keep their story

Numbers that carry meaning need care, or the demo stops making sense:

- Choose new values from the **story** you want to show (direction, rough magnitude, relative sizes), not by multiplying the originals. If a scaling factor is used at all, it is random, private and never written to a shared file, and each value gets its own variation.
- Re-derive everything that depends on a value: totals, percentages, deltas, chart bars, table sums, "up 12%" labels. Arithmetic on screen must be correct.
- A chart that goes up in the reference goes up in the scene. A ranking keeps its order unless the story changes.
- Avoid round or suspiciously exact numbers.

## 4. Consistency rules

- **One entity, one replacement, everywhere on the page.** If `Campaign 839271` becomes `Campaign 472918`, every occurrence, in every scene, state, tooltip, table, chart label, URL, alt text and description, becomes `Campaign 472918`. Do not generate a new value each time the same entity appears.
- **Match all surface forms.** `Campaign 839271`, `campaign_839271`, `#839271` and a bare `839271` are one entity. Match ignoring case, whitespace, separators and Unicode variants. Rebuild each form from the same replacement core with that form's prefix and separators.
- **Across scenes, languages and outputs.** The preview, the bundle, every scene, and every language use the same map. Translators receive only the resolved values.
- **Across rebuilds.** The map is frozen. A rebuild reads it and never regenerates.
- **Across pages of the same product.** If you build more than one page for one product, reuse the same map, or a shared "demo company" persona (names, accounts, campaigns), so the story stays coherent.
- **Internal consistency.** Names match their avatars' initials, emails match names where the reference shows that relationship, IDs match their URLs, and counts match the rows shown.
- **No collisions.** Two different entities never share a replacement, and no replacement equals any original.
- **Related entities keep their relationships.** A campaign still belongs to the same account, an ad group to the same campaign.

## 5. Reference image and video handling

- Screenshots, frames, contact sheets and videos are **inputs only**. They are never placed on the page, under the scene, or over it to hide anything. Never crop, blur or annotate a reference image and use it as an asset.
- Extracted frames and OCR output contain real data. They live in `analysis/` or `.private/`, never in `preview/`, `handoff/` or any repo folder. Add both to `.gitignore`.
- The analysis records describe layout, states and interactions. They refer to sensitive text by entity id and location ("`acct-1` in the header, frame 12"), not by value.
- Video needs extra care: sensitive values may be visible for a fraction of a second, appear only in a hover, tooltip or notification, or change between frames. Review the contact sheet **and** the sampled frames near every state change.
- The scene is rebuilt from resolved values. It does not include the pixels, the image, or a cropped copy of any reference.
- Reference **images inside the UI** (avatars, logos, ad thumbnails, product photos) are replaced with initials, neutral shapes or original illustrations, never with cropped originals.
- Do not describe originals in chat, reports or commit messages. Refer to categories and entity ids.
- The user may show real data to Claude to get a scene built, but it must never reach a shared file. If the user pastes a value into chat, register it and stop repeating it.

## 6. Source-code safety

The original value must not remain in **any** of these, in any form:

- HTML, CSS and JavaScript, including comments, `data-*` attributes, class names, ids, `title` and `aria-*` text, and alt text
- JSON, YAML and TOML data files, front matter and content files
- Translation and UI string files, in every language
- React props or component state, framework config and test fixtures (if the target uses them)
- Metadata, `<meta>` tags, Open Graph text, sitemaps, manifest files
- URLs, query strings, hash fragments and filenames
- SVG text and metadata, generated images, image EXIF, PDF properties
- Source maps, build caches, logs, screenshots taken during validation, and version-control history

Rules that follow:

1. **Replace upstream, never at render time.** The scene must be generated from the resolved spec. Do not ship a script, template filter or CSS rule that swaps or hides text at run time, because that would carry the original in the shipped code.
2. **No derived tokens.** Do not use a hash, encoding, encryption, reversed string, base64 or fragment of an original as an id, key, class or filename.
3. **No originals in scripts or logs.** Any script that touches originals (OCR, the scanner) writes to `.private/` only, and does not print values. The scanner reports entity ids and file locations, never the values.
4. **No leaks through helpers.** Commit messages, PR text, reports, checkpoint summaries and chat contain categories and counts, not values.
5. **Version control.** If an original is ever committed, deleting it in a later commit does not remove it from history. Tell the user, so the repository owners can purge history and, for secrets, rotate the credential.
6. **Ignore rules.** `.private/`, `analysis/`, `input/` and any OCR or frame output are git-ignored in the work directory.
7. **Do not decide by visibility.** A value hidden by `display: none` or off-screen is still shipped. It is still a leak.

## 7. Final privacy validation

Runs in phase 14 as a **required gate**. The page is not complete while any check fails. A finding is a **blocker**.

### The scan

Search every file in `preview/` and `handoff/` (and in Mode B, every file added or changed in the repo, including each language's content, data and UI string files) for the following. Include text files, SVG, comments, filenames, and metadata.

1. **Exact match.** Every original in `.private/originals.json` and every surface form recorded for it.
2. **Normalized match.** The same originals ignoring case, whitespace, separators and punctuation, Unicode normalization, HTML entities, and percent-encoding.
3. **Encoded and reversed.** Common encodings of the originals (base64, hex, URL-encoded) and reversed strings.
4. **Fragments.** For ID-like originals (no spaces, at least one digit, six characters or more), any run of four or more consecutive characters, including first-N and last-N pieces (the classic partial-mask leak). For name-like originals, any distinctive word of five or more letters, except common words and segments declared in `format.keep`. Fragment hits are `review` items: check each by hand and remove coincidences.
5. **Unregistered patterns.** Sensitive-looking values that are not in the privacy map: emails on non-reserved domains, phone numbers, ID-shaped digit runs, UUIDs, high-entropy strings, URLs with identifiers, IP addresses outside documentation ranges. Each one is either registered and replaced, or explicitly justified as public.
6. **Runtime check.** Render the page in a headless browser in each state the timeline can reach, extract the visible and accessible text, and scan it too. This catches values built by scripts at run time.
7. **Media check.** Confirm no reference screenshot, frame, video or contact sheet is in the output. Check any shipped image for text, EXIF and other metadata. Look at it, not just its name.
8. **Localization check.** Scan every language's files (Mode B) or the English bundle plus any preview-only translations (Mode A). Confirm the same replacement is used in each language.

### The map audit

- Every `{{entity}}` reference in the spec resolved. None remain in output.
- Every replacement differs from its original, shares no long run with it, and does not collide with another entity's original or replacement.
- Every entity has exactly one replacement everywhere it appears, in all its surface forms.
- Amounts and charts are internally consistent (totals add up, percentages match, directions match the story).
- Format is preserved: same length, grouping and structure as the original, so layout matches the reference.

### Report

`reports/privacy.md` and the bundle's `spec/privacy-report.md` state:

- Counts of entities replaced by class (for example "12 IDs, 5 names, 3 emails").
- Result of each scan step, with file paths and entity ids for any finding, never original values.
- Judgment calls that were made and by whom.
- Residual risks (for example a phone number from a country with no reserved range).

The report never contains an original value.

### On a finding

Fix the map and spec, regenerate the affected scenes from the resolved spec (never patch the output), and re-run the whole scan. Also check whether the original reached any shared location (a commit, a chat message, a shared preview link) and tell the user if so.

## Judgment calls to raise with the user

- Whether a piece of data is actually public (a public product name, a public statistic) and may stay.
- Whether a customer or person may be shown by name because they approved it, and where that approval is recorded.
- Business figures where even changed values could be sensitive, such as revenue or customer counts a company would not publish.
- Third-party personal data in demo content.
- Phone numbers and company names where no safe range exists.

Ask rather than assume. It is cheaper to replace something unnecessarily than to publish something that should have been replaced.

## What this skill does not do

It does not decide legal or compliance questions. If the material may be covered by a confidentiality agreement, a data-protection law or another regulation, tell the user to have the page reviewed before it is published or shared, including the preview link.
