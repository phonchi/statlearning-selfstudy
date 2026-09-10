/* Reading flow's only newly hidden timer: evalMSE. No frame reset on collapse. */
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const root = path.resolve(__dirname, '../../..');
const puppeteer = require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const chromeBase = path.join(process.env.HOME,'.cache/puppeteer/chrome');
const chrome = path.join(chromeBase,fs.readdirSync(chromeBase).sort().at(-1),'chrome-linux64/chrome');
const pause = ms => new Promise(r => setTimeout(r,ms));
(async()=>{
 const browser=await puppeteer.launch({executablePath:chrome,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
 try {
  const page=await browser.newPage();await page.setViewport({width:1280,height:900});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file://'+path.join(root,'p2_flow_functions.html'),{waitUntil:'networkidle2'});
  const id='w15detail-function-lab';
  assert.equal(await page.$eval('#'+id,e=>e.open),false);
  await page.$eval('#'+id,e=>{e.open=true});await pause(150);
  await page.$eval('#'+id+' button[onclick="w15fnPlay()"]',e=>e.click());await pause(700);
  const playing=await page.evaluate(()=>({frame:w15fnI,timer:w15fnTimer}));assert(playing.frame>0);assert(playing.timer!==null);
  await page.$eval('#'+id,e=>{e.open=false});await pause(80);
  const closed=await page.evaluate(()=>({frame:w15fnI,timer:w15fnTimer,button:document.querySelector('#w15detail-function-lab button[onclick="w15fnPlay()"]').textContent}));
  assert.equal(closed.frame,playing.frame);assert.equal(closed.timer,null);assert.equal(closed.button,'▶ 重新播放');
  await pause(1300);
  assert.equal(await page.evaluate(()=>w15fnI),closed.frame);
  await page.$eval('#'+id,e=>{e.open=true});await pause(300);
  const reopened=await page.evaluate(()=>({frame:w15fnI,timer:w15fnTimer}));assert.equal(reopened.frame,closed.frame);assert.equal(reopened.timer,null);
  await page.$eval('#'+id+' button[onclick="w15fnStep()"]',e=>e.click());
  assert.equal(await page.evaluate(()=>w15fnI),closed.frame+1);
  console.log(JSON.stringify({playing,closed,reopened,errors},null,2));assert.deepEqual(errors,[]);
  console.log('PASS: close stops timer, preserves frame and updates button; reopen stays paused; single-step continues.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
