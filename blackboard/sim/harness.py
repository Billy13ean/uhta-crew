#!/usr/bin/env python3
"""uhta reference sim — CANONICAL against rules-v3.2-C (schema 3.2.3, CANON v10).

Keeper-authored (runs 7-14). This is the executable spec the Phaser build must
match (GDD 3.3); see SPEC.md (run 15). The module is fully DATA-DRIVEN — it reads
every tunable from the JSON named by env RULES (default below is a historical
fallback; ALWAYS run with RULES=rules-v3.2-C.json). Inline value-comments quoting
+-8/1.8/2.1/0.5 are STALE v2.x artifacts; the authoritative values come from the
loaded JSON (v3.2-C: span +-12, flame 2.0, roar 2.8, save 0.75, Y 4).

VENDORED COPY — this file is `sim/harness-v3.9.py` from the uhta blackboard,
copied here verbatim under the module name `harness` because `sim/bots.py` does
`import harness as H`. Do not edit it in this repo: it is the Playtester's tool,
not code the crew regenerates (prompts/playtester.md, hard rule 1).

Implements, selected by JSON presence (no env flags for v3.2-C):
G5 >=Y burnout, Y=2*pull; G6/G16 hold windows spanning a generation, pauses/fail
continuity; G10 zero-stamina idleness; G11 grey-0 averages; G12 flat growth;
G13/G18/G19 split zero-value membership + cumulative re-adoption window; G14
awake-scaled pull + sleep-only decay; G18/G20 zealot_fate (defer + breath-hold,
integer-state averaging, per-pole bars, Hope-converts/Fear-breaks); G19 no-living-
opposing-zealot win precondition. Conformance: rule-facing averages use integer I;
group_size counts |I|>=1; burned excluded from contagion.

HARNESS ASSUMPTIONS (H-1..H-8), documented in metrics-v2.md:
H-1 Static NPC positions (no pathfinding/wandering); tribes are fixed clusters.
H-2 Chebyshev distances; roads modeled as per-tribe adjacency count + a flat
    stamina pre-charge for the roads-siege bot (no tile network).
H-3 Intent window "trailing 1 sleep" = pressure entries from the current wake
    plus the immediately preceding sleep's ticks.
H-4 Integer state I = trunc(v); sub-integer accumulator is v's fraction
    (designer Assumption 1); step cap clamps dv per tick to +-1.
H-5 Each player action advances the world one tick (auras/pulls/decay co-resolve).
H-6 Sphere pull: tribe members in own sphere take zealot pull 2.0; non-members
    inside a sphere take overlap pull 0.8 toward that sphere's zealot pole.
H-7 Wake movement: bots pay Chebyshev distance x walk cost once per relocation;
    within-cluster adjacency assumed thereafter.
H-8 Save action = the opposing-valence verb applied to burned NPCs in radius;
    it clears flags only (no scale pressure that tick, canon: not pressure).
"""
import json, math, random, sys, copy
from collections import deque

import os
RULES = json.load(open(os.environ.get('RULES','rules-v2.1-C.json')))

SPAN   = RULES['scale']['max']                  # 12
ZVAL   = RULES['scale']['zealot_value']         # 12
TENT_LO, TENT_HI = RULES['bands']['tentative']  # 1,5
DEV_LO, DEV_HI   = RULES['bands']['devout']     # 6,11
STEP   = RULES['contagion']['step_per_tick_max']            # 1
SPH_BASE = RULES['contagion']['sphere_base_radius_tiles']   # 2
OVERLAP  = RULES['contagion']['overlap_pull_strength']      # 0.8
AWAKE_MULT = RULES['contagion'].get('awake_pull_multiplier', None)  # schema 2.2 (G14)
_zvm = RULES['contagion'].get('zero_value_membership', {})
READOPT_W = _zvm.get('readoption_window_ticks', _zvm.get('window_ticks_at_zero_cumulative', None))  # schema 3/3.2 shapes
WINDOW_CUM = (_zvm.get('window_counter') == 'cumulative_ticks_at_zero') or ('window_ticks_at_zero_cumulative' in _zvm) or __import__('os').environ.get('WINDOW_CUM','0') == '1'
STABLE_ABS = _zvm.get('counter_resets_on_stable_adoption_abs', _zvm.get('reset_on_stable_adoption_abs_gte', 2))
ZFATE = RULES.get('zealot_fate', None)                    # schema 3 (G18-1)
PP     = RULES['player_pressure']
FLAME_PUSH, FLAME_R = PP['flame_push_base'], PP['flame_radius_tiles']   # 1.8, 3
ROAR_PUSH, ROAR_R   = PP['roar_fear_push'], PP['roar_witness_radius_R_tiles']  # 2.1, 6
WAIT_PUSH, WAIT_R   = PP['wait_apathy_push'], PP['wait_witness_radius_tiles']  # 0.5, 1
SLEEP_PUSH, SLEEP_R = PP['sleep_tick_push'], PP['sleep_radius_tiles']   # 0.3, 3
BEAC_PUSH, BEAC_R   = PP['beacon_tick_push'], PP['beacon_radius_tiles'] # 0.5, 4
Y      = RULES['burnout']['overdose_threshold_Y_per_tick']  # 4
X_SLP  = RULES['burnout']['timer_X_sleeps']                 # 3
SAVE_F = RULES['burnout']['save_penalty_fraction']          # 0.5
SETTLE_ABS = RULES['settling']['settle_band_threshold_abs'] # 6
SETTLE_HOLD = RULES['settling']['settle_hold_generations']  # 1
UNSETTLE_HOLD = RULES['settling']['unsettle_hold_generations'] # 1
RES_MULT = RULES['settling']['resistance_opposing_multiplier'] # 0.3
ROAD_ERO = RULES['settling']['road_erosion_per_adjacent_tile'] # 0.2
RES_FLOOR = RULES['settling']['resistance_floor']           # 0.2
ST     = RULES['stamina']
FLOOR  = ST['floor_actions']                                # 5
W_T, W_D, W_Z = (ST['worship_band_weights'][k] for k in ('tentative','devout','zealot'))
BEACON_BONUS = ST['per_beacon_bonus']                       # 1.5
COST = ST['costs']
WALK_C, FLAME_C, BEACON_C = COST['walk_per_tile_base'], COST['flame'], COST['light_beacon']
ROAR_C = 0.5 * WALK_C * ROAR_R   # projection base: 0.5*0.5*6 = 1.5
RAZE = RULES['raze']
WORLD  = RULES['world']
N_GROW = WORLD['growth_per_tribe_per_sleep']                # 2
DECAY  = WORLD['apathy_decay_per_tick']                     # 0.4
PULL   = WORLD['zealot_pull_per_tick']                      # 2.0
T_SLEEP = WORLD['generation_ticks_per_sleep']               # 3
TRIBE_SIZE = WORLD['tribe_size_initial']                    # 12
MAP = WORLD['map_size']                                     # 48
WANDER = WORLD.get('wander', None)                          # schema 3.3 (belief-neutral nomadic drift)
ROAD_FOLLOW = (WANDER or {}).get('road_follow', None)       # schema 3.4 (strong road-following steer)
FIGHT  = WORLD.get('faction_fight', None)                   # schema 3.4 (real-casualty faction fights)
BP     = (FIGHT or {}).get('battle_pressure', None)         # schema 3.5 (Fear breaks / Hope bends)
EXILE  = WORLD.get('settlement_exile', None)                # schema 3.4 (burnout-only settlement exit -> loner)
LONER  = -1                                                 # loner tribe id (detached wanderer)
GEN    = WORLD.get('genesis', None)                         # schema 3.6 (grey-nomad genesis start)
MIN_SETTLE = (GEN or {}).get('min_settle_members', 0) if (GEN and GEN.get('enabled')) else 0
FORMED_FRAC = (GEN or {}).get('formed_aligned_fraction', 0.4)
SCHISM = WORLD.get('schism', None)                          # schema 3.7 (capped-count colony fission)
ROADALLEG = WORLD.get('road_allegiance', None)              # schema 3.7.1 (roads carry a pole; erode enemies)
HOPE_TRADE = WORLD.get('hope_trade', None)                  # schema 3.7.2 (hope colonies trade -> green roads)
CONTAGION = WORLD.get('contagion_spread', None)             # schema 3.8.1 (peer belief contagion)
UHT    = WORLD.get('uhtcearu_events', None)                 # schema 3.9 (Run 23: Uhtcearu active events)
UHT_ON = bool(UHT and UHT.get('enabled') and UHT.get('variant') == 'A_grief_front')
GF     = (UHT or {}).get('grief_front', {})                 # schema 3.9 grief-front params
# ---- schema 3.10 (Run 24 proposal, GDD §9): the Temple — grief gets a home. ALL default-off; ----
# ---- with every flag absent/false the module is bit-identical to schema 3.9.1.              ----
TEMPLE = WORLD.get('temple', None)                          # schema 3.10 temple block
TEMPLE_ON = bool(TEMPLE and TEMPLE.get('enabled'))
TWELL = (TEMPLE or {}).get('local_decay', None)             # schema 3.10 variant C: local decay zone
TWELL_ON = bool(TEMPLE_ON and TWELL and TWELL.get('enabled'))
ASCENSION = RULES.get('ascension', {})                      # schema 3.8 (follower-driven power scale)
TIERS = ASCENSION.get('tiers', None) if ASCENSION.get('enabled') else None
STAM_PER_FOLLOWER = ASCENSION.get('stamina_per_follower', 0.35)
WL     = RULES['win_loss']
TIE_LOSS = WL.get('tie_priority') == 'loss'                 # schema 3.9 (v0.9.1: tie -> loss)
HOLD   = WL['hold_window_ticks']                            # 6
HOLD_SPAN_GEN = WL.get('hold_must_span_generation', False)   # G16
THRESH = WL['unification_threshold_fraction']               # 0.8
# schema 3.10: two-phase win terminal. 'hold_complete' (default, = 3.9.1) fires the win the
# tick the hold completes; 'temple_entry' ARMS it there and fires it when the avatar enters
# the temple footprint. Requires the temple to be enabled, else silently 'hold_complete'.
TERM_ON = WL.get('terminal_fires_on', 'hold_complete')
TEMPLE_TERM = TEMPLE_ON and TERM_ON == 'temple_entry'
TENTRY = WL.get('temple_entry', {}) if TEMPLE_TERM else {}
S_GATE = 3.0   # |S| >= 3 from intent_measure
IDLE_CO = 0.4  # damping idle coefficient from formula
import os as _os
AWAKE_PULL = _os.environ.get('AWAKE_PULL','1') == '1'  # canon-literal co-resolution default

def band(I):
    a = abs(I)
    if a == 0: return 'grey'
    if a <= TENT_HI: return 'tentative'
    if a <= DEV_HI: return 'devout'
    return 'zealot'

class NPC:
    _n = 0
    def __init__(self, tribe, pos, v, zealot=False):
        self.id = NPC._n; NPC._n += 1
        self.tribe, self.pos, self.v, self.zealot = tribe, pos, float(v), zealot
        self.burn = False; self.burn_frozen = 0.0; self.burn_sleeps = 0
        self.ever_nonzero = abs(int(v)) >= 1
        self.zero_ticks = 0
    @property
    def I(self): return int(self.v)
    @property
    def absorbing(self):
        if self.zealot or self.burn or self.I != 0: return False
        # schema 3.6: an uncommitted wanderer (a genesis grey nomad that never held a conviction)
        # never lapses into apathy — it stays open to conviction until first aligned. The re-adoption
        # window (absorbing-out) applies only to souls that ONCE believed and drifted back to 0.
        if self.tribe < 0 and not self.ever_nonzero: return False
        if READOPT_W is not None:
            return self.zero_ticks >= READOPT_W
        return self.ever_nonzero

def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

class Tribe:
    def __init__(self, idx, center, pole):
        self.idx, self.center, self.pole = idx, center, pole
        self.settled = False; self.settle_pole = 0
        self.hold_ctr = 0; self.unsettle_ctr = 0
        self.road_tiles = 0
        self.fate_ctr = 0; self.zealotless = False
        self.home = list(center); self.heading = (0,0); self.rout_from = None; self.rout_dist = None

class World:
    def __init__(self, seed, zealot_poles=(-1,-1,1), road_tiles=None, start='tentative'):
        self.rng = random.Random(seed)
        self.wrng = random.Random((seed ^ 0x9E3779B9) & 0xFFFFFFFF)
        self.start = start
        self.npcs = []; self.tribes = []
        if GEN and GEN.get('enabled'):
            # ---- schema 3.6 GENESIS: grey nomads + lone founding zealots that gather & settle ----
            fpoles = GEN.get('founding_poles', list(zealot_poles))   # schema 3.7.1: symmetric 1F/1H by default
            gcenters = [(12,24),(36,24),(24,13),(24,35),(6,6)][:len(fpoles)]
            seeds = GEN.get('zealot_seeds_each', 3)
            for i,(c,pole) in enumerate(zip(gcenters, fpoles)):
                t = Tribe(i, c, pole); self.tribes.append(t)
                self.npcs.append(NPC(i, c, ZVAL*pole, zealot=True))
                for _ in range(seeds):   # a small aligned nucleus so the zealot's sphere can begin gathering
                    off = (c[0]+self.rng.randint(-1,1), c[1]+self.rng.randint(-1,1))
                    self.npcs.append(NPC(i, off, 2*pole))
            for _ in range(GEN.get('grey_nomads', 40)):   # unaligned wanderers (loners) scattered
                p = (self.rng.randint(0, MAP-1), self.rng.randint(0, MAP-1))
                self.npcs.append(NPC(LONER, p, 0))
        else:
            centers = [(10,10),(38,10),(24,38)]
            for i,(c,pole) in enumerate(zip(centers, zealot_poles)):
                t = Tribe(i, c, pole); self.tribes.append(t)
                self.npcs.append(NPC(i, c, ZVAL*pole, zealot=True))
                for _ in range(TRIBE_SIZE-1):
                    off = (c[0]+self.rng.randint(-2,2), c[1]+self.rng.randint(-2,2))
                    # initial_state per G17 sweep: tentative | mixed | grey
                    if self.start == 'grey': v0 = 0
                    elif self.start == 'mixed': v0 = self.rng.choice([0, 2*pole, 2*pole])
                    else: v0 = 2*pole
                    self.npcs.append(NPC(i, off, v0))
        self.sleep_no = 0; self.tick_no = 0
        self.player_pos = (24,24); self.player_pole = 1  # hope default
        self.beacons = []            # (pos, pole)
        self.idle_sleeps = 0
        self.win_hold = 0; self.loss_hold = 0; self.max_wf = 0.0; self.win_hold_sleepticks = 0
        self.intent = deque()        # (tick, signed valence delivered)
        self.wake_entries = []       # intent entries this wake
        self.terminal = None         # ('win'|'loss', sleep)
        self.formed = not (GEN and GEN.get('enabled'))   # genesis: no terminals until the world takes shape
        self.stamina_spent_this_wake = 0.0
        self.selfburn_nozealot = 0   # A9 counter
        self.log_burns = []
        self.roads = set()           # schema 3.4: real road-tile network (mirrors the build's walked tiles)
        self.road_pole = {}          # schema 3.7.1: tile -> pole (allegiance)
        self.road_str = {}           # schema 3.7.1: tile -> strength (worn by opposing crossings)
        self.flame_r = FLAME_R; self.aura_r = SLEEP_R       # schema 3.8: ascension-scaled radii
        self.stamina_cap = 14; self.beacon_cap = ASCENSION.get('beacon_cap_t1', 1); self.tier = 0
        self.fight_deaths = 0        # casualties this run (belief-affecting; exploit-tracked)
        self.exiles = 0              # settlement burnout-exiles this run
        self.readoptions = 0         # loners re-adopted into a tribe this run
        # schema 3.9: Grief Front state (Variant A, Run 23) — scheduler state, not an agent
        self.front = None            # None | {'center':[x,y], 'sleeps_left':int}
        self.front_cooldown = 0
        self.fronts_spawned = 0
        self.front_max_concurrent = 0
        self.front_exposure_npc_sleeps = 0.0  # NPC-sleeps of decay taken inside a front (efficacy)
        self.front_zealot_decays = 0          # zealots_immune audit: must stay 0
        self.front_events = []                # (sleep_no, 'spawn'|'expire', (cx,cy)) audit trail
        # schema 3.9.1 (Run 23b): trailing trigger window, dom-only audit, per-front exposure
        self.dom_hist = deque(maxlen=max(1, GF.get('trigger_trailing_window_sleeps', 1)))
        self.front_offpole_decays = 0         # affects_dominant_pole_only audit: must stay 0
        self.front_expo_log = []              # exposure (NPC-sleeps) per expired front
        # schema 3.10: temple + armed terminal state (all None/False unless enabled)
        self.temple_pos = None
        self.win_armed = False; self.win_armed_sleep = None
        self.pilgrim_tiles = 0                 # autopilot tiles walked while armed (H-9)
        self.front_travel_sleeps = []          # per spawned front: sleeps spent travelling (spawn_at temple)
        self.well_exposure_npc_sleeps = 0.0    # variant C: NPC-sleeps of elevated decay in the zone
        if TEMPLE_ON:
            self.temple_pos = self._place_temple(seed)
        self.recompute_power()       # schema 3.8: initial power tier

    # ---------- schema 3.10: temple placement ----------
    def _place_temple(self, seed):
        """Seeded, constrained random placement. Draws from its OWN rng stream so enabling the
        temple perturbs nothing else in the world (the two existing streams are untouched).
        Constraints (GDD §9): >= min_dist_cave from the cave, >= min_dist_sites from every
        beacon basin, >= min_dist_edge from the map edge, >= min_dist_tribes from every tribe
        centre at genesis. placement 'fixed' uses fixed_position verbatim (LANDMARKS §4)."""
        if TEMPLE.get('placement', 'random_constrained') == 'fixed':
            fp = TEMPLE.get('fixed_position', [24, 6]); return (int(fp[0]), int(fp[1]))
        trng = random.Random((seed ^ 0x7E3A9C1F) & 0xFFFFFFFF)
        cave = tuple(TEMPLE.get('cave', [24, 24]))
        sites = [tuple(q) for q in TEMPLE.get('beacon_sites', [[7,7],[41,7],[7,41],[41,41],[24,44]])]
        d_cave = TEMPLE.get('min_dist_cave', 14); d_site = TEMPLE.get('min_dist_sites', 6)
        d_edge = TEMPLE.get('min_dist_edge', 6);  d_tribe = TEMPLE.get('min_dist_tribes', 6)
        centers = [tuple(t.center) for t in self.tribes]
        def ok(c):
            if cheb(c, cave) < d_cave: return False
            if any(cheb(c, q) < d_site for q in sites): return False
            if any(cheb(c, q) < d_tribe for q in centers): return False
            return True
        lo, hi = d_edge, MAP - 1 - d_edge
        for _ in range(TEMPLE.get('placement_tries', 500)):
            c = (trng.randint(lo, hi), trng.randint(lo, hi))
            if ok(c): return c
        # fallback (constraints unsatisfiable on this map): the in-bounds tile farthest from everything
        best, bd = None, -1
        for x in range(lo, hi+1):
            for y in range(lo, hi+1):
                d = min([cheb((x,y), cave)] + [cheb((x,y), q) for q in sites + centers])
                if d > bd: bd, best = d, (x, y)
        return best

    def _pilgrim_step(self, pace):
        px, py = self.player_pos; tx, ty = self.temple_pos
        dx = max(-pace, min(pace, tx - px)); dy = max(-pace, min(pace, ty - py))
        self.player_pos = (px + dx, py + dy); self.pilgrim_tiles += max(abs(dx), abs(dy))

    def in_temple(self, pos):
        return self.temple_pos is not None and cheb(pos, self.temple_pos) <= TEMPLE.get('footprint_radius_tiles', 2)

    # ---------- population helpers ----------
    def pop(self): return len(self.npcs)
    def win_count(self):
        p = self.player_pole; n = 0
        for x in self.npcs:
            if x.burn: continue
            if x.I*p >= 1 or (x.zealot and x.I*p > 0): n += 1
        return n
    def loss_count(self):
        n = 0
        for x in self.npcs:
            if x.burn or x.I == 0: n += 1
        return n
    def dominance(self): return self.win_count()/self.pop()
    def weighted_worship(self):
        p = self.player_pole; w = 0.0
        for x in self.npcs:
            if x.burn or x.I*p < 1: continue
            b = band(x.I)
            w += {'tentative':W_T,'devout':W_D,'zealot':W_Z}.get(b,0)
        return w
    def budget(self):
        return min(self.stamina_cap, FLOOR + STAM_PER_FOLLOWER*self.weighted_worship() + BEACON_BONUS*len(self.beacons))

    def recompute_power(self):
        """schema 3.8 ascension: your power tier scales with your flock (win_count). Recomputed at
        each sleep = 'level up'. Higher tiers: more beacons, bigger flame/aura, larger stamina cap."""
        if not TIERS:
            self.flame_r = FLAME_R; self.aura_r = SLEEP_R; self.stamina_cap = 14
            self.beacon_cap = ASCENSION.get('beacon_cap_t1', 1); self.tier = 0; return
        f = self.win_count()
        ti = 0
        for i, t in enumerate(TIERS):
            if f >= t.get('min_followers', 0): ti = i
        t = TIERS[ti]
        self.tier = ti
        self.flame_r = FLAME_R + t.get('flame_radius_bonus', 0)
        self.aura_r = SLEEP_R + t.get('aura_radius_bonus', 0)
        self.stamina_cap = t.get('stamina_cap', 14)
        self.beacon_cap = t.get('beacons', 1)

    # ---------- spheres ----------
    def sphere(self, t):
        gs = sum(1 for x in self.npcs if x.tribe==t.idx and not x.burn and abs(x.I)>=1)
        return SPH_BASE + int(math.isqrt(max(gs,0)))
    def eff_mult(self, npc, pressure_pole):
        """settlement resistance on opposing-pole pressure; v3.2.2 breath-hold:
        a fate-deferred camp gets settled-equivalent resistance on the CONVERSION
        side (protects the deep average from its own zealot) for that generation."""
        if npc.tribe == LONER: return 1.0   # loners carry no settlement resistance
        t = self.tribes[npc.tribe]
        sp = t.settle_pole if t.settled else 0
        if getattr(t, 'fate_deferred', False):
            sp = -t.pole
        if sp != 0 and pressure_pole == -sp:
            return min(RES_MULT + ROAD_ERO*t.road_tiles, 1-RES_FLOOR)
        return 1.0

    # ---------- one tick ----------
    def tick(self, actions=(), sleeping=False):
        """actions: list of (kind, pos, pole) resolved THIS tick."""
        self.tick_no += 1
        self._tick_sleeping = sleeping
        contrib = {}   # npc.id -> list of (signed_push, source_has_zealot)
        def add(x, push, zsrc=False):
            contrib.setdefault(x.id, []).append((push, zsrc))
        # passive gating: schema 2.2 (G14) = pulls every tick, awake scaled; decay sleep-only
        if AWAKE_MULT is not None:
            do_passive = True
            pull_scale = 1.0 if sleeping else AWAKE_MULT
            do_decay = sleeping
        else:
            do_passive = sleeping or AWAKE_PULL
            pull_scale = 1.0
            do_decay = do_passive
        for t in self.tribes:
            if t.zealotless:
                # H-10: zealot-less regulars drift toward the player's emotion while awake
                if do_passive and not sleeping:
                    for x in self.npcs:
                        if x.tribe == t.idx and not x.zealot and not x.burn and not x.absorbing:
                            add(x, PULL*(AWAKE_MULT or 0.3)*self.player_pole*self.eff_mult(x, self.player_pole), False)
                continue
            _z = next((x for x in self.npcs if x.tribe==t.idx and x.zealot), None)
            if _z is None:
                t.zealotless = True; continue
            rad = self.sphere(t); zpos = _z.pos
            # schema 3.7.1: a zealot standing on an ENEMY-colored road pulls at a damped rate
            zdamp = 1.0
            if ROADALLEG and ROADALLEG.get('enabled'):
                _rp = self.road_pole.get(tuple(zpos))
                if _rp is not None and _rp == -t.pole:
                    zdamp = ROADALLEG.get('zealot_pull_damp_on_enemy_road', 0.5)
            zp = PULL * zdamp
            for x in self.npcs:
                if not do_passive: break
                if x.zealot or x.burn or x.absorbing: continue
                d = cheb(x.pos, zpos)
                if d <= rad:
                    if x.tribe == t.idx:
                        add(x, zp*pull_scale*t.pole*self.eff_mult(x, t.pole), True)
                    elif x.tribe == LONER:
                        # a wanderer in a sphere: an uncommitted nomad (never aligned) is CLAIMED at full
                        # pull; an ex-believer exile only feels the weaker overlap (it must be re-won)
                        _lp = zp if not x.ever_nonzero else OVERLAP
                        add(x, _lp*pull_scale*t.pole*self.eff_mult(x, t.pole), False)
                    elif t.pole == self.tribes[x.tribe].pole:
                        # H-9: same-pole neighboring zealot COMPOUNDS (canon: merging tribes
                        # compounds zealot influence) — full zealot pull, flagged as zealot source
                        add(x, zp*pull_scale*t.pole*self.eff_mult(x, t.pole), True)
                    else:
                        add(x, OVERLAP*pull_scale*t.pole*self.eff_mult(x, t.pole), False)
        # auras: beacons always; sleep aura only while sleeping
        for (bp, bpole) in self.beacons:
            for x in self.npcs:
                if x.zealot or x.burn: continue
                if cheb(x.pos, bp) <= BEAC_R:
                    add(x, BEAC_PUSH*bpole*self.eff_mult(x, bpole), False)
        if sleeping:
            for x in self.npcs:
                if x.zealot or x.burn: continue
                if cheb(x.pos, self.player_pos) <= self.aura_r:   # schema 3.8 ascension-scaled sleep aura
                    add(x, SLEEP_PUSH*self.player_pole*self.eff_mult(x, self.player_pole), False)
        # ---- schema 3.8.1 PEER CONTAGION: neighbours infect each other (hope/fear/apathy spread) ----
        if CONTAGION and CONTAGION.get('enabled') and do_passive:
            cr = CONTAGION.get('radius_tiles', 2); cs = CONTAGION.get('strength_per_neighbor', 0.10)
            mx = CONTAGION.get('max_push', 0.7); ap = CONTAGION.get('apathy_spreads', True)
            for x in self.npcs:
                if x.zealot or x.burn or x.absorbing: continue
                hf = 0.0; grey = 0
                for y in self.npcs:
                    if y is x or y.zealot or y.burn: continue
                    if cheb(x.pos, y.pos) <= cr:
                        if y.I > 0: hf += cs
                        elif y.I < 0: hf -= cs
                        else: grey += 1
                if ap and grey and x.v != 0.0: hf += -math.copysign(cs*grey, x.v)   # apathy drags toward 0
                if hf != 0.0:
                    hf = max(-mx, min(mx, hf))
                    add(x, hf*pull_scale, False)
        # actions
        for (kind, pos, pole) in actions:
            if kind == 'flame':
                _fr = self.flame_r   # schema 3.8 ascension-scaled flame radius
                for x in self.npcs:
                    if x.zealot: continue
                    if cheb(x.pos, pos) <= _fr:
                        if x.burn:
                            if x.I*pole < 0:  # opposing valence -> save
                                x.burn = False
                                x.v = float(int(x.burn_frozen*SAVE_F))
                                if x.v == 0.0: x.ever_nonzero = True
                        else:
                            add(x, FLAME_PUSH*pole*self.eff_mult(x, pole), False)
                self.wake_entries.append(FLAME_PUSH*pole*sum(1 for x in self.npcs if not x.zealot and not x.burn and cheb(x.pos,pos)<=_fr))
            elif kind == 'roar':
                for x in self.npcs:
                    if x.zealot: continue
                    if cheb(x.pos, pos) <= ROAR_R:
                        if x.burn and x.I > 0:   # hope-burned -> save
                            x.burn = False
                            nv = x.burn_frozen*SAVE_F
                            x.v = float(int(nv)); x.ever_nonzero = x.ever_nonzero or x.v==0.0
                        elif not x.burn:
                            add(x, -ROAR_PUSH*self.eff_mult(x, -1), False)
                self.wake_entries.append(-ROAR_PUSH*sum(1 for x in self.npcs if not x.zealot and not x.burn and cheb(x.pos,pos)<=ROAR_R))
            elif kind == 'raze':
                for x in self.npcs:
                    if x.zealot or x.burn: continue
                    if cheb(x.pos, pos) <= RAZE['witness_radius_tiles']:
                        add(x, -RAZE['fear_push_per_witness']*self.eff_mult(x, -1), False)
                self.wake_entries.append(-RAZE['fear_push_per_witness']*sum(1 for x in self.npcs if not x.zealot and not x.burn and cheb(x.pos,pos)<=RAZE['witness_radius_tiles']))
            elif kind == 'wait':
                for x in self.npcs:
                    if x.zealot or x.burn or x.absorbing: continue
                    if cheb(x.pos, pos) <= WAIT_R and x.I != 0:
                        add(x, -math.copysign(WAIT_PUSH, x.v), False)  # toward 0
        # sleep/beacon aura entries also count toward intent (per v2 intent measure)
        if sleeping:
            n_in = sum(1 for x in self.npcs if not x.zealot and not x.burn and cheb(x.pos,self.player_pos)<=SLEEP_R)
            self.wake_entries.append(SLEEP_PUSH*self.player_pole*n_in)
        for (bp,bpole) in self.beacons:
            n_in = sum(1 for x in self.npcs if not x.zealot and not x.burn and cheb(x.pos,bp)<=BEAC_R)
            self.wake_entries.append(BEAC_PUSH*bpole*n_in)
        # resolve: burnout then movement
        dom = self.dominance()
        decay_eff = DECAY*(1 + 1*dom + IDLE_CO*max(0, self.idle_sleeps-1))
        # schema 3.9: inside an active grief front the dominance term is REPLACED by
        # front_strength (no double-punishment); outside is exactly the live formula.
        # Zealots immune (they never reach the decay branch); everything else about decay
        # semantics (toward 0, absorbing-skip, sign-flip clamp) is unchanged.
        _gf_c = None; _gf_decay = decay_eff
        # schema 3.10 variant C: local decay zone around the temple. ADDS well_strength to the
        # dominance term (the front REPLACES it; an active front takes precedence inside its
        # own radius, so no NPC is ever under both). Default-off.
        _tw_decay = None
        if TWELL_ON:
            _tw_r = TWELL.get('radius_tiles', 8)
            _tw_decay = DECAY*(1 + 1*dom + TWELL.get('strength', 1.0) + IDLE_CO*max(0, self.idle_sleeps-1))
            _tw_dom_only = TWELL.get('affects_dominant_pole_only', True)
        if UHT_ON and self.front is not None:
            _gf_c = tuple(self.front['center']); _gf_r = GF.get('radius_tiles', 6)
            _gf_decay = DECAY*(1 + GF.get('front_strength', 1.6) + IDLE_CO*max(0, self.idle_sleeps-1))
            _gf_dom_only = GF.get('affects_dominant_pole_only', False)   # schema 3.9.1
        for x in self.npcs:
            if x.zealot or x.burn: continue
            entries = contrib.get(x.id, [])
            if x.I != 0:
                pole = 1 if x.I > 0 else -1
                same = sum(p for (p,_) in entries if p*pole > 0)
                if abs(same) >= Y:
                    x.burn = True; x.burn_frozen = x.v; x.burn_sleeps = 0
                    if not any(z for (p,z) in entries if p*pole > 0 and z):
                        if pole == self.player_pole: self.selfburn_nozealot += 1
                    self.log_burns.append((self.sleep_no, x.id))
                    continue
            net_p = sum(p for (p,_) in entries)
            decay_term = 0.0
            # decay toward 0 (not for absorbing; newborn at exactly 0 has nothing to decay)
            if do_decay and not x.absorbing and x.v != 0.0:
                _de = decay_eff
                if _gf_c is not None and cheb(x.pos, _gf_c) <= _gf_r:   # schema 3.9
                    if x.zealot:
                        self.front_zealot_decays += 1   # unreachable (zealot loop-skip); audit only
                    elif (not _gf_dom_only) or x.I*self.player_pole >= 1:
                        # schema 3.9.1: dom-only gate — grief wears the WINNER; enemies and
                        # greys inside the radius take the normal formula (the branch below
                        # is simply not entered for them, so front_offpole_decays stays 0
                        # by construction; the counter exists as the audit witness).
                        if _gf_dom_only and x.I*self.player_pole < 1:
                            self.front_offpole_decays += 1   # unreachable; audit only
                        _de = _gf_decay
                        # exposure metric: 1/T_SLEEP per front-decayed sleeping tick, so one
                        # full-generation membership sums to 1.0 NPC-sleep
                        if sleeping:
                            self.front_exposure_npc_sleeps += 1.0/T_SLEEP
                            self.front['expo'] = self.front.get('expo', 0.0) + 1.0/T_SLEEP
                elif _tw_decay is not None and cheb(x.pos, self.temple_pos) <= _tw_r:   # schema 3.10 C
                    if (not _tw_dom_only) or x.I*self.player_pole >= 1:
                        _de = _tw_decay
                        if sleeping: self.well_exposure_npc_sleeps += 1.0/T_SLEEP
                decay_term = -math.copysign(_de, x.v)
            dv = max(-STEP, min(STEP, net_p + decay_term))
            newv = x.v + dv
            if x.v != 0.0 and newv * x.v < 0:
                # sign flip: legitimate only if pressure alone (capped) flips it;
                # decay may carry a value TO 0, never through it (canon: toward 0)
                dv_p = max(-STEP, min(STEP, net_p))
                if (x.v + dv_p) * x.v >= 0:
                    newv = 0.0
            was = x.I
            x.v = max(-ZVAL+0.001, min(ZVAL-0.001, newv))
            if abs(x.I) >= 1:
                x.ever_nonzero = True
                if (not WINDOW_CUM) or abs(x.I) >= STABLE_ABS: x.zero_ticks = 0
            else: x.zero_ticks += 1
            if was != 0 and x.I == 0: x.ever_nonzero = True
        # trim intent window (H-3): current wake + previous sleep
        self.check_terminals()

    def intent_S(self):
        return sum(self.wake_entries) + sum(v for (_,v) in self.intent)

    def check_terminals(self):
        if self.terminal: return
        # schema 3.6 genesis grace: no win/loss until the world has taken shape (a tribe settled,
        # or the aligned fraction crossed the formed threshold). No-op once formed / for legacy start.
        if not self.formed:
            aligned = sum(1 for x in self.npcs if not x.burn and abs(x.I) >= 1)
            if any(t.settled for t in self.tribes) or aligned/max(self.pop(),1) >= FORMED_FRAC:
                self.formed = True
            else:
                return
        pop = self.pop()
        wf = self.win_count()/pop; lf = self.loss_count()/pop
        self.max_wf = max(self.max_wf, wf)
        S = self.intent_S()
        # win check: skipped (pauses hold) unless |S|>=gate and sign matches counted pole
        if abs(S) >= S_GATE:
            pole = 1 if S > 0 else -1
            if pole == self.player_pole and wf >= THRESH:
                self.win_hold += 1
                if getattr(self, '_tick_sleeping', False): self.win_hold_sleepticks += 1
            elif pole == self.player_pole:
                self.win_hold = 0; self.win_hold_sleepticks = 0
            # opposing-pole S: win check counts that pole; scripted bots never win off-pole; treat as pause
        # else: skipped tick pauses (no reset)
        if lf >= THRESH: self.loss_hold += 1
        else: self.loss_hold = 0
        win_ok = self.win_hold >= HOLD and (not HOLD_SPAN_GEN or self.win_hold_sleepticks >= T_SLEEP)
        _wnf = WL.get('requires_no_living_opposing_zealot', False) or __import__('os').environ.get('WIN_NEEDS_FATE','0') == '1'
        if win_ok and _wnf:
            for x in self.npcs:
                if x.zealot and x.I * self.player_pole < 0: win_ok = False; break
        loss_ok = self.loss_hold >= HOLD
        if TEMPLE_TERM:
            # schema 3.10: two-phase win. The hold ARMS (once; a broken hold does not disarm
            # unless disarm_if_hold_breaks), the avatar entering the temple FIRES. The loss
            # check is untouched and stays live while armed — the walk can be lost, and a
            # same-tick tie still goes to the loss (tie_priority).
            if win_ok and not self.win_armed:
                self.win_armed = True; self.win_armed_sleep = self.sleep_no
            elif self.win_armed and TENTRY.get('disarm_if_hold_breaks', False) and self.win_hold == 0:
                self.win_armed = False; self.win_armed_sleep = None
            fire = self.win_armed and self.in_temple(self.player_pos)
            if TIE_LOSS and loss_ok: self.terminal = ('loss', self.sleep_no)
            elif fire: self.terminal = ('win', self.sleep_no)
            elif loss_ok: self.terminal = ('loss', self.sleep_no)
            return
        if TIE_LOSS and loss_ok:
            # schema 3.9 (v0.9.1): tie_priority=loss — if win and loss complete on the same
            # tick the loss fires. (Legacy code below gave the WIN the tie; flipped when ruled.)
            self.terminal = ('loss', self.sleep_no)
        elif win_ok: self.terminal = ('win', self.sleep_no)
        elif loss_ok: self.terminal = ('loss', self.sleep_no)

    # ---------- schema 3.4 movement helpers ----------
    def _nearest_road(self, c, sight):
        """closest road tile within Chebyshev `sight` of point c, or None."""
        best, bd = None, sight + 1
        for r in self.roads:
            d = cheb(c, r)
            if d < bd: bd, best = d, r
        return best

    def _road_target(self, c, home, sight, pole=None):
        """schema 3.4 road-following target: among road tiles within `sight` of c, the one
        FARTHEST from home. schema 3.7.2: a tribe only follows roads of its OWN color (or neutral) —
        so a fear band won't be misguided by a green trade corridor (it still erodes crossing it)."""
        cand = [r for r in self.roads if cheb(c, r) <= sight
                and (pole is None or self.road_pole.get(r, pole) == pole)]
        if not cand: return None
        # farthest-from-home, tie-broken by nearest-to-current (smooth stepping)
        return max(cand, key=lambda r: (cheb(r, home), -cheb(r, c)))

    def _step_toward(self, c, tgt, step):
        """one unit heading (dx,dy) in {-1,0,1}^2 pointing from c toward tgt."""
        sx = (tgt[0] > c[0]) - (tgt[0] < c[0])
        sy = (tgt[1] > c[1]) - (tgt[1] < c[1])
        return (sx, sy)

    def _drift_center(self, t, step, box):
        """compute a tribe's next center. Strong road-following (schema 3.4): if a road is
        within sight, steer toward/along it (leaving the home box when leave_box_on_road);
        otherwise random cohesive drift bounded to the home box (schema 3.3 behavior)."""
        rf = ROAD_FOLLOW if (ROAD_FOLLOW and ROAD_FOLLOW.get('enabled') and self.roads) else None
        if getattr(t, 'rout_from', None) is not None:
            # routing: flee directly away from the enemy that beat us, clear of its sphere
            # in one move (overrides road-follow and the home box)
            e = t.rout_from; fd = getattr(t, 'rout_dist', step) or step
            t.rout_from = None; t.rout_dist = None
            h = (-((e[0] > t.center[0]) - (e[0] < t.center[0])),
                 -((e[1] > t.center[1]) - (e[1] < t.center[1])))
            if h == (0, 0):
                # enemy is on top of us (fully overlapped): scatter deterministically by tribe id
                h = [(1,0),(-1,0),(0,1),(0,-1)][t.idx % 4]
            t.heading = h
            nc = [t.center[0] + h[0]*fd, t.center[1] + h[1]*fd]
            for i in (0, 1): nc[i] = max(0, min(MAP-1, nc[i]))
            return nc, True   # rout ignores the box
        if rf:
            road = self._road_target(tuple(t.center), tuple(t.home), rf.get('road_sight_tiles', 6))   # follow ANY road (lure)
            if road is not None and tuple(t.center) != road:
                h = self._step_toward(t.center, road, step)
                t.heading = h
                nc = [t.center[0] + h[0]*step, t.center[1] + h[1]*step]
                leave = rf.get('leave_box_on_road', True)
                for i in (0, 1):
                    if not leave and abs(nc[i] - t.home[i]) > box:
                        nc[i] = t.center[i]
                    nc[i] = max(0, min(MAP-1, nc[i]))
                return nc, leave
        # random cohesive drift within the home box (schema 3.3)
        dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]
        if t.heading == (0,0) or self.wrng.random() < 0.34:
            t.heading = dirs[self.wrng.randrange(8)]
        nc = [t.center[0] + t.heading[0]*step, t.center[1] + t.heading[1]*step]
        for i in (0,1):
            if abs(nc[i] - t.home[i]) > box:
                h = list(t.heading); h[i] = -h[i]; t.heading = tuple(h)
                nc[i] = t.center[i] + t.heading[i]*step
            nc[i] = max(0, min(MAP-1, nc[i]))
        return nc, False

    def _shift_tribe(self, t, dx, dy):
        for x in self.npcs:
            if x.tribe == t.idx:
                x.pos = (max(0,min(MAP-1,x.pos[0]+dx)), max(0,min(MAP-1,x.pos[1]+dy)))
        t.center = [t.center[0]+dx, t.center[1]+dy]

    def lay_road(self, a, b, pole):
        """lay a road line a->b stamped with `pole` (schema 3.7.1 allegiance)."""
        steps = cheb(a, b)
        for i in range(steps+1):
            f = i/steps if steps else 0
            x = round(a[0]+(b[0]-a[0])*f); y = round(a[1]+(b[1]-a[1])*f)
            self.roads.add((x,y))
            if ROADALLEG and ROADALLEG.get('enabled'):
                self.road_pole[(x,y)] = pole
                self.road_str[(x,y)] = ROADALLEG.get('initial_strength', 3)

    # ---------- schema 3.4: faction fights (real casualties + rout) ----------
    def _resolve_fights(self):
        if not (FIGHT and FIGHT.get('enabled')): return
        rate = FIGHT.get('casualty_rate', 0.2); mn = FIGHT.get('min_casualty_per_side', 1)
        ratio = FIGHT.get('rout_if_contested_strength_ratio_below', 0.5)
        settled_stand = FIGHT.get('settled_tribes_stand', True)
        live = [t for t in self.tribes if not t.zealotless]
        zof = {}
        for t in live:
            z = next((x for x in self.npcs if x.tribe==t.idx and x.zealot), None)
            if z is not None: zof[t.idx] = z
        kills = []   # (npc, enemy_center) to remove after scanning
        bp_done = set()   # ids already battle-pressured this resolve (avoid double in 3-way overlaps)
        for i in range(len(live)):
            for j in range(i+1, len(live)):
                a, b = live[i], live[j]
                if a.pole == b.pole: continue           # only rivals fight
                za, zb = zof.get(a.idx), zof.get(b.idx)
                if za is None or zb is None: continue
                ra, rb = self.sphere(a), self.sphere(b)
                if cheb(za.pos, zb.pos) > ra + rb: continue   # spheres don't overlap -> no fight
                # contested = non-zealot, non-burn members inside the ENEMY sphere
                ca = [x for x in self.npcs if x.tribe==a.idx and not x.zealot and not x.burn and cheb(x.pos, zb.pos) <= rb]
                cb = [x for x in self.npcs if x.tribe==b.idx and not x.zealot and not x.burn and cheb(x.pos, za.pos) <= ra]
                if not ca or not cb: continue   # a fight needs LIVE combatants on BOTH sides
                # each side kills weakest-first of the other, proportional to its own contested strength
                da = min(len(cb), max(mn if cb else 0, round(rate*len(ca))))
                db = min(len(ca), max(mn if ca else 0, round(rate*len(cb))))
                for x in sorted(cb, key=lambda x: abs(x.I))[:da]: kills.append(x)
                for x in sorted(ca, key=lambda x: abs(x.I))[:db]: kills.append(x)
                # rout: the outnumbered UNSETTLED tribe flees the enemy zealot
                # after a clash, unsettled combatants RECOIL clear of the enemy sphere — a fight is a
                # punctuated skirmish, not a grind-to-death. The outnumbered side flees farther (a true
                # rout). Settled tribes stand and bleed. The player must keep forcing contact (roads)
                # to grind a tribe down — casualties are a deliberate cost, not an accident that wipes.
                sa, sb = len(ca), len(cb)
                if not (a.settled and settled_stand):
                    a.rout_from = list(zb.pos); a.rout_dist = rb + (4 if sa < ratio*max(sb,1) else 2)
                if not (b.settled and settled_stand):
                    b.rout_from = list(za.pos); b.rout_dist = ra + (4 if sb < ratio*max(sa,1) else 2)
                # ---- schema 3.5 battle pressure: Fear breaks / Hope bends ----
                if BP and BP.get('enabled'):
                    kill_ids = {x.id for x in kills}
                    contested = [x for x in (ca + cb) if x.id not in kill_ids and x.id not in bp_done]
                    def _depthf(x):  # 0 (shallow |1|) .. 1 (devout cap |11|)
                        return max(0.0, min(1.0, (abs(x.I) - 1) / max(1, DEV_HI - 1)))
                    hope_here = [x for x in (ca + cb) if x.v > 0]
                    opp_hope_df = (sum(_depthf(x) for x in hope_here) / len(hope_here)) if hope_here else 0.0
                    hx = BP.get('hope_exhaust_per_sleep', 1.0); hr = BP.get('hope_depth_resist', 0.5)
                    fd = BP.get('fear_deepen_per_sleep', 1.0);  fb = BP.get('fear_deepen_hope_bonus', 0.5)
                    for x in contested:
                        bp_done.add(x.id)
                        if x.v > 0:   # HOPE bends: exhaust toward 0, deep hope resists (never crosses 0)
                            drain = hx * (1.0 - hr * _depthf(x))
                            x.v = max(0.0, x.v - drain)
                            if x.I == 0: x.ever_nonzero = True
                        elif x.v < 0: # FEAR breaks: deepen toward -SPAN; burn out at the regular cap
                            deepen = fd * (1.0 + fb * opp_hope_df)
                            nv = x.v - deepen
                            if BP.get('fear_burnout_at_regular_cap', True) and nv <= -(SPAN - 1):
                                x.burn = True; x.burn_frozen = float(-(SPAN - 1)); x.burn_sleeps = 0
                                self.log_burns.append((self.sleep_no, x.id))
                            else:
                                x.v = max(-(ZVAL - 0.001), nv)
        seen = set()
        for x in kills:
            if x.id in seen: continue
            seen.add(x.id)
            if x in self.npcs:
                self.npcs.remove(x); self.fight_deaths += 1

    # ---------- sleep ----------
    def do_sleep(self):
        if self.stamina_spent_this_wake == 0:
            self.idle_sleeps += 1
        else:
            self.idle_sleeps = 0
        # H-9 (schema 3.10): the scripted bots know nothing about the temple. While the win is
        # armed the harness models the pilgrimage as a steady walk of harness_pilgrim_tiles_per_sleep
        # toward the temple, taken at the sleep boundary, uncosted (bots account their own stamina).
        # 0 disables it (a bot must walk itself). The pace is a DIAL for the Red-Teamer to attack.
        if TEMPLE_TERM and self.win_armed and not self.terminal:
            pace = int(TENTRY.get('harness_pilgrim_tiles_per_sleep', 6))
            if pace > 0 and not self.in_temple(self.player_pos):
                self._pilgrim_step(pace)
                self.check_terminals()   # entry can fire before the sleep ticks
        for _ in range(T_SLEEP):
            if self.terminal: break
            self.tick(sleeping=True)
        # snapshot settled state at generation entry: a member that burned out inside a settlement
        # exiles even if that same loss unsettles the camp this generation (schema 3.4 exile rule)
        _pre_settled = {t.idx: t.settled for t in self.tribes}
        # end of generation: births, timers, settling
        self.sleep_no += 1
        for x in self.npcs:
            if x.burn:
                x.burn_sleeps += 1
                if x.burn_sleeps >= X_SLP:
                    x.burn = False; x.v = 0.0; x.ever_nonzero = True
        for t in self.tribes:
            # schema 3.7: during genesis FORMATION no births (grow by recruiting nomads); after forming,
            # a tribe births only UP TO the schism pop_cap (giving hope its newborn replenishment) — a
            # full tribe schisms into a colony instead of ballooning. Total pop stays bounded by
            # max_tribes * pop_cap. Non-genesis is the tuned birth engine, unchanged.
            if GEN and GEN.get('enabled'):
                _cap = (SCHISM or {}).get('pop_cap', 14)
                _sz = sum(1 for x in self.npcs if x.tribe == t.idx and not x.zealot)
                n_births = N_GROW if (self.formed and _sz < _cap) else 0
            else:
                n_births = N_GROW
            for _ in range(n_births):
                off = (t.center[0]+self.rng.randint(-2,2), t.center[1]+self.rng.randint(-2,2))
                self.npcs.append(NPC(t.idx, off, 0))
            members = [x for x in self.npcs if x.tribe == t.idx]
            avg = sum((0 if x.burn else x.I) for x in members)/len(members)
            nonz = sum(1 for x in members if not x.zealot)   # schema 3.6: follower count
            if not t.settled:
                if abs(avg) >= SETTLE_ABS and nonz >= MIN_SETTLE:   # a tribe needs real followers to settle
                    t.hold_ctr += 1
                    if t.hold_ctr >= SETTLE_HOLD:
                        t.settled = True; t.settle_pole = 1 if avg > 0 else -1
                else: t.hold_ctr = 0
            else:
                if abs(avg) < SETTLE_ABS:
                    t.unsettle_ctr += 1
                    if t.unsettle_ctr >= UNSETTLE_HOLD:
                        t.settled = False; t.settle_pole = 0; t.unsettle_ctr = 0
                else: t.unsettle_ctr = 0
        # ---- schema 3.7 SCHISM: a full, devout settlement throws a same-pole colony ----
        # Bounds every settlement to a convertible size and spreads the world by colonization
        # rather than ballooning. Symmetric (both poles), total tribe count capped at max_tribes.
        if SCHISM and SCHISM.get('enabled'):
            cap = SCHISM.get('pop_cap', 14); dth = SCHISM.get('devout_threshold_abs', 8)
            frac = SCHISM.get('daughter_takes_fraction', 0.5); rad = SCHISM.get('fission_radius_tiles', 10)
            maxt = SCHISM.get('max_tribes', 7)
            for t in list(self.tribes):
                if len(self.tribes) >= maxt: break
                if not t.settled: continue
                mem = [x for x in self.npcs if x.tribe==t.idx and not x.zealot and not x.burn]
                if len(mem) < cap: continue
                avg = sum(x.I for x in mem)/len(mem)
                if abs(avg) < dth: continue
                # found the colony: migrate a fixed radius away in an open direction, settle it
                dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
                dx, dy = dirs[self.wrng.randrange(8)]
                dc = [max(0,min(MAP-1,t.center[0]+dx*rad)), max(0,min(MAP-1,t.center[1]+dy*rad))]
                didx = len(self.tribes)
                dt = Tribe(didx, dc, t.pole); dt.home = list(dc)
                dt.settled = True; dt.settle_pole = t.settle_pole
                self.tribes.append(dt)
                self.npcs.append(NPC(didx, tuple(dc), ZVAL*t.pole, zealot=True))
                take = mem[len(mem)-int(len(mem)*frac):]   # daughter takes ~half the flock
                for x in take:
                    x.tribe = didx
                    x.pos = (max(0,min(MAP-1,dc[0]+self.rng.randint(-2,2))), max(0,min(MAP-1,dc[1]+self.rng.randint(-2,2))))
                if not hasattr(self, 'schisms'): self.schisms = []
                self.schisms.append((self.sleep_no, t.idx, didx, t.pole))
        # zealot_fate (schema 3, G18-1): generation-boundary check, settling cadence
        if ZFATE is not None:
            if not hasattr(self, 'fate_events'): self.fate_events = []
            for t in self.tribes:
                if t.zealotless: continue
                z = next((x for x in self.npcs if x.tribe==t.idx and x.zealot), None)
                if z is None: continue
                mem = [x for x in self.npcs if x.tribe==t.idx and not x.zealot]
                if not mem: continue
                vals = []
                for x in mem:
                    if x.burn: vals.append(0)
                    elif x.I == 0:
                        if ZFATE.get('average_excludes_window_zeros') and READOPT_W is not None and x.zero_ticks < READOPT_W:
                            continue   # schema 3.2: in-window zeros excluded from the fate average
                        vals.append(0)
                    else: vals.append(x.I)
                if not vals: continue
                avg = sum(vals)/len(vals)
                zpole = 1 if z.I > 0 else -1
                if avg*(-zpole) >= ZFATE['trigger_tribe_average_opposite_min_abs']:
                    t.fate_ctr += 1
                else:
                    t.fate_ctr = 0
                _fire = None
                _ce = ZFATE.get('convert_eval')
                if _ce is not None:
                    _key = 'fear_zealot' if zpole < 0 else 'hope_zealot'
                    _b2 = _ce['at_check2_if_avg_abs_gte'][_key]
                    _b3 = _ce['at_check3_if_avg_abs_gte'][_key]
                    if getattr(t, 'fate_deferred', False):
                        # deferred fate decides at this check regardless
                        _fire = 'convert' if (_b3 is not None and abs(avg) >= _b3) else 'expel'
                        t.fate_deferred = False
                    elif t.fate_ctr >= ZFATE['trigger_hold_generations']:
                        if _b2 is not None and abs(avg) >= _b2:
                            _fire = 'convert'
                        elif _b2 is not None and abs(avg) >= _ce['defer_to_check3_if_check2_avg_abs_gte']:
                            t.fate_deferred = True   # decision deferred one generation
                        else:
                            _fire = 'expel'   # incl. declared expel-only targets (bar None)
                elif t.fate_ctr >= ZFATE['trigger_hold_generations']:
                    _bar = ZFATE['convert_if_tribe_average_abs_gte']
                    if isinstance(_bar, dict):
                        _bar = _bar['fear_zealot'] if zpole < 0 else _bar['hope_zealot']
                    _fire = 'convert' if abs(avg) >= _bar else 'expel'
                if _fire == 'convert':
                    z.v = float(-zpole*ZVAL); t.pole = -zpole
                    self.fate_events.append((self.sleep_no, t.idx, 'convert'))
                    t.fate_ctr = 0
                elif _fire == 'expel':
                    self.npcs.remove(z); t.zealotless = True
                    self.fate_events.append((self.sleep_no, t.idx, 'expel'))
                    t.fate_ctr = 0
        # ---- schema 3.4: settlement exile — burnout is the ONLY exit from a settlement ----
        # A settled tribe roots (it no longer wanders and cannot be led out). When one of its
        # members burns out, the broken NPC detaches as a lone wanderer (tribe = LONER); it keeps
        # its burn state (recovers to 0 on its own timer) and drifts until a sphere re-adopts it.
        if EXILE and EXILE.get('enabled') and EXILE.get('detach_on_burnout_if_settled', True):
            for t in self.tribes:
                if not _pre_settled.get(t.idx): continue
                for x in self.npcs:
                    if x.tribe == t.idx and x.burn and not x.zealot:
                        x.tribe = LONER; self.exiles += 1
        # ---- schema 3.4: faction fights (real casualties + rout) — before movement ----
        self._resolve_fights()
        # ---- nomadic drift (schema 3.3 + 3.4 road-following): unsettled tribes migrate ----
        # Cohesive rigid-body shift (intra-tribe distances preserved -> belief-neutral for the
        # tribe's own dynamics). schema 3.4: strong road-following steers the body onto/along
        # player-laid roads (leaving the home box when on a road); routing overrides toward flight.
        if WANDER and WANDER.get('enabled'):
            box = WANDER.get('home_box_tiles', 6); step = WANDER.get('step_tiles_per_sleep', 1)
            for t in self.tribes:
                if t.settled: continue
                nc, _free = self._drift_center(t, step, box)
                dx, dy = nc[0]-t.center[0], nc[1]-t.center[1]
                if dx or dy: self._shift_tribe(t, dx, dy)
            # ---- loner drift: roads first, else SEEK the nearest conviction (a wanderer drawn to belong) ----
            lstep = (EXILE or {}).get('loner_step_tiles_per_sleep', 1) if EXILE else 0
            lroad = (EXILE or {}).get('loner_follows_roads', True) if EXILE else False
            zpos = [next((zz.pos for zz in self.npcs if zz.tribe==t.idx and zz.zealot), None) for t in self.tribes]
            zpos = [p for p in zpos if p is not None]
            for x in self.npcs:
                if x.tribe != LONER: continue
                road = self._nearest_road(x.pos, ROAD_FOLLOW.get('road_sight_tiles', 6)) if (lroad and ROAD_FOLLOW and ROAD_FOLLOW.get('enabled') and self.roads) else None
                if road is not None and x.pos != road:
                    h = self._step_toward(x.pos, road, lstep)
                elif zpos and self.wrng.random() < 0.8:
                    tgt = min(zpos, key=lambda p: cheb(x.pos, p))   # drift toward the nearest zealot (gather)
                    h = self._step_toward(x.pos, tgt, lstep)
                else:
                    d = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]
                    h = d[self.wrng.randrange(8)]
                x.pos = (max(0,min(MAP-1,x.pos[0]+h[0]*lstep)), max(0,min(MAP-1,x.pos[1]+h[1]*lstep)))
        # ---- loner recruitment / re-adoption inside a sphere ----
        # schema 3.6: an uncommitted grey nomad that wanders into a zealot's sphere is CLAIMED —
        # aligned to that pole at tentative belief and folded into the tribe (the zealot gathers it).
        # schema 3.4: an ex-believer exile only re-adopts once it's been pulled back to |I|>=abs.
        if EXILE and EXILE.get('enabled'):
            radopt = EXILE.get('readopt_on_stable_adoption_abs', 2)
            for x in self.npcs:
                if x.tribe != LONER or x.burn: continue
                nomad = not x.ever_nonzero
                if not nomad and abs(x.I) < radopt: continue
                best, bd = None, 10**9
                for t in self.tribes:
                    if t.zealotless: continue
                    z = next((zz for zz in self.npcs if zz.tribe==t.idx and zz.zealot), None)
                    if z is None: continue
                    d = cheb(x.pos, z.pos)
                    if d <= self.sphere(t) and d < bd: bd, best = d, t
                if best is not None:
                    if nomad:   # claim the uncommitted wanderer at tentative belief; it joins the CLUSTER
                        x.v = float(2*best.pole); x.ever_nonzero = True
                        x.pos = (max(0,min(MAP-1,best.center[0]+self.rng.randint(-2,2))),
                                 max(0,min(MAP-1,best.center[1]+self.rng.randint(-2,2))))
                    x.tribe = best.idx; self.readoptions += 1
        # ---- schema 3.7.1 ROAD ALLEGIANCE: an opposing NPC on your road loses conviction (toward grey)
        # and grinds the road down; worn to grey it detaches as a re-recruitable wanderer. ----
        if ROADALLEG and ROADALLEG.get('enabled'):
            erode = ROADALLEG.get('erode_per_sleep', 1.0); wear = ROADALLEG.get('wear_per_crossing', 1)
            detach = ROADALLEG.get('detach_to_loner_on_zero', True)
            for x in self.npcs:
                if x.zealot or x.burn: continue
                tile = tuple(x.pos); rp = self.road_pole.get(tile)
                if rp is not None and x.v * rp < 0:      # an enemy of the road's pole is standing on it
                    x.v = math.copysign(max(0.0, abs(x.v) - erode), x.v)
                    self.road_str[tile] = self.road_str.get(tile, 0) - wear
                    if self.road_str[tile] <= 0:
                        self.road_pole.pop(tile, None); self.road_str.pop(tile, None); self.roads.discard(tile)
                    if detach and x.I == 0:              # worn to grey -> uncommitted wanderer, re-recruitable
                        x.tribe = LONER; x.ever_nonzero = False; x.zero_ticks = 0
        # ---- schema 3.7.2 HOPE TRADE: hope colonies refresh green corridors between each other ----
        # Hope's passive spread & identity: trade keeps the road network green (self-reinforcing), and
        # green corridors erode+reclaim any fear that crosses them. Hope builds; Fear conquers.
        if HOPE_TRADE and HOPE_TRADE.get('enabled') and ROADALLEG and ROADALLEG.get('enabled'):
            hcol = [t for t in self.tribes if t.settled and t.settle_pole > 0]
            if len(hcol) >= HOPE_TRADE.get('min_colonies', 2):
                crad = HOPE_TRADE.get('connect_radius_tiles', 28)
                for a in hcol:
                    others = [b for b in hcol if b is not a]
                    b = min(others, key=lambda b: cheb(a.center, b.center))
                    if cheb(a.center, b.center) <= crad:
                        self.lay_road(tuple(a.center), tuple(b.center), 1)   # green trade route, refreshed
        self._uhtcearu_events()  # schema 3.9: grief-front scheduler (after births/settling —
                                 # reads the fully post-generation world)
        self.recompute_power()   # schema 3.8: level up at sleep (power tier = f(flock size))
        # roll intent window: previous-sleep entries = this wake's + this sleep's
        self.intent = deque((0,v) for v in self.wake_entries)
        self.wake_entries = []
        self.stamina_spent_this_wake = 0.0

    # ---------- schema 3.9: Uhtcearu Grief Front (Variant A, Run 23) ----------
    def _uhtcearu_events(self):
        """Sleep-boundary scheduler. Active front: crawl move_tiles_per_sleep toward the
        largest dominant-pole tribe (most non-burn members with I*player_pole >= 1; fall back
        to any tribe of the player's pole; if none, don't move), then age; on expiry start the
        cooldown. No front: tick the cooldown down; once cooled, if dominance >= trigger,
        condense a front at the tile centroid (rounded) of dominant-pole NPCs. Dominance
        source = the same player-pole fraction self.dominance() the damping formula reads
        (packet rebind). enabled=false -> this is a no-op (bit-identical to v3.7)."""
        if not UHT_ON: return
        p = self.player_pole
        # schema 3.9.1: dominance sampled at EVERY boundary; the trigger reads the max over
        # the trailing trigger_trailing_window_sleeps boundaries (deque maxlen; absent field
        # -> maxlen 1 -> max == current sample == exact v3.9 trigger).
        self.dom_hist.append(self.dominance())
        if self.front is not None:
            best = self._gf_largest_tribe(p)
            if best is not None:
                step = GF.get('move_tiles_per_sleep', 1)
                c = self.front['center']
                # per-axis clamp to the remaining distance: identical to the 3.9.1 unit-heading
                # step at step=1; at step>1 (schema 3.10 travel) it stops a front overshooting
                # and oscillating around its target.
                dx = max(-step, min(step, best.center[0] - c[0])); dy = max(-step, min(step, best.center[1] - c[1]))
                self.front['center'] = [max(0, min(MAP-1, c[0]+dx)), max(0, min(MAP-1, c[1]+dy))]
            # schema 3.10: a temple-spawned front with duration_counts_from 'arrival' does not
            # age until it is within arrival_radius_tiles of its target (or max_travel_sleeps
            # have elapsed — a front never hangs). Absent fields -> ages from spawn, as 3.9.1.
            if 'travel' in self.front and not self.front.get('arrived', False):
                self.front['travel'] += 1
                near = best is not None and cheb(self.front['center'], best.center) <= GF.get('arrival_radius_tiles', 1)
                if near or self.front['travel'] >= GF.get('max_travel_sleeps', 6):
                    self.front['arrived'] = True
                    self.front_travel_sleeps.append(self.front['travel'])
                else:
                    return   # still travelling: no ageing this boundary
            self.front['sleeps_left'] -= 1
            if self.front['sleeps_left'] <= 0:
                self.front_events.append((self.sleep_no, 'expire', tuple(self.front['center'])))
                self.front_expo_log.append(round(self.front.get('expo', 0.0), 2))
                self.front = None
                self.front_cooldown = GF.get('cooldown_sleeps_after_expiry', 2)
        else:
            if self.front_cooldown > 0: self.front_cooldown -= 1
            if self.front_cooldown == 0 and max(self.dom_hist) >= GF.get('trigger_dominance_min', 0.55):
                c = None
                if GF.get('spawn_at') == 'temple_position' and TEMPLE_ON:        # schema 3.10
                    c = (int(self.temple_pos[0]), int(self.temple_pos[1]))
                elif GF.get('spawn_at') == 'largest_dominant_pole_tribe_position':  # schema 3.9.1
                    t = self._gf_largest_tribe(p)
                    if t is not None:
                        c = (int(round(t.center[0])), int(round(t.center[1])))
                else:   # v3.9 default: tile centroid of dominant-pole NPCs
                    dom_npcs = [x for x in self.npcs if not x.burn and x.I*p >= 1]
                    if dom_npcs:
                        c = (round(sum(x.pos[0] for x in dom_npcs)/len(dom_npcs)),
                             round(sum(x.pos[1] for x in dom_npcs)/len(dom_npcs)))
                if c is not None:
                    self.front = {'center': [c[0], c[1]], 'sleeps_left': GF.get('duration_sleeps', 3)}
                    if GF.get('spawn_at') == 'temple_position' and TEMPLE_ON and GF.get('duration_counts_from', 'spawn') == 'arrival':
                        self.front['travel'] = 0; self.front['arrived'] = False
                    self.fronts_spawned += 1
                    self.front_max_concurrent = max(self.front_max_concurrent, 1)
                    assert self.front_max_concurrent <= GF.get('max_concurrent_fronts', 1)
                    self.front_events.append((self.sleep_no, 'spawn', c))

    def _gf_largest_tribe(self, p):
        """schema 3.9: largest dominant-pole tribe = most non-burn members with
        I*player_pole >= 1 (zealot included); fall back to any tribe of the player's pole."""
        best, bn = None, 0
        for t in self.tribes:
            n = sum(1 for x in self.npcs if x.tribe == t.idx and not x.burn and x.I*p >= 1)
            if n > bn: bn, best = n, t
        if best is None:
            best = next((t for t in self.tribes if t.pole == p), None)
        return best

    # ---------- wake action wrappers (spend + tick) ----------
    def act(self, kind, pos=None, pole=None, cost=0.0):
        self.stamina_spent_this_wake += cost
        if kind == 'walk':
            if TEMPLE_TERM and self.win_armed and int(TENTRY.get('harness_pilgrim_tiles_per_sleep', 6)) > 0 \
                    and not self.in_temple(self.player_pos):
                # H-9 (schema 3.10): while armed the avatar is on pilgrimage — a bot's walk is
                # consumed as pace tiles toward the temple; its destination is ignored.
                self._pilgrim_step(int(TENTRY.get('harness_pilgrim_tiles_per_sleep', 6)))
            else:
                self.player_pos = pos
            self.tick()
        elif kind == 'none':
            self.tick(sleeping=False)
        else:
            self.tick(actions=[(kind, pos or self.player_pos, pole if pole is not None else self.player_pole)])

def run(bot, seed, poles=(-1,-1,1), max_sleeps=25, player_pole=1):
    w = World(seed, zealot_poles=poles)
    w.player_pole = player_pole
    stats = {'stamina_total':0.0}
    while w.sleep_no < max_sleeps and not w.terminal:
        bot(w, stats)
        w.do_sleep()
    stats['terminal'] = w.terminal; stats['sleeps'] = w.sleep_no
    stats['final_wf'] = w.win_count()/w.pop(); stats['final_lf'] = w.loss_count()/w.pop()
    stats['selfburns'] = w.selfburn_nozealot; stats['pop'] = w.pop()
    stats['fronts_spawned'] = w.fronts_spawned                     # schema 3.9
    stats['front_exposure'] = round(w.front_exposure_npc_sleeps, 2)  # schema 3.9
    stats['front_events'] = list(w.front_events)                   # schema 3.9 audit
    if TEMPLE_ON:                                                  # schema 3.10 audit
        stats['temple_pos'] = list(w.temple_pos)
        stats['win_armed_sleep'] = w.win_armed_sleep
        stats['armed_to_terminal_sleeps'] = (w.sleep_no - w.win_armed_sleep) if (w.win_armed_sleep is not None and w.terminal) else None
        stats['lost_while_armed'] = bool(w.win_armed and w.terminal and w.terminal[0] == 'loss')
        stats['pilgrim_tiles'] = w.pilgrim_tiles
        stats['front_travel_sleeps'] = list(w.front_travel_sleeps)
        stats['well_exposure'] = round(w.well_exposure_npc_sleeps, 2)
    return stats
