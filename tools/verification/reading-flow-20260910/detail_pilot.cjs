const fs=require('fs'),path=require('path');
const puppeteer=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const base=path.join(process.env.HOME,'.cache/puppeteer/chrome');
const chrome=path.join(base,fs.readdirSync(base).sort().at(-1),'chrome-linux64/chrome');
(async()=>{
 const b=await puppeteer.launch({executablePath:chrome,headless:true,args:['--no-sandbox']});
 const p=await b.newPage();const errors=[];p.on('pageerror',e=>errors.push(String(e)));
 const settle=async()=>{await new Promise(r=>setTimeout(r,300));await p.evaluate(async()=>{await HC._mathQueue;});};
 try{
  await p.setViewport({width:1280,height:900});
  await p.goto('file://'+path.join(__dirname,'intermediate/geometry-pilot.html'),{waitUntil:'networkidle2'});
  await p.evaluate(async()=>{await MathJax.startup.promise;});
  const id='w02-detail-pilot-geometry';
  if(await p.$eval('#'+id,d=>d.open))throw Error('not collapsed by default');
  await p.click('#'+id+' > summary');await settle();
  const dimensions=await p.$eval('#w02curChart',c=>[c.width,c.height]);
  if(dimensions.some(x=>x<50))throw Error('hidden chart failed to resize: '+dimensions);
  await p.$eval('#w02curP',el=>{el.value='10';el.dispatchEvent(new Event('input',{bubbles:true}));});
  await p.$eval('#'+id,d=>d.open=false);await settle();
  await p.$eval('#'+id,d=>d.open=true);await settle();
  if(await p.$eval('#w02curP',e=>e.value)!=='10')throw Error('reopening reset slider');
  await p.$eval('#'+id,d=>d.open=false);await settle();
  await p.evaluate(()=>{location.hash='w02curChart';});await settle();
  if(!await p.$eval('#'+id,d=>d.open))throw Error('deep link did not open ancestor');
  await p.setViewport({width:390,height:844});await settle();
  const mobile=await p.evaluate(()=>({width:document.documentElement.scrollWidth,viewport:innerWidth,chart:[HC.get('w02curChart').width,HC.get('w02curChart').height]}));
  if(mobile.width>mobile.viewport+1)throw Error('mobile overflow '+JSON.stringify(mobile));
  if(errors.length)throw Error(errors.join('; '));
  fs.mkdirSync(path.join(__dirname,'shots'),{recursive:true});
  await p.screenshot({path:path.join(__dirname,'shots/pilot-mobile.png')});
  console.log(JSON.stringify({status:'PASS',initialCollapsed:true,desktopChart:dimensions,reopeningPreservesSlider:true,deepLinkOpensAncestors:true,mobile,errors},null,2));
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
