#!/usr/bin/env python3
"""
Scans posts/*.md, parses YAML frontmatter and generates posts/index.json.
No external dependencies — runs on the plain GitHub Actions ubuntu runner.

Frontmatter format (at top of each .md file):
---
title: Mein erster Post
date: 2025-04-28
excerpt: Kurze Zusammenfassung die in der Kachel erscheint.
tags: linux, open-source, howto
---
"""

import os
import json
import re

POSTS_DIR = "posts"

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML-like frontmatter and return (meta, body)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}, content

    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()

    body = content[match.end():]
    return meta, body


def auto_excerpt(body: str, length: int = 160) -> str:
    """Generate an excerpt from the first non-empty paragraph."""
    # Strip markdown syntax for a cleaner preview
    text = re.sub(r"#+\s*", "", body)          # headings
    text = re.sub(r"\*\*?|__?", "", text)       # bold/italic
    text = re.sub(r"`[^`]*`", "", text)         # inline code
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # links
    text = " ".join(text.split())
    if len(text) > length:
        return text[:length].rsplit(" ", 1)[0] + " …"
    return text


posts = []

for filename in sorted(os.listdir(POSTS_DIR)):
    if not filename.endswith(".md"):
        continue

    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    meta, body = parse_frontmatter(content)

    # Fallbacks if frontmatter fields are missing
    title   = meta.get("title") or filename.replace(".md", "").replace("-", " ").title()
    date    = meta.get("date", "")
    excerpt = meta.get("excerpt") or auto_excerpt(body)
    tags    = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]

    posts.append({
        "file":    filename,
        "title":   title,
        "date":    date,
        "excerpt": excerpt,
        "tags":    tags,
    })

# Newest first
posts.sort(key=lambda p: p["date"], reverse=True)

out_path = os.path.join(POSTS_DIR, "index.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"✓ Generated {out_path} with {len(posts)} post(s).")
