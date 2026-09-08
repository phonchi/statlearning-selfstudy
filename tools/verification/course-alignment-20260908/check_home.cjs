const path=require('path'),fs=require('fs');
const root=path.resolve(__dirname,'../../..');
const puppeteer=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const base=path.join(process.env.HOME,'.cache/puppeteer/chrome');
(async()=>{
 const browser=await puppeteer.launch({executablePath:path.join(base,fs.readdirSync(base).sort().at(-1),'chrome-linux64/chrome'),args:['--no-sandbox','--disable-dev-shm-usage']});
 for(const width of [1280,390]){
  const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewport({width,height:900});await page.goto('file://'+path.join(root,'index.html'),{waitUntil:'networkidle2'});await page.evaluate(()=>document.fonts.ready);
  const got=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,cards:document.querySelectorAll('a.ch-card').length,countLabels:document.querySelectorAll('.ch-meta').length}));
  if(got.scrollWidth>width||got.cards!==26||got.countLabels||errors.length)throw Error(JSON.stringify({got,errors}));
  await page.screenshot({path:path.join(__dirname,'screenshots',width===1280?'index.png':'index_mobile.png'),fullPage:true});
  await Promise.all([page.waitForNavigation(),page.click('a.ch-card')]);
  if(!page.url().endsWith('/00a_why_code.html'))throw Error('Home chapter link failed');
  console.log('PASS home',JSON.stringify(got),'first chapter navigation');await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
