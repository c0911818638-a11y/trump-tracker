import json
import urllib.request
import urllib.error
import sys
import os
import re
from datetime import datetime, timezone, timedelta

ACCOUNT_ID = "107780257626128497"
API_URL = f"https://truthsocial.com/api/v1/accounts/{ACCOUNT_ID}/statuses?limit=20"

def fetch_posts():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    req = urllib.request.Request(API_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def strip_html(text):
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def utc_to_tw(dt_str):
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone(timedelta(hours=8)))

last_seen_id = open('state/last_seen_id.txt').read().strip()
print(f"Last seen ID: {last_seen_id}")

posts = fetch_posts()
new_posts = []
for p in posts:
    if p['id'] <= last_seen_id:
        break
    if p.get('reblog'):
        continue
    new_posts.append(p)

new_posts.reverse()
print(f"New posts: {len(new_posts)}")

if not new_posts:
    print("No new posts.")
    sys.exit(0)

for p in new_posts:
    post_id = p['id']
    created_at = p['created_at']
    content = strip_html(p.get('content', ''))
    tw_time = utc_to_tw(created_at)

    date_str = tw_time.strftime('%Y-%m-%d')
    filename = f"posts/{date_str}_{post_id}.md"

    md = f"""# 川普 Truth Social 新貼文

**發布時間：** {created_at.replace('.000Z','Z')}
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

# Update last_seen_id
newest_id = new_posts[-1]['id']
with open('state/last_seen_id.txt', 'w') as f:
    f.write(newest_id)
print(f"Updated last_seen_id: {newest_id}")
