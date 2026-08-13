// Headless verification: extract the authored <script> and run its on-load
// self-test with a minimal DOM stub. Phaser is absent, which the build guards for.
const fs=require('fs');
const src=fs.readFileSync(process.argv[2],'utf8');
const blocks=[...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const body=blocks.filter(b=>b.includes('function selfTest()')).sort((a,b)=>b.length-a.length)[0];
if(!body){console.error('no authored script block');process.exit(2);}
let panel='';
const el={set textContent(v){panel=v;},get textContent(){return panel;},set className(v){},style:{}};
global.document={getElementById:()=>el};
global.window=global;
let logged='';
const realLog=console.log; console.log=(...a)=>{logged+=a.join(' ')+'\n';};
try{ new Function(body)(); }catch(e){ console.log=realLog; console.error('THREW:',e.message); process.exit(3); }
console.log=realLog;
const out=panel||logged;
const pass=(out.match(/PASS/g)||[]).length, fail=(out.match(/FAIL/g)||[]).length;
console.log(out.trim());
console.log(`\n==> ${pass} PASS / ${fail} FAIL`);
process.exit(fail===0&&pass>0?0:1);
