const fs=require('fs'),path=require('path');
const pup=require(path.join(process.env.HOME,'.cache/selfstudy-node/node_modules/puppeteer-core'));
const base=path.join(process.env.HOME,'.cache/puppeteer/chrome');
const chrome=path.join(base,fs.readdirSync(base).sort().at(-1),'chrome-linux64/chrome');
(async()=>{
 const browser=await pup.launch({executablePath:chrome,headless:true,args:['--no-sandbox']});
 const results=[];
 try {
  for(const n of ['202','204','206']){
   const url=`https://www.csie.ntu.edu.tw/~htlin/mooc/doc/${n}_handout.pdf`;
   const p=await browser.newPage();let observed=null;
   p.on('response',r=>{if(r.url()===url)observed={status:r.status(),contentType:r.headers()['content-type']};});
   try{const r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:25000});
    results.push({url,status:r?.status(),contentType:r?.headers()['content-type'],certificateErrorsIgnored:false});
   }catch(e){results.push({url,...observed,navigationMessage:String(e),certificateErrorsIgnored:false});}
   await p.close();
  }
 }finally{await browser.close();}
 fs.writeFileSync(path.join(__dirname,'network-browser.json'),JSON.stringify(results,null,2)+'\n');
 console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
