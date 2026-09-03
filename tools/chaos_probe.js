#!/usr/bin/env node
/* chaos_probe — Assignment 9: the adversarial QA agent's hands.
 * Nicholas Rouke · capstone game: uhta · ELVTR Multi-Agent AI for Game Development
 *
 * Drives the uhta vertical slice (blackboard/build/uhta-slice.html) in real
 * Chromium and actively tries to BREAK it — not play it. "Broken" is defined
 * up front as a violation of one of the invariants I1–I10 below; anything
 * else the agent does is just pressure applied to make a violation happen.
 *
 * THE STRATEGY (what "broken" means, per the rubric):
 *   I1  zero page errors / console errors, ever
 *   I2  the avatar's position stays inside the 48x48 map
 *   I3  no NPC ever holds NaN state; |v| never exceeds the zealot pin
 *   I4  population stays inside sane bounds (never 0, never runaway)
 *   I5  the stamina ledger never goes NaN and the budget never goes negative
 *   I6  a terminal, once fired, never changes (win cannot become loss)
 *   I7  the phase machine only holds known states; input after a terminal is inert-safe
 *   I8  camera zoom stays positive and finite under wheel abuse
 *   I9  the on-load self-test still fully passes AFTER an entire chaos run
 *   I10 the world is never stuck: real input during play advances the tick counter
 *   I11 a won world can be SEALED: with every heart aligned and no opposing zealot,
 *       flame-beside-the-flock + sleep-among-them must fire the win terminal within
 *       4 generations (regression: 2026-08-24 "it worked but I couldn't win" — the
 *       S-gate never saw enough expressed intent in a sparse terrain endgame, and
 *       burn churn moved the 0.8 denominator)
 *
 * BEHAVIORS (the chaos loop, seeded and reproducible):
 *   title_mash        clicks/keys hammered on the title screen
 *   boundary_march    held movement into all four map edges
 *   key_monkey        random keyboard input incl. keys the game never bound
 *   click_storm       rapid left/right clicks at random coords (roar has no menu?)
 *   wheel_abuse       extreme scroll-zoom in both directions
 *   flame_overdraft   spam flame far past the stamina budget
 *   sleep_spam        space held through generation after generation (to terminal)
 *   resize_jitter     viewport resized mid-play
 *   replay_hammer     rapid successive newGame() replays
 *   post_terminal_mash keeps playing after the run has ended
 *
 * Every finding is emitted as structured JSON with the fields the assignment
 * requires — location (mechanic/system), error_type, game_context — plus a
 * seeded repro. Usage:
 *   node tools/chaos_probe.js blackboard/build/uhta-slice.html [--seed 7] [--out out/a9/chaos-report.json]
 *   add --headed to watch the agent in a real browser window; --slow 150 throttles it to watchable speed
 *   add --arm idle for the do-nothing control arm (sleep-only, 40 generations)
 * Exit 0 = ran to completion (findings or not); exit 2 = probe itself failed.
 */
const path = require('path');
const fs = require('fs');

function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}}

const args = process.argv.slice(2);
const file = args[0];
const SEED = parseInt((args[args.indexOf('--seed')+1]||'7'), 10) || 7;
const OUT  = args.includes('--out') ? args[args.indexOf('--out')+1] : null;
const rng = mulberry32(SEED);
const pick = a => a[Math.floor(rng()*a.length)];

const findings = [];
const inputLog = [];   // rolling tail of raw inputs, for repro context
function logInput(s){ inputLog.push(s); if (inputLog.length > 40) inputLog.shift(); }

async function snapshot(page){
  return page.evaluate(() => {
    const s = { phase: (typeof phase!=='undefined')?phase:'UNREACHABLE' };
    try {
      if (typeof SIM !== 'undefined' && SIM) {
        s.sleep_no = SIM.sleep_no; s.tick_no = SIM.tick_no;
        s.pos = SIM.player_pos && SIM.player_pos.slice();
        s.pole = SIM.player_pole; s.pop = SIM.npcs.length;
        s.terminal = SIM.terminal ? SIM.terminal.slice() : null;
        s.stamina_spent = SIM.stamina_spent_this_wake;
        s.nan_npcs = SIM.npcs.filter(n => !Number.isFinite(n.v) || !Number.isFinite(n.pos[0]) || !Number.isFinite(n.pos[1])).length;
        const zv = (typeof RULES!=='undefined') ? RULES.scale.zealot_value : 12;
        s.over_pin = SIM.npcs.filter(n => Math.abs(n.v) > zv).length;
        s.map = (typeof MAP!=='undefined') ? MAP : 48;
      }
    } catch (e) { s.sim_error = String(e).slice(0,120); }
    return s;
  });
}

function finding(behavior, location, error_type, evidence, ctx, severity){
  findings.push({
    id: `F${String(findings.length+1).padStart(2,'0')}`,
    behavior, location, error_type, evidence, severity: severity||'medium',
    game_context: { seed: SEED, phase: ctx.phase, sleep_no: ctx.sleep_no,
      tick_no: ctx.tick_no, player_pos: ctx.pos, player_pole: ctx.pole,
      pop: ctx.pop, terminal: ctx.terminal,
      recent_inputs: inputLog.slice(-12) },
  });
}

async function checkInvariants(behavior, page, errors, prev){
  const s = await snapshot(page);
  if (s.sim_error) finding(behavior, 'core sim exposure', 'STATE_UNREADABLE', s.sim_error, s, 'high');
  if (errors.length) {
    finding(behavior, 'page runtime', 'PAGE_ERROR', errors.splice(0).join(' | '), s, 'high');     // I1
  }
  if (s.pos && (s.pos[0] < 0 || s.pos[1] < 0 || s.pos[0] > s.map-1 || s.pos[1] > s.map-1))
    finding(behavior, 'movement / walk verb', 'OUT_OF_BOUNDS', `player_pos ${JSON.stringify(s.pos)} outside 0..${s.map-1}`, s, 'high');  // I2
  if (s.nan_npcs) finding(behavior, 'contagion scale', 'NAN_STATE', `${s.nan_npcs} NPC(s) with non-finite v/pos`, s, 'high');            // I3
  if (s.over_pin) finding(behavior, 'contagion scale', 'VALUE_OVER_PIN', `${s.over_pin} NPC(s) with |v| beyond the zealot pin`, s, 'high');
  if (typeof s.pop === 'number' && (s.pop <= 0 || s.pop > 400))
    finding(behavior, 'population / births', 'POP_BOUNDS', `pop=${s.pop}`, s, 'high');                                                   // I4
  if (typeof s.stamina_spent === 'number' && !Number.isFinite(s.stamina_spent))
    finding(behavior, 'stamina economy', 'NAN_STAMINA', `stamina_spent_this_wake=${s.stamina_spent}`, s, 'high');                        // I5
  if (prev && prev.terminal && s.terminal && JSON.stringify(prev.terminal) !== JSON.stringify(s.terminal))
    finding(behavior, 'win/loss check', 'TERMINAL_MUTATED', `${JSON.stringify(prev.terminal)} -> ${JSON.stringify(s.terminal)}`, s, 'high'); // I6
  const known = ['title','play','end','ended','cave','ERR','UNREACHABLE'];
  if (s.phase && !known.includes(s.phase))
    finding(behavior, 'phase machine', 'UNKNOWN_PHASE', `phase='${s.phase}'`, s, 'medium');                                              // I7
  return s;
}

const ARM = args.includes('--arm') ? args[args.indexOf('--arm')+1] : 'all';
const HEADED = args.includes('--headed');                                   // watch the agent work
const SLOW = args.includes('--slow') ? parseInt(args[args.indexOf('--slow')+1],10)||120 : 0;   // ms per action

async function main(){
  const { chromium } = require('playwright');
  const browser = await chromium.launch({ headless: !HEADED, slowMo: SLOW });
  const page = await browser.newPage({ viewport: { width: 1000, height: 800 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + String(e).slice(0,200)));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0,200)); });

  await page.goto('file://' + path.resolve(file));
  await page.waitForTimeout(2200);
  let s = await checkInvariants('load', page, errors, null);

  if (ARM === 'idle'){
    // Pure control arm: start a run, touch nothing but Sleep, 40 generations.
    // The reference harness's do-nothing baseline LOSES at sleep 24; if the slice
    // never ends, the idle player has no ending and criterion 6 cannot be asked.
    await page.mouse.click(500,400); logInput('start (idle arm)'); await page.waitForTimeout(700);
    let slept=0;
    for (let g=0; g<40; g++){
      const b=(await snapshot(page)).sleep_no;
      await page.keyboard.press('Space').catch(()=>{});
      let w=0; while(w<4000){ await page.waitForTimeout(150); w+=150;
        const n=await snapshot(page); if(n.terminal||(typeof n.sleep_no==='number'&&n.sleep_no>b)) break;
        if(w===2100) await page.keyboard.press('Space').catch(()=>{}); }
      const a=await snapshot(page); if(typeof a.sleep_no==='number'&&a.sleep_no>b) slept++;
      if(a.terminal) break;
      if(g%8===0) s=await checkInvariants('idle_march', page, errors, s);
    }
    s = await checkInvariants('idle_march', page, errors, s);
    if (!s.terminal && slept >= 35)
      finding('idle_march', 'win/loss check (apathy loss)', 'NO_ENDING_FOR_IDLE_RUN',
        `${slept} idle generations, no terminal; harness do-nothing baseline loses at sleep 24. Suspect: the slice-only ambient peer-contagion beat keeps enough of the world aligned that grey+burned never reaches 0.8`, s, 'medium');
    await emit(page, !!s.terminal, browser, ['idle_march']);
    return;
  }

  // -------- title_mash --------
  for (let i=0;i<25;i++){
    const x=100+rng()*800, y=80+rng()*640;
    if (rng()<0.5){ await page.mouse.click(x,y,{button:pick(['left','right'])}); logInput(`click ${x|0},${y|0}`);}
    else { const k=pick(['Escape','Enter','Space','KeyQ','F1','Tab','KeyW']); await page.keyboard.press(k).catch(()=>{}); logInput(`key ${k}`);}
    if (i%8===0) await page.waitForTimeout(60);
  }
  await page.waitForTimeout(500);
  s = await checkInvariants('title_mash', page, errors, s);

  // make sure we are in play (title click starts the run)
  if (s.phase === 'title'){ await page.mouse.click(500,400); logInput('click 500,400 (start)'); await page.waitForTimeout(700); s = await snapshot(page); }
  // builds with the CAVE opening: walk out of the right-hand mouth before the world exists
  for (let i=0;i<140;i++){
    const inCave = await page.evaluate(() => { try { return CAVE.active === true; } catch(e){ return false; } });
    if (!inCave) break;
    await page.keyboard.press('KeyD').catch(()=>{});
  }
  logInput('cave exit (if present)');
  s = await checkInvariants('cave_exit', page, errors, s);

  // -------- boundary_march: hold movement into each edge --------
  for (const key of ['KeyA','KeyW','KeyD','KeyS']){
    for (let i=0;i<40;i++){ await page.keyboard.press(key).catch(()=>{}); }
    logInput(`held ${key} x40`);
    await page.waitForTimeout(250);
    s = await checkInvariants('boundary_march', page, errors, s);
  }

  // -------- key_monkey --------
  const keys=['KeyW','KeyA','KeyS','KeyD','Space','Enter','Escape','Tab','KeyE','KeyR','KeyF','KeyB','Digit1','F5','ArrowUp','ArrowLeft','Backquote','Minus','Equal','BracketLeft'];
  for (let i=0;i<120;i++){ const k=pick(keys); await page.keyboard.press(k).catch(()=>{}); if(i%20===0){logInput(`monkey ${k}…`); await page.waitForTimeout(40);} }
  s = await checkInvariants('key_monkey', page, errors, s);

  // -------- click_storm --------
  for (let i=0;i<80;i++){ const x=rng()*1000,y=rng()*800; await page.mouse.click(x,y,{button:pick(['left','right','left'])}).catch(()=>{}); }
  logInput('click_storm x80');
  s = await checkInvariants('click_storm', page, errors, s);

  // -------- wheel_abuse --------
  for (let i=0;i<30;i++){ await page.mouse.wheel(0, pick([-2400, 2400, -12000, 12000])); }
  logInput('wheel_abuse x30');
  await page.waitForTimeout(300);
  const zoom = await page.evaluate(() => { try { return (typeof scene!=='undefined' && scene) ? scene.zoom : null; } catch(e){ return 'unreadable'; } });
  if (typeof zoom === 'number' && (!(zoom > 0) || !Number.isFinite(zoom) || zoom < 0.4 || zoom > 3))
    finding('wheel_abuse', 'camera / scroll zoom', 'ZOOM_BOUNDS', `camera zoom=${zoom}`, await snapshot(page), 'medium');   // I8
  s = await checkInvariants('wheel_abuse', page, errors, s);

  // -------- flame_overdraft: spam flame far beyond budget --------
  const before = await snapshot(page);
  for (let i=0;i<60;i++){ await page.mouse.click(500,400,{button:'left'}).catch(()=>{}); }
  logInput('flame_overdraft x60 (left-click on avatar tile)');
  s = await checkInvariants('flame_overdraft', page, errors, before);
  if (typeof s.stamina_spent === 'number' && before && typeof before.stamina_spent === 'number'){
    const budget = await page.evaluate(() => { try { return SIM.budget ? SIM.budget() : null; } catch(e){ return null; } });
    if (typeof budget === 'number' && s.stamina_spent > budget + 6)
      finding('flame_overdraft', 'stamina economy', 'BUDGET_OVERDRAFT', `spent ${s.stamina_spent.toFixed(1)} vs budget ${budget.toFixed(1)}`, s, 'medium');
  }

  // -------- stuck check (I10): does input still advance the world? --------
  const t0 = (await snapshot(page)).tick_no;
  for (let i=0;i<6;i++){ await page.keyboard.press('KeyW').catch(()=>{}); await page.waitForTimeout(60); }
  const t1 = (await snapshot(page)).tick_no;
  if (s.phase === 'play' && typeof t0 === 'number' && t0 === t1){
    // distinguish a real freeze from a silently-exhausted stamina budget
    const diag = await page.evaluate(() => { try { return {
      remaining: (typeof scene!=='undefined' && scene && scene.remaining) ? scene.remaining() : null,
      tip: (document.getElementById('tip')||{}).innerText || '' }; } catch(e){ return {remaining:'unreadable'}; } });
    const beforeSleepNo = (await snapshot(page)).sleep_no;
    await page.keyboard.press('Space').catch(()=>{});
    await page.waitForTimeout(1200);
    const afterSleepNo = (await snapshot(page)).sleep_no;
    if (afterSleepNo === beforeSleepNo)
      finding('stuck_check', 'core loop', 'WORLD_STUCK', `tick_no frozen at ${t0}; movement AND sleep both dead`, await snapshot(page), 'high');
    else if (typeof diag.remaining === 'number' && diag.remaining < 0.5 && !/sleep|stamina|spent|rest/i.test(diag.tip))
      finding('stuck_check', 'stamina economy / input feedback', 'ZERO_STAMINA_NO_FEEDBACK',
        `wake budget exhausted (remaining=${diag.remaining.toFixed(2)}): every verb silently no-ops and nothing on screen says why or points at Sleep; tip='${(diag.tip||'').slice(0,70)}'`, await snapshot(page), 'medium');
  }

  // -------- roar_offmap: right-click into the void at every corner --------
  for (const [x,y] of [[2,2],[998,2],[2,798],[998,798],[500,2],[2,400]]){
    await page.mouse.click(x,y,{button:'right'}).catch(()=>{});
  }
  logInput('roar_offmap x6 (corners)');
  s = await checkInvariants('roar_offmap', page, errors, s);

  // -------- verb_hammer: beacon / raze / wait / art-pass toggles mid-play --------
  for (let i=0;i<30;i++){ const k=pick(['KeyE','KeyR','KeyQ','Digit1','Digit2','Digit3','Digit4','Digit5','Digit0']); await page.keyboard.press(k).catch(()=>{}); }
  logInput('verb_hammer x30 (e/r/q/art toggles)');
  s = await checkInvariants('verb_hammer', page, errors, s);

  // -------- stamina_exhaust: burn the whole wake budget, then poke every verb --------
  // (from code reading: moveStep/tryAct return silently when cost > remaining;
  //  this arm proves what the player experiences at that moment)
  {
    const st = await page.evaluate(async () => {
      try {
        let guard = 0;
        while (scene.remaining() >= 2.5 && guard++ < 40) {           // FLAME_C = 2.5
          SIM.act('flame', SIM.player_pos, SIM.player_pole, 2.5);    // same call the click path makes
        }
        return { remaining: scene.remaining(), guard };
      } catch(e){ return { err: String(e).slice(0,150) }; }
    });
    logInput(`stamina_exhaust: drained to ${st.remaining!==undefined?st.remaining.toFixed(2):st.err}`);
    if (st.err) finding('stamina_exhaust', 'stamina economy', 'STATE_UNREADABLE', st.err, await snapshot(page), 'medium');
    else {
      const tick0 = (await snapshot(page)).tick_no;
      const tip0 = await page.evaluate(() => (document.getElementById('tip')||{}).innerText || '');
      for (const k of ['KeyW','KeyA','KeyE','KeyR']) await page.keyboard.press(k).catch(()=>{});   // costed verbs only — Wait (q) is free by design
      await page.mouse.click(500,400).catch(()=>{});
      await page.mouse.click(500,400,{button:'right'}).catch(()=>{});
      logInput('poked all 7 verbs at zero budget');
      await page.waitForTimeout(700);
      const tick1 = (await snapshot(page)).tick_no;
      const tip1 = await page.evaluate(() => (document.getElementById('tip')||{}).innerText || '');
      const fed = /sleep|stamina|tired|spent|rest|night/i.test(tip1) && tip1 !== tip0;
      if (tick1 === tick0 && !fed)
        finding('stamina_exhaust', 'stamina economy / input feedback', 'ZERO_STAMINA_NO_FEEDBACK',
          `wake budget exhausted (remaining=${st.remaining.toFixed(2)}): walk, beacon, raze, flame and roar all silently no-op (tick_no held at ${tick0}) and the tip line never changes — nothing tells the player Sleep is the only remaining verb. moveStep()/tryAct() bail with a bare return`, await snapshot(page), 'medium');
      // recover for the next behaviors
      await page.keyboard.press('Space').catch(()=>{});
      await page.waitForTimeout(1200);
    }
  }
  s = await checkInvariants('stamina_exhaust', page, errors, s);

  // -------- sleep_march: REAL generations — press space, wait out the night transition --------
  // The harness's do-nothing baseline loses at sleep 24. If the slice cannot reach a
  // terminal in 40 idle generations, the idle player has no ending — that is a finding.
  // 2026-08-24: a fresh run opens in THE MEETING's tutorial map, and skipping it now
  // requires the are-you-sure dialog's PHYSICAL mouse click — exercise that exact path:
  // space raises the dialog, a key must NOT confirm it, the mouse click must.
  {
    const inTut = await page.evaluate(() => { try { return typeof TUTOR!=='undefined' && TUTOR.active; } catch(e){ return false; } });
    if (inTut){
      // earlier chaos arms may have left the dialog OPEN — normalize to closed first
      await page.evaluate(() => { try { if (typeof tutSkipAsk==='function') tutSkipAsk(false); } catch(e){} });
      await page.waitForTimeout(150);
      await page.keyboard.press('Space').catch(()=>{});
      await page.waitForTimeout(350);
      const up1 = await page.evaluate(() => typeof TUT_SKIP_UP!=='undefined' && TUT_SKIP_UP);
      await page.keyboard.press('Space').catch(()=>{});   // a key STAYS — must not confirm
      await page.waitForTimeout(250);
      const stillTut = await page.evaluate(() => TUTOR.active===true);
      await page.keyboard.press('Space').catch(()=>{});   // re-raise, then confirm by mouse
      await page.waitForTimeout(300);
      const clicked = await page.evaluate(() => { const b=document.getElementById('tskgo'); if(b&&TUT_SKIP_UP){b.click();return true;} return false; });
      logInput(`tutorial skip dialog: raised=${up1} key-stayed=${stillTut} mouse-confirmed=${clicked}`);
      if (!up1 || !stillTut || !clicked)
        finding('sleep_march', 'tutorial skip confirm', 'SKIP_CONFIRM_BROKEN',
          `space mid-lesson must raise are-you-sure (raised=${up1}), a key must stay (stayed=${stillTut}), only a mouse click may confirm (clicked=${clicked})`, await snapshot(page), 'medium');
      await page.waitForTimeout(2400);   // transition into the real world
      // whatever happened above, the march below must test the REAL world's sleep
      await page.evaluate(() => { try { if (typeof TUTOR!=='undefined' && TUTOR.active) tutorFinish(true); } catch(e){} });
      await page.waitForTimeout(2400);
    }
  }
  let slept = 0; let stuckSleeps = 0;
  for (let g=0; g<40; g++){
    const beforeSleep = (await snapshot(page)).sleep_no;
    await page.keyboard.press('Space').catch(()=>{});
    let waited = 0;
    while (waited < 4000){
      await page.waitForTimeout(150); waited += 150;
      const now = await snapshot(page);
      if (now.terminal || (typeof now.sleep_no==='number' && now.sleep_no > beforeSleep)) break;
      // a sonder telling card or the encounter legitimately holds input — resolve, don't count
      const held = await page.evaluate(() => { try {
        if (document.querySelector('[role=dialog]')) return 'card';
        if (typeof MG !== 'undefined' && MG.active) return 'mg';
        return null; } catch(e){ return null; } });
      if (held === 'card'){ await page.keyboard.press('Enter').catch(()=>{}); waited = Math.min(waited, 1800); }
      else if (held === 'mg'){ for (let c=0;c<6;c++) await page.mouse.click(500,400).catch(()=>{}); waited = Math.min(waited, 1800); }
      // transition may still be running; keep waiting, re-press once at 2s
      if (waited === 2100) await page.keyboard.press('Space').catch(()=>{});
    }
    const after = await snapshot(page);
    if (typeof after.sleep_no==='number' && after.sleep_no === beforeSleep) stuckSleeps++;
    else slept++;
    if (after.terminal) break;
    if (g % 8 === 0) s = await checkInvariants('sleep_march', page, errors, s);
  }
  logInput(`sleep_march: ${slept} generations`);
  s = await checkInvariants('sleep_march', page, errors, s);
  if (stuckSleeps >= 3)
    finding('sleep_march', 'sleep / night transition', 'SLEEP_UNRESPONSIVE', `${stuckSleeps} space presses failed to advance the generation within 4s`, s, 'medium');
  const reachedTerminal = !!s.terminal;
  if (!reachedTerminal && slept >= 35)
    finding('sleep_march', 'win/loss check (apathy loss)', 'NO_ENDING_FOR_IDLE_RUN',
      `${slept} idle generations, no terminal. The reference harness's do-nothing baseline loses at sleep 24; the slice's ambient peer-contagion appears to keep the world aligned enough that the grey never claims 0.8 — an idle player never receives an ending`, s, 'medium');

  // -------- post_terminal_mash --------
  if (reachedTerminal){
    const termBefore = s.terminal;
    for (let i=0;i<60;i++){ rng()<0.5 ? await page.keyboard.press(pick(keys)).catch(()=>{}) : await page.mouse.click(rng()*1000,rng()*800).catch(()=>{}); }
    logInput('post_terminal_mash x60');
    s = await checkInvariants('post_terminal_mash', page, errors, s);
    const after = await snapshot(page);
    if (after.terminal && JSON.stringify(after.terminal) !== JSON.stringify(termBefore))
      finding('post_terminal_mash', 'win/loss check', 'TERMINAL_MUTATED', `${JSON.stringify(termBefore)} -> ${JSON.stringify(after.terminal)}`, after, 'high');
  }

  // -------- resize_jitter --------
  for (const vp of [{width:340,height:280},{width:1900,height:400},{width:800,height:1200},{width:1000,height:800}]){
    await page.setViewportSize(vp); await page.waitForTimeout(200);
  }
  logInput('resize_jitter x4');
  s = await checkInvariants('resize_jitter', page, errors, s);

  // -------- replay_hammer --------
  for (let i=0;i<5;i++){
    await page.evaluate(() => { try { newGame(Math.random()<0.5?1:-1); } catch(e){ window.__replayErr = String(e); } });
    await page.waitForTimeout(150);
  }
  logInput('replay_hammer x5 (newGame)');
  const replayErr = await page.evaluate(() => window.__replayErr || null);
  // teaching must fire again on a fresh run (scene.tut is reset by newGame — verify it)
  await page.keyboard.press('KeyW').catch(()=>{});
  await page.waitForTimeout(1400);   // teaching line lands on the next tip refresh
  const tip = await page.evaluate(() => { try { return (document.getElementById('tip')||{}).innerText || ''; } catch(e){ return ''; } });
  const taught = await page.evaluate(() => { try { return TEACHING_TEXT && tip !== undefined ? null : null; } catch(e){ return null; } });
  const walkLine = await page.evaluate(() => { try { return TEACHING_TEXT.walk.slice(0, 18); } catch(e){ return null; } });
  if (walkLine && !tip.includes(walkLine.slice(0,12))){
    // 2026-08-24: THE MEETING (skippable tutorial) supersedes the sleep-0 teaching lines on a
    // fresh run — its narration on the tip surface IS the teaching. Only flag silence when
    // neither surface spoke.
    const meeting = await page.evaluate(() => { try { return typeof TUTOR!=='undefined' && TUTOR.active; } catch(e){ return false; } });
    if (!meeting)
      finding('replay_hammer', 'teaching narration (G12 surface)', 'TEACHING_SILENT_ON_REPLAY',
        `first walk of a fresh run did not surface the walk teaching line and no tutorial was narrating; tip='${tip.slice(0,80)}'`, await snapshot(page), 'low');
  }
  if (replayErr) finding('replay_hammer', 'newGame / reset path', 'REPLAY_ERROR', replayErr.slice(0,200), await snapshot(page), 'high');
  s = await checkInvariants('replay_hammer', page, errors, s);

  // -------- win_seal (I11): a won world must be SEALABLE --------
  // replay_hammer left us in a fresh run. Force the won-but-unsealed state (all aligned,
  // no opposing zealot), then do exactly what the game telegraphs: flame beside the flock
  // and sleep among them. If the terminal doesn't fire, the win is unreachable — the
  // 2026-08-24 class (S-gate starvation / burn-churn denominator), found by a human first.
  {
    // 2026-08-24: a fresh run opens in THE MEETING's tutorial world (SIM is swapped).
    // Seal the REAL world: finish the tutorial first and wait out its transition.
    await page.evaluate(() => { try { if (typeof TUTOR!=='undefined' && TUTOR.active) tutorFinish(true); } catch(e){} });
    await page.waitForTimeout(2200);
    await page.evaluate(() => { try {
      const p1 = SIM.player_pole;
      for (const x of SIM.npcs){ if (x.zealot){ if (x.I*p1<0) x.v = 8*p1; continue; } x.burn=false; x.v=8*p1; x.ever_nonzero=true; }
      for (const t of SIM.tribes) t.pole = p1;
    } catch(e){ window.__sealErr = String(e); } });
    let sealed = false, holdTrace = [], wfTrace = [];
    for (let round=0; round<4 && !sealed; round++){
      await page.evaluate(() => { try {
        const c = SIM.tribes[0].center; SIM.player_pos = [c[0], c[1]];
        SIM.act('flame', null, SIM.player_pole, 2.5);
      } catch(e){ window.__sealErr = String(e); } });
      const before = (await snapshot(page)).sleep_no;
      await page.keyboard.press('Space').catch(()=>{});
      let waited = 0;
      while (waited < 4500){
        await page.waitForTimeout(150); waited += 150;
        const now = await snapshot(page);
        if (now.terminal || (typeof now.sleep_no==='number' && now.sleep_no > before)) break;
        if (await page.evaluate(() => !!document.querySelector('[role=dialog]')).catch(()=>false))
          await page.keyboard.press('Enter').catch(()=>{});
      }
      const st = await page.evaluate(() => { try { return { terminal: SIM.terminal && SIM.terminal.slice(),
        hold: SIM.win_hold, wf: +( (SIM.win_frac?SIM.win_frac():SIM.dominance()) ).toFixed(2) }; } catch(e){ return {err:String(e).slice(0,120)}; } });
      holdTrace.push(st.hold); wfTrace.push(st.wf);
      if (st.terminal && st.terminal[0] === 'win') sealed = true;
      if (st.terminal && st.terminal[0] !== 'win'){
        finding('win_seal', 'win/loss check', 'SEAL_BECAME_LOSS',
          `forced-won world terminated ${JSON.stringify(st.terminal)} while sealing`, await snapshot(page), 'high');
        break;
      }
    }
    logInput(`win_seal: sealed=${sealed} hold=[${holdTrace}] wf=[${wfTrace}]`);
    if (!sealed && !findings.some(f=>f.error_type==='SEAL_BECAME_LOSS'))
      finding('win_seal', 'win/loss check (S-gate / win denominator)', 'WIN_UNSEALABLE',
        `every heart aligned, no opposing zealot, flame+sleep among the flock x4 generations — win terminal never fired (win_hold trace [${holdTrace.join(',')}], win_frac trace [${wfTrace.join(',')}]). The 0.8 hold either never accumulates (intent S-gate starved in a sparse endgame) or the denominator churns (burnout). Human-found 2026-08-24; this arm keeps it found.`,
        await snapshot(page), 'high');
    s = await checkInvariants('win_seal', page, errors, s);
  }

  await emit(page, reachedTerminal, browser, null);
}

async function emit(page, reachedTerminal, browser, behaviors){
  const post = await page.evaluate(() => { try { selfTest(); const el=document.getElementById('tests'); return el?el.textContent:'(no panel)'; } catch(e){ return 'THREW: '+String(e).slice(0,180); } });
  const fails = (post.match(/FAIL/g)||[]).length;
  if (post.startsWith('THREW') || fails > 0)
    finding('post_chaos_selftest', 'self-test harness', 'SELFTEST_REGRESSION', post.slice(0,300), await snapshot(page), 'high');
  await browser.close();

  const report = {
    game: 'uhta — vertical slice (blackboard/build/uhta-slice.html)',
    author: 'Nicholas Rouke',
    agent: 'chaos_probe v1 (Assignment 9)',
    seed: SEED,
    when: new Date().toISOString(),
    invariants: ['I1 no page errors','I2 avatar in bounds','I3 finite NPC state within pin','I4 population bounds','I5 stamina ledger sane','I6 terminal immutable','I7 known phases only / inert after terminal','I8 zoom bounds','I9 self-test green after chaos','I10 world never stuck','I11 a won world can be sealed'],
    arm: ARM,
    behaviors_run: behaviors || ['title_mash','boundary_march','key_monkey','click_storm','wheel_abuse','roar_offmap','verb_hammer','flame_overdraft','stuck_check','stamina_exhaust','sleep_march','post_terminal_mash','resize_jitter','replay_hammer','win_seal','post_chaos_selftest'],
    reached_terminal: reachedTerminal,
    selftest_after_chaos_fails: (findings.some(f=>f.error_type==='SELFTEST_REGRESSION')) ? 'REGRESSED' : 'all green',
    findings_count: findings.length,
    findings,
  };
  const json = JSON.stringify(report, null, 1);
  if (OUT){ fs.mkdirSync(path.dirname(OUT), {recursive:true}); fs.writeFileSync(OUT, json); }
  console.log(json);
}

main().catch(e => { console.error('PROBE FAILED:', e); process.exit(2); });
