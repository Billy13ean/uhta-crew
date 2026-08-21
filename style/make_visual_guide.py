#!/usr/bin/env python3
"""make_visual_guide.py — the visual half of the uhta style guide.

Generates style/VISUAL-GUIDE.html: a single self-contained page showing every
character, location, flame and scene the art pipeline produces, rendered from
the REAL generators (art/make_sprites.py + scene scripts), never mocked.

Three things distinguish this from a gallery:
  1. The locked COL palette is shown as named swatches — the visual canon's
     equivalent of rule IDs.
  2. A deterministic PALETTE AUDIT runs on every asset: fraction of opaque
     pixels whose nearest locked-palette color is farther than tolerance.
     Same division of labor as style/checks.py — code measures, it does not
     judge. Off-palette pixels in composed scenes (glows, fog) are expected
     and reported, not failed.
  3. The written guide stays active: the page embeds STYLEGUIDE.md's hash and
     rule index, so one artifact carries both halves of the aesthetic canon.

Inspiration: drop reference images into style/inspiration/ (any png/jpg/webp)
and re-run; they render in their own section with filenames as captions.

Usage:  python style/make_visual_guide.py [--assets art/assets]
Stdlib + PIL only (PIL is already the art pipeline's dependency).
"""
import argparse, base64, hashlib, io, re, sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("PIL required (the art pipeline's own dependency): pip install pillow")

HERE = Path(__file__).resolve().parent
GUIDE = HERE / "STYLEGUIDE.md"
INSPO = HERE / "inspiration"

# ---- locked palette, verbatim from build COL via art/make_sprites.py ------
PALETTE = {
    "VOID": "#050507", "BG": "#0c0c10", "MEMORY": "#101016", "LIT": "#16161d",
    "ROAD": "#2f2a22", "HOPE": "#63c76b", "HOPE_DIM": "#2f5a34",
    "Z_HOPE": "#9dffb0", "FEAR": "#d45b57", "FEAR_DIM": "#5c2f2e",
    "Z_FEAR": "#ff8a86", "GREY": "#6a6a72", "PLAYER": "#f2f2f5",
    "NIGHT": "#05050a", "GOLD": "#d9c98a",
    # derived ramp stops (stay in family)
    "OUTLINE": "#0e0e12", "GREY_D": "#3a3a40", "GREY_L": "#9a9aa2",
    "HOPE_XD": "#1d3a22", "HOPE_XL": "#d6ffdd", "FEAR_XD": "#3c1f1e",
    "FEAR_XL": "#ffc7c4", "ROAD_L": "#4a4136", "ROAD_D": "#221e19",
    "WHITE_L": "#ffffff", "GOLD_D": "#8a7c4e",
}
TOL = 28  # euclidean RGB distance; audit threshold, stated policy


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


PAL_RGB = [rgb(v) for v in PALETTE.values()]


def audit(img: Image.Image, step: int = 1):
    """Return (opaque_px_sampled, off_palette_fraction)."""
    img = img.convert("RGBA")
    w, h = img.size
    if w * h > 200_000:
        step = 4
    px = img.load()
    total = off = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b, a = px[x, y]
            if a < 32:
                continue
            total += 1
            if min((r-pr)**2 + (g-pg)**2 + (b-pb)**2
                   for pr, pg, pb in PAL_RGB) > TOL * TOL:
                off += 1
    return total, (off / total if total else 0.0)


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def img_tag(path: Path, scale: int, cap: str, audit_note: str = "") -> str:
    return (f'<figure><img class="px" src="data:image/png;base64,{b64(path)}" '
            f'style="width:{Image.open(path).size[0]*scale}px">'
            f'<figcaption>{cap}{audit_note}</figcaption></figure>')


# ---- section layout: (title, blurb, [(glob-or-name, base-dir)], scale) ----
def collect(assets: Path):
    S = lambda *names: [assets / n for n in names if (assets / n).exists()]
    return [
        ("The avatar & the flames",
         "The unnamed being and the white flame that becomes what you do with "
         "it. The run's identity is written on the body: red veins in a Fear "
         "run, green vines in a Hope run (GDD v0.9.5). Era-invariant by ruling.",
         S("fx/flame_white.png", "fx/flame_hope.png", "fx/flame_fear.png",
           "sprites/avatar_hope.png", "sprites/avatar_fear.png",
           "hd/hd_avatar_body.png", "hd/hd_avatar_vines_hope.png",
           "hd/hd_avatar_veins_fear.png"), 6),
        ("Era I — nomads (the world before anyone builds)",
         "Hooded wanderers on a fogbound rockscape; belief state via ramp "
         "substitution: grey → tentative → devout, per pole.",
         S("sprites/wanderer_grey.png", "sprites/wanderer_hope_tent.png",
           "sprites/wanderer_hope_dev.png", "sprites/wanderer_fear_tent.png",
           "sprites/wanderer_fear_dev.png"), 6),
        ("Era II — villages",
         "Tribes that crossed the threshold of feeling stopped wandering and "
         "built. Coifs and tunics; thatched cottages vs. spiked palisades.",
         S("era/villager_grey.png", "era/villager_hope_tent.png",
           "era/villager_hope_dev.png", "era/villager_fear_tent.png",
           "era/villager_fear_dev.png", "era/settlement_hope_v2.png",
           "era/settlement_fear_v2.png"), 6),
        ("Era III — Victorian towns",
         "Top hats and long coats; row houses with warm windows vs. the dark "
         "mill and its smokestack. Clocktowers and smoking factories are the "
         "named furniture (GDD §2 visual canon).",
         S("era/townsfolk_grey.png", "era/townsfolk_hope_tent.png",
           "era/townsfolk_hope_dev.png", "era/townsfolk_fear_tent.png",
           "era/townsfolk_fear_dev.png", "era/settlement_hope_v3.png",
           "era/settlement_fear_v3.png", "era/smoke_a.png"), 6),
        ("The era-invariant (mythic constants)",
         "Zealots, loners and the burned never age with the eras — timeless "
         "by Director ruling (v0.9.4). The burned wear a faint ring of the "
         "color they used to be.",
         S("sprites/zealot_hope.png", "sprites/zealot_fear.png",
           "sprites/loner.png", "sprites/burnout.png",
           "fx/ring_frozen_hope.png", "fx/ring_frozen_fear.png"), 6),
        ("Roads — the ground remembering you",
         "Per-tile aging, decoupled from era art: compacted earth → cobble → "
         "paver stone; allegiance colors them green / red / grey.",
         S("era/compacted_neutral.png", "era/compacted_hope.png",
           "era/compacted_fear.png", "era/road_neutral_v2.png",
           "era/road_hope_v2.png", "era/road_fear_v2.png",
           "era/road_neutral_v3.png", "era/road_hope_v3.png",
           "era/road_fear_v3.png"), 5),
        ("Beacons & basins",
         "Placed beacons in each color, and the unlit ruined basin from the "
         "opening myth — five discoverable on the map.",
         S("tiles/beacon_hope.png", "tiles/beacon_fear.png",
           "era/beacon_site.png"), 6),
        ("Verb & event language",
         "The roar, the clash of rival spheres, conversion sparkles — every "
         "mechanic's render cue, because this game has no other channel.",
         S("fx/roar.png", "fx/clash.png", "fx/convert_sparkle_hope.png",
           "fx/convert_sparkle_fear.png", "fx/scatter_puff.png"), 6),
        ("Settings — composed scenes",
         "Full scenes from the scene generators: the world mock, the cave "
         "opening's temple, and the title. These are the closest thing to "
         "screenshots the pipeline produces deterministically; in-game "
         "captures can be dropped into style/inspiration/ alongside them.",
         S("scene_mock.png", "temple_scene.png", "title_scene.png"), 1),
    ]


def build(assets: Path, out: Path, include_inspo: bool = True):
    guide_txt = GUIDE.read_text(encoding="utf-8")
    guide_sha = hashlib.sha256(GUIDE.read_bytes()).hexdigest()[:16]
    rule_ids = re.findall(r"\*\*([TVF]\d)\b", guide_txt)

    css_pal = "".join(
        f'<div class="sw"><span style="background:{v}"></span>{k}<code>{v}</code></div>'
        for k, v in PALETTE.items())

    sections, audit_rows = [], []
    for title, blurb, paths, scale in collect(assets):
        figs = []
        for p in paths:
            total, frac = audit(Image.open(p))
            audit_rows.append((str(p.relative_to(assets)), total, frac))
            note = "" if frac < 0.02 else f' <b class="off">{frac:.0%} off-palette</b>'
            figs.append(img_tag(p, scale, p.stem, note))
        sections.append(f"<section><h2>{title}</h2><p>{blurb}</p>"
                        f'<div class="row">{"".join(figs)}</div></section>')

    # Reference images are LOCAL ONLY (gitignored): they are other people's
    # work, kept as a private mood board, never redistributed in the repo.
    # CREDITS.txt maps a filename prefix to a credit line, e.g.
    #   o-empire: O EMPIRE! WARD OFF THY ROT (c) AwkwardSilenceGames | https://store.steampowered.com/app/4331110/
    credits = []
    cfile = INSPO / "CREDITS.txt"
    if cfile.exists():
        for line in cfile.read_text(encoding="utf-8").splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                k, v = line.split(":", 1)
                credits.append((k.strip().lower(), v.strip()))
    def credit_for(name):
        for k, v in credits:
            if name.lower().startswith(k):
                text, _, url = v.partition("|")
                text = text.strip(); url = url.strip()
                return (f'{name} — <a href="{url}">{text}</a>' if url
                        else f"{name} — {text}")
        return name
    inspo_figs = []
    if include_inspo and INSPO.exists():
        for p in sorted(INSPO.iterdir()):
            if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                mime = "jpeg" if p.suffix.lower() in (".jpg", ".jpeg") else p.suffix[1:]
                inspo_figs.append(
                    f'<figure><img src="data:image/{mime};base64,{b64(p)}" '
                    f'style="max-width:340px"><figcaption>{credit_for(p.name)}</figcaption></figure>')
    inspo_note = ("<p class='dim'>Reference frames are a private mood board — "
                  "local files, gitignored, credited below, never part of the "
                  "committed repo. Principles taken from them live in "
                  "<code>art/ART-DIRECTION-STUDY-o-empire.md</code>.</p>")
    inspo_html = (inspo_note + "".join(inspo_figs) if inspo_figs else
                  "<p class='dim'>No local reference images. Drop png/jpg/webp into "
                  "<code>style/inspiration/</code> (gitignored; credit them in "
                  "<code>CREDITS.txt</code>) and re-run "
                  "<code>python style/make_visual_guide.py</code>. Principles drawn "
                  "from reference work live in "
                  "<code>art/ART-DIRECTION-STUDY-o-empire.md</code>.</p>")

    worst = sorted(audit_rows, key=lambda r: -r[2])[:8]
    audit_html = "".join(
        f"<tr><td>{n}</td><td>{t}</td><td>{f:.1%}</td></tr>" for n, t, f in worst)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>uhta — visual style guide</title><style>
body{{background:#0c0c10;color:#d9d9de;font:15px/1.55 Georgia,serif;
     max-width:1100px;margin:0 auto;padding:2rem 1.5rem 5rem}}
h1{{font-weight:normal;letter-spacing:.06em}} h2{{color:#d9c98a;font-weight:normal;
     border-bottom:1px solid #2f2a22;padding-bottom:.3rem;margin-top:2.6rem}}
.dim{{color:#6a6a72}} .off{{color:#d45b57;font-weight:normal}}
.row{{display:flex;flex-wrap:wrap;gap:1.1rem;align-items:flex-end}}
figure{{margin:0;text-align:center}} figcaption{{font-size:.72rem;color:#9a9aa2;
     margin-top:.35rem;font-family:monospace}}
img.px{{image-rendering:pixelated;background:#101016;border:1px solid #16161d;
     padding:6px;border-radius:4px}}
.pal{{display:flex;flex-wrap:wrap;gap:.5rem .9rem}}
.sw{{font-family:monospace;font-size:.75rem;display:flex;align-items:center;gap:.4rem}}
.sw span{{width:22px;height:22px;border-radius:4px;display:inline-block;
     border:1px solid #2f2a22}} .sw code{{color:#6a6a72}}
table{{border-collapse:collapse;font-family:monospace;font-size:.78rem}}
td,th{{border:1px solid #2f2a22;padding:.25rem .6rem;text-align:left}}
header p{{color:#9a9aa2}}
.status{{font-family:monospace;font-size:.78rem;color:#63c76b}}
</style></head><body>
<header><h1>uhta — visual style guide</h1>
<p>The visual half of the aesthetic canon. Every image below is rendered by the
real art pipeline (<code>art/make_sprites.py</code> + scene generators) from the
locked palette — never mocked, never hand-placed.</p>
<p class="status">written guide ACTIVE — STYLEGUIDE.md sha {guide_sha} ·
rules enforced by the text loop: {", ".join(dict.fromkeys(rule_ids))}</p></header>

<section><h2>The locked palette (build COL table)</h2>
<p>Landscape tint communicates feeling; era art communicates time (GDD §2,
locked). Every sprite is authored from these ramps.</p>
<div class="pal">{css_pal}</div></section>

{"".join(sections)}

<section><h2>Palette audit (deterministic)</h2>
<p>Code, not judgment: fraction of opaque pixels farther than tolerance
{TOL} from the nearest locked color. Sprites authored from ramps should sit
near zero; composed scenes carry glow and fog and are <em>expected</em> to
drift — reported so drift is visible, not to fail it. Worst eight:</p>
<table><tr><th>asset</th><th>px sampled</th><th>off-palette</th></tr>
{audit_html}</table></section>

<section><h2>Inspiration</h2>{inspo_html}</section>

<footer><p class="dim">Generated by style/make_visual_guide.py · palette
verbatim from build COL · audit tolerance is stated policy, not a GDD
constant.</p></footer></body></html>"""
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size//1024} KB), "
          f"{len(audit_rows)} assets audited")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default=str(HERE.parent / "art" / "assets"))
    ap.add_argument("--no-inspiration", action="store_true",
                    help="render without local reference images (use for the committed page)")
    ap.add_argument("--out", default=str(HERE / "VISUAL-GUIDE.html"))
    args = ap.parse_args()
    assets = Path(args.assets)
    if not assets.exists():
        sys.exit(f"assets dir not found: {assets} — run art/make_sprites.py "
                 "and the scene scripts first")
    INSPO.mkdir(exist_ok=True)
    build(assets, Path(args.out), include_inspo=not args.no_inspiration)
