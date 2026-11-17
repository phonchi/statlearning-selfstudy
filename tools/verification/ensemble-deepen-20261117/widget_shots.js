const path=require('path'),fs=require('fs');
const P=path.join(process.env.HOME,'.cache/selfstudy-node');const pp=require(path.join(P,'node_modules','puppeteer-core'));
const base=path.join(process.env.HOME,'.cache/puppeteer/chrome'),d=fs.readdirSync(base).sort();const CH=path.join(base,d[d.length-1],'chrome-linux64','chrome');
(async()=>{const b=await pp.launch({executablePath:CH,args:['--no-sandbox']});const p=await b.newPage();
await p.setViewport({width:1280,height:900});await p.goto('file://'+path.resolve(__dirname,'../../../tree_based_methods.html'),{waitUntil:'networkidle2',timeout:60000});
await p.evaluate(async()=>{await MathJax.startup.promise;});
await new Promise(r=>setTimeout(r,1000));
fs.mkdirSync('shots_widgets',{recursive:true});
for(const id of ['w09xgbSvg','w09splitSvg','w09stackSvg']){
 const el=await p.$('#'+id); if(!el){console.log('missing',id);continue;}
 const lay=await el.evaluateHandle(e=>e.closest('.viz-layout'));
 await lay.asElement().screenshot({path:`shots_widgets/${id}.png`});
 console.log(id,'ok');}
await b.close();})();
