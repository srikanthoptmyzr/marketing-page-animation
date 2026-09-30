#!/usr/bin/env python3
"""Validate scene definitions against ui-scene-system.md section 12.

Usage:
  validate_scene.py SCENE.json [SCENE.json ...] [--content CONTENT.json ...]
                    [--json] [--strict]

A scene file may hold one scene object, {"scenes": [...]}, or a list of scenes.
--content takes one or more content files (one per language). When omitted, the
script looks for content*.json next to each scene file and says so.

Checks (errors unless marked warning)
  ids         component ids unique; children / parent refs exist
  types       type in the primitive/pattern vocabulary, or 'custom' + description
  content     every component `content` key and timeline `source` resolves in every
              content file; every entry has role (chrome|data), translate, sensitivity
  presentation  no literal text fields, colors or px sizes on components / state props
  states      exactly one `final`; `visible` and `props` ids exist; unreachable states (warning)
  timeline    ids unique; exactly one anchor (at | after | with); refs exist;
              no cycles; targets / states exist; last enter-state == final state;
              unknown verbs (warning: not in animation-system.md sections 4-5)
  responsive  designWidth, minTextPx, >= 1 variant with name/strategy; ids exist
  accessibility  name and description
  meta        id / version / claim / approximations / uncertainties (warnings)

Exit codes: 0 valid (warnings allowed unless --strict), 1 validation errors,
2 usage error or unreadable input.
"""
import argparse
import glob
import json
import os
import re
import sys

PRIMITIVES = ["frame", "header", "sidebar", "tabs", "list", "list-item", "card", "table", "chart", "message",
              "composer", "input", "button", "chip", "badge", "status", "avatar", "icon", "toggle", "menu",
              "tooltip", "modal", "notification", "cursor", "image", "text"]
PATTERNS = ["message", "chat", "dashboard", "metric", "chart", "table", "notification", "recommendation",
            "change-request", "approval", "success-state", "loading-state", "empty-state", "cursor", "tooltip"]
TYPES = set(PRIMITIVES) | set(PATTERNS) | {"custom"}
GENERIC_VERBS = {"reveal", "hide", "stagger", "count", "type", "stream", "draw", "highlight", "expand",
                 "collapse", "press", "move", "wait", "loop", "zoom", "zoom-out"}
RECIPES = {"user-types", "cursor-moves", "click", "hover", "select", "switch-tab", "scroll", "system-processes",
           "response-streams", "notification-arrives", "recommendation-appears", "approval-clicked",
           "success-state", "data-updates"}
VERBS = GENERIC_VERBS | RECIPES | {"enter-state"}
STRATEGIES = {"scale", "crop", "stack", "simplify", "shorten", "swap"}
PRIORITIES = {"essential", "normal", "optional"}
BASIS = {"observed", "inferred", "assumed"}
NO_TARGET_VERBS = {"enter-state", "loop", "wait", "zoom-out"}
LITERAL_TEXT_KEYS = {"text", "label", "title", "body", "caption", "placeholder", "heading", "value", "subtitle"}
PRESENTATION_KEYS = {"color", "background", "backgroundcolor", "bg", "fill", "stroke", "fontsize", "fontfamily",
                     "font", "style", "styles", "css", "class", "classname", "fontweight", "borderradius"}
COLOR_RE = re.compile(r"(#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch)\s*\()")
PX_RE = re.compile(r"(?<![\w-])-?\d+(?:\.\d+)?\s*px\b", re.I)
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+([-+].*)?$")


class Report:
    def __init__(self, name):
        self.name = name
        self.items = []

    def err(self, code, where, msg):
        self.items.append({"level": "error", "code": code, "where": where, "message": msg})

    def warn(self, code, where, msg):
        self.items.append({"level": "warning", "code": code, "where": where, "message": msg})

    @property
    def errors(self):
        return [i for i in self.items if i["level"] == "error"]

    @property
    def warnings(self):
        return [i for i in self.items if i["level"] == "warning"]


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def base_id(ref):
    return ref.split(".", 1)[0] if isinstance(ref, str) else ref


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        print("error: file not found: %s" % path, file=sys.stderr)
    except (OSError, ValueError) as e:
        print("error: cannot parse %s: %s" % (path, e), file=sys.stderr)
    sys.exit(2)


def unwrap_scenes(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("scenes"), list):
        return data["scenes"]
    return [data]


def unwrap_content(data):
    if isinstance(data, dict) and isinstance(data.get("content"), dict) and \
            set(data) <= {"content", "lang", "language", "locale", "$schema", "version"}:
        return data["content"]
    return data


# ---------------------------------------------------------------- component tree
def walk_components(comps, path, out, r, parent=None):
    if not isinstance(comps, list):
        r.err("components-shape", path, "components/children must be a list")
        return
    for i, c in enumerate(comps):
        p = "%s[%d]" % (path, i)
        if not isinstance(c, dict):
            r.err("component-shape", p, "component must be an object")
            continue
        out.append((c, p, parent))
        if "children" in c:
            walk_components(c["children"], p + ".children", out, r, c.get("id"))


def check_literals(value, where, r, key=None, top=False):
    """Colors / px sizes anywhere in the value; literal text and presentation keys on components."""
    if isinstance(value, dict):
        for k, v in value.items():
            if k == "children":
                continue
            if isinstance(k, str) and k.lower() in PRESENTATION_KEYS:
                r.err("presentation-field", "%s.%s" % (where, k),
                      "presentation field '%s' on a component; colors, fonts and sizes come from the theme" % k)
            check_literals(v, "%s.%s" % (where, k), r, k)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            check_literals(v, "%s[%d]" % (where, i), r, key)
    elif isinstance(value, str):
        if COLOR_RE.search(value):
            r.err("literal-color", where, "literal color value in scene.json; use a theme role")
        if PX_RE.search(value):
            r.err("literal-size", where, "literal px size in scene.json; sizes come from the theme/primitives")


# ---------------------------------------------------------------- main validation
def validate_scene(scene, idx, contents, r, content_note):
    if not isinstance(scene, dict):
        r.err("scene-shape", "scene", "scene must be an object")
        return
    # meta
    sid = scene.get("id")
    if not isinstance(sid, str) or not sid:
        r.err("meta-id", "id", "scene needs a string id")
    elif not KEBAB_RE.match(sid):
        r.warn("meta-id-format", "id", "id should be kebab-case")
    if "version" not in scene:
        r.warn("meta-version", "version", "missing version")
    elif not isinstance(scene["version"], str) or not SEMVER_RE.match(scene["version"]):
        r.warn("meta-version", "version", "version should be semver (e.g. 1.0.0)")
    if not scene.get("claim"):
        r.warn("meta-claim", "claim", "missing claim (the one thing the scene proves)")
    for k in ("approximations", "uncertainties"):
        if k not in scene:
            r.warn("meta-" + k, k, "no '%s' block; carry analysis assumptions here (empty list if none)" % k)
    # designWidth lives in `responsive` (authoritative); a `stage.designWidth` is optional

    # components
    comps_raw = scene.get("components")
    flat = []
    if not isinstance(comps_raw, list) or not comps_raw:
        r.err("components-missing", "components", "scene needs a non-empty components list")
    else:
        walk_components(comps_raw, "components", flat, r)
    ids = {}
    for c, p, parent in flat:
        cid = c.get("id")
        if not isinstance(cid, str) or not cid:
            r.err("component-id", p, "component needs a string id")
            continue
        if cid in ids:
            r.err("duplicate-component-id", p, "duplicate component id '%s' (first at %s)" % (cid, ids[cid]))
        else:
            ids[cid] = p
    content_keys_used = {}
    for c, p, parent in flat:
        cid = c.get("id", "?")
        t = c.get("type")
        if not isinstance(t, str) or not t:
            r.err("component-type", p, "component '%s' has no type" % cid)
        elif t not in TYPES:
            r.err("unknown-type", p, "component '%s' type '%s' is not in the vocabulary (primitives + patterns + custom)" % (cid, t))
        elif t == "custom" and not (isinstance(c.get("description"), str) and c["description"].strip()):
            r.err("custom-description", p, "custom component '%s' requires a description" % cid)
        if "parent" in c and c["parent"] not in ids and c["parent"] not in {x[0].get("id") for x in flat}:
            r.err("parent-missing", p, "parent '%s' does not exist" % c["parent"])
        if "priority" in c and c["priority"] not in PRIORITIES:
            r.err("priority", p, "priority must be one of essential|normal|optional")
        if "content" in c:
            if isinstance(c["content"], str) and c["content"]:
                content_keys_used.setdefault(c["content"], []).append(p)
            else:
                r.err("content-key", p, "content must be a non-empty string key, never literal text objects")
        for k in c:
            if isinstance(k, str) and k.lower() in LITERAL_TEXT_KEYS:
                r.err("literal-text", "%s.%s" % (p, k), "literal text field '%s' on a component; put text in the content file" % k)
        check_literals({k: v for k, v in c.items() if k != "content"}, p, r)

    # content resolution
    if contents:
        for key, places in content_keys_used.items():
            for cname, cdata in contents:
                if key not in cdata:
                    r.err("content-unresolved", places[0], "content key '%s' not found in %s" % (key, cname))
    else:
        if content_keys_used:
            r.warn("content-unchecked", "content", content_note)

    # states
    states = scene.get("states")
    state_ids = {}
    final = []
    if not isinstance(states, list) or not states:
        r.err("states-missing", "states", "scene needs a states list with exactly one final state")
        states = []
    for i, s in enumerate(states):
        p = "states[%d]" % i
        if not isinstance(s, dict) or not isinstance(s.get("id"), str):
            r.err("state-id", p, "state needs a string id")
            continue
        if s["id"] in state_ids:
            r.err("duplicate-state-id", p, "duplicate state id '%s'" % s["id"])
        state_ids[s["id"]] = p
        if not KEBAB_RE.match(s["id"]):
            r.warn("state-id-format", p, "state id '%s' should be kebab-case" % s["id"])
        if s.get("final") is True:
            final.append(s["id"])
        elif "final" in s and s["final"] is not False:
            r.err("state-final", p, "'final' must be true or omitted")
        if "basis" in s and s["basis"] not in BASIS:
            r.warn("basis", p, "basis should be observed|inferred|assumed")
        vis = s.get("visible")
        if not isinstance(vis, list):
            r.err("state-visible", p, "state '%s' needs a visible list" % s["id"])
        else:
            for v in vis:
                if v not in ids:
                    r.err("state-visible-missing", p, "visible id '%s' is not a component" % v)
        for pid in (s.get("props") or {}):
            if pid not in ids:
                r.err("state-props-missing", p, "props refer to unknown component '%s'" % pid)
        check_literals(s.get("props") or {}, p + ".props", r)
    if states:
        if len(final) != 1:
            r.err("final-state", "states", "exactly one state must be final (found %d)" % len(final))
    final_id = final[0] if len(final) == 1 else None

    # timeline
    tl = scene.get("timeline")
    steps = []
    if tl is None:
        if len(states) > 1:
            r.err("timeline-missing", "timeline", "scene has %d states but no timeline" % len(states))
    elif isinstance(tl, str):
        r.warn("timeline-external", "timeline", "timeline is a file reference ('%s'); steps not validated" % tl)
    elif not isinstance(tl, list):
        r.err("timeline-shape", "timeline", "timeline must be a list of steps")
    else:
        steps = tl
    step_idx = {}
    for i, st in enumerate(steps):
        if isinstance(st, dict) and isinstance(st.get("id"), str):
            if st["id"] in step_idx:
                r.err("duplicate-step-id", "timeline[%d]" % i, "duplicate step id '%s'" % st["id"])
            step_idx[st["id"]] = i
    deps = {}
    entered = []
    for i, st in enumerate(steps):
        p = "timeline[%d]" % i
        label = st.get("id", "#%d" % i) if isinstance(st, dict) else "#%d" % i
        if not isinstance(st, dict):
            r.err("step-shape", p, "step must be an object")
            continue
        verb = st.get("do")
        if not isinstance(verb, str) or not verb:
            r.err("step-verb", p, "step '%s' has no `do` verb" % label)
        elif verb not in VERBS:
            r.warn("unknown-verb", p, "verb '%s' is not in animation-system.md (generic motion, recipes, enter-state)" % verb)
        anchors = [k for k in ("at", "after", "with") if k in st]
        if len(anchors) != 1:
            r.err("step-anchor", p, "step '%s' needs exactly one of at | after | with (found %s)" % (label, anchors or "none"))
        for k in ("at", "delay", "duration"):
            if k in st and (not is_num(st[k]) or st[k] < 0):
                r.err("step-number", "%s.%s" % (p, k), "%s must be a non-negative number of ms" % k)
        deps[label] = []
        for k in ("after", "with"):
            if k in st:
                ref = st[k]
                if ref not in step_idx:
                    r.err("step-ref-missing", "%s.%s" % (p, k), "%s refers to unknown step '%s'" % (k, ref))
                else:
                    deps[label].append(ref)
                    if ref == st.get("id"):
                        r.err("step-cycle", p, "step '%s' refers to itself" % label)
                    elif step_idx[ref] > i:
                        r.warn("step-order", p, "step '%s' refers forward to '%s'; keep steps in causal order" % (label, ref))
        if "target" in st:
            # A step may address one component or several (the player staggers a list).
            for tgt in (st["target"] if isinstance(st["target"], list) else [st["target"]]):
                if base_id(tgt) not in ids:
                    r.err("step-target-missing", p + ".target", "target '%s' is not a component id" % tgt)
        elif verb and verb not in NO_TARGET_VERBS and not ("to" in st and verb in ("cursor-moves", "move", "zoom")):
            r.warn("step-no-target", p, "step '%s' (%s) has no target" % (label, verb))
        if "to" in st and base_id(st["to"]) not in ids:
            r.err("step-to-missing", p + ".to", "'to' refers to unknown component '%s'" % st["to"])
        if "source" in st:
            key = st["source"]
            if contents:
                for cname, cdata in contents:
                    if key not in cdata:
                        r.err("step-source-missing", p + ".source", "source content key '%s' not found in %s" % (key, cname))
            content_keys_used.setdefault(key, [])
        if verb == "enter-state":
            s = st.get("state")
            if s not in state_ids:
                r.err("step-state-missing", p + ".state", "enter-state refers to unknown state '%s'" % s)
            else:
                entered.append((i, s))
        elif "state" in st and st["state"] not in state_ids:
            r.err("step-state-missing", p + ".state", "unknown state '%s'" % st["state"])
        if "basis" in st and st["basis"] not in BASIS:
            r.warn("basis", p, "basis should be observed|inferred|assumed")
        if "essential" in st and not isinstance(st["essential"], bool):
            r.err("essential", p, "essential must be true/false")
    # cycles
    color = {}

    def dfs(n, stack):
        color[n] = 1
        for m in deps.get(n, []):
            if color.get(m) == 1:
                r.err("step-cycle", "timeline", "timing cycle: %s" % " -> ".join(stack + [n, m]))
                return True
            if color.get(m) is None and dfs(m, stack + [n]):
                return True
        color[n] = 2
        return False

    for n in list(deps):
        if color.get(n) is None:
            dfs(n, [])
    # approximate start times to find the final enter-state
    if steps and entered and final_id:
        start, end = {}, {}

        def t_start(label, depth=0):
            if label in start:
                return start[label]
            st = steps[step_idx[label]] if label in step_idx else {}
            if depth > 200:
                return 0
            d = st.get("delay", 0) if is_num(st.get("delay")) else 0
            if "at" in st and is_num(st["at"]):
                v = st["at"] + d
            elif "after" in st and st["after"] in step_idx:
                v = t_end(st["after"], depth + 1) + d
            elif "with" in st and st["with"] in step_idx:
                v = t_start(st["with"], depth + 1) + d
            else:
                v = d
            start[label] = v
            return v

        def t_end(label, depth=0):
            st = steps[step_idx[label]]
            du = st.get("duration", 0) if is_num(st.get("duration")) else 0
            return t_start(label, depth + 1) + du

        if not any(color.get(n) == 1 for n in color) and not [i for i in r.items if i["code"] == "step-cycle"]:
            best = None
            for i, s in entered:
                lab = steps[i].get("id")
                tv = t_start(lab) if lab in step_idx else i
                key = (tv, i)
                if best is None or key > best[0]:
                    best = (key, s)
            if best and best[1] != final_id:
                r.err("final-not-last", "timeline", "the last enter-state enters '%s', not the final state '%s'" % (best[1], final_id))
    elif final_id and len(states) > 1 and steps and not entered:
        r.err("no-enter-state", "timeline", "timeline never enters a state; the sequence must end in the final state '%s'" % final_id)
    if steps and states:
        first = states[0].get("id") if isinstance(states[0], dict) else None
        entered_ids = {s for _, s in entered}
        for sid_, p in state_ids.items():
            if sid_ != first and sid_ not in entered_ids:
                r.warn("state-unreachable", p, "state '%s' is never entered by the timeline" % sid_)

    # A target the timeline animates but no state ever makes visible. The player hides
    # every data-target the current state omits, so such an element is invisible for the
    # scene's whole life — the scene renders as an empty frame and nothing errors. This
    # is only catchable here: the runtime has no way to know it was meant to show.
    shown = set()
    for st_ in scene.get("states", []):
        for vid in st_.get("visible", []) or []:
            shown.add(base_id(vid))
    animated = set()
    for st_ in scene.get("timeline", []):
        tgt = st_.get("target")
        if tgt is None:
            continue
        for one in (tgt if isinstance(tgt, list) else [tgt]):
            animated.add(base_id(one))
    for tid in sorted(animated - shown):
        if tid in ("cur", "cursor"):
            continue          # the pointer is deliberately outside the state machine
        r.err("target-never-visible", "states",
              "'%s' is animated by the timeline but no state lists it as visible, so the "
              "player keeps it hidden for the whole scene" % tid)

    # content usage
    if contents:
        used = set(content_keys_used)
        for cname, cdata in contents:
            for key, entry in cdata.items():
                p = "%s:%s" % (os.path.basename(cname), key)
                if not isinstance(entry, dict):
                    r.err("content-entry", p, "content entry must be an object")
                    continue
                if entry.get("role") not in ("chrome", "data"):
                    r.err("content-role", p, "content entry needs role: chrome | data")
                if "translate" not in entry or not isinstance(entry["translate"], (bool, dict)):
                    r.err("content-translate", p, "content entry needs translate (true/false or per-field object)")
                if not isinstance(entry.get("sensitivity"), str) or not entry["sensitivity"]:
                    r.err("content-sensitivity", p, "content entry needs a sensitivity class (e.g. 'none')")
                if key not in used:
                    r.warn("content-unused", p, "content key '%s' is not used by any component or step" % key)

    # responsive
    resp = scene.get("responsive")
    if not isinstance(resp, dict):
        r.err("responsive-missing", "responsive", "scene needs a responsive block")
    else:
        if not is_num(resp.get("designWidth")) or resp["designWidth"] <= 0:
            r.err("responsive-designWidth", "responsive.designWidth", "responsive.designWidth must be a positive number")
        if not is_num(resp.get("minTextPx")) or resp["minTextPx"] <= 0:
            r.err("responsive-minTextPx", "responsive.minTextPx", "responsive.minTextPx (legibility limit) must be a positive number")
        elif resp["minTextPx"] < 11:
            r.warn("responsive-minTextPx", "responsive.minTextPx", "minTextPx below 11 is below the legibility limit")
        vs = resp.get("variants")
        if not isinstance(vs, list) or not vs:
            r.err("responsive-variants", "responsive.variants", "at least one responsive variant is required")
        else:
            for i, v in enumerate(vs):
                p = "responsive.variants[%d]" % i
                if not isinstance(v, dict):
                    r.err("variant-shape", p, "variant must be an object")
                    continue
                if not v.get("name"):
                    r.err("variant-name", p, "variant needs a name")
                if v.get("strategy") not in STRATEGIES:
                    r.err("variant-strategy", p, "strategy must be one of %s" % "|".join(sorted(STRATEGIES)))
                if not is_num(v.get("below")):
                    r.err("variant-below", p, "variant needs `below` (container width in px) as a number")
                for k in ("hide", "keep", "show", "affects", "components"):
                    for ref in v.get(k) or []:
                        if base_id(ref) not in ids:
                            r.err("variant-ref", "%s.%s" % (p, k), "refers to unknown component '%s'" % ref)
                for ref in v.get("hide") or []:
                    comp = next((c for c, _, _ in flat if c.get("id") == ref), None)
                    if comp and comp.get("priority") == "essential":
                        r.err("variant-hides-essential", p, "variant hides essential component '%s'" % ref)

    # accessibility
    a11y = scene.get("accessibility")
    if not isinstance(a11y, dict):
        r.err("a11y-missing", "accessibility", "scene needs an accessibility block")
    else:
        for k in ("name", "description"):
            if not isinstance(a11y.get(k), str) or not a11y[k].strip():
                r.err("a11y-" + k, "accessibility." + k, "accessibility.%s is required" % k)
        loops = any(isinstance(s, dict) and s.get("do") == "loop" for s in steps)
        if loops and not a11y.get("controls"):
            r.warn("a11y-controls", "accessibility", "looping scene: declare play/pause/replay controls in accessibility.controls")


def find_content(scene_path):
    d = os.path.dirname(os.path.abspath(scene_path))
    return sorted(glob.glob(os.path.join(d, "content*.json")))


def build_parser():
    p = argparse.ArgumentParser(
        description="Validate scene definitions against ui-scene-system.md section 12.",
        epilog="Exit codes: 0 valid, 1 errors found, 2 usage/input error.")
    p.add_argument("scene", nargs="+", help="scene JSON file(s): one scene, {'scenes': [...]}, or a list")
    p.add_argument("--content", nargs="+", metavar="PATH", help="content file(s) (one per language) the scenes must resolve in")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--strict", action="store_true", help="treat warnings as failures")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    reports = []
    explicit = None
    if a.content:
        explicit = [(c, unwrap_content(load_json(c))) for c in a.content]
        for c, d in explicit:
            if not isinstance(d, dict):
                print("error: content file %s must be an object keyed by content key" % c, file=sys.stderr)
                return 2
    for path in a.scene:
        data = load_json(path)
        scenes = unwrap_scenes(data)
        if explicit is not None:
            contents, note = explicit, ""
        else:
            found = find_content(path)
            contents = [(c, unwrap_content(load_json(c))) for c in found]
            contents = [(c, d) for c, d in contents if isinstance(d, dict)]
            note = "no --content given and no content*.json next to the scene; content keys not resolved"
        for i, sc in enumerate(scenes):
            name = path if len(scenes) == 1 else "%s#%d" % (path, i)
            if isinstance(sc, dict) and isinstance(sc.get("id"), str):
                name += " (%s)" % sc["id"]
            r = Report(name)
            validate_scene(sc, i, contents, r, note)
            reports.append(r)
    failed = any(r.errors or (a.strict and r.warnings) for r in reports)
    if a.json:
        print(json.dumps({"ok": not failed,
                          "scenes": [{"scene": r.name, "errors": len(r.errors), "warnings": len(r.warnings),
                                      "findings": r.items} for r in reports]}, indent=2))
    else:
        for r in reports:
            print("%s: %s (%d error(s), %d warning(s))" % (r.name, "FAIL" if r.errors or (a.strict and r.warnings) else "ok",
                                                          len(r.errors), len(r.warnings)))
            for it in r.errors + r.warnings:
                print("  %-7s %-24s %s: %s" % (it["level"], it["code"], it["where"], it["message"]))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
