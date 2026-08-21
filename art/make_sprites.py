#!/usr/bin/env python3
"""uhta — 16x16 pixel art asset generator.
Palette locked to build/uhta-slice.html COL table (CANON v15 render).
Sprites authored as ASCII pixel maps; ramps substituted per belief state.
"""
from PIL import Image, ImageDraw
import os, math, random

OUT = "assets"
os.makedirs(f"{OUT}/sprites", exist_ok=True)
os.makedirs(f"{OUT}/tiles", exist_ok=True)
os.makedirs(f"{OUT}/fx", exist_ok=True)
os.makedirs(f"{OUT}/ui", exist_ok=True)
os.makedirs(f"{OUT}/era", exist_ok=True)

def hx(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2],16), int(s[2:4],16), int(s[4:6],16), a)

# ---- game palette (verbatim from build COL) ----
VOID   = hx('050507'); BG   = hx('0c0c10'); MEMORY = hx('101016')
LIT    = hx('16161d'); ROAD = hx('2f2a22')
HOPE   = hx('63c76b'); HOPE_DIM = hx('2f5a34'); Z_HOPE = hx('9dffb0')
FEAR   = hx('d45b57'); FEAR_DIM = hx('5c2f2e'); Z_FEAR = hx('ff8a86')
GREY   = hx('6a6a72'); PLAYER = hx('f2f2f5'); NIGHT = hx('05050a')
GOLD   = hx('d9c98a')
# extended ramp stops (derived, stay in family)
OUTLINE   = hx('0e0e12')
GREY_D    = hx('3a3a40'); GREY_L  = hx('9a9aa2')
HOPE_XD   = hx('1d3a22'); HOPE_XL = hx('d6ffdd')
FEAR_XD   = hx('3c1f1e'); FEAR_XL = hx('ffc7c4')
ROAD_L    = hx('4a4136'); ROAD_D  = hx('221e19')
WHITE_D   = hx('9a9aa2'); WHITE_L = hx('ffffff')
GOLD_D    = hx('8a7c4e')
T = (0,0,0,0)

def ramp(d,m,l): return {'D':d,'M':m,'L':l}

RAMPS = {
    'grey':      ramp(GREY_D, GREY, GREY_L),
    'hope_tent': ramp(HOPE_XD, HOPE_DIM, HOPE),
    'hope_dev':  ramp(HOPE_DIM, HOPE, Z_HOPE),
    'fear_tent': ramp(FEAR_XD, FEAR_DIM, FEAR),
    'fear_dev':  ramp(FEAR_DIM, FEAR, Z_FEAR),
    'zeal_hope': ramp(HOPE, Z_HOPE, HOPE_XL),
    'zeal_fear': ramp(FEAR, Z_FEAR, FEAR_XL),
    'white':     ramp(WHITE_D, PLAYER, WHITE_L),
}

def render_map(rows, ramp_map, extra=None):
    h = len(rows); w = len(rows[0])
    img = Image.new('RGBA', (w,h), T)
    px = img.load()
    table = {'.':T, 'O':OUTLINE, 'G':GOLD, 'g':GOLD_D, 'K':VOID}
    table.update(ramp_map)
    if extra: table.update(extra)
    for y,row in enumerate(rows):
        for x,c in enumerate(row):
            px[x,y] = table.get(c, T)
    return img

# =====================================================================
# CHARACTERS — small hooded wanderer, 16x16, ~12px figure
# =====================================================================
WANDERER = [
"................",
"................",
"......OOOO......",
".....OMMMMO.....",
".....OMLLMO.....",
".....ODDDDO.....",
".....OMLLMO.....",
"......OMMO......",
".....OMMMMO.....",
"....OMMMMMMO....",
"....OMDMMDMO....",
"....OMDMMDMO....",
"....ODMMMMDO....",
".....ODDDDO.....",
".....OD..DO.....",
"......O..O......",
]

# zealot: bigger presence, gold staff + light halo dots
ZEALOT = [
".....L..L...G...",
"......OOOO..g...",
"...L.OMMMMO.g.L.",
"....OMLLLLMOg...",
"....OMDDDDMOg...",
"....OMLLLLMOg...",
".....OMMMMO.g...",
"....OMMMMMMOg...",
"...OMMLMMLMMg...",
"..OMMDMMMMDMg...",
"..OMDMMMMMMDg...",
"..OMDMMMMMMDg...",
"..ODMMMMMMMDg...",
"...ODDDDDDDOg...",
"...OD.OOO.DOg...",
"....O.....O.....",
]

# loner: grey wanderer with faint questing halo dots
LONER = [
"................",
"....w......w....",
"......OOOO......",
".....OMMMMO.....",
".w...OMLLMO...w.",
".....ODDDDO.....",
".....OMLLMO.....",
"......OMMO......",
".....OMMMMO.....",
"....OMMMMMMO....",
".w..OMDMMDMO..w.",
"....OMDMMDMO....",
"....ODMMMMDO....",
".....ODDDDO.....",
"....w.OD.DO.w...",
"......O..O......",
]

# burnout: hunched kneeling figure (grey), frozen ring drawn separately
BURNOUT = [
"................",
"................",
"................",
"................",
"......OOOO......",
".....OMMMMO.....",
".....ODDDDO.....",
".....OMMMMO.....",
"....OMMMMMMO....",
"...OMMDMMDMMO...",
"...OMDMMMMDMO...",
"...ODMMMMMMDO...",
"...ODDDDDDDDO...",
"....OD.OO.DO....",
"................",
"................",
]

# player avatar: white flame-bearer; F/f = pole flame color
AVATAR = [
".......F........",
"......FLF.......",
"......fFf.......",
"......OOOO......",
".....OMLLMO.....",
".....OLLLLO.....",
".....ODLLDO.....",
"......OMMO......",
"....OMMMMMMO....",
"...OMMLMMLMMO...",
"...OMMFMMFMMO...",
"...OMMLMMLMMO...",
"...OMDMMMMDMO...",
"....ODDDDDDO....",
"....OD.OO.DO....",
".....O....O.....",
]

chars = {}
for state in ['grey','hope_tent','hope_dev','fear_tent','fear_dev']:
    chars[f'wanderer_{state}'] = render_map(WANDERER, RAMPS[state])
chars['zealot_hope'] = render_map(ZEALOT, RAMPS['zeal_hope'])
chars['zealot_fear'] = render_map(ZEALOT, RAMPS['zeal_fear'])
chars['loner'] = render_map(LONER, RAMPS['grey'], extra={'w':GREY_L[:3]+(120,)})
chars['burnout'] = render_map(BURNOUT, RAMPS['grey'])
chars['avatar_hope'] = render_map(AVATAR, RAMPS['white'],
    extra={'F':HOPE, 'f':HOPE_DIM})
chars['avatar_fear'] = render_map(AVATAR, RAMPS['white'],
    extra={'F':FEAR, 'f':FEAR_DIM})

for name,img in chars.items():
    img.save(f"{OUT}/sprites/{name}.png")

# =====================================================================
# TILES — 16x16, programmatic where noise helps
# =====================================================================
rng = random.Random(19)  # run 19 :)

def noise_tile(base, fleck, n=10, seed=1):
    r = random.Random(seed)
    img = Image.new('RGBA',(16,16),base)
    px = img.load()
    for _ in range(n):
        px[r.randrange(16), r.randrange(16)] = fleck
    return img

tiles = {}
tiles['ground_lit']    = noise_tile(LIT,    hx('1c1c25'), 12, 2)
tiles['ground_memory'] = noise_tile(MEMORY, hx('15151c'), 10, 3)
tiles['ground_void']   = noise_tile(VOID,   hx('0a0a10'),  6, 4)

def road_tile(edge, mid, fleck, seed):
    img = noise_tile(LIT, hx('1c1c25'), 8, seed)
    px = img.load(); r = random.Random(seed+7)
    for y in range(16):
        # worn path running vertically w/ ragged edges
        x0 = 4 + (1 if r.random()<0.5 else 0)
        x1 = 11 + (1 if r.random()<0.5 else 0)
        for x in range(x0, x1+1):
            px[x,y] = mid if 5 < x < 10 else edge
    for _ in range(9):
        px[r.randrange(5,11), r.randrange(16)] = fleck
    return img

tiles['road_neutral'] = road_tile(ROAD_D, ROAD, ROAD_L, 11)
tiles['road_hope']    = road_tile(HOPE_XD, hx('27402a'), HOPE_DIM, 12)
tiles['road_fear']    = road_tile(FEAR_XD, hx('4a2a28'), FEAR_DIM, 13)

# ---- v1.1 landscape detail: rocky base ground, lush grass (hope), embers (fear) ----
def rock_tile(seed):
    r = random.Random(seed)
    img = Image.new('RGBA',(16,16),hx('16161d'))
    px = img.load()
    for _ in range(14): px[r.randrange(16),r.randrange(16)] = hx('101016')
    for _ in range(6):  px[r.randrange(16),r.randrange(16)] = hx('1c1c25')
    for _ in range(r.randint(2,3)):   # stones w/ highlight + shadow
        sx,sy = r.randrange(1,12), r.randrange(1,11)
        w,h = r.randint(2,4), r.randint(2,3)
        for yy in range(h):
            for xx in range(w): px[min(15,sx+xx),min(15,sy+yy)] = hx('23232b')
        px[sx,sy] = hx('2e2e38')
        for xx in range(w): px[min(15,sx+xx),min(15,sy+h)] = hx('0d0d11')
    cx,cy = r.randrange(2,13), r.randrange(2,12)     # crack
    for _ in range(r.randint(3,5)):
        px[cx,cy]=hx('0f0f14'); cx=max(0,min(15,cx+r.choice([-1,0,1]))); cy=min(15,cy+1)
    return img

def grass_tile(seed):
    r = random.Random(seed)
    img = Image.new('RGBA',(16,16),hx('1c3f24'))
    px = img.load()
    for _ in range(10): px[r.randrange(16),r.randrange(16)] = hx('16341d')
    for _ in range(10):                               # blade tufts, bright tips
        bx,by = r.randrange(16), r.randrange(2,16)
        h = r.randint(2,3)
        for k in range(h):
            px[bx,max(0,by-k)] = hx('2f5a34') if k<h-1 else hx('63c76b')
    for _ in range(3): px[r.randrange(16),r.randrange(16)] = hx('9dffb0')
    return img

def ember_tile(seed):
    r = random.Random(seed)
    img = Image.new('RGBA',(16,16),hx('391f1d'))
    px = img.load()
    for _ in range(10): px[r.randrange(16),r.randrange(16)] = hx('241312')
    for _ in range(7):
        bx,by = r.randrange(1,15), r.randrange(1,15)
        px[bx,by]=hx('5c2f2e'); px[min(15,bx+1),by]=hx('5c2f2e')
    for _ in range(4): px[r.randrange(16),r.randrange(16)] = hx('d45b57')
    for _ in range(2): px[r.randrange(16),r.randrange(16)] = hx('ff8a86')
    return img

for i,v in enumerate('abc'):
    tiles[f'rock_{v}']  = rock_tile(31+i)
    tiles[f'grass_{v}'] = grass_tile(61+i)
    tiles[f'ember_{v}'] = ember_tile(91+i)

# settlement structures — hope: open hall (single square, door, banner)
SETTLE_HOPE = [
"................",
".......G........",
".......G........",
"......FGF.......",
"...OOOOOOOOOO...",
"...OMMMMMMMMO...",
"...OMLLLLLLMO...",
"...OMMMMMMMMO...",
"...ODDDDDDDDO...",
"...ODMMMMMMDO...",
"...ODMMOOMMDO...",
"...ODMMOKMMDO...",
"...ODMMOKMMDO...",
"...ODDDDDDDDO...",
"..OODDDDDDDDOO..",
"................",
]
# fear: double-walled keep with spikes
SETTLE_FEAR = [
"................",
"..O..O.OO.O..O..",
"..OO.OOMMOO.OO..",
"..OMOOMMMMOOMO..",
"..OMMMMLLMMMMO..",
"..ODMMMMMMMMDO..",
"..ODOOOOOOOODO..",
"..ODOMMMMMMODO..",
"..ODOMLLLLMODO..",
"..ODOMMMMMMODO..",
"..ODODDDDDDODO..",
"..ODODMOOMDODO..",
"..ODODMOKMDODO..",
"..ODDDDDDDDDDO..",
".OODDDDDDDDDDOO.",
"................",
]
tiles['settlement_hope'] = render_map(SETTLE_HOPE, RAMPS['hope_dev'],
    extra={'F':HOPE, 'K':VOID})
tiles['settlement_fear'] = render_map(SETTLE_FEAR, RAMPS['fear_dev'],
    extra={'K':VOID})

# beacon — post with flame, hope/fear
BEACON = [
"................",
".......LL.......",
"......LMML......",
"......FMMF......",
".......FF.......",
"......OggO......",
".......gg.......",
".......gg.......",
".......gg.......",
".......gg.......",
".......gg.......",
"......Ogg0......",
".....OggggO.....",
"....OggggggO....",
"....OOOOOOOO....",
"................",
]
tiles['beacon_hope'] = render_map(BEACON, RAMPS['hope_dev'],
    extra={'F':HOPE_DIM, '0':OUTLINE})
tiles['beacon_fear'] = render_map(BEACON, RAMPS['fear_dev'],
    extra={'F':FEAR_DIM, '0':OUTLINE})

for name,img in tiles.items():
    img.save(f"{OUT}/tiles/{name}.png")

# =====================================================================
# EFFECTS — 16x16
# =====================================================================
fx = {}

def ring(color, r=6.5, w=1.4):
    img = Image.new('RGBA',(16,16),T); px = img.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x-7.5, y-7.5)
            if abs(d-r) < w*0.5:
                px[x,y] = color
    return img

fx['ring_frozen_hope'] = ring(Z_HOPE)
fx['ring_frozen_fear'] = ring(Z_FEAR)

CLASH = [
"................",
".......G........",
"...w...G...w....",
"....w..L..w.....",
".....wGLGw......",
"......LLL.......",
"..GGLLwwwLLGG...",
"......LLL.......",
".....wGLGw......",
"....w..L..w.....",
"...w...G...w....",
".......G........",
"................",
"................",
"................",
"................",
]
fx['clash'] = render_map(CLASH, ramp(GOLD_D, GOLD, WHITE_L),
    extra={'w':WHITE_L, 'L':WHITE_L, 'G':GOLD})

SPARKLE = [
"................",
".......L........",
".......L........",
".....D.L.D......",
"......DLD.......",
"...LLDLMLDLL....",
"......DLD.......",
".....D.L.D......",
".......L........",
".......L........",
"................",
"................",
"................",
"................",
"................",
"................",
]
fx['convert_sparkle_hope'] = render_map(SPARKLE, RAMPS['zeal_hope'])
fx['convert_sparkle_fear'] = render_map(SPARKLE, RAMPS['zeal_fear'])

PUFF = [
"................",
"................",
"....MM..M.......",
"...MDDM.........",
"....MM...MM.....",
"..M.....MDDM....",
".........MM..M..",
"....M...........",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
]
fx['scatter_puff'] = render_map(PUFF, RAMPS['grey'])

FLAME = [
"................",
".......L........",
"......LL........",
"......LLL.......",
".....LLML.......",
".....MLMML......",
"....MMLMMML.....",
"....MMMLMMM.....",
"...DMMLLLMMD....",
"...DMLLLLLMD....",
"...DMLLLLLMD....",
"....DMLLLMD.....",
".....DMMMD......",
"......DDD.......",
"................",
"................",
]
fx['flame_hope'] = render_map(FLAME, RAMPS['hope_dev'])
fx['flame_fear'] = render_map(FLAME, RAMPS['fear_dev'])
fx['flame_white'] = render_map(FLAME, RAMPS['white'])

ROAR = [
"................",
"..D.............",
"..MD............",
"..DMD...........",
"...DMD..D.......",
"..D.DMD.MD......",
"..MD.DMDDMD.....",
"..MD.DMDDMD.....",
"..D.DMD.MD......",
"...DMD..D.......",
"..DMD...........",
"..MD............",
"..D.............",
"................",
"................",
"................",
]
fx['roar'] = render_map(ROAR, RAMPS['fear_dev'])

for name,img in fx.items():
    img.save(f"{OUT}/fx/{name}.png")

# =====================================================================
# UI — belief meter + action icons
# =====================================================================
ui = {}

# belief scale bar: 50x8, fear left, grey middle, hope right, frame
bar = Image.new('RGBA',(50,8),T); d = ImageDraw.Draw(bar)
d.rectangle([0,0,49,7], outline=OUTLINE, fill=BG)
for i in range(24):
    t = i/23
    d.line([(1+i,1),(1+i,6)], fill=tuple(int(FEAR[j]*(1-t)+GREY_D[j]*t) for j in range(3))+(255,))
for i in range(24):
    t = i/23
    d.line([(25+i,1),(25+i,6)], fill=tuple(int(GREY_D[j]*(1-t)+HOPE[j]*t) for j in range(3))+(255,))
d.line([(24,1),(24,6)], fill=GREY)
ui['belief_meter'] = bar

# stamina pip
pip = Image.new('RGBA',(6,6),T); d = ImageDraw.Draw(pip)
d.ellipse([0,0,5,5], fill=PLAYER, outline=OUTLINE)
ui['stamina_pip'] = pip

ICON_WAIT = [
"................",
"...OOOOOOOOOO...",
"....OMMMMMMO....",
"....OMMMMMMO....",
".....ODMMDO.....",
"......ODDO......",
".......OO.......",
".......OO.......",
"......OMDO......",
".....OMMDDO.....",
"....OMMMDDDO....",
"....OMMMMDDO....",
"...OOOOOOOOOO...",
"................",
"................",
"................",
]
ui['icon_wait'] = render_map(ICON_WAIT, RAMPS['grey'])

ICON_SLEEP = [
"................",
"......OOOO......",
"....OOMMMMOO....",
"...OMMMOOOOO....",
"...OMMO.........",
"..OMMO..........",
"..OMMO..........",
"..OMMO..........",
"..OMMO..........",
"...OMMO.........",
"...OMMMOOOOO....",
"....OOMMMMOO....",
"......OOOO......",
"................",
"................",
"................",
]
ui['icon_sleep'] = render_map(ICON_SLEEP, ramp(GOLD_D, GOLD, WHITE_L))

ICON_RAZE = [
"................",
"...O.O..O.O.....",
"...OOOOOOOO.....",
"...OMMLLMMO.....",
"...OMMLMMMO.....",
"...ODMLMMDO.....",
"...ODMGLMDO.....",
"...ODMMGMDO.....",
"...ODDMGDDO.....",
"...ODDGMDDO.....",
"...ODDMGDDO.....",
"..ODDDGGDDDO....",
"..OOOOOOOOOO....",
"................",
"................",
"................",
]
ui['icon_raze'] = render_map(ICON_RAZE, RAMPS['grey'])

# ---- title wordmark: "uhta" pixel type, white with drop shadow ----
LET = {
 'u':["....","....","X..X","X..X","X..X","X..X",".XX."],
 'h':["X...","X...","XXX.","X..X","X..X","X..X","X..X"],
 't':[".X..",".X..","XXX.",".X..",".X..",".X..","..XX"],
 'a':["....","....",".XX.","...X",".XXX","X..X",".XXX"],
}
word = 'uhta'
wm = Image.new('RGBA',(4*len(word)+len(word)-1+2, 10), T)
wpx = wm.load()
for pass_i,(ox,oy,cols) in enumerate([(2,2,None),(1,1,'main')]):  # shadow then main
    xoff = 0
    for ch in word:
        for ry,row in enumerate(LET[ch]):
            for rx,c in enumerate(row):
                if c=='X':
                    if cols is None: wpx[xoff+rx+ox-1, ry+oy-1+1] = OUTLINE
                    else: wpx[xoff+rx, ry+1] = WHITE_L if ry<4 else PLAYER
        xoff += 5
ui['title_wordmark'] = wm

ui['icon_flame_hope'] = fx['flame_hope'].copy()
ui['icon_flame_fear'] = fx['flame_fear'].copy()
ui['icon_roar'] = fx['roar'].copy()
ui['icon_beacon'] = tiles['beacon_hope'].copy()

for name,img in ui.items():
    img.save(f"{OUT}/ui/{name}.png")

# =====================================================================
# ERA PROGRESSION (2026-07-23) — passage of time through art, presentation-only.
# Era 1 = the existing sprites above (hooded wanderers / hall & keep / worn dirt).
# Era 2 "Village": villager figures, cottage/motte settlements, cobbled roads.
# Era 3 "Victorian": townsfolk, row houses / mill, paved roads.
# Plus beacon_site (unlit ruined basin) for the discoverable-beacons feature.
# CRITICAL: appended as a FIFTH group so atlas frames 0-49 keep their exact
# insertion order (the build's F map hardcodes them); new frames land at 50+.
# =====================================================================

# villager: upright, simple tunic + brimmed coif — a readably more "settled" silhouette
VILLAGER = [
"................",
"......OOOO......",
".....OMMMMO.....",
"....OOOOOOOO....",
".....OLLLLO.....",
".....OLDDLO.....",
"......OLLO......",
".....OMMMMO.....",
"....OMMMMMMO....",
"....OMDLLDMO....",
"....OMDLLDMO....",
"....ODMMMMDO....",
".....ODDDDO.....",
".....OD..DO.....",
".....OD..DO.....",
"......O..O......",
]

# townsfolk: tall thin silhouette, top hat, long coat, small collar highlight
TOWNSFOLK = [
".....OOOOOO.....",
".....OMMMMO.....",
".....OMMMMO.....",
"....OOOOOOOO....",
".....OLLLLO.....",
".....OLDDLO.....",
"......OLLO......",
".....OLMMLO.....",
".....OMMMMO.....",
".....OMDDMO.....",
".....OMDDMO.....",
".....OMMMMO.....",
".....ODMMDO.....",
".....ODDDDO.....",
"......OD.DO.....",
"......O..O......",
]

# era-2 hope settlement: thatched cottage cluster + small gold-crossed chapel — cozy, open
SETTLE_HOPE_V2 = [
"................",
"..........G.....",
".........GGG....",
"....OO....G.....",
"...OLLO..OOO....",
"..OLLLLO.OMLO...",
".OLLLLLLOOMLMO..",
".OMMMMMMOMLLMO..",
".OMDGDMMOMMMMO..",
".OMDDDMMOMGMMO..",
".OMDDDMMOMMMMO..",
".OMMMMMMOMDMMO..",
"OOOOOOOOOOOOOOO.",
"..O..O...O..O...",
"................",
"................",
]

# era-2 fear settlement: squat stone motte tower inside a spiked palisade
SETTLE_FEAR_V2 = [
"................",
".......OO.......",
"..O...OMMO...O..",
"..OO..OMMO..OO..",
"..OMO.ODDO.OMO..",
"..OMOOMMMMOOMO..",
"..OMOMLLLLMOMO..",
"..OMOMMMMMMOMO..",
"..OMOMDOODMOMO..",
"..OMOMDOODMOMO..",
"..OMODMMMMDOMO..",
"..OMODDDDDDOMO..",
"..ODDDDDDDDDDO..",
".OODDDDDDDDDDOO.",
"................",
"................",
]

# era-3 hope settlement: row houses, chimneys, warm gold-lit windows, a lamp post
SETTLE_HOPE_V3 = [
"..O..O.....O....",
"..O..O.....O..G.",
".OOOOOOOOOOO..g.",
".OMMMMMMMMMO..g.",
".OMLMMLMMLMO..g.",
".OMGMMGMMGMO..g.",
".OMMMMMMMMMO..g.",
".OMGMMGMMGMO..g.",
".OMMMMMMMMMO..g.",
".OMDOMMDOMMO..g.",
".OMDOMMDOMMO..g.",
".ODDDDDDDDDO.OgO",
"OODDDDDDDDDOOOOO",
"................",
"................",
"................",
]

# era-3 fear settlement: dark mill silhouette, smokestack ('w' = grey smoke), barred windows
SETTLE_FEAR_V3 = [
"...ww...........",
"..ww..OO........",
"......OMO.......",
"......OMO.......",
"......OMO.......",
".OOOOOOMOOOOOO..",
".OMMMMMMMMMMMO..",
".OMDODDODDODMO..",
".OMDODDODDODMO..",
".OMMMMMMMMMMMO..",
".OMDODDODDODMO..",
".OMDODDODDODMO..",
".ODDDDDDDDDDDO..",
"OODDDDDDDDDDDOO.",
"................",
"................",
]

# beacon_site: the UNLIT ruined basin (GDD §2.2 opening) — the beacon post minus its
# flame, more ruined: broken rim/base pixels, tarnished gold on a grey stone ramp
BEACON_SITE = [
"................",
"................",
"................",
"................",
"................",
"................",
".......gg.......",
"......Ogg.......",
".......gg.......",
".......gg.......",
".....g.gg.g.....",
"......Dgg0......",
".....OggggO.....",
"....Og.gggDO....",
"....OO.OOOOO....",
"................",
]

for _m in (VILLAGER,TOWNSFOLK,SETTLE_HOPE_V2,SETTLE_FEAR_V2,SETTLE_HOPE_V3,SETTLE_FEAR_V3,BEACON_SITE):
    assert len(_m)==16 and all(len(r)==16 for r in _m), "era map must be 16x16"

# era-2 cobbled road: offset stone courses in the path bed, pole-tinted like road_tile
def cobble_road_tile(edge, mid, fleck, seed):
    img = noise_tile(LIT, hx('1c1c25'), 8, seed)
    px = img.load(); r = random.Random(seed+7)
    for y in range(16):
        for x in range(4,12):
            px[x,y] = edge            # mortar bed
    for cy in range(0,16,3):          # 2-tall stone courses, offset every other course
        off = 4 + (2 if (cy//3)%2 else 0)
        for cx in range(off-4, 12, 4):
            for yy in range(2):
                for xx in range(3):
                    X,Yc = cx+xx, cy+yy
                    if 4<=X<12 and 0<=Yc<16:
                        px[X,Yc] = mid
    for _ in range(7):
        px[r.randrange(4,12), r.randrange(16)] = fleck
    return img

# era-3 paved road: flat slab bed, curb lines, dashed center seam + slab joints, pole-tinted
def paved_road_tile(edge, mid, fleck, seed):
    img = noise_tile(LIT, hx('1c1c25'), 8, seed)
    px = img.load(); r = random.Random(seed+7)
    for y in range(16):
        for x in range(4,12):
            px[x,y] = mid             # slab bed
        px[4,y] = edge; px[11,y] = edge          # curbs
        if y%2==0: px[8,y] = edge                # dashed center seam
    for jy in (5,11):                            # slab joints
        for x in range(5,11): px[x,jy] = edge
    for _ in range(5):
        px[r.randrange(5,11), r.randrange(16)] = fleck
    return img

era = {}
for state in ['grey','hope_tent','hope_dev','fear_tent','fear_dev']:
    era[f'villager_{state}'] = render_map(VILLAGER, RAMPS[state])
for state in ['grey','hope_tent','hope_dev','fear_tent','fear_dev']:
    era[f'townsfolk_{state}'] = render_map(TOWNSFOLK, RAMPS[state])
era['settlement_hope_v2'] = render_map(SETTLE_HOPE_V2, RAMPS['hope_dev'])
era['settlement_fear_v2'] = render_map(SETTLE_FEAR_V2, RAMPS['fear_dev'])
era['settlement_hope_v3'] = render_map(SETTLE_HOPE_V3, RAMPS['hope_dev'])
era['settlement_fear_v3'] = render_map(SETTLE_FEAR_V3, RAMPS['fear_dev'], extra={'w':GREY})
era['road_neutral_v2'] = cobble_road_tile(ROAD_D,  ROAD,         ROAD_L,   21)
era['road_hope_v2']    = cobble_road_tile(HOPE_XD, hx('27402a'), HOPE_DIM, 22)
era['road_fear_v2']    = cobble_road_tile(FEAR_XD, hx('4a2a28'), FEAR_DIM, 23)
era['road_neutral_v3'] = paved_road_tile(ROAD_D,  ROAD,         ROAD_L,   31)
era['road_hope_v3']    = paved_road_tile(HOPE_XD, hx('27402a'), HOPE_DIM, 32)
era['road_fear_v3']    = paved_road_tile(FEAR_XD, hx('4a2a28'), FEAR_DIM, 33)
era['beacon_site']     = render_map(BEACON_SITE, RAMPS['grey'], extra={'0':OUTLINE})

# ---------------------------------------------------------------------
# ART PASS 3 (2026-07-23) — player-road two-stage aging: 'compacted' stage.
# Director: the player's trail stays its own category — trodden ground first,
# paved once a generation passes. These three tiles are the COMPACTED stage
# (the existing road_*_v3 paved tiles are reused as the aged stage).
# Trodden-earth look: the rock/ground base with a subtle flattened path —
# no raised bed, no stones in the band, faint pole tint on the path only.
# APPEND-ONLY: added at the end of the era group -> frames 71/72/73;
# the first 71 atlas names keep their exact order (asserted below).
# ---------------------------------------------------------------------
def compacted_tile(tint, seed):
    r = random.Random(seed)
    img = Image.new('RGBA',(16,16),hx('16161d'))          # same base as rock_tile
    px = img.load()
    for _ in range(14): px[r.randrange(16),r.randrange(16)] = hx('101016')
    for _ in range(6):  px[r.randrange(16),r.randrange(16)] = hx('1c1c25')
    for _ in range(2):                                     # a stone or two OUTSIDE the band only
        sx = r.choice([r.randrange(0,3), r.randrange(12,14)]); sy = r.randrange(1,12)
        for xx in range(r.randint(2,3)): px[min(15,sx+xx),sy] = hx('23232b')
    for y in range(16):                                    # flattened trodden band, ragged edge
        x0 = 5 + (1 if r.random()<0.3 else 0)
        x1 = 10 - (1 if r.random()<0.3 else 0)
        for x in range(x0, x1+1):
            # gently lighter than base, center worn smoothest: "the ground remembers you"
            px[x,y] = hx('23232c') if 6 < x < 9 else hx('1e1e26')
    for _ in range(8):                                     # faint pole tint, path only
        px[r.randrange(5,11), r.randrange(16)] = tint
    for _ in range(4):                                     # footworn dark specks in the band
        px[r.randrange(5,11), r.randrange(16)] = hx('14141a')
    return img

era['compacted_neutral'] = compacted_tile(hx('2b2620'), 41)   # dim ROAD-family
era['compacted_hope']    = compacted_tile(hx('27452a'), 42)   # dim hope
era['compacted_fear']    = compacted_tile(hx('422725'), 43)   # dim fear

# ---------------------------------------------------------------------
# ART PASS 3b (2026-07-23) — factory smokestack smoke animation frames.
# 3 semi-transparent grey 16x16 puffs at increasing dispersal; cycled by
# the render layer above the era-3 fear factory's stack (render-only).
# APPEND-ONLY: era group tail -> 16px atlas frames 74/75/76 (asserted).
# ---------------------------------------------------------------------
SMOKE_ALPHA = {'s': GREY[:3]+(150,), 'S': GREY_L[:3]+(130,), 'e': GREY_D[:3]+(110,)}
SMOKE_A = [               # tight fresh puff
"................",
"................",
"................",
"................",
"................",
"......sss.......",
".....sSSSs......",
"....sSSSSSs.....",
"....sSSSSSs.....",
".....sSSSs......",
"......sss.......",
"................",
"................",
"................",
"................",
"................",
]
SMOKE_B = [               # drifting, looser — split puffs
"................",
"................",
"................",
"....ss..........",
"...sSSs...ss....",
"....sSs..sSSs...",
"..........sSs...",
"....es.....s....",
"...sSSs.........",
"....se...ss.....",
"........sSs.....",
".........s......",
"................",
"................",
"................",
"................",
]
SMOKE_C = [               # thin dissipating wisps
"................",
"..s.......s.....",
".....e.......s..",
"...s......s.....",
".........e......",
"..e...s......s..",
"............s...",
"....s....e......",
".e..............",
"..s.....s....e..",
"................",
".....e......s...",
"...s............",
"................",
"................",
"................",
]
for _m in (SMOKE_A,SMOKE_B,SMOKE_C):
    assert len(_m)==16 and all(len(r)==16 for r in _m), "smoke map must be 16x16"
era['smoke_a'] = render_map(SMOKE_A, RAMPS['grey'], extra=SMOKE_ALPHA)
era['smoke_b'] = render_map(SMOKE_B, RAMPS['grey'], extra=SMOKE_ALPHA)
era['smoke_c'] = render_map(SMOKE_C, RAMPS['grey'], extra=SMOKE_ALPHA)

for name,img in era.items():
    img.save(f"{OUT}/era/{name}.png")

# =====================================================================
# ART PASS 3 (2026-07-23) — HD 32x32 character set (SECOND atlas: atlas32).
# Director: avatar "a bit larger, humanoid, glowing aspects — red veins for
# fear, vines growing for hope", plus "higher resolution pixel characters".
# Same palette / RAMPS / belief-state substitution as the 16px set; authored
# as 32x32 ASCII maps (rows may be short — padded right with transparent).
# The 16px atlas keeps tiles/fx/ui/settlements/beacons; ONLY characters move
# to the HD sheet in the build.
# =====================================================================
os.makedirs(f"{OUT}/hd", exist_ok=True)

def pad32(rows):
    assert len(rows) <= 32, f"hd map has {len(rows)} rows"
    out = []
    for i,r in enumerate(rows):
        assert len(r) <= 32, f"hd map row {i} is {len(r)} chars"
        out.append(r + '.'*(32-len(r)))
    while len(out) < 32: out.append('.'*32)
    return out

def sprinkle(rows, pts, ch='w'):
    g = [list(r) for r in rows]
    for x,y in pts:
        if g[y][x] == '.': g[y][x] = ch
    return [''.join(r) for r in g]

# deep-hooded wanderer (era 1) — dark hood cavity, cloak folds, wooden walking staff
HD_WANDERER = pad32([
"",
"",
".............OOOOOO",
"...........OOMMMMMMOO",
"..........OMMMMMMMMMMO",
".........OMMMMMMMMMMMMO",
".........OMMLLLLLLLLMMO",
"........OMMLDDDDDDDDLMMO",
"........OMLDDDDDDDDDDLMO",
"........OMLDDLDDDDLDDLMO...gg",
"........OMLDDDDDDDDDDLMO...Gg",
"........OMMLDDDDDDDDLMMO....g",
".........OMMLLLLLLLLMMO.....g",
".........OMMMMMMMMMMMMO.....g",
"..........OMMMMMMMMMMO......g",
".........OMMMMMMMMMMMMO.....g",
"........OMMMMMMMMMMMMMMO....g",
".......OMMMMMMMMMMMMMMMMOOOOg",
".......OMMDMMMMMMMMMMDMMMMMMg",
"......OMMDMMMMMMMMMMMMDMMO..g",
"......OMMDMMMMMMMMMMMMDMMO..g",
"......OMDMMMLMMMMMMLMMMDMO..g",
"......OMDMMMMLMMMMLMMMMDMO..g",
"......OMDMMMMMMMMMMMMMMDMO..g",
"......ODMMMMMMMMMMMMMMMMDO..g",
"......ODMMMMMMMMMMMMMMMMDO..g",
"......ODDMMMMMMMMMMMMMMDDO..g",
".......ODDDDDDDDDDDDDDDDO...g",
".......ODDDDDDDDDDDDDDDO....g",
"........ODD...DDDD...DDO...OgO",
"........OD.....DD.....DO",
".........O.....OO.....O",
])

# villager (era 2) — brimmed coif, open face, belted tunic, satchel at the hip
HD_VILLAGER = pad32([
"",
"",
"............OOOOOOO",
"..........OOMMMMMMMOO",
".........OMMMMMMMMMMMO",
"........OOOOOOOOOOOOOOO",
".........OLLLLLLLLLLLO",
".........OLLDDLLLLDDLO",
".........OLLLLLLLLLLLO",
".........OLLLDDDDLLLLO",
"..........OLLLLLLLLLO",
"..........OMMLLLLMMO",
".........OMMgMMMMMMMO",
"........OMMMMgMMMMMMMO",
".......OMMMMMMgMMMMMMMO",
".......OMDMMMMMgMMMMDMO",
"......OMMDMMMMMMgMMMDMMO",
"......OMDMMMMMMMMgMMMDMO",
"......OMDMMMMMMMMMgMMDMO",
"......OMDMDDDDDDDDDDMDMO",
"......OMDMMMMMMMMMMMMDMOgg",
"......OMDMMMMMMMMMMMDMOggg",
"......ODMMMMMMMMMMMMMDOggg",
"......ODMMMMMMMMMMMMMDO.g",
".......ODMMMMMMMMMMMDO",
".......ODDDDDDDDDDDDDO",
".......OD.DDDD..DDDD.DO",
"........O.ODDO..ODDO.O",
"..........ODDO..ODDO",
"..........ODDO..ODDO",
"..........ODDD..DDDO",
"..........OOOO..OOOO",
])

# townsfolk (era 3) — top hat, long coat with button line, cane
HD_TOWNSFOLK = pad32([
"..........OOOOOOOOO",
"..........OMMMMMMMO",
"..........OMMMMMMMO",
"..........OMMMMMMMO",
"..........OMMMMMMMO",
"........OOOOOOOOOOOOO",
".........OLLLLLLLLLO",
".........OLDDLLLDDLO",
".........OLLLLLLLLLO",
".........OLLDDDDLLLO",
"..........OLLLLLLLO",
"..........OMLLLLMMO",
".........OMMLLLLMMMO",
"........OMMMMMMMMMMMO",
".......OMMMMMMMMMMMMMO",
".......OMDMMMLMMMMMDMO",
".......OMDMMMMMMMMMDMO",
".......OMDMMLMLMMMMDMO",
".......OMDMMMMMMMMMDMO..gg",
".......OMDMMMLMMMMMDMO...g",
".......OMDMMMMMMMMMDMO...g",
".......OMDMMMLMMMMMDMO...g",
".......OMDMMMMMMMMMDMO...g",
".......ODMMMMMMMMMMDO....g",
".......ODMMMMMMMMMMDO....g",
".......ODMMMMMMMMMMDO....g",
".......ODDMMMMMMMMDDO....g",
".......ODDDDDDDDDDDDO....g",
"........OD.DDD..DDD.O....g",
"..........ODDO..ODDO.....g",
"..........ODDO..ODDO....OgO",
"..........OOOO..OOOO",
])

# zealot — imposing anchor: halo motes, gold staff with a burning orb, wide robe
HD_ZEALOT = pad32([
"..........................GG",
"..L......................GGGG",
"......L...OOOOOOOO.......GGGG",
"..........OMMMMMMO........GG",
".L.......OMMLLLLMMO........g",
".........OMLLLLLLMO........g",
"......L..OMLDDDDLMO........g",
".........OMLDDDDLMO........g",
".L.......OMLLLLLLMO........g",
".........OMMLLLLMMO....L...g",
"......L...OMMMMMMO.........g",
"..........OMMMMMMO.....L...g",
".L.......OMMMMMMMMO........g",
".......OMMMMMMMMMMMMO..L...g",
"......OMMMMMMMMMMMMMMO.....g",
".....OMMMMMMMMMMMMMMMMO....g",
"....OMMLMMMMMMMMMMMMLMMO...g",
"....OMMLMMMMMMMMMMMMLMMOOOOg",
"....OMLMMMMMMMMMMMMMMLMMMMMg",
"....OMLMMDMMMMMMMMDMMLMO...g",
"....OMLMMDMMMMMMMMDMMLMO...g",
"....OMMLMDMMMMMMMMDMLMMO...g",
"....OMMLMDMMMMMMMMDMLMMO...g",
"....OMMMLDMMMMMMMMDLMMMO...g",
"....OMDMMDMMMMMMMMDMMDMO...g",
"....OMDMMDMMMMMMMMDMMDMO...g",
"....ODMMMDMMMMMMMMDMMMDO...g",
"....ODMMMMMMMMMMMMMMMMDO...g",
"....ODDDDDDDDDDDDDDDDDDO...g",
"....ODDDDDDDDDDDDDDDDDDO..OgO",
".....ODD.OOOOOOOOOO.DDO",
"......O..............O",
])

# burnout — kneeling, hollow: bowed head, void-hollow face and chest
HD_BURNOUT = pad32([
"","","","","","","","","","",
"..........OOOOOO",
".........OMMMMMMO",
".........OMMDDMMO",
".........OMDKKDMO",
".........OMMDDMMO",
"..........OMMMMO",
".........OMMMMMMO",
"........OMMMMMMMMOO",
".......OMMDKKDMMMMMO",
".......OMMDKKDMMMMMMO",
"......OMMMDDDDMMMMMMMO",
"......OMMMMMMMMMMDMMMO",
"......OMDMMMMMMMMDMMMO",
"......OMDMMMMMMMMMDMMO",
"......ODMMMMMMMMMMDMMO",
"......ODMMMMMMMMMMMDDO",
".....ODMMMMMMMMMMMMMDO",
".....ODDMMMMMMMMMMMDDO",
".....ODDDDDDDDDDDDDDDO",
"....ODDDDDDDDDDDDDDDDDO",
"....ODDDOODDDDDDOODDDDO",
".....OOO..OOOOOO..OOOO",
])

# THE AVATAR — pale kaiju-esque humanoid: broad shoulders, featureless glowing
# face, the white flame held aloft in the raised hand (baked white; pole reads
# through the veins/vines overlays below + the existing fx tints).
HD_AVATAR_BODY = pad32([
"........................LL",
".......................LLLL",
"......................LLMLL",
"......................MLLLM",
".......................MMM",
"..........OOOOOOOO.....OMO",
".........OMLLLLLLMO....OMO",
"........OMLLLLLLLLMO...OMO",
"........OLLLLLLLLLLO..OMMO",
"........OLLLLLLLLLLO..OMMO",
"........OMLLLLLLLLMO..OMO",
".........OMLLLLLLMO..OMMO",
"..........OMMMMMMO..OMMO",
".......OOOMMMMMMMMOOMMMO",
".....OOMMMMMMMMMMMMMMMMO",
"....OMMMMMMMMMMMMMMMMMMO",
"...OMMMMMMMMMMMMMMMMMMMO",
"...OMMDMMMMMMMMMMMMMDMMO",
"...OMMDMMLLMMMMLLMMMDMO",
"...OMDMMMLLMMMMLLMMMDMO",
"...OMDMMMMMMMMMMMMMMDMO",
"...OMDMMMMMDDDDMMMMMDMO",
"....OMDMMMDMMMMDMMMDMO",
"....OMDMMMMDDDDMMMMDMO",
"....OMMDMMMMMMMMMMDMMO",
".....OMMDMMMMMMMMDMMO",
"......OMMMMMMMMMMMMO",
"......OMMMMOOOOMMMMO",
"......OMMDO....ODMMO",
"......OMMDO....ODMMO",
"......OMMDO....ODMMO",
"......OOOOO....OOOOO",
])

# OVERLAY: branching red vein network (fear) — transparent except the detail.
# r = FEAR, R = Z_FEAR bright node. Chest / arms / legs, avoiding the face.
HD_AVATAR_VEINS_FEAR = pad32([
"","","","","","","","",
"......................r",
"......................R",
"","","",
"........r......R",
"......rrRr....r.rr..r",
"....rR...r...r...rR..r",
"...r......r..r....r...R",
"..........R..r....r",
".........r...R.....r",
".........r...r......r",
"..........r.R........R",
"..........R.r",
"...........rr....r",
"...........r.....R",
"..........rR......r",
"..........r.......r",
".........r.r......rr",
".........r.......r..r",
"........r........r...r",
"........R.......r....R",
"........r.......R",
"........r.......r",
])

# OVERLAY: winding green vines (hope) — n = HOPE_DIM stem, v = HOPE leaf,
# V = Z_HOPE bright tip. Climbing the legs / torso / left arm.
HD_AVATAR_VINES_HOPE = pad32([
"","","","","","","","","","","","","",
".....V.............V",
"....nv.n..........V",
"....n...n........n",
".....v...n.......nv",
"..........n.....n",
"...........n...v",
"..........vn..n",
"...........n.n",
"...........nn..v",
"..........vn.n",
"...........n.nn",
"........v..nn..n",
"...........n...n",
"..........nn...nv",
"..........n.....n",
".........nv.....nn",
".........n.......n",
"........nn.......nv",
"........Vn.......nV",
])

hd = {}
for state in ['grey','hope_tent','hope_dev','fear_tent','fear_dev']:
    hd[f'hd_wanderer_{state}'] = render_map(HD_WANDERER, RAMPS[state])
for state in ['grey','hope_tent','hope_dev','fear_tent','fear_dev']:
    hd[f'hd_villager_{state}'] = render_map(HD_VILLAGER, RAMPS[state])
for state in ['grey','hope_tent','hope_dev','fear_tent','fear_dev']:
    hd[f'hd_townsfolk_{state}'] = render_map(HD_TOWNSFOLK, RAMPS[state])
hd['hd_zealot_hope'] = render_map(HD_ZEALOT, RAMPS['zeal_hope'])
hd['hd_zealot_fear'] = render_map(HD_ZEALOT, RAMPS['zeal_fear'])
hd['hd_loner']   = render_map(
    sprinkle(HD_WANDERER, [(4,3),(27,5),(2,9),(29,12),(3,17),(30,21),(2,25),(28,27),(4,29)]),
    RAMPS['grey'], extra={'w':GREY_L[:3]+(120,)})
hd['hd_burnout'] = render_map(HD_BURNOUT, RAMPS['grey'])
hd['hd_avatar_body']       = render_map(HD_AVATAR_BODY, RAMPS['white'])
hd['hd_avatar_veins_fear'] = render_map(HD_AVATAR_VEINS_FEAR, RAMPS['white'],
    extra={'r':FEAR, 'R':Z_FEAR})
hd['hd_avatar_vines_hope'] = render_map(HD_AVATAR_VINES_HOPE, RAMPS['white'],
    extra={'n':HOPE_DIM, 'v':HOPE, 'V':Z_HOPE})

# =====================================================================
# ART PASS 3b (2026-07-23) — HD 32x32 era settlements (atlas32, APPEND-ONLY
# at 22-25; the first 22 frame indices must not move — asserted below).
# Director: settlement-footprint upsizing approved; the Victorian era gains
# a CLOCKTOWER (hope town) and a FACTORY with a smokestack (fear), whose
# smoke is animated by the render layer (16px smoke_a/b/c frames).
# =====================================================================

# era-2 hope: thatched cottage pair flanking a small gold-crossed chapel,
# stone well out front, warm gold door/window glow.
HD_SETTLE_HOPE_V2 = pad32([
"",
"",
"...............G",
"..............GGG",
"...............G",
"..............OMO",
".............OMMMO",
"............OMLLLMO",
"............OMLLLMO",
"...........OMMMMMMMO",
"...........OOOOOOOOO",
"............OMMMMMO",
".....OO.....OMGGGMO......OO",
"....OLLO....OMGGGMO.....OLLO",
"...OLLLLO...OMMMMMO....OLLLLO",
"..OLLLLLLO..OMMMMMO...OLLLLLLO",
".OLLLLLLLLO.OMMMMMO..OLLLLLLLLO",
"OOOOOOOOOOOOOMMMMMO.OOOOOOOOOOOO",
".OMMMMMMMMO.OMDGDMO..OMMMMMMMMO",
".OMGGMMMMMO.OMDGDMO..OMMMMGGMMO",
".OMGGMMMMMO.OMDGDMO..OMMMMGGMMO",
".OMMMMMMMMO.OMDGDMO..OMMMMMMMMO",
".OMMMMDDMMO.OMMMMMO..OMMDDMMMMO",
".OMMMMDGMMO.OMMMMMO..OMGDDMMMMO",
".OMMMMDDMMO..OOOOO...OMMDDMMMMO",
".OMMMMDDMMO..OMMMO...OMMDDMMMMO",
".ODDDDDDDDO..OKKKO...ODDDDDDDDO",
".OO.OOOO.OO..OOOOO...OO.OOOO.OO",
"",
])

# era-2 fear: squat stone motte tower (void slit windows) ringed by a
# spiked palisade — four flanking sharpened posts + low front fence.
HD_SETTLE_FEAR_V2 = pad32([
"",
"",
"",
"",
"..........OO...OO...OO",
"..........OMMMMMMMMMMO",
"..........OMMMMMMMMMMO",
"..........OMMKMMMMKMMO",
"..........OMMKMMMMKMMO",
"..........OMMMMMMMMMMO",
"..........OMDMMMMMMDMO",
"..........OMMKMMMMKMMO",
"..........OMMKMMMMKMMO",
"..O.......OMMMMMMMMMMO.......O",
"..OO......OMDMMMMMMDMO......OO",
"..OM..O...ODMMMMMMMMDO...O..MO",
"..OM..OO..ODMMMMMMMMDO..OO..MO",
"..OM..OM..ODMMOKKOMMDO..MO..MO",
"..OM..OM..ODMMOKKOMMDO..MO..MO",
"..OM..OM..ODMMOKKOMMDO..MO..MO",
"..OM..OM..ODMMOKKOMMDO..MO..MO",
"..OM..OM..ODMMOKKOMMDO..MO..MO",
"..OM..OM..ODMMOKKOMMDO..MO..MO",
"..OM..OM..ODDDDDDDDDDO..MO..MO",
"..OM..OM..ODDDDDDDDDDO..MO..MO",
".O..O..O..O..O..O..O..O..O..O",
".OMMMMMMMMMMMMMMMMMMMMMMMMMMMO",
".ODDDDDDDDDDDDDDDDDDDDDDDDDDDO",
"..OO....OO....OOOO....OO....OO",
"",
])

# era-3 hope: Victorian row houses (chimneys, gold-lit sash windows, doors
# with transoms) + a prominent CLOCKTOWER above the roofline — square tower,
# gold-lit clock face with dark-gold hands, small spire and finial.
HD_SETTLE_HOPE_V3 = pad32([
"..........................G",
"..........................O",
".........................OMO",
"........................OMMMO",
".......................OMMMMMO",
"......................OOOOOOOOO",
"......................OMMMMMMMO",
"......................OMMGGGMMO",
"......................OMGGgGGMO",
"......................OMGGggGMO",
"..OO.....OO....OO.....OMGGGGGMO",
"..OM.....OM....OM.....OMMGGGMMO",
"OOOOOOOOOOOOOOOOOOOOO.OOOOOOOOO",
"OMMMMMMMMMMMMMMMMMMMO.OMMMMMMMO",
"OMMMMMMOMMMMMMOMMMMMO.OMDMMMDMO",
"OMGMGMMOMGMGMMOMGMGMO.OMMMGMMMO",
"OMGMGMMOMGMGMMOMGMGMO.OMMMGMMMO",
"OMMMMMMOMMMMMMOMMMMMO.OMDMMMDMO",
"OMMMMMMOMMMMMMOMMMMMO.OMMMMMMMO",
"OMGMGMMOMGMGMMOMGMGMO.OMMMGMMMO",
"OMGMGMMOMGMGMMOMGMGMO.OMMMMMMMO",
"OMMMMMMOMMMMMMOMMMMMO.OMDMMMDMO",
"OMMGGMMOMMGGMMOMMGMMO.OMMMMMMMO",
"OMMDDMMOMMDDMMOMMDMMO.OMMDDDMMO",
"OMMDDMMOMMDDMMOMMDMMO.OMMDGDMMO",
"OMMDDMMOMMDDMMOMMDMMO.OMMDDDMMO",
"OMMDDMMOMMDDMMOMMDMMO.OMMDDDMMO",
"ODDDDDDODDDDDDODDDDDO.ODDDDDDDO",
"OOOOOOOOOOOOOOOOOOOOO.OOOOOOOOO",
"",
])

# era-3 fear: FACTORY — dark grey-masonry industrial block (fear-band
# courses), barred void windows, wide freight door, and a tall SMOKESTACK
# rising to row 4. Rows 0-3 above the stack tip stay CLEAR of detail so the
# render layer's smoke frames read cleanly. Stack tip center: col 20, row 4
# (offsets from sprite center (16,16): +4.5px right, -12px up at 1x).
HD_SETTLE_FEAR_V3 = pad32([
"",
"",
"",
"",
"...................OOO",
"...................OxO",
"...................OxO",
"...................OzO",
"...................OzO",
"...................OzO",
"..................OzzzO",
"..................OzzzO",
".OOOOOOOOOOOOOOOOOOOOOOOOOOO",
".OzzxzzzzzzzxzzzzzzzzzxzzzzO",
".ODDDDDDDDDDDDDDDDDDDDDDDDDO",
".OzzzKOKOKzzKOKOKzzKOKOKzzzO",
".OzzzKOKOKzzKOKOKzzKOKOKzzzO",
".OzzzKOKOKzzKOKOKzzKOKOKzzzO",
".OzzzzzzzzzzzzzzzzzzzzzzzzzO",
".ODzDzzzzzzzzzzzzzzzzzzDzDzO",
".OzzzzzzzzzzzzMzzzzzzzzzzzzO",
".OzzzKOKOKzzOKKKOzzKOKOKzzzO",
".OzzzKOKOKzzOKKKOzzKOKOKzzzO",
".OzzzKOKOKzzOKKKOzzKOKOKzzzO",
".OzzzKOKOKzzOKKKOzzKOKOKzzzO",
".OzzzzzzzzzzOKKKOzzzzzzzzzzO",
".OzzzzzzzzzzOKKKOzzzzzzzzzzO",
".ODDDDDDDDDDDDDDDDDDDDDDDDDO",
".OOOOOOOOOOOOOOOOOOOOOOOOOOO",
"",
])

MASONRY = {'x': GREY_D, 'z': hx('26262b')}
hd['hd_settlement_hope_v2'] = render_map(HD_SETTLE_HOPE_V2, RAMPS['hope_dev'])
hd['hd_settlement_fear_v2'] = render_map(HD_SETTLE_FEAR_V2, RAMPS['fear_dev'])
hd['hd_settlement_hope_v3'] = render_map(HD_SETTLE_HOPE_V3, RAMPS['hope_dev'])
hd['hd_settlement_fear_v3'] = render_map(HD_SETTLE_FEAR_V3, RAMPS['fear_dev'], extra=MASONRY)

for name,img in hd.items():
    assert img.size == (32,32)
    img.save(f"{OUT}/hd/{name}.png")

# =====================================================================
# ATLAS + labeled preview
# =====================================================================
groups = [
    ('characters', chars),
    ('tiles', tiles),
    ('fx', fx),
    ('ui', ui),
    ('era', era),      # appended AFTER ui: frames 0-49 stay stable, era frames occupy 50+ (compacted_* at 71-73)
]

SCALE = 8
pad = 12
cellw = 16*SCALE + pad
rows_out = []
maxcols = 7
from PIL import ImageFont
font = None
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
except Exception:
    font = ImageFont.load_default()

sections = []
for title, group in groups + [('hd32', hd)]:   # hd previewed, packed separately below
    n = len(group)
    cols = min(maxcols, n)
    rws = math.ceil(n/cols)
    h = 30 + rws*(16*SCALE + 34)
    sec = Image.new('RGBA', (maxcols*cellw + pad, h), hx('0c0c10'))
    d = ImageDraw.Draw(sec)
    d.text((pad, 6), title.upper(), fill=hx('9a9aa2'), font=font)
    for i,(name,img) in enumerate(group.items()):
        cx = pad + (i%cols)*cellw
        cy = 30 + (i//cols)*(16*SCALE + 34)
        s = max(1, min(SCALE, (16*SCALE)//img.width, (16*SCALE)//img.height))
        big = img.resize((img.width*s, img.height*s), Image.NEAREST)
        # checker-free dark backdrop per sprite
        d.rectangle([cx-2, cy-2, cx+16*SCALE+1, cy+16*SCALE+1], outline=hx('26262e'))
        ox = cx + (16*SCALE - big.width)//2; oy = cy + (16*SCALE - big.height)//2
        sec.alpha_composite(big, (ox, oy))
        d.text((cx, cy+16*SCALE+6), name, fill=hx('6a6a72'), font=font)
    sections.append(sec)

W = maxcols*cellw + pad
H = sum(s.height for s in sections) + 20
preview = Image.new('RGBA', (W, H), hx('0c0c10'))
y = 10
for s in sections:
    preview.alpha_composite(s, (0, y)); y += s.height
preview.convert('RGB').save(f"{OUT}/preview.png")

# packed 1x atlas
import json
allsprites = {}
for _, group in groups:
    allsprites.update(group)
names = list(allsprites.keys())

# ART PASS 3 append-only guard: the first 71 names of the previous atlas.json
# must be unchanged IN ORDER (the build's F map hardcodes them); the three
# compacted_* tiles land at 71-73. ART PASS 3b extends the stable prefix to
# 74 and lands the smoke_* animation frames at 74-76.
try:
    with open(f"{OUT}/atlas.json") as f:
        prev = list(json.load(f).keys())
except FileNotFoundError:
    prev = None
if prev is not None:
    stable = min(len(prev), 74)
    assert names[:stable] == prev[:stable], "16px atlas stable-prefix order CHANGED — F map would break"
assert names[70] == 'beacon_site' and names[71:74] == ['compacted_neutral','compacted_hope','compacted_fear'], names[68:]
assert names[74:77] == ['smoke_a','smoke_b','smoke_c'], names[74:]

cols = 8
rws = math.ceil(len(names)/cols)
atlas = Image.new('RGBA', (cols*18, rws*18), T)
meta = {}
for i,name in enumerate(names):
    x = (i%cols)*18+1; ypos = (i//cols)*18+1
    img = allsprites[name]
    atlas.alpha_composite(img.crop((0,0,min(16,img.width),min(16,img.height))), (x,ypos))
    meta[name] = {'x':x,'y':ypos,'w':min(16,img.width),'h':min(16,img.height)}
atlas.save(f"{OUT}/atlas.png")
with open(f"{OUT}/atlas.json",'w') as f:
    json.dump(meta, f, indent=1)

# ART PASS 3: SECOND packed atlas for the HD 32px characters — the 18px->34px
# grid mirrors the 16px packer at doubled scale (32px frames + 1px margin +
# 2px spacing; Phaser: frameWidth/Height 32, margin 1, spacing 2).
hd_names = list(hd.keys())
# ART PASS 3b append-only guard: the first 22 names of the previous
# atlas32.json must be unchanged IN ORDER (the build's F32 map hardcodes
# them); the four hd_settlement_* frames land at 22-25.
try:
    with open(f"{OUT}/atlas32.json") as f:
        prev32 = list(json.load(f).keys())
except FileNotFoundError:
    prev32 = None
if prev32 is not None:
    stable32 = min(len(prev32), 22)
    assert hd_names[:stable32] == prev32[:stable32], "atlas32 stable-prefix order CHANGED — F32 map would break"
assert hd_names[22:26] == ['hd_settlement_hope_v2','hd_settlement_fear_v2','hd_settlement_hope_v3','hd_settlement_fear_v3'], hd_names[22:]
cols32 = 6
rws32 = math.ceil(len(hd_names)/cols32)
atlas32 = Image.new('RGBA', (cols32*34, rws32*34), T)
meta32 = {}
for i,name in enumerate(hd_names):
    x = (i%cols32)*34+1; ypos = (i//cols32)*34+1
    atlas32.alpha_composite(hd[name], (x,ypos))
    meta32[name] = {'x':x,'y':ypos,'w':32,'h':32}
atlas32.save(f"{OUT}/atlas32.png")
with open(f"{OUT}/atlas32.json",'w') as f:
    json.dump(meta32, f, indent=1)

print("sprites:", len(chars), "tiles:", len(tiles), "fx:", len(fx), "ui:", len(ui), "era:", len(era), "hd32:", len(hd))
print("atlas:", len(names), "frames (first-74 stable, smoke @74-76) | atlas32:", len(hd_names), "frames (first-22 stable, settlements @22-25)")
print("preview:", f"{OUT}/preview.png", preview.size)
