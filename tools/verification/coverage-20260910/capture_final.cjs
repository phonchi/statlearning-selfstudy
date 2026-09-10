const fs=require('fs'),path=require('path'),crypto=require('crypto');
const pup=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const OUT=__dirname,ROOT=path.resolve(OUT,'../../..'),SHOTS=path.join(OUT,'final-reading');
const chromeBase=path.join(process.env.HOME,'.cache/puppeteer/chrome');
const chrome=path.join(chromeBase,fs.readdirSync(chromeBase).sort().at(-1),'chrome-linux64/chrome');
const stems=fs.readdirSync(ROOT).filter(n=>n.endsWith('.html')).map(n=>n.slice(0,-5)).sort();
fs.mkdirSync(SHOTS,{recursive:true});
(async()=>{
 const b=await pup.launch({executablePath:chrome,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const records=[];let cursor=0;
 try{
  await Promise.all(Array.from({length:3},async()=>{
   while(cursor<stems.length){
    const stem=stems[cursor++],p=await b.newPage();
    await p.setViewport({width:1100,height:900,deviceScaleFactor:1});
    const errors=[];p.on('pageerror',e=>errors.push(String(e)));
    try{
     await p.goto('file://'+path.join(ROOT,stem+'.html'),{waitUntil:'networkidle2',timeout:60000});
     await p.evaluate(async()=>{if(window.MathJax?.startup?.promise)await MathJax.startup.promise;});
     const state=await p.$$eval('details.proof',ds=>({count:ds.length,open:ds.filter(d=>d.open).length,ids:ds.map(d=>d.id)}));
     if(state.open)errors.push('Proofs open in default state');
     await p.screenshot({path:path.join(SHOTS,stem+'-top.png')});
     const target=(await p.$('details.proof'))||(await p.$('main section:nth-of-type(3)'))||(await p.$('section'));
     if(target)await target.evaluate(e=>window.scrollTo(0,Math.max(0,e.getBoundingClientRect().top+window.scrollY-150)));
     await p.screenshot({path:path.join(SHOTS,stem+'-reading.png')});
     const proof=await p.$('details.proof');
     if(proof){
      await proof.evaluate(d=>{d.open=true;});await new Promise(r=>setTimeout(r,1000));
      await proof.screenshot({path:path.join(SHOTS,stem+'-proof.png')});
      const es=await p.$$eval('details.proof[open] mjx-merror',es=>es.map(e=>e.textContent));errors.push(...es);
      await proof.evaluate(d=>{d.open=false;});
     }
     await p.setViewport({width:390,height:844,deviceScaleFactor:1});
     if(target)await target.evaluate(e=>window.scrollTo(0,Math.max(0,e.getBoundingClientRect().top+window.scrollY-90)));
     await p.screenshot({path:path.join(SHOTS,stem+'-mobile.png')});
     const overflow=await p.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1);
     if(overflow)errors.push('Mobile page overflow');
     const rec={stem,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,stem+'.html'))).digest('hex'),proofs:state.count,defaultOpen:state.open,errors};
     records.push(rec);console.log(stem,errors.length?'FAIL '+errors.join('; '):'OK',state.count+' collapsed proofs');
    }finally{await p.close();}
   }
  }));
  fs.writeFileSync(path.join(OUT,'final-reading.json'),JSON.stringify({browser:await b.version(),pages:records.sort((a,b)=>a.stem.localeCompare(b.stem))},null,2)+'\n');
  if(records.some(r=>r.errors.length))process.exitCode=1;
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
