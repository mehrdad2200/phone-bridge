#!/usr/bin/env python3
"""Check Markdown links: relative files exist AND #anchors match a heading (GitHub-style slugs).

    python scripts/check_links.py          # exit code 1 if something is broken

Slug rule (same as GitHub): lower-case, drop everything except letters/digits/_/-/space
(this also drops zero-width non-joiners and punctuation in Persian headings), spaces -> '-',
duplicates get -1, -2 …
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")


def strip_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def slugs_of(path):
    seen, out = {}, set()
    for line in strip_code(path.read_text(encoding="utf-8")).splitlines():
        m = HEADING.match(line)
        if not m:
            continue
        t = re.sub(r"<[^>]+>", "", m.group(1))
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
        t = t.replace("`", "").replace("*", "")
        slug = re.sub(r"[^\w\- ]", "", t.lower()).replace(" ", "-")
        k = seen.get(slug, 0)
        seen[slug] = k + 1
        out.add(slug if k == 0 else "%s-%d" % (slug, k))
    return out


def main():
    mds = [p for p in sorted(ROOT.rglob("*.md")) if not ({"node_modules", ".git", ".venv"} & set(p.parts))]
    cache, bad, n = {}, [], 0
    for md in mds:
        for target in LINK.findall(strip_code(md.read_text(encoding="utf-8"))):
            if re.match(r"^(https?:|mailto:)", target):
                continue
            n += 1
            file_part, _, anchor = target.partition("#")
            dest = (md.parent / unquote(file_part)).resolve() if file_part else md.resolve()
            if not dest.exists():
                bad.append("%s -> %s (missing file)" % (md.relative_to(ROOT), target))
                continue
            if anchor and dest.suffix == ".md":
                cache.setdefault(dest, slugs_of(dest))
                if unquote(anchor) not in cache[dest]:
                    bad.append("%s -> %s (no such heading)" % (md.relative_to(ROOT), target))
    print("checked %d relative links/anchors in %d Markdown files" % (n, len(mds)))
    for b in bad:
        print("  BROKEN:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
