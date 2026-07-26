import json
import urllib.request
import sys
import os
import re
from datetime import datetime, timezone, timedelta

ACCOUNT_ID = "107780257626128497"
BASE = "https://truthsocial.com"
BEARER_TOKEN = "SOy4INfwedBfuwjjErgWILeyTm1x9_3DHz91xT_8Q88"
COOKIE = "__cflb=0H28vTPqhjwKvpvovP7uB2bKEYha7QdonHKrdCTVJjh; osano_consentmanager_uuid=85809a79-9a72-42a0-8323-54b59bc3aa07; osano_consentmanager=6_cF9k8YehXMRs-m8tMcbAWRWVMMuhbvmhZJoki1mJGRIUbFO-woS19yuBoTqR-pReFUN3kuvk4PHL417RHNtifpV5Qdny2aU3xWzio8GxWHnRV5p4B5biRs3ciL7udI9OwETboSxBQc1MfQGeVpwMdSNc62eKpSZD_dDXEpZcWS3-jguFrE1nVzKEqF5QCz-keafXGxRDLH3tgVjFbtzoQqUmms-sSKJs68lSIkFhSRrrUohV_CUG66Lje3HCZb7L2zYmNcDpTkw4Mx6bOApZSq5ZMsC7t_AjvegiEm1dBEa7FYCZz2-by90K5D7FfuZqljVTOHXb8mCNj3k6f6TKXuC4bbwKbO--BqorbJkVaXrZxpmtbRF7eYdCx1JuSmQlKD44U5NWpdoa9SQ0jZUegb6spEH5wl7cfl6hyLeT5u3gvmqJOQGQyzG4F91rzWTBU0WeGPTvf31VAevyePMzRB7ZTxE1Mwkx1nZv4QTijiVSMVWKJ9e5LaZyVS4ETwHWkHDZCwDBXagSTrewCB5ycs4Z0xuiuPx1-nV1prcj6DpbNxIxvNUXsr3-0eo_5Ygz7WGaLhSCvwaWKoVksMPDIaXMpoO3YY_RSf9iJzU_uvRHweuITRR4-n-rKYke0nhbgqpNirEGmYn4FSgTa4QL3RHxEdn8zPiTf1KUyd4m5ianlPz0kirg==; _cfuvid=9eDCgu.dqV5TKpiEnKHUcjuC9LsCkrRCvx5qWeGg_14-1785080629.43982-1.0.1.1-Pw1vpHgdm0KDGunswx_3EQz.Bi9AAD5CJfH4PrcfUl0; mp_15c0cd079bcfa80cd935f3a1b8606b48_mixpanel=%7B%22distinct_id%22%3A%20%22poyi1210%22%2C%22%24device_id%22%3A%20%2219f9f17c8b8846-0655f9cc85d57-26071951-144000-19f9f17c8b918ca%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Ftruthsocial.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22truthsocial.com%22%2C%22%24user_id%22%3A%20%22poyi1210%22%7D; __cf_bm=JLb6ET9ndSSpQkkLVKpyaHAe_okO1sTEooVMgvDFpgk-1785081264.9319522-1.0.1.1-RFLfhEm1hZKJ03X22c6dfJcd8FDBW.ND5F1FtIKFp.3yM07l7_9DBicxDlE16ITm7XsDkKMIMs43jsLP2FGMPUHN3FLr_UiZV7yHud.niKTRAQgmbSRMH2JQhju4ppJT; _mastodon_session=pGlL%2FReS1gRHWOF6fVXiK%2BIJr%2FP8ohyEDqXTLuIcd%2B%2F05Yj8ylOynw2yHY0%2BRCw1neGB3zgWdkSgyrE4%2BN1aXCGdIKnxmkMM7oHo2HYWPShxVCf2qvwrp5s5V6rDLf04DB0fQ9uKMsi5hmOd9k75PonksLUhVt3uhsGeMXSA26uDypOQi4r3RdLQNhifwfSfxSo8UElznck%2BKgaMB6GHcX5%2B9%2BWSpPkN9Y%2Bkrb6ivxnKr7PzJi5eEWDOz1rfO5KhlQ%3D%3D--g%2B9gi72MLFMZBjTr--7gMo5dKjFZd%2BiVZXOcRS7A%3D%3D"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Cookie": COOKIE,
    "Origin": "https://truthsocial.com",
    "Referer": "https://truthsocial.com/",
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
