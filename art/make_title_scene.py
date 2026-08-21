#!/usr/bin/env python3
"""uhta — TITLE SCENE painter (art pass 4, 2026-07-24).
The Plato's-cave opening (GDD §2.5) as a single 340x340 hand-built pixel
painting: dark cave, two tunnel mouths — the left lit red with shadows
FIGHTING on its wall, the right lit green with shadows TENDING/JOINING —
and the pale avatar small in the center foreground, white flame raised.

Painted (not tiled) in float RGB with a three-light model + hand-stamped
silhouettes, then quantized to a ~38-color uhta-family palette with ordered
(Bayer 8x8) dithering. Displayed at 2x nearest in the build (680x680).
"""
import numpy as np
from PIL import Image
import math, random, sys

W = H = 340
OUT = "assets"
rng = random.Random(11)

# ---------------------------------------------------------------- MODE (landmark revisit)
# The cave is a LANDMARK, not just a menu. On the opening it asks a question: two tunnels,
# two futures, fighting on one wall and tending on the other. Revisit it later and it stops
# asking — both walls now show what the world ACTUALLY became. The question turns into a
# mirror of your own record, and it does that WITHOUT A WORD (CANON v17 #5).
#
#   opening  both tunnels differ  — the question        (default; byte-identical output)
#   hope     both tunnels tend    — what you built
#   fear     both tunnels fight   — what you did
#   grey     both tunnels still   — what you let happen
MODE = sys.argv[1] if len(sys.argv) > 1 else 'opening'
assert MODE in ('opening', 'hope', 'fear', 'grey'), f"unknown mode {MODE}"

# ---------------------------------------------------------------- palette
def hx(s):
    s = s.lstrip('#'); return (int(s[0:2],16), int(s[2:4],16), int(s[4:6],16))
def npc(s): return np.array(hx(s))/255.0

STONE = ['050507','0a0a0e','101018','16161d','1e1e26','26262e','31313a','3d3d47','4a4a55','6a6a72','9a9aa2']
RED   = ['170d0d','2a1515','3c1f1e','5c2f2e','8a423f','b34f4b','d45b57','ff8a86','ffc7c4']
GREEN = ['0e1c12','16301c','1d3a22','2f5a34','468c4c','63c76b','9dffb0','d6ffdd']
WHITE = ['3a3a44','6a6a72','9a9aa2','c9c9d3','f2f2f5','ffffff']
GOLD  = ['4a4130','8a7c4e','d9c98a','f5ecc0']
PALETTE = np.array([hx(c) for c in STONE+RED+GREEN+WHITE+GOLD], dtype=np.float64)

# ---------------------------------------------------------------- helpers
def bayer8():
    m = np.array([[0]])
    for _ in range(3):
        m = np.block([[4*m+0, 4*m+2],[4*m+3, 4*m+1]])
    return m / m.size
B8 = bayer8()

def vnoise(w, h, freq, seed):
    r = np.random.default_rng(seed)
    gw, gh = int(w/freq)+2, int(h/freq)+2
    g = r.random((gh, gw))
    ys = np.arange(h)/freq; xs = np.arange(w)/freq
    y0 = ys.astype(int); x0 = xs.astype(int)
    fy = ys - y0; fx = xs - x0
    fy = fy*fy*(3-2*fy); fx = fx*fx*(3-2*fx)
    a = g[np.ix_(y0,   x0)];   b = g[np.ix_(y0,   x0+1)]
    c = g[np.ix_(y0+1, x0)];   d = g[np.ix_(y0+1, x0+1)]
    return a*(1-fx)[None,:]*(1-fy)[:,None] + b*fx[None,:]*(1-fy)[:,None] \
         + c*(1-fx)[None,:]*fy[:,None]     + d*fx[None,:]*fy[:,None]

def fbm(w, h, base, octaves, seed):
    out = np.zeros((h, w)); amp = 1.0; tot = 0.0; f = base
    for o in range(octaves):
        out += amp * vnoise(w, h, f, seed+o*77); tot += amp
        amp *= 0.5; f = max(2.0, f/2)
    return out/tot

YY, XX = np.mgrid[0:H, 0:W].astype(np.float64)

# ---------------------------------------------------------------- geometry
floorline = 212 + 5*fbm(W, 4, 60, 1, 5)[0] + 2*np.sin(np.arange(W)/47.0)
FLOOR = YY > floorline[np.newaxis, :]
WALL  = ~FLOOR

LCX, RCX = 95, 245
ATOP, AHW = 100, 38
def arch(cx, seed):
    edge = fbm(W, H, 22, 2, seed) * 3.0
    yb = floorline[np.newaxis, :] + 3
    t = np.clip((YY - ATOP) / np.maximum(yb - ATOP, 1), 0, 1)
    hw = np.where(t < 0.5, AHW*np.sqrt(np.clip(1-((0.5-t)/0.5)**2, 0, 1)), AHW)
    dist = np.abs(XX - cx) - (hw - edge)               # <0 inside
    inside = (dist < 0) & (YY >= ATOP) & (YY <= yb)
    rim = (np.abs(dist) < 3.0) & (YY >= ATOP-3) & (YY <= yb)
    return inside, rim
L_ARCH, L_RIM = arch(LCX, 21)
R_ARCH, R_RIM = arch(RCX, 22)

# ---------------------------------------------------------------- light model
def glow(cx, cy, radius, power=2.6):
    d = np.hypot(XX-cx, YY-cy)
    return 1.0/(1.0 + (d/radius)**power)

RED_L, GREEN_L = npc('d45b57'), npc('63c76b')
WHITE_L, GOLD_L = npc('f2f2f5'), npc('d9c98a')

# what falls on the OUTER wall/floor: spill from each mouth + the small white flame
I_red   = 0.50*glow(LCX, 190, 62) + 0.14*glow(LCX, 150, 90)
I_green = 0.50*glow(RCX, 190, 62) + 0.14*glow(RCX, 150, 90)
I_white = 0.68*glow(186, 212, 19) + 0.40*glow(172, 260, 40, 2.2) + 0.14*glow(170, 196, 85, 2.0)   # flame + floor pool + faint mid-wall presence

AMB = 0.018
Lsum = AMB + I_red[...,None]*RED_L + I_green[...,None]*GREEN_L + I_white[...,None]*WHITE_L

# ---------------------------------------------------------------- albedo + base compose
albedo = np.clip(0.78 + 0.38*(fbm(W, H, 40, 4, 9)-0.5)
                 + 0.10*np.sin(YY/10.0 + 5.0*fbm(W, H, 90, 2, 13)), 0.5, 1.15)
floor_albedo = np.clip(0.72 + 0.30*(fbm(W, H, 22, 4, 31)-0.5), 0.5, 1.05)

img = np.zeros((H, W, 3))
CRISP = np.zeros((H, W), bool)     # stamped art (figure/flame/wordmark/etc): no dither flicker
img[WALL]  = (albedo[...,None]*Lsum)[WALL]
img[FLOOR] = (floor_albedo[...,None]*Lsum*0.8)[FLOOR]

# ambient-occlusion seam where wall meets floor
seam = np.exp(-np.abs(YY - floorline[np.newaxis,:])/3.0)
img *= (1 - 0.45*seam)[...,None]

# ---------------------------------------------------------------- tunnel interiors
# hot fire deeper in, dark throat at the top of the arch (the passage bends away)
def interior(mask, cx, tint, seed):
    tex = 0.72 + 0.5*(fbm(W, H, 26, 3, seed)-0.5)
    heat = 1.10*glow(cx, 206, 58, 1.8) + 0.50*glow(cx, 172, 48, 2.0)
    throat = np.clip((YY-ATOP)/64.0, 0, 1)**1.5        # 0 at arch top -> 1 lower
    lateral = 1 - 0.30*np.clip(np.abs(XX-cx)/AHW, 0, 1)**2
    v = np.clip(heat*tex*throat*lateral, 0, 1.05)
    out = v[...,None]*tint*1.18 + 0.006
    img[mask] = out[mask]
L_TINT, R_TINT = RED_L, GREEN_L
if   MODE == 'hope': L_TINT = R_TINT = GREEN_L      # both mouths burn the same colour now
elif MODE == 'fear': L_TINT = R_TINT = RED_L
elif MODE == 'grey': L_TINT = R_TINT = npc('6a6a72')
interior(L_ARCH, LCX, L_TINT, 61)
interior(R_ARCH, RCX, R_TINT, 62)

# rock rim framing each mouth (lit edge facing its own fire)
for RIM, tint in [(L_RIM, L_TINT), (R_RIM, R_TINT)]:
    img[RIM] = (0.16*tint + 0.35*img[RIM])

# ---------------------------------------------------------------- shadow plays
# Big readable silhouettes (~44px figures, 3-4px limbs) drawn with PIL strokes
# onto a mask, then stamped as darkness CLIPPED to each arch interior.
from PIL import ImageDraw

def sil_layer(draw_fn):
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    draw_fn(d)
    return np.asarray(m, dtype=np.float64)/255.0

def head(d, x, y, r=4): d.ellipse([x-r, y-r, x+r, y+r], fill=255)

def fight_layer(d):
    # LUNGER: leaning right, wide lunge, spear thrust up-right
    hx0, hy0 = LCX-16, 160
    head(d, hx0, hy0, 5)
    d.line([hx0, hy0+4, hx0+8, hy0+22], width=7, fill=255)            # torso leaning in
    d.line([hx0+8, hy0+22, hx0-4, hy0+36], width=4, fill=255)         # back leg
    d.line([hx0-4, hy0+36, hx0-9, hy0+50], width=4, fill=255)
    d.line([hx0+8, hy0+22, hx0+18, hy0+36], width=4, fill=255)        # front leg (lunge)
    d.line([hx0+18, hy0+36, hx0+20, hy0+52], width=4, fill=255)
    d.line([hx0+4, hy0+10, hx0+18, hy0+4], width=4, fill=255)         # arms to spear
    d.line([hx0-14, hy0+26, hx0+30, hy0-12], width=3, fill=255)       # SPEAR (long diagonal)
    d.polygon([(hx0+30, hy0-12),(hx0+36, hy0-18),(hx0+33, hy0-10)], fill=255)  # spearhead
    # DEFENDER: knocked back, arm up, own spear dropping
    dx0, dy0 = LCX+22, 156
    head(d, dx0, dy0, 5)
    d.line([dx0, dy0+4, dx0-7, dy0+22], width=7, fill=255)            # torso reeling back
    d.line([dx0-7, dy0+22, dx0-14, dy0+38], width=4, fill=255)        # leg
    d.line([dx0-14, dy0+38, dx0-12, dy0+54], width=4, fill=255)
    d.line([dx0-7, dy0+22, dx0+4, dy0+40], width=4, fill=255)         # braced leg
    d.line([dx0+4, dy0+40, dx0+8, dy0+54], width=4, fill=255)
    d.line([dx0-2, dy0+8, dx0+12, dy0-6], width=4, fill=255)          # arm flung up
    # FALLEN: compact prone figure between the fighters
    fx0, fy0 = LCX+1, 202
    head(d, fx0-11, fy0+1, 3)
    d.line([fx0-7, fy0+2, fx0+9, fy0], width=4, fill=255)             # prone body

def tend_layer(d):
    # TWO FIGURES JOINING HANDS across the center
    ax0, ay0 = RCX-20, 158
    head(d, ax0, ay0, 5)
    d.line([ax0, ay0+4, ax0-2, ay0+24], width=7, fill=255)            # torso
    d.line([ax0-2, ay0+24, ax0-8, ay0+40], width=4, fill=255)         # legs
    d.line([ax0-8, ay0+40, ax0-8, ay0+54], width=4, fill=255)
    d.line([ax0-2, ay0+24, ax0+4, ay0+40], width=4, fill=255)
    d.line([ax0+4, ay0+40, ax0+4, ay0+54], width=4, fill=255)
    bx0, by0 = RCX+18, 158
    head(d, bx0, by0, 5)
    d.line([bx0, by0+4, bx0+2, by0+24], width=7, fill=255)
    d.line([bx0+2, by0+24, bx0+8, by0+40], width=4, fill=255)
    d.line([bx0+8, by0+40, bx0+8, by0+54], width=4, fill=255)
    d.line([bx0+2, by0+24, bx0-4, by0+40], width=4, fill=255)
    d.line([bx0-4, by0+40, bx0-4, by0+54], width=4, fill=255)
    d.line([ax0+2, ay0+10, RCX-1, ay0+18], width=4, fill=255)         # reaching arms -> clasp
    d.line([bx0-2, by0+10, RCX+1, by0+18], width=4, fill=255)
    d.ellipse([RCX-4, ay0+15, RCX+4, ay0+22], fill=255)               # joined hands
    pass  # (collaboration is carried by the joined pair; a garden grows at their feet)

def plant_stamp():
    # a small garden growing at the pair's feet: two dark stalks, bright HOPE tips
    for (px0, py0, hgt) in [(RCX-26, 186, 22), (RCX-18, 196, 14)]:
        if not R_ARCH[py0+hgt, px0]: continue
        for dy in range(hgt):
            t = dy/hgt
            dx = int(2*math.sin(dy/3.5))
            img[py0+dy, px0+dx] *= 0.10
            if dy % 5 == 2 and dy < hgt-3:                    # leaf pairs
                img[py0+dy, px0+dx-2] *= 0.12; img[py0+dy, px0+dx+2] *= 0.12
        for (dx,dy) in [(0,-1),(-2,2),(2,4)]:
            img[py0+dy, px0+dx] = npc('9dffb0')*0.85
            CRISP[py0+dy, px0+dx] = True

def still_layer(d):
    # Apathy's shadow-play is the ABSENCE of a verb. Where fight and tend are both actions,
    # these figures have simply stopped: heads down, no reaching, no contact between them.
    for cx0 in (LCX, RCX):
        for (ox, oy, s) in [(-22, 168, 1.0), (-2, 176, 1.1), (20, 170, 0.95)]:
            x, y = cx0+ox, oy
            head(d, x, y, int(5*s))
            d.line([x, y+int(5*s), x-int(3*s), y+int(26*s)], width=int(7*s), fill=255)
            d.line([x-int(3*s), y+int(26*s), x-int(8*s), y+int(44*s)], width=int(4*s), fill=255)
            d.line([x-int(3*s), y+int(26*s), x+int(5*s), y+int(44*s)], width=int(4*s), fill=255)

def mirror_layer(which):
    """Both walls carry the same play on a revisit — the world has already chosen."""
    def f(d):
        for cx0 in (LCX, RCX):
            dx = cx0 - (LCX if which is fight_layer else RCX)
            d.im_offset = dx
        which(d)
    return f

if MODE == 'opening':
    L_PLAY, R_PLAY = sil_layer(fight_layer), sil_layer(tend_layer)
elif MODE == 'fear':
    L_PLAY = R_PLAY = sil_layer(fight_layer)
    R_PLAY = np.roll(L_PLAY, RCX-LCX, axis=1)      # same play, mirrored into the other mouth
elif MODE == 'hope':
    R_PLAY = sil_layer(tend_layer)
    L_PLAY = np.roll(R_PLAY, LCX-RCX, axis=1)
else:                                              # grey
    L_PLAY = R_PLAY = sil_layer(still_layer)

img[L_ARCH] *= (1 - 0.92*L_PLAY[L_ARCH])[...,None]
img[R_ARCH] *= (1 - 0.92*R_PLAY[R_ARCH])[...,None]
if MODE in ('opening', 'hope'):
    plant_stamp()   # the garden only grows where something was tended

# ---------------------------------------------------------------- stalactites
def stalactite(cx, ln, hw, seed):
    r = random.Random(seed)
    near = RED_L if cx < 170 else GREEN_L
    for y in range(0, ln):
        t = y/ln
        w = max(1, int(hw*(1-t) + r.uniform(-0.6,0.6)))
        x0, x1 = int(cx-w), int(cx+w)
        img[y, max(0,x0):min(W,x1)] = img[y, max(0,x0):min(W,x1)]*0.12
        if 0 <= x1 < W and t > 0.25:                     # rim toward its light
            img[y, x1 if cx<170 else max(0,x0)] = near*(0.16*t) + img[y, x1 if cx<170 else max(0,x0)]*0.4
for i,(cx,ln,hw) in enumerate([(26,52,7),(58,30,5),(126,42,6),(154,24,4),(188,28,4),(216,46,6),(284,34,5),(314,56,8),(96,18,3),(246,20,3),(170,16,3)]):
    stalactite(cx, ln, hw, 100+i)

# ---------------------------------------------------------------- foreground vignette
def vignette_blob(cx, cy, rx, ry, seed, dark=0.05):
    e = fbm(W, H, 30, 3, seed)
    d = ((XX-cx)/rx)**2 + ((YY-cy)/ry)**2 + 0.5*(e-0.5)
    m = d < 1.0
    tex = (0.6+0.8*fbm(W, H, 18, 3, seed+5))
    img[m] = np.clip(img[m]*dark*tex[m][...,None] + 0.006, 0, 1)
    return m
vignette_blob(-40, 360, 150, 150, 201)
vignette_blob(385, 365, 160, 145, 202)
vignette_blob(-45, 160, 62, 190, 203)
vignette_blob(388, 158, 64, 195, 204)
vignette_blob(170, 392, 210, 66, 205)

# floor rubble (a few small lit-top stones, subtle)
for _ in range(12):
    x = rng.randrange(70, 270); y = rng.randrange(int(np.interp(x, np.arange(W), floorline))+10, 315)
    w2 = rng.randrange(2, 4)
    if abs(x-170) < 30 and y < 290: continue            # keep the light pool clean
    img[y:y+2, x-w2:x+w2] *= 0.45
    img[y-1, x-w2+1:x+w2-1] += Lsum[y-1, x]*0.9

# ---------------------------------------------------------------- floor reflections
# wet stone: vertical mirrored shafts under each light, broken by dry rows
rcolumns = np.random.default_rng(57).random(W)
row_break = fbm(W, H, 9, 2, 58) > 0.42
streak = (rcolumns > 0.74)[np.newaxis, :] & row_break
for (cx, col, st, wsc) in [(LCX,RED_L,0.30,4.6),(RCX,GREEN_L,0.30,4.6),(172,WHITE_L,0.34,5.2)]:
    cy = float(np.interp(cx, np.arange(W), floorline))
    mirror = 1.0/(1.0 + (np.hypot((XX-cx)*wsc, (YY-cy)*1.0)/46)**2.2)
    m = FLOOR & streak
    img[m] += (st*mirror[...,None]*col)[m]

# ---------------------------------------------------------------- the avatar
# ~48px tall, seen from behind: pale broad-shouldered humanoid, right arm
# raised, white flame above the fist. Built as an ImageDraw mask, then shaded
# in the WHITE ramp with a dark outline and red/green rim light.
def stamp_avatar():
    cx, top = 170, 214
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.line([cx+8, top+23, cx+15, top+7], width=4, fill=255)           # raised right arm
    d.ellipse([cx+12, top+2, cx+19, top+9], fill=255)                 # fist
    d.ellipse([cx-5, top+8, cx+5, top+19], fill=255)                  # head
    d.polygon([(cx-12,top+21),(cx+12,top+21),(cx+9,top+35),
               (cx+10,top+42),(cx-10,top+42),(cx-9,top+35)], fill=255)  # broad torso -> waist
    d.line([cx-10, top+24, cx-13, top+37], width=4, fill=255)         # left arm down
    d.rectangle([cx-8, top+42, cx-3, top+56], fill=255)               # legs
    d.rectangle([cx+3, top+42, cx+8, top+56], fill=255)
    M = np.asarray(m) > 0
    inner = M & np.roll(M,1,0) & np.roll(M,-1,0) & np.roll(M,1,1) & np.roll(M,-1,1)
    outline = M & ~inner
    body = np.where(((YY-top) > 42)[...,None], npc('c9c9d3'), npc('f2f2f5'))   # legs a step dimmer
    img[M] = body[M]
    img[outline] = npc('0a0a0e')
    CRISP[M] = True
    # crown of the head catches its own flame
    img[top+8:top+11, cx-2:cx+3] = npc('ffffff')
    # rim light: red on the LEFT edge, green on the RIGHT — the choice on the body
    for y in range(top+20, top+57):
        xs_ = np.where(M[y])[0]
        if len(xs_) < 3: continue
        img[y, xs_[0]] = 0.6*RED_L + 0.4*img[y, xs_[0]]
        img[y, xs_[0]+1] = 0.3*RED_L + 0.7*img[y, xs_[0]+1]
        img[y, xs_[-1]] = 0.6*GREEN_L + 0.4*img[y, xs_[-1]]
        img[y, xs_[-1]-1] = 0.3*GREEN_L + 0.7*img[y, xs_[-1]-1]
    # THE WHITE FLAME above the fist: gold-warm halo, hot white teardrop core
    fx_, fy_ = cx+16, top-2
    for r, col, a in [(7, GOLD_L, 0.30), (5, npc('ffc7c4')*0.5+npc('ffffff')*0.5, 0.5)]:
        yy0, xx0 = np.ogrid[-r:r+1, -r:r+1]
        disc = (xx0*xx0 + yy0*yy0) <= r*r
        reg = img[fy_-r:fy_+r+1, fx_-r:fx_+r+1]
        reg[disc] = reg[disc]*(1-a) + col*a
    d2 = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(d2)
    dd.polygon([(fx_, fy_-7),(fx_+3, fy_-1),(fx_+2, fy_+3),(fx_-2, fy_+3),(fx_-3, fy_-1)], fill=255)
    FM = np.asarray(d2) > 0
    img[FM] = npc('ffffff')
    CRISP[FM] = True
stamp_avatar()

# unlit gold basin, right of the figure (the myth's dark basin)
BASIN = [
"..gGGg....",
".g....Gg..",
"g........g",
".gggggggg.",
]
for dy,row in enumerate(BASIN):
    for dx,ch in enumerate(row):
        if ch=='G':
            img[272+dy, 138+dx] = GOLD_L*0.8; CRISP[272+dy, 138+dx] = True
        elif ch=='g':
            img[272+dy, 138+dx] = GOLD_L*0.38; CRISP[272+dy, 138+dx] = True

# ---------------------------------------------------------------- dust motes
for _ in range(90):
    x = rng.randrange(20, W-20); y = rng.randrange(60, 230)
    l = Lsum[y, x]
    if 0.05 < l.max() < 0.6 and rng.random() < 0.55:
        img[y, x] = np.clip(l*4.0, 0, 0.8)

# ---------------------------------------------------------------- wordmark "uhta"
# baseline-aligned lowercase: h/t carry ascenders (8 rows), u/a sit at
# x-height (rows 3-7) — so it reads as a word, not capitals.
LET = {
 'u':(3, ["#...#","#...#","#...#","#...#",".###."]),
 'h':(0, ["#....","#....","#....","####.","#...#","#...#","#...#","#...#"]),
 't':(0, ["..#..","..#..","..#..","#####","..#..","..#..","..#..","...##"]),
 'a':(3, [".###.","....#",".####","#...#",".####"]),
}
def wordmark(y0, s=4, gap=2):
    total = (5*4 + gap*3)*s
    x = (W-total)//2
    dark = npc('050507')
    for ch in "uhta":
        yo, rows = LET[ch]
        for dy,row in enumerate(rows):
            for dx,c in enumerate(row):
                if c=='#':
                    ys, xs_ = y0+(yo+dy)*s, x+dx*s
                    img[ys-1:ys+s+1, xs_-1:xs_+s+1] = dark          # halo/outline
        for dy,row in enumerate(rows):
            for dx,c in enumerate(row):
                if c=='#':
                    ys, xs_ = y0+(yo+dy)*s, x+dx*s
                    img[ys:ys+s, xs_:xs_+s] = npc('f2f2f5')
                    CRISP[ys-1:ys+s+1, xs_-1:xs_+s+1] = True
        x += (5+gap)*s
if MODE == 'opening':
    wordmark(20, 4)   # the wordmark belongs to the TITLE. A revisit is a place, not a menu.

# ---------------------------------------------------------------- quantize
def quantize(im):
    im8 = np.clip(im, 0, 1)*255
    d = (np.tile(B8, (H//8+1, W//8+1))[:H,:W,None]-0.5) * 22.0
    d[CRISP] = 0.0                                   # stamped art stays flat/clean
    im8 = np.clip(im8 + d, 0, 255)
    flat = im8.reshape(-1, 3)
    dist = ((flat[:,None,:]-PALETTE[None,:,:])**2).sum(-1)
    idx = dist.argmin(1)
    return PALETTE[idx].reshape(H, W, 3).astype(np.uint8)

out = quantize(img)
stem = "title_scene" if MODE == 'opening' else f"cave_mirror_{MODE}"
Image.fromarray(out).save(f"{OUT}/{stem}.png")
Image.fromarray(out).resize((W*2, H*2), Image.NEAREST).save(f"{OUT}/{stem}_2x.png")
print("palette:", len(PALETTE), "| mode:", MODE, "| wrote", f"{OUT}/{stem}.png", "+ 2x preview")
