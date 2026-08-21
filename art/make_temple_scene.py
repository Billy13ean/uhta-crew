#!/usr/bin/env python3
"""uhta — THE TEMPLE OF UHTCEARU (the Mourning House), landmark scene painter.

Sibling to art/make_title_scene.py: same 340x340 canvas, same three-light model, same
~38-colour uhta-family palette, same Bayer-8 ordered dithering with a CRISP mask for
stamped art. Displayed at 2x nearest in the build (680x680), exactly like the cave.

WHAT THE IMAGE HAS TO SAY (CANON v17, GRIEF CANON):
  "grief is not a pole — it is the gravity. Uhtcearu never fights for a colour;
   he drowns the board in grey."

So the temple is painted under one rule: NO POLE COLOUR EXISTS IN THIS ROOM. There is no
red light and no green light anywhere in the frame. The only warm thing in 340x340 pixels
is the player's own white flame, it is very small, and its light does not reach the god.
Everything else is the STONE ramp. That is the whole argument, made without a word.

Second rule, from the art-direction study (P2 — light is rationed): the oculus light is
cold and falls off before the floor, so the room is mostly darkness with a lit throat.

Scale is the third argument: the avatar is ~26px against a ~200px seated figure. In the
cave the player was the largest lit thing in the frame. Here he is a detail.
"""
import numpy as np
from PIL import Image, ImageDraw
import math, random

W = H = 340
OUT = "assets"
rng = random.Random(29)

# ---------------------------------------------------------------- palette (identical family)
def hx(s):
    s = s.lstrip('#'); return (int(s[0:2],16), int(s[2:4],16), int(s[4:6],16))
def npc(s): return np.array(hx(s))/255.0

STONE = ['050507','0a0a0e','101018','16161d','1e1e26','26262e','31313a','3d3d47','4a4a55','6a6a72','9a9aa2']
RED   = ['170d0d','2a1515','3c1f1e','5c2f2e','8a423f','b34f4b','d45b57','ff8a86','ffc7c4']
GREEN = ['0e1c12','16301c','1d3a22','2f5a34','468c4c','63c76b','9dffb0','d6ffdd']
WHITE = ['3a3a44','6a6a72','9a9aa2','c9c9d3','f2f2f5','ffffff']
GOLD  = ['4a4130','8a7c4e','d9c98a','f5ecc0']
PALETTE = np.array([hx(c) for c in STONE+RED+GREEN+WHITE+GOLD], dtype=np.float64)

# ---------------------------------------------------------------- helpers (same as the cave)
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

def glow(cx, cy, radius, power=2.6):
    d = np.hypot(XX-cx, YY-cy)
    return 1.0/(1.0 + (d/radius)**power)

def sil_layer(draw_fn):
    m = Image.new('L', (W, H), 0)
    draw_fn(ImageDraw.Draw(m))
    return np.asarray(m, dtype=np.float64)/255.0

# ---------------------------------------------------------------- geometry
FLOOR_Y = 262.0
floorline = FLOOR_Y + 3*fbm(W, 4, 70, 1, 3)[0]
FLOOR = YY > floorline[np.newaxis, :]
WALL  = ~FLOOR

# the oculus: a tall slot high in the back wall — the room's only real light
OCX, OCY, OCW, OCH = 170, 62, 21, 58

# ---------------------------------------------------------------- light model
COLD = npc('9a9aa2')      # daylight, drained of every hue — the STONE ramp's top stop
WHITE_L, GOLD_L = npc('f2f2f5'), npc('d9c98a')

# NOTE: no RED_L / GREEN_L in this file at all. That absence is the design.
I_cold = 0.62*glow(OCX, OCY+34, 58, 2.2) + 0.30*glow(OCX, OCY+120, 168, 1.7)
FLAME_X, FLAME_Y = 148, 272                     # the player's flame, low and far right of centre
I_flame = 0.55*glow(FLAME_X, FLAME_Y, 15) + 0.22*glow(FLAME_X, FLAME_Y+18, 30, 2.2)

AMB = 0.015
Lsum = AMB + I_cold[...,None]*COLD + I_flame[...,None]*WHITE_L

# ---------------------------------------------------------------- albedo + base compose
albedo = np.clip(0.74 + 0.34*(fbm(W, H, 46, 4, 17)-0.5)
                 + 0.09*np.sin(YY/13.0 + 4.0*fbm(W, H, 95, 2, 23)), 0.5, 1.12)
floor_albedo = np.clip(0.66 + 0.28*(fbm(W, H, 24, 4, 41)-0.5), 0.45, 1.0)

img = np.zeros((H, W, 3))
CRISP = np.zeros((H, W), bool)
img[WALL]  = (albedo[...,None]*Lsum)[WALL]
img[FLOOR] = (floor_albedo[...,None]*Lsum*0.76)[FLOOR]

seam = np.exp(-np.abs(YY - floorline[np.newaxis,:])/3.5)
img *= (1 - 0.42*seam)[...,None]

# ---------------------------------------------------------------- the oculus itself
oc = (np.abs(XX-OCX) < OCW/2) & (YY > OCY-OCH/2) & (YY < OCY+OCH/2)
arch_top = (np.hypot((XX-OCX), (YY-(OCY-OCH/2))*1.1) < OCW/2) & (YY <= OCY-OCH/2)
OCULUS = oc | arch_top
img[OCULUS] = COLD*0.92
CRISP[OCULUS] = True
rim = ((np.abs(np.abs(XX-OCX) - OCW/2) < 2.0) & (YY > OCY-OCH/2-8) & (YY < OCY+OCH/2+2))
img[rim] = 0.30*COLD + 0.45*img[rim]

# a shaft of light falling from it, catching dust
shaft = np.clip(1 - np.abs(XX-OCX)/(OCW/2 + (YY-OCY)*0.42), 0, 1)
shaft = np.where((YY > OCY) & (YY < FLOOR_Y+14), shaft**2.0, 0)
img += (shaft*0.085)[...,None]*COLD

# ---------------------------------------------------------------- columns (depth by ranks)
def column(cx, top, w, dark):
    """A pier receding into the dark. Lit edge faces the oculus."""
    body = (np.abs(XX-cx) < w/2) & (YY > top) & (YY < floorline[np.newaxis,:]+2)
    img[body] = img[body]*dark
    inner = cx + (w/2 if cx < OCX else -w/2)     # edge facing centre light
    edge = (np.abs(XX-inner) < 1.2) & (YY > top) & (YY < floorline[np.newaxis,:])
    img[edge] = 0.20*COLD*np.clip((1-(YY[edge]-top)/240),0.15,1)[...,None] + img[edge]*0.55
    cap = (np.abs(XX-cx) < w/2+3) & (YY > top-6) & (YY < top+2)   # capital
    img[cap] = img[cap]*(dark*0.8) + 0.03

for (cx, top, w, dk) in [(24, 74, 30, 0.14), (63, 92, 22, 0.17), (95, 106, 16, 0.21),
                         (316, 74, 30, 0.14), (277, 92, 22, 0.17), (245, 106, 16, 0.21)]:
    column(cx, top, w, dk)

# ---------------------------------------------------------------- the frieze
# generations of mourners carved into the back wall, small and repeating — the room has
# been doing this for a very long time and will continue after you leave.
def frieze(y0, n, step, x0, scale=1.0, dark=0.42):
    for i in range(n):
        x = x0 + i*step
        if not (0 < x < W-4): continue
        h_ = int(9*scale)
        for dy in range(h_):
            t = dy/h_
            wdt = 1 if t < 0.30 else 2                      # bowed head, then body
            xx0 = int(x-wdt); xx1 = int(x+wdt+1)
            img[y0+dy, max(0,xx0):min(W,xx1)] *= dark
        img[y0+h_, max(0,int(x-2)):min(W,int(x+3))] *= 0.55  # the ground they kneel on
# kept OUTSIDE the god's silhouette on purpose — inside it they just read as noise in a
# black mass. They belong on the lit wall either side of him, where they can be seen.
frieze(120, 3, 12, 62, 0.9, 0.42)
frieze(120, 3, 12, 250, 0.9, 0.42)
frieze(150, 2, 14, 58, 1.05, 0.48)
frieze(150, 2, 14, 258, 1.05, 0.48)

# ---------------------------------------------------------------- UHTCEARU
# A vast bowed figure filling the centre: shoulders wide, head down, hands in the lap.
# Never fully lit, never fully visible — you are not shown all of him.
# A single union silhouette this large just reads as a bell. So he is built as NAMED PARTS,
# unioned for the dark mass, but each part ALSO rim-lit along its own upper edge — so the
# head, the shoulders, the arms and the hands separate as contours inside the darkness.
# Same trick the cave uses on its stalactites, applied to anatomy.
CX = OCX
def p_dais(d):  d.polygon([(CX-112,268),(CX+112,268),(CX+98,248),(CX-98,248)], fill=255)
def p_lap(d):   d.polygon([(CX-92,252),(CX+92,252),(CX+78,212),(CX-78,212)], fill=255)
def p_torso(d): d.polygon([(CX-58,216),(CX+58,216),(CX+50,150),(CX-50,150)], fill=255)
def p_back(d):  d.ellipse([CX-62,100,CX+62,178], fill=255)          # the crest — highest point
def p_head(d):  d.ellipse([CX-24,142,CX+24,190], fill=255)          # hanging BELOW the crest
def p_armL(d):  d.polygon([(CX-60,146),(CX-34,154),(CX-26,222),(CX-70,214)], fill=255)
def p_armR(d):  d.polygon([(CX+60,146),(CX+34,154),(CX+26,222),(CX+70,214)], fill=255)
def p_handL(d): d.ellipse([CX-66,206,CX-16,240], fill=255)
def p_handR(d): d.ellipse([CX+16,206,CX+66,240], fill=255)

PARTS = [p_dais, p_lap, p_torso, p_back, p_head, p_armL, p_armR, p_handL, p_handR]
MASKS = [sil_layer(f) > 0.5 for f in PARTS]
GOD = np.zeros((H, W), bool)
for m in MASKS: GOD |= m
img[GOD] = img[GOD]*0.16 + 0.004

def rim(mask, strength, spread=150.0, depth=3):
    """Light the upper edge of one part, falling off away from the oculus."""
    for x in range(W):
        col = np.where(mask[:, x])[0]
        if len(col) < 3: continue
        top = col[0]
        fall = max(0.0, 1.0 - abs(x-CX)/spread)
        for k in range(depth):
            if top+k < H:
                img[top+k, x] = (strength-strength/depth*k)*COLD*fall + img[top+k, x]*0.62

for m, s in zip(MASKS, [0.10, 0.16, 0.13, 0.34, 0.22, 0.15, 0.15, 0.20, 0.20]):
    rim(m, s)
# the faintest hollow where a face would be — read it or don't
face = (np.hypot((XX-OCX)/15.0, (YY-172)/12.0) < 1.0) & GOD
img[face] += 0.012

# ---------------------------------------------------------------- mourner shadow-plays
# The cave's tunnels showed FIGHTING and TENDING — two verbs, two futures. Grief's
# shadow-play is the absence of a verb: figures that have stopped. Stamped as darkness
# on the lit floor in front of the god, the same technique as the cave's arch interiors.
def mourners(d):
    # on the open floor either side of the dais, where they silhouette against wet stone
    for (mx, my, s) in [(64, 284, 1.0), (92, 292, 1.2), (246, 286, 1.1), (276, 294, 1.25), (300, 288, 0.95)]:
        hh = int(9*s)
        d.ellipse([mx-int(3*s), my-hh, mx+int(3*s), my-hh+int(6*s)], fill=255)   # bowed head
        d.polygon([(mx-int(6*s), my+int(9*s)), (mx+int(7*s), my+int(9*s)),
                   (mx+int(4*s), my-hh+int(4*s)), (mx-int(3*s), my-hh+int(3*s))], fill=255)
        d.polygon([(mx-int(7*s), my+int(9*s)), (mx+int(2*s), my+int(9*s)),
                   (mx-int(1*s), my+int(3*s)), (mx-int(6*s), my+int(4*s))], fill=255)  # folded knees
MOURN = sil_layer(mourners)
img *= (1 - 0.88*MOURN)[...,None]

# ---------------------------------------------------------------- grief pooled on the floor
# standing water that never drains. Vertical mirror streaks under the cold light only —
# the flame's reflection is deliberately tiny.
rcolumns = np.random.default_rng(71).random(W)
row_break = fbm(W, H, 10, 2, 73) > 0.40
streak = (rcolumns > 0.70)[np.newaxis, :] & row_break
for (cx, col, st, wsc) in [(OCX, COLD, 0.26, 4.4), (FLAME_X, WHITE_L, 0.20, 6.0)]:
    cy = float(np.interp(cx, np.arange(W), floorline))
    mirror = 1.0/(1.0 + (np.hypot((XX-cx)*wsc, (YY-cy)*1.0)/44)**2.2)
    m = FLOOR & streak
    img[m] += (st*mirror[...,None]*col)[m]

# tarnished offerings at the god's feet — the only gold in the room, and it is dull
for (gx, gy, gw) in [(126, 258, 5), (150, 261, 4), (196, 259, 6), (218, 262, 4)]:
    for dx in range(-gw, gw+1):
        t = 1 - abs(dx)/(gw+1)
        img[gy, gx+dx] = GOLD_L*(0.20+0.16*t)
        CRISP[gy, gx+dx] = True

# ---------------------------------------------------------------- vignette
def vignette_blob(cx, cy, rx, ry, seed, dark=0.05):
    e = fbm(W, H, 32, 3, seed)
    d = ((XX-cx)/rx)**2 + ((YY-cy)/ry)**2 + 0.5*(e-0.5)
    m = d < 1.0
    tex = (0.6+0.8*fbm(W, H, 20, 3, seed+5))
    img[m] = np.clip(img[m]*dark*tex[m][...,None] + 0.005, 0, 1)
vignette_blob(-46, 172, 66, 205, 301)
vignette_blob(390, 172, 68, 205, 302)
vignette_blob(170, 396, 220, 70, 303)
vignette_blob(-40, -30, 130, 130, 304)
vignette_blob(384, -30, 130, 130, 305)

# ---------------------------------------------------------------- the avatar
# ~26px against a ~200px god. In the cave he was the biggest lit thing in frame; here he
# is a detail, and his flame does not reach the figure above him. Same WHITE ramp, same
# dark outline, but NO red/green rim light — there is no pole light in this room to catch.
def stamp_avatar():
    cx, top = FLAME_X - 6, 274
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.line([cx+4, top+12, cx+8, top+3], width=2, fill=255)          # raised arm
    d.ellipse([cx+6, top, cx+11, top+5], fill=255)                  # fist
    d.ellipse([cx-3, top+4, cx+3, top+11], fill=255)                # head
    d.polygon([(cx-7,top+12),(cx+7,top+12),(cx+5,top+20),
               (cx+5,top+24),(cx-5,top+24),(cx-5,top+20)], fill=255)
    d.line([cx-6, top+13, cx-7, top+21], width=2, fill=255)         # arm down
    d.rectangle([cx-4, top+24, cx-2, top+31], fill=255)             # legs
    d.rectangle([cx+2, top+24, cx+4, top+31], fill=255)
    M = np.asarray(m) > 0
    inner = M & np.roll(M,1,0) & np.roll(M,-1,0) & np.roll(M,1,1) & np.roll(M,-1,1)
    outline = M & ~inner
    img[M] = npc('c9c9d3')
    img[outline] = npc('0a0a0e')
    CRISP[M] = True
    # THE WHITE FLAME — the only warm light in 340x340 pixels, and it is 6 pixels tall
    fx_, fy_ = cx+9, top-3
    for r, col, a in [(6, GOLD_L, 0.26), (4, npc('ffffff'), 0.5)]:
        yy0, xx0 = np.ogrid[-r:r+1, -r:r+1]
        disc = (xx0*xx0 + yy0*yy0) <= r*r
        reg = img[fy_-r:fy_+r+1, fx_-r:fx_+r+1]
        reg[disc] = reg[disc]*(1-a) + col*a
    d2 = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(d2)
    dd.polygon([(fx_, fy_-5),(fx_+2, fy_-1),(fx_+2, fy_+2),(fx_-2, fy_+2),(fx_-2, fy_-1)], fill=255)
    FM = np.asarray(d2) > 0
    img[FM] = npc('ffffff')
    CRISP[FM] = True
stamp_avatar()

# ---------------------------------------------------------------- dust in the shaft
for _ in range(70):
    x = rng.randrange(30, W-30); y = rng.randrange(70, 250)
    if shaft[y, x] < 0.10: continue
    if rng.random() < 0.5:
        img[y, x] = np.clip(COLD*(0.22+0.5*shaft[y, x]), 0, 0.72)

# ---------------------------------------------------------------- quantize
def quantize(im):
    im8 = np.clip(im, 0, 1)*255
    # Dither amplitude scales with brightness. The cave is mostly mid-tones so a flat 22
    # works there; the temple is mostly deep shadow, and a flat amplitude turns all that
    # darkness into visible chequerboard. Ramp it down where there is nothing to dither.
    amp = 8.0 + 16.0*np.clip(im8.max(axis=2)/120.0, 0, 1)
    d = (np.tile(B8, (H//8+1, W//8+1))[:H,:W]-0.5)[...,None] * amp[...,None]
    d[CRISP] = 0.0
    im8 = np.clip(im8 + d, 0, 255)
    flat = im8.reshape(-1, 3)
    dist = ((flat[:,None,:]-PALETTE[None,:,:])**2).sum(-1)
    idx = dist.argmin(1)
    return PALETTE[idx].reshape(H, W, 3).astype(np.uint8)

out = quantize(img)
Image.fromarray(out).save(f"{OUT}/temple_scene.png")
Image.fromarray(out).resize((W*2, H*2), Image.NEAREST).save(f"{OUT}/temple_scene_2x.png")

# audit the design rule: assert no pole colour survived into the image
pole = set(hx(c) for c in RED[3:]) | set(hx(c) for c in GREEN[3:])
used = set(map(tuple, out.reshape(-1,3).tolist()))
bleed = pole & used
print("palette:", len(PALETTE), "| wrote", f"{OUT}/temple_scene.png", "+ 2x preview")
print("distinct colours used:", len(used))
print("POLE-COLOUR BLEED:", "none — the room takes no side" if not bleed else bleed)
