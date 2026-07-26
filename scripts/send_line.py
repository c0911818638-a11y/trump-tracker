import sys
import re
import json
import urllib.request
from datetime import datetime, timezone, timedelta

def extract(text, key):
    m = re.search(rf'\*\*{key}[：:]\*\*\s*(.+)', text)
    return m.group(1).strip() if m else ''

def utc_to_tw(t):
    try:
        dt = datetime.strptime(t.strip(), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    except:
        return t

file_path  = sys.argv[1]
line_token = sys.argv[2]
line_uid   = sys.argv[3]

content = open(file_path, encoding='utf-8').read()

publish_time = extract(content, '發布時間')
post_id      = extract(content, '貼文 ID')
summary      = extract(content, '主題摘要')
tone         = extract(content, '情緒語氣')
target       = extract(content, '涉及對象')
impact       = extract(content, '政治意涵')
importance   = extract(content, '重要程度')
tw_time      = utc_to_tw(publish_time)

msg = f"""🇺🇸 川普新發文

⏰ {tw_time} (台灣時間)
📝 摘要：{summary}
😠 語氣：{tone}
🎯 對象：{target}
🌏 影響：{impact}
⭐ 重要程度：{importance}

🔗 https://truthsocial.com/@realDonaldTrump/{post_id}"""

payload = json.dumps({
    "to": line_uid,
    "messages": [{"type": "text", "text": msg}]
}).encode('utf-8')

req = urllib.request.Request(
    'https://api.line.me/v2/bot/message/push',
    data=payload,
    headers={
        'Authorization': f'Bearer {line_token}',
        'Content-Type': 'application/json'
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"OK: {resp.status}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"FAIL: {e.code} {body}")
    sys.exit(1)
