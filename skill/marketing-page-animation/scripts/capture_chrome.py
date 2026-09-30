#!/usr/bin/env python3
"""Capture the site's real header and footer into the kit, verbatim.

Mode A users have no repo and no Hugo, so the kit must carry the *rendered*
chrome, not a hand-simplified copy: mega menu, product switcher, mobile menu,
language picker and promo banner included. The live site is the rendered
authority, so read it from there.

  capture_chrome.py [--page URL] [--kit DIR] [--keep-scripts]

Writes <kit>/captured/: header.html, footer.html, banner.html (when a promo
banner is running), chrome-meta.json and the head links the chrome needs.
Relative URLs are made absolute so the preview loads the same assets.

Exit codes: 0 ok, 1 a part was not found, 2 error.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PAGE = "https://www.optmyzr.com/solutions/monitoring/"
UA = "marketing-page-animation/kit-refresh"
# Attribute values may be unquoted in the minified output, so match both forms.
ATTR = re.compile(r'\b(href|src|srcset|data-src|poster)=("([^"]*)"|\'([^\']*)\'|([^\s>]+))', re.I)


def absolutise(html, origin):
    def fix_one(url):
        u = url.strip()
        if not u or u.startswith(("http://", "https://", "//", "data:", "#", "mailto:", "tel:", "javascript:")):
            return url
        if u.startswith("/"):
            return origin + u
        return url

    def repl(m):
        attr, raw = m.group(1), m.group(2)
        quote = '"' if raw.startswith('"') else ("'" if raw.startswith("'") else "")
        val = m.group(3) if quote == '"' else (m.group(4) if quote == "'" else m.group(5))
        if attr.lower() == "srcset":
            parts = []
            for chunk in val.split(","):
                bits = chunk.strip().split(None, 1)
                if not bits:
                    continue
                parts.append(" ".join([fix_one(bits[0])] + bits[1:]))
            new = ", ".join(parts)
        else:
            new = fix_one(val)
        return f'{attr}={quote}{new}{quote}' if quote else f'{attr}={new}'

    return ATTR.sub(repl, html)


# Asset paths inside the chrome's inline scripts (menu icons, images) are JS string
# literals, not HTML attributes, so the attribute rewriter never sees them and every
# mega-menu icon 404s in a preview. Rewrite those separately.
JS_ASSET = re.compile(r'(["\'])(/(?:images|forestry|websitejs|websitecss|websitefonts|static)/[^"\']*)\1')


def absolutise_js(code, origin):
    return JS_ASSET.sub(lambda m: f"{m.group(1)}{origin}{m.group(2)}{m.group(1)}", code)


def extract(html, tag, class_hint=None):
    """Return the full element for the first <tag> (optionally matching a class), balanced."""
    for m in re.finditer(rf'<{tag}\b[^>]*>', html):
        if class_hint and class_hint not in m.group(0):
            continue
        start = m.start()
        depth, pos = 0, start
        token = re.compile(rf'</?{tag}\b', re.I)
        while True:
            t = token.search(html, pos)
            if not t:
                return None
            if html[t.start():t.start() + 2 + len(tag)].lower().startswith(f"</{tag}"):
                depth -= 1
                if depth == 0:
                    end = html.find(">", t.start())
                    return html[start:end + 1]
            else:
                depth += 1
            pos = t.end()
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", default=DEFAULT_PAGE, help=f"page to read the chrome from (default {DEFAULT_PAGE})")
    ap.add_argument("--kit", default=None)
    ap.add_argument("--keep-scripts", action="store_true",
                    help="keep <script> tags inside the chrome (default: keep them; this flag is retained for clarity)")
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args()

    kit = Path(args.kit) if args.kit else Path(__file__).resolve().parent.parent / "site-kit"
    out = kit / "captured"
    out.mkdir(parents=True, exist_ok=True)

    m = re.match(r"(https?://[^/]+)", args.page)
    if not m:
        print(f"error: --page must be an absolute URL, got {args.page}", file=sys.stderr)
        return 2
    origin = m.group(1)

    try:
        req = urllib.request.Request(args.page, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=args.timeout) as r:
            html = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"error: cannot read {args.page} ({e})", file=sys.stderr)
        return 2

    meta = {"page": args.page, "origin": origin,
            "captured": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "note": "Rendered chrome copied verbatim from the live site. Refresh with scripts/capture_chrome.py.",
            "parts": {}}
    missing = False

    for name, tag, hint in (("header", "header", "header"), ("footer", "footer", "footer")):
        el = extract(html, tag, hint)
        if not el:
            print(f"warning: no <{tag}> found on {args.page}", file=sys.stderr)
            missing = True
            continue
        el = absolutise(el, origin)
        (out / f"{name}.html").write_text(el + "\n")
        meta["parts"][name] = {"bytes": len(el),
                               "hasAlpine": "x-data" in el,
                               "hasLanguagePicker": "language-picker" in el or "languagePicker" in el,
                               "hasMobileMenu": bool(re.search(r'mobile|hamburger|lg:hidden', el, re.I))}
        print(f"captured {name}.html ({len(el):,} bytes)")

    # The mega-menu overlay is a sibling of <header>, not a child, so extracting the
    # header alone leaves the script with a null element and no menu ever opens.
    extras = []
    for m in re.finditer(r'<div[^>]*class=["\']?[^"\'>]*\boverlay\b[^>]*>\s*</div>', html):
        extras.append(m.group(0))
    if extras:
        (out / "chrome-extras.html").write_text(absolutise("\n".join(extras), origin) + "\n")
        meta["parts"]["extras"] = {"count": len(extras)}
        print(f"captured chrome-extras.html ({len(extras)} sibling element(s) the chrome scripts need)")
    else:
        meta["parts"]["extras"] = None

    banner = None
    for pat in (r'<div[^>]*id=["\']?bfcm-banner', r'<div[^>]*class=["\'][^"\']*promo-banner'):
        bm = re.search(pat, html)
        if bm:
            banner = extract(html[bm.start():], "div")
            break
    if banner:
        (out / "banner.html").write_text(absolutise(banner, origin) + "\n")
        meta["parts"]["banner"] = {"bytes": len(banner)}
        print(f"captured banner.html ({len(banner):,} bytes)")
    else:
        meta["parts"]["banner"] = None
        print("no promo banner running on this page (that is normal)")

    # Render-critical resources only. A preview must never load the company's
    # analytics, error tracking or chat widgets: it would send real telemetry from
    # a page no visitor asked for, and pollute the site's own metrics.
    TRACKING = ("pagesense", "sentry", "partytown", "googletagmanager", "gtag", "google-analytics",
                "hotjar", "segment", "intercom", "meetvolley", "clarity", "facebook", "linkedin",
                "doubleclick", "hubspot", "drift", "qualified")
    head = re.search(r"<head\b[^>]*>(.*?)</head>", html, re.S | re.I)
    kept, dropped = [], []
    if head:
        for link in re.findall(r'<link\b[^>]*rel=["\']?stylesheet[^>]*>', head.group(1), re.I):
            kept.append(link)
        for s in re.findall(r'<script\b[^>]*src=[^>]*>\s*</script>', head.group(1), re.I):
            (dropped if any(t in s.lower() for t in TRACKING) else kept).append(s)

    # Alpine drives the header menus and the language picker, but the site loads it
    # from an inline loader on first interaction, so it is not a plain <script src>.
    am = re.search(r'src=["\']?(\S*?/websitejs/alpine[^"\'\s,)]+\.js)', html)
    if am:
        kept.append(f'<script src="{am.group(1)}" defer></script>')

    # Subresource integrity is same-origin on the live site. A preview loads these
    # cross-origin (file://, data:, or a preview host), where an integrity-checked
    # resource is blocked unless the server sends CORS headers - which silently
    # unstyles the whole page. Drop the attribute for the kit copy.
    kept = [re.sub(r'\s+integrity=("[^"]*"|\'[^\']*\'|[^\s>]+)', '', k) for k in kept]
    (out / "head-links.html").write_text(absolutise("\n".join(kept), origin) + "\n")
    if dropped:
        (out / "head-links.excluded.html").write_text("\n".join(
            ["<!-- Deliberately NOT loaded in previews: analytics, error tracking and chat widgets.",
             "     A preview is not a visit; loading these would send real telemetry. -->"] + dropped) + "\n")
    meta["parts"]["headLinks"] = {"kept": len(kept), "excludedTracking": len(dropped),
                                  "alpineFound": bool(am)}
    print(f"captured head-links.html ({len(kept)} render-critical, {len(dropped)} tracking excluded"
          + (", alpine included" if am else ", ALPINE NOT FOUND - header menus will not open") + ")")

    # The chrome's Alpine expressions (menuData, getCompanyData, getMobileMenuData,
    # languagePicker, ...) are defined in INLINE scripts elsewhere in the page. Without
    # them the markup renders but every menu throws ReferenceError and will not open.
    chrome_html = ""
    for name in ("header", "footer", "banner"):
        f = out / f"{name}.html"
        if f.exists():
            chrome_html += f.read_text()
    idents = set()
    # The live HTML is minified, so Alpine attribute values are often UNQUOTED
    # (x-data=getMobileMenuData()). Match quoted and unquoted forms, or the scan
    # silently finds nothing and every menu ships broken.
    ALPINE = (r'(?:x-data|x-show|x-text|x-init|x-if|x-on:[\w.]+|@[\w.]+|:[\w-]+)='
              r'("[^"]*"|\'[^\']*\'|[^\s>]+)')
    for attr in re.findall(ALPINE, chrome_html):
        idents |= set(re.findall(r'\b([a-zA-Z_$][a-zA-Z0-9_$]{3,})\s*\(', attr))
        idents |= set(re.findall(r'\b([a-zA-Z_$][a-zA-Z0-9_$]{3,})\b', attr))
    NOISE = {"true", "false", "null", "this", "window", "document", "function", "return",
             "class", "style", "length", "value", "event", "index", "item", "open", "close"}
    idents -= NOISE

    # Hooks the chrome's non-Alpine scripts query by: every id in the chrome, plus the
    # class names the mega-menu script uses. Without these the markup renders and the
    # desktop dropdowns never open, with no error to explain why.
    hooks = set(re.findall(r'\bid=["\']?([A-Za-z][\w-]{2,})', chrome_html))
    hooks |= {"nav-link", "popover", "overlay", "data-nav"}

    INLINE_TRACKING = ("googletagmanager.com", "google-analytics.com", "pagesense",
                       "sentry-cdn", "browser.sentry", "partytown", "hotjar.com",
                       "cdn.segment.com", "widget.intercom", "clarity.ms",
                       "connect.facebook.net", "snap.licdn.com", "doubleclick.net",
                       "js.hs-scripts.com", "js.driftt.com", "qualified.com")
    inline = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>.*?</script>', html, re.S)
    wanted, seen = [], set()
    for block in inline:
        if any(tk in block.lower() for tk in INLINE_TRACKING):
            continue
        defines = [i for i in idents
                   if re.search(rf'(?:function\s+{re.escape(i)}\b|\b{re.escape(i)}\s*[:=]\s*(?:function|\(|async))', block)]
        uses = [h for h in hooks if f'"{h}"' in block or f"'{h}'" in block or f".{h}" in block or f"#{h}" in block]
        if (defines or len(uses) >= 2) and block not in seen:
            defines = defines or [f"drives: {', '.join(sorted(uses)[:4])}"]
            seen.add(block)
            wanted.append((sorted(defines), block))
    if wanted:
        parts = ["<!-- Inline scripts the captured header/footer depend on, copied from the live page.",
                 "     Without these the menus render but throw ReferenceError and never open. -->"]
        for defines, block in wanted:
            parts.append(f"<!-- defines: {', '.join(defines)} -->")
            parts.append(absolutise_js(absolutise(block, origin), origin))
        (out / "chrome-scripts.html").write_text("\n".join(parts) + "\n")
        meta["parts"]["chromeScripts"] = {"blocks": len(wanted),
                                          "defines": sorted({d for ds, _ in wanted for d in ds})}
        print(f"captured chrome-scripts.html ({len(wanted)} inline block(s), "
              f"defining {', '.join(sorted({d for ds, _ in wanted for d in ds})[:6])}...)")
    else:
        meta["parts"]["chromeScripts"] = None
        print("warning: no inline chrome scripts found; menus may not open in the preview", file=sys.stderr)

    (out / "chrome-meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    return 1 if missing else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
