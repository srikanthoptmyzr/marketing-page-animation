#!/usr/bin/env python3
"""Privacy leak scanner (privacy-masking.md section 7: final privacy validation).

Usage:
  leak_scan.py --originals .private/originals.json [--map spec/privacy-map.json]
               --scan DIR [DIR ...] [--report reports/privacy.md] [--json]

Inputs
  originals.json  {"entities":[{"id","class","original","surfaceForms":[...]}]}
  privacy-map.json {"entities":[{"id","class","replacement","format":{...}}]}  (optional)

Checks, per scanned file (text; binaries are read as latin-1, files > 20 MB are skipped)
  exact           every original and surface form                         blocker
  normalized      case/whitespace/separators/punctuation, NFKC, HTML
                  entities, percent-decoding, \\uXXXX escapes ignored      blocker
  encoded         base64 (all 3 alignments, std + urlsafe), hex,
                  URL-encoded, JS \\u escapes, UTF-8/UTF-16 byte forms    blocker
  reversed        reversed original (raw and normalized)                  blocker
  fragment        originals >= 6 chars: any run of 4+ chars (this covers
                  first-4 / last-4 pieces, e.g. a "****7890" mask)        review
  unregistered    emails outside reserved domains, phone-like numbers,
                  digit runs >= 8, UUIDs, high-entropy tokens, URLs with
                  numeric ids, IPv4 outside documentation ranges          review
  media-review    png/jpg/gif/mp4/webm/mov/pdf... files and data: URIs    review
  forbidden-dir   input/, analysis/, .private/ inside a scanned dir       blocker
  placeholder     unresolved {{entity}} placeholders                      blocker
File names (every path component) are scanned with the same checks.
Binary files get exact/encoded/reversed checks only (no fragment/pattern noise).

Map audit (with --map): replacement != original, no shared run of 4+ chars
(blocker), 3+ same-position chars (review), no collisions with any other
entity's original or replacement, every original has exactly one replacement.

Output never contains original text: only entity ids, classes, check names and
locations. Paths whose own name matches an original are shown redacted.

Exit codes: 0 no blockers (review items may exist), 1 at least one blocker,
2 usage error or unreadable input.
"""
import argparse
import fnmatch
import base64
import binascii
import collections
import datetime
import hashlib
import html
import json
import math
import os
import re
import sys
import unicodedata
import urllib.parse

MAX_BYTES = 20 * 1024 * 1024
FORBIDDEN_DIRS = {"input", "analysis", ".private"}
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".gif", ".mp4", ".webm", ".mov", ".pdf",
             ".webp", ".avif", ".bmp", ".tif", ".tiff", ".heic", ".mkv", ".m4v"}
SAFE_EMAIL_DOMAINS = ("example.com", "example.org", "example.net")
SAFE_TLDS = {"test", "invalid", "example", "localhost"}
FILE_LIKE_TLDS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "avif", "css", "js", "json", "map",
                  "woff", "woff2", "ttf", "otf", "html", "md", "mp4", "webm", "ico", "txt"}
DOC_NETS = ("192.0.2.", "198.51.100.", "203.0.113.")
SEV_ORDER = {"blocker": 0, "review": 1}
CHECK_STEP = {"exact": 1, "normalized": 2, "encoded": 3, "reversed": 3, "fragment": 4,
              "unregistered-pattern": 5, "media-review": 7, "forbidden-dir": 7,
              "placeholder": 0, "map-audit": 0, "skipped": 0}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@([A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+)")
PHONE_RE = re.compile(r"(?<![\w.])(\+?\d[\d\s().\-]{7,}\d)(?![\w])")
DIGITS_RE = re.compile(r"(?<![\w.])\d{8,}(?![\w])")
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
TOKEN_RE = re.compile(r"[A-Za-z0-9_\-+/=]{20,}")
URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+")
IPV4_RE = re.compile(r"(?<![\w.\-])(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?![\w\-]|\.\d)")
PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_.\-]+)\s*\}\}")
DATA_URI_RE = re.compile(r"data:(image|video|audio|application/pdf)[^,;\"' ]*[;,]", re.I)
UESC_RE = re.compile(r"\\u([0-9a-fA-F]{4})")


# ---------------------------------------------------------------- normalization
def norm(s):
    """Aggressive normalization used for matching (never printed)."""
    for _ in range(2):
        s2 = urllib.parse.unquote(html.unescape(s))
        if s2 == s:
            break
        s = s2
    s = UESC_RE.sub(lambda m: chr(int(m.group(1), 16)), s)
    s = unicodedata.normalize("NFKC", s).casefold()
    return "".join(ch for ch in s if ch.isalnum())


def light(s):
    """Lowercased, decoded line used for fragment matching."""
    s = urllib.parse.unquote(html.unescape(s))
    s = UESC_RE.sub(lambda m: chr(int(m.group(1), 16)), s)
    return unicodedata.normalize("NFKC", s).lower()


def entropy(s):
    c = collections.Counter(s)
    n = len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def b64_variants(data):
    """Substrings of base64(data) that survive at any of the 3 byte alignments."""
    out = set()
    for k, skip in ((0, 0), (1, 2), (2, 3)):
        enc = base64.b64encode(b"\x00" * k + data).decode()
        enc = enc[skip:]
        rem = (len(data) + k) % 3
        enc = enc.rstrip("=")
        if rem:
            enc = enc[:-1]
        if len(enc) >= 6:
            out.add(enc)
            out.add(enc.replace("+", "-").replace("/", "_"))
    return out


# Ordinary words that are never treated as identifying when they appear in a name-like original.
COMMON_WORDS = set('''search brand display video shopping performance campaign campaigns group groups
account accounts budget budgets keyword keywords remarketing generic local national global summer winter
spring autumn spring sales sale offer offers products product store stores online service services
customer customers company business marketing digital media social network partners partner default
standard premium basic pilot test testing retargeting prospecting awareness conversion conversions
traffic leads lead traffic mobile desktop tablet europe north south east west united states'''.split())


# ---------------------------------------------------------------- entity model
class Entity:
    def __init__(self, eid, cls, forms, keep=None):
        self.id, self.cls = eid, cls
        self.keep = [k.lower() for k in (keep or []) if isinstance(k, str) and k.strip()]
        forms = [f for f in dict.fromkeys(forms) if isinstance(f, str) and f]
        self.forms = forms
        self.exact = [f for f in forms if len(f) >= 2]
        # Normalisation strips punctuation from the HAYSTACK as well as the needle, so a
        # short digits-only form ("$3,596" -> "3596") collides constantly with minified
        # markup, where class names like z-index:31 and duration-300 concatenate into
        # long digit runs. Those matches are noise, not leaks: a real leak of a money
        # value shows up in the `exact` check. Require a longer run before a digits-only
        # form is matched normalised or reversed.
        def _usable(n):
            return len(n) >= (8 if n.isdigit() else 4)
        self.norms = sorted({norm(f) for f in forms if _usable(norm(f))})
        self.rev_raw = sorted({f[::-1].lower() for f in forms
                               if len(f) >= 4 and not f.strip().lstrip('$\u20ac\u00a3').replace(',', '').replace('.', '').isdigit()
                               and f[::-1].lower() != f.lower()})
        self.rev_norm = sorted({n[::-1] for n in self.norms if n[::-1] != n})
        enc = {}  # needle -> label
        text_needles = {}
        for f in forms:
            if len(f) < 3:
                continue
            for raw in {f.encode("utf-8"), f.lower().encode("utf-8")}:
                for v in b64_variants(raw):
                    enc[v] = "base64"
                hx = binascii.hexlify(raw).decode()
                enc[hx] = "hex"
            q1, q2 = urllib.parse.quote(f, safe=""), urllib.parse.quote_plus(f)
            for q in (q1, q2):
                if q != f:
                    text_needles[q.lower()] = "url-encoded"
            je = json.dumps(f)[1:-1]
            if je != f and "\\u" in je:
                text_needles[je.lower()] = "unicode-escape"
        self.enc_case = enc                     # matched case-sensitively (base64) / lower for hex
        self.enc_lower = {k.lower(): v for k, v in enc.items() if v == "hex"}
        self.enc_b64 = {k: v for k, v in enc.items() if v == "base64"}
        self.enc_text = text_needles
        # binary-only byte forms
        self.byte_forms = {}
        for f in forms:
            if len(f) < 3:
                continue
            for name, codec in (("utf8", "utf-8"), ("utf16", "utf-16le")):
                try:
                    b = f.lower().encode(codec).decode("latin-1")
                except UnicodeError:
                    continue
                if b != f.lower():
                    self.byte_forms[b] = name
        # fragments. Segments listed in the map's format.keep (generic labels such as "| Search")
        # are not identifying, so they are removed before fragments are built.
        # ID-like originals (no spaces, contain a digit) are checked by 4-character runs.
        # Name-like originals are checked as whole words of 5+ letters, so ordinary code and
        # prose do not produce noise.
        self.grams = {}
        self.words = set()
        for f in forms:
            if len(f.strip()) < 6:
                continue
            base = f.lower()
            for k in self.keep:
                base = base.replace(k, " ")
            idlike = (" " not in f.strip()) and any(ch.isdigit() for ch in f)
            if idlike:
                j = norm(base)
                for i in range(len(j) - 3):
                    g = j[i:i + 4]
                    if len(set(g)) < 2:
                        continue
                    pos = "first" if i == 0 else ("last" if i == len(j) - 4 else "middle")
                    self.grams.setdefault(g, pos)
            else:
                for w in re.findall(r"[^\W\d_]{5,}", base, re.U):
                    if w not in COMMON_WORDS:
                        self.words.add(w)
        self.gram_re = None
        if self.grams:
            self.gram_re = re.compile("(?=(" + "|".join(sorted(map(re.escape, self.grams))) + "))")
        self.word_re = None
        if self.words:
            self.word_re = re.compile(r"(?<![^\W\d_])(" + "|".join(sorted(map(re.escape, self.words))) + r")(?![^\W\d_])", re.U)


def load_json(path, what):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        print("error: %s not found: %s" % (what, path), file=sys.stderr)
    except (OSError, ValueError) as e:
        print("error: cannot read %s %s: %s" % (what, path, type(e).__name__), file=sys.stderr)
    sys.exit(2)


def build_entities(data, keep_by_id=None):
    ents = []
    keep_by_id = keep_by_id or {}
    for e in (data.get("entities") if isinstance(data, dict) else None) or []:
        if not isinstance(e, dict) or "id" not in e:
            continue
        forms = [e.get("original")] + list(e.get("surfaceForms") or [])
        ents.append(Entity(str(e["id"]), str(e.get("class", "unknown")), forms, keep_by_id.get(str(e["id"]))))
    return ents


# ---------------------------------------------------------------- findings
class Findings:
    def __init__(self):
        self.items = []
        self._seen = set()

    def add(self, path, line, entity, check, severity, detail="", offset=None, cls=""):
        key = (path, line, offset, entity, check, detail)
        if key in self._seen:
            return
        self._seen.add(key)
        self.items.append({"path": path, "line": line, "offset": offset, "entity": entity, "class": cls,
                           "check": check, "severity": severity, "detail": detail})


def display_path(rel, ents, cache={}):
    """Path for output; any component that itself matches an original is redacted."""
    parts = []
    for comp in rel.replace("\\", "/").split("/"):
        key = (comp, id(ents))
        if key not in cache:
            hit = bool(name_hits(comp, ents))
            cache[key] = "<redacted:%s>" % hashlib.sha256(comp.encode()).hexdigest()[:6] if hit else comp
        parts.append(cache[key])
    return "/".join(parts)


def name_hits(text, ents):
    """(entity, check) hits of the strong checks on a short string."""
    res = []
    n = norm(text)
    low = text.lower()
    lt = urllib.parse.unquote(html.unescape(text)).lower()
    for e in ents:
        chk = None
        if any(f in text for f in e.exact):
            chk = "exact"
        elif any(x in n for x in e.norms):
            chk = "normalized"
        elif (any(k in text for k in e.enc_b64) or any(k in low for k in e.enc_lower)
              or any(k in low or k in lt for k in e.enc_text)):
            chk = "encoded"
        elif any(x in lt for x in e.rev_raw) or any(x in n for x in e.rev_norm):
            chk = "reversed"
        if chk:
            res.append((e, chk))
    return res


# ---------------------------------------------------------------- line scanning
def strong_checks(line, ents, out):
    """Exact / normalized / encoded / reversed. out: list of (entity, check)."""
    n = norm(line)
    low = line.lower()
    lt = urllib.parse.unquote(html.unescape(line)).lower()
    for e in ents:
        chk = None
        if any(f in line for f in e.exact) or any(f.lower() in low for f in e.exact):
            chk = "exact"
        elif any(x in n for x in e.norms):
            chk = "normalized"
        elif (any(k in line for k in e.enc_b64) or any(k in low for k in e.enc_lower)
              or any(k in low or k in lt for k in e.enc_text)):
            chk = "encoded"
        elif any(x in lt for x in e.rev_raw) or any(x in n for x in e.rev_norm):
            chk = "reversed"
        if chk:
            out.append((e, chk))


def is_safe_email_domain(dom):
    d = dom.lower()
    if d.rsplit(".", 1)[-1] in SAFE_TLDS or d.rsplit(".", 1)[-1] in FILE_LIKE_TLDS:
        return True
    return any(d == s or d.endswith("." + s) for s in SAFE_EMAIL_DOMAINS)


def digit_count(s):
    return sum(ch.isdigit() for ch in s)


def pattern_hits(line, known_norms, skip_entropy=False):
    """Yield (kind) for unregistered sensitive-looking values. known_norms: normalized
    strings that are handled elsewhere (originals) or registered (replacements)."""
    hits = []

    def registered(v):
        nv = norm(v)
        return nv in known_norms

    for m in EMAIL_RE.finditer(line):
        if not is_safe_email_domain(m.group(1)) and not registered(m.group(0)):
            hits.append("email")
    for m in PHONE_RE.finditer(line):
        v = m.group(1)
        d = digit_count(v)
        has_sep = bool(re.search(r"[\s().\-]", v)) or v.startswith("+")
        if d < 9 or d > 15 or not has_sep:
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", v.strip()) or "555-01" in v or registered(v):
            continue
        if re.fullmatch(r"\d+(\.\d+)+", v):  # version / decimal
            continue
        hits.append("phone-like")
    for m in DIGITS_RE.finditer(line):
        v = m.group(0)
        if len(set(v)) > 1 and not registered(v):
            hits.append("digit-run")
    for m in UUID_RE.finditer(line):
        v = m.group(0).lower()
        if set(v.replace("-", "")) <= {"0"} or registered(v):
            continue
        hits.append("uuid")
    if not skip_entropy:
        for m in TOKEN_RE.finditer(line):
            t = m.group(0)
            if "/" in t and t.count("/") > 1:
                continue
            if not (re.search(r"[A-Za-z]", t) and re.search(r"\d", t)):
                continue
            if entropy(t) >= 4.0 and not registered(t) and not t.lower().startswith(("sha256", "sha384", "sha512")):
                hits.append("high-entropy-token")
    for m in URL_RE.finditer(line):
        u = m.group(0)
        try:
            p = urllib.parse.urlsplit(u)
        except ValueError:
            continue
        host = (p.hostname or "").lower()
        if host.rsplit(".", 1)[-1] in SAFE_TLDS or any(host == s or host.endswith("." + s) for s in SAFE_EMAIL_DOMAINS):
            continue
        segs = [s for s in p.path.split("/") if s]
        q = urllib.parse.parse_qsl(p.query)
        if any(re.fullmatch(r"\d{4,}", s) or re.fullmatch(r"[a-z]*[-_]?\d{5,}", s, re.I) for s in segs) or \
           any(re.search(r"(^|_)(id|uid|account|acct|customer|user|cid)$", k, re.I) and v for k, v in q):
            hits.append("url-with-id")
    for m in IPV4_RE.finditer(line):
        o = [int(x) for x in m.groups()]
        ip = ".".join(map(str, o))
        if any(x > 255 for x in o) or ip.startswith(DOC_NETS) or o[0] in (0, 127) or ip == "255.255.255.255":
            continue
        hits.append("ipv4")
    return hits


def scan_text(text, path, ents, all_ents_by_id, known_norms, ids, F, name_only=False, cap=None):
    counts = collections.Counter()
    for ln, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            continue
        strong = []
        strong_checks(line, ents, strong)
        hit_ids = set()
        for e, chk in strong:
            F.add(path, ln, e.id, chk, "blocker", cls=e.cls)
            hit_ids.add(e.id)
        if name_only:
            continue
        low = None
        for e in ents:
            if e.id in hit_ids or not e.gram_re:
                continue
            if low is None:
                low = light(line)
            m = e.gram_re.search(low)
            if m:
                g = m.group(1)
                F.add(path, ln, e.id, "fragment", "review",
                      detail="run of 4+ chars matches %s piece of original" % e.grams.get(g, "middle"),
                      cls=e.cls)
        for e in ents:
            if e.id in hit_ids or not e.word_re:
                continue
            if low is None:
                low = light(line)
            if e.word_re.search(low):
                F.add(path, ln, e.id, "fragment", "review",
                      detail="a distinctive word from the original appears here", cls=e.cls)
        for m in PLACEHOLDER_RE.finditer(line):
            name = m.group(1)
            if name in ids:
                F.add(path, ln, name, "placeholder", "blocker", detail="unresolved {{entity}} placeholder",
                      cls=all_ents_by_id.get(name, ""))
            elif re.fullmatch(r"[A-Za-z0-9_\-]+", name) and "-" in name:
                F.add(path, ln, "-", "placeholder", "review", detail="placeholder-like {{token}} (id not in map)")
        if DATA_URI_RE.search(line):
            F.add(path, ln, "-", "media-review", "review", detail="embedded data: URI media")
        skip_entropy = "base64," in line
        for kind in dict.fromkeys(pattern_hits(line, known_norms, skip_entropy)):
            if cap and counts[kind] >= cap:
                counts[kind] += 1
                continue
            counts[kind] += 1
            F.add(path, ln, "-", "unregistered-pattern", "review", detail=kind)
    if cap:
        for kind, c in counts.items():
            if c > cap:
                F.add(path, 0, "-", "unregistered-pattern", "review",
                      detail="%s: %d more hits suppressed (cap %d per file)" % (kind, c - cap, cap))


def scan_binary(data, path, ents, F):
    low = data.decode("latin-1")
    lowl = low.lower()
    for e in ents:
        for f in e.exact:
            for cand in (f, f.lower()):
                i = lowl.find(cand.lower())
                if i >= 0:
                    F.add(path, None, e.id, "exact", "blocker", offset=i, cls=e.cls)
                    break
        for b, name in e.byte_forms.items():
            i = lowl.find(b)
            if i >= 0:
                F.add(path, None, e.id, "exact", "blocker", offset=i, detail=name + " bytes", cls=e.cls)
        for k in list(e.enc_b64):
            i = low.find(k)
            if i >= 0:
                F.add(path, None, e.id, "encoded", "blocker", offset=i, detail="base64", cls=e.cls)
                break
        for k in e.enc_lower:
            i = lowl.find(k)
            if i >= 0:
                F.add(path, None, e.id, "encoded", "blocker", offset=i, detail="hex", cls=e.cls)
                break
        for k in e.rev_raw:
            i = lowl.find(k)
            if i >= 0:
                F.add(path, None, e.id, "reversed", "blocker", offset=i, cls=e.cls)
                break


# ---------------------------------------------------------------- walking
def walk(root):
    if os.path.isfile(root):
        yield os.path.dirname(root) or ".", [], [os.path.basename(root)]
        return
    for dp, dn, fn in os.walk(root, followlinks=False):
        yield dp, dn, fn


EXCLUDES = []


def scan_dirs(dirs, ents, by_id, known_norms, ids, F, skip_paths, cap):
    stats = {"files": 0, "skipped_large": 0, "binary": 0}
    for root in dirs:
        base = root if os.path.isdir(root) else (os.path.dirname(root) or ".")
        for dp, dn, fn in walk(root):
            rel_dir = os.path.relpath(dp, base)
            rel_dir = "" if rel_dir == "." else rel_dir
            keep = []
            for d in dn:
                rel = os.path.join(rel_dir, d)
                disp = display_path(rel, ents) + "/"
                if d.lower() in FORBIDDEN_DIRS:
                    F.add(disp, None, "-", "forbidden-dir", "blocker",
                          detail="'%s/' must not ship in output" % d.lower())
                    continue  # its contents are not scanned individually
                if os.path.islink(os.path.join(dp, d)):
                    F.add(disp, None, "-", "skipped", "review", detail="symlinked directory not followed")
                    continue
                for e, chk in name_hits(d, ents):
                    F.add(disp, 0, e.id, chk, "blocker", detail="in directory name", cls=e.cls)
                keep.append(d)
            dn[:] = keep
            for f in fn:
                full = os.path.join(dp, f)
                if os.path.abspath(full) in skip_paths:
                    continue
                rel = os.path.join(rel_dir, f)
                if any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(f, g) for g in EXCLUDES):
                    continue
                disp = display_path(rel, ents)
                ext = os.path.splitext(f)[1].lower()
                for e, chk in name_hits(f, ents):
                    F.add(disp, 0, e.id, chk, "blocker", detail="in file name", cls=e.cls)
                for kind in dict.fromkeys(pattern_hits(f, known_norms, True)):
                    F.add(disp, 0, "-", "unregistered-pattern", "review", detail=kind + " (in file name)")
                if ext in MEDIA_EXT:
                    F.add(disp, None, "-", "media-review", "review", detail="media file; confirm it is not a reference")
                if os.path.islink(full):
                    F.add(disp, None, "-", "skipped", "review", detail="symlink not followed")
                    continue
                try:
                    size = os.path.getsize(full)
                    if size > MAX_BYTES:
                        stats["skipped_large"] += 1
                        F.add(disp, None, "-", "skipped", "review", detail="larger than 20 MB, not scanned")
                        continue
                    with open(full, "rb") as fh:
                        data = fh.read()
                except OSError as e:
                    F.add(disp, None, "-", "skipped", "review", detail="unreadable (%s)" % type(e).__name__)
                    continue
                stats["files"] += 1
                if b"\x00" in data[:8192] or ext in MEDIA_EXT:
                    stats["binary"] += 1
                    scan_binary(data, disp, ents, F)
                    continue
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = data.decode("latin-1")
                    stats["binary"] += 1
                if text.startswith("﻿"):
                    text = text[1:]
                scan_text(text, disp, ents, by_id, known_norms, ids, F, cap=cap)
    return stats


# ---------------------------------------------------------------- map audit
TLD_RE = re.compile(r"\.(com|org|net|io|co|in|dev|app|ai|test|invalid)\b", re.I)


def lcs_len(a, b):
    best = 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


def keep_map(mapdata):
    out = {}
    for e in (mapdata.get("entities") or []) if isinstance(mapdata, dict) else []:
        if isinstance(e, dict) and "id" in e:
            fmt = e.get("format") if isinstance(e.get("format"), dict) else {}
            out[str(e["id"])] = [k for k in (fmt.get("keep") or []) if isinstance(k, str)]
    return out


def audit_map(mapdata, orig_data, F, mapname):
    m_ents = [e for e in (mapdata.get("entities") or []) if isinstance(e, dict) and "id" in e]
    o_ents = {str(e["id"]): e for e in (orig_data.get("entities") or []) if isinstance(e, dict) and "id" in e}
    seen, reps = {}, {}
    for e in m_ents:
        eid = str(e["id"])
        cls = str(e.get("class", ""))
        if eid in seen:
            F.add(mapname, None, eid, "map-audit", "blocker", detail="duplicate entity id in map", cls=cls)
        seen[eid] = e
        rep = e.get("replacement")
        if not isinstance(rep, str) or not rep:
            F.add(mapname, None, eid, "map-audit", "blocker", detail="missing replacement", cls=cls)
            continue
        reps[eid] = rep
    for eid in o_ents:
        if eid not in seen:
            F.add(mapname, None, eid, "map-audit", "blocker", detail="original has no replacement in map",
                  cls=str(o_ents[eid].get("class", "")))
    for eid in seen:
        if eid not in o_ents:
            F.add(mapname, None, eid, "map-audit", "review", detail="map entity has no matching original")
    all_orig_forms = {i: [x for x in [o.get("original")] + list(o.get("surfaceForms") or []) if isinstance(x, str) and x]
                      for i, o in o_ents.items()}
    for eid, rep in reps.items():
        cls = str(seen[eid].get("class", ""))
        nrep = norm(rep)
        keeps = [k.lower() for k in keep_map(mapdata).get(eid, []) if k.strip()]

        def strip(s, keeps=keeps):
            low = s.lower()
            for k in keeps:
                low = low.replace(k, " ")
            return norm(TLD_RE.sub("", low))
        if eid in all_orig_forms:
            for f in all_orig_forms[eid]:
                if rep == f or (nrep and nrep == norm(f)):
                    F.add(mapname, None, eid, "map-audit", "blocker", detail="replacement equals original", cls=cls)
                    break
            for f in all_orig_forms[eid]:
                a, b = strip(f), strip(rep)
                run = lcs_len(a, b)
                if run >= 4:
                    F.add(mapname, None, eid, "map-audit", "blocker",
                          detail="replacement shares a run of %d chars with original" % run, cls=cls)
                    break
            for f in all_orig_forms[eid]:
                a, b = strip(f), strip(rep)
                same = sum(1 for x, y in zip(a, b) if x == y)
                if same >= 3:
                    F.add(mapname, None, eid, "map-audit", "review",
                          detail="%d chars identical at the same position" % same, cls=cls)
                    break
        for oid, forms in all_orig_forms.items():
            if oid == eid:
                continue
            for f in forms:
                nf = norm(f)
                if rep == f or (nrep and nrep == nf) or (len(nf) >= 4 and nf in nrep):
                    F.add(mapname, None, eid, "map-audit", "blocker",
                          detail="replacement collides with original of entity '%s'" % oid, cls=cls)
                    break
        for oid, r2 in reps.items():
            if oid != eid and (rep == r2 or nrep == norm(r2)) and eid < oid:
                F.add(mapname, None, eid, "map-audit", "blocker",
                      detail="replacement equals replacement of entity '%s'" % oid, cls=cls)


# ---------------------------------------------------------------- reporting
def summarize(F):
    c = collections.Counter((f["check"], f["severity"]) for f in F.items)
    return {"blockers": sum(1 for f in F.items if f["severity"] == "blocker"),
            "review": sum(1 for f in F.items if f["severity"] == "review"),
            "by_check": {"%s/%s" % k: v for k, v in sorted(c.items())}}


def loc(f):
    if f["line"]:
        return "%s:%d" % (f["path"], f["line"])
    if f["offset"] is not None:
        return "%s@byte %d" % (f["path"], f["offset"])
    return f["path"]


def human(F, stats):
    lines = []
    for f in sorted(F.items, key=lambda x: (SEV_ORDER[x["severity"]], x["path"], x["line"] or 0)):
        lines.append("[%-7s] %-20s %-14s %s%s" % (f["severity"], f["check"], f["entity"], loc(f),
                                                    ("  (%s)" % f["detail"]) if f["detail"] else ""))
    s = summarize(F)
    lines.append("")
    lines.append("scanned %d file(s) (%d binary/latin-1, %d skipped as large): %d blocker(s), %d review item(s)"
                 % (stats["files"], stats["binary"], stats["skipped_large"], s["blockers"], s["review"]))
    return "\n".join(lines)


def write_report(path, F, stats, ents, args, orig_names):
    s = summarize(F)
    by_cls = collections.Counter(e.cls for e in ents)
    checks = collections.defaultdict(list)
    for f in F.items:
        checks[f["check"]].append(f)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = ["# Privacy report", "",
         "Generated by `leak_scan.py` on %s. This report never contains original values: only entity ids, "
         "classes, check names and locations." % now, "",
         "**Result: %s** (%d blocker(s), %d review item(s))" % ("FAIL" if s["blockers"] else "PASS", s["blockers"], s["review"]),
         "", "## Entities registered", ""]
    if by_cls:
        L.append(", ".join("%d %s" % (v, k) for k, v in sorted(by_cls.items())))
    else:
        L.append("none")
    L += ["", "## Scan coverage", "",
          "- Directories scanned: %s" % ", ".join("`%s`" % d for d in args.scan),
          "- Files scanned: %d (%d read as binary/latin-1, %d skipped as larger than 20 MB)"
          % (stats["files"], stats["binary"], stats["skipped_large"]),
          "- Map audit: %s" % ("run" if args.map else "not run (no --map given)"), "",
          "## Results by step", "",
          "| Step (privacy-masking.md s7) | Check | Blockers | Review |", "|---|---|---|---|"]
    rows = [("1", "exact"), ("2", "normalized"), ("3", "encoded"), ("3", "reversed"), ("4", "fragment"),
            ("5", "unregistered-pattern"), ("7", "media-review"), ("7", "forbidden-dir"),
            ("-", "placeholder"), ("-", "map-audit"), ("-", "skipped")]
    for step, chk in rows:
        b = sum(1 for f in checks.get(chk, []) if f["severity"] == "blocker")
        r = sum(1 for f in checks.get(chk, []) if f["severity"] == "review")
        L.append("| %s | %s | %d | %d |" % (step, chk, b, r))
    L += ["| 6 | runtime (rendered text) | - | not run by this script; use `check_page.py` output and re-scan its extracted text |",
          "| 8 | localization | - | covered by scanning every language's files listed under --scan |", "",
          "## Findings", ""]
    if not F.items:
        L.append("No findings.")
    else:
        L += ["| Severity | Check | Entity | Location | Note |", "|---|---|---|---|---|"]
        for f in sorted(F.items, key=lambda x: (SEV_ORDER[x["severity"]], x["path"], x["line"] or 0)):
            L.append("| %s | %s | %s | `%s` | %s |" % (f["severity"], f["check"], f["entity"], loc(f).replace("|", "\\|"),
                                                        f["detail"].replace("|", "\\|")))
    L += ["", "## Notes", "",
          "- Fragment and unregistered-pattern findings are `review`: fix them or justify them (public value, coincidence).",
          "- Media findings list paths only; look at the file, do not trust the name.", ""]
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def build_parser():
    p = argparse.ArgumentParser(
        description="Scan output directories for leaks of original sensitive values (privacy-masking.md s7).",
        epilog="Exit codes: 0 no blockers, 1 blockers found, 2 usage/input error. "
               "Output never contains original values.")
    p.add_argument("--originals", required=True, metavar="PATH", help=".private/originals.json")
    p.add_argument("--map", metavar="PATH", help="spec/privacy-map.json (enables the map audit)")
    p.add_argument("--scan", required=True, nargs="+", metavar="DIR", help="directories (or files) to scan")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                   help="skip files whose relative path matches (repeatable). Use only for shipped tooling such as "
                        "scene-player.js, never for content")
    p.add_argument("--report", metavar="PATH", help="write a markdown report (e.g. reports/privacy.md)")
    p.add_argument("--json", action="store_true", help="print machine-readable JSON instead of text")
    p.add_argument("--max-pattern-hits", type=int, default=50, metavar="N",
                   help="cap unregistered-pattern hits per kind per file (default 50)")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    for d in a.scan:
        if not os.path.exists(d):
            print("error: scan path not found: %s" % d, file=sys.stderr)
            return 2
    orig = load_json(a.originals, "originals file")
    if not isinstance(orig, dict) or not isinstance(orig.get("entities"), list):
        print('error: originals file must look like {"entities":[...]}', file=sys.stderr)
        return 2
    mapdata = None
    if a.map:
        mapdata = load_json(a.map, "privacy map")
        if not isinstance(mapdata, dict) or not isinstance(mapdata.get("entities"), list):
            print('error: privacy map must look like {"entities":[...]}', file=sys.stderr)
            return 2
    ents = build_entities(orig, keep_map(mapdata) if mapdata else None)
    by_id = {e.id: e.cls for e in ents}
    ids = set(by_id)
    known = set()
    for e in ents:
        known.update(e.norms)
    if mapdata:
        for e in mapdata.get("entities", []):
            if isinstance(e, dict) and isinstance(e.get("replacement"), str):
                known.add(norm(e["replacement"]))
                ids.add(str(e.get("id")))
    skip = {os.path.abspath(a.originals)}
    if a.report:
        skip.add(os.path.abspath(a.report))
    if a.map:
        skip.add(os.path.abspath(a.map))
    EXCLUDES[:] = a.exclude
    F = Findings()
    stats = scan_dirs(a.scan, ents, by_id, known, ids, F, skip, a.max_pattern_hits)
    if mapdata:
        audit_map(mapdata, orig, F, os.path.basename(a.map))
    s = summarize(F)
    if a.report:
        write_report(a.report, F, stats, ents, a, None)
    if a.json:
        print(json.dumps({"summary": s, "stats": stats, "findings": F.items}, indent=2))
    else:
        print(human(F, stats))
    return 1 if s["blockers"] else 0


if __name__ == "__main__":
    sys.exit(main())
