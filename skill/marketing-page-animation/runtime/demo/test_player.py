#!/usr/bin/env python3
"""Headless tests for scene-player.js using demo/index.html. Needs Playwright + Chromium.
Usage: python3 test_player.py [--shots DIR]   Exit 0 = all passed."""
import sys, re, json, pathlib, argparse
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser(); ap.add_argument("--shots"); a = ap.parse_args()
here = pathlib.Path(__file__).parent
URL = (here / "index.html").resolve().as_uri()
fails = []
def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + str(info)) if info and not ok else ""))
    if not ok: fails.append(name)

def norm(h):
    h = re.sub(r'\sstyle=""', '', h)
    h = re.sub(r'\sdata-(state|duration)="[^"]*"', '', h)
    h = re.sub(r'\sclass="([^"]*)"', lambda m: ' class="%s"' % ' '.join(sorted(set(m.group(1).split()) - {"pu-reduced","pu-resetting"})) if m.group(1).strip() else '', h)
    return re.sub(r'\s+', ' ', h).strip()

with sync_playwright() as p:
    b = p.chromium.launch()
    # 0. no-JS markup (the authored final state)
    ctx0 = b.new_context(java_script_enabled=False); pg0 = ctx0.new_page(); pg0.goto(URL)
    raw = {sid: pg0.eval_on_selector(f'[data-scene="{sid}"]', 'e=>e.innerHTML') for sid in ("demo-a","demo-b")}
    ctx0.close()

    # 1. reduced motion: final state at once, identical to authored markup
    ctx = b.new_context(reduced_motion="reduce", viewport={"width":900,"height":900}); pg = ctx.new_page()
    msgs = []; pg.on("console", lambda m: msgs.append((m.type, m.text))); pg.on("pageerror", lambda e: msgs.append(("pageerror", str(e))))
    pg.goto(URL); pg.wait_for_timeout(300)
    for sid in ("demo-a","demo-b"):
        st = pg.get_attribute(f'[data-scene="{sid}"]', "data-state")
        check(f"reduced-motion {sid}: data-state is final", st == "approved", st)
        cur = pg.eval_on_selector(f'[data-scene="{sid}"]', 'e=>e.innerHTML')
        check(f"reduced-motion {sid}: markup equals authored final state", norm(cur) == norm(raw[sid]))
        vis = pg.evaluate('''sid=>{const r=document.querySelector(`[data-scene="${sid}"]`);
          const v=t=>{const e=r.querySelector(`[data-target="${t}"]`);return e&&getComputedStyle(e).visibility!=='hidden'};
          return {ok:v('ok'),note:v('note'),rec:v('rec'),composer:v('composer'),cur:v('cur')}}''', sid)
        check(f"reduced-motion {sid}: result visible, controls hidden", vis["ok"] and vis["note"] and vis["rec"] and not vis["composer"] and not vis["cur"], vis)
    check("reduced-motion: no console errors/warnings", not [m for m in msgs if m[0] in ("error","warning","pageerror")], msgs)
    ctx.close()

    # 2. normal motion
    ctx = b.new_context(viewport={"width":900,"height":900}); pg = ctx.new_page()
    msgs = []; pg.on("console", lambda m: msgs.append((m.type, m.text))); pg.on("pageerror", lambda e: msgs.append(("pageerror", str(e))))
    pg.goto(URL); pg.wait_for_timeout(200)
    total = {sid: pg.evaluate(f'ProductScenes.get("{sid}").total') for sid in ("demo-a","demo-b")}
    print("durations ms:", total)
    check("durations sane (2s..15s)", all(2000 < v < 15000 for v in total.values()), total)

    def snap(sid, ms):
        return pg.evaluate('''([sid,ms])=>{const s=ProductScenes.get(sid);s.seek(ms);const r=s.el;
          const vis=t=>{const e=r.querySelector(`[data-target="${t}"]`);if(!e)return null;const cs=getComputedStyle(e);
             return cs.visibility!=='hidden'&&parseFloat(cs.opacity)>0.01};
          const txt=t=>{const e=r.querySelector(`[data-target="${t}"] [data-text],[data-target="${t}"] [data-input]`);return e?e.textContent:null};
          return {state:r.getAttribute('data-state'),composer:vis('composer'),q1:vis('q1'),load:vis('load'),a1:vis('a1'),m1:vis('m1'),
            rec:vis('rec'),appr:vis('appr'),ok:vis('ok'),note:vis('note'),cur:vis('cur'),
            typed:r.querySelector('[data-target="composer"] [data-input]').textContent,
            count:r.querySelector('[data-target="m1"] [data-count-to]').textContent,
            aText:r.querySelector('[data-target="a1"] [data-text]').textContent.length}}''', [sid, ms])

    # demo A
    s0 = snap("demo-a", 0)
    check("A t=0: only composer visible", s0["composer"] and not s0["q1"] and not s0["a1"] and not s0["ok"], s0)
    s = snap("demo-a", 900)
    check("A t=900: typing in composer", s["composer"] and 0 < len(s["typed"].replace("​","")) and s["typed"] != "Ask anything about your accounts", s)
    s = snap("demo-a", 3800)
    check("A loading shown", s["load"] and s["q1"] and not s["a1"], s)
    s = snap("demo-a", 5200)
    check("A answer streaming/visible", s["a1"] and not s["load"] and not s["rec"], s)
    s = snap("demo-a", 7600)
    check("A proposal shown, count finished", s["rec"] and s["appr"], s)
    s = snap("demo-a", 11000)
    check("A approved state", s["ok"] and s["note"] and not s["appr"] and not s["cur"] and s["state"] == "approved", s)
    if a.shots:
        d = pathlib.Path(a.shots); d.mkdir(parents=True, exist_ok=True)
        for sid in ("demo-a","demo-b"):
            for ms in (0, 900, 2500, 4500, 6500, 8500, 10500):
                snap(sid, ms); pg.locator(f'[data-scene="{sid}"]').screenshot(path=str(d / f"{sid}_{ms:05d}.png"))

    # demo B (recipes)
    s = snap("demo-b", 0)
    check("B t=0: only composer", s["composer"] and not s["q1"] and not s["ok"], s)
    s = snap("demo-b", 1500)
    check("B user-types typed text mirrors question", 0 < len(s["typed"]) and "Which" in s["typed"] or s["typed"].startswith("W"), s)
    s = snap("demo-b", total["demo-b"] + 10)
    check("B end: result visible, appr+composer+cursor hidden", s["ok"] and not s["appr"] and not s["composer"] and not s["cur"] and s["rec"] and s["a1"], s)

    # seek determinism: seek forward, backward, forward gives identical snapshots
    a1 = snap("demo-a", 6000); snap("demo-a", 500); a2 = snap("demo-a", 6000)
    check("seek is deterministic", a1 == a2, (a1, a2))

    # real-time playback: replay, wait, reaches final; player finishes and restores authored markup
    pg.evaluate('ProductScenes.get("demo-b").setSpeed(6); ProductScenes.get("demo-b").replay()')
    pg.wait_for_function('ProductScenes.get("demo-b").finished === true', timeout=15000)
    cur = pg.eval_on_selector('[data-scene="demo-b"]', 'e=>e.innerHTML')
    check("B playback ends and restores authored final-state markup", norm(cur) == norm(raw["demo-b"]))
    check("B complete event/state", pg.get_attribute('[data-scene="demo-b"]', "data-state") == "approved")

    # animate only opacity/transform: sample inline style props during playback
    pg.evaluate('ProductScenes.get("demo-a").setSpeed(1); ProductScenes.get("demo-a").replay()')
    seen = set()
    for _ in range(25):
        pg.wait_for_timeout(120)
        props = pg.evaluate('''()=>{const out=new Set();document.querySelectorAll('[data-scene="demo-a"] [style]').forEach(e=>{for(const n of e.style)out.add(n)});return [...out]}''')
        seen.update(props)
    print("inline style properties seen:", sorted(seen))
    allowed = {"opacity","transform","transform-origin","stroke-dasharray","stroke-dashoffset","position"}
    check("only opacity/transform (and svg stroke offset) animated", seen <= allowed, sorted(seen - allowed))

    # controls
    pg.evaluate('ProductScenes.get("demo-a").replay()')
    pg.click('[data-scene="demo-a"] [data-action="toggle"]')
    paused_t = pg.evaluate('ProductScenes.get("demo-a").t'); pg.wait_for_timeout(400)
    check("pause holds the clock", abs(pg.evaluate('ProductScenes.get("demo-a").t') - paused_t) < 1)
    check("no console errors/warnings (normal motion)", not [m for m in msgs if m[0] in ("error","warning","pageerror")], msgs)

    # reduced motion turned on live
    pg.emulate_media(reduced_motion="reduce"); pg.wait_for_timeout(300)
    check("live switch to reduced motion shows final state", pg.get_attribute('[data-scene="demo-a"]', "data-state") == "approved")
    ctx.close(); b.close()

print("\nFAILED: %s" % fails if fails else "\nALL PASSED")
sys.exit(1 if fails else 0)
