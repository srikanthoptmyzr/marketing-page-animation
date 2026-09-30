#!/usr/bin/env python3
"""Derive a product-UI theme from the reference screenshots, and check a theme against them.

A reconstruction only looks like the product if it is *painted* like the product. The single
biggest fidelity failure is a scene themed from memory, from the marketing brand, or carried
over from an unrelated scene set - it reads as "some SaaS app", not as this one. This makes the
palette a measured input instead of an assertion.

  extract_palette.py shots/*.png                  # print the palette + a --product-* block
  extract_palette.py shots/*.png --check a.css    # verify a stylesheet's theme against them

--check is the important mode. It reads every `--product-*: #hex` in the stylesheet and fails
when a value does not appear in the screenshots, telling you the nearest colour that does.

Needs Pillow. Without it the script exits 2 and says so; it degrades, it does not guess.

Exit codes: 0 ok, 1 a theme colour is not in the references, 2 usage error or Pillow missing.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("error: this script needs Pillow (the palette must be measured, not guessed).",
          file=sys.stderr)
    print("Without it, derive the theme by eye from the screenshots and say so in the handoff.",
          file=sys.stderr)
    sys.exit(2)

def load_rgb(path):
    """Open a screenshot as RGB, compositing any transparency onto white.

    Screenshots exported from design tools and browsers often carry an alpha channel with a
    transparent page. A bare .convert("RGB") turns those pixels black, which inverts the page
    background, the band edges and the palette - silently, because the numbers still look
    plausible. Transparent means "the page", and the page a screenshot sits on is white.
    """
    im = Image.open(path)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        return bg.convert("RGB")
    return im.convert("RGB")


HEX = re.compile(r'(--product-[a-z-]+)\s*:\s*(#[0-9a-fA-F]{3,8})')


def is_neutral(r, g, b):
    """Near-white, near-black or flat grey: structural, not part of the brand palette."""
    return max(r, g, b) - min(r, g, b) < 16 and (r > 232 or r < 58)


def counts(paths):
    total = Counter()
    per_file = {}
    for p in paths:
        try:
            im = load_rgb(p)
        except OSError as e:
            print(f"warning: cannot read {p} ({e})", file=sys.stderr)
            continue
        data = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
        c = Counter(data)
        per_file[Path(p).name] = c
        total.update(c)
    return total, per_file


def ranked(c, top=24, keep_neutral=False):
    out = []
    for (r, g, b), n in c.most_common(4000):
        if not keep_neutral and is_neutral(r, g, b):
            continue
        out.append((f"#{r:02X}{g:02X}{b:02X}", n))
        if len(out) >= top:
            break
    return out


def to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def sat_lum(rgb):
    r, g, b = (v / 255 for v in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    lum = (mx + mn) / 2
    if mx == mn:
        return 0.0, lum
    d = mx - mn
    return (d / (2 - mx - mn) if lum > 0.5 else d / (mx + mn)), lum


def pick_accent(spread, total, min_files):
    """The accent is a SATURATED, reasonably dark colour used across screenshots.

    Ranking by pixel count alone picks the pale tint that fills large areas (a soft lavender
    background beats the purple it is a tint of). Ranking by saturation alone picks whichever
    platform logo is brightest. Spread across screenshots is what separates the product's own
    accent from one screen's content, so rank on that first.
    """
    cands = []
    for rgb, files in spread.items():
        if len(files) < min_files:
            continue
        sat, lum = sat_lum(rgb)
        if sat < 0.30 or lum > 0.62 or lum < 0.08:
            continue
        cands.append((len(files), total.get(rgb, 0), rgb))
    if not cands:
        return None
    cands.sort(reverse=True)
    return cands[0][2]


def pale_tint_of(accent, spread, min_files):
    """The soft companion: the palest colour sharing the accent's hue."""
    if not accent:
        return None
    ah = sat_lum(accent)
    best = None
    for rgb, files in spread.items():
        if len(files) < min_files:
            continue
        sat, lum = sat_lum(rgb)
        if lum < 0.70 or sat < 0.15:
            continue
        # same hue family: the accent's dominant channel order is preserved
        if sorted(range(3), key=lambda i: -accent[i]) != sorted(range(3), key=lambda i: -rgb[i]):
            continue
        if best is None or lum > sat_lum(best)[1]:
            best = rgb
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shots", nargs="+", help="reference screenshots")
    ap.add_argument("--check", metavar="CSS", help="stylesheet whose --product-* theme to verify")
    ap.add_argument("--tolerance", type=float, default=18.0,
                    help="how far a theme colour may sit from a colour in the shots (default 26)")
    ap.add_argument("--min-files", type=int, default=2,
                    help="a colour must appear in at least this many shots to count as the "
                         "product's own (default 2)")
    args = ap.parse_args()

    total, per_file = counts(args.shots)
    if not total:
        print("error: no readable images", file=sys.stderr)
        return 2

    # A colour seen across several screenshots is the product's; one seen in a single shot may
    # just be that screen's content.
    spread = {}
    for name, c in per_file.items():
        for rgb, n in c.most_common(600):
            if is_neutral(*rgb):
                continue
            spread.setdefault(rgb, set()).add(name)
    common = {rgb for rgb, files in spread.items() if len(files) >= args.min_files}

    if not args.check:
        print(f"{len(per_file)} screenshot(s)\n")
        print("Palette, most used first (● = appears in 2+ shots, so it is the product's own):")
        for hx, n in ranked(total, 22):
            mark = "●" if to_rgb(hx) in common else " "
            files = len(spread.get(to_rgb(hx), ()))
            print(f"  {mark} {hx}  {n:>9,}px   in {files} shot(s)")
        a = pick_accent(spread, total, args.min_files)
        t = pale_tint_of(a, spread, args.min_files)
        acc = "#%02X%02X%02X" % a if a else "#000000"
        soft = "#%02X%02X%02X" % t if t else "<pale tint of the accent>"
        print("\nStarting point for the scene theme — check each against the shots before using:")
        print(f"""
.product-ui{{--product-bg:#fff;--product-panel:#F8F9FB;--product-text:#4A4F57;
  --product-head:#2F3644;--product-muted:#6B7280;--product-border:#E5E7EB;
  --product-accent:{acc};--product-accent-soft:{soft};
  --product-ok:#1F8A4C;--product-warn:#C98A1F}}""")
        print("\nPlatform marks keep their own brand colours; never repaint them to the accent.")
        return 0

    css = Path(args.check).read_text(encoding="utf-8", errors="replace")
    theme = HEX.findall(css)
    if not theme:
        print(f"error: no --product-* colours found in {args.check}", file=sys.stderr)
        return 2

    # Validate against every colour the product actually paints with, in ANY screenshot: a
    # platform mark that appears in one shot is still the product's. The "2+ shots" rule is for
    # CHOOSING the accent, not for judging whether a colour is real.
    check_against = [rgb for rgb, files in spread.items()
                     if max(c.get(rgb, 0) for c in per_file.values()) >= 40]
    common_rgb = [rgb for rgb in check_against if rgb in common]
    dominant = pick_accent(spread, total, args.min_files)
    if dominant:
        print(f"  product accent: #{dominant[0]:02X}{dominant[1]:02X}{dominant[2]:02X}"
              f"  (saturated, in {len(spread.get(dominant, ()))} of {len(per_file)} shots)\n")
    bad = []
    print(f"checking {len(theme)} theme colour(s) in {args.check} "
          f"against {len(per_file)} screenshot(s)\n")
    for var, hx in theme:
        rgb = to_rgb(hx)
        if is_neutral(*rgb):
            print(f"  ok      {var}: {hx}  (neutral)")
            continue
        near = min(check_against, key=lambda c: dist(rgb, c)) if check_against else None
        d = dist(rgb, near) if near else 999
        if d <= args.tolerance:
            print(f"  ok      {var}: {hx}")
        else:
            # For the accent, the answer is the product's dominant colour, not whatever happens
            # to sit nearest to a wrong value - nearest-match would "fix" indigo to icon blue.
            if "accent" in var and "soft" not in var and dominant:
                sugg = "#%02X%02X%02X" % dominant
                why = "the product's accent"
            elif "accent-soft" in var and (t := pale_tint_of(dominant, spread, args.min_files)):
                sugg = "#%02X%02X%02X" % t
                why = "the accent's pale tint in the shots"
            else:
                sugg = "#%02X%02X%02X" % near if near else "?"
                why = f"nearest colour the product actually uses, distance {d:.0f}"
            print(f"  WRONG   {var}: {hx}  is not in the references ({why}: {sugg})")
            bad.append((var, hx, sugg))

    if bad:
        print(f"\n{len(bad)} theme colour(s) are not in the reference screenshots.")
        print("A scene painted in colours the product does not use will not read as the product,")
        print("however correct its layout is. Replace each one:")
        for var, hx, sugg in bad:
            print(f"    {var}: {hx}  ->  {sugg}")
        print("\nThen re-render and compare against the screenshot side by side.")
        return 1
    print("\nevery theme colour appears in the reference screenshots")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
