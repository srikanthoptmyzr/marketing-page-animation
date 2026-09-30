#!/usr/bin/env python3
"""Check every CSS class in a built page against the site's real stylesheet.

The site ships one generated Tailwind file, purged to the classes its own templates
use. A class the site has never used is NOT in that file, so markup written with it
renders **unstyled and without any error**. `gap-8` exists; `gap-16` does not.
`rounded-[12px]` exists; `rounded-[20px]` does not. Arbitrary values only exist when
that exact value is already used somewhere.

That makes this check the difference between "designed a new section" and "shipped a
broken one". Run it on every page before review, and always after designing a section
that is not a straight copy of an existing component.

  check_classes.py PAGE.html [PAGE2.html ...] [--css URL|FILE] [--ignore PREFIX ...]

With no --css it reads the URL cached in site-kit/captured/site-css.json, refreshing
it from the live site when possible.

Classes the page defines itself (in an inline <style> or a local stylesheet) are not
misses: pass their prefixes with --ignore, e.g. `--ignore pu- ozcl-`.

Exit codes: 0 every class resolves, 1 at least one missing, 2 usage error.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# A real class attribute only. The lookbehind rejects Alpine/Vue bindings (:class, x-bind:class),
# whose values are JS expressions, not class lists.
CLASS_ATTR = re.compile(r'(?<![-:.\w])class\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', re.I)

# Class names that are structural hooks rather than styled utilities: Bookshop component roots
# and landmark names. They are expected to have no rules of their own.
SEMANTIC = re.compile(r'^(c-[a-z0-9-]+|header|footer|main|nav|section-[a-z-]+)$')
# Tailwind escapes these in the generated selector
ESCAPE = set('[]:/.%!#(),<>+*~=\'"&')


def selector_for(cls):
    return '.' + ''.join('\\' + c if c in ESCAPE else c for c in cls)


def load_css(arg, kit):
    if arg and not arg.startswith("http"):
        return Path(arg).read_text(encoding="utf-8", errors="replace"), arg
    url = arg
    if not url:
        cache = kit / "captured" / "site-css.json"
        if not cache.exists():
            print(f"error: no --css given and no cache at {cache}", file=sys.stderr)
            return None, None
        url = json.loads(cache.read_text()).get("url")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "marketing-page-animation/class-check"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", "replace"), url
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"error: cannot fetch the stylesheet ({e})", file=sys.stderr)
        return None, None


def classes_in(html):
    out = {}
    for m in CLASS_ATTR.finditer(html):
        raw = m.group(1) or m.group(2) or m.group(3) or ""
        # a template or JS expression, not a literal class list
        if any(ch in raw for ch in "{}()"):
            continue
        for c in raw.split():
            if c and not c.startswith("{"):
                out.setdefault(c, 0)
                out[c] += 1
    return out


def local_style_classes(html):
    """Classes the page defines for itself, inline or in a <style> block."""
    found = set()
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.S | re.I):
        found |= set(re.findall(r"\.([A-Za-z_][\w-]*)", m.group(1)))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="+")
    ap.add_argument("--css", help="stylesheet URL or local file (default: the kit's cached URL)")
    ap.add_argument("--kit", default=None)
    ap.add_argument("--ignore", nargs="*", default=[], help="class prefixes the page styles itself")
    ap.add_argument("--live", nargs="*", default=[], metavar="URL|FILE",
                    help="live pages to compare against. A class the real site also uses is a JS "
                         "hook or inline-styled, not your bug, and is reported separately")
    ap.add_argument("--quiet", action="store_true", help="only print misses")
    args = ap.parse_args()

    kit = Path(args.kit) if args.kit else Path(__file__).resolve().parent.parent / "site-kit"
    css, src = load_css(args.css, kit)
    if css is None:
        return 2
    if not args.quiet:
        print(f"stylesheet: {src}  ({len(css):,} bytes)")

    live = ""
    for ref in args.live:
        try:
            if ref.startswith("http"):
                r = urllib.request.Request(ref, headers={"User-Agent": "marketing-page-animation"})
                live += urllib.request.urlopen(r, timeout=20).read().decode("utf-8", "replace")
            else:
                live += Path(ref).read_text(encoding="utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            print(f"warning: could not read {ref} ({e})", file=sys.stderr)
    if live and not args.quiet:
        print(f"live corpus: {len(live):,} bytes from {len(args.live)} page(s)")

    total_missing = 0
    for p in args.pages:
        path = Path(p)
        if not path.exists():
            print(f"error: no such file: {p}", file=sys.stderr)
            return 2
        html = path.read_text(encoding="utf-8", errors="replace")
        own = local_style_classes(html)
        used = classes_in(html)
        missing, semantic, on_site = {}, [], {}
        for c, n in used.items():
            if c in own or any(c.startswith(pre) for pre in args.ignore):
                continue
            if selector_for(c) in css:
                continue
            if SEMANTIC.match(c):
                semantic.append(c)          # a hook, not a style. Expected.
                continue
            if live and c in live:
                on_site[c] = n              # the site uses it too: JS hook or inline-styled
                continue
            missing[c] = n
        if not args.quiet:
            print(f"\n{p}: {len(used)} distinct classes, {len(missing)} not in the stylesheet"
                  f" ({len(semantic)} semantic hooks ignored)")
        if on_site and not args.quiet:
            print(f"  {len(on_site)} class(es) absent from the stylesheet but used by the live site")
            print("  (JS hooks or inline-styled — not invented here): "
                  + ", ".join(sorted(on_site)))
        if missing:
            total_missing += len(missing)
            print(f"  MISSING from {p} — not in the stylesheet and not used by the live site:")
            for c, n in sorted(missing.items(), key=lambda kv: -kv[1]):
                print(f"    {c}   (used {n}x)")

    if total_missing:
        print(f"\n{total_missing} class(es) are absent from the site's stylesheet.")
        print("The site's CSS is purged: a class it has never used does not exist. Either reuse a")
        print("class the site already has, or move the styling into the component's own stylesheet")
        print("(references/new-sections.md). Do not ship markup that depends on a purged class.")
        return 1
    if not args.quiet:
        print("\nevery class resolves against the site stylesheet")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
