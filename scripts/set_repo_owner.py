#!/usr/bin/env python3
"""Replace the YOUR_USERNAME placeholder (badges, links, issue-template URLs) with your GitHub name.

    python scripts/set_repo_owner.py octocat                 # -> github.com/octocat/phone-bridge
    python scripts/set_repo_owner.py octocat --repo my-name  # if you named the repository differently
    python scripts/set_repo_owner.py --check                 # list remaining placeholders
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", "__pycache__", ".venv", "images"}
TEXT = {".md", ".toml", ".yml", ".yaml", ".py", ".txt", ".json", ".bat", ".sh", ".svg", ""}


def files():
    for p in ROOT.rglob("*"):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP) and p.suffix.lower() in TEXT and p.name != "set_repo_owner.py":
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("owner", nargs="?")
    ap.add_argument("--repo", default="phone-bridge")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    hits = 0
    for p in files():
        try:
            s = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "YOUR_USERNAME" not in s:
            continue
        hits += s.count("YOUR_USERNAME")
        if a.check or not a.owner:
            print("  %s: %d" % (p.relative_to(ROOT), s.count("YOUR_USERNAME")))
            continue
        s = s.replace("YOUR_USERNAME/phone-bridge", "%s/%s" % (a.owner, a.repo)).replace("YOUR_USERNAME", a.owner)
        p.write_text(s, encoding="utf-8")
    print(("%d placeholder(s) found" if (a.check or not a.owner) else "%d placeholder(s) replaced") % hits)
    return 1 if (a.check and hits) else 0


if __name__ == "__main__":
    sys.exit(main())
