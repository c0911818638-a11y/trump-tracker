import json
import urllib.request
import sys
import os
import re
from datetime import datetime, timezone, timedelta

ACCOUNT_ID = "107780257626128497"
BASE = "https://truthsocial.com"
BEARER_TOKEN = "SOy4INfwedBfuwjjErgWILeyTm1x9_3DHz91xT_8Q88"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}",
}

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def strip_html(text):
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def utc_to_tw(dt):
    return dt.astimezone(timezone(timedelta(hours=8)))

print("Fetching posts with bearer token...")
url = f"{BASE}/api/v1/accounts/{ACCOUNT_ID}/statuses?limit=20"
data = get(url)
print(f"Fetched {len(data)} posts")

last_seen_id = open("state/last_seen_id.txt").read().strip()
print(f"Last seen ID: {last_seen_id}")

new_posts = []
for p in data:
    if p["id"] <= last_seen_id:
        break
    if p.get("reblog"):
        continue
    dt = datetime.strptime(p["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    new_posts.append({"id": p["id"], "created_at": dt, "content": strip_html(p.get("content", ""))})

new_posts.sort(key=lambda p: p["id"])
print(f"New posts: {len(new_posts)}")

if not new_posts:
    print("No new posts.")
    sys.exit(0)

for p in new_posts:
    post_id = p["id"]
    created_at = p["created_at"]
    tw_time = utc_to_tw(created_at)
    date_str = tw_time.strftime("%Y-%m-%d")
    filename = f"posts/{date_str}_{post_id}.md"

    md = f"""# 川普 Truth Social 新貼文

**發布時間：** {created_at.strftime('%Y-%m-%dT%H:%M:%SZ')}
**貼文 ID：** {post_id}
**連結：** https://truthsocial.com/@realDonaldTrump/{post_id}

---

## 原文
{p['content']}

---

## 中文分析

**主題摘要：** （待 Claude 分析）
**情緒語氣：** （待分析）
**涉及對象：** （待分析）
**政治意涵：** （待分析）
**重要程度：** （待分析）
"""
    os.makedirs("posts", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Created: {filename}")

newest_id = new_posts[-1]["id"]
with open("state/last_seen_id.txt", "w") as f:
    f.write(newest_id)
print(f"Updated last_seen_id: {newest_id}")
