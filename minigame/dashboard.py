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
</div>"""


def render_dashboard(run_id: str, cards: list[dict]) -> str:
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
              "[--built id=note ...]")
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
    run_id, cards = cards_from_run(run_dir, built)
    out = run_dir / DASHBOARD_NAME
    out.write_text(render_dashboard(run_id, cards), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} B, {len(cards)} cards)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
