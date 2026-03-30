#!/usr/bin/env python3
"""Migrate WordPress posts to Quarto .qmd files.

Reads posts-index.json, fetches content from WP.com REST API,
converts WP block HTML to markdown, writes .qmd files.

Usage: python3 migrate.py [--token TOKEN] [--dry-run]
"""
import html as htmlmod
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

SITE_ID = "173374270"
API_BASE = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE_ID}/posts"
BASE_DIR = Path(__file__).parent.parent  # project root


def fetch_post_content(post_id, token=None):
    """Fetch post content. Checks local cache first, then WP.com REST API."""
    # Check local cache (JSON or plain text)
    cache_file = Path(__file__).parent / "posts-content" / f"{post_id}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f).get("content", "")
    txt_file = Path(__file__).parent / "posts-content" / f"{post_id}.txt"
    if txt_file.exists():
        return txt_file.read_text()

    url = f"{API_BASE}/{post_id}"
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("content", "")
    except urllib.error.HTTPError as e:
        return None


def wp_html_to_markdown(html_content):
    """Convert WordPress block HTML to clean markdown."""
    text = html_content

    # Strip WP block comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Images in figures
    text = re.sub(
        r"<figure[^>]*>\s*<img[^>]*?src=[\"']([^\"']*)[\"'][^>]*?(?:alt=[\"']([^\"']*)[\"'])?[^>]*/?\s*>\s*(?:<figcaption[^>]*>(.*?)</figcaption>)?\s*</figure>",
        lambda m: f"![{m.group(2) or m.group(3) or ''}]({m.group(1)})",
        text,
        flags=re.DOTALL,
    )

    # Standalone images
    text = re.sub(
        r"<img[^>]*?src=[\"']([^\"']*)[\"'][^>]*?(?:alt=[\"']([^\"']*)[\"'])?[^>]*/?\s*>",
        lambda m: f"![{m.group(2) or ''}]({m.group(1)})",
        text,
    )

    # Links
    text = re.sub(
        r"<a[^>]*?href=[\"']([^\"']*)[\"'][^>]*>(.*?)</a>",
        r"[\2](\1)",
        text,
        flags=re.DOTALL,
    )

    # Bold
    text = re.sub(
        r"<(?:strong|b)>(.*?)</(?:strong|b)>", r"**\1**", text, flags=re.DOTALL
    )

    # Italic
    text = re.sub(r"<(?:em|i)>(.*?)</(?:em|i)>", r"*\1*", text, flags=re.DOTALL)

    # Headings
    for i in range(6, 0, -1):
        text = re.sub(
            rf"<h{i}[^>]*>(.*?)</h{i}>",
            rf'{"#" * i} \1',
            text,
            flags=re.DOTALL,
        )

    # Blockquotes
    def convert_blockquote(m):
        inner = m.group(1).strip()
        inner = re.sub(r"<[^>]+>", "", inner)  # strip inner HTML
        lines = [l.strip() for l in inner.split("\n") if l.strip()]
        return "\n".join("> " + l for l in lines)

    text = re.sub(
        r"<blockquote[^>]*>(.*?)</blockquote>",
        convert_blockquote,
        text,
        flags=re.DOTALL,
    )

    # Ordered list items (number them)
    def convert_ol(m):
        items = re.findall(r"<li[^>]*>(.*?)</li>", m.group(1), flags=re.DOTALL)
        return "\n".join(
            f"{i+1}. {re.sub(r'<[^>]+>', '', item).strip()}"
            for i, item in enumerate(items)
        )

    text = re.sub(r"<ol[^>]*>(.*?)</ol>", convert_ol, text, flags=re.DOTALL)

    # Unordered list items
    def convert_ul(m):
        items = re.findall(r"<li[^>]*>(.*?)</li>", m.group(1), flags=re.DOTALL)
        return "\n".join(
            f"- {re.sub(r'<[^>]+>', '', item).strip()}" for item in items
        )

    text = re.sub(r"<ul[^>]*>(.*?)</ul>", convert_ul, text, flags=re.DOTALL)

    # Horizontal rule
    text = re.sub(r"<hr[^>]*/?>", "\n---\n", text)

    # Line breaks
    text = re.sub(r"<br\s*/?>", "\n", text)

    # Strip remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities
    text = htmlmod.unescape(text)

    # Clean up whitespace
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def categorize_post(post):
    """Determine subfolder: book-reviews or posts."""
    cats = [c.lower() for c in post.get("categories", [])]
    if "book review" in cats:
        return "book-reviews"
    return "posts"


def build_qmd(post, content_md):
    """Build .qmd file content with YAML frontmatter."""
    title = post["title"].replace('"', '\\"')
    date = post["date"]
    categories = post.get("categories", [])
    tags = post.get("tags", [])
    status = post["status"]
    lang = post.get("language", "EN")

    lines = ["---"]
    lines.append(f'title: "{title}"')
    lines.append(f"date: {date}")
    if categories:
        lines.append(f"categories: {json.dumps(categories, ensure_ascii=False)}")
    if tags:
        lines.append(f"tags: {json.dumps(tags, ensure_ascii=False)}")
    if lang:
        lines.append(f"lang-post: {lang}")
    if status in ("draft", "private"):
        lines.append("draft: true")
    lines.append("---")
    lines.append("")
    lines.append(content_md)
    lines.append("")

    return "\n".join(lines)


def main():
    token = None
    dry_run = False
    for arg in sys.argv[1:]:
        if arg.startswith("--token="):
            token = arg.split("=", 1)[1]
        elif arg == "--token":
            idx = sys.argv.index("--token")
            token = sys.argv[idx + 1]
        elif arg == "--dry-run":
            dry_run = True

    index_path = Path(__file__).parent / "posts" / "posts-index.json"
    with open(index_path) as f:
        posts = json.load(f)

    # Track results
    ok, skipped, failed = [], [], []

    for post in posts:
        pid = post["id"]
        slug = post["slug"]
        date = post["date"]
        subfolder = categorize_post(post)
        filename = f"{date}-{slug}.qmd"
        out_dir = BASE_DIR / "mind-wandering" / subfolder
        out_path = out_dir / filename

        if out_path.exists():
            skipped.append(pid)
            continue

        # Fetch content
        content_html = fetch_post_content(pid, token=token)
        if content_html is None:
            failed.append((pid, post["title"], post["status"]))
            continue

        content_md = wp_html_to_markdown(content_html)
        qmd = build_qmd(post, content_md)

        if dry_run:
            print(f"  [dry-run] {subfolder}/{filename}")
            ok.append(pid)
            continue

        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(qmd)
        print(f"  ✓ {subfolder}/{filename}")
        ok.append(pid)

    print(f"\n✓ Migrated: {len(ok)} | Skipped: {len(skipped)} | Failed: {len(failed)}")
    if failed:
        print("\nFailed (need auth token for private/draft posts):")
        for pid, title, status in failed:
            print(f"  [{status}] {pid}: {title}")


if __name__ == "__main__":
    main()
