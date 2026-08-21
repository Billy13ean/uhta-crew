#!/usr/bin/env python3
"""Compose a mock in-game scene from the generated 16x16 assets (readability check)."""
from PIL import Image
import random

A = "assets"
def L(p): return Image.open(f"{A}/{p}").convert('RGBA')

TW, TH = 24, 14           # tiles
SCALE = 4
scene = Image.new('RGBA', (TW*16, TH*16), (5,5,7,255))
rng = random.Random(7)

ground = L("tiles/ground_lit.png"); memory = L("tiles/ground_memory.png")
void_t = L("tiles/ground_void.png")
road_n = L("tiles/road_neutral.png"); road_h = L("tiles/road_hope.png"); road_f = L("tiles/road_fear.png")

def put_tile(img, tx, ty):
    scene.alpha_composite(img, (tx*16, ty*16))

# terrain: lit center, memory ring, void corners
for ty in range(TH):
    for tx in range(TW):
        edge = min(tx, ty, TW-1-tx, TH-1-ty)
        if edge == 0: put_tile(void_t, tx, ty)
        elif edge == 1: put_tile(memory, tx, ty)
        else: put_tile(ground, tx, ty)

# road: hope-tinted from the hope camp, neutral mid, fear-tinted near fear camp
ry = 7
for tx in range(2, 22):
    img = road_h if tx < 9 else road_n if tx < 15 else road_f
    # horizontal road: rotate the vertical road tile
    put_tile(img.rotate(90), tx, ry)

def put(img, tx, ty, dx=0, dy=0):
    scene.alpha_composite(img, (tx*16+dx, ty*16+dy))

# hope camp (left)
put(L("tiles/settlement_hope.png"), 3, 4)
put(L("sprites/zealot_hope.png"), 4, 5, 8, 4)
put(L("sprites/wanderer_hope_dev.png"), 2, 6, 4, 2)
put(L("sprites/wanderer_hope_tent.png"), 5, 6, 2, -3)
put(L("sprites/wanderer_hope_tent.png"), 3, 8, 6, 0)
put(L("tiles/beacon_hope.png"), 6, 3)

# player avatar walking the road with white flame
put(L("sprites/avatar_hope.png"), 8, 6, 0, 2)

# fear camp (right)
put(L("tiles/settlement_fear.png"), 19, 4)
put(L("sprites/zealot_fear.png"), 18, 5, -4, 4)
put(L("sprites/wanderer_fear_dev.png"), 21, 6, -2, 0)
put(L("sprites/wanderer_fear_tent.png"), 19, 7, 2, 4)

# clash in the middle where spheres overlap
put(L("sprites/wanderer_hope_dev.png"), 11, 5, 2, 0)
put(L("sprites/wanderer_fear_dev.png"), 13, 5, -2, 0)
put(L("fx/clash.png"), 12, 4, 0, 6)
put(L("fx/scatter_puff.png"), 12, 6, 2, 2)

# burnout with frozen fear ring, below road
b = L("sprites/burnout.png"); put(b, 15, 9)
put(L("fx/ring_frozen_fear.png"), 15, 9)

# loner drifting on the road; grey wanderers; conversion sparkle
put(L("sprites/loner.png"), 16, 6, 4, 6)
put(L("sprites/wanderer_grey.png"), 9, 9)
put(L("sprites/wanderer_grey.png"), 7, 10, 6, 2)
put(L("fx/convert_sparkle_hope.png"), 9, 8, 0, 4)

# UI strip: belief meter + icons bottom-left
put(L("ui/belief_meter.png"), 1, 12, 0, 4)
for i, ic in enumerate(["icon_flame_hope","icon_roar","icon_beacon","icon_wait","icon_sleep","icon_raze"]):
    put(L(f"ui/{ic}.png"), 6+i, 12)

big = scene.resize((scene.width*SCALE, scene.height*SCALE), Image.NEAREST)
big.convert('RGB').save(f"{A}/scene_mock.png")
print("scene:", big.size)
