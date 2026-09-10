const path=require('path'),fs=require('fs');
const pup=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const base=path.join(process.env.HOME,'.cache/puppeteer/chrome');
const chrome=path.join(base,fs.readdirSync(base).sort().at(-1),'chrome-linux64/chrome');
(async()=>{const b=await pup.launch({executablePath:chrome,headless:true,args:['--no-sandbox']});
try{for(const [stem,id] of [['linear_regression','w03proofPartialF'],['classification','w04proofLogistic'],['resampling_methods','w05proofCvVariance'],['model_selection','w06proofLasso']]){
const p=await b.newPage();await p.setViewport({width:800,height:1000});await p.goto('file:///home/phonchi/statlearning-selfstudy/'+stem+'.html',{waitUntil:'networkidle0'});await p.evaluate(async()=>{if(window.MathJax?.startup?.promise)await MathJax.startup.promise;});
await p.$eval('#'+id,e=>{e.open=true;});await new Promise(r=>setTimeout(r,1100));await (await p.$('#'+id)).screenshot({path:path.join(__dirname,'ch1-6-browser',stem+'_proof-focus.png')});
await p.close();}}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
