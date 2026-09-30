#!/usr/bin/env python3
"""Report which optional tools this environment has, and what degrades without them.

Run once at phase 1, before asking the user for anything. The skill never installs
anything and never asks the user to install anything: it states what it can and
cannot do here, and takes the documented fallback.

  preflight.py [--json]

Exit codes: 0 every capability available, 1 at least one degraded, 2 usage error.
"""
import argparse
import importlib.util
import json
import shutil
import sys

CAPS = [
    {
        "id": "python-imaging",
        "needs": "Pillow (python package)",
        "check": ("module", "PIL"),
        "enables": "phase 4: measuring the reference screenshots (scan_reference.py, "
                   "extract_palette.py) — palette, page background, section bands, theme check. "
                   "phase 11: fitting page images to the site's slots (prepare_image.py)",
        "fallback": "Page images: ask the user for images already at the slot's export widths and record "
                    "every un-fitted one as an approximation. Scenes: derive the palette and the layout "
                    "bands by eye from the screenshots at full resolution, state in the handoff that the "
                    "theme is unverified, and expect it to be close but wrong — an accent that is nearly "
                    "right makes a scene read as a generic app and does not look broken.",
        "blocks": "nothing outright, but scene fidelity stops being checkable: the palette and the "
                  "layout rhythm become estimates instead of measurements.",
    },
    {
        "id": "video-frames",
        "needs": "ffmpeg and ffprobe on PATH",
        "check": ("binaries", ["ffmpeg", "ffprobe"]),
        "enables": "phase 5: reading a screen recording (extract_frames.py)",
        "fallback": "Ask the user for still frames of the key moments and analyse those as screenshots "
                    "(references/video-analysis.md step 0). Never claim to have watched a video that could not be read.",
        "blocks": "video input only. A page built from screenshots is unaffected.",
    },
    {
        "id": "headless-browser",
        "needs": "Playwright with Chromium",
        "check": ("module", "playwright"),
        "enables": "phase 14: automated visual, responsive, reduced-motion and accessibility checks (check_page.py)",
        "fallback": "Do the viewport-matrix, overflow, text-size and reduced-motion checks by hand, and say "
                    "in reports/validation.md that they were manual (references/validation.md).",
        "blocks": "automated validation only. The privacy gate is pure Python and still runs.",
    },
]


def available(check):
    kind, what = check
    if kind == "module":
        return importlib.util.find_spec(what) is not None
    return all(shutil.which(b) for b in what)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    results = []
    for cap in CAPS:
        ok = available(cap["check"])
        results.append({**{k: v for k, v in cap.items() if k != "check"}, "available": ok})

    degraded = [r for r in results if not r["available"]]

    if args.json:
        print(json.dumps({"capabilities": results, "degraded": len(degraded)}, indent=1))
        return 1 if degraded else 0

    for r in results:
        print(f"[{'ok ' if r['available'] else 'MISSING'}] {r['id']:18} {r['needs']}")
    if not degraded:
        print("\nall capabilities available")
        return 0

    print(f"\n{len(degraded)} capability(ies) unavailable in this environment.")
    print("The privacy gate (leak_scan.py) and the scene validator are pure Python and always run.\n")
    for r in degraded:
        print(f"- {r['id']}: {r['enables']}")
        print(f"  affects: {r['blocks']}")
        print(f"  fallback: {r['fallback']}\n")
    print("Tell the user which parts are degraded, in plain language, before starting work.")
    print("Do not ask them to install anything.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
