const path=require('path'),fs=require('fs');
const P=path.join(process.env.HOME,'.cache/selfstudy-node');const pp=require(path.join(P,'node_modules','puppeteer-core'));
const base=path.join(process.env.HOME,'.cache/puppeteer/chrome'),d=fs.readdirSync(base).sort();const CH=path.join(base,d[d.length-1],'chrome-linux64','chrome');
(async()=>{const b=await pp.launch({executablePath:CH,args:['--no-sandbox']});const p=await b.newPage();
await p.setViewport({width:390,height:844});await p.goto('file://'+process.argv[2],{waitUntil:'networkidle2',timeout:60000});
await p.evaluate(async()=>{document.querySelectorAll('details').forEach(d=>d.open=true);await MathJax.startup.promise;await MathJax.typesetPromise();});
await new Promise(r=>setTimeout(r,1500));
const r=await p.evaluate(()=>[...document.querySelectorAll('section#boosting mjx-container')].filter(e=>!e.closest('mjx-assistive-mml')&&e.getBoundingClientRect().right>innerWidth+2).map(e=>({right:Math.round(e.getBoundingClientRect().right),w:Math.round(e.getBoundingClientRect().width),disp:e.getAttribute('display'),tex:(e.querySelector('mjx-assistive-mml')||e).textContent.slice(0,80),ctx:e.parentElement.textContent.slice(0,60)})));
console.log(JSON.stringify(r,null,1));await b.close();})();
