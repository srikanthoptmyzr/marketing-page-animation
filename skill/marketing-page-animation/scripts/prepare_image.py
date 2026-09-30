#!/usr/bin/env python3
"""Prepare an uploaded image for a named site slot.

The uploaded size is never used: the image is cropped (cover) or fitted (contain)
to the slot in site-kit/image-specs.json and exported at the slot's widths.

  prepare_image.py IMAGE --slot feature --out DIR [--name NAME] [--focus X,Y] [--alt TEXT]
  prepare_image.py --list

Writes DIR/NAME-<w>.webp for each width and DIR/NAME.picture.html (<picture> snippet).
Needs Pillow. Exit: 0 ok, 1 failure, 2 usage/missing input.
Product screenshots are inputs, not assets: use this for photos, thumbnails and
static visuals, never to embed a screenshot of UI that should be a scene.
"""
import argparse, json, os, sys
SPECS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site-kit", "image-specs.json")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", nargs="?")
    ap.add_argument("--slot")
    ap.add_argument("--out")
    ap.add_argument("--name")
    ap.add_argument("--focus", default="0.5,0.5", help="crop focus x,y 0..1 (cover slots)")
    ap.add_argument("--alt", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    specs = json.load(open(SPECS))
    if a.list:
        for k, s in specs["slots"].items():
            print(f"{k:18} {s['fit']:8} widths={s['export_widths']}  {s['description']}")
        return 0
    if not (a.image and a.slot and a.out):
        ap.print_usage(sys.stderr); return 2
    if a.slot not in specs["slots"]:
        print("unknown slot; use --list", file=sys.stderr); return 2
    try:
        from PIL import Image
    except ImportError:
        print("Pillow missing: pip install pillow", file=sys.stderr); return 2
    s = specs["slots"][a.slot]
    fmt = s.get("format", specs["format"]); q = specs["quality"]
    im = Image.open(a.image); im.load()
    if im.mode not in ("RGB", "RGBA"): im = im.convert("RGBA")
    w0, h0 = im.size
    notes = []
    if s["fit"] == "cover":
        ar = s["aspect"][0] / s["aspect"][1]
        fx, fy = [min(1, max(0, float(v))) for v in a.focus.split(",")]
        if w0 / h0 > ar:
            nw = round(h0 * ar); x = round((w0 - nw) * fx); box = (x, 0, x + nw, h0)
        else:
            nh = round(w0 / ar); y = round((h0 - nh) * fy); box = (0, y, w0, y + nh)
        im = im.crop(box); notes.append(f"cropped {w0}x{h0} -> {im.size[0]}x{im.size[1]} to {s['aspect'][0]}:{s['aspect'][1]}")
    else:
        ar = w0 / h0
        lo, hi = s["aspect_min"], s["aspect_max"]
        tgt = min(hi, max(lo, ar))
        if abs(tgt - ar) > 0.01:
            if ar > tgt: nw, nh = w0, round(w0 / tgt)
            else: nw, nh = round(h0 * tgt), h0
            bg = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
            bg.paste(im.convert("RGBA"), ((nw - w0) // 2, (nh - h0) // 2)); im = bg
            notes.append(f"padded to aspect {tgt:.2f} (was {ar:.2f})")
    os.makedirs(a.out, exist_ok=True)
    name = a.name or os.path.splitext(os.path.basename(a.image))[0]
    out = []
    for w in s["export_widths"]:
        if w > im.size[0]:
            notes.append(f"source too small for {w}w (max {im.size[0]}); skipped, ask for a larger image")
            continue
        h = round(im.size[1] * w / im.size[0])
        r = im.resize((w, h), Image.LANCZOS)
        fn = f"{name}-{w}.{fmt}"
        r.save(os.path.join(a.out, fn), fmt.upper(), quality=q, method=6)
        out.append((fn, w, h))
    if not out:
        print("no size produced: source smaller than every slot width", file=sys.stderr); return 1
    big = out[-1]
    srcset = ", ".join(f"{f} {w}w" for f, w, _ in out)
    obj = "object-cover" if s["fit"] == "cover" else "object-contain"
    html = (f'<picture><source type="image/{fmt}" srcset="{srcset}" sizes="{s["sizes"]}">'
            f'<img src="{big[0]}" width="{big[1]}" height="{big[2]}" alt="{a.alt}" loading="lazy" class="w-full h-full {obj}"></picture>\n')
    open(os.path.join(a.out, name + ".picture.html"), "w").write(html)
    print(f"slot={a.slot} source={w0}x{h0}")
    for n in notes: print(" -", n)
    for f, w, h in out: print(f" wrote {f} {w}x{h}")
    if not a.alt: print(" - alt text missing: add descriptive alt before handoff")
    return 0

if __name__ == "__main__":
    sys.exit(main())
