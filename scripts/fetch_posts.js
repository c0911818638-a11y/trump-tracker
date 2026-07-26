const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const ACCOUNT_URL = 'https://truthsocial.com/@realDonaldTrump';
const BEARER_TOKEN = 'SOy4INfwedBfuwjjErgWILeyTm1x9_3DHz91xT_8Q88';
const COOKIE_STR = '__cflb=0H28vTPqhjwKvpvovP7uB2bKEYha7QdonHKrdCTVJjh; osano_consentmanager_uuid=85809a79-9a72-42a0-8323-54b59bc3aa07; osano_consentmanager=6_cF9k8YehXMRs-m8tMcbAWRWVMMuhbvmhZJoki1mJGRIUbFO-woS19yuBoTqR-pReFUN3kuvk4PHL417RHNtifpV5Qdny2aU3xWzio8GxWHnRV5p4B5biRs3ciL7udI9OwETboSxBQc1MfQGeVpwMdSNc62eKpSZD_dDXEpZcWS3-jguFrE1nVzKEqF5QCz-keafXGxRDLH3tgVjFbtzoQqUmms-sSKJs68lSIkFhSRrrUohV_CUG66Lje3HCZb7L2zYmNcDpTkw4Mx6bOApZSq5ZMsC7t_AjvegiEm1dBEa7FYCZz2-by90K5D7FfuZqljVTOHXb8mCNj3k6f6TKXuC4bbwKbO--BqorbJkVaXrZxpmtbRF7eYdCx1JuSmQlKD44U5NWpdoa9SQ0jZUegb6spEH5wl7cfl6hyLeT5u3gvmqJOQGQyzG4F91rzWTBU0WeGPTvf31VAevyePMzRB7ZTxE1Mwkx1nZv4QTijiVSMVWKJ9e5LaZyVS4ETwHWkHDZCwDBXagSTrewCB5ycs4Z0xuiuPx1-nV1prcj6DpbNxIxvNUXsr3-0eo_5Ygz7WGaLhSCvwaWKoVksMPDIaXMpoO3YY_RSf9iJzU_uvRHweuITRR4-n-rKYke0nhbgqpNirEGmYn4FSgTa4QL3RHxEdn8zPiTf1KUyd4m5ianlPz0kirg==; _cfuvid=9eDCgu.dqV5TKpiEnKHUcjuC9LsCkrRCvx5qWeGg_14-1785080629.43982-1.0.1.1-Pw1vpHgdm0KDGunswx_3EQz.Bi9AAD5CJfH4PrcfUl0; mp_15c0cd079bcfa80cd935f3a1b8606b48_mixpanel=%7B%22distinct_id%22%3A%20%22poyi1210%22%2C%22%24device_id%22%3A%20%2219f9f17c8b8846-0655f9cc85d57-26071951-144000-19f9f17c8b918ca%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Ftruthsocial.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22truthsocial.com%22%2C%22%24user_id%22%3A%20%22poyi1210%22%7D; __cf_bm=JLb6ET9ndSSpQkkLVKpyaHAe_okO1sTEooVMgvDFpgk-1785081264.9319522-1.0.1.1-RFLfhEm1hZKJ03X22c6dfJcd8FDBW.ND5F1FtIKFp.3yM07l7_9DBicxDlE16ITm7XsDkKMIMs43jsLP2FGMPUHN3FLr_UiZV7yHud.niKTRAQgmbSRMH2JQhju4ppJT; _mastodon_session=pGlL%2FReS1gRHWOF6fVXiK%2BIJr%2FP8ohyEDqXTLuIcd%2B%2F05Yj8ylOynw2yHY0%2BRCw1neGB3zgWdkSgyrE4%2BN1aXCGdIKnxmkMM7oHo2HYWPShxVCf2qvwrp5s5V6rDLf04DB0fQ9uKMsi5hmOd9k75PonksLUhVt3uhsGeMXSA26uDypOQi4r3RdLQNhifwfSfxSo8UElznck%2BKgaMB6GHcX5%2B9%2BWSpPkN9Y%2Bkrb6ivxnKr7PzJi5eEWDOz1rfO5KhlQ%3D%3D--g%2B9gi72MLFMZBjTr--7gMo5dKjFZd%2BiVZXOcRS7A%3D%3D';

function parseCookies(str) {
  return str.split(';').map(c => {
    const [name, ...rest] = c.trim().split('=');
    return { name: name.trim(), value: rest.join('='), domain: 'truthsocial.com', path: '/' };
  });
}

function stripHtml(html) {
  return html.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '').trim();
}

(async () => {
  const lastSeenId = fs.readFileSync('state/last_seen_id.txt', 'utf8').trim();
  console.log('Last seen ID:', lastSeenId);

  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  });
  await context.addCookies(parseCookies(COOKIE_STR));

  const posts = [];
  context.on('response', async (response) => {
    const url = response.url();
    if (url.includes('/api/v1/accounts/') && url.includes('/statuses')) {
      try {
        const data = await response.json();
        if (Array.isArray(data)) {
          console.log(`API response: ${data.length} posts`);
          posts.push(...data);
        }
      } catch {}
    }
  });

  const page = await context.newPage();
  console.log('Navigating...');
  await page.goto(ACCOUNT_URL, { waitUntil: 'domcontentloaded', timeout: 90000 });
  console.log('Page loaded, waiting for API...');
  await page.waitForTimeout(8000);
  await browser.close();

  console.log(`Total captured: ${posts.length} posts`);

  const newPosts = posts
    .filter(p => !p.reblog && p.id > lastSeenId)
    .sort((a, b) => a.id.localeCompare(b.id));

  console.log(`New posts: ${newPosts.length}`);
  if (!newPosts.length) { console.log('No new posts.'); process.exit(0); }

  fs.mkdirSync('posts', { recursive: true });
  for (const p of newPosts) {
    const dt = new Date(p.created_at);
    const twDt = new Date(dt.getTime() + 8 * 3600 * 1000);
    const dateStr = twDt.toISOString().slice(0, 10);
    const filename = `posts/${dateStr}_${p.id}.md`;
    const content = stripHtml(p.content || '');

    fs.writeFileSync(filename, `# 川普 Truth Social 新貼文

**發布時間：** ${dt.toISOString().replace('.000Z', 'Z')}
**貼文 ID：** ${p.id}
**連結：** https://truthsocial.com/@realDonaldTrump/${p.id}

---

## 原文
${content}

---

## 中文分析

**主題摘要：** （待 Claude 分析）
**情緒語氣：** （待分析）
**涉及對象：** （待分析）
**政治意涵：** （待分析）
**重要程度：** （待分析）
`, 'utf8');
    console.log(`Created: ${filename}`);
  }

  const newestId = newPosts[newPosts.length - 1].id;
  fs.writeFileSync('state/last_seen_id.txt', newestId, 'utf8');
  console.log(`Updated last_seen_id: ${newestId}`);
})();
