#!/usr/bin/env python3
#
# =========================================================
# wpxml2md.py
# Originally developed through collaboration with ChatGPT.
# Final design, implementation, testing and maintenance by Tougen-roushi.
#
# v1.0 2026-06-29
#
# WordPress XML -> Markdown for Obsidian
# - remove invalid XML chars
# - preprocess hljs-wrap
# - simplify linked images
# - normalize tag names
# - skip existing posts by wordpress_post_id
# - update modified posts by wordpress_post_modified
# =========================================================


import argparse
import html
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


# ===== User Settings =====================================

DEFAULT_OUT_DIR = Path.home() / "Documents" / "Obsidian" / "Obsidian Vault" / "Imports" / "WordPress"
DEFAULT_SKIP_EXISTING = True

# =========================================================


NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def remove_invalid_xml_chars(text: str) -> str:
    # XML 1.0で許されない制御文字を除去。^H 対策。
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)


def safe_filename(s: str) -> str:
    s = html.unescape(s or "untitled")
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:120] or "untitled"


def yaml_escape(s: str) -> str:
    s = "" if s is None else str(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def get_text(elem, path: str, default: str = "") -> str:
    found = elem.find(path, NS)
    return found.text if found is not None and found.text is not None else default


def normalize_tag(s: str) -> str:
    # Markdown で無効になるタグをノーマライズ（正常化）
    s = html.unescape(s or "")
    s = s.strip()
    s = re.sub(r"\s+", "-", s)
    return s


def simplify_linked_images(text: str) -> str:
    # WordPress の Lightbox 用画像リンクなどの同じ画像への自己リンク
    # を除去
    pattern = re.compile(
        r'<a\b[^>]*href="([^"]+)"[^>]*>\s*'
        r'<img\b([^>]*)/?>\s*'
        r'</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )

    def repl(m):
        href = m.group(1).strip()
        img_attrs = m.group(2)

        src_m = re.search(r'\bsrc="([^"]+)"', img_attrs, flags=re.IGNORECASE)
        alt_m = re.search(r'\balt="([^"]*)"', img_attrs, flags=re.IGNORECASE)

        src = src_m.group(1).strip() if src_m else href
        alt = alt_m.group(1).strip() if alt_m else ""
        
        # リンクと画像が同じ時のみ発火
        if href == src:
            return f'<img src="{src}" alt="{alt}" />'
        else:
            return m.group(0)

    return pattern.sub(repl, text)


def preprocess_html(text: str) -> str:
    # 1) リンク付き画像を簡素化
    text = simplify_linked_images(text)
    
    # 2) hljs-wrap の外側だけ剥がす
    # <div class="hljs-wrap">...</div> の外側だけ剥がす
    text = re.sub(
        r'<div\s+class=["\']hljs-wrap["\'][^>]*>\s*(.*?)\s*</div>',
        lambda m: "\n" + m.group(1).strip() + "\n",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return text


def pandoc_html_to_md(text: str) -> str:
    if not text.strip():
        return ""

    try:
        # +raw_html によって pandoc が解釈できない html タグ（<video>など）をそのまま出力
        p = subprocess.run(
            [
                "pandoc",
                "-f", "html+raw_html",
                "-t", "gfm",
                "--wrap=none",
            ],
            input=text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return p.stdout.strip() + "\n"
    except Exception as e:
        print(f"[WARN] pandoc failed: {e}", file=sys.stderr)
        return text.strip() + "\n"


def fix_fence_language_space(md: str) -> str:
    # Pandoc由来で ` ``` bash` のように空白が入るのを補正
    return re.sub(
        r"^([ \t]*```)[ \t]+([A-Za-z0-9_+.-]+)[ \t]*$",
        r"\1\2",
        md,
        flags=re.MULTILINE,
    )


def load_existing_posts(out_dir: Path) -> dict[str, str]:
    # Markdown 化した投稿をスキャンし、id をキーにして、modified
    # を値とする辞書を生成
    posts = {}

    if not out_dir.exists():
        return posts

    for path in out_dir.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        id_match = re.search(
            r'^wordpress_post_id:\s*"([^"]+)"\s*$',
            text,
            flags=re.MULTILINE
        )

        modified_match = re.search(
            r'^wordpress_post_modified:\s*"([^"]+)"\s*$',
            text,
            flags=re.MULTILINE
        )

        if id_match and modified_match:
            posts[id_match.group(1)] = modified_match.group(1)

    return posts


def main():
    parser = argparse.ArgumentParser(
    description="Convert WordPress XML export to Obsidian-friendly Markdown."
    )
    parser.add_argument("xmlfile")
    parser.add_argument("--include-pages", action="store_true", help="Export pages as well")
    parser.add_argument("--all-status", action="store_true", help="Export posts regardless of status")
    parser.add_argument("--debug-title", help="Export only posts whose title contains the specified string")
    parser.add_argument(
    "--force", action="store_true", help="Re-export existing posts")
    parser.add_argument(
    "--out",
    type=Path,
    help="Output directory")
    args = parser.parse_args()

    OUT_DIR = args.out if args.out else DEFAULT_OUT_DIR
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    SKIP_EXISTING = DEFAULT_SKIP_EXISTING and not args.force
    
    existing_posts = load_existing_posts(OUT_DIR) if SKIP_EXISTING else dict()

    raw = Path(args.xmlfile).read_text(encoding="utf-8", errors="replace")
    raw = remove_invalid_xml_chars(raw)
    root = ET.fromstring(raw)

    items = root.findall("./channel/item")
    count = 0

    for item in items:
        post_type = get_text(item, "wp:post_type")
        status = get_text(item, "wp:status")
        title = get_text(item, "title", "untitled")

        if post_type == "page" and not args.include_pages:
            continue
        if post_type not in ("post", "page"):
            continue
        if status != "publish" and not args.all_status:
            continue
        if args.debug_title and args.debug_title not in title:
            continue

        post_date = get_text(item, "wp:post_date")
        post_id = get_text(item, "wp:post_id")
        post_modified = get_text(item, "wp:post_modified")
        link = get_text(item, "link")
        creator = get_text(item, "dc:creator")
        content = get_text(item, "content:encoded")
        
        action = "NEW"
        old_modified = existing_posts.get(post_id)
        
        if SKIP_EXISTING:
            if old_modified == post_modified:
                action = "SKIP"
            elif old_modified:
                action = "UPDATE"

        categories = []
        tags = []

        for cat in item.findall("category"):
            domain = cat.attrib.get("domain", "")
            nicename = cat.attrib.get("nicename", "")
            value = cat.text or nicename
            if domain == "category":
                categories.append(value)
            elif domain == "post_tag":
                tags.append(value)

        content = preprocess_html(content)
        body_md = pandoc_html_to_md(content)
        body_md = fix_fence_language_space(body_md)

        date_part = post_date[:10] if post_date else "no-date"
        filename = f"{date_part} {safe_filename(title)}.md"
        out_path = OUT_DIR / filename

        frontmatter = [
            "---",
            f"title: {yaml_escape(title)}",
            f"date: {yaml_escape(post_date)}",
            f"status: {yaml_escape(status)}",
            f"post_type: {yaml_escape(post_type)}",
            f"wordpress_post_id: {yaml_escape(post_id)}",
            f"wordpress_post_modified: {yaml_escape(post_modified)}",
            f"url: {yaml_escape(link)}",
            f"author: {yaml_escape(creator)}",
            "categories:",
        ]

        for c in categories:
            frontmatter.append(f"  - {yaml_escape(c)}")

        frontmatter.append("tags:")
        for t in tags:
            frontmatter.append(f"  - {yaml_escape(normalize_tag(t))}")

        frontmatter.append("---")
        frontmatter.append("")

        out_path.write_text("\n".join(frontmatter) + body_md, encoding="utf-8")
        
        if action == "SKIP":
            print(f"[{action}] {post_id} {title}")
            continue

        print(f"[{action}] {post_id} {title}")

        count += 1

    print(f"\nDone: {count} files exported to {OUT_DIR}")


if __name__ == "__main__":
    main()
