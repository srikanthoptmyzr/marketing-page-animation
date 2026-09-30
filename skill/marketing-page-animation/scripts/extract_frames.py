#!/usr/bin/env python3
"""Extract frames, metadata and an optional contact sheet from a video.

Usage:
  extract_frames.py VIDEO --out DIR [--fps 2] [--scene-threshold 0.3]
                    [--max-frames N] [--contact-sheet [--timestamps]]

Output layout (DIR):
  frames/frame_0001.png ...   extracted frames (1-based, zero padded)
  frames.json                 video metadata + [{index, file, timestamp}]
  contact_sheet.png           only with --contact-sheet
  .gitignore                  "*" (frames are reference material, never ship them)

Modes:
  interval (default)  one frame every 1/FPS seconds. If --max-frames would be
                      exceeded, the rate is lowered so frames stay evenly spread.
  scene               with --scene-threshold T (0 < T <= 1) the first frame plus
                      every frame whose ffmpeg scene score exceeds T. If fewer
                      than two frames are found, falls back to interval mode
                      and says so.

Requires ffmpeg and ffprobe on PATH (standard library only otherwise).

Exit codes: 0 ok, 1 extraction failed / no frames, 2 usage error or missing
tool or input.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys


def die(code, msg):
    print(msg, file=sys.stderr)
    sys.exit(code)


def run(cmd, timeout=None):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, errors="replace", timeout=timeout)


def parse_rate(s):
    try:
        if "/" in s:
            a, b = s.split("/")
            return float(a) / float(b) if float(b) else 0.0
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def probe(video):
    r = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", video])
    if r.returncode != 0:
        die(1, "ffprobe could not read the video: " + r.stderr.strip()[:300])
    data = json.loads(r.stdout or "{}")
    vs = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not vs:
        die(1, "no video stream found in input")
    dur = None
    for cand in (vs.get("duration"), data.get("format", {}).get("duration")):
        try:
            dur = float(cand)
            break
        except (TypeError, ValueError):
            pass
    w, h = int(vs.get("width", 0)), int(vs.get("height", 0))
    rot = 0
    for sd in vs.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"]) % 360
    if rot in (90, 270):  # ffmpeg autorotates, so report the displayed size
        w, h = h, w
    fps = parse_rate(vs.get("avg_frame_rate", "")) or parse_rate(vs.get("r_frame_rate", ""))
    return {"duration": dur, "width": w, "height": h, "fps": round(fps, 3),
            "codec": vs.get("codec_name"), "frame_count": vs.get("nb_frames")}


SHOWINFO_RE = re.compile(r"pts_time:\s*(-?[0-9.]+)")


def times_from_showinfo(stderr):
    return [max(0.0, float(m.group(1))) for m in SHOWINFO_RE.finditer(stderr)]


def clean_frames(frames_dir):
    os.makedirs(frames_dir, exist_ok=True)
    for f in os.listdir(frames_dir):
        if re.fullmatch(r"frame_\d{4,}\.png", f):
            os.remove(os.path.join(frames_dir, f))


def extract(video, frames_dir, vf_head, max_frames):
    pattern = os.path.join(frames_dir, "frame_%04d.png")
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", video,
           "-vf", vf_head + ",showinfo", "-fps_mode", "passthrough"]
    if max_frames:
        cmd += ["-frames:v", str(max_frames)]
    cmd += [pattern]
    r = run(cmd)
    if r.returncode != 0 and "fps_mode" in r.stderr:  # ffmpeg < 5.1
        cmd[cmd.index("-fps_mode")] = "-vsync"
        r = run(cmd)
    files = sorted(f for f in os.listdir(frames_dir) if re.fullmatch(r"frame_\d{4,}\.png", f))
    return r, files


def make_contact_sheet(frames_dir, files, times, out_png, cols, thumb_w, max_tiles, stamps):
    n = len(files)
    step = max(1, math.ceil(n / max_tiles))
    idxs = list(range(0, n, step))
    rows = math.ceil(len(idxs) / cols)
    filt = ["select='not(mod(n\\,%d))'" % step, "setpts=N/FRAME_RATE/TB",
            "scale=%d:-1" % thumb_w]
    if stamps:
        for j, i in enumerate(idxs):
            filt.append("drawtext=text='%s':x=6:y=6:fontsize=%d:fontcolor=white:"
                        "box=1:boxcolor=black@0.6:enable='eq(n\\,%d)'"
                        % ("%.2fs" % times[i], max(12, thumb_w // 16), j))
    filt.append("tile=%dx%d:padding=4:margin=4:color=black" % (cols, rows))
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-framerate", "1", "-start_number", "1",
           "-i", os.path.join(frames_dir, "frame_%04d.png"),
           "-vf", ",".join(filt), "-frames:v", "1", "-update", "1", out_png]
    r = run(cmd)
    return r.returncode == 0 and os.path.exists(out_png), r.stderr, len(idxs), step


def build_parser():
    p = argparse.ArgumentParser(
        description="Extract frames + frames.json (+ optional contact sheet) from a video with ffmpeg.",
        epilog="Exit codes: 0 ok, 1 failure, 2 usage error / missing ffmpeg or input.")
    p.add_argument("video", help="input video file")
    p.add_argument("--out", metavar="DIR", help="output directory (default: <video-stem>_frames next to cwd)")
    p.add_argument("--fps", type=float, default=2.0, help="interval sampling rate (default 2)")
    p.add_argument("--scene-threshold", type=float, metavar="T",
                   help="scene-change detection, 0<T<=1 (typical 0.2-0.4); falls back to --fps if too few hits")
    p.add_argument("--max-frames", type=int, metavar="N", help="hard cap on number of frames written")
    p.add_argument("--contact-sheet", action="store_true", help="also write contact_sheet.png")
    p.add_argument("--timestamps", action="store_true",
                   help="burn timestamps into contact sheet tiles (needs ffmpeg drawtext)")
    p.add_argument("--sheet-cols", type=int, default=5, help="contact sheet columns (default 5)")
    p.add_argument("--sheet-thumb-width", type=int, default=320, help="contact sheet tile width px (default 320)")
    p.add_argument("--sheet-max", type=int, default=48, help="max tiles on the sheet, evenly sampled (default 48)")
    return p


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)

    if a.fps <= 0:
        ap.error("--fps must be > 0")
    if a.scene_threshold is not None and not (0 < a.scene_threshold <= 1):
        ap.error("--scene-threshold must be in (0, 1]")
    if a.max_frames is not None and a.max_frames < 1:
        ap.error("--max-frames must be >= 1")
    if a.sheet_cols < 1 or a.sheet_thumb_width < 16 or a.sheet_max < 1:
        ap.error("--sheet-* values out of range")
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        die(2, "error: %s not found on PATH. Install ffmpeg (which includes ffprobe), e.g. "
               "'apt install ffmpeg' or 'brew install ffmpeg', then re-run." % " and ".join(missing))
    if not os.path.isfile(a.video):
        die(2, "error: video not found: %s" % a.video)

    out = a.out or (os.path.splitext(os.path.basename(a.video))[0] + "_frames")
    frames_dir = os.path.join(out, "frames")
    info = probe(a.video)
    dur = info["duration"]
    clean_frames(frames_dir)
    try:
        with open(os.path.join(out, ".gitignore"), "w") as fh:
            fh.write("*\n")
    except OSError as e:
        die(2, "error: cannot write to %s: %s" % (out, e))

    mode, note, used_fps = "interval", None, a.fps
    times, files = [], []
    if a.scene_threshold is not None:
        vf = "select='eq(n\\,0)+gt(scene\\,%s)'" % a.scene_threshold
        r, files = extract(a.video, frames_dir, vf, a.max_frames)
        times = times_from_showinfo(r.stderr)
        if r.returncode == 0 and len(files) >= 2:
            mode = "scene"
        else:
            note = "scene detection found %d frame(s); fell back to interval sampling" % len(files)
            clean_frames(frames_dir)
            files = []
    if mode == "interval":
        if a.max_frames and dur and dur * used_fps > a.max_frames:
            used_fps = a.max_frames / dur
            note = ((note + "; ") if note else "") + \
                "fps lowered to %.4f to stay within --max-frames" % used_fps
        r, files = extract(a.video, frames_dir, "fps=%.6f" % used_fps, a.max_frames)
        times = times_from_showinfo(r.stderr)
        if r.returncode != 0 or not files:
            die(1, "ffmpeg failed: " + r.stderr.strip()[-400:])

    if len(times) != len(files):  # showinfo parsing mismatch: derive from rate
        times = [i / used_fps for i in range(len(files))] if mode == "interval" else \
            (times + [0.0] * len(files))[:len(files)]
    frames = [{"index": i + 1, "file": "frames/" + f, "timestamp": round(times[i], 3)}
              for i, f in enumerate(files)]

    sheet = None
    if a.contact_sheet and files:
        sheet_png = os.path.join(out, "contact_sheet.png")
        ok, err, tiles, step = make_contact_sheet(frames_dir, files, times, sheet_png, a.sheet_cols,
                                                  a.sheet_thumb_width, a.sheet_max, a.timestamps)
        if not ok and a.timestamps:
            print("warning: timestamps unavailable (ffmpeg drawtext failed); building sheet without them",
                  file=sys.stderr)
            ok, err, tiles, step = make_contact_sheet(frames_dir, files, times, sheet_png, a.sheet_cols,
                                                      a.sheet_thumb_width, a.sheet_max, False)
        if ok:
            sheet = {"file": "contact_sheet.png", "tiles": tiles, "every_nth_frame": step}
        else:
            print("warning: contact sheet failed: " + err.strip()[-200:], file=sys.stderr)

    meta = {"source": os.path.basename(a.video), "mode": mode, "duration": dur,
            "width": info["width"], "height": info["height"], "fps": info["fps"],
            "codec": info["codec"], "sampling_fps": round(used_fps, 4) if mode == "interval" else None,
            "scene_threshold": a.scene_threshold if mode == "scene" else None,
            "note": note, "contact_sheet": sheet, "frames": frames}
    with open(os.path.join(out, "frames.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")

    print("duration:   %s" % ("%.3f s" % dur if dur is not None else "unknown"))
    print("resolution: %dx%d" % (info["width"], info["height"]))
    print("fps:        %s" % info["fps"])
    print("mode:       %s%s" % (mode, " (" + note + ")" if note else ""))
    print("frames:     %d -> %s" % (len(frames), frames_dir))
    if sheet:
        print("sheet:      %s (%d tiles)" % (os.path.join(out, sheet["file"]), sheet["tiles"]))
    print("note: frames are reference material; keep them out of preview/ and handoff/ "
          "(a .gitignore was written in the output dir).")
    return 0 if frames else 1


if __name__ == "__main__":
    sys.exit(main())
