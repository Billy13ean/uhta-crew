/* sonder-teller.js — the Sonder engine's game-side half. Zero dependencies.
 *
 * Include after the bank:
 *   <script src="sonder-bank.js"></script>    (generated: window.SONDER_BANK)
 *   <script src="sonder-teller.js"></script>
 *
 * Then, at the moment the build wants to tell a story — e.g. when the player's
 * flame converts someone (an NPC crosses into devout under the player's colour):
 *
 *   const story = Sonder.pick({ flame: player.pole });          // 'fear' | 'hope'
 *   if (story) Sonder.show(story, { tint: player.pole });        // overlay card
 *
 * pick() never repeats a story in one run until the pool is exhausted, prefers
 * tellings that passed the style gate, and can be narrowed by tags, era, line:
 *   Sonder.pick({ flame: 'fear', anyTags: ['someone-broke', 'betrayed-someone'] })
 *   Sonder.pick({ flame: 'hope', era: 'villages' })          // match the town's age
 *   Sonder.pick({ flame: 'fear', line: 'hild' })             // the same bloodline, any age
 * Every story ends on THE CHOICE — a question put to the player (story.choice.question).
 *
 * Canon note: where a telling may appear in the wordless game is a Director
 * ruling (see README, "Integration"). This file only makes it one call.
 */
(function (global) {
  const bank = () => global.SONDER_BANK || { stories: [], index: {} };
  const told = new Set();

  function pick(opts) {
    opts = opts || {};
    let pool = bank().stories.slice();
    if (opts.flame) pool = pool.filter(s => s.flame === opts.flame);
    if (opts.ending) pool = pool.filter(s => s.ending === opts.ending);
    if (opts.who) pool = pool.filter(s => s.who.id === opts.who);
    if (opts.era) pool = pool.filter(s => s.era === opts.era);
    if (opts.line) pool = pool.filter(s => s.who.line === opts.line);
    if (opts.anyTags && opts.anyTags.length) pool = pool.filter(s => s.tags.some(t => opts.anyTags.includes(t)));
    if (opts.allTags && opts.allTags.length) pool = pool.filter(s => opts.allTags.every(t => s.tags.includes(t)));
    if (!opts.includeUnclean) { const clean = pool.filter(s => s.telling_clean); if (clean.length) pool = clean; }
    if (!pool.length) return null;
    let fresh = pool.filter(s => !told.has(s.id));
    if (!fresh.length) { pool.forEach(s => told.delete(s.id)); fresh = pool; }
    const rng = typeof opts.random === 'function' ? opts.random : Math.random;
    const s = fresh[Math.floor(rng() * fresh.length)];
    told.add(s.id);
    return s;
  }

  // A minimal overlay in the uhta palette. Replace with the build's own card if it has one.
  const PAL = { void: '#050507', bg: '#0c0c10', grey: '#6a6a72', greyL: '#9a9aa2', player: '#f2f2f5', gold: '#d9c98a', hope: '#63c76b', fear: '#d45b57' };
  function show(story, opts) {
    opts = opts || {};
    const tint = opts.tint || story.flame;
    const col = tint === 'hope' ? PAL.hope : tint === 'fear' ? PAL.fear : PAL.player;
    const host = opts.parent || document.body;
    const el = document.createElement('div');
    el.setAttribute('role', 'dialog');
    el.style.cssText = `position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(5,5,7,.82);z-index:9999;font-family:ui-monospace,Consolas,monospace;color:${PAL.greyL};`;
    const card = document.createElement('div');
    card.style.cssText = `max-width:56ch;padding:1.6em 2em;background:${PAL.bg};border:1px solid ${col};box-shadow:0 0 40px rgba(0,0,0,.7);line-height:1.55;font-size:14px;`;
    const head = document.createElement('div');
    head.style.cssText = `color:${col};letter-spacing:.14em;font-size:11px;margin-bottom:.8em;`;
    head.textContent = `${story.who.name.toUpperCase()} — WHO ${story.who.role.toUpperCase()}`;
    const q = story.choice && story.choice.question ? story.choice.question : '';
    let text = story.telling || '';
    if (q && text.trim().endsWith(q)) text = text.trim().slice(0, -q.length).trimEnd();
    const body = document.createElement('div');
    body.style.cssText = `color:${PAL.player};white-space:pre-wrap;`;
    body.textContent = text;
    const ask = document.createElement('div');
    ask.style.cssText = `color:${PAL.gold};margin-top:1em;padding-left:.8em;border-left:2px solid ${PAL.gold};white-space:pre-wrap;`;
    ask.textContent = q;
    const foot = document.createElement('div');
    foot.style.cssText = `color:${PAL.grey};font-size:11px;margin-top:1em;`;
    foot.textContent = 'sonder';
    card.appendChild(head); card.appendChild(body); if (q) card.appendChild(ask); card.appendChild(foot); el.appendChild(card); host.appendChild(el);
    const close = () => { el.remove(); if (opts.onClose) opts.onClose(story); };
    el.addEventListener('click', close);
    global.addEventListener('keydown', function k(e) { if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') { global.removeEventListener('keydown', k); close(); } });
    if (opts.autoCloseMs) setTimeout(close, opts.autoCloseMs);
    return el;
  }

  function stats() {
    const b = bank(); const by = k => Object.fromEntries(Object.entries(b.index[k] || {}).map(([a, v]) => [a, v.length]));
    return { count: b.count || 0, clean: b.clean_count || 0, byFlame: by('by_flame'), byEnding: by('by_ending'), byEra: by('by_era'), byLine: by('by_line'), told: told.size };
  }

  global.Sonder = { pick, show, stats, reset: () => told.clear() };
})(typeof window !== 'undefined' ? window : globalThis);
