/* 展開第 7 章收合，檢查 MathJax 錯誤、橫向捲動、新元件；截圖輸出到第一個引數的目錄。 */
const path=require('path'),fs=require('fs');
const P=process.env.PPT_HOME||path.join(process.env.HOME,'.cache/selfstudy-node');
const pp=require(path.join(P,'node_modules','puppeteer-core'));
const base=path.join(process.env.HOME,'.cache/puppeteer/chrome'),dirs=fs.readdirSync(base).sort();
const CH=path.join(base,dirs[dirs.length-1],'chrome-linux64','chrome');
const OUT=process.argv[2];const ROOT=path.resolve(__dirname,'../../..');
(async()=>{const b=await pp.launch({executablePath:CH,args:['--no-sandbox','--disable-dev-shm-usage']});
for(const [w,h,tag] of [[1440,900,'d'],[390,844,'m']]){
 const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.setViewport({width:w,height:h});
 await p.goto('file://'+ROOT+'/beyond_linearity.html',{waitUntil:'networkidle2',timeout:60000});
 await p.evaluate(async()=>{document.querySelectorAll('details').forEach(d=>d.open=true);await MathJax.startup.promise;await MathJax.typesetPromise();});
 await new Promise(r=>setTimeout(r,1500));
 const m=await p.evaluate(()=>({merr:document.querySelectorAll('mjx-merror').length,hs:document.documentElement.scrollWidth-innerWidth,
   wide:[...document.querySelectorAll('.detail-body>p,.detail-body>table,mjx-container')].filter(e=>e.getBoundingClientRect().right>innerWidth+2&&!e.closest('[style*="overflow"]')&&!e.closest('mjx-container[display]')).length}));
 console.log(tag,JSON.stringify(m),'pageerrors',errs.length,errs.slice(0,2));
 for(const id of ['w08-detail-spline-compare','w08-detail-logit-ci','w08-detail-step-coding','w08-detail-basis-fixed-learned','w08-detail-spline-calculation','w08-detail-natural-basis','w08-detail-smoothing-df','w08-detail-smoothing-computation','w08-detail-local-calculation']){
  const el=await p.$('#'+id);const bb=await el.boundingBox();
  await p.evaluate(e=>e.scrollIntoView(),el);await new Promise(r=>setTimeout(r,120));
  await el.screenshot({path:`${OUT}/${tag}_${id}.png`,captureBeyondViewport:true}).catch(e=>console.log(id,e.message));
  console.log(' ',id,Math.round(bb.height));}
 if(tag==='d'){const el=await p.$('#w08shrinkSvg');
  const vals=await p.evaluate(()=>{const o=[];for(const v of [0,10,20,30,40]){const s=document.getElementById('w08shrinkSl');s.value=v;w08shrinkDraw();o.push([v,document.getElementById('w08shrinkSlVal').textContent,document.getElementById('w08shrinkLam').textContent,document.getElementById('w08shrinkDf').textContent,document.getElementById('w08shrinkHead').textContent,document.getElementById('w08shrinkTail').textContent]);}
   document.getElementById('w08shrinkSl').value=20;w08shrinkDraw();return o;});console.log('shrink',JSON.stringify(vals));
  await p.evaluate(()=>document.getElementById('w08shrinkSvg').closest('.viz-layout').scrollIntoView());await new Promise(r=>setTimeout(r,200));
  await (await p.evaluateHandle(()=>document.getElementById('w08shrinkSvg').closest('.viz-layout'))).asElement().screenshot({path:`${OUT}/d_shrink.png`});
  const r=await p.evaluate(()=>{const o={};for(const s of [.2,.3,.5]){w08loessBox=false;const a=w08loessFine(s).jump;w08loessBox=true;const c=w08loessFine(s).jump;o[s]=[+a.toFixed(2),+c.toFixed(2)];}w08loessBox=false;return o;});console.log('最大折動 tricube/box',JSON.stringify(r));
  await p.evaluate(()=>{w08loessToggleKer();document.getElementById('w08loessSvg').closest('.viz-layout').scrollIntoView();});await new Promise(r=>setTimeout(r,200));
  await (await p.evaluateHandle(()=>document.getElementById('w08loessSvg').closest('.viz-layout'))).asElement().screenshot({path:`${OUT}/d_loess_box.png`});
 }
 await p.close();}
await b.close();})();
