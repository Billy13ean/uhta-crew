"""The Director's dashboard — the human gate, rendered as a checklist.

Every propose run now emits `MINIGAME-DASHBOARD.html`: a self-contained page
(inline CSS/JS, no network, no storage) where each surviving candidate is a
card carrying everything the Director needs to rule — the RULES (premise,
loop, controls, stakes, outcomes) and the VISUALS (the diegetic signal
language, ready to hand to the render layer) — plus the Judge's cited
verdict. The Director checks off approvals and the page generates the
ruling: a signed selection block and the exact `run_minigame.py --build
--select <id>` command per approved item, downloadable as
DIRECTOR-SELECTION.md.

The gate stays structural: the dashboard produces the COMMAND — a human
still has to run it. Escalated candidates render locked, exactly as the
build phase would refuse them.

Also usable standalone against a completed run directory:

    python3 -m minigame.dashboard out/mg-live \
        --built first-contact-hope=out/mg-directors-cut
"""
from __future__ import annotations

import html as _html
import json
import re
import sys
from pathlib import Path

DASHBOARD_NAME = "MINIGAME-DASHBOARD.html"


def _e(s) -> str:
    return _html.escape(str(s if s is not None else ""))


def _card(c: dict) -> str:
    esc = c.get("status") != "ACCEPTED"
    pole = c.get("pole", "")
    pole_cls = "hope" if pole == "hope" else "fear"
    built = c.get("built")
    ctrl = ", ".join(c.get("controls") or [])
    eff = ", ".join(sorted(set(c.get("effects") or [])))
    judge = c.get("judge_reason", "")
    chunk = c.get("judge_chunk", "")
    return f"""
<div class="card {'escalated' if esc else ''}" data-id="{_e(c['id'])}">
  <div class="cardhead">
    <label class="approve">
      <input type="checkbox" class="pick" value="{_e(c['id'])}"
             {'disabled' if esc else ''} onchange="tally()">
      <span></span>
    </label>
    <div>
      <h2>{_e(c.get('name', c['id']))}</h2>
      <div class="badges">
        <span class="badge slot">{_e(c.get('encounter', ''))}</span>
        <span class="badge {pole_cls}">{_e(pole)}</span>
        {'<span class="badge locked">ESCALATED — cannot be selected</span>' if esc
         else '<span class="badge pass">judge: PASS</span>'}
        {f'<span class="badge built">BUILT — {_e(built)}</span>' if built else ''}
      </div>
    </div>
  </div>
  <p class="premise">{_e(c.get('premise', ''))}</p>
  <div class="cols">
    <div class="col">
      <h3>The rules</h3>
      <p>{_e(c.get('loop', ''))}</p>
      <p class="kv"><b>Controls</b> {_e(ctrl)}</p>
      <p class="kv"><b>Stakes</b> {_e(eff)}</p>
      <p class="kv"><b>Win</b> {_e(c.get('outcome_win', ''))}</p>
      <p class="kv"><b>Fail</b> {_e(c.get('outcome_fail', ''))}</p>
    </div>
    <div class="col">
      <h3>The visuals <span class="sub">(drop-in for the render layer)</span></h3>
      <p>{_e(c.get('signals', ''))}</p>
      <p class="kv"><b>Why fun</b> {_e(c.get('why_fun', ''))}</p>
      <p class="kv"><b>Pattern</b> {_e(c.get('pattern_source', ''))}</p>
    </div>
  </div>
  <div class="ground">
    <p><b>GDD grounding</b> “{_e(c.get('gdd_quote', ''))}”</p>
    {f'<p><b>Judge</b> {_e(judge)}</p>' if judge else ''}
    {f'<p class="chunk">chunk honored: “{_e(chunk)}”</p>' if chunk else ''}
  </div>
  {_dossier_html(c['dossier']) if c.get('dossier') else ''}
</div>"""


def dossier_from_build(build_dir: Path) -> dict | None:
    """Read a BUILD run directory into a dossier: what every seat past the
    human gate actually did. Deterministic, best-effort — each artifact is
    optional so a partial or Director's-cut directory still yields a
    dossier. Paths in the result are relative to a sibling run directory
    (the propose run's dashboard lives in out/<propose>/, the build in
    out/<build>/ — hence "../<build>/...")."""
    build_dir = Path(build_dir)
    if not build_dir.is_dir():
        return None

    def _load(name: str):
        f = build_dir / name
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return None
        return None

    rel = f"../{build_dir.name}"
    instructions = _load("instructions.json") or {}
    presentation = _load("presentation.json") or {}
    manifest = _load("manifest.json") or {}
    build = manifest.get("build") or {}
    probe_raw = _load("play-probe.json")
    patch = _load("patch.json") or {}

    probe = None
    if probe_raw is not None:
        if probe_raw.get("skipped"):
            probe = {"skipped": str(probe_raw["skipped"])}
        elif isinstance(probe_raw.get("checks"), dict):
            ch = probe_raw["checks"]
            probe = {"passed": sum(1 for v in ch.values() if v),
                     "total": len(ch),
                     "failed": sorted(k for k, v in ch.items() if not v)}

    d = {
        "build_run": build_dir.name,
        "first_use_line": (instructions.get("first_use_line")
                           or build.get("first_use_line")
                           or patch.get("first_use_line")),
        "instructor_repairs": instructions.get(
            "repair_rounds", build.get("instructor_repairs")),
        "presentation": presentation or None,
        "checks": build.get("checks"),
        "repair_rounds": build.get("repair_rounds"),
        "probe": probe,
        "patched_rel": (f"{rel}/uhta-slice.minigame.patched.html"
                        if (build_dir /
                            "uhta-slice.minigame.patched.html").exists()
                        else None),
        "repair_ledger_rel": (f"{rel}/DIRECTORS-REPAIR.md"
                              if (build_dir / "DIRECTORS-REPAIR.md").exists()
                              else None),
        "shots": [f"{rel}/{f.name}"
                  for f in sorted(build_dir.glob("*.png"))],
        "canon": manifest.get("canon"),
    }
    if not any((d["first_use_line"], d["presentation"], d["checks"],
                d["probe"], d["patched_rel"])):
        return None
    return d


def dossier_merge(dossiers: list[dict | None]) -> dict | None:
    """Merge dossiers from several build directories into one card's
    dossier (e.g. the LLM build run that holds the Instructor/Presenter
    artifacts + the Director's-cut directory that holds the ratified
    playable, the probe, the ledger, and the screenshots). First
    non-empty value wins per field; screenshots concatenate in order."""
    ds = [d for d in dossiers if d]
    if not ds:
        return None
    out = dict(ds[0])
    for d in ds[1:]:
        for k, v in d.items():
            if k == "shots":
                out["shots"] = (out.get("shots") or []) + v
            elif not out.get(k):
                out[k] = v
    out["build_run"] = " + ".join(dict.fromkeys(d["build_run"] for d in ds))
    return out


def _dossier_html(d: dict) -> str:
    parts = ['<div class="dossier">',
             '<h3>The build — the seats past the gate '
             f'<span class="sub">(run <code>{_e(d["build_run"])}</code>)'
             '</span></h3>']

    if d.get("first_use_line"):
        rep = d.get("instructor_repairs")
        rep_s = (f" · {rep} repair round(s)" if rep is not None else "")
        parts.append(
            f'<p class="seat"><b>Writer (Instructor)</b> — first-use line'
            f'{rep_s}:<br><span class="line">&ldquo;'
            f'{_e(d["first_use_line"])}&rdquo;</span></p>')

    pres = d.get("presentation")
    if pres:
        sig = pres.get("signal_map") or {}
        hier = pres.get("visual_hierarchy") or []
        rows = "".join(
            f"<p class='kv'><b>{_e(k.replace('_', ' '))}</b> {_e(v)}</p>"
            for k, v in sig.items())
        hier_html = "".join(f"<p class='kv'>{i + 1}. {_e(h)}</p>"
                            for i, h in enumerate(hier))
        blocks = ""
        for key, label in (("attention_cue", "Attention cue"),
                           ("entry_transition", "Entry"),
                           ("feedback_win", "Win"),
                           ("feedback_fail", "Fail"),
                           ("exit_transition", "Exit")):
            if pres.get(key):
                blocks += (f"<p class='kv'><b>{label}</b> "
                           f"{_e(pres[key])}</p>")
        parts.append(
            f'<details class="seat"><summary><b>Aesthetic Director '
            f'(Presenter)</b> — presentation spec: {len(sig)} signal(s), '
            f'entry/win/fail/exit defined</summary>'
            f'{blocks}'
            + (f"<p class='kv'><b>Visual hierarchy</b></p>{hier_html}"
               if hier_html else "")
            + (f"<p class='kv'><b>Signal map</b></p>{rows}" if rows else "")
            + '</details>')

    checks = d.get("checks")
    if checks:
        n_ok = sum(1 for v in checks.values() if v)
        bad = sorted(k for k, v in checks.items() if not v)
        rr = d.get("repair_rounds")
        parts.append(
            f'<p class="seat"><b>Programmer</b> — patch post-checks '
            f'{n_ok}/{len(checks)} passed'
            + (f", failed: {_e(', '.join(bad))}" if bad else "")
            + (f" · {rr} repair round(s)" if rr is not None else "")
            + '</p>')

    probe = d.get("probe")
    if probe:
        if probe.get("skipped"):
            parts.append(f'<p class="seat"><b>Play-probe</b> — SKIPPED: '
                         f'{_e(probe["skipped"])}</p>')
        else:
            bad = probe.get("failed") or []
            parts.append(
                f'<p class="seat"><b>Play-probe</b> (headless playthrough) '
                f'— {probe["passed"]}/{probe["total"]} checks'
                + (f", failed: {_e(', '.join(bad))}" if bad else " passed")
                + '</p>')

    links = []
    if d.get("patched_rel"):
        links.append(f'<a class="play" href="{_e(d["patched_rel"])}#mg" '
                     f'target="_blank">&#9654; play the patched build</a>')
    if d.get("repair_ledger_rel"):
        links.append(f'<a href="{_e(d["repair_ledger_rel"])}" '
                     f'target="_blank">Director\'s repair ledger</a>')
    if links:
        parts.append('<p class="seat links">' + " · ".join(links) + '</p>')
    if d.get("shots"):
        imgs = "".join(
            f'<a href="{_e(u)}" target="_blank"><img src="{_e(u)}" '
            f'alt="{_e(Path(u).name)}" loading="lazy"></a>'
            for u in d["shots"])
        parts.append(f'<div class="shots">{imgs}</div>')
    parts.append('</div>')
    return "".join(parts)


def _canon_line(canon: dict | None) -> str:
    """The law these candidates were judged under — the same summary the
    manifest carries, stamped on the human gate so a verdict can never be
    separated from its canon. Links to the Bible (../../canon/ works when
    the page is opened from a run directory on disk; the console serves the
    live Bible at /bible)."""
    link = ("<a href='../../canon/CANON-BIBLE.html'>open the canon bible</a> "
            "(or <code>/bible</code> in the crew console)")
    if canon is None:
        return (f"<p class='canonline'>Judged under baseline canon — this "
                f"run predates the canon bench (no canon block in its "
                f"manifest). {link}.</p>")
    if not canon.get("rules"):
        return (f"<p class='canonline'>Judged under baseline canon — "
                f"registry absent, the spec constants in force. {link}.</p>")
    if canon.get("ruling_file"):
        non = canon.get("non_upheld") or {}
        det = ("; ".join(f"<code>{_e(k)}</code> {_e(v)}"
                         for k, v in non.items())
               or "every rule UPHELD")
        return (f"<p class='canonline'>Judged under RULED canon — "
                f"{_e(canon['ruling_file'])} "
                f"(sha256:{_e(canon.get('ruling_sha256_16') or '')}, ruled by "
                f"{_e(canon.get('ruled_by') or '(unsigned)')}): {det}. "
                f"{link}.</p>")
    return (f"<p class='canonline'>Judged under baseline canon — every rule "
            f"UPHELD as written, no ruling on file. {link}.</p>")


def render_dashboard(run_id: str, cards: list[dict],
                     canon: dict | None = None) -> str:
    n_ok = sum(1 for c in cards if c.get("status") == "ACCEPTED")
    cards_html = "\n".join(_card(c) for c in cards)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>uhta — mini-game candidates · Director's dashboard · {_e(run_id)}</title>
<style>
  :root {{ --bg:#0b0b0e; --card:#15151b; --ink:#d8d4c8; --dim:#8a8578;
           --gold:#e8b64c; --ember:#c8503c; --green:#5cb46a; --line:#2a2a33; }}
  * {{ box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--ink); margin:0;
         font:15px/1.55 Georgia, 'Times New Roman', serif; padding-bottom:120px; }}
  header {{ padding:28px 32px 18px; border-bottom:1px solid var(--line); }}
  header h1 {{ margin:0; font-size:22px; font-weight:normal; letter-spacing:.06em; }}
  header h1 b {{ color:var(--gold); font-weight:normal; }}
  header p {{ color:var(--dim); margin:6px 0 0; font-size:13px; }}
  header p.canonline {{ font-size:12px; }}
  header p.canonline a {{ color:var(--gold); }}
  header p.canonline code {{ color:var(--gold); font-size:11px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(430px,1fr));
          gap:18px; padding:24px 32px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
          padding:18px 20px; }}
  .card.escalated {{ opacity:.55; }}
  .cardhead {{ display:flex; gap:14px; align-items:flex-start; }}
  .card h2 {{ margin:0 0 6px; font-size:18px; color:var(--gold); font-weight:normal; }}
  .badges {{ display:flex; gap:6px; flex-wrap:wrap; }}
  .badge {{ font:11px/1 monospace; padding:4px 8px; border-radius:20px;
           border:1px solid var(--line); color:var(--dim); }}
  .badge.hope {{ color:var(--green); border-color:var(--green); }}
  .badge.fear {{ color:var(--ember); border-color:var(--ember); }}
  .badge.pass {{ color:var(--gold); border-color:var(--gold); }}
  .badge.built {{ color:#0b0b0e; background:var(--gold); border-color:var(--gold); }}
  .badge.locked {{ color:var(--ember); border-color:var(--ember); }}
  .approve input {{ display:none; }}
  .approve span {{ display:inline-block; width:26px; height:26px; margin-top:2px;
                  border:2px solid var(--dim); border-radius:6px; cursor:pointer; }}
  .approve input:checked + span {{ background:var(--gold); border-color:var(--gold);
      box-shadow:0 0 12px rgba(232,182,76,.5); }}
  .approve input:disabled + span {{ opacity:.3; cursor:not-allowed; }}
  .premise {{ font-style:italic; color:var(--dim); margin:12px 0; }}
  .dossier {{ border-top:1px dashed var(--line); margin-top:14px; padding-top:10px; }}
  .dossier h3 {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase;
            color:var(--gold); margin:0 0 8px; font-weight:normal; }}
  .dossier .sub {{ color:var(--dim); text-transform:none; letter-spacing:0; }}
  .seat {{ font-size:13px; margin:8px 0; }}
  .seat .line {{ font-style:italic; color:var(--gold); }}
  .seat.links a, .dossier a {{ color:var(--gold); }}
  details.seat summary {{ cursor:pointer; }}
  details.seat {{ background:#0f0f14; border:1px solid var(--line);
            border-radius:8px; padding:8px 12px; }}
  .shots {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }}
  .shots img {{ height:84px; border:1px solid var(--line); border-radius:6px; }}
  .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .col h3 {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase;
            color:var(--gold); margin:0 0 6px; font-weight:normal; }}
  .col h3 .sub {{ color:var(--dim); text-transform:none; letter-spacing:0; }}
  .col p {{ margin:0 0 8px; font-size:13.5px; }}
  .kv b {{ color:var(--dim); font-weight:normal; font-variant:small-caps;
          margin-right:6px; }}
  .ground {{ border-top:1px dashed var(--line); margin-top:12px; padding-top:10px;
            font-size:12.5px; color:var(--dim); }}
  .ground b {{ color:var(--ink); font-weight:normal; font-variant:small-caps; }}
  .ground .chunk {{ font-style:italic; }}
  footer {{ position:fixed; bottom:0; left:0; right:0; background:#101017;
           border-top:1px solid var(--line); padding:14px 32px;
           display:flex; gap:18px; align-items:center; }}
  footer .count {{ color:var(--gold); font-size:15px; min-width:180px; }}
  footer button {{ background:var(--gold); color:#0b0b0e; border:none;
      font:14px Georgia, serif; padding:10px 22px; border-radius:8px; cursor:pointer; }}
  footer button:disabled {{ opacity:.35; cursor:not-allowed; }}
  footer a {{ color:var(--gold); font-size:13px; display:none; }}
  #ruling {{ display:none; white-space:pre-wrap; background:#101017;
      border:1px solid var(--gold); border-radius:10px; margin:0 32px 24px;
      padding:16px 20px; font:12.5px/1.6 monospace; color:var(--ink); }}
</style></head><body>
<header>
  <h1><b>uhta</b> · encounter mini-game candidates — the Director's dashboard</h1>
  <p>Run <code>{_e(run_id)}</code> · {n_ok} selectable candidate(s) ·
     check what you approve, then generate the ruling. The gate stays
     structural: the ruling contains the build command — a human still runs it.</p>
  {_canon_line(canon)}
</header>
<div class="grid">{cards_html}</div>
<pre id="ruling"></pre>
<footer>
  <span class="count" id="count">0 approved</span>
  <button id="go" disabled onclick="rule()">Generate Director's ruling</button>
  <button id="copy" style="display:none" onclick="copyRuling()">Copy</button>
  <a id="dl" download="DIRECTOR-SELECTION.md">Download DIRECTOR-SELECTION.md</a>
</footer>
<script>
const RUN = {json.dumps(run_id)};
function picks() {{
  return [...document.querySelectorAll('.pick:checked')].map(x => x.value);
}}
function tally() {{
  const n = picks().length;
  document.getElementById('count').textContent = n + ' approved';
  document.getElementById('go').disabled = n === 0;
}}
function rule() {{
  const ids = picks();
  const lines = [];
  lines.push('# DIRECTOR SELECTION — encounter mini-games');
  lines.push('');
  lines.push('Run: ' + RUN);
  lines.push('Approved: ' + ids.join(', '));
  lines.push('Rejected/held: ' + [...document.querySelectorAll('.pick:not(:checked):not(:disabled)')].map(x=>x.value).join(', '));
  lines.push('');
  lines.push('## Build commands (one per approved design)');
  lines.push('');
  for (const id of ids)
    lines.push('python3 run_minigame.py --build --select ' + id + ' --from-run ' + RUN + ' --run-id build-' + id);
  lines.push('');
  lines.push('Signed (Director): Nicholas Rouke');
  const text = lines.join('\\n');
  const pre = document.getElementById('ruling');
  pre.textContent = text; pre.style.display = 'block';
  const dl = document.getElementById('dl');
  dl.href = 'data:text/markdown;charset=utf-8,' + encodeURIComponent(text);
  dl.style.display = 'inline';
  document.getElementById('copy').style.display = 'inline';
  pre.scrollIntoView({{behavior:'smooth'}});
}}
function copyRuling() {{
  const t = document.getElementById('ruling').textContent;
  if (navigator.clipboard) navigator.clipboard.writeText(t);
}}
</script>
</body></html>"""


# ---------------------------------------------------------------------------
# standalone: rebuild the dashboard from a completed propose run directory
# ---------------------------------------------------------------------------

def cards_from_run(run_dir: Path, built: dict[str, str] | None = None) -> tuple[str, list[dict]]:
    data = json.loads((run_dir / "CANDIDATES.json").read_text(encoding="utf-8"))
    md = (run_dir / "MINIGAME-CANDIDATES.md").read_text(encoding="utf-8") \
        if (run_dir / "MINIGAME-CANDIDATES.md").exists() else ""
    cards: list[dict] = []
    for d in data.get("accepted", []):
        c = dict(d)
        c["status"] = "ACCEPTED"
        m = re.search(
            r"## `" + re.escape(d["id"]) + r"`.*?\*\*Judge:\*\* PASS — (.*?)\n"
            r"(?:\s*- chunk honored: \"(.*?)\")?", md, re.DOTALL)
        if m:
            c["judge_reason"] = m.group(1).strip()
            c["judge_chunk"] = (m.group(2) or "").strip()
        if built and d["id"] in built:
            c["built"] = built[d["id"]]
        cards.append(c)
    for slot in data.get("escalated", []):
        cards.append({"id": slot, "name": slot, "status": "ESCALATED",
                      "premise": "Escalated by the circuit breaker — see "
                                 "MG-ESCALATED.md for every round of evidence."})
    return data.get("run_id", run_dir.name), cards


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python3 -m minigame.dashboard <run_dir> "
              "[--built id=note ...] [--dossier id=build_dir ...]")
        return 1
    run_dir = Path(argv[0])
    built: dict[str, str] = {}
    for a in argv[1:]:
        if a.startswith("--built") and "=" in a:
            k, v = a.split("=", 1)
            built[k.replace("--built", "").strip() or v.split("=")[0]] = v
    # simpler: accept id=note pairs after --built flags
    built = {}
    i = 1
    while i < len(argv):
        if argv[i] == "--built" and i + 1 < len(argv) and "=" in argv[i + 1]:
            k, v = argv[i + 1].split("=", 1)
            built[k] = v
            i += 2
        else:
            i += 1
    dossiers: dict[str, str] = {}
    i = 1
    while i < len(argv):
        if argv[i] == "--dossier" and i + 1 < len(argv) and "=" in argv[i + 1]:
            k, v = argv[i + 1].split("=", 1)
            dossiers[k] = v
            i += 2
        else:
            i += 1
    run_id, cards = cards_from_run(run_dir, built)
    for c in cards:
        if c["id"] in dossiers:
            d = dossier_merge([dossier_from_build(Path(x.strip()))
                               for x in dossiers[c["id"]].split(",")])
            if d:
                c["dossier"] = d
                c.setdefault("built", built.get(c["id"]) or d["build_run"])
    canon = None
    mf = run_dir / "manifest.json"
    if mf.exists():
        try:
            canon = json.loads(mf.read_text(encoding="utf-8")).get("canon")
        except json.JSONDecodeError:
            pass
    out = run_dir / DASHBOARD_NAME
    out.write_text(render_dashboard(run_id, cards, canon), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} B, {len(cards)} cards)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
