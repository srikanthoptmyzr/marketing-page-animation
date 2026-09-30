#!/usr/bin/env python3
"""Capture a Bookshop component from the site repo into the site kit.

Users of this skill have no repo access, so the kit must carry the real markup
and the real field names. This copies a component's authoritative template and
blueprint out of a read-only checkout and records the fields it accepts, so a
page can be assembled in Mode A without guessing.

  capture_component.py --repo DIR --name features-section [--name hero-solution ...]
  capture_component.py --repo DIR --all
  capture_component.py --repo DIR --used-by content/english/solutions-new/search/monitoring.md

Writes <kit>/components/<name>/: template.hugo.html (verbatim), fields.json
(blueprint fields, CloudCannon input types, which are translatable) and
component.md (a short human summary). Never writes to the repo.

Exit codes: 0 ok, 1 nothing captured, 2 usage error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FIELD_RE = re.compile(r'\{\{-?\s*\.([A-Za-z_][A-Za-z0-9_]*)')
RANGE_RE = re.compile(r'\{\{-?\s*range\s+(?:\$\w+,\s*\$\w+\s*:=\s*)?\.([A-Za-z_][A-Za-z0-9_]*)')
I18N_RE = re.compile(r'\{\{-?\s*i18n\s+"([^"]+)"')
PARTIAL_RE = re.compile(r'partial\s+"([^"]+)"')
BOOKSHOP_RE = re.compile(r'_bookshop_name:\s*([A-Za-z0-9_-]+)')


def load_key_lists(repo):
    """Read the site's translatable / skip key lists so the kit records them per field."""
    cfg = repo / "scripts/translation-scripts/translation/config.js"
    if not cfg.exists():
        return set(), set(), set()
    t = cfg.read_text(encoding="utf-8", errors="replace")

    def lst(name):
        m = re.search(name + r"\s*=\s*\[(.*?)\n\];", t, re.S)
        if not m:
            return set()
        return {a or b for a, b in re.findall(r"'([^']+)'|\"([^\"]+)\"", m.group(1))}

    return lst("translatableKeys"), lst("skipKeys"), lst("urlReplaceKeys")


def blueprint_fields(yml_text):
    """Field names and their defaults from the blueprint block, without a YAML dependency."""
    out, in_bp, base = {}, False, None
    for line in yml_text.splitlines():
        if re.match(r"^blueprint:", line):
            in_bp = True
            continue
        if in_bp and re.match(r"^[A-Za-z_]", line):
            break
        if not in_bp or not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^(\s+)([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if not m:
            m2 = re.match(r"^(\s+)-\s+([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
            if not m2:
                continue
            indent, key, val = m2.group(1) + "  ", m2.group(2), m2.group(3)
        else:
            indent, key, val = m.group(1), m.group(2), m.group(3)
        if base is None:
            base = len(indent)
        depth = max(0, (len(indent) - base) // 2)
        out.setdefault(key, {"default": val.strip().strip("'\""), "depth": depth})
    return out


def input_types(yml_text):
    out = {}
    m = re.search(r"^_inputs:(.*)$", yml_text, re.S | re.M)
    if not m:
        return out
    key = None
    for line in m.group(1).splitlines():
        km = re.match(r"^\s{2,}([A-Za-z_][A-Za-z0-9_]*):\s*$", line)
        if km:
            key = km.group(1)
            continue
        tm = re.match(r"^\s+type:\s*(\S+)", line)
        if tm and key:
            out.setdefault(key, tm.group(1))
    return out


def capture(repo, kit, name, keys):
    src = repo / "component-library" / "components" / name
    tpl = src / f"{name}.hugo.html"
    yml = src / f"{name}.bookshop.yml"
    if not tpl.exists():
        print(f"  skip {name}: no template at {tpl}", file=sys.stderr)
        return False

    tpl_text = tpl.read_text(encoding="utf-8", errors="replace")
    yml_text = yml.read_text(encoding="utf-8", errors="replace") if yml.exists() else ""
    translatable, skip, urlkeys = keys

    bp = blueprint_fields(yml_text)
    types = input_types(yml_text)
    used = sorted(set(FIELD_RE.findall(tpl_text)) | set(RANGE_RE.findall(tpl_text)))
    used = [f for f in used if f not in ("Params", "Site", "Page")]

    fields = {}
    for f in sorted(set(used) | set(bp)):
        fields[f] = {
            "usedInTemplate": f in used,
            "inBlueprint": f in bp,
            "default": bp.get(f, {}).get("default", None),
            "inputType": types.get(f),
            "localization": ("translatable" if f in translatable
                             else "skip" if f in skip
                             else "url-prefixed" if f in urlkeys
                             else "unlisted"),
        }

    out = kit / "components" / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "template.hugo.html").write_text(tpl_text)
    (out / "fields.json").write_text(json.dumps({
        "component": name,
        "source": f"component-library/components/{name}/",
        "fields": fields,
        "i18nKeys": sorted(set(I18N_RE.findall(tpl_text))),
        "partials": sorted(set(PARTIAL_RE.findall(tpl_text))),
    }, indent=1) + "\n")

    missing = [f for f, v in fields.items() if v["usedInTemplate"] and not v["inBlueprint"]]
    # An unlisted field is skipped by the SCRIPT translator (processor.js matches a
    # field's own key exactly; isParentTranslatable is honoured only for bare strings
    # directly inside an array, not for object-nested strings). The LLM localization
    # agent may still translate it, so the two paths can disagree. Only flag fields
    # that actually hold visible copy - an unlisted image path or flag is harmless.
    NON_TEXT = ("image", "img", "icon", "logo", "url", "link", "href", "path", "id",
                "color", "type", "style", "show_", "is_", "has_")
    untranslated = [f for f, v in fields.items()
                    if v["usedInTemplate"] and v["localization"] == "unlisted"
                    and not any(n in f.lower() for n in NON_TEXT)]
    lines = [f"# {name}", "",
             f"Captured verbatim from `component-library/components/{name}/`.",
             "", f"- Fields used by the template: {len(used)}",
             f"- Fields with a blueprint default: {len(bp)}"]
    if missing:
        lines.append(f"- **Template reads fields with no blueprint default:** {', '.join(missing)}")
    if untranslated:
        lines.append(f"- **Copy fields not in the translatable-key list:** {', '.join(untranslated)}. "
                     "The script translator (`scripts/translate.js`) matches a field's own key exactly, so it "
                     "skips these; the LLM localization agent usually translates them anyway. Parity therefore "
                     "depends on which path runs. Prefer a listed field name for new scene copy, and flag this "
                     "for the dev team.")
    if I18N_RE.findall(tpl_text):
        lines.append(f"- i18n keys: {', '.join(sorted(set(I18N_RE.findall(tpl_text))))}")
    if PARTIAL_RE.findall(tpl_text):
        lines.append(f"- Depends on partials: {', '.join(sorted(set(PARTIAL_RE.findall(tpl_text))))}")
    (out / "component.md").write_text("\n".join(lines) + "\n")
    print(f"  captured {name}: {len(fields)} field(s)"
          + (f", {len(untranslated)} copy field(s) not in the key list" if untranslated else ""))
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="read-only checkout of the site repo")
    ap.add_argument("--kit", default=None)
    ap.add_argument("--name", action="append", default=[], help="component to capture (repeatable)")
    ap.add_argument("--all", action="store_true", help="capture every component")
    ap.add_argument("--used-by", help="capture every component a content file references")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    kit = Path(args.kit) if args.kit else Path(__file__).resolve().parent.parent / "site-kit"
    comps = repo / "component-library" / "components"
    if not comps.is_dir():
        print(f"error: no component library at {comps}", file=sys.stderr)
        return 2

    names = list(args.name)
    if args.all:
        names += sorted(d.name for d in comps.iterdir() if d.is_dir())
    if args.used_by:
        f = Path(args.used_by)
        if not f.is_absolute():
            f = repo / f
        if not f.exists():
            print(f"error: no content file at {f}", file=sys.stderr)
            return 2
        names += BOOKSHOP_RE.findall(f.read_text(encoding="utf-8", errors="replace"))
    names = list(dict.fromkeys(names))
    if not names:
        print("error: give --name, --all or --used-by", file=sys.stderr)
        return 2

    keys = load_key_lists(repo)
    print(f"capturing {len(names)} component(s) into {kit / 'components'}")
    n = sum(capture(repo, kit, name, keys) for name in names)
    print(f"\n{n} captured, {len(names) - n} skipped")
    return 0 if n else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
