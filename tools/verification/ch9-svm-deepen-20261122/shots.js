/* 展開整頁收合，檢查 MathJax 錯誤、水平溢出與 pageerror；把指定 id 的元素截圖。
   用法：node shots.js <stem> <輸出目錄> <id> [<id> ...]   （桌面 1440 與手機 390 各一次） */
const path = require('path'), fs = require('fs');
const P = process.env.PPT_HOME || path.join(process.env.HOME, '.cache/selfstudy-node');
const pp = require(path.join(P, 'node_modules', 'puppeteer-core'));
const base = path.join(process.env.HOME, '.cache/puppeteer/chrome'), dirs = fs.readdirSync(base).sort();
const CH = path.join(base, dirs[dirs.length - 1], 'chrome-linux64', 'chrome');
const [stem, OUT, ...ids] = process.argv.slice(2);
const ROOT = path.resolve(__dirname, '../../..');
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await pp.launch({ executablePath: CH, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  for (const [w, h, tag] of [[1440, 900, 'd'], [390, 844, 'm']]) {
    const p = await b.newPage(); const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    await p.setViewport({ width: w, height: h });
    await p.goto('file://' + ROOT + '/' + stem + '.html', { waitUntil: 'networkidle2', timeout: 60000 });
    await p.evaluate(async () => {
      document.querySelectorAll('details').forEach(d => d.open = true);
      await MathJax.startup.promise; await MathJax.typesetPromise();
    });
    await new Promise(r => setTimeout(r, 1500));
    const m = await p.evaluate(() => ({
      merr: document.querySelectorAll('mjx-merror').length,
      hs: document.documentElement.scrollWidth - innerWidth,
      wide: [...document.querySelectorAll('.detail-body>p,.detail-body>table,section>p,mjx-container')]
        .filter(e => e.getBoundingClientRect().right > innerWidth + 2 && !e.closest('[style*="overflow"]')
                     && !e.closest('mjx-container[display]')).length }));
    console.log(tag, JSON.stringify(m), 'pageerrors', errs.length, errs.slice(0, 3));
    for (const id of ids) {
      const el = await p.$('#' + id);
      if (!el) { console.log('  缺少', id); continue; }
      await p.evaluate(e => e.scrollIntoView(), el); await new Promise(r => setTimeout(r, 150));
      await el.screenshot({ path: `${OUT}/${tag}_${id}.png`, captureBeyondViewport: true })
        .catch(e => console.log(id, e.message));
      const bb = await el.boundingBox();
      console.log('  ', id, Math.round(bb ? bb.height : -1));
    }
    await p.close();
  }
  await b.close();
})();
