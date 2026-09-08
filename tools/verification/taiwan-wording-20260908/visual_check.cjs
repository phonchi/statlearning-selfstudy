const fs=require('fs'),path=require('path');
const puppeteer=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const root=path.resolve(__dirname,'../../..'),base=path.join(process.env.HOME,'.cache/puppeteer/chrome');
(async()=>{const browser=await puppeteer.launch({executablePath:path.join(base,fs.readdirSync(base).sort().at(-1),'chrome-linux64/chrome'),args:['--no-sandbox','--disable-dev-shm-usage']});
for(const width of [1280,390]){const page=await browser.newPage();await page.setViewport({width,height:900});const errors=[];page.on('pageerror',e=>errors.push(e.message));
for(const [file,selector,label]of [['index.html','.container','home'],['introduction.html','#w01ivWageAge','wage'],['classification.html','#threshold','threshold'],['model_selection.html','#reference','model-reference']].filter(x=>!process.env.REVIEW_LABEL||x[2]===process.env.REVIEW_LABEL)){
await page.goto('file://'+path.join(root,file),{waitUntil:'networkidle2'});await page.evaluate(async()=>{await document.fonts.ready;if(window.MathJax?.startup?.promise)await MathJax.startup.promise;});
const el=await page.$(selector);await el.evaluate(el=>window.scrollTo({top:el.getBoundingClientRect().top+scrollY-25,behavior:'instant'}));
const state=await page.evaluate(()=>({width:innerWidth,bodyWidth:document.documentElement.scrollWidth,mathErrors:document.querySelectorAll('mjx-merror').length,fitWords:document.body.innerText.includes('擬合')}));
if(state.bodyWidth>width||state.mathErrors||errors.length)throw Error(JSON.stringify({file,state,errors}));
await page.screenshot({path:path.join(__dirname,'screenshots',`${label}-${width}.png`)});console.log('PASS',file,JSON.stringify(state));}
await page.close();}await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
