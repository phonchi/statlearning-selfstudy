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
 * island/index.html（3D 群島）另走 checkIsland()：WebGL 正常／CDN 被攔／getContext 回傳 null
 * 三種狀態 × 桌面與 390×844，確認 3D 畫得出來、點島／標籤開面板、入夜切換、維導導覽與代表圖、2D 備援、26 個入口都可達。
 *
 * 用法：
 *   node tools/browser_check.js                     # 全部頁面
 *   node tools/browser_check.js resampling_methods
 *   SHOT_DIR=/tmp/shots node tools/browser_check.js
 */
const path = require('path');
const fs = require('fs');

// puppeteer-core 裝在 repo 外面（repo 不放 node_modules）：
//   mkdir -p ~/.cache/selfstudy-node && cd ~/.cache/selfstudy-node
//   npm init -y && npm i puppeteer-core && npx puppeteer browsers install chrome
const PPT_HOME = process.env.PPT_HOME || path.join(process.env.HOME, '.cache/selfstudy-node');
const puppeteer = require(path.join(PPT_HOME, 'node_modules', 'puppeteer-core'));

const ROOT = path.resolve(__dirname, '..');
const SHOT_DIR = process.env.SHOT_DIR || path.join(PPT_HOME, 'shots');
const CHROME = process.env.CHROME_PATH || (() => {
  const base = path.join(process.env.HOME, '.cache/puppeteer/chrome');
  const dirs = fs.existsSync(base) ? fs.readdirSync(base).sort() : [];
  if (!dirs.length) {
    console.error('找不到 Chrome。先跑：npx puppeteer browsers install chrome');
    process.exit(2);
  }
  return path.join(base, dirs[dirs.length - 1], 'chrome-linux64', 'chrome');
})();

const ARGS = process.argv.slice(2).map(s => s.replace(/\.html$/, '').replace(/\/index$/, ''));
const WITH_ISLAND = !ARGS.length || ARGS.includes('island');
const PAGES = ARGS.length
  ? ARGS.filter(s => s !== 'island')
  : fs.readdirSync(ROOT).filter(f => f.endsWith('.html') && f !== 'index.html')
      .map(f => f.replace(/\.html$/, ''));

const problems = [];
const note = (page, msg) => problems.push(`[${page}] ${msg}`);

const IGNORE = [
  /favicon/i,
  /net::ERR_FAILED/, /net::ERR_INTERNET_DISCONNECTED/,   // CDN 攔截測試時預期會有
  /Failed to load resource/i,
];

/* 全頁截圖：頁面高度超過 Chrome 上限（Page is too large）時，改截最上方 16000px，其餘檢查照常 */
async function shot(page, file) {
  try {
    await page.screenshot({ path: file, fullPage: true });
  } catch (e) {
    if (!/too large/i.test(String(e))) throw e;
    const vp = page.viewport();
    await page.screenshot({ path: file, clip: { x: 0, y: 0, width: vp.width, height: 16000 } });
  }
}

const DRAG_CHECKS = {
  beyond_linearity: [['#w08stepSvg rect.drag', 1, 'w08stepCuts[1]', 6, 0], ['#w08knotSvg .drag', 0, 'w08knotXi', 6, 0]],
  deep_learning: [['#w11fwdSvg .w11node', 0, 'w11fwdX[0]', 0, -12]],
  unsupervised_learning: [['#w07spinSvg .drag', 0, 'w07spinAngle', 0, 16]],
};

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
  await page.evaluate(async () => {
    if (window.MathJax?.startup?.promise) await MathJax.startup.promise;
  });
  const mathErrors = await page.$$eval('mjx-merror', els => els.map(el => el.textContent));
  mathErrors.forEach(msg => note(stem, '數學排版錯誤：' + msg));

  // First validate the uninterrupted default reading view.
  const disclosureState = await page.$$eval('details.proof, details.reading-detail', ds => ds.map(d => ({
    id: d.id, open: d.open, summary: d.querySelector('summary')?.textContent.trim()
  })));
  disclosureState.forEach(d => {
    if (d.open) note(stem, `細節預設展開：${d.id}`);
    if (!d.id || !d.summary) note(stem, '收合區缺少錨點或摘要');
  });
  fs.mkdirSync(SHOT_DIR, { recursive: true });
  await shot(page, path.join(SHOT_DIR, stem + '_reading.png'));
  const readingSummary = await page.$('details.reading-detail > summary');
  if (readingSummary) {
    await readingSummary.focus(); await page.keyboard.press('Enter');
    if (!await readingSummary.evaluate(el => el.parentElement.open)) note(stem, 'Enter 無法展開閱讀細節');
    await page.keyboard.press('Space');
    if (await readingSummary.evaluate(el => el.parentElement.open)) note(stem, 'Space 無法收合閱讀細節');
  }
  // Every hidden teaching unit must be opened before testing its real controls.
  await page.evaluate(async () => {
    document.querySelectorAll('details.reading-detail').forEach(d => { d.open = true; });
    await new Promise(r => setTimeout(r, 200));
    if (window.MathJax?.startup?.promise) await MathJax.startup.promise;
    if (typeof HC !== 'undefined') await HC._mathQueue;
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  });
  // 可拖把手要能連續拖：曾經因為重畫換掉把手，拖一下就斷（第 7、10 章與 PCA 旋轉）
  for (const [sel, idx, read, dx, dy] of DRAG_CHECKS[stem] || []) {
    const pos = await page.evaluate(async (sel, idx) => {
      const y = document.querySelectorAll(sel)[idx].getBoundingClientRect().top + scrollY - 300;
      window.scrollTo({ top: y, behavior: 'instant' });
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
      const b = document.querySelectorAll(sel)[idx].getBoundingClientRect();
      return [b.x + b.width / 2, b.y + b.height / 2];
    }, sel, idx);
    const seen = new Set();
    await page.mouse.move(pos[0], pos[1]); await page.mouse.down();
    for (let i = 1; i <= 6; i++) {
      await page.mouse.move(pos[0] + i * dx, pos[1] + i * dy);
      await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
      seen.add(await page.evaluate(read));
    }
    await page.mouse.up();
    if (seen.size < 4) note(stem, `拖曳 ${sel} 無法連續移動：6 次移動只看到 ${seen.size} 個值`);
  }

  const firstProof = await page.$('details.proof > summary');
  if (firstProof) {
    await firstProof.focus(); await page.keyboard.press('Enter');
    if (!await firstProof.evaluate(el => el.parentElement.open)) note(stem, 'Enter 無法展開證明');
    await page.keyboard.press('Space');
    if (await firstProof.evaluate(el => el.parentElement.open)) note(stem, 'Space 無法收合證明');
  }

  // Card JSON and its reader-visible text must agree (including <, > and &).
  const cardTextProblems = await page.evaluate(() => {
    if (typeof FLASHCARDS === 'undefined') return [];
    return [...document.querySelectorAll('.fc-card')].flatMap((el, i) => {
      const front = el.querySelector('.fc-front > div');
      const back = el.querySelector('.fc-back');
      return front?.textContent === FLASHCARDS[i]?.front
        && back?.textContent === FLASHCARDS[i]?.back && back.childElementCount === 0
        ? [] : ['詞彙卡 ' + (i + 1) + ' 文字與母檔不符'];
    });
  });
  cardTextProblems.forEach(msg => note(stem, msg));

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
    if (await b.evaluate(el => el.disabled)) continue;
    try { await b.click(); await new Promise(r => setTimeout(r, 260)); }
    catch (e) { note(stem, '控制鈕無法操作：' + await b.evaluate(el => el.textContent.trim())); }
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
    const expected = typeof FLASHCARDS === 'undefined' ? null : FLASHCARDS.length;
    if (!grid) return { n: 0, expected, hasGrid: false };
    const n = grid.children.length;
    if (n) grid.children[0].click();
    const flipped = grid.querySelectorAll('.fc-card.flipped').length;
    const sh = document.getElementById('fcShuffle'); if (sh) sh.click();
    const fa = document.getElementById('fcFlipAll'); if (fa) fa.click();
    const allFlipped = grid.querySelectorAll('.fc-card.flipped').length;
    return { n, flipped, allFlipped, expected, hasGrid: true };
  });
  if (fc.expected === 0) {
    if (fc.hasGrid) note(stem, '沒有合適術語時不應顯示空詞彙卡區塊');
  } else if (fc.n !== fc.expected || fc.n === 0) note(stem, '詞彙卡與資料筆數不符');
  else {
    if (fc.flipped !== 1) note(stem, `點第一張卡沒有翻面（flipped=${fc.flipped}）`);
    if (fc.allFlipped !== fc.n) note(stem, `「全部翻面」只翻了 ${fc.allFlipped}/${fc.n}`);
  }

  // 觀念 Q&A：展開後 MathJax 要有排版結果
  const qaBad = await page.evaluate(async () => {
    const items = [...document.querySelectorAll('.qa-item')];
    items.forEach(d => { d.open = true; });
    await new Promise(r => setTimeout(r, 200));
    if (typeof HC !== 'undefined') await HC._mathQueue;
    return items.filter(d => /\$[^$]/.test(d.textContent)).map(d =>
      (d.querySelector('summary') || {}).textContent || '(?)');
  });
  qaBad.forEach(q => note(stem, `Q&A 展開後仍看到未排版的 $：${String(q).slice(0, 40)}`));
  const expandedErrors = await page.$$eval('details mjx-merror', es => es.map(e => e.textContent));
  expandedErrors.forEach(msg => note(stem, '收合內容展開後公式錯誤：' + msg));

  // 全頁截圖
  fs.mkdirSync(SHOT_DIR, { recursive: true });
  await shot(page, path.join(SHOT_DIR, stem + '.png'));

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
  await shot(page, path.join(SHOT_DIR, stem + '_mobile.png'));

  const reflowBad = await page.evaluate(async () => {
    document.querySelectorAll('details.reading-detail').forEach(d => { d.open = false; });
    await new Promise(r => setTimeout(r, 120));
    document.querySelectorAll('details.reading-detail').forEach(d => { d.open = true; });
    await new Promise(r => setTimeout(r, 250));
    if (typeof HC !== 'undefined') await HC._mathQueue;
    return [...document.querySelectorAll('.chart-wrap.ready canvas')].filter(c => c.width < 50 || c.height < 50).map(c => c.id);
  });
  reflowBad.forEach(id => note(stem, `重新展開後圖表尺寸異常：${id}`));

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
    document.querySelectorAll('details.reading-detail').forEach(d => { d.open = true; });
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

const ISLAND_IGNORE = [/software WebGL/i, /GL Driver Message/i, /GPU stall/i];

/* 3D 群島：三種狀態 × 桌面／手機。回傳摘要字串。 */
async function checkIsland(browser) {
  const stem = 'island';
  const url = 'file://' + path.join(ROOT, 'island', 'index.html');
  const html = fs.readFileSync(path.join(ROOT, 'island', 'index.html'), 'utf8');
  const total = (html.match(/class="isl-link"/g) || []).length;
  fs.mkdirSync(SHOT_DIR, { recursive: true });
  const summary = [];

  async function open(mode) {
    const page = await browser.newPage();
    const errors = [];
    page.on('console', m => {
      if (m.type() === 'error' || m.type() === 'warning') {
        const t = m.text();
        if (!IGNORE.some(re => re.test(t)) && !ISLAND_IGNORE.some(re => re.test(t))) errors.push(`console.${m.type()}: ${t}`);
      }
    });
    page.on('pageerror', e => errors.push('pageerror: ' + e.message));
    if (mode === 'cdn') {
      await page.setRequestInterception(true);
      page.on('request', req => {
        if (/cdn\.jsdelivr\.net/.test(req.url())) req.abort().catch(() => {});
        else req.continue().catch(() => {});
      });
    }
    if (mode === 'nogl') {
      await page.evaluateOnNewDocument(() => {
        const orig = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function (type, ...rest) {
          return /webgl/i.test(type) ? null : orig.call(this, type, ...rest);
        };
      });
    }
    return { page, errors };
  }

  // 頁面本體不得橫向捲動；26 個入口都要可見（可 Tab 到達）
  async function layout(page, label) {
    const r = await page.evaluate(() => {
      const de = document.documentElement;
      const links = [...document.querySelectorAll('.isl-link')];
      return {
        over: de.scrollWidth - de.clientWidth,
        visible: links.filter(a => a.offsetParent !== null && a.tabIndex >= 0).length,
        webgl: document.body.classList.contains('webgl-ready'),
      };
    });
    if (r.over > 1) note(stem, `${label}：橫向溢出 ${r.over}px`);
    if (r.visible !== total) note(stem, `${label}：只有 ${r.visible}/${total} 個入口可見`);
    return r;
  }

  // 畫布是否真的畫出東西：截圖後在頁面裡解碼，數不同顏色
  async function canvasColors(page) {
    const el = await page.$('#islCanvas');
    const b64 = await el.screenshot({ encoding: 'base64' });
    return page.evaluate(async src => {
      const img = new Image(); img.src = 'data:image/png;base64,' + src; await img.decode();
      const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
      const g = c.getContext('2d'); g.drawImage(img, 0, 0);
      const d = g.getImageData(0, 0, c.width, c.height).data, seen = new Set();
      for (let i = 0; i < d.length; i += 4 * 97) seen.add((d[i] >> 3) << 10 | (d[i + 1] >> 3) << 5 | d[i + 2] >> 3);
      return seen.size;
    }, b64);
  }

  // (a) WebGL 正常
  {
    const { page, errors } = await open('gl');
    await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 1 });
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });  // 3D 動畫持續繪製，不等 networkidle
    await page.evaluate(() => { try { localStorage.removeItem('slss-island:trail:v1'); } catch (e) {} });
    const ready = await page.waitForSelector('body.webgl-ready', { timeout: 30000 }).then(() => true, () => false);
    if (!ready) note(stem, 'WebGL 可用時沒有進入 3D 模式');
    else {
      await new Promise(r => setTimeout(r, 1200));
      const colors = await canvasColors(page);
      if (colors < 40) note(stem, `3D 畫布幾乎是空的（${colors} 種顏色）`);
      await page.screenshot({ path: path.join(SHOT_DIR, 'island_3d.png') });
      // 點建築 → 面板
      const pos = await page.evaluate(() => window.__island.screenPos('resampling_methods'));
      await page.mouse.click(pos.x, pos.y);
      await new Promise(r => setTimeout(r, 300));
      const t1 = await page.$eval('#islPanel', el => el.hidden ? '' : document.getElementById('islPanelTitle').textContent);
      if (t1 !== '重抽樣方法') note(stem, `點 Bootstrap 噴泉沒有開對面板（得到「${t1}」）`);
      const refs = await page.$$eval('.isl-item.is-ref', els => els.length);
      if (!refs) note(stem, '選取正課後沒有高亮相關先備頁');
      // 列表 Enter → 面板、焦點到「前往教材」；Esc 關閉並還原焦點
      await page.focus('.isl-item[data-stem="tree_based_methods"] .isl-link');
      await page.keyboard.press('Enter');
      await new Promise(r => setTimeout(r, 900));
      const k = await page.evaluate(() => ({
        title: document.getElementById('islPanelTitle').textContent,
        focus: document.activeElement && document.activeElement.id,
        href: document.getElementById('islPanelGo').getAttribute('href'),
      }));
      if (k.title !== '樹狀方法與集成學習' || k.focus !== 'islPanelGo') note(stem, `鍵盤選取失敗：${JSON.stringify(k)}`);
      if (k.href !== '../tree_based_methods.html') note(stem, `「前往教材」連結錯誤：${k.href}`);
      await page.screenshot({ path: path.join(SHOT_DIR, 'island_3d_selected.png') });
      await page.keyboard.press('Escape');
      const back = await page.evaluate(() => ({
        hidden: document.getElementById('islPanel').hidden,
        focus: document.activeElement && document.activeElement.dataset.stem,
      }));
      if (!back.hidden || back.focus !== 'tree_based_methods') note(stem, `Esc 沒有關閉面板或還原焦點：${JSON.stringify(back)}`);
      // 足跡：標記完成 → 列表與 localStorage
      await page.click('.isl-item[data-stem="introduction"] .isl-mark');
      const done = await page.evaluate(() => ({
        cls: document.querySelector('.isl-item[data-stem="introduction"]').classList.contains('is-done'),
        saved: (localStorage.getItem('slss-island:trail:v1') || '').includes('introduction'),
      }));
      if (!done.cls || !done.saved) note(stem, `標記完成沒有生效：${JSON.stringify(done)}`);
      for (const b of await page.$$('.isl-jump-btn')) { await b.click(); await new Promise(r => setTimeout(r, 120)); }
      await page.click('#islReset');
      await new Promise(r => setTimeout(r, 1200));
      // 地圖標籤：全景時正課 11 章都要有標籤（擠不下時可退成只有編號）；點標籤＝選取
      const tagInfo = await page.$$eval('.isl-tag-core', els => ({
        total: els.length, shown: els.filter(e => !e.classList.contains('is-off')).length }));
      if (tagInfo.shown < tagInfo.total) note(stem, `全景時正課標籤只顯示 ${tagInfo.shown}/${tagInfo.total}`);
      const tag = await page.$('.isl-tag-core:not(.is-off)');
      if (tag) {
        const want = await tag.evaluate(el => el.querySelector('.isl-tag-t').textContent);
        await tag.click(); await new Promise(r => setTimeout(r, 400));
        const got = await page.$eval('#islPanelTitle', el => el.textContent);
        if (got !== want) note(stem, `點地圖標籤「${want}」開成「${got}」`);
        await page.keyboard.press('Escape');
      }
      // 入夜：按鈕狀態、畫面變暗並截圖
      await page.click('#islNight'); await new Promise(r => setTimeout(r, 1800));
      const night = await page.evaluate(() => ({
        pressed: document.getElementById('islNight').getAttribute('aria-pressed'),
        cls: document.getElementById('islStage').classList.contains('is-night') }));
      if (night.pressed !== 'true' || !night.cls) note(stem, `入夜切換無效：${JSON.stringify(night)}`);
      await page.screenshot({ path: path.join(SHOT_DIR, 'island_3d_night.png') });
      await page.click('#islNight'); await new Promise(r => setTimeout(r, 300));
      await page.evaluate(() => { try { localStorage.removeItem('slss-island:night'); } catch (e) {} });
      // 拖曳旋轉時每個畫面幀最多畫一次（曾經因為重複排程，一幀畫十幾次）
      {
        const cv = await page.$('#islCanvas'), bb = await cv.boundingBox();
        await page.evaluate(() => { window.__rafN = 0; const f = () => { window.__rafN++; if (window.__rafN < 1e6) requestAnimationFrame(f); }; requestAnimationFrame(f); });
        const s0 = await page.evaluate(() => ({ d: window.__island.stats().draws, f: window.__rafN }));
        await page.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2); await page.mouse.down();
        for (let i = 0; i < 25; i++) { await page.mouse.move(bb.x + bb.width / 2 + i * 8, bb.y + bb.height / 2, { steps: 2 }); }
        await page.mouse.up(); await new Promise(r => setTimeout(r, 600));
        const s1 = await page.evaluate(() => ({ d: window.__island.stats().draws, f: window.__rafN }));
        if (s1.d - s0.d > s1.f - s0.f + 3) note(stem, `拖曳時繪製次數（${s1.d - s0.d}）多於畫面幀數（${s1.f - s0.f}）：繪製迴圈被重複排程`);
      }
      // 維導導覽：氣泡 → 選「照正課走」→ 第 1 站有代表圖 → 下一站（嚮導移動、繪製不重複排程）→ 結束 → 再開會問要不要接著走
      {
        const sleep = ms => new Promise(r => setTimeout(r, ms));
        await page.evaluate(() => { try { localStorage.removeItem('slss-island:tour:v1'); } catch (e) {} });
        const bubble = await page.waitForSelector('#islBubble:not([hidden])', { timeout: 5000 }).catch(() => null);
        if (!bubble) note(stem, '開場沒有出現維導的氣泡');
        else {
          await bubble.click(); await sleep(300);
          const routes = await page.$$('#islGuideChoices .isl-choice');
          if (routes.length !== 3) note(stem, `選路線應有 3 個選項，得到 ${routes.length}`);
          else {
            await routes[1].click(); await sleep(900);
            await page.waitForFunction(() => document.getElementById('islFigImg').complete, { timeout: 5000 }).catch(() => {});
            const a = await page.evaluate(() => ({
              step: document.getElementById('islGuideStep').textContent,
              title: document.getElementById('islPanelTitle').textContent,
              img: document.getElementById('islFigImg').naturalWidth,
              href: document.getElementById('islFigGo').getAttribute('href'),
              nav: !document.getElementById('islGuideNav').hidden,
            }));
            if (!a.step.startsWith('第 1／11 站') || a.title !== '統計學習導論與 EDA' || !a.nav) note(stem, `導覽第 1 站不對：${JSON.stringify(a)}`);
            if (!a.img) note(stem, '代表互動圖縮圖沒有載入');
            if (!/^\.\.\/introduction\.html#\w+$/.test(a.href || '')) note(stem, `代表圖連結錯誤：${a.href}`);
            const g0 = await page.evaluate(() => window.__island.guidePos());
            const s0 = await page.evaluate(() => ({ d: window.__island.stats().draws, f: window.__rafN }));
            await page.click('#islGuideNext'); await sleep(2000);
            const s1 = await page.evaluate(() => ({ d: window.__island.stats().draws, f: window.__rafN }));
            if (s1.d - s0.d > s1.f - s0.f + 3) note(stem, `導覽跳站時繪製次數（${s1.d - s0.d}）多於畫面幀數（${s1.f - s0.f}）`);
            const b = await page.evaluate(() => ({ title: document.getElementById('islPanelTitle').textContent, g: window.__island.guidePos() }));
            if (b.title !== '統計學習的基本框架') note(stem, `「下一站」沒有前往第 2 站：${b.title}`);
            if (Math.hypot(b.g.x - g0.x, b.g.z - g0.z) < 1) note(stem, '「下一站」後維導沒有移動');
            await page.screenshot({ path: path.join(SHOT_DIR, 'island_3d_tour.png') });
            await page.click('#islGuideEnd'); await sleep(200);
            const c = await page.evaluate(() => ({ panel: document.getElementById('islPanel').hidden, guide: document.getElementById('islGuide').hidden }));
            if (!c.panel || !c.guide) note(stem, `「結束導覽」沒有收起面板：${JSON.stringify(c)}`);
            await page.click('#islBubble'); await sleep(300);
            const r = await page.$$eval('#islGuideChoices .isl-choice b', els => els.map(e => e.textContent));
            if (r[0] !== '接著走') note(stem, `再次開啟導覽沒有問要不要接著走：${JSON.stringify(r)}`);
            // 導覽中點別的島：退出導覽，對話列不能殘留在一般面板上
            await page.click('.isl-choice'); await sleep(600);
            await page.click('.isl-item[data-stem="support_vector_machines"] .isl-link'); await sleep(400);
            const e = await page.evaluate(() => ({ guide: document.getElementById('islGuide').hidden, nav: document.getElementById('islGuideNav').hidden }));
            if (!e.guide || !e.nav) note(stem, `導覽中改選別章後，對話列沒有收起：${JSON.stringify(e)}`);
            await page.keyboard.press('Escape');
          }
        }
        await page.evaluate(() => { try { localStorage.removeItem('slss-island:tour:v1'); } catch (e) {} });
      }
      // 閒置暫停：把門檻調短，確認停止繪製；滑鼠一動就恢復
      const calls = await page.evaluate(() => window.__island.stats().calls);
      if (calls > 80) note(stem, `每幀繪製呼叫過多：${calls}`);
      await page.evaluate(() => { window.__islandIdleMs = 1500; });
      // 軟體算圖幀率很低，日夜淡出、飛行可能還在收尾：最多等 10 秒，直到連續 1 秒沒有新繪製
      let d0 = 0, d1 = -1;
      for (let k = 0; k < 10 && d1 !== d0; k++) {
        d0 = await page.evaluate(() => window.__island.stats().draws);
        await new Promise(r => setTimeout(r, 1000));
        d1 = await page.evaluate(() => window.__island.stats().draws);
      }
      const motionOk = await page.evaluate(() => !matchMedia('(prefers-reduced-motion: reduce)').matches);
      if (motionOk && d1 !== d0) note(stem, `閒置 10 秒後仍在繪製（最後 1 秒 ${d1 - d0} 幀）`);
      const pos2 = await page.evaluate(() => window.__island.screenPos('linear_regression'));
      await page.mouse.move(pos2.x + 5, pos2.y + 5); await page.mouse.move(pos2.x - 5, pos2.y);
      await new Promise(r => setTimeout(r, 1200));
      const d2 = await page.evaluate(() => window.__island.stats().draws);
      if (motionOk && d2 <= d1) note(stem, '有操作後沒有恢復繪製');
      await page.evaluate(() => { window.__islandIdleMs = 0; });
      await page.evaluate(() => { try { localStorage.removeItem('slss-island:trail:v1'); } catch (e) {} });
    }
    await layout(page, '桌面 3D');
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
    await new Promise(r => setTimeout(r, 900));
    await layout(page, '手機 3D');
    await page.screenshot({ path: path.join(SHOT_DIR, 'island_3d_mobile.png') });
    errors.forEach(e => note(stem, '3D：' + e));
    await page.close();
    summary.push('3D ' + (ready ? 'OK' : '失敗'));
  }

  // (b) CDN 被攔、(c) WebGL 不可用 → 2D 地圖
  for (const [mode, label] of [['cdn', 'CDN 失效'], ['nogl', '無 WebGL']]) {
    const { page, errors } = await open(mode);
    await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 1 });
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 2000));
    const r = await layout(page, label + '桌面');
    if (r.webgl) note(stem, `${label}時仍進入 3D 模式`);
    const stageHidden = await page.$eval('#islStage', el => el.hidden);
    if (!stageHidden) note(stem, `${label}時 3D 畫布沒有隱藏`);
    // 2D 模式：點卡片直接前往教材（記錄造訪），不攔截
    await page.click('.isl-mark');
    const marked = await page.$eval('.isl-mark', el => el.getAttribute('aria-pressed'));
    if (marked !== 'true') note(stem, `${label}時無法標記完成`);
    await page.evaluate(() => { try { localStorage.removeItem('slss-island:trail:v1'); } catch (e) {} });
    await page.screenshot({ path: path.join(SHOT_DIR, `island_2d_${mode}.png`), fullPage: true });
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
    await new Promise(r => setTimeout(r, 600));
    await layout(page, label + '手機');
    await page.screenshot({ path: path.join(SHOT_DIR, `island_2d_${mode}_mobile.png`) });
    errors.forEach(e => note(stem, `${label}：${e}`));
    await page.close();
    summary.push(label + (r.webgl ? ' 失敗' : ' → 2D'));
  }

  // 每個入口都指到存在的教材頁
  const missing = [...html.matchAll(/class="isl-link" href="\.\.\/([^"]+)"/g)]
    .map(m => m[1]).filter(f => !fs.existsSync(path.join(ROOT, f)));
  missing.forEach(f => note(stem, '入口指向不存在的 ' + f));
  return `${total} 入口 · ${summary.join(' · ')}`;
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
  if (WITH_ISLAND) {
    const before = problems.length;
    let info = '';
    try { info = await checkIsland(browser); } catch (e) { note('island', '檢查中斷：' + e.message); }
    const n = problems.length - before;
    console.log(`  ${'island/index.html'.padEnd(34)} ${n === 0 ? 'OK  ' : n + ' 問題'} ${info}`);
  }
  await browser.close();
  console.log('');
  problems.forEach(p => console.log('  ✗ ' + p));
  console.log(`\n${problems.length} 個問題（截圖在 ${SHOT_DIR}）`);
  process.exit(problems.length ? 1 : 0);
})();
