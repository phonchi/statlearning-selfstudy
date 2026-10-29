#!/usr/bin/env node
/* 產生 3D 群島面板裡各章的代表互動圖縮圖：island/figs/<stem>.webp。
 *
 * 要截哪張圖由 tools/island_meta.py 的 FIGS 決定：開啟教材頁、等 Chart.js 與 MathJax 畫完、
 * 執行 prep（例如先跑到收斂），再截 #fig 所在的 .viz-panel（whole=False 時只截 #fig）。教材改版後重跑一次，結果要 commit。
 * Chart.js 從 jsDelivr 載入，需要網路。puppeteer-core 的安裝方式見 browser_check.js。
 *
 * 用法：
 *   node tools/build_island_figs.js                 # 全部
 *   node tools/build_island_figs.js resampling_methods
 */
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');

const PPT_HOME = process.env.PPT_HOME || path.join(process.env.HOME, '.cache/selfstudy-node');
const puppeteer = require(path.join(PPT_HOME, 'node_modules', 'puppeteer-core'));
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'island', 'figs');
const CHROME = process.env.CHROME_PATH || (() => {
  const base = path.join(process.env.HOME, '.cache/puppeteer/chrome');
  const dirs = fs.existsSync(base) ? fs.readdirSync(base).sort() : [];
  if (!dirs.length) { console.error('找不到 Chrome。先跑：npx puppeteer browsers install chrome'); process.exit(2); }
  return path.join(base, dirs[dirs.length - 1], 'chrome-linux64', 'chrome');
})();

const FIGS = JSON.parse(execFileSync('python3', ['-c',
  'import json, sys; sys.path.insert(0, "tools"); import island_meta as M; print(json.dumps(M.FIGS))'],
  { cwd: ROOT, encoding: 'utf8' }));
const ARGS = process.argv.slice(2).map(s => s.replace(/\.html$/, ''));
const STEMS = ARGS.length ? ARGS : Object.keys(FIGS);

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'] });
  let failed = 0;
  for (const stem of STEMS) {
    const f = FIGS[stem];
    if (!f) { console.error(`  ${stem}: FIGS 沒有這一章`); failed++; continue; }
    const page = await browser.newPage();
    // 寬 1100：教材的雙欄版面（圖＋側欄）；DPR 1.25 讓縮圖在面板（約 340px）上的高解析螢幕仍清楚
    await page.setViewport({ width: 1100, height: 900, deviceScaleFactor: 1.25 });
    await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'no-preference' }]);
    await page.goto('file://' + path.join(ROOT, stem + '.html'), { waitUntil: 'networkidle2', timeout: 60000 });
    await page.evaluate(async () => {
      if (window.MathJax?.startup?.promise) await MathJax.startup.promise;
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
    });
    await new Promise(r => setTimeout(r, 400));
    if (f.prep) {
      await page.evaluate(src => (0, eval)(src), f.prep);
      await new Promise(r => setTimeout(r, f.wait || 3000));
    }
    const el = await page.evaluateHandle((id, whole) => {
      const t = document.getElementById(id);
      return t && (whole && t.closest('.viz-panel') || t);
    }, f.fig, f.whole !== false);
    if (!el || !(await el.asElement())) { console.error(`  ${stem}: 找不到 #${f.fig}`); failed++; await page.close(); continue; }
    await el.asElement().evaluate(e => e.scrollIntoView({ block: 'center' }));
    await new Promise(r => setTimeout(r, 300));
    const file = path.join(OUT, stem + '.webp');
    await el.asElement().screenshot({ path: file, type: 'webp', quality: 78 });
    const box = await el.asElement().boundingBox();
    console.log(`  ${stem.padEnd(26)} #${f.fig.padEnd(14)} ${Math.round(box.width)}×${Math.round(box.height)}  ${(fs.statSync(file).size / 1024).toFixed(1)} KB`);
    await page.close();
  }
  await browser.close();
  if (failed) process.exit(1);
})();
