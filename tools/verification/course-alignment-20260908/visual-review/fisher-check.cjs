const fs=require('fs');const path=require('path');
const puppeteer=require('/home/phonchi/.cache/selfstudy-node/node_modules/puppeteer-core');
(async()=>{
 const browser=await puppeteer.launch({executablePath:'/home/phonchi/.cache/puppeteer/chrome/linux-151.0.7922.71/chrome-linux64/chrome',headless:true,args:['--no-sandbox','--disable-setuid-sandbox','--allow-file-access-from-files']});
 const results=[];
 for(const [name,width,height] of [['desktop',1280,900],['mobile',390,844]]){
  const page=await browser.newPage();await page.setViewport({width,height,deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file://'+path.resolve('classification.html'),{waitUntil:'networkidle2',timeout:60000});
  await page.evaluate(async()=>{if(window.MathJax?.startup?.promise) await MathJax.startup.promise;await document.fonts.ready;document.documentElement.style.scrollBehavior='auto';document.body.style.scrollBehavior='auto';});
  const status=await page.evaluate(()=>({mathErrors:[...document.querySelectorAll('mjx-merror')].map(x=>x.textContent),bodyWidth:document.documentElement.scrollWidth,viewport:innerWidth,mathCount:document.querySelectorAll('mjx-container').length,navDisplay:getComputedStyle(document.getElementById('floatNav')).display}));
  for(const spot of ['top','scatter','binary','iris']){
   await page.evaluate(spot=>{let el=document.querySelector('#w04fisher');if(spot==='scatter'){while(el&&!el.textContent.includes('以 nk')){if(el.tagName==='P'&&el.textContent.includes('散布矩陣'))break;el=el.nextElementSibling;}}if(spot==='binary')el=[...document.querySelectorAll('#lda h4')].find(x=>x.textContent.startsWith('二類'));if(spot==='iris')el=[...document.querySelectorAll('#lda h4')].find(x=>x.textContent.includes('Iris'));if(!el)throw Error('missing spot '+spot);window.scrollTo({top:el.getBoundingClientRect().top+window.scrollY-80,behavior:"instant"})},spot);
   await new Promise(r=>setTimeout(r,150));await page.screenshot({path:path.join(__dirname,`fisher-${name}-${spot}.png`)});
  }
  results.push({name,...status,errors});await page.close();
 }
 for(const width of [1360,1361,1440]){const page=await browser.newPage();await page.setViewport({width,height:900});await page.goto('file://'+path.resolve('classification.html'),{waitUntil:'networkidle2'});const nav=await page.evaluate(()=>{const n=document.getElementById('floatNav'),r=n.getBoundingClientRect(),c=document.querySelector('#w04fisher').getBoundingClientRect();return {width:innerWidth,navDisplay:getComputedStyle(n).display,navLeft:r.left,contentRight:c.right,overlap:getComputedStyle(n).display!=='none'&&r.left<c.right};});results.push(nav);await page.close();}console.log(JSON.stringify(results,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
