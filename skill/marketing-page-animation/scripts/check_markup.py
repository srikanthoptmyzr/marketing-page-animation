#!/usr/bin/env python3
"""Tag-balance check for a built page.

Usage:
  check_markup.py PAGE.html [--baseline CHROME.html] [--tags div,section,p]

Why this exists: when a page is assembled by substituting into markup copied from the
live site, an edit that emits one extra closing tag produces no error anywhere. The
browser simply closes an ancestor early, and any absolutely positioned child inside it
re-anchors to a different containing block — an illustration lands in the wrong section,
a sticky element stops sticking. Nothing in the console, nothing in the class checker.

`--baseline` is the chrome the page was built from. The site's own markup is not
perfectly balanced by this crude count (a footer may leave one <div> open), so the test
is "same as the source", not "zero". Script and style bodies are stripped first: a tag
name inside a JS comment is not markup.

Exit codes: 0 balanced, 1 differs from baseline, 2 usage error.
"""
import argparse
import re
import sys

DEFAULT_TAGS = ("div", "section", "p", "figure", "span", "ul", "li", "table")


def strip_code(text):
    out = re.sub(r"<script\b[\s\S]*?</script>", "", text, flags=re.I)
    return re.sub(r"<style\b[\s\S]*?</style>", "", out, flags=re.I)


def balance(text, tag):
    t = strip_code(text)
    opens = len(re.findall(r"<%s[\s>]" % tag, t, flags=re.I))
    closes = len(re.findall(r"</%s>" % tag, t, flags=re.I))
    selfclosed = len(re.findall(r"<%s\b[^>]*/>" % tag, t, flags=re.I))
    return opens - selfclosed - closes


def first_unclosed(text, tag):
    """Offset of an opening tag that never closes, for a useful error message."""
    stack = []
    for m in re.finditer(r"<(/?)%s\b[^>]*?(/?)>" % tag, strip_code(text), flags=re.I):
        if m.group(2) == "/":
            continue
        if m.group(1):
            if stack:
                stack.pop()
        else:
            stack.append(m.start())
    return stack[0] if stack else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--baseline", help="the chrome the page was assembled from")
    ap.add_argument("--tags", default=",".join(DEFAULT_TAGS))
    a = ap.parse_args()

    try:
        page = open(a.page, encoding="utf8").read()
        base = open(a.baseline, encoding="utf8").read() if a.baseline else None
    except OSError as e:
        print("cannot read: %s" % e, file=sys.stderr)
        return 2

    bad = 0
    for tag in [t.strip() for t in a.tags.split(",") if t.strip()]:
        got = balance(page, tag)
        want = balance(base, tag) if base is not None else 0
        if got == want:
            continue
        bad += 1
        print("<%s>: page %+d, expected %+d" % (tag, got, want))
        off = first_unclosed(page, tag)
        if off is not None and got > want:
            line = page[:off].count("\n") + 1
            print("    first unclosed <%s> at line %d: %s"
                  % (tag, line, page[off:off + 90].replace("\n", " ")))
    if bad:
        print("\n%d tag(s) out of balance. An extra close tag re-parents absolutely "
              "positioned children without raising any error." % bad)
        return 1
    print("%s: tag balance matches%s" % (a.page, " the baseline" if base else " zero"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
