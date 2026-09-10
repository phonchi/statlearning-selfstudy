const path=require('path'),fs=require('fs');
const pup=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const root='/home/phonchi/statlearning-selfstudy';
const out=path.join(root,'tools/verification/reading-flow-20260910/shots/ch1-6');
const chromeBase=path.join(process.env.HOME,'.cache/puppeteer/chrome');
const chrome=path.join(chromeBase,fs.readdirSync(chromeBase).sort().at(-1),'chrome-linux64/chrome');
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const checks=[];
function assert(ok,msg){if(!ok)throw new Error(msg);checks.push(msg);}
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await pup.launch({executablePath:chrome,headless:true,args:['--no-sandbox']});
try{
 const p=await browser.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 const load=async(stem,hash='')=>{await p.goto('file://'+root+'/'+stem+'.html'+hash,{waitUntil:'networkidle0'});await p.evaluate(async()=>{if(window.MathJax?.startup?.promise)await MathJax.startup.promise;});await pause(250);};
 for(const width of [1280,390]){
  await p.setViewport({width,height:900});
  await load('introduction');assert(await p.$$eval('details.reading-detail',ds=>ds.every(d=>!d.open)),'Intro default details closed '+width);
  await (await p.$('#eda')).screenshot({path:path.join(out,'intro-eda-reading-'+width+'.png')});
  await load('statistical_learning');assert(await p.$eval('#w02-detail-geometry',d=>!d.open),'Ch2 geometry default closed '+width);
  await (await p.$('#curse')).screenshot({path:path.join(out,'ch2-curse-reading-'+width+'.png')});
  await p.$eval('#w02-detail-geometry',d=>{d.open=true;});await pause(500);
  await p.$eval('#w02curP',x=>{x.value='9';x.dispatchEvent(new Event('input',{bubbles:true}));});await pause(200);
  const before=await p.$eval('#w02curR',x=>x.textContent);
  await p.$eval('#w02-detail-geometry',d=>{d.open=false;});await pause(100);await p.$eval('#w02-detail-geometry',d=>{d.open=true;});await pause(300);
  assert(await p.$eval('#w02curP',x=>x.value)==='9','Ch2 reopen keeps slider '+width);
  assert(await p.$eval('#w02curR',x=>x.textContent)===before,'Ch2 reopen keeps computed radius '+width);
  await (await p.$('#w02-detail-geometry .viz-layout')).screenshot({path:path.join(out,'ch2-geometry-open-'+width+'.png')});
  await load('linear_regression');assert(await p.$eval('#w03-detail-rss-surface',d=>!d.open),'Ch3 RSS default closed '+width);
  await (await p.$('#slr')).screenshot({path:path.join(out,'ch3-slr-reading-'+width+'.png')});
  await p.$eval('#w03-detail-rss-surface',d=>{d.open=true;});await pause(350);
  await p.$eval('#w03rssU',x=>{x.value='35';x.dispatchEvent(new Event('input',{bubbles:true}));});
  await p.$eval('#w03rssV',x=>{x.value='-20';x.dispatchEvent(new Event('input',{bubbles:true}));});await pause(200);
  const rb=await p.$eval('#w03rssVal',x=>x.textContent);
  await p.$eval('#w03-detail-rss-surface',d=>{d.open=false;});await pause(100);await p.$eval('#w03-detail-rss-surface',d=>{d.open=true;});await pause(300);
  assert(await p.$eval('#w03rssU',x=>x.value)==='35' && await p.$eval('#w03rssV',x=>x.value)==='-20','Ch3 reopen keeps sliders '+width);
  assert(await p.$eval('#w03rssVal',x=>x.textContent)===rb,'Ch3 reopen keeps RSS '+width);
  await (await p.$('#w03-detail-rss-surface .viz-layout')).screenshot({path:path.join(out,'ch3-rss-open-'+width+'.png')});
 }
 await load('statistical_learning','#w02curP');assert(await p.$eval('#w02-detail-geometry',d=>d.open),'Ch2 slider deep link opens ancestor');
 await load('statistical_learning','#w02proofBallVolume');assert(await p.$eval('#w02-detail-geometry',d=>d.open)&&await p.$eval('#w02proofBallVolume',d=>d.open),'Ch2 proof deep link opens both levels');
 await load('linear_regression','#w03rssSvg');assert(await p.$eval('#w03-detail-rss-surface',d=>d.open),'Ch3 deep link opens ancestor');
 assert(errors.length===0,'No browser runtime errors');
}finally{await browser.close();}
const report={result:'PASS',checks};fs.writeFileSync(path.join(root,'tools/verification/reading-flow-20260910/ch1-6-focus.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
