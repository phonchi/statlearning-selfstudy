const path = require('path');
const fs = require('fs');
const puppeteer = require('/home/phonchi/.cache/selfstudy-node/node_modules/puppeteer-core');
const root = path.resolve(__dirname, '../../..');
const base = '/home/phonchi/.cache/puppeteer/chrome';
const chrome = path.join(base, fs.readdirSync(base).sort().at(-1), 'chrome-linux64/chrome');
(async () => {
 const browser = await puppeteer.launch({executablePath: chrome, headless: true, args: ['--no-sandbox','--disable-dev-shm-usage']});
 try {
 const page = await browser.newPage();
 await page.setViewport({width:1280,height:1000,deviceScaleFactor:1});
 await page.goto('file://'+path.join(root,'classification.html'), {waitUntil:'networkidle2',timeout:60000});
 await page.waitForFunction(() => window.MathJax?.startup?.document && document.querySelector('mjx-container'),{timeout:30000});
 await page.evaluate(async () => { await MathJax.startup.promise; await HC._mathQueue; await document.fonts.ready; document.documentElement.style.scrollBehavior='auto'; });
 const shots=[];
 async function shot(name, selector, open=[]) {
  await page.evaluate(async (selector,ids) => {
   document.querySelectorAll('details').forEach(d=>d.open=false);
   for(const id of ids) document.getElementById(id).open=true;
   await HC._mathQueue;
   await new Promise(r=>setTimeout(r,300));
   const target=document.querySelector(selector);
   window.scrollTo({top:window.scrollY+target.getBoundingClientRect().top-25,behavior:'instant'});
  },selector,open);
  await new Promise(r=>setTimeout(r,250));
  await page.screenshot({path:path.join(__dirname,'screenshots',name+'.png')});shots.push(name);
 }
 await shot('logistic-model-desktop','#logistic');
 await shot('lda-estimates-desktop','#lda .viz-layout');
 await shot('multiclass-mle-desktop','#w04-detail-multinomial-fit',['w04-detail-multinomial-fit']);
 await shot('fisher-geometry-desktop','#w04-detail-fisher',['w04-detail-fisher']);
 await page.setViewport({width:390,height:844,deviceScaleFactor:1});
 await shot('logistic-model-mobile','#logistic');
 await shot('logistic-quiz-mobile','#qLogOptions');
 await shot('multiclass-mle-mobile','#w04-detail-multinomial-fit',['w04-detail-multinomial-fit']);
 await page.evaluate(async()=>{
  document.querySelectorAll('details').forEach(d=>d.open=true);
  await HC._mathQueue;
  await MathJax.typesetPromise();
 });
 const result=await page.evaluate(()=>({
  mathCount:document.querySelectorAll('mjx-container').length,
  mathErrors:[...document.querySelectorAll('mjx-merror')].map(n=>n.textContent),
  horizontalOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
  detailCount:document.querySelectorAll('details').length,
  estimateTypeset:document.querySelector('#prologue').innerHTML.includes('mjx-mover'),
  sections:[...document.querySelectorAll('section[id]')].map(s=>s.id),
  remainingMathText:(()=>{ const a=[]; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let n; while(n=w.nextNode()){ if(n.parentElement.closest('mjx-container,script,style,pre,code,svg'))continue; if(/\$[^$]+\$|β̂|e\^β/.test(n.textContent))a.push(n.textContent.slice(0,120));}return a;})()
 }));
 result.screenshots=shots;
 fs.writeFileSync(path.join(__dirname,'browser-details.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result,null,2));
 if(result.mathErrors.length || result.horizontalOverflow>2 || result.remainingMathText.length || result.mathCount<150 || !result.estimateTypeset)process.exitCode=1;
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
