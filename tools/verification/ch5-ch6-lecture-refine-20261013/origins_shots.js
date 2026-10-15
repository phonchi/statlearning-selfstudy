// 打開指定收合區並逐一截圖（1440 與 390 寬），用來目視檢查數學排版與表格。
const path = require('path'), fs = require('fs');
const PPT_HOME = process.env.PPT_HOME || path.join(process.env.HOME, '.cache/selfstudy-node');
const puppeteer = require(path.join(PPT_HOME, 'node_modules', 'puppeteer-core'));
const ROOT = path.resolve(__dirname, '../../..');
const OUT = process.argv[2];
const base = path.join(process.env.HOME, '.cache/puppeteer/chrome');
const CHROME = path.join(base, fs.readdirSync(base).sort().pop(), 'chrome-linux64', 'chrome');
const TARGETS = {
  model_selection: ["w06-detail-criteria-origins","w06-detail-cp-intuition","w06-detail-cp-risk","w06-detail-criteria-scale"],
};
const _OLD = {
  resampling_methods: ['w05proofPortfolio', 'w05-boot-world', 'w05-detail-boot-why-replace', 'w05-detail-misuse-code', 'w05-detail-bootstrap-oob', 'w05-boot-appendix'],
  model_selection: ['subset', 'w06-detail-two-stage', 'w06-detail-snooping', 'w06-detail-guided-search', 'w06-detail-orthogonal-forward', 'w06-detail-cp-intuition', 'w06-detail-aic-bic-goals', 'w06-detail-adjr2-df', 'w06-detail-cv-se', 'dx-geom', 'w06-why-diag', 'w06-detail-diag-closed-form', 'w06-why-bayes', 'prologue'],
};
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  for (const [stem, ids] of Object.entries(TARGETS)) for (const w of [1440, 390]) {
    const page = await browser.newPage();
    await page.setViewport({ width: w, height: 900 });
    await page.goto('file://' + path.join(ROOT, stem + '.html'), { waitUntil: 'networkidle2', timeout: 60000 });
    for (const id of ids) {
      await page.evaluate(id => { const e = document.getElementById(id); if (e && e.tagName === 'DETAILS') e.open = true; }, id);
    }
    await page.evaluate(() => window.MathJax && MathJax.typesetPromise());
    await new Promise(r => setTimeout(r, 1500));
    const err = await page.evaluate(() => document.querySelectorAll('mjx-merror').length);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    console.log(stem, w, 'mjx-merror', err, 'horizontal overflow', overflow);
    for (const id of ids) {
      const el = await page.$('#' + id);
      if (!el) { console.log('missing', id); continue; }
      await el.screenshot({ path: path.join(OUT, `${stem}-${w}-${id}.png`) }).catch(e => console.log(id, String(e).slice(0, 80)));
    }
    await page.close();
  }
  await browser.close();
})();
