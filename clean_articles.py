#!/usr/bin/env python3
"""Clean Medium UI chrome from article reader.html files."""

import os
import re
from bs4 import BeautifulSoup, NavigableString, Tag


def is_empty(tag):
    """True if a tag has no meaningful content (only whitespace)."""
    if isinstance(tag, NavigableString):
        return tag.strip() == ""
    if isinstance(tag, Tag):
        if tag.name in ("img", "br", "hr", "input", "source"):
            return False
        return all(is_empty(c) for c in tag.children)
    return True


def remove_newsletter_forms(article):
    """Remove Medium newsletter signup forms.
    Must run BEFORE buttons/inputs are removed so we can detect them."""
    for h2 in article.find_all("h2"):
        text = h2.get_text().lower()
        if "inbox" in text or "stories in" in text:
            node = h2
            for _ in range(6):
                node = node.parent
                if node is None or node is article:
                    break
                if node.find("input") or node.find("button"):
                    node.decompose()
                    break


def clean_reader_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    article = soup.find("article")
    if not article:
        return content

    # 1. Remove speechify-ignore elements (author info, "press enter" text)
    for el in article.find_all(class_="speechify-ignore"):
        el.decompose()

    # 2. Remove newsletter signup forms (before removing inputs/buttons)
    remove_newsletter_forms(article)

    # 3. Remove elements with data-testid (all are UI chrome)
    for el in article.find_all(attrs={"data-testid": True}):
        el.decompose()

    # 4. Remove buttons, svgs, inputs
    for el in article.find_all(["button", "svg", "input"]):
        el.decompose()

    # 5. Remove h1 title (already shown in page h1)
    for h1 in article.find_all("h1"):
        h1.decompose()

    # 6. Remove auth/signin/vote/bookmark/repost links
    for a in article.find_all("a", href=True):
        href = a["href"]
        if any(x in href for x in ["signin", "/vote/", "/bookmark/", "/repost/", "/plans"]):
            a.decompose()

    # 7. Simplify picture to just img
    for picture in article.find_all("picture"):
        img = picture.find("img")
        if img:
            picture.replace_with(img)
    for source in article.find_all("source"):
        source.decompose()

    # 8. Unwrap spans inside pre (Medium wraps code text in spans)
    for pre in article.find_all("pre"):
        for span in pre.find_all("span"):
            span.unwrap()

    # 9. Remove "Press enter or click to view image" text
    for text in article.find_all(string=re.compile(r"Press enter or click")):
        text.extract()

    # 10. Iteratively remove empty wrapper divs/spans/sections
    for _ in range(10):
        removed = False
        for el in article.find_all(["div", "span", "section"]):
            if is_empty(el):
                el.decompose()
                removed = True
        if not removed:
            break

    # 11. Flatten figure wrappers: move img directly inside figure
    for fig in article.find_all("figure"):
        img = fig.find("img")
        if img:
            fig.clear()
            fig.append(img)

    # 12. Clean all remaining attributes (keep only essential ones)
    keep_attrs = {"href", "src", "alt", "width", "height", "loading", "target", "rel", "id", "colspan", "rowspan"}
    for tag in article.find_all(True):
        for attr in list(tag.attrs.keys()):
            if attr not in keep_attrs:
                del tag[attr]

    # 13. Improve CSS: add monospace font for pre
    style = soup.find("style")
    if style and style.string:
        css = style.string
        if "article pre{" in css and "monospace" not in css.split("article pre{")[1].split("}")[0]:
            style.string = css.replace(
                "article pre{background:#f6f6f6;padding:14px 16px;border-radius:6px;overflow-x:auto;font-size:.85em;margin:18px 0;border:1px solid #e8e8e8}",
                "article pre{background:#f6f6f6;padding:14px 16px;border-radius:6px;overflow-x:auto;font-size:.85em;margin:18px 0;border:1px solid #e8e8e8;font-family:'SF Mono',Monaco,Consolas,monospace}",
            )

    return str(soup)


def main():
    articles_dir = "articles"
    count = 0
    errors = 0

    for slug in os.listdir(articles_dir):
        reader_path = os.path.join(articles_dir, slug, "reader.html")
        if not os.path.exists(reader_path):
            continue
        try:
            cleaned = clean_reader_html(reader_path)
            with open(reader_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            count += 1
        except Exception as e:
            print(f"Error: {slug}: {e}")
            errors += 1

    print(f"Done. Cleaned {count} articles, {errors} errors.")


if __name__ == "__main__":
    main()
