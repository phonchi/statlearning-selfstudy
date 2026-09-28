// Measure the actual visible MathJax boxes, including opened details and quiz feedback.
const fs=require('fs'),path=require('path');
const puppeteer=require('/home/phonchi/.cache/selfstudy-node/node_modules/puppeteer-core');
const dir='/home/phonchi/.cache/puppeteer/chrome';
const chrome=path.join(dir,fs.readdirSync(dir).sort().at(-1),'chrome-linux64/chrome');
const root=path.resolve(__dirname,'../../..');
const file=process.argv[2]||path.join(root,'classification.html');
const prefix=process.argv[3]||'after';
(async()=>{const browser=await puppeteer.launch({executablePath:chrome,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});try{
 const page=await browser.newPage();await page.setViewport({width:1280,height:1000});
 await page.goto('file://'+file,{waitUntil:'networkidle2'});
 await page.waitForFunction(()=>window.MathJax?.startup?.document&&document.querySelector('mjx-container'));
 await page.evaluate(async()=>{await MathJax.startup.promise;document.querySelectorAll('details').forEach(d=>d.open=true);await HC._mathQueue;await document.fonts.ready;document.documentElement.style.scrollBehavior='auto';});
 const measure=()=>{
  const roots=[...document.querySelectorAll('mjx-container')].filter(n=>!n.closest('mjx-assistive-mml')&&!n.parentElement.closest('mjx-container')&&n.getBoundingClientRect().width);
  const metrics=roots.map(n=>{const r=n.getBoundingClientRect(),m=n.querySelector('mjx-math').getBoundingClientRect(),s=getComputedStyle(n);return {formula:n.querySelector('mjx-assistive-mml')?.textContent?.slice(0,150),clipped:['hidden','auto','scroll','clip'].includes(s.overflowY)&&(m.top<r.top-1||m.bottom>r.bottom+1),outsideInline:!n.hasAttribute('display')&&m.right>innerWidth+1&&!n.closest('table'),top:r.top-m.top,bottom:m.bottom-r.bottom,overflow:s.overflow};});
  return {formulaCount:roots.length,clipped:metrics.filter(n=>n.clipped),outsideInline:metrics.filter(n=>n.outsideInline),mathErrors:[...document.querySelectorAll('mjx-merror')].filter(n=>!n.closest('mjx-assistive-mml')).map(n=>n.textContent),pageOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth};
 };
 const results={};
 for(const width of [1280,390]){
  await page.setViewport({width,height:width===390?844:1000});
  results[width]=await page.evaluate(measure);
  // Select every answer once so this also exercises dynamic MathJax feedback.
  const ids=await page.$$eval('.quiz-options',ns=>ns.map(n=>n.id));
  const feedbackClips=[];
  for(const id of ids){
   const n=await page.$$eval('#'+id+' .quiz-opt',ns=>ns.length);
   for(let i=0;i<n;i++){
    await page.evaluate(async(id,i)=>{const el=document.querySelectorAll('#'+id+' .quiz-opt')[i];el.click();await HC._mathQueue;},id,i);
    const m=await page.evaluate(measure);if(m.clipped.length)feedbackClips.push({id,answer:i,count:m.clipped.length});
   }
  }
  results[width].feedbackClips=feedbackClips;
  for(const [name,selector]of [['score-intuition','#w04-score-intuition'],['fisher-intuition','#w04-detail-fisher'],['qda-distance','#w04-qda-distance']]){
   if(!await page.$(selector))continue;
   await page.evaluate(sel=>{const n=document.querySelector(sel);window.scrollTo({top:scrollY+n.getBoundingClientRect().top-20,behavior:'instant'});},selector);
   await page.screenshot({path:path.join(__dirname,`${prefix}-${name}-${width}.png`)});
  }
 }
 results.ldaControls=await page.evaluate(()=>{
  const set=(m1,m2,p)=>{document.querySelector('#w04lda1M1').value=String(m1);document.querySelector('#w04lda1M2').value=String(m2);document.querySelector('#w04lda1P1').value=String(p);w04lda1Draw();return document.querySelector('#w04lda1Status').textContent;};
  w04lda1Reset();const tied=set(0,0,.5),priorWins=set(0,0,.7);w04lda1Reset();return {tied,priorWins};
 });
 fs.writeFileSync(path.join(__dirname,prefix+'-clipping.json'),JSON.stringify(results,null,2)+'\n');
 for(const w of [1280,390])console.log(w,JSON.stringify(results[w]));
 const bad=Object.values(results).filter(x=>x.clipped).some(x=>x.clipped.length||x.outsideInline.length||x.mathErrors.length||x.pageOverflow>2||x.feedbackClips.length);
 if(bad||!results.ldaControls.tied.includes('平手')||!results.ldaControls.priorWins.includes('第 1 類'))process.exitCode=1;
 console.log('LDA controls',results.ldaControls);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=2});
