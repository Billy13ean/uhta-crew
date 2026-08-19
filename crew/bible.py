"""The Canon Bible — every rule the Evaluators enforce, on one page,
rulable.

    python3 -m crew.bible          # writes canon/CANON-BIBLE.html and opens it
    (or served live by run_console.py at /bible)

The page renders the registry (canon/rules.json) as cards the Director can
rule on: UPHOLD (default), AMEND (edit the text or the parameters), or
REPEAL (where the rule is repealable). "Generate ruling" produces
CANON-RULING.json + a human-readable CANON-RULING.md — downloadable from
the page, or saved straight into canon/ when the page is served by the
crew console. The pipelines read the ruling through crew/canon.py at the
start of every run and record what law was in force in CANON-IN-FORCE.md.

The page cannot change the pipelines directly — same principle as the
mini-game dashboard: the Bible writes the RULING, and the ruling is a
committed artifact the next run obeys. There is no ignore button, by the
Director's own ruling (2026-08-19).
"""
from __future__ import annotations

import html as _html
import json
import sys
import webbrowser
from pathlib import Path

from .canon import Canon

REPO_ROOT = Path(__file__).resolve().parent.parent

_CSS = """
:root{--bg:#0b0b0e;--card:#15151b;--ink:#d8d4c8;--dim:#8a8578;--gold:#e8b64c;
--ember:#c8503c;--green:#5cb46a;--blue:#5c8ab4;--line:#2a2a33}
*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);margin:0;
font:15px/1.55 Georgia,serif}
header{padding:26px 34px 16px;border-bottom:1px solid var(--line)}
header h1{margin:0;font-size:21px;font-weight:normal}
header h1 b{color:var(--gold);font-weight:normal}
header p{color:var(--dim);font-size:13px;max-width:920px}
.wrap{padding:20px 34px;max-width:1080px}
h2{color:var(--gold);font-weight:normal;font-size:15px;letter-spacing:.09em;
text-transform:uppercase;margin:28px 0 10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:16px 20px;margin-bottom:14px}
.card.repealed-now{opacity:.75;border-color:#4a2a22}
.rhead{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
.rhead b{color:var(--gold);font-weight:normal;font-size:15.5px}
.rid{font:11.5px monospace;color:var(--dim)}
.badge{font:10.5px monospace;letter-spacing:.06em;padding:2px 8px;
border-radius:9px;border:1px solid var(--line);color:var(--dim)}
.badge.UPHELD{color:var(--green);border-color:var(--green)}
.badge.AMENDED{color:var(--gold);border-color:var(--gold)}
.badge.REPEALED{color:var(--ember);border-color:var(--ember)}
.src{color:var(--dim);font-size:12px;margin:4px 0 8px}
.law{background:#0f0f14;border:1px solid var(--line);border-radius:8px;
padding:10px 13px;font-size:13.5px;margin:8px 0;color:var(--ink)}
.law.amended-law{border-color:var(--gold)}
.params{font:12px monospace;color:var(--dim)}
.controls{display:flex;gap:16px;margin-top:10px;flex-wrap:wrap;align-items:center}
.controls label{font-size:13px;cursor:pointer}
.controls input[type=radio]{accent-color:var(--gold)}
.norepeal{color:var(--dim);font-size:12px;font-style:italic}
textarea,input[type=text],input[type=number]{background:#0f0f14;color:var(--ink);
border:1px solid var(--line);border-radius:7px;font:12.5px monospace;
padding:8px 10px;width:100%}
textarea{min-height:84px}
.editor{display:none;margin-top:10px}.editor.show{display:block}
.editor .plabel{font-size:12px;color:var(--dim);margin:8px 0 3px}
.opt{display:block;margin:6px 0;font-size:13.5px;cursor:pointer}
button{background:var(--gold);color:#0b0b0e;border:none;font:14px Georgia,serif;
padding:10px 20px;border-radius:8px;cursor:pointer}
button.ghost{background:transparent;color:var(--gold);border:1px solid var(--gold)}
.bench{background:var(--card);border:1px solid var(--gold);border-radius:10px;
padding:18px 22px;margin:26px 0}
.bench .row{display:flex;gap:10px;margin:8px 0;flex-wrap:wrap}
.bench input[type=text]{flex:1;min-width:200px}
#out{display:none;margin-top:14px}#out.show{display:block}
#out a{color:var(--gold)}
.note{color:var(--dim);font-size:12.5px}
pre{background:#0f0f14;border:1px solid var(--line);border-radius:8px;
padding:10px 13px;font:11.5px/1.5 monospace;overflow-x:auto;white-space:pre-wrap;
color:var(--dim)}
.hist{font-size:12px;color:var(--dim);margin-top:8px}
"""

_JS = r"""
const REG = window.__REGISTRY__, RULING = window.__RULING__ || {};
const state = {rules:{}, proposals:{}};

function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}

function setStatus(rid, st){
  state.rules[rid] = state.rules[rid] || {}; state.rules[rid].status = st;
  const ed = document.querySelector('#ed-'+rid);
  if (ed) ed.classList.toggle('show', st==='AMENDED');
  const badge = document.querySelector('#badge-'+rid);
  badge.textContent = st; badge.className = 'badge '+st;
}

function collect(){
  const ruling = {ruled_by: document.querySelector('#ruled-by').value.trim(),
                  ruled_at: new Date().toISOString().slice(0,19),
                  note: document.querySelector('#ruling-note').value.trim(),
                  rules:{}, proposals:{}};
  for (const r of REG.rules){
    const st = (state.rules[r.id]||{}).status || 'UPHELD';
    if (st === 'UPHELD') continue;
    const entry = {status: st};
    const reason = document.querySelector('#reason-'+r.id);
    if (reason && reason.value.trim()) entry.reason = reason.value.trim();
    if (st === 'AMENDED'){
      const ta = document.querySelector('#text-'+r.id);
      if (ta && ta.value.trim() && ta.value.trim() !== (r.text||'').trim())
        entry.text = ta.value.trim();
      if (r.params){
        const params = {};
        for (const k of Object.keys(r.params)){
          const el = document.querySelector('#p-'+r.id+'-'+k);
          if (!el) continue;
          if (Array.isArray(r.params[k])){
            const v = el.value.split('\n').map(s=>s.trim()).filter(Boolean);
            if (JSON.stringify(v)!==JSON.stringify(r.params[k])) params[k]=v;
          } else {
            const v = parseInt(el.value,10);
            if (!isNaN(v) && v!==r.params[k]) params[k]=v;
          }
        }
        if (Object.keys(params).length) entry.params = params;
      }
      if (!entry.text && !entry.params){
        alert('Rule '+r.id+' is marked AMENDED but nothing was changed — '+
              'either edit it or set it back to UPHELD.');
        return null;
      }
    }
    ruling.rules[r.id] = entry;
  }
  for (const p of REG.proposals||[]){
    const sel = document.querySelector('input[name=choice-'+p.id+']:checked');
    const notes = document.querySelector('#pnotes-'+p.id).value.trim();
    if (sel || notes)
      ruling.proposals[p.id] = {choice: sel ? sel.value : null, notes: notes};
  }
  if (!ruling.ruled_by){ alert('Sign the ruling — "ruled by" is empty.'); return null; }
  return ruling;
}

function rulingMd(ruling){
  const rules = Object.fromEntries(REG.rules.map(r=>[r.id,r]));
  const props = Object.fromEntries((REG.proposals||[]).map(p=>[p.id,p]));
  let md = "# Director's canon ruling\n\nRuled by: "+ruling.ruled_by+
           "\nRuled at: "+ruling.ruled_at+"\n\n";
  if (ruling.note) md += "> "+ruling.note+"\n\n";
  for (const [rid,e] of Object.entries(ruling.rules)){
    md += "## "+rid+" — "+(rules[rid]?rules[rid].title:'')+": **"+e.status+"**\n\n";
    if (e.text) md += 'Amended text: "'+e.text+'"\n\n';
    if (e.params) md += "Amended params: `"+JSON.stringify(e.params)+"`\n\n";
    if (e.reason) md += "Reason: "+e.reason+"\n\n";
  }
  for (const [pid,e] of Object.entries(ruling.proposals)){
    md += "## Proposal — "+(props[pid]?props[pid].title:pid)+": chose **"+
          (e.choice||'(none)')+"**\n\n";
    if (e.notes) md += e.notes+"\n\n";
  }
  return md;
}

async function generate(){
  const ruling = collect(); if (!ruling) return;
  const jsonText = JSON.stringify(ruling, null, 2)+"\n";
  const md = rulingMd(ruling);
  const out = document.querySelector('#out'); out.classList.add('show');
  const dl = (name, text) => '<a download="'+name+'" href="data:text/plain;charset=utf-8,'+
    encodeURIComponent(text)+'">download '+name+'</a>';
  let saved = '';
  try{
    const r = await fetch('/save_canon', {method:'POST',
      headers:{'Content-Type':'application/json'}, body: jsonText});
    saved = r.ok ? '<span style="color:var(--green)">'+esc(await r.text())+'</span>'
                 : '<span style="color:var(--ember)">'+esc(await r.text())+'</span>';
  }catch(e){
    saved = '<span class="note">not served by the console — use the downloads, '+
            'then drop both files into <code>canon/</code>.</span>';
  }
  out.innerHTML = '<p>'+dl('CANON-RULING.json', jsonText)+' · '+
    dl('CANON-RULING.md', md)+'</p><p>'+saved+'</p>'+
    '<p class="note">The next run of either pipeline reads this ruling and '+
    'writes what law was in force into its CANON-IN-FORCE.md. Commit '+
    'canon/CANON-RULING.* — the ruling is evidence.</p>'+
    '<pre>'+esc(md)+'</pre>';
  out.scrollIntoView({behavior:'smooth'});
}

// prefill from the existing ruling
for (const [rid,e] of Object.entries(RULING.rules||{})) setStatus(rid, e.status);
"""


def _rule_card(rule: dict, canon: Canon) -> str:
    rid = rule["id"]
    st = canon.status(rid)
    entry = (canon.ruling.get("rules") or {}).get(rid) or {}
    e = _html.escape
    parts = [f'<div class="card{" repealed-now" if st == "REPEALED" else ""}" id="card-{rid}">']
    parts.append(
        f'<div class="rhead"><b>{e(rule["title"])}</b>'
        f'<span class="rid">{rid} · {e(rule.get("kind", ""))}</span>'
        f'<span class="badge {st}" id="badge-{rid}">{st}</span></div>')
    parts.append(f'<div class="src">source: {e(rule.get("source", ""))} · '
                 f'enforced by: {e(rule.get("enforced_by", ""))}</div>')
    if rule.get("text"):
        parts.append(f'<div class="law">&ldquo;{e(rule["text"])}&rdquo;</div>')
        if st == "AMENDED" and entry.get("text"):
            parts.append(f'<div class="law amended-law">AMENDED to: '
                         f'&ldquo;{e(entry["text"])}&rdquo;</div>')
    if rule.get("params"):
        eff = canon.params(rid)
        parts.append('<div class="params">' + " · ".join(
            f"{e(k)} = {e(json.dumps(v))}" for k, v in eff.items())
            + "</div>")
    if rule.get("note"):
        parts.append(f'<div class="note" style="margin-top:6px">{e(rule["note"])}</div>')

    # controls
    checked = {s: (" checked" if st == s else "") for s in
               ("UPHELD", "AMENDED", "REPEALED")}
    repeal = (f'<label><input type="radio" name="st-{rid}" value="REPEALED"'
              f'{checked["REPEALED"]} onchange="setStatus(\'{rid}\',\'REPEALED\')"> repeal</label>'
              if rule.get("repealable", True) else
              f'<span class="norepeal">not repealable — '
              f'{e(rule.get("why_not_repealable", "amend instead"))}</span>')
    parts.append(
        f'<div class="controls">'
        f'<label><input type="radio" name="st-{rid}" value="UPHELD"'
        f'{checked["UPHELD"]} onchange="setStatus(\'{rid}\',\'UPHELD\')"> uphold</label>'
        f'<label><input type="radio" name="st-{rid}" value="AMENDED"'
        f'{checked["AMENDED"]} onchange="setStatus(\'{rid}\',\'AMENDED\')"> amend</label>'
        f'{repeal}</div>')

    # amend editor
    ed = [f'<div class="editor{" show" if st == "AMENDED" else ""}" id="ed-{rid}">']
    if rule.get("kind") == "prose" or rule.get("text"):
        current = canon.text(rid)
        ed.append(f'<div class="plabel">amended text</div>'
                  f'<textarea id="text-{rid}">{e(current)}</textarea>')
    for k, v in (rule.get("params") or {}).items():
        eff_v = canon.param(rid, k, v)
        if isinstance(v, list):
            ed.append(f'<div class="plabel">{e(k)} (one per line)</div>'
                      f'<textarea id="p-{rid}-{k}">'
                      + e("\n".join(str(x) for x in eff_v)) + '</textarea>')
        else:
            ed.append(f'<div class="plabel">{e(k)}</div>'
                      f'<input type="number" id="p-{rid}-{k}" value="{eff_v}">')
    ed.append(f'<div class="plabel">reason (goes into the ruling and every '
              f'run log)</div>'
              f'<input type="text" id="reason-{rid}" '
              f'value="{e(entry.get("reason", ""))}">')
    ed.append('</div>')
    parts += ed
    parts.append('</div>')
    return "".join(parts)


def _proposal_card(prop: dict, canon: Canon) -> str:
    e = _html.escape
    pid = prop["id"]
    entry = (canon.ruling.get("proposals") or {}).get(pid) or {}
    opts = "".join(
        f'<label class="opt"><input type="radio" name="choice-{pid}" '
        f'value="{e(o["key"])}"'
        f'{" checked" if entry.get("choice") == o["key"] else ""}> '
        f'{e(o["label"])}</label>'
        for o in prop.get("options", []))
    return (
        f'<div class="card"><div class="rhead"><b>{e(prop["title"])}</b>'
        f'<span class="rid">{pid} · raised {e(prop.get("raised", ""))} · '
        f'targets {e(", ".join(prop.get("targets", [])))}</span></div>'
        f'<div class="note" style="margin:6px 0 8px">{e(prop.get("context", ""))}</div>'
        f'{opts}'
        f'<div class="editor show"><div class="plabel">notes for the ruling '
        f'(the "specific circumstances", N for fading, etc.)</div>'
        f'<textarea id="pnotes-{pid}">{e(entry.get("notes", ""))}</textarea>'
        f'</div></div>')


def render_bible(canon: Canon | None = None) -> str:
    canon = canon or Canon.load()
    e = _html.escape
    groups: dict[str, list[str]] = {}
    for rule in canon.registry.get("rules", []):
        groups.setdefault(rule.get("group", "other"), []).append(
            _rule_card(rule, canon))
    titles = {"minigame": "Encounter law — the mini-game pipeline",
              "ger": "Narration law — the verb-teaching pipeline"}
    sections = "".join(
        f"<h2>{e(titles.get(g, g))}</h2>" + "".join(cards)
        for g, cards in groups.items())
    proposals = canon.proposals
    prop_html = ""
    if proposals:
        prop_html = ("<h2>Proposed amendments awaiting ruling</h2>"
                     + "".join(_proposal_card(p, canon) for p in proposals))
    ruled = ""
    if canon.ruling:
        n_hist = len(canon.ruling.get("history") or [])
        ruled = (f'<p class="note">Ruling on file: by '
                 f'{e(str(canon.ruling.get("ruled_by", "(unsigned)")))} at '
                 f'{e(str(canon.ruling.get("ruled_at", "(undated)")))} '
                 f'(sha256:{canon.ruling_sha})'
                 + (f' · {n_hist} prior ruling(s) in history' if n_hist else "")
                 + '. A new ruling REPLACES it; the old one is preserved in '
                   'the history array.</p>')
    bench = f"""
<div class="bench"><h2 style="margin-top:0">The bench</h2>
{ruled}
<div class="row"><input type="text" id="ruled-by" placeholder="ruled by (sign it)"
  value="{e(str(canon.ruling.get('ruled_by') or 'Nicholas Rouke'))}"></div>
<div class="row"><input type="text" id="ruling-note"
  placeholder="one-line note for this ruling (optional)"
  value="{e(str(canon.ruling.get('note') or ''))}"></div>
<div class="row"><button onclick="generate()">Generate Director's ruling ▸</button></div>
<div id="out"></div>
</div>"""
    data = (f"<script>window.__REGISTRY__={json.dumps(canon.registry)};"
            f"window.__RULING__={json.dumps(canon.ruling or None)};</script>")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>uhta · canon bible</title><style>{_CSS}</style></head><body>
<header><h1><b>uhta</b> · the canon bible</h1>
<p>Every rule the two Evaluators enforce, and the bench to rule on them.
A rule is <b style="color:var(--green)">UPHELD</b> (the default),
<b style="color:var(--gold)">AMENDED</b> (your edited law is enforced instead;
the baseline is kept as history), or
<b style="color:var(--ember)">REPEALED</b> (not enforced — and the skip is
logged in every run's CANON-IN-FORCE.md). There is deliberately no ignore
button: a silent skip would make every green run log unfalsifiable. This page
changes nothing by itself — it writes a <i>ruling</i>
(canon/CANON-RULING.json), and the next run obeys it.</p></header>
<div class="wrap">{sections}{prop_html}{bench}</div>
{data}<script>{_JS}</script></body></html>"""


def main() -> int:
    out = REPO_ROOT / "canon" / "CANON-BIBLE.html"
    out.write_text(render_bible(), encoding="utf-8")
    print(f"wrote {out.relative_to(REPO_ROOT)}")
    if "--no-open" not in sys.argv:
        try:
            webbrowser.open(out.as_uri())
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
