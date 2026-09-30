#!/usr/bin/env python3
"""Check generated SVGs against the site's icon / illustration house style.

The site's 225 SVGs have no outliers, so "does this match the site" is a checkable
question rather than a matter of taste. This answers it.

  check_svg_style.py FILE.svg [...]            # auto-detects icon vs illustration
  check_svg_style.py --kind icon FILE.svg      # force a mode

Icon rules (references/icons-and-illustrations.md §2):
  square viewBox on a 24x24 grid, fill="none" root, strokes only in #069BA2,
  stroke-width ~6.7% of the viewBox, round caps and joins, no gradients/filters.

Illustration rules (§3):
  canvas 520x420 / 420x360 / 360x320 / 216x160, flat fills from the tint ladder,
  no gradients, at least one low-opacity backdrop shape.

Exit 0 clean, 1 if anything deviates, 2 on usage error.
"""
import argparse
import re
import sys
from pathlib import Path

# Measured from the icons the live site serves. Colour is chosen by role, not freely.
CONTENT_STROKES = {"#069BA2", "#058C92"}          # marketing / content icons
CHROME_STROKES = {"#2D3A48"}                      # close, hamburger and friends
ACCENT_STROKES = {"#66B205"}
PALETTE = CONTENT_STROKES | CHROME_STROKES | ACCENT_STROKES

TEAL_RAMP = {"#069BA2", "#058C92", "#045D61", "#02393C"}
SURFACE_DARK = {"#191B1F", "#22262B", "#0B0C0D", "#2D3A48"}
BADGE_FILLS = {"#058C92", "#069BA2", "#AAB0B7", "#F29C07", "#E72C64"}   # state discs
SOLID_FILLS = {"#F29C07", "#E17F0E", "#069BA2", "#058C92"}              # star and friends
WARM = {"#F29C07", "#F6CC6F", "#F4B44C"}
OBSERVED_TINTS = {"#66AFAB", "#B5D5D4", "#EDF4F4", "#E4EBEB", "#FFFFFE"}
ILLO_PALETTE = TEAL_RAMP | WARM | OBSERVED_TINTS | SURFACE_DARK

# stroke-width sits at roughly 7-10% of the grid across the whole set
SW_MIN, SW_MAX = 0.065, 0.105

BRANDISH = ("logo", "social_", "partner", "badge", "medal", "-marketing-", "tiktok",
            "slack", "linkedin", "reddit", "youtube", "-yt-", "_yt")


def viewbox(svg):
    m = re.search(r'viewBox\s*=\s*["\']([\d.\s-]+)["\']', svg)
    if not m:
        return None
    parts = m.group(1).split()
    if len(parts) != 4:
        return None
    try:
        return float(parts[2]), float(parts[3])
    except ValueError:
        return None


def hexes(svg):
    return {("#" + h.upper()) for h in re.findall(r'#([0-9a-fA-F]{6})\b', svg)}


def strokes_in(svg):
    return {("#" + h.upper()) for h in re.findall(r'stroke\s*=\s*["\']#([0-9a-fA-F]{6})', svg)}


def is_brand_mark(path, svg):
    """Third-party marks keep their own colours and must not be recoloured."""
    name = Path(path).name.lower()
    if any(b in name for b in BRANDISH):
        return True
    # no strokes at all, several fill colours, none of them ours
    fills = {("#" + h.upper()) for h in re.findall(r'fill\s*=\s*["\']#([0-9a-fA-F]{6})', svg)}
    return not strokes_in(svg) and len(fills) >= 2 and not (fills & (PALETTE | ILLO_PALETTE))


def fills_in(svg):
    out = set()
    for f in re.findall(r'fill\s*=\s*["\']([^"\']+)["\']', svg):
        f = f.strip()
        if f.lower() in ("none", ""):
            continue
        out.add(f.upper() if f.startswith("#") else f.lower())
    return out


def icon_family(svg):
    """The set has three families; each has its own rules."""
    st = strokes_in(svg)
    fl = fills_in(svg)
    solid = {f for f in fl if f != "white" and f != "#FFFFFF"}
    if st and not solid:
        return "outline"
    if solid and ("white" in fl or "#FFFFFF" in fl or "white" in svg):
        return "badge"
    if solid and not st:
        return "solid"
    return "outline"


def check_icon(svg, vb, notes):
    bad = []
    w, h = vb
    if abs(w - h) > 1.5:
        bad.append(f"viewBox is {w:g}x{h:g}; icons are square (1 unit of slack is normal)")
    if not 16 <= w <= 48:
        bad.append(f"grid is {w:g}; the house grid is 20 or 24 (scaled to 32/40 at most)")

    root = re.search(r'<svg\b[^>]*>', svg)
    if not root or 'fill="none"' not in root.group(0).replace("'", '"'):
        bad.append('root <svg> is missing fill="none"')
    if "Gradient" in svg or "<filter" in svg:
        bad.append("gradients and filters do not appear anywhere in the site's icon set")

    fam = icon_family(svg)
    notes.append(f"family: {fam}")
    st = strokes_in(svg)
    widths = {float(x) for x in re.findall(r'stroke-width\s*=\s*["\']([\d.]+)["\']', svg)}

    if fam == "outline":
        if not st:
            bad.append("no stroked paths; an outline icon is strokes, not fills")
        else:
            if len(st) > 1:
                bad.append(f"{len(st)} stroke colours ({', '.join(sorted(st))}); one per icon")
            off = st - PALETTE
            if off:
                bad.append(f"stroke colour(s) outside the palette: {', '.join(sorted(off))}"
                           f" (content icons use {' or '.join(sorted(CONTENT_STROKES))})")
            elif st & CHROME_STROKES:
                notes.append(f"{', '.join(st)} is the chrome colour (close/hamburger); "
                             f"a marketing section icon should be teal")
            if not widths:
                bad.append("no stroke-width set")
    elif fam == "badge":
        disc = {f for f in fills_in(svg) if f.startswith("#")} - {"#FFFFFF"}
        off = disc - BADGE_FILLS
        if off:
            bad.append(f"badge disc colour(s) outside the state palette: {', '.join(sorted(off))}")
        if not re.search(r'stroke\s*=\s*["\']white["\']', svg) and "#FFFFFF" not in {
                x.upper() for x in re.findall(r'stroke\s*=\s*["\']([^"\']+)["\']', svg)}:
            bad.append("a filled badge carries a white stroked glyph over the disc")
    else:  # solid
        off = {f for f in fills_in(svg) if f.startswith("#")} - SOLID_FILLS
        if off:
            bad.append(f"solid glyph colour(s) outside the accent palette: {', '.join(sorted(off))}")
        if st:
            bad.append("a solid glyph is one filled path with no strokes")

    for x in widths:
        if not (SW_MIN * w <= x <= SW_MAX * w):
            bad.append(f"stroke-width {x:g} on a {w:g} grid is outside 7-10% "
                       f"({SW_MIN * w:.2f}-{SW_MAX * w:.2f})")

    open_stroked = len([m for m in re.finditer(r'<(path|line|polyline|polygon)\b[^>]*>', svg)
                        if 'stroke="' in m.group(0) or "stroke='" in m.group(0)])
    for attr in ("stroke-linecap", "stroke-linejoin"):
        if len(re.findall(attr + r'\s*=\s*["\']round["\']', svg)) < open_stroked:
            bad.append(f'every stroked path needs {attr}="round"')

    shapes = len(re.findall(r'<(path|circle|rect|line|polyline|ellipse)\b', svg))
    if shapes > 12:
        bad.append(f"{shapes} shapes; the house style is 2-9 simple ones")
    return bad


def check_illustration(svg, vb):
    bad = []
    if "Gradient" in svg:
        bad.append("gradient found; no sampled site illustration uses one")
    off = hexes(svg) - ILLO_PALETTE
    if off:
        bad.append("colour(s) outside the teal ramp and accents: " + ", ".join(sorted(off)))
    ops = [float(o) for o in re.findall(r'opacity\s*=\s*["\']([\d.]+)["\']', svg)]
    ops += [float(o) for o in re.findall(r'opacity\s*:\s*([\d.]+)', svg)]
    big = max(vb) >= 300 and bool(hexes(svg) & TEAL_RAMP)
    if big and not any(0.3 <= o <= 0.6 for o in ops):
        bad.append("large decorative art sits at 0.4-0.5 opacity so it stays behind the copy")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--kind", choices=["icon", "illustration"], help="skip auto-detection")
    args = ap.parse_args()

    total = 0
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"error: no such file: {f}", file=sys.stderr)
            return 2
        svg = p.read_text(encoding="utf-8", errors="replace")
        if not args.kind and is_brand_mark(f, svg):
            print(f"{f}  [brand mark]  skipped - third-party marks keep their own colours")
            continue

        notes = []
        vb = viewbox(svg)
        if not vb:
            print(f"{f}: FAIL - no usable viewBox")
            total += 1
            continue

        kind = args.kind or ("icon" if max(vb) <= 64 else "illustration")
        bad = check_icon(svg, vb, notes) if kind == "icon" else check_illustration(svg, vb)

        if bad:
            total += len(bad)
            print(f"{f}  [{kind}]  {len(bad)} deviation(s):")
            for b in bad:
                print(f"    - {b}")
        else:
            print(f"{f}  [{kind}]  ok")
        for n in notes:
            print(f"    note: {n}")

    if total:
        print(f"\n{total} deviation(s) from the house style.")
        print("See references/icons-and-illustrations.md sections 2 and 3.")
        return 1
    print("\nall assets match the house style")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
