#!/usr/bin/env node
/* Independent numerical and rendered-geometry checks for statistics prerequisites.
 * Screenshots stay outside the repo (inline-only visual contract).
 */
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const root = path.resolve(__dirname, '..');
const home = process.env.HOME;
const puppeteer = require(path.join(home, '.cache/selfstudy-node/node_modules/puppeteer-core'));
const chromeBase = path.join(home, '.cache/puppeteer/chrome');
const chrome = process.env.CHROME_PATH || path.join(chromeBase, fs.readdirSync(chromeBase).sort().at(-1), 'chrome-linux64/chrome');
const shots = process.env.SHOT_DIR || '/tmp/statistics-20260906/review';
fs.mkdirSync(shots, {recursive:true});
function close(actual, expected, tol=1e-10) {
  assert.ok(Number.isFinite(actual) && Math.abs(actual-expected) <= tol,
    `actual ${actual}, expected ${expected}, tolerance ${tol}`);
}
(async()=>{
  const browser = await puppeteer.launch({executablePath:chrome,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
  const results = {};
  try {
    const page = await browser.newPage();
    await page.setViewport({width:1280,height:900});
    async function open(stem) {
      await page.goto('file://'+path.join(root,stem+'.html'),{waitUntil:'networkidle2'});
      await page.evaluate(async()=>{if(window.MathJax?.startup?.promise) await MathJax.startup.promise;});
      const mathErrors = await page.$$eval('mjx-merror', els=>els.map(e=>e.textContent));
      assert.deepEqual(mathErrors, [], stem+' MathJax errors');
    }
    async function capture(stem) {
      const widgets = await page.$$('.viz-layout');
      for(let i=0;i<widgets.length;i++) await widgets[i].screenshot({path:path.join(shots,stem+'-widget'+(i+1)+'.png')});
    }
    await open('s1_probability');
    results.s1 = await page.evaluate(()=>{
      const models=[0,.3,.5,1].map(w21Model);
      const run=(p)=>{document.getElementById('w21p').value=p;w21Change();w21Toss(100);return {n:w21Values.length,heads:w21Values.reduce((a,b)=>a+b,0)};};
      const zero=run(0), one=run(1), a=run(.5), b=run(.5);
      w21Reset(); w21Toss(100);
      return {models,zero,one,a,b};
    });
    assert.deepEqual(results.s1.zero,{n:100,heads:0});
    assert.deepEqual(results.s1.one,{n:100,heads:100});
    assert.deepEqual(results.s1.a, results.s1.b);
    close(results.s1.models[1].variance,.21);
    await capture('s1_probability');

    await open('s2_conditional');
    results.s2 = await page.evaluate(()=>{
      const ids=['w22n11','w22n10','w22n01','w22n00'];
      const run=(values)=>{ids.forEach((id,i)=>document.getElementById(id).value=values[i]);w22condDraw();return ['w22condN','w22condAB','w22condBA'].map(id=>document.getElementById(id).textContent);};
      const zero=run([0,0,0,0]);
      const baseline=run([8,2,10,80]);
      return {zero,baseline};
    });
    assert.ok(results.s2.zero[1].includes('未定義'));
    assert.ok(results.s2.baseline[1].includes('0.444'));
    assert.ok(results.s2.baseline[2].includes('0.800'));
    await capture('s2_conditional');

    await open('s3_distributions');
    results.s3=await page.evaluate(()=>{
      const pmf=[0,.2,.5,1].map(p=>Array.from({length:11},(_,k)=>w23binomPmf(k,10,p)));
      const uniform=w23distContinuous('uniform',0,8,2,5);
      const normal=w23distContinuous('normal',0,1,-1,1);
      const narrow=w23distContinuous('normal',0,1,.01,.011);
      const polygons=document.querySelectorAll('#w23distSvg polygon').length;
      const repeated=JSON.stringify(w23cltMeans(10))===JSON.stringify(w23cltMeans(10));
      document.getElementById('w23distKind').value='normal';w23distChange();
      document.getElementById('w23cltN').value='10';w23cltDraw();
      return {pmf,uniform,normal,narrow,polygons,repeated};
    });
    [0,.2,.5,1].forEach((p,i)=>{
      const pmf=results.s3.pmf[i];
      close(pmf.reduce((a,b)=>a+b,0),1);
      close(pmf.reduce((s,q,k)=>s+k*q,0),10*p);
      close(pmf.reduce((s,q,k)=>s+(k-10*p)**2*q,0),10*p*(1-p));
    });
    close(results.s3.uniform,3/8); close(results.s3.normal,.6826894921370859,2e-7);
    assert.ok(results.s3.narrow>0 && results.s3.polygons>0);
    assert.ok(results.s3.repeated);
    await capture('s3_distributions');

    await open('s4_inference');
    results.s4=await page.evaluate(()=>{
      document.getElementById('w24testN').value='25';document.getElementById('w24testMean').value='54.4';
      document.getElementById('w24testSide').value='two';w24testDraw();
      const p=document.getElementById('w24testP').textContent;
      const polys=[...document.querySelectorAll('#w24testSvg polygon')].map(el=>el.getAttribute('points').split(' ').map(v=>Number(v.split(',')[0])));
      const center=w24testSvc.X(0);
      document.getElementById('w24testN').value='100';document.getElementById('w24testMean').value='45';
      document.getElementById('w24testSide').value='right';w24testDraw();
      const farLeft=[...document.querySelectorAll('#w24testSvg polygon')].map(el=>el.getAttribute('points').split(' ').map(v=>Number(v.split(',')[0])));
      document.getElementById('w24testN').value='25';document.getElementById('w24testMean').value='54.4';
      document.getElementById('w24testSide').value='two';w24testDraw();
      document.getElementById('w24ciN').value='10';document.getElementById('w24ciLevel').value='.99';
      // DOM select values use the canonical strings.
      document.getElementById('w24ciLevel').value='0.99';
      document.getElementById('w24ciLevel').dispatchEvent(new Event('change'));
      w24ciAdd(); const first=JSON.stringify(w24ciRows);
      const rows=w24ciRows.map(x=>({...x}));
      const counts={total:w24ciTotal,hit:w24ciHit};
      const domain=w24ciSvc.xd.slice();
      return {p,polys,farLeft,center,rows,counts,domain,critical:w24ciCritical(.99)};
    });
    close(Number(results.s4.p),.0278,1e-5);
    assert.equal(results.s4.polys.length,2,'two tails must be separate polygons');
    assert.equal(results.s4.farLeft.length,1);
    assert.ok(Math.min(...results.s4.farLeft[0])<results.s4.center && Math.max(...results.s4.farLeft[0])>results.s4.center,'right tail of far-left z must cover displayed curve');
    for(const xs of results.s4.polys) assert.ok(Math.max(...xs)<=results.s4.center || Math.min(...xs)>=results.s4.center,'tail shading crosses null center');
    close(results.s4.critical,2.5758293035489004);
    for(const row of results.s4.rows) {
      close(row.hi-row.lo,2*2.5758293035489004*10/Math.sqrt(10));
      assert.equal(row.cover,row.lo<=50 && row.hi>=50);
      assert.ok(row.lo>=results.s4.domain[0] && row.hi<=results.s4.domain[1]);
    }
    assert.equal(results.s4.counts.hit,results.s4.rows.filter(r=>r.cover).length);
    await capture('s4_inference');

    await open('s5_bayesian');
    results.s5=await page.evaluate(()=>{
      const cases=[[1,1],[2,2],[9,5],[40,40]];
      const density=cases.map(([a,b])=>[.1,.5,.9].map(x=>w25betaDensity(x,a,b)));
      const integrals=cases.map(([a,b])=>{let s=0;const n=4000;for(let i=0;i<=n;i++)s+=w25betaDensity(i/n,a,b)*(i===0||i===n?.5:1);return s/n;});
      const endpoints=[w25betaDensity(0,1,5),w25betaDensity(1,5,1),w25betaDensity(0,2,2),w25betaDensity(1,2,2)];
      [['w25alpha',2],['w25beta',2],['w25success',7],['w25failure',3]].forEach(([id,v])=>document.getElementById(id).value=v);
      w25bayesDraw();
      return {density,integrals,endpoints,post:document.getElementById('w25postRead').textContent,mean:document.getElementById('w25meanRead').textContent,ratio:Math.exp(w25logLike(.7,7,3)-w25logLike(.5,7,3))};
    });
    function factorial(n){let v=1;for(let k=2;k<=n;k++)v*=k;return v;}
    [[1,1],[2,2],[9,5],[40,40]].forEach(([a,b],i)=>{
      [.1,.5,.9].forEach((x,j)=>close(results.s5.density[i][j],factorial(a+b-1)/(factorial(a-1)*factorial(b-1))*x**(a-1)*(1-x)**(b-1),1e-9));
      close(results.s5.integrals[i],1,1e-6);
    });
    results.s5.endpoints.forEach((v,i)=>close(v,[5,5,0,0][i]));
    assert.equal(results.s5.post,'Beta(9, 5)'); close(Number(results.s5.mean),.643,1e-6);
    close(results.s5.ratio,(.7**7*.3**3)/(.5**10));
    await capture('s5_bayesian');

    await open('s6_regression');
    results.s6=await page.evaluate(()=>{
      w26olsSolve();
      const optimum={...w26olsFit};
      const rectangles=[];
      for(const b0 of [-2,4])for(const b1 of [-1,3]){
        document.getElementById('w26b0').value=b0;document.getElementById('w26b1').value=b1;w26olsDraw();
        rectangles.push(...[...document.querySelectorAll('#w26olsSvg rect.errsquare')].map(e=>['x','y','width','height'].map(a=>Number(e.getAttribute(a)))));
      }
      w26olsSolve();
      return {optimum,rectangles};
    });
    close(results.s6.optimum.b0,.8);close(results.s6.optimum.b1,1);close(results.s6.optimum.rss,.8);close(results.s6.optimum.r2,25/27);
    for(const [x,y,w,h] of results.s6.rectangles) assert.ok(x>=0 && y>=0 && x+w<=620 && y+h<=430,'residual square outside SVG');
    await capture('s6_regression');

    // All responses and readable full-page/mobile screenshots are covered by browser_check.js.
    console.log(JSON.stringify(results,null,2));
    console.log('PASS: six pages; independent reference values, seed repeatability, zero denominators, exact tail regions, interval bounds, Beta normalization, OLS geometry.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
