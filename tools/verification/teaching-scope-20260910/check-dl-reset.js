const fs=require('fs'),path=require('path');
const puppeteer=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
(async()=>{
const dir=path.join(process.env.HOME,'.cache/puppeteer/chrome');const chrome=path.join(dir,fs.readdirSync(dir).sort().pop(),'chrome-linux64/chrome');
const browser=await puppeteer.launch({executablePath:chrome,headless:true,args:['--no-sandbox']});
try{
 const p=await browser.newPage();await p.setViewport({width:1280,height:900});
 await p.goto('file:///home/phonchi/statlearning-selfstudy/deep_learning.html',{waitUntil:'networkidle2'});
 await p.evaluate(async()=>{document.getElementById('w11detail-parameters').open=true;if(window.MathJax?.startup?.promise)await MathJax.startup.promise;await HC._mathQueue;});
 for(let i=0;i<3;i++){
  await p.evaluate(()=>{document.getElementById('w11paramH1').value=16;document.getElementById('w11paramH2').value=8;w11paramDraw();});
  await p.click('button[onclick="w11paramReset()"]');
  const out=await p.evaluate(()=>({h1:document.getElementById('w11paramH1').value,h2:document.getElementById('w11paramH2').value,total:document.getElementById('w11paramTot').textContent}));
  if(out.h1!=='256'||out.h2!=='128'||out.total.replace(/[^0-9]/g,'')!=='235146')throw new Error(JSON.stringify(out));
  console.log('reset',i+1,JSON.stringify(out));
 }
 console.log('PASS: actual pointer click restores both widths and parameter total');
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
