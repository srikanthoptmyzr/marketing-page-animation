#!/usr/bin/env python3
"""Measure a reference screenshot before rebuilding it: palette, aspect, bands, gutters, regions.

A reconstruction drifts from its reference in two ways, and both are measurable before a line
of markup is written:

  * **Colour.** An accent that is close but wrong makes every scene read as a generic app, and
    it does not look broken, so it survives review.
  * **Geometry.** Sizing each element by eye works for one card and compounds into a layout
    that is subtly wrong everywhere. And the trimmed content aspect is the number a fixed-slot
    scene sets its design width from (reference-scanning.md §4) - the raw image aspect includes
    whatever margin the crop happened to capture, so matching it leaves the scene mis-shapen.

This prints what the image actually contains, so both become inputs instead of guesses.

  scan_reference.py shot.png                 # full report
  scan_reference.py shot.png --regions       # add a per-region palette grid
  scan_reference.py *.png --palette-only     # cross-image palette (use before theming)

Needs Pillow. Without it the script exits 2 and says so rather than guessing.
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("error: this script needs Pillow; measurement cannot be faked.", file=sys.stderr)
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



def px(im):
    return im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()


def neutral(rgb):
    return max(rgb) - min(rgb) < 16 and (rgb[0] > 232 or rgb[0] < 58)


def hx(rgb):
    return "#%02X%02X%02X" % rgb


def palette(im, top=14, skip_neutral=True):
    c = Counter(px(im))
    out = []
    for rgb, n in c.most_common(6000):
        if skip_neutral and neutral(rgb):
            continue
        out.append((hx(rgb), n))
        if len(out) >= top:
            break
    return out


def bg_candidates(im, n=4):
    """Rank candidates for the page background by coverage.

    Sampling a fixed edge does not generalise: a dashboard usually opens with a white header,
    so the top edge returns the header's white, and a screenshot often carries a white margin,
    so the side gutters do too. Both make every band boundary come out inverted.

    What does generalise: the page background is the largest flat NEUTRAL area that is not
    effectively pure white (cards are). Ranked, so a wrong guess is visible rather than silent.
    """
    c = Counter(px(im))
    total = im.size[0] * im.size[1]
    out = []
    for rgb, cnt in c.most_common(400):
        if max(rgb) - min(rgb) >= 16:          # tinted: a band or a card accent, not the page
            continue
        if min(rgb) >= 252:                    # cards and margins
            continue
        if cnt / total < 0.004:
            continue
        out.append((rgb, cnt))
        if len(out) >= n:
            break
    if not out:                                 # flat white page: fall back to the mode
        out = [(c.most_common(1)[0][0], c.most_common(1)[0][1])]
    return out


def bands(im, bg, tol=7):
    """Horizontal bands: rows where the page background stops and card surface starts.

    Reading the layout rhythm off the pixels beats estimating it. The y values it prints are
    the card edges - use them as the section boundaries and the gaps between them as the gutter.
    """
    W, H = im.size
    p = im.load()
    cov = []
    for y in range(H):
        n = 0
        for x in range(0, W, 6):
            c = p[x, y]
            if not all(abs(a - b) <= tol for a, b in zip(c, bg)):
                n += 1
        cov.append(n / len(range(0, W, 6)))
    # Hysteresis: a band must hold for MIN_RUN rows before it counts as a change. Without it a
    # row of text inside a card dips the coverage for two or three pixels and the report fills
    # with boundaries that are not there.
    MIN_RUN = 5
    raw = [v > 0.55 for v in cov]
    out, prev, i = [], None, 0
    while i < len(raw):
        b = raw[i]
        run = 1
        while i + run < len(raw) and raw[i + run] == b:
            run += 1
        if run >= MIN_RUN or prev is None:
            if b != prev:
                out.append((i, "card" if b else "gap"))
                prev = b
        i += run
    return out


def content_box(im, tol=12):
    """The bounding box of everything that is not the outer margin.

    A screenshot usually carries a margin, so its raw width/height aspect is not the aspect of
    the UI. When the reconstruction goes into a fixed slot, the number you set the design width
    from is the TRIMMED content aspect, not the image aspect - matching the raw aspect leaves the
    scene the wrong shape by however much margin the crop happened to include.

    Trim against the CORNER colour, not the detected page background: the outer margin is often a
    different shade from the neutral that fills the gaps between cards, so trimming against the
    page background can leave the whole image untrimmed.
    """
    from PIL import ImageChops
    W, H = im.size
    corners = [im.getpixel(p) for p in ((1, 1), (W - 2, 1), (1, H - 2), (W - 2, H - 2))]
    margin = Counter(corners).most_common(1)[0][0]
    solid = Image.new("RGB", im.size, margin)
    diff = ImageChops.difference(im, solid).convert("L").point(lambda v: 255 if v > tol else 0)
    return diff.getbbox() or (0, 0, W, H)


def gutters(im, bg, y0, y1, tol=8, minw=5):
    """Vertical gutters inside a band: columns that are page background top to bottom."""
    W = im.size[0]
    p = im.load()
    ys = list(range(y0 + 2, y1 - 2, 3)) or [y0]
    runs, start = [], None
    for x in range(W):
        isbg = all(all(abs(a - b) <= tol for a, b in zip(p[x, y], bg)) for y in ys)
        if isbg and start is None:
            start = x
        elif not isbg and start is not None:
            if x - start >= minw:
                runs.append((start, x))
            start = None
    if start is not None and W - start >= minw:
        runs.append((start, W))
    return runs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shots", nargs="+")
    ap.add_argument("--regions", action="store_true", help="add a 4x3 region palette grid")
    ap.add_argument("--palette-only", action="store_true")
    ap.add_argument("--bg", help="page background as #RRGGBB, when the detected one is wrong")
    args = ap.parse_args()

    if args.palette_only:
        tot, spread = Counter(), {}
        for s in args.shots:
            im = load_rgb(s)
            c = Counter(px(im))
            tot.update(c)
            for rgb, n in c.most_common(600):
                if not neutral(rgb):
                    spread.setdefault(rgb, set()).add(Path(s).name)
        print(f"{len(args.shots)} screenshot(s) — colours seen in 2+ are the product's own\n")
        for h, n in palette(Image.new("RGB", (1, 1)) if False else None, 0) if False else []:
            pass
        shown = 0
        for rgb, n in tot.most_common(6000):
            if neutral(rgb):
                continue
            files = len(spread.get(rgb, ()))
            print(f"  {'*' if files > 1 else ' '} {hx(rgb)}  {n:>10,}px   {files} shot(s)")
            shown += 1
            if shown >= 20:
                break
        return 0

    for s in args.shots:
        im = load_rgb(s)
        W, H = im.size
        cands = bg_candidates(im)
        bg = tuple(int(args.bg.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) if args.bg else cands[0][0]
        print(f"\n=== {Path(s).name} ===")
        print(f"size {W}x{H}   aspect {W/H:.3f}")
        print(f"page background: {hx(bg)}" + ("  (from --bg)" if args.bg else ""))
        if len(cands) > 1 and not args.bg:
            alt = ", ".join(f"{hx(r)} {n/(W*H)*100:.1f}%" for r, n in cands[1:])
            print(f"   other candidates: {alt}   — if the bands below look wrong, re-run with --bg")

        cb = content_box(im)
        cw, ch = cb[2] - cb[0], cb[3] - cb[1]
        print(f"content box (margin trimmed): {cw}x{ch}   aspect {cw/ch:.3f}"
              " ← match a fixed slot to THIS, not the raw aspect")

        print("\npalette (most used first, neutrals dropped):")
        for h, n in palette(im):
            print(f"   {h}  {n:>9,}px")

        b = bands(im, bg)
        print("\nhorizontal bands — y where the surface changes:")
        for y, kind in b:
            print(f"   y={y:<5} {kind}")

        card_bands = []
        for i, (y, kind) in enumerate(b):
            if kind == "card":
                y2 = b[i + 1][0] if i + 1 < len(b) else H
                if y2 - y > 24:
                    card_bands.append((y, y2))
        print("\nvertical gutters inside each band (x ranges of page background):")
        for y0, y1 in card_bands:
            g = [r for r in gutters(im, bg, y0, y1) if r[1] - r[0] >= 6]
            cols = len([r for r in g if r[0] > 2 and r[1] < W - 2]) + 1
            print(f"   band y {y0}-{y1}: {cols} column(s); gutters {g[:8]}")

        if args.regions:
            print("\nregion palette (4 cols x 3 rows):")
            for r in range(3):
                for c in range(4):
                    box = (c * W // 4, r * H // 3, (c + 1) * W // 4, (r + 1) * H // 3)
                    pl = palette(im.crop(box), 4)
                    print(f"   r{r}c{c}: " + "  ".join(h for h, _ in pl))

        print("\nNext: build the theme from the palette above, author the layout at "
              f"{W}x{H} and scale it as a whole (references/ui-reconstruction.md).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
