import json
import urllib.request
import urllib.error
import sys
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

ACCOUNT_ID = "107780257626128497"
RSS_URL = "https://truthsocial.com/@realDonaldTrump.rss"
API_URL = f"https://truthsocial.com/api/v1/accounts/{ACCOUNT_ID}/statuses?limit=20"

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def strip_html(text):
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def utc_to_tw(dt):
    return dt.astimezone(timezone(timedelta(hours=8)))

def fetch_rss():
    print("Trying RSS feed...")
    headers = {**BROWSER_HEADERS, "Accept": "application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8"}
    req = urllib.request.Request(RSS_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    ns = {'content': 'http://purl.org/rss/1.0/modules/content/'}
    posts = []
    for item in root.findall('.//item'):
        link = item.findtext('link', '')
        post_id = link.rstrip('/').split('/')[-1]
        pub_date = item.findtext('pubDate', '')
        dt = parsedate_to_datetime(pub_date).astimezone(timezone.utc)
        content_encoded = item.find('content:encoded', ns)
        raw = content_encoded.text if content_encoded is not None else item.findtext('description', '')
        text = strip_html(raw or '')
        posts.append({"id": post_id, "created_at": dt, "content": text})
    return posts

def fetch_api():
    print("Trying API...")
    headers = {**BROWSER_HEADERS, "Accept": "application/json"}
    req = urllib.request.Request(API_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    posts = []
    for p in data:
        if p.get('reblog'):
            continue
        dt = datetime.strptime(p['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
        posts.append({"id": p['id'], "created_at": dt, "content": strip_html(p.get('content', ''))})
    return posts

# Try RSS first, then API
posts = None
for method in [fetch_rss, fetch_api]:
    try:
        posts = method()
        print(f"Success: {len(posts)} posts fetched")
        break
    except Exception as e:
        print(f"Failed: {e}")

if not posts:
    print("All fetch methods failed.")
    sys.exit(1)

last_seen_id = open('state/last_seen_id.txt').read().strip()
print(f"Last seen ID: {last_seen_id}")

new_posts = [p for p in posts if p['id'] > last_seen_id]
new_posts.sort(key=lambda p: p['id'])
print(f"New posts: {len(new_posts)}")

if not new_posts:
    print("No new posts.")
    sys.exit(0)

for p in new_posts:
    post_id = p['id']
    created_at = p['created_at']
    content = p['content']
    tw_time = utc_to_tw(created_at)
    date_str = tw_time.strftime('%Y-%m-%d')
    filename = f"posts/{date_str}_{post_id}.md"

    md = f"""# 川普 Truth Social 新貼文

**發布時間：** {created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}
**貼文 ID：** {post_id}
**連結：** https://truthsocial.com/@realDonaldTrump/{post_id}

---

## 原文
{content}

---

## 中文分析

**主題摘要：** （待 Claude 分析）
**情緒語氣：** （待分析）
**涉及對象：** （待分析）
**政治意涵：** （待分析）
**重要程度：** （待分析）
"""
    os.makedirs('posts', exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Created: {filename}")

newest_id = new_posts[-1]['id']
with open('state/last_seen_id.txt', 'w') as f:
    f.write(newest_id)
print(f"Updated last_seen_id: {newest_id}")
