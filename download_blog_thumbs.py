#!/usr/bin/env python3
"""Download all blog article thumbnails from Medium to local storage."""

import json, re, os, hashlib, urllib.request, time

ROOT = os.path.dirname(os.path.abspath(__file__))
BLOG_PATH = os.path.join(ROOT, "data", "sources", "blog.json")
IMG_DIR = os.path.join(ROOT, "articles", "images")

def download_image(url):
    try:
        os.makedirs(IMG_DIR, exist_ok=True)
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        ext = '.jpg'
        m = re.search(r'\.(jpg|jpeg|png|gif|webp)', url, re.IGNORECASE)
        if m:
            ext = '.' + m.group(1).lower()
            if ext == '.jpeg':
                ext = '.jpg'
        filename = url_hash + ext
        filepath = os.path.join(IMG_DIR, filename)
        if os.path.exists(filepath):
            return f'articles/images/{filename}'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://blog.palantir.com/'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 100:
            return None
        with open(filepath, 'wb') as f:
            f.write(data)
        return f'articles/images/{filename}'
    except Exception as e:
        return None

def main():
    with open(BLOG_PATH, 'r', encoding='utf-8') as f:
        blog = json.load(f)

    articles = blog['articles']
    remote = [a for a in articles if a.get('th', '').startswith('http')]
    print(f'Total blog articles: {len(articles)}')
    print(f'Remote thumbnails to download: {len(remote)}')

    downloaded = 0
    failed = 0
    for i, a in enumerate(remote):
        url = a['th']
        local = download_image(url)
        if local:
            a['th'] = local
            downloaded += 1
        else:
            failed += 1
        if (i + 1) % 50 == 0:
            print(f'  Progress: {i+1}/{len(remote)} (downloaded={downloaded}, failed={failed})')
            with open(BLOG_PATH, 'w', encoding='utf-8') as f:
                json.dump(blog, f, ensure_ascii=False, indent=2)
        time.sleep(0.1)

    with open(BLOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(blog, f, ensure_ascii=False, indent=2)

    print(f'\nDone: downloaded={downloaded}, failed={failed}')
    remaining = sum(1 for a in blog['articles'] if a.get('th', '').startswith('http'))
    print(f'Remaining remote: {remaining}')

if __name__ == '__main__':
    main()
