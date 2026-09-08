/* Compare JavaScript ASTs; only displayed Chinese string values may change. */
const fs=require('fs'),path=require('path'),cp=require('child_process');
const acorn=require('internal/deps/acorn/acorn/dist/acorn');
const root=path.resolve(__dirname,'../../..'),base=JSON.parse(fs.readFileSync(path.join(__dirname,'baseline.json'))).head;
function normalize(node){
 if(Array.isArray(node))return node.map(normalize);
 if(node&&typeof node==='object'){
  const out={};
  for(const [k,v]of Object.entries(node)){
   if(['start','end','raw'].includes(k))continue;
   if(k==='value'&&typeof v==='string'&&/[\u3400-\u9fff]/.test(v)){
    out[k]='<reader-text>';out.textNumbers=v.match(/\d+(?:\.\d+)?/g)||[];continue;
   }
   // Template text may vary; ${expressions} remain normal AST nodes.
   if(node.type==='TemplateElement'&&k==='value'){
    out[k]=/[\u3400-\u9fff]/.test(v.cooked)?{readerText:true,numbers:v.cooked.match(/\d+(?:\.\d+)?/g)||[]}:v;continue;
   }
   out[k]=normalize(v);
  }return out;
 }return node;
}
function scripts(html){return [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>normalize(acorn.parse(m[1],{ecmaVersion:'latest'})));}
let failures=[];
for(const file of fs.readdirSync(root).filter(x=>x.endsWith('.html'))){
 const old=cp.execFileSync('git',['show',base+':'+file],{cwd:root,maxBuffer:10*1024*1024}).toString();
 const a=scripts(old),b=scripts(fs.readFileSync(path.join(root,file),'utf8'));
 if(JSON.stringify(a)!==JSON.stringify(b))failures.push(file);
}
fs.writeFileSync(path.join(__dirname,'js-preservation.json'),JSON.stringify({failures},null,2)+'\n');
if(failures.length)throw Error('Executable AST or numeric literal changed: '+failures.join(', '));
console.log('PASS all JavaScript ASTs: only Chinese display strings changed; numeric literals, identifiers, operations and structure preserved.');
