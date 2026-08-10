#!/usr/bin/env node
/* 瀏覽器逐項驗收。對每一頁：
 *   - console 必須無錯
 *   - 每個 ▶／→／重置 按鈕各按一次
 *   - 每個 <select> 與 range 滑桿推到兩端
 *   - 每個 quiz 點一個選項，確認有回饋
 *   - 詞彙卡翻面／洗牌／全部翻面
 *   - Chart.js 的 canvas 必須真的畫出東西（.chart-wrap.ready）
 *   - 390×844 手機版：頁面本體不得橫向滾動
 *   - 離線重載：.chart-fallback 要出現，SVG 元件仍在
 *   - 全頁截圖
 *
 * 用法：
 *   node tools/browser_check.js                     # 全部頁面
 *   node tools/browser_check.js resampling_methods
 *   SHOT_DIR=/tmp/shots node tools/browser_check.js
 */
const path = require('path');
const fs = require('fs');

const SCRATCH = process.env.PPT_HOME
  || '/tmp/claude-1000/-home-phonchi-statslearning/a66bde28-081c-4e48-ab81-6c6791815e77/scratchpad';
const puppeteer = require(path.join(SCRATCH, 'node_modules', 'puppeteer-core'));

const ROOT = path.resolve(__dirname, '..');
const SHOT_DIR = process.env.SHOT_DIR || path.join(SCRATCH, 'shots');
const CHROME = process.env.CHROME_PATH
  || `${process.env.HOME}/.cache/puppeteer/chrome/linux-151.0.7922.71/chrome-linux64/chrome`;

const PAGES = process.argv.slice(2).length
  ? process.argv.slice(2).map(s => s.replace(/\.html$/, ''))
  : fs.readdirSync(ROOT).filter(f => f.endsWith('.html') && f !== 'index.html')
      .map(f => f.replace(/\.html$/, ''));

const problems = [];
const note = (page, msg) => problems.push(`[${page}] ${msg}`);

const IGNORE = [
  /favicon/i,
  /net::ERR_FAILED/, /net::ERR_INTERNET_DISCONNECTED/,   // CDN 攔截測試時預期會有
  /Failed to load resource/i,
];

async function checkOne(browser, stem) {
  const url = 'file://' + path.join(ROOT, stem + '.html');
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 1 });
  const errors = [];
  page.on('console', m => {
    if (m.type() === 'error' || m.type() === 'warning') {
      const t = m.text();
      if (!IGNORE.some(re => re.test(t))) errors.push(`console.${m.type()}: ${t}`);
    }
  });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));

  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
  await new Promise(r => setTimeout(r, 1500));

  // Chart.js 是否真的畫了
  const charts = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.chart-wrap').forEach(w => {
      const cv = w.querySelector('canvas');
      out.push({ id: cv ? cv.id : '(no canvas)', ready: w.classList.contains('ready'),
                 w: cv ? cv.width : 0, h: cv ? cv.height : 0 });
    });
    return out;
  });
  charts.forEach(c => {
    if (!c.ready) note(stem, `圖表 #${c.id} 沒有進入 ready（Chart.js 未成功繪製）`);
    if (c.ready && (c.w < 50 || c.h < 50)) note(stem, `圖表 #${c.id} 尺寸異常 ${c.w}×${c.h}`);
  });

  // SVG 元件是否有內容
  const svgs = await page.evaluate(() =>
    [...document.querySelectorAll('svg.viz-svg')].map(s => ({ id: s.id, kids: s.childElementCount })));
  svgs.forEach(s => { if (s.kids === 0) note(stem, `SVG 元件 #${s.id} 是空的`); });

  // 按下每個控制鈕
  const btns = await page.$$('.controls-bar .btn');
  for (const b of btns) {
    try { await b.click(); await new Promise(r => setTimeout(r, 260)); } catch (e) { /* 被覆蓋就跳過 */ }
  }
  // select 推到每個選項
  for (const sel of await page.$$('.controls-bar select')) {
    const vals = await sel.evaluate(el => [...el.options].map(o => o.value));
    for (const v of vals) {
      await sel.select(v); await new Promise(r => setTimeout(r, 220));
    }
  }
  // range 滑桿推到兩端
  for (const r of await page.$$('input[type="range"]')) {
    await r.evaluate(el => {
      el.value = el.min; el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await new Promise(t => setTimeout(t, 200));
    await r.evaluate(el => {
      el.value = el.max; el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await new Promise(t => setTimeout(t, 200));
  }

  // 每個 quiz 點第一個選項，確認回饋出現
  const quizBad = await page.evaluate(() => {
    const bad = [];
    document.querySelectorAll('.quiz-options').forEach(box => {
      const opt = box.querySelector('.quiz-opt');
      if (!opt) { bad.push(box.id + '：沒有選項'); return; }
      opt.click();
      const fb = document.getElementById(box.id.replace(/Options$/, 'Feedback'));
      if (!fb || !fb.classList.contains('show') || !fb.textContent.trim()) {
        bad.push(box.id + '：點了沒有回饋');
      }
    });
    return bad;
  });
  quizBad.forEach(b => note(stem, 'quiz ' + b));

  // 詞彙卡
  const fc = await page.evaluate(() => {
    const grid = document.getElementById('fcGrid');
    if (!grid) return { n: 0 };
    const n = grid.children.length;
    if (n) grid.children[0].click();
    const flipped = grid.querySelectorAll('.fc-card.flipped').length;
    const sh = document.getElementById('fcShuffle'); if (sh) sh.click();
    const fa = document.getElementById('fcFlipAll'); if (fa) fa.click();
    const allFlipped = grid.querySelectorAll('.fc-card.flipped').length;
    return { n, flipped, allFlipped };
  });
  if (fc.n === 0) note(stem, '詞彙卡是空的（尚未注入 FLASHCARDS）');
  else {
    if (fc.flipped !== 1) note(stem, `點第一張卡沒有翻面（flipped=${fc.flipped}）`);
    if (fc.allFlipped !== fc.n) note(stem, `「全部翻面」只翻了 ${fc.allFlipped}/${fc.n}`);
  }

  // 觀念 Q&A：展開後 MathJax 要有排版結果
  const qaBad = await page.evaluate(async () => {
    const items = [...document.querySelectorAll('.qa-item')];
    items.forEach(d => { d.open = true; });
    await new Promise(r => setTimeout(r, 900));
    return items.filter(d => /\$[^$]/.test(d.textContent)).map(d =>
      (d.querySelector('summary') || {}).textContent || '(?)');
  });
  qaBad.forEach(q => note(stem, `Q&A 展開後仍看到未排版的 $：${String(q).slice(0, 40)}`));

  // 全頁截圖
  fs.mkdirSync(SHOT_DIR, { recursive: true });
  await page.screenshot({ path: path.join(SHOT_DIR, stem + '.png'), fullPage: true });

  // 手機版：頁面本體不得橫向滾動
  await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
  await new Promise(r => setTimeout(r, 900));
  const overflow = await page.evaluate(() => {
    const de = document.documentElement;
    const wide = [];
    if (de.scrollWidth > de.clientWidth + 1) {
      document.querySelectorAll('body *').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.right > de.clientWidth + 2 && getComputedStyle(el).overflowX !== 'auto'
            && el.closest('[style*="overflow-x"]') === null && el.offsetParent !== null) {
          wide.push((el.tagName + '.' + (el.className || '')).slice(0, 60) + ' → ' + Math.round(r.right));
        }
      });
      return { over: de.scrollWidth - de.clientWidth, wide: wide.slice(0, 5) };
    }
    return null;
  });
  if (overflow) note(stem, `手機版橫向溢出 ${overflow.over}px：${overflow.wide.join(' | ')}`);
  await page.screenshot({ path: path.join(SHOT_DIR, stem + '_mobile.png'), fullPage: true });

  // CDN 掛掉時：圖表退回 fallback，SVG 元件仍在
  // 用攔截 cdn.jsdelivr.net 而不是 setOfflineMode——後者仍會從磁碟快取供應 Chart.js，
  // 測不到真正的「CDN 失效」情境。
  await page.setViewport({ width: 1280, height: 900 });
  await page.setRequestInterception(true);
  page.on('request', req => {
    if (/cdn\.jsdelivr\.net/.test(req.url())) req.abort().catch(() => {});
    else req.continue().catch(() => {});
  });
  await page.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 1200));
  const off = await page.evaluate(() => {
    const wraps = [...document.querySelectorAll('.chart-wrap')];
    return {
      fallbackVisible: wraps.filter(w => !w.classList.contains('ready')).length,
      total: wraps.length,
      svgAlive: [...document.querySelectorAll('svg.viz-svg')].filter(s => s.childElementCount > 0).length,
      svgTotal: document.querySelectorAll('svg.viz-svg').length,
    };
  });
  if (off.total && off.fallbackVisible !== off.total) {
    note(stem, `離線時有 ${off.total - off.fallbackVisible} 個圖表沒退回 fallback`);
  }
  if (off.svgTotal && off.svgAlive !== off.svgTotal) {
    note(stem, `離線時 SVG 元件掛了 ${off.svgTotal - off.svgAlive}/${off.svgTotal} 個`);
  }
  await page.setRequestInterception(false);

  errors.forEach(e => note(stem, e));
  await page.close();
  return { charts: charts.length, svgs: svgs.length, btns: btns.length, cards: fc.n };
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });
  for (const stem of PAGES) {
    const before = problems.length;
    let s;
    try {
      s = await checkOne(browser, stem);
    } catch (e) {
      note(stem, '檢查中斷：' + e.message);
    }
    const n = problems.length - before;
    const info = s ? `${s.charts} 圖表 · ${s.svgs} SVG · ${s.btns} 按鈕 · ${s.cards} 詞彙卡` : '';
    console.log(`  ${(stem + '.html').padEnd(34)} ${n === 0 ? 'OK  ' : n + ' 問題'} ${info}`);
  }
  await browser.close();
  console.log('');
  problems.forEach(p => console.log('  ✗ ' + p));
  console.log(`\n${problems.length} 個問題（截圖在 ${SHOT_DIR}）`);
  process.exit(problems.length ? 1 : 0);
})();
