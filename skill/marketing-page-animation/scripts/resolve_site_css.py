#!/usr/bin/env python3
"""Resolve the site's current generated stylesheet URL, and cache it in the kit.

The site serves one Tailwind file whose name carries a content hash
(websitecss/styles.min.<hash>.css). The hash changes on every deploy, so a URL
hardcoded in a page generator silently unstyles every preview built before that
deploy. Resolve it at build time instead.

  resolve_site_css.py [--site URL] [--kit DIR] [--print] [--max-age-days N]

Reads the site's homepage, extracts the stylesheet URL, and writes it to
<kit>/captured/site-css.json with the time it was seen. With no network, falls
back to the cached value and says so, so an offline build still works.

Exit codes: 0 resolved (fresh or cache still current), 1 cache used or stale, 2 error.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PATTERN = re.compile(r'websitecss/styles\.min\.[a-f0-9]{8,}\.css')
DEFAULT_SITE = "https://www.optmyzr.com"
UA = "marketing-page-animation/kit-refresh"


def fetch(site, timeout):
    req = urllib.request.Request(site, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default=DEFAULT_SITE, help=f"site root (default {DEFAULT_SITE})")
    ap.add_argument("--kit", default=None, help="site-kit directory (default: the kit next to this script)")
    ap.add_argument("--print", dest="show", action="store_true", help="print only the URL, nothing else")
    ap.add_argument("--max-age-days", type=int, default=14, help="warn when the cache is older than this (default 14)")
    ap.add_argument("--timeout", type=float, default=10.0)
    args = ap.parse_args()

    kit = Path(args.kit) if args.kit else Path(__file__).resolve().parent.parent / "site-kit"
    cache_path = kit / "captured" / "site-css.json"
    cached = None
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text())
        except (json.JSONDecodeError, OSError):
            cached = None

    try:
        html = fetch(args.site, args.timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        if not cached:
            print(f"error: cannot reach {args.site} ({e}) and no cached stylesheet in {cache_path}", file=sys.stderr)
            return 2
        url = cached["url"]
        if args.show:
            print(url)
        else:
            print(f"offline: using cached stylesheet from {cached.get('seen', 'unknown time')}")
            print(url)
        return 1

    m = PATTERN.search(html)
    if not m:
        if cached:
            if args.show:
                print(cached["url"])
            else:
                print(f"warning: no stylesheet link found at {args.site}; using cache", file=sys.stderr)
                print(cached["url"])
            return 1
        print(f"error: no stylesheet matching {PATTERN.pattern} at {args.site}", file=sys.stderr)
        return 2

    url = f"{args.site.rstrip('/')}/{m.group(0)}"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    changed = bool(cached) and cached.get("url") != url

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({
        "url": url,
        "seen": now,
        "site": args.site,
        "note": "Generated Tailwind stylesheet. The hash changes on every deploy; never hardcode this URL in a page generator. Re-run scripts/resolve_site_css.py before each build.",
        "previous": cached.get("url") if changed else (cached or {}).get("previous"),
    }, indent=1) + "\n")

    if args.show:
        print(url)
        return 0

    if changed:
        print("the site has deployed since the last build: stylesheet hash changed")
        print(f"  was: {cached['url'].rsplit('/', 1)[-1]}")
        print(f"  now: {url.rsplit('/', 1)[-1]}")
        print("Previews built before now are unstyled. Rebuild them.")
    else:
        print("stylesheet unchanged" if cached else "stylesheet cached for the first time")
    print(url)

    if cached and cached.get("seen"):
        try:
            seen = datetime.fromisoformat(cached["seen"])
            if datetime.now(timezone.utc) - seen > timedelta(days=args.max_age_days):
                print(f"note: previous check was {(datetime.now(timezone.utc) - seen).days} days ago", file=sys.stderr)
        except ValueError:
            pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
