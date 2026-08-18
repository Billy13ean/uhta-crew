#!/usr/bin/env node
/* mg_probe — the mini-game pipeline's headless play-probe (the Playtester's
 * seat, applied to the overlay).
 *
 * Added after the third Director playtest. The patch contract verified that
 * a patch PARSES and ASSERTS; it never verified that it PLAYS. Two shipped
 * candidates were statically green and behaviorally broken (a permanent
 * `transitioning` freeze; a getter-only `NPC.I` assignment that threw every
 * frame after resolution). This probe drives the candidate build in real
 * Chromium and rejects what a static check cannot see:
 *
 *   P1 no page errors, at load or during 25s of scripted play
 *   P2 the encounter is NOT active at the title screen (self-test leakage)
 *   P3 WASD moves the avatar during the encounter
 *   P4 the Instructor's first-use line reaches the tip display
 *   P5 clicking produces a response (flame rises on click)
 *   P6 the encounter survives >= 8s of no input (human tuning floor)
 *   P7 after resolution, WASD still moves and no errors follow (control
 *      returns — the v2/v3 freeze class)
 *
 * Usage: node tools/mg_probe.js <patched.html> <first_use_line...>
 * Prints one JSON object to stdout; exit 0 iff every check passed.
 * Requires the `playwright` package; the pipeline treats its absence as
 * SKIPPED (recorded, never silent).
 */
const path = require('path');

async function main() {
  const file = process.argv[2];
  const line = process.argv.slice(3).join(' ');
  const { chromium } = require('playwright');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 800 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e).slice(0, 200)));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 200)); });

  const res = { checks: {}, detail: {} };
  const url = 'file://' + path.resolve(file) + '#mg';
  await page.goto(url);
  await page.waitForTimeout(2500);

  const title = await page.evaluate(() => {
    const o = {};
    try { o.phase = phase; } catch (e) { o.phase = 'ERR'; }
    try { o.active = MG.active; } catch (e) { o.active = 'ERR'; }
    return o;
  });
  res.checks.P2_not_active_at_title = title.active === false;
  res.detail.title = title;

  await page.mouse.click(300, 400);           // title -> THE CAVE
  await page.waitForTimeout(800);
  // P0: the cave opening — the section before the main game. The probe
  // walks out through the right-hand (Hope) mouth; the game must reach
  // phase 'play' with the pole chosen by the exit.
  const caveSeen = await page.evaluate(() => {
    try { return { cave: CAVE.active, tip: (document.querySelector('#tip')?.innerText || '').slice(0, 60) }; }
    catch (e) { return { cave: 'absent' }; }
  });
  res.detail.cave = caveSeen;
  await page.keyboard.down('d');
  const caveOut = await page.evaluate(async () => {
    const t0 = Date.now();
    try {
      while (Date.now() - t0 < 20000) {
        if (typeof phase !== 'undefined' && phase === 'play') return { play_ms: Date.now() - t0 };
        await new Promise(r => setTimeout(r, 200));
      }
      return { timeout: true };
    } catch (e) { return { err: e.message }; }
  });
  await page.keyboard.up('d');
  res.checks.P0_cave_opens_and_exits_to_play =
    caveSeen.cave === true && !!caveOut.play_ms;
  res.detail.caveOut = caveOut;
  await page.waitForTimeout(800);

  // P2b: with #mg the encounter must ACTUALLY ACTIVATE within a few seconds
  // of play starting — a patch whose arming self-cancels passes every other
  // check vacuously (this happened: arm-then-init, where init reset active).
  // Polled, not snapshot: the discovery pass adds an intentional attention-
  // cue delay before activation.
  const act = await page.evaluate(async () => {
    const t0 = Date.now();
    try {
      while (Date.now() - t0 < 6000) {
        if (MG.active) return { active: true, after_ms: Date.now() - t0, phase: phase };
        await new Promise(r => setTimeout(r, 150));
      }
      return { active: MG.active, after_ms: 6000, phase: phase };
    } catch (e) { return { err: e.message }; }
  });
  res.checks.P2b_activates_after_start = act.active === true;
  res.detail.activation = act;

  // P3 (inverted after the anchor fix): during the encounter the avatar is
  // HELD at the anchor — "the circle moves around" was a playtest defect.
  // Free movement after resolution is P7's job (and the cave walk already
  // proved WASD input works).
  const posBefore = await page.evaluate(() => { try { return SIM.player_pos.slice(); } catch (e) { return null; } });
  for (let i = 0; i < 3; i++) { await page.keyboard.press('w'); await page.waitForTimeout(100); }
  const posAfter = await page.evaluate(() => { try { return SIM.player_pos.slice(); } catch (e) { return null; } });
  res.checks.P3_avatar_held_during_encounter = !!posBefore && !!posAfter &&
    posBefore[0] === posAfter[0] && posBefore[1] === posAfter[1];
  res.detail.wasd = { before: posBefore, after: posAfter };

  // let any entry transition finish before testing input response
  await page.waitForTimeout(1500);
  const f0 = await page.evaluate(() => { try { return MG.flame; } catch (e) { return null; } });
  await page.mouse.down(); await page.waitForTimeout(50);
  const f1 = await page.evaluate(() => { try { return MG.flame; } catch (e) { return null; } });
  await page.mouse.up();
  res.checks.P5_click_feeds_flame = f0 !== null && f1 !== null && f1 > f0 + 0.001;
  res.detail.flame = { before: f0, afterClick: f1 };

  // survive-without-input floor: watch for 8s from encounter start
  const survived = await page.evaluate(async () => {
    const t0 = Date.now();
    try {
      while (Date.now() - t0 < 8000) {
        if (MG.failed || MG.won) return { survived_ms: Date.now() - t0, ended: true };
        await new Promise(r => setTimeout(r, 250));
      }
      return { survived_ms: 8000, ended: false };
    } catch (e) { return { err: e.message }; }
  });
  res.checks.P6_survives_8s_idle = !survived.err && survived.survived_ms >= 8000;
  res.detail.idle = survived;

  const tip = await page.evaluate(() => {
    const el = document.querySelector('#tip');
    return el ? el.innerText.slice(0, 300) : '';
  });
  const norm = s => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  res.checks.P4_first_use_line_shown = line ? norm(tip).includes(norm(line).slice(0, 40)) : true;
  res.detail.tip = tip.slice(0, 140);

  // force the run onward: wait out a resolution (up to 75s idle -> fail state), then re-test control
  await page.evaluate(async () => {
    const t0 = Date.now();
    try { while (MG.active && Date.now() - t0 < 75000) await new Promise(r => setTimeout(r, 400)); } catch (e) {}
  });
  const errCountAtResolve = errors.length;
  await page.waitForTimeout(1500);
  const pb = await page.evaluate(() => { try { return SIM.player_pos.slice(); } catch (e) { return null; } });
  for (let i = 0; i < 3; i++) { await page.keyboard.press('d'); await page.waitForTimeout(100); }
  const pa = await page.evaluate(() => { try { return SIM.player_pos.slice(); } catch (e) { return null; } });
  const resolved = await page.evaluate(() => { try { return { active: MG.active, won: MG.won, failed: MG.failed }; } catch (e) { return null; } });
  res.checks.P7_control_returns_after_resolution =
    !!resolved && resolved.active === false && !!pb && !!pa &&
    (pb[0] !== pa[0] || pb[1] !== pa[1]) && errors.length === errCountAtResolve;
  res.detail.resolution = { resolved, moveBefore: pb, moveAfter: pa };

  res.checks.P1_no_page_errors = errors.length === 0;
  res.detail.errors = errors.slice(0, 6);

  await browser.close();
  res.ok = Object.values(res.checks).every(Boolean);
  console.log(JSON.stringify(res));
  process.exit(res.ok ? 0 : 1);
}

main().catch(e => {
  console.log(JSON.stringify({ ok: false, probe_error: String(e).slice(0, 300) }));
  process.exit(2);
});
