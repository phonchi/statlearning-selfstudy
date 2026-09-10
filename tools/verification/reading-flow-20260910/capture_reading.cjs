const fs=require('fs'),path=require('path'),crypto=require('crypto');
const pup=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const OUT=__dirname,ROOT=path.resolve(OUT,'../../..'),SHOTS=path.join(OUT,'final-views');
const base=path.join(process.env.HOME,'.cache/puppeteer/chrome');
const chrome=path.join(base,fs.readdirSync(base).sort().at(-1),'chrome-linux64/chrome');
const sections={introduction:'eda',statistical_learning:'curse',linear_regression:'mlr',classification:'logistic',resampling_methods:'bootstrap',model_selection:'lasso',beyond_linearity:'smooth',tree_based_methods:'modern',support_vector_machines:'soft',unsupervised_learning:'practical',deep_learning:'fitting'};
const stems=fs.readdirSync(ROOT).filter(n=>n.endsWith('.html')).map(n=>n.slice(0,-5)).sort();
fs.mkdirSync(SHOTS,{recursive:true});
(async()=>{
 const b=await pup.launch({executablePath:chrome,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const records=[];let cursor=0;
 try{
  await Promise.all(Array.from({length:3},async()=>{
   while(cursor<stems.length){
    const stem=stems[cursor++],p=await b.newPage(),errors=[];
    p.on('pageerror',e=>errors.push(String(e)));
    try{
     await p.setViewport({width:1100,height:900,deviceScaleFactor:1});
     await p.goto('file://'+path.join(ROOT,stem+'.html'),{waitUntil:'networkidle2',timeout:60000});
     await p.evaluate(async()=>{if(window.MathJax?.startup?.promise)await MathJax.startup.promise;});
     const stats=await p.evaluate(()=>({
      details:document.querySelectorAll('details.reading-detail').length,
      defaultOpen:document.querySelectorAll('details.reading-detail[open],details.proof[open]').length,
      height:document.documentElement.scrollHeight,
      overflow:document.documentElement.scrollWidth>innerWidth+1
     }));
     if(stats.defaultOpen)errors.push('Default detail/proof open');
     if(stats.overflow)errors.push('Default desktop overflow');
     await p.screenshot({path:path.join(SHOTS,stem+'-top.png')});
     const selector=sections[stem]?'#'+sections[stem]:'section';
     let target=await p.$(selector);if(!target)target=await p.$('.container');
     if(target)await target.evaluate(e=>window.scrollTo(0,Math.max(0,e.getBoundingClientRect().top+scrollY-20)));
     await p.screenshot({path:path.join(SHOTS,stem+'-reading.png')});
     const detail=(target&&await target.$('details.reading-detail'))||await p.$('details.reading-detail');
     if(detail){
      await detail.evaluate(d=>{for(let e=d.parentElement;e;e=e.parentElement)if(e.tagName==='DETAILS')e.open=true;d.open=true;});
      await new Promise(r=>setTimeout(r,180));
      await p.evaluate(async()=>{await HC._mathQueue;});
      await detail.evaluate(e=>window.scrollTo(0,Math.max(0,e.getBoundingClientRect().top+scrollY-20)));
      await p.screenshot({path:path.join(SHOTS,stem+'-expanded.png')});
     }
     await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>{d.open=false;}));
     await p.setViewport({width:390,height:844,deviceScaleFactor:1});
     await new Promise(r=>setTimeout(r,180));
     if(target)await target.evaluate(e=>window.scrollTo(0,Math.max(0,e.getBoundingClientRect().top+scrollY-20)));
     const mobileOverflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
     if(mobileOverflow)errors.push('Default mobile overflow');
     await p.screenshot({path:path.join(SHOTS,stem+'-mobile.png')});
     records.push({stem,...stats,mobileOverflow,errors,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,stem+'.html'))).digest('hex')});
     console.log(stem,errors.length?'FAIL '+errors.join('; '):'OK',stats.details+' details');
    }finally{await p.close();}
   }
  }));
  fs.writeFileSync(path.join(OUT,'final-views.json'),JSON.stringify({browser:await b.version(),pages:records.sort((a,b)=>a.stem.localeCompare(b.stem))},null,2)+'\n');
  if(records.some(r=>r.errors.length))process.exitCode=1;
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
