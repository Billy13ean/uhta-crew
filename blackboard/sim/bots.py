#!/usr/bin/env python3
"""Run-7 regression bots vs rules-v2.1-C. Usage: python3 bots.py [test ...]

VENDORED COPY — `sim/bots.py` from the uhta blackboard, verbatim. It does
`import harness as H`, which is why the harness is vendored next to it under the
module name `harness` (the blackboard's own file is `sim/harness-v3.9.py`).
"""
import sys, copy, math, statistics as st
import harness as H
from harness import World, cheb

SEEDS = range(20)

def med(xs): return st.median(xs) if xs else None

def wake_budget(w): return w.budget()

# ---------- simple bots ----------
def bot_do_nothing(w, s): pass

def bot_wait_once(w, s):
    w.act('wait', cost=0.0)

def bot_walk_one(w, s):
    p = w.player_pos
    w.act('walk', pos=(p[0]+1, p[1]), cost=H.WALK_C)
    s['stamina_total'] = s.get('stamina_total',0)+H.WALK_C

def make_flamer(target_tribe, pole):
    """walk to target tribe wake 1, then flame every wake, sleep on site."""
    def bot(w, s):
        w.player_pole = pole
        tgt = w.tribes[target_tribe].center
        b = wake_budget(w)
        if w.player_pos != tgt:
            d = cheb(w.player_pos, tgt)
            c = min(d*H.WALK_C, b-2)
            w.act('walk', pos=tgt, cost=c); b -= c
            s['stamina_total'] = s.get('stamina_total',0)+c
        while b >= H.FLAME_C:
            w.act('flame', pole=pole, cost=H.FLAME_C); b -= H.FLAME_C
            s['stamina_total'] += H.FLAME_C
            if w.terminal: return
    return bot

def bot_throughput(w, s):
    """hope player; each wake target the enemy/grey tribe with most non-hope heads."""
    w.player_pole = 1
    best, bn = None, -1
    for t in w.tribes:
        n = sum(1 for x in w.npcs if x.tribe==t.idx and not x.zealot and x.I < 1)
        if n > bn: bn, best = n, t
    b = wake_budget(w)
    if w.player_pos != best.center:
        d = cheb(w.player_pos, best.center); c = min(d*H.WALK_C, b-H.FLAME_C)
        w.act('walk', pos=best.center, cost=c); b -= c
        s['stamina_total'] = s.get('stamina_total',0)+c
    while b >= H.FLAME_C and not w.terminal:
        w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C
        s['stamina_total'] += H.FLAME_C

# ---------- sieges (A14 pricing + A1) ----------
def siege_common(w, s, use_roar):
    """hope vs settled fear tribe 0. Returns when tribe flipped or budget gone."""
    w.player_pole = 1
    t = w.tribes[0]; tgt = t.center
    b = wake_budget(w)
    if w.player_pos != tgt:
        d = cheb(w.player_pos, tgt); c = min(d*H.WALK_C, b-2)
        w.act('walk', pos=tgt, cost=c); b -= c; s['stamina_total'] += c
    if use_roar and not s.get('roared'):
        w.act('roar', cost=H.ROAR_C); b -= H.ROAR_C
        s['stamina_total'] += H.ROAR_C; s['roared'] = True
    while b >= H.FLAME_C and not w.terminal:
        w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C
        s['stamina_total'] += H.FLAME_C

def run_siege(seed, use_roar, roads):
    w = World(seed); w.player_pole = 1
    s = {'stamina_total': 4.0 if roads else 0.0}   # road spur pre-charge (H-2)
    if roads: w.tribes[0].road_tiles = 2
    # let tribe 0 settle first (regulars pulled to -11 by ~sleep 2)
    for _ in range(3): w.do_sleep()
    flipped_at = None
    while w.sleep_no < 20 and not w.terminal and flipped_at is None:
        siege_common(w, s, use_roar)
        mem = [x for x in w.npcs if x.tribe==0 and not x.zealot]
        heads = sum(1 for x in mem if x.I >= 1)   # measured pre-sleep (peak claim)
        if not w.tribes[0].settled and heads >= len(mem)*0.5:
            flipped_at = w.sleep_no
        w.do_sleep()
    heads = sum(1 for x in w.npcs if x.tribe==0 and not x.zealot and x.I >= 1)
    return {'flip_sleep': flipped_at, 'stamina': s['stamina_total'],
            'heads': heads, 'per_head': s['stamina_total']/heads if heads else None,
            'unsettled': not w.tribes[0].settled}

# ---------- A9 self-burn probe: two adjacent hope tribes + auras ----------
def run_selfburn(seed):
    w = World(seed, zealot_poles=(1,1,-1)); w.player_pole = 1
    # move tribe 1 adjacent to tribe 0 so spheres overlap
    for x in w.npcs:
        if x.tribe == 1:
            x.pos = (16+w.rng.randint(-2,2), 10+w.rng.randint(-2,2))
    w.tribes[1].center = (16,10)
    w.player_pos = (13,10)
    w.beacons.append(((13,10), 1))
    s = {'stamina_total': H.BEACON_C}
    for _ in range(8):
        if w.terminal: break
        b = wake_budget(w)
        while b >= H.FLAME_C and not w.terminal:
            w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C
            s['stamina_total'] += H.FLAME_C
        w.do_sleep()
    return {'selfburns': w.selfburn_nozealot, 'sleeps': w.sleep_no}

# ---------- A5 save vs wait ----------
def run_save_vs_wait(seed):
    base = World(seed); base.player_pole = 1
    for _ in range(3): base.do_sleep()          # let camp settle
    base.player_pos = base.tribes[0].center
    base.act('roar', cost=H.ROAR_C)             # burn the camp
    burned = [x.id for x in base.npcs if x.burn]
    out = {}
    for policy in ('save','wait'):
        w = copy.deepcopy(base); stam = H.ROAR_C
        if policy == 'save':
            w.act('flame', pole=1, cost=H.FLAME_C); stam += H.FLAME_C   # save
            for _ in range(5):
                b = wake_budget(w) - (H.FLAME_C if _==0 else 0)
                while b >= H.FLAME_C and not w.terminal:
                    w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C; stam += H.FLAME_C
                w.do_sleep()
        else:
            for k in range(5):
                if k >= H.X_SLP:   # after zero-out: seed the absorbing greys
                    b = wake_budget(w)
                    while b >= H.FLAME_C and not w.terminal:
                        w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C; stam += H.FLAME_C
                w.do_sleep()
        heads = sum(1 for x in w.npcs if x.id in burned and not x.burn and x.I >= 1)
        out[policy] = {'heads_reclaimed': heads, 'stamina': stam}
    return out

# ---------- A13 seeded holds ----------
def run_hold(seed, f):
    w = World(seed); w.player_pole = 1
    regs = [x for x in w.npcs if not x.zealot]
    need = int(f*w.pop())
    for x in regs[:need]:
        x.v = 7.0; x.ever_nonzero = True
    w.beacons.append((w.tribes[2].center, 1))
    w.player_pos = w.tribes[2].center
    # awake attempt: idle ticks while beacon keeps |S| alive
    for _ in range(H.HOLD+2):
        if w.terminal: break
        w.act('none')
    awake_win = w.terminal is not None and w.terminal[0]=='win'
    # sleeping attempt from fresh copy
    w2 = World(seed); w2.player_pole = 1
    regs = [x for x in w2.npcs if not x.zealot]
    for x in regs[:need]: x.v = 7.0; x.ever_nonzero = True
    w2.beacons.append((w2.tribes[2].center, 1)); w2.player_pos = w2.tribes[2].center
    w2.stamina_spent_this_wake = 1.0
    for _ in range(3):
        if w2.terminal: break
        w2.do_sleep()
    sleep_win = w2.terminal is not None and w2.terminal[0]=='win'
    return {'awake': awake_win, 'sleeping': sleep_win}

# ---------- tyrant burst ----------
def run_tyrant(seed):
    from harness import World
    w = World(seed); w.player_pole = -1
    s = {'stamina_total':0.0}
    while w.sleep_no < 15 and not w.terminal:
        make_flamer(2, -1)(w, s)
        w.do_sleep()
    return {'terminal': w.terminal, 'max_wf': w.max_wf, 'sleeps': w.sleep_no}

def summarize(name, runs, keys):
    print(f"\n== {name} (n={len(runs)}) ==")
    for k in keys:
        vals = [r[k] for r in runs if r.get(k) is not None]
        if vals and isinstance(vals[0], (int,float)):
            print(f"  {k}: med={med(vals)} min={min(vals)} max={max(vals)} n={len(vals)}")
        else:
            print(f"  {k}: {vals[:8]}")

if __name__ == '__main__':
    which = set(sys.argv[1:]) or {'all'}
    def on(k): return 'all' in which or k in which

    if on('donothing'):
        runs = [H.run(bot_do_nothing, s, max_sleeps=40) for s in SEEDS]
        terms = [r['terminal'] for r in runs]
        print("\n== do-nothing (A11/G8, cap 40) ==")
        print("  terminals:", sorted(set(str(t) for t in terms)))
        tsleeps = [t[1] for t in terms if t]
        print(f"  loss terminal sleeps: med={med(tsleeps)} range={min(tsleeps) if tsleeps else '-'}..{max(tsleeps) if tsleeps else '-'} rate={len(tsleeps)}/20")
    if on('waitonce'):
        runs = [H.run(bot_wait_once, s, max_sleeps=40) for s in SEEDS]
        tsleeps = [r['terminal'][1] for r in runs if r['terminal']]
        print("\n== wait-once (A12 p1 / G10, cap 40) ==")
        print(f"  terminal rate={len(tsleeps)}/20 med_sleep={med(tsleeps)}")
    if on('walkone'):
        runs = [H.run(bot_walk_one, s, max_sleeps=40) for s in SEEDS]
        tsleeps = [r['terminal'][1] for r in runs if r['terminal']]
        print("\n== walk-one (active-idle residual, cap 40) ==")
        print(f"  terminal rate={len(tsleeps)}/20 med_sleep={med(tsleeps)} final_lf med={med([r['final_lf'] for r in runs]):.2f}")
    if on('tyrant'):
        runs = [run_tyrant(s) for s in SEEDS]
        wins = [r for r in runs if r['terminal'] and r['terminal'][0]=='win']
        print("\n== tyrant flame-burst (A7, fear, cap 15) ==")
        print(f"  win rate={len(wins)}/20 med_max_wf={med([r['max_wf'] for r in runs]):.3f}")
        if wins: print(f"  win sleeps: med={med([r['terminal'][1] for r in wins])}")
    if on('missionary'):
        runs = [H.run(make_flamer(0, 1), s, max_sleeps=25) for s in SEEDS]
        wins = [r for r in runs if r['terminal'] and r['terminal'][0]=='win']
        print("\n== missionary hope (cap 25) ==")
        print(f"  terminals: win={len(wins)}/20 loss={sum(1 for r in runs if r['terminal'] and r['terminal'][0]=='loss')}/20")
        print(f"  max_wf med={med([r['final_wf'] for r in runs]):.3f} selfburns med={med([r['selfburns'] for r in runs])}")
    if on('throughput'):
        runs = [H.run(bot_throughput, s, max_sleeps=25) for s in SEEDS]
        wins = [r for r in runs if r['terminal'] and r['terminal'][0]=='win']
        losses = [r for r in runs if r['terminal'] and r['terminal'][0]=='loss']
        print("\n== throughput hope (A10 pacing, cap 25) ==")
        print(f"  win={len(wins)}/20 loss={len(losses)}/20 none={20-len(wins)-len(losses)}/20")
        if wins: print(f"  win sleeps med={med([r['terminal'][1] for r in wins])} range={min(r['terminal'][1] for r in wins)}..{max(r['terminal'][1] for r in wins)}")
        print(f"  final_wf med={med([r['final_wf'] for r in runs]):.3f} selfburns med={med([r['selfburns'] for r in runs])}")
    if on('siege'):
        ro = [run_siege(s, use_roar=True, roads=False) for s in SEEDS]
        rd = [run_siege(s, use_roar=False, roads=True) for s in SEEDS]
        rn = [run_siege(s, use_roar=False, roads=False) for s in SEEDS]
        summarize("overdose-siege (A14 route)", ro, ['flip_sleep','stamina','heads','per_head'])
        summarize("roads-siege (2 tiles + 4.0 pre-charge)", rd, ['flip_sleep','stamina','heads','per_head'])
        summarize("frontal-siege (no roar, no roads)", rn, ['flip_sleep','stamina','heads','per_head'])
    if on('selfburn'):
        runs = [run_selfburn(s) for s in SEEDS]
        print("\n== A9 overlap self-burn probe (8 wakes, beacon+flames in overlap) ==")
        print(f"  selfburns (no-zealot, own pole): med={med([r['selfburns'] for r in runs])} max={max(r['selfburns'] for r in runs)}")
    if on('savewait'):
        runs = [run_save_vs_wait(s) for s in SEEDS]
        sh = [r['save']['heads_reclaimed'] for r in runs]; wh = [r['wait']['heads_reclaimed'] for r in runs]
        ss = [r['save']['stamina'] for r in runs]; ws = [r['wait']['stamina'] for r in runs]
        print("\n== A5 save vs wait (+5 sleeps horizon) ==")
        print(f"  save: heads med={med(sh)} stamina med={med(ss):.1f}")
        print(f"  wait: heads med={med(wh)} stamina med={med(ws):.1f}")
    if on('hold'):
        for f in (0.82, 0.85, 0.90):
            runs = [run_hold(s, f) for s in SEEDS]
            aw = sum(1 for r in runs if r['awake']); sl = sum(1 for r in runs if r['sleeping'])
            print(f"\n== A13 seeded hold f={f}: awake {aw}/20, sleeping-through {sl}/20 ==")

# ---------- run 9 additions: campaign bot + merged-camp overdose + start sweep ----------
def run_campaign(seed, start='tentative'):
    w = World(seed, start=start); w.player_pole = 1
    s = {'stamina_total': 0.0}
    roads_paid = set()
    while w.sleep_no < 25 and not w.terminal:
        # pick target: first enemy tribe not yet hope-majority-durable
        tgt = None
        for t in w.tribes:
            mem = [x for x in w.npcs if x.tribe==t.idx and not x.zealot]
            deep = sum(1 for x in mem if x.I >= 3)
            if t.pole == -1 and deep < len(mem)*0.5: tgt = t; break
        if tgt is None:
            # consolidate: deepen shallowest cohort anywhere, keep S alive, let hold complete
            shallow = [x for x in w.npcs if not x.zealot and 0 <= x.I < 3]
            tgt = w.tribes[shallow[0].tribe] if shallow else w.tribes[2]
        b = wake_budget(w)
        if tgt.idx not in roads_paid and tgt.pole == -1:
            pay = min(4.0, b-3); s['stamina_total'] += pay; b -= pay
            w.tribes[tgt.idx].road_tiles = 4; roads_paid.add(tgt.idx)
        if w.player_pos != tgt.center:
            d = cheb(w.player_pos, tgt.center); c = min(d*H.WALK_C, max(0.0, b-H.FLAME_C))
            w.act('walk', pos=tgt.center, cost=c); b -= c; s['stamina_total'] += c
        while b >= H.FLAME_C and not w.terminal:
            w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C; s['stamina_total'] += H.FLAME_C
        if w.terminal: break
        w.do_sleep()
    return {'terminal': w.terminal, 'sleeps': w.sleep_no, 'final_wf': w.win_count()/w.pop(),
            'stamina': s['stamina_total'], 'selfburns': w.selfburn_nozealot}

def run_overdose_merged(seed):
    """A14 re-gate test: adjacent fear camps (double-pull zone) + roar."""
    w = World(seed, zealot_poles=(-1,-1,1)); w.player_pole = 1
    for x in w.npcs:
        if x.tribe == 1: x.pos = (16+w.rng.randint(-2,2), 10+w.rng.randint(-2,2))
    w.tribes[1].center = (16,10)
    for _ in range(3): w.do_sleep()
    w.player_pos = (13,10)
    s = {'stamina_total': 4.0}   # merge-engineering pre-charge per designer walk
    w.act('roar', cost=H.ROAR_C); s['stamina_total'] += H.ROAR_C
    burned0 = sum(1 for x in w.npcs if x.burn)
    for _ in range(6):
        if w.terminal: break
        b = wake_budget(w)
        while b >= H.FLAME_C and not w.terminal:
            w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C; s['stamina_total'] += H.FLAME_C
        w.do_sleep()
    heads = sum(1 for x in w.npcs if x.tribe in (0,1) and not x.zealot and not x.burn and x.I >= 1)
    return {'burned_on_roar': burned0, 'heads': heads, 'stamina': s['stamina_total'],
            'per_head': s['stamina_total']/heads if heads else None}

def run_solo_roar(seed):
    """re-gate negative control: roar a solo camp — should burn zero."""
    w = World(seed); w.player_pole = 1
    for _ in range(3): w.do_sleep()
    w.player_pos = w.tribes[0].center
    w.act('roar', cost=H.ROAR_C)
    return {'burned': sum(1 for x in w.npcs if x.burn)}

# ---------- run 11: fate-aware campaign ----------
def run_campaign_v3(seed, start='tentative'):
    w = World(seed, start=start); w.player_pole = 1
    s = {'stamina_total': 0.0}
    roads_paid = set()
    # cap 32: wander adds ~5 sleeps of chase-cost to the sequential campaign (v3.3);
    # under v3.2 (no wander) wins land 22-24, under v3.3 they land 28-29.
    while w.sleep_no < 32 and not w.terminal:
        # target: enemy tribe that still has a living opposing zealot; else deepen shallow
        tgt = None
        for t in w.tribes:
            if not t.zealotless and t.pole == -1:
                tgt = t; break
        if tgt is None:
            shallow = [x for x in w.npcs if not x.zealot and 0 <= x.I < 4]
            tgt = w.tribes[shallow[0].tribe] if shallow else w.tribes[2]
        b = wake_budget(w)
        if tgt.idx not in roads_paid and tgt.pole == -1 and not tgt.zealotless:
            pay = min(4.0, b-3); s['stamina_total'] += pay; b -= pay
            w.tribes[tgt.idx].road_tiles = 4; roads_paid.add(tgt.idx)
        if w.player_pos != tgt.center:
            d = cheb(w.player_pos, tgt.center); c = min(d*H.WALK_C, max(0.0, b-H.FLAME_C))
            w.act('walk', pos=tgt.center, cost=c); b -= c; s['stamina_total'] += c
        while b >= H.FLAME_C and not w.terminal:
            w.act('flame', pole=1, cost=H.FLAME_C); b -= H.FLAME_C; s['stamina_total'] += H.FLAME_C
        if w.terminal: break
        w.do_sleep()
    ev = getattr(w, 'fate_events', [])
    return {'terminal': w.terminal, 'sleeps': w.sleep_no, 'final_wf': w.win_count()/w.pop(),
            'fate_events': ev, 'stamina': s['stamina_total'], 'selfburns': w.selfburn_nozealot}
