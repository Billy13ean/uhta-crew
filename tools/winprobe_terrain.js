#!/usr/bin/env node
/* winprobe_terrain — the Playtester's terrain-winnability harness (JS-side).
 * Nicholas Rouke · capstone game: uhta · ELVTR Multi-Agent AI for Game Development
 *
 * Origin: 2026-08-24, Director bug "it worked but I couldn't win." The wild shipped
 * slice-first (python harness twin = schema 3.11, pending), so the reference sim for
 * terrain IS the slice's embedded World. This tool extracts it headlessly and plays a
 * SKILLED policy per seed — measured flames (no overdose spam), beacons at pockets,
 * found-site lighting, fear-hunts, and the telegraphed endgame: when the world leans
 * your way, walk home, flame beside your people, and sleep among them (the S-gate).
 *
 * THE GATE (what "broken" means):
 *   - wins  < --min-wins (default 6 of 8 seeds)      -> exit 1  (win too rare)
 *   - any PLATEAU: run ends NONE with max_wf >= 0.75 -> exit 1  (the 2026-08-24 class:
 *     the world was effectively won and the terminal never fired)
 *
 * Falsification metrics emitted (Red-Teamer attack rows may name these):
 *   wins, losses, none, plateaus, median_win_sleep, median_max_wf, median_burn_peak
 *
 * Usage:
 *   node tools/winprobe_terrain.js blackboard/build/uhta-slice.html
 *     [--seeds 8] [--cap 70] [--min-wins 6] [--out out/terrain/winprobe.json]
 */
const fs=require('fs'),path=require('path');
const args=process.argv.slice(2);
const FILE=args[0];
const SEEDS=+(args.includes('--seeds')?args[args.indexOf('--seeds')+1]:8);
const CAP=+(args.includes('--cap')?args[args.indexOf('--cap')+1]:70);
const MINW=+(args.includes('--min-wins')?args[args.indexOf('--min-wins')+1]:6);
const OUT=args.includes('--out')?args[args.indexOf('--out')+1]:null;

const src=fs.readFileSync(FILE,'utf8');
const blocks=[...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const body=blocks.filter(b=>b.includes('function selfTest()')).sort((a,b)=>b.length-a.length)[0];
if(!body){console.error('no authored script block in '+FILE);process.exit(2);}
const el={textContent:'',className:'',style:{}};
global.document={getElementById:()=>el};global.window=global;
const _log=console.log;console.log=()=>{};
const g=new Function(body+';return {W:World,setT:(v)=>{TERRAIN_RT=v;}};')();
console.log=_log;
const cheb=(a,b)=>Math.max(Math.abs(a[0]-b[0]),Math.abs(a[1]-b[1]));
const WALK_C=0.5,FLAME_C=2.5,BEAC_C=3;

function play(seed){
  g.setT({enabled:true});
  const w=new g.W(seed,[-1,1]);w.player_pole=1;
  const pockets=(w._pockets&&w._pockets.length)?w._pockets.map(p=>p.c):[[12,24],[36,24],[24,24]];
  let tour=0,burnPeak=0;
  while(w.sleep_no<CAP&&!w.terminal){
    const br={b:w.budget()};
    let target=null,sealing=false;
    const fearT=w.tribes.filter(t=>!t.zealotless&&w.npcs.some(x=>x.tribe===t.idx&&x.zealot&&x.I<0));
    const wfNow=w.win_frac?w.win_frac():w.dominance();
    if(!fearT.length&&wfNow>=0.78){ // the telegraphed seal: sleep among the biggest flock
      sealing=true;let bt=null,bn=-1;
      for(const t of w.tribes){const n=w.npcs.filter(x=>!x.burn&&x.I*w.player_pole>=1&&cheb(x.pos,t.center)<=4).length;
        if(n>bn){bn=n;bt=t;}}
      target=bt?bt.center.slice():w.player_pos.slice();
    } else if(fearT.length){let bt=null,bd=1e9;for(const t of fearT){const d=cheb(w.player_pos,t.center);if(d<bd){bd=d;bt=t;}}target=bt.center.slice();}
    else{let bt=null,bn=0;
      for(const pc of pockets){const n=w.npcs.filter(x=>!x.burn&&x.I*w.player_pole<1&&cheb(x.pos,pc)<=6).length;
        if(n>bn){bn=n;bt=pc;}}
      if(bt)target=bt.slice(); else{tour=(tour+1)%pockets.length;target=pockets[tour].slice();}}
    while((w.player_pos[0]!==target[0]||w.player_pos[1]!==target[1])&&br.b>=WALK_C+6){
      const np=[w.player_pos[0]+Math.sign(target[0]-w.player_pos[0]),w.player_pos[1]+Math.sign(target[1]-w.player_pos[1])];
      w._layRoad(w.player_pos,np,w.player_pole);w.player_pos=np;br.b-=WALK_C;w.stamina_spent_this_wake+=WALK_C;}
    for(let i=0;i<w.sites.length;i++){const s=w.sites[i];
      if(!s.lit&&cheb(w.player_pos,s.pos)<=2&&br.b>=BEAC_C){if(w.light_site(i,1)){br.b-=BEAC_C;w.stamina_spent_this_wake+=BEAC_C;}}}
    if(w.placed_beacons<w.beacon_cap&&br.b>=BEAC_C&&!w.beacons.some(([bp])=>cheb(bp,w.player_pos)<=5)){
      w.beacons.push([w.player_pos.slice(),1]);w.placed_beacons++;br.b-=BEAC_C;w.stamina_spent_this_wake+=BEAC_C;}
    const nearNon=w.npcs.filter(x=>!x.burn&&x.I*w.player_pole<1&&cheb(x.pos,w.player_pos)<=w.flame_r).length;
    let casts=sealing?1:Math.min(2,Math.ceil(nearNon/5));
    while(casts-->0&&br.b>=FLAME_C){w.act('flame',null,1,FLAME_C);br.b-=FLAME_C;}
    w.do_sleep();
    burnPeak=Math.max(burnPeak,w.npcs.filter(x=>x.burn).length);
  }
  return {seed,terminal:w.terminal?w.terminal[0]:'NONE',sleep:w.terminal?w.terminal[1]:null,
    max_wf:+(w.max_wf||0).toFixed(2),final_wf:+(w.win_frac?w.win_frac():w.dominance()).toFixed(2),
    pop:w.pop(),burn_peak:burnPeak,roads:w.roads.size};
}
const med=a=>{if(!a.length)return null;const s=a.slice().sort((x,y)=>x-y);return s[Math.floor(s.length/2)];};
const rows=[];for(let s=0;s<SEEDS;s++)rows.push(play(s));
const wins=rows.filter(r=>r.terminal==='win');
const plateaus=rows.filter(r=>r.terminal==='NONE'&&r.max_wf>=0.75);
const report={
  game:'uhta — vertical slice (terrain: THE WILD)', author:'Nicholas Rouke',
  agent:'winprobe_terrain v1 (Playtester terrain harness)',
  build:path.basename(FILE), seeds:SEEDS, cap_sleeps:CAP,
  gate:{min_wins:MINW, plateaus_allowed:0},
  wins:wins.length, losses:rows.filter(r=>r.terminal==='loss').length,
  none:rows.filter(r=>r.terminal==='NONE').length, plateaus:plateaus.length,
  median_win_sleep:med(wins.map(r=>r.sleep)), median_max_wf:med(rows.map(r=>r.max_wf)),
  median_burn_peak:med(rows.map(r=>r.burn_peak)),
  rows,
  verdict:(wins.length>=MINW&&plateaus.length===0)?'PASS':'FAIL',
};
const json=JSON.stringify(report,null,1);
if(OUT){fs.mkdirSync(path.dirname(OUT),{recursive:true});fs.writeFileSync(OUT,json);}
console.log(json);
process.exit(report.verdict==='PASS'?0:1);
