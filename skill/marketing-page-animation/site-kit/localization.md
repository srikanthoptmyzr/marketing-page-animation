# Localization (site kit)

How the Optmyzr marketing website localizes pages. Answers to the discovery table in
`references/localization.md` step 1, read from the repository (read-only).

**Source:** `Optmyzr-Engineering/marketing-website`, branch `main`, commit `c9ac095` (2026-09-28).
**Status of this file:** **verified** unless a row says otherwise. Verified = read from repository code or config.

## 1. Language definition

| Question | Answer | Source | Status |
|---|---|---|---|
| How are languages defined? | Hugo `[languages]` block, one table per language with `contentDir`, `languageCode`, `languageName`, `weight` | `config/_default/hugo.toml` | verified |
| Which languages are active? | **en, es, de, fr, jp** — five. **`da` (Danish) is disabled** via `disableLanguages = ["da"]` | `config/_default/hugo.toml` | verified |
| Default language | `en`, and `defaultContentLanguageInSubdir = false`, so English is served at the site root with **no prefix** | `config/_default/hugo.toml` | verified |

Active languages, exactly as configured:

| Key | Name | `languageCode` | `contentDir` | Data dir | UI strings | URL prefix | weight |
|---|---|---|---|---|---|---|---|
| `en` | English (source) | `en-us` | `content/english/` | `data/en/` | `i18n/en.toml` | `/` (none) | 1 |
| `es` | Español | `es-es` | `content/es/` | `data/es/` | `i18n/es.toml` | `/es/` | 2 |
| `de` | Deutsch | `de-de` | `content/de/` | `data/de/` | `i18n/de.toml` | `/de/` | 3 |
| `da` | Dansk — **DISABLED** | `da-dk` | `content/dansk/` | `data/da/` | `i18n/da.toml` | — | 4 |
| `fr` | Français | `fr-fr` | `content/fr/` | `data/fr/` | `i18n/fr.toml` | `/fr/` | 5 |
| `jp` | 日本語 | `ja-jp` | `content/jp/` | `data/jp/` | `i18n/jp.toml` | `/jp/` | 6 |

**The Japanese key is `jp`, not `ja`.** The content dir is `content/jp/` and the strings file `i18n/jp.toml`.
Any `ja` file in the repo is legacy; never write to it, never create `content/ja/`.

Note the asymmetry the skill must respect: the English **content** directory is `content/english/`
(spelled out), while its **data** directory and strings file use the short code (`data/en/`, `i18n/en.toml`).

## 2. Where content lives

| Question | Answer | Source | Status |
|---|---|---|---|
| How is translated page content stored? | One Markdown file per language, mirroring the path: `content/english/<rel>` → `content/<lang>/<rel>` | `.claude/agents/mktos-localization.md`, `config/_default/hugo.toml` | verified |
| Front matter format | **YAML** (`metaDataFormat = "yaml"`). Never emit TOML front matter | `config/_default/hugo.toml` | verified |
| How are structured data and lists translated? | Per-language data directories: `data/en/<rel>` → `data/<lang>/<rel>`. Shared, non-textual data (authors, taxonomies, `languages.yaml`) sits at `data/` root and is not per-language | `data/` | verified |
| How are small UI strings stored? | Hugo i18n TOML, one file per language, flat keys with an `other = "…"` value. Called from templates as `{{ i18n "key" }}` | `i18n/*.toml`, e.g. `features-section.hugo.html` uses `{{ i18n "alert_delivery_options" }}` | verified |

## 3. Which fields are translated

The authoritative lists live in **`scripts/translation-scripts/translation/config.js`**:

| List | Size | Meaning |
|---|---|---|
| `translatableKeys` | 306 keys | Front-matter keys whose values are translated when present |
| `skipKeys` | 121 keys | Never translated, copied verbatim; also **halts recursion** into that subtree |
| `urlReplaceKeys` | 27 keys | Internal/relative links that get the language prefix added |

Consequences for this skill:

- A field name **not in `translatableKeys` is silently left untranslated**. Naming a scene field is therefore a localization decision, not a cosmetic one.
- A field name in `skipKeys` is not only untranslated, it **blocks everything nested inside it**. Never nest scene copy under a skipped key.
- `image`, `ogImage`, `icon`, `video`, `screenshot`, `alt`-bearing media paths and `_bookshop_name` are all skip-keys — the skill's scene assets and component names are safe there by default.
- `alt`, `altText`, `caption`, `placeholder`, `tooltip`, `label`, `animation_alt` **are** translatable, so alt text on a scene is translated automatically.

### Scene-relevant translatable keys that already exist

The list already carries UI labels for an **animated product-UI scene** (added for `claude-connector-hero`).
Reuse these names before inventing any:

`chat_title`, `chat_chip`, `new_chat`, `recents_label`, `recent_chats`, `connected_label`, `greeting`,
`prompt`, `composer_placeholder`, `reply_text`, `preview_label`, `preview_pill`, `staged_label`,
`staged_scope`, `col_term`, `col_keyword`, `col_match`, `col_spend`, `match_phrase`, `match_exact`,
`pending_status`, `applied_status`, `remove_label`, `apply_label`, `apply_label_one`, `applying_label`,
`applied_label`, `done_title`, `done_text`, `term`, `keyword`, `animation_alt`.

Plus the general-purpose ones a scene caption or heading needs: `heading`, `subheading`, `subtext`,
`feature_title`, `question`, `answer`, `anchor_text`, `link_text`, `title`, `description`, `label`,
`caption`, `note`, `step`, `steps`, `item`, `items`, `point`, `points`.

**Careful — these are skip-keys and must never hold visible copy:** `value`, `price`, `figure`, `spend`,
`match`, `uncheck`, `currency_prefix`, `product_type`, `status_color`, `table_style`, `default_open`.
The connector scene deliberately puts its numbers in `spend` and its row flags in `uncheck` so they are
**not** translated; the skill should follow that split — words translate, data does not.

If a scene genuinely needs a new translatable field name, that is a **dev-team configuration change** to
`config.js`. Flag it in the handoff; never edit that file.

## 4. How translations are produced

| Question | Answer | Source | Status |
|---|---|---|---|
| Who produces translations? | The **Marketing-OS localization agent** (`.claude/agents/mktos-localization.md`), run right after the English change and **before** QA review, so the reviewer sees the full multilingual change | `.claude/agents/mktos-localization.md` | verified |
| Supporting scripts | `scripts/translate.js`, `translate-data.js`, `translate-toml.js`, `gen-retranslate-list.js`, `retranslate-missing-links.js` | `scripts/` | verified |
| Parity check | `node scripts/validateTranslations.js` (plus `validateTranslationsAI.js`); an eval check exists at `evals/checks/locale-parity.sh` | `scripts/`, `evals/` | verified |
| Per-language tone | Spanish informal (tú, es-419 LATAM, sentence case); German formal (Sie, de-DE, noun capitalization); French formal (vous, NBSP before `: ; ! ?`); Japanese polite です／ます, never あなた | `.claude/agents/mktos-localization.md` | verified |
| Terms never translated | Hugo shortcodes `{{< … >}}`, template expressions `{{ … }}`, code, data URIs, and Optmyzr product/feature names | `.claude/agents/mktos-localization.md` | verified |

**Rule for this skill: hand over English source only.** Do not write `content/es|de|fr|jp` files. The
dev team's agent produces them and the parity validator checks them.

## 5. Language switching, URLs and SEO

| Question | Answer | Source | Status |
|---|---|---|---|
| Language switcher | Bookshop component **`language-picker`**, Alpine-driven (`x-data="languagePicker()"`), used in both header and footer (`isFooter` flag, `dropdown_direction` up/down). Reads `site.Data.languages.languages` | `component-library/components/language-picker/`, `data/languages.yaml` | verified |
| Missing-translation behaviour | Each language carries a `fallbackMessage` in `data/languages.yaml`, surfaced by `layouts/partials/scripts/lang-fallback-toast.html`; a visitor preference script exists at `static/websitejs/lang-pref.js` | `data/languages.yaml`, theme partials | verified |
| URL shape | English at root, others prefixed `/es/`, `/de/`, `/fr/`, `/jp/`. `canonifyURLs = true`, `relativeURLs = false`. Page `url:` front matter sets the path, e.g. `url: /solutions/monitoring/` | `config/_default/hugo.toml`, content files | verified |
| hreflang | Generated by `layouts/partials/hreflang.html` from `.AllTranslations`, using each language's `languageCode`, plus an always-emitted `x-default` preferring the default language. **Never hand-write hreflang or canonical tags** | `themes/.../partials/hreflang.html` | verified |
| Metadata fields | `title`, `description`, `ogTitle`, `ogDescription`, `ogImage`, `ogUrl`, `ogType`, `serpTitle`, `serpDescription`, `keywords`, `sitemap.priority` — the text ones are all in `translatableKeys`, `ogImage`/`ogUrl` are not | content front matter, `config.js` | verified |
| Navigation and chrome | Per-language **data files**, not i18n keys: `data/<lang>/navbar/`, `data/<lang>/footer/`, `data/<lang>/links.yaml`, `data/<lang>/language.yml` | `data/` | verified |
| CMS editing | CloudCannon collections point at **English only**; no collection targets `content/es|de|fr|jp`. Marketers edit English, the pipeline does the rest | `.cloudcannon/schemas/slack-sidekick-template.md`, `cloudcannon.config.yml` | verified |
| Fonts / script coverage | Japanese is active, so CJK coverage is required. Font files under `static/websitefonts/` | `static/websitefonts/` | **observed — coverage per weight not yet checked** |
| Right-to-left | **No.** No RTL language is configured | `config/_default/hugo.toml` | verified |

## 6. What this means for a generated page

1. Write **English source only**, as YAML front matter under `content/english/<section>/<page>.md`, with
   `content_blocks` entries carrying `_bookshop_name`.
2. Name every field from `translatableKeys`. Put numbers, ids, image paths and state flags in `skipKeys`
   names so they are left alone.
3. Put small chrome labels in `i18n/en.toml` only if a template needs them outside component fields;
   component copy belongs in the component's own fields.
4. Internal links go in `urlReplaceKeys` fields (`url`, `link`, `anchor_url`, `cta_url`, …) as ordinary
   site-relative paths so the pipeline can prefix them.
5. Never add a language switcher, never write other-language files, never hand-write hreflang.
6. Check layout in **German** (longest) and **Japanese** (CJK line breaking, different glyph widths)
   before handoff.

## Preview-only language switching (verified, 2026-09-30)

The site's language picker dispatches an Alpine event on every selection:

```js
this.$dispatch("language-changed", { code: n, label: s })
```

It bubbles, so a listener on `document` receives it. That is the whole hook a preview
needs to switch language **in place** rather than navigating to a URL that does not exist
yet. Build it from three pieces:

1. **`data-i18n="key"` on every translatable element.** The key must sit on the element
   whose *entire* text is the string. Assign keys by matching the source strings the
   content module already holds, so nothing is written twice, and fail the build on any
   key whose string is not found — a copy edit must not silently drop a key.
2. **`window.__pvI18n = { de: {...}, jp: {...} }`**, with product-UI strings nested under
   `sc` and addressed as `sc.<name>`.
3. **An apply function** on `language-changed` that swaps `textContent`, restores the
   captured English on `en`, sets `<html lang>` (`jp` → `ja`), stubs
   `window.showLangFallbackToast` to a no-op (the site's "no translation" toast must not
   also fire), and logs a console notice that the copy is drafted.

Two traps:

- **A leftover fallback map looks like it works.** A captured header may still carry
  `showLangFallbackToast` with URLs from the page it was copied from. Clicking a language
  then opens a real translated page — of a *different* product — in a new tab. It is
  convincing and completely wrong. Replace the map; never leave it pointing elsewhere.
- **`>TEXT<` can match a closing tag.** Inserting the attribute after that `>` yields
  `</span data-i18n="...">`, which breaks the element with no error. Only tag when the
  nearest preceding `<` starts an opening tag, and run `scripts/check_markup.py`
  afterwards.

Languages with no pack should say so in the UI rather than doing nothing, and the drafted
packs are **preview-only**: strip the pack script from the bundle's preview copy so the
handoff stays English source. Keep the `data-i18n` keys — they are the string ids the
site's own pipeline would key against.
