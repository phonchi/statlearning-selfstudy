// Capture each 00C section with every reading detail opened (desktop 1280, mobile 390).
const path = require('path'), fs = require('fs');
const HOME = process.env.HOME, PPT = path.join(HOME, '.cache/selfstudy-node');
const puppeteer = require(path.join(PPT, 'node_modules', 'puppeteer-core'));
const base = path.join(HOME, '.cache/puppeteer/chrome');
const chrome = path.join(base, fs.readdirSync(base).sort().pop(), 'chrome-linux64', 'chrome');
const ROOT = path.resolve(__dirname, '../../..'), OUT = path.join(__dirname, 'sections');
fs.mkdirSync(OUT, {recursive: true});
(async () => {
  const b = await puppeteer.launch({executablePath: chrome, args: ['--no-sandbox']});
  for (const [tag, w] of [['desktop', 1280], ['mobile', 390]]) {
    const p = await b.newPage();
    await p.setViewport({width: w, height: 900, deviceScaleFactor: 1});
    await p.goto('file://' + path.join(ROOT, '00c_ai_assisted.html'), {waitUntil: 'networkidle0'});
    await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
    await new Promise(r => setTimeout(r, 800));
    const ids = await p.evaluate(() => [...document.querySelectorAll('section[id]')].map(s => s.id));
    for (const id of ids) {
      const el = await p.$('#' + id);
      await el.screenshot({path: path.join(OUT, `${tag}-${id}.png`)});
    }
    const overflow = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    console.log(tag, ids.join(','), 'horizontal overflow:', overflow);
  }
  await b.close();
})();
