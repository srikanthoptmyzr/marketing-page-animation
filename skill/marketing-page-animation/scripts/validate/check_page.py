#!/usr/bin/env python3
"""Headless-browser checks for a built page (needs Playwright + Chromium).

Usage:
  check_page.py URL_OR_FILE [--viewports 320,390,768,1024,1440,1920]
                [--reduced-motion] [--out DIR] [--lang CODE]
                [--budget-bytes 1048576] [--wait MS]

Per viewport
  horizontal-scroll   document.scrollingElement.scrollWidth <= innerWidth
  console             console errors, uncaught page errors, failed requests
  img-alt             <img> without an alt attribute (alt="" is decorative and allowed)
  text-overflow       text elements whose box leaves their parent's box, or whose
                      own content is clipped by overflow:hidden/clip
  font-size           visible text whose rendered size (computed size x visible
                      transform scale) is under 11 px
  page-weight         sum of response body bytes vs --budget-bytes (default 1 MiB)
  html-lang           <html lang> present (and matching --lang if given)
With --reduced-motion the browser emulates prefers-reduced-motion: reduce for the
whole run, and every [data-scene] must have data-state equal to its
data-final-state after load.

A JSON summary is printed to stdout. Screenshots (full page) go to --out.

Exit codes: 0 all checks pass, 1 at least one check failed, 2 usage error,
missing Playwright/Chromium, or the page could not be opened.
"""
import argparse
import json
import os
import sys
import urllib.parse

MIN_FONT_PX = 11

PAGE_JS = r"""
(minFont) => {
  const out = {scrollWidth: 0, innerWidth: window.innerWidth, imgs: [], overflow: [], small: [], scenes: [],
               lang: document.documentElement.getAttribute('lang')};
  const se = document.scrollingElement || document.documentElement;
  out.scrollWidth = se.scrollWidth;
  const describe = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    else if (el.classList.length) s += '.' + Array.from(el.classList).slice(0, 2).join('.');
    return s;
  };
  document.querySelectorAll('img').forEach(img => {
    if (!img.hasAttribute('alt')) out.imgs.push({el: describe(img)});
  });
  const skip = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'HEAD', 'TITLE', 'META', 'LINK', 'OPTION']);
  const visible = (el, cs, r) => cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0
                                  && r.width > 0 && r.height > 0;
  const all = document.body ? document.body.querySelectorAll('*') : [];
  for (const el of all) {
    if (skip.has(el.tagName) || el.closest('svg')) continue;
    let own = '';
    for (const n of el.childNodes) if (n.nodeType === 3) own += n.textContent;
    own = own.trim();
    if (!own) continue;
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if (!visible(el, cs, r)) continue;
    // font size (account for transform scale)
    let fs = parseFloat(cs.fontSize);
    if (el.offsetWidth > 0) {
      const ratio = r.width / el.offsetWidth;
      if (ratio > 0.05 && ratio <= 1.5) fs = fs * ratio;
    }
    if (fs < minFont - 0.01) out.small.push({el: describe(el), px: Math.round(fs * 10) / 10, chars: own.length});
    // overflow vs parent
    const p = el.parentElement;
    if (p && p !== document.body && p !== document.documentElement && cs.position !== 'absolute' && cs.position !== 'fixed') {
      const pcs = getComputedStyle(p);
      if (pcs.display !== 'contents') {
        const pr = p.getBoundingClientRect();
        const clips = pcs.overflowX !== 'visible' || pcs.overflowY !== 'visible';
        const tol = 1.5;
        const dirs = [];
        if (r.right > pr.right + tol) dirs.push('right');
        if (r.left < pr.left - tol) dirs.push('left');
        if (r.bottom > pr.bottom + tol) dirs.push('bottom');
        if (r.top < pr.top - tol) dirs.push('top');
        if (dirs.length) out.overflow.push({el: describe(el), parent: describe(p), dirs, clipped: clips, kind: 'outside-parent'});
      }
    }
    const clipX = cs.overflowX === 'hidden' || cs.overflowX === 'clip';
    if (clipX && !el.closest('.pu-sr-only') && el.scrollWidth > el.clientWidth + 1 && cs.textOverflow !== 'ellipsis' && el.clientWidth > 0) {
      out.overflow.push({el: describe(el), parent: '-', dirs: ['right'], clipped: true, kind: 'text-clipped'});
    }
  }
  document.querySelectorAll('[data-scene]').forEach(s => {
    out.scenes.push({el: describe(s), scene: s.getAttribute('data-scene'), state: s.getAttribute('data-state'),
                     final: s.getAttribute('data-final-state')});
  });
  return out;
}
"""


def to_url(target):
    if "://" in target:
        return target
    path = os.path.abspath(target)
    if os.path.isdir(path):
        path = os.path.join(path, "index.html")
    if not os.path.exists(path):
        return None
    return "file://" + urllib.parse.quote(path)


def parse_viewports(s):
    try:
        vs = [int(x) for x in s.split(",") if x.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError("viewports must be comma-separated integers")
    if not vs or any(v < 200 or v > 10000 for v in vs):
        raise argparse.ArgumentTypeError("viewport widths must be between 200 and 10000")
    return vs


def build_parser():
    p = argparse.ArgumentParser(
        description="Headless Chromium checks: overflow, console, alt, clipping, font size, weight, reduced motion.",
        epilog="Exit codes: 0 pass, 1 checks failed, 2 usage/environment error (e.g. Playwright missing).")
    p.add_argument("target", help="URL or path to an HTML file (or a directory containing index.html)")
    p.add_argument("--viewports", type=parse_viewports, default=parse_viewports("320,390,768,1024,1440,1920"),
                   help="comma-separated widths (default 320,390,768,1024,1440,1920)")
    p.add_argument("--reduced-motion", action="store_true",
                   help="emulate prefers-reduced-motion and check [data-scene] final states")
    p.add_argument("--out", metavar="DIR", help="write full-page screenshots here")
    p.add_argument("--lang", metavar="CODE", help="browser locale (e.g. de) and expected <html lang> prefix")
    p.add_argument("--budget-bytes", type=int, default=1048576, help="page weight budget (default 1048576)")
    p.add_argument("--wait", type=int, default=400, metavar="MS", help="settle time after load (default 400)")
    p.add_argument("--height", type=int, default=900, help="viewport height (default 900)")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("error: Playwright is not importable. Install it with 'pip install playwright' and make sure a "
              "Chromium build is available (PLAYWRIGHT_BROWSERS_PATH); this script never runs 'playwright install'.",
              file=sys.stderr)
        return 2
    url = to_url(a.target)
    if url is None:
        print("error: file not found: %s" % a.target, file=sys.stderr)
        return 2
    if a.out:
        os.makedirs(a.out, exist_ok=True)

    summary = {"target": a.target, "reducedMotion": a.reduced_motion, "budgetBytes": a.budget_bytes,
               "viewports": [], "failures": []}

    def fail(vp, check, msg, **extra):
        d = {"viewport": vp, "check": check, "message": msg}
        d.update(extra)
        summary["failures"].append(d)

    try:
        pw_cm = sync_playwright().start()
    except Exception as e:  # noqa: BLE001
        print("error: could not start Playwright: %s" % e, file=sys.stderr)
        return 2
    try:
        try:
            browser = pw_cm.chromium.launch()
        except Exception as e:  # noqa: BLE001
            print("error: could not launch Chromium (%s). Check PLAYWRIGHT_BROWSERS_PATH; "
                  "this script does not install browsers." % str(e).splitlines()[0], file=sys.stderr)
            return 2
        for w in a.viewports:
            ctx_args = {"viewport": {"width": w, "height": a.height},
                        "reduced_motion": "reduce" if a.reduced_motion else "no-preference"}
            if a.lang:
                ctx_args["locale"] = a.lang
            ctx = browser.new_context(**ctx_args)
            page = ctx.new_page()
            console, sizes = [], {}
            page.on("console", lambda m: console.append(("console." + m.type, m.text[:300])) if m.type == "error" else None)
            page.on("pageerror", lambda e: console.append(("pageerror", str(e)[:300])))
            page.on("requestfailed", lambda r: console.append(("requestfailed", "%s (%s)" % (r.url[:200], r.failure))))

            def on_resp(resp):
                try:
                    sizes[resp.url] = len(resp.body())
                except Exception:  # noqa: BLE001
                    sizes.setdefault(resp.url, 0)
            page.on("response", on_resp)
            try:
                resp = page.goto(url, wait_until="load", timeout=30000)
            except Exception as e:  # noqa: BLE001
                print("error: could not open %s: %s" % (a.target, str(e).splitlines()[0]), file=sys.stderr)
                browser.close()
                return 2
            page.wait_for_timeout(a.wait)
            data = page.evaluate(PAGE_JS, MIN_FONT_PX)
            vp_res = {"width": w}

            # horizontal scroll
            vp_res["scrollWidth"] = data["scrollWidth"]
            if data["scrollWidth"] > data["innerWidth"]:
                fail(w, "horizontal-scroll", "scrollWidth %d > innerWidth %d" % (data["scrollWidth"], data["innerWidth"]))
            # console
            errs = [(k, m) for k, m in console if "favicon" not in m.lower()]
            vp_res["consoleErrors"] = len(errs)
            for k, m in errs[:10]:
                fail(w, "console", "%s: %s" % (k, m))
            # alt
            vp_res["imagesWithoutAlt"] = len(data["imgs"])
            for i in data["imgs"][:10]:
                fail(w, "img-alt", "<img> without alt attribute", element=i["el"])
            # overflow
            bad = [o for o in data["overflow"]]
            vp_res["overflowingText"] = len(bad)
            for o in bad[:15]:
                fail(w, "text-overflow", "%s %s (parent %s) %s" % (
                    o["el"], o["kind"], o["parent"], "clipped" if o["clipped"] else "spills"),
                    element=o["el"], directions=o["dirs"])
            # font size
            vp_res["smallText"] = len(data["small"])
            for s in data["small"][:15]:
                fail(w, "font-size", "%s renders at %spx (< %d)" % (s["el"], s["px"], MIN_FONT_PX), element=s["el"])
            # html lang
            lang = data["lang"]
            if not lang:
                fail(w, "html-lang", "<html> has no lang attribute")
            elif a.lang and not lang.lower().startswith(a.lang.lower().split("-")[0]):
                fail(w, "html-lang", "<html lang> is '%s', expected '%s'" % (lang, a.lang))
            # weight
            total = sum(sizes.values())
            if total == 0:  # file:// responses may not report bodies; fall back to resource timing + document
                try:
                    total = page.evaluate(
                        "() => performance.getEntriesByType('resource').reduce((s,e)=>s+(e.encodedBodySize||e.decodedBodySize||0),0)")
                    if url.startswith("file://"):
                        total += os.path.getsize(urllib.parse.unquote(url[7:]))
                except Exception:  # noqa: BLE001
                    pass
            vp_res["bytes"] = total
            vp_res["requests"] = len(sizes)
            if total > a.budget_bytes:
                fail(w, "page-weight", "%d bytes exceeds budget %d" % (total, a.budget_bytes))
            # scenes
            vp_res["scenes"] = len(data["scenes"])
            if a.reduced_motion:
                for s in data["scenes"]:
                    if not s["final"]:
                        fail(w, "scene-final-state", "[data-scene] %s has no data-final-state" % (s["scene"] or s["el"]),
                             element=s["el"])
                    elif s["state"] != s["final"]:
                        fail(w, "scene-final-state", "[data-scene] %s data-state '%s' != final '%s' under reduced motion"
                             % (s["scene"] or s["el"], s["state"], s["final"]), element=s["el"])
            if a.out:
                shot = os.path.join(a.out, "viewport-%d%s.png" % (w, "-reduced" if a.reduced_motion else ""))
                try:
                    page.screenshot(path=shot, full_page=True)
                    vp_res["screenshot"] = shot
                except Exception as e:  # noqa: BLE001
                    vp_res["screenshot"] = None
                    fail(w, "screenshot", "could not capture screenshot: %s" % str(e).splitlines()[0])
            summary["viewports"].append(vp_res)
            ctx.close()
        browser.close()
    finally:
        pw_cm.stop()
    summary["maxBytes"] = max((v["bytes"] for v in summary["viewports"]), default=0)
    summary["budgetOk"] = summary["maxBytes"] <= a.budget_bytes
    summary["passed"] = not summary["failures"]
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
