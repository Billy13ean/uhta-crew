"""Run rooms — one window per run, ending at its human decision.

The console's launch cards open a room (`/run?id=<run-id>`) in a new
window: live log tail while the agents work, the artifact shelf, and —
the point — the run's DECISION PANEL. Every pipeline in this repo ends
at a human gate; the room detects which gate this run is waiting at and
renders it as a form whose button writes the decision back into the run
directory as committed evidence:

    minigame propose  -> DIRECTOR-SELECTION.md (+ one-click build launches)
    A3 crew           -> the Ruling block INSIDE contradictions-<run>.md
    A6 narration GER  -> the Director-selection block INSIDE teaching-lines.md

Nothing here talks to an agent, and nothing here can run one — recording
a decision writes a file; launching a build POSTs to the same /start the
launch cards use. The gates did not move; they grew buttons (again).

Detection and recording are deterministic string work over the pipelines'
own stable templates (keeper.RULING_BLOCK, ger/assemble's selection
block, the dashboard's DIRECTOR-SELECTION format). A decision is
"recorded" when the template's signature placeholder is gone — the same
test a human reading the file would apply.
"""
from __future__ import annotations

import html as _html
import json
import re
import time
from pathlib import Path

SIG_PLACEHOLDER = "**Signed (Director):** _______________"

VALID_VERDICTS = ("UPHOLD", "AMEND", "DEFER")


# ---------------------------------------------------------------------------
# detection
# ---------------------------------------------------------------------------

def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def detect_decisions(run_dir: Path) -> list[dict]:
    """Every human gate present in this run directory, with its state."""
    out: list[dict] = []

    # -- minigame propose: candidate selection --------------------------
    cand_file = run_dir / "CANDIDATES.json"
    if cand_file.exists():
        try:
            data = json.loads(_read(cand_file))
        except json.JSONDecodeError:
            data = {}
        cards = ([{"id": d.get("id"), "name": d.get("name", d.get("id")),
                   "status": "ACCEPTED",
                   "premise": str(d.get("premise", ""))[:220]}
                  for d in data.get("accepted", [])]
                 + [{"id": s, "name": s, "status": "ESCALATED", "premise":
                     "Escalated by the circuit breaker — locked."}
                    for s in data.get("escalated", [])])
        sel = run_dir / "DIRECTOR-SELECTION.md"
        approved: list[str] = []
        if sel.exists():
            m = re.search(r"^Approved:\s*(.*)$", _read(sel), re.MULTILINE)
            if m:
                approved = [x.strip() for x in m.group(1).split(",")
                            if x.strip()]
        out.append({
            "kind": "mg-select",
            "title": "Director's selection — encounter mini-games",
            "recorded": sel.exists(),
            "approved": approved,
            "candidates": cards,
            "dashboard": (f"out/{run_dir.name}/MINIGAME-DASHBOARD.html"
                          if (run_dir / "MINIGAME-DASHBOARD.html").exists()
                          else None),
            "artifact": f"out/{run_dir.name}/DIRECTOR-SELECTION.md",
        })

    # -- A3 crew: the Keeper's Ruling block -----------------------------
    for f in sorted(run_dir.glob("contradictions-*.md")):
        text = _read(f)
        if "## Ruling" not in text:
            continue
        verdict_m = re.search(r"## Coherence verdict\s*\n+([^\n]+)", text)
        flags = re.findall(r"^### (\[[A-Z-]+\][^\n|]*)", text, re.MULTILINE)
        rec_m = re.search(r"## Coherence recommendation\s*\n+(.*?)(?:\n\n|\Z)",
                          text, re.DOTALL)
        out.append({
            "kind": "crew-ruling",
            "title": f"Director's ruling — {f.name}",
            "recorded": SIG_PLACEHOLDER not in text,
            "file": f.name,
            "coherence": (verdict_m.group(1).strip() if verdict_m else ""),
            "flags": [x.strip() for x in flags],
            "recommendation": (rec_m.group(1).strip()[:900] if rec_m else ""),
            "artifact": f"out/{run_dir.name}/{f.name}",
        })

    # -- A6 narration GER: teaching-lines selection ---------------------
    tl = run_dir / "teaching-lines.md"
    if tl.exists():
        text = _read(tl)
        rows = re.findall(r"^\| `(\w+)` \| ([^|]+) \| (.*?) \|$",
                          text, re.MULTILINE)
        out.append({
            "kind": "ger-selection",
            "title": "Director selection — teaching lines",
            "recorded": SIG_PLACEHOLDER not in text,
            "verbs": [{"verb": v, "status": s.strip(), "line": ln.strip()}
                      for v, s, ln in rows],
            "artifact": f"out/{run_dir.name}/teaching-lines.md",
        })

    return out


# ---------------------------------------------------------------------------
# recording
# ---------------------------------------------------------------------------

class DecisionError(RuntimeError):
    pass


def record_decision(run_dir: Path, kind: str, payload: dict) -> str:
    signed = str(payload.get("signed", "")).strip()
    if not signed:
        raise DecisionError("unsigned — a ruling without a name is not "
                            "evidence")
    date = time.strftime("%Y-%m-%d")

    if kind == "mg-select":
        approved = [str(x) for x in (payload.get("approved") or [])]
        if not approved:
            raise DecisionError("no candidates approved — approve at least "
                                "one, or leave the gate open")
        try:
            data = json.loads(_read(run_dir / "CANDIDATES.json"))
        except json.JSONDecodeError:
            raise DecisionError("CANDIDATES.json unreadable")
        known = {d.get("id") for d in data.get("accepted", [])}
        bad = [a for a in approved if a not in known]
        if bad:
            raise DecisionError(f"unknown/escalated candidate id(s): {bad}")
        rejected = sorted(known - set(approved))
        lines = ["# DIRECTOR SELECTION — encounter mini-games", "",
                 f"Run: {run_dir.name}",
                 f"Approved: {', '.join(approved)}",
                 f"Rejected/held: {', '.join(rejected)}", "",
                 "## Build commands (one per approved design)", ""]
        for a in approved:
            lines.append(f"python3 run_minigame.py --build --select {a} "
                         f"--from-run {run_dir.name} --run-id build-{a}")
        lines += ["", f"Signed (Director): {signed}", f"Date: {date}",
                  "", "*Recorded via the crew console run room.*"]
        (run_dir / "DIRECTOR-SELECTION.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")
        return (f"recorded out/{run_dir.name}/DIRECTOR-SELECTION.md — "
                f"{len(approved)} approved")

    if kind == "crew-ruling":
        fname = str(payload.get("file", ""))
        f = run_dir / fname
        if not fname.startswith("contradictions-") or not f.exists():
            raise DecisionError(f"no such contradictions file: {fname!r}")
        verdict = str(payload.get("verdict", "")).upper()
        if verdict not in VALID_VERDICTS:
            raise DecisionError(f"verdict must be one of {VALID_VERDICTS}")
        klass = str(payload.get("klass", "")).strip() or "n/a"
        canon_line = str(payload.get("canon_line", "")).strip()
        if verdict == "AMEND" and not canon_line:
            raise DecisionError("AMEND requires the CANON line the Keeper "
                                "will transcribe")
        text = _read(f)
        if SIG_PLACEHOLDER not in text:
            raise DecisionError("this ruling is already recorded — edit the "
                                "file directly if it must change")
        subs = [
            (r"\*\*Class answered:\*\* _\(.*?\)_",
             f"**Class answered:** {klass}"),
            (r"\*\*Verdict:\*\* _\(exactly one of\)_ "
             r"`UPHOLD` \| `AMEND` \| `DEFER`",
             f"**Verdict:** `{verdict}`"),
            (r"\*\*Signed \(Director\):\*\* _+\s+\*\*Date:\*\* _+",
             f"**Signed (Director):** {signed}  **Date:** {date}"),
        ]
        for pat, repl in subs:
            text, n = re.subn(pat, repl.replace("\\", "\\\\"), text,
                              count=1, flags=re.DOTALL)
            if n != 1:
                raise DecisionError(
                    f"ruling template drifted — could not fill {pat[:40]!r}. "
                    f"Fill the block in the file by hand.")
        if canon_line:
            text = text.replace(
                "**CANON line added (AMEND only):**",
                f"**CANON line added (AMEND only):** {canon_line}", 1)
        text += (f"\n*Ruling recorded via the crew console run room, "
                 f"{date}.*\n")
        f.write_text(text, encoding="utf-8")
        return (f"recorded ruling `{verdict}` in out/{run_dir.name}/{fname}"
                + (" — the Keeper transcribes the CANON line next run"
                   if verdict == "AMEND" else ""))

    if kind == "ger-selection":
        f = run_dir / "teaching-lines.md"
        if not f.exists():
            raise DecisionError("no teaching-lines.md in this run")
        selection = str(payload.get("selection", "")).strip()
        if not selection:
            raise DecisionError("empty selection — say apply-as-is, or name "
                                "the edits/rejections per verb")
        text = _read(f)
        if SIG_PLACEHOLDER not in text:
            raise DecisionError("this selection is already recorded")
        text, n1 = re.subn(
            r"\*\*Apply as-is / edit / reject \(per verb\):\*\* _+",
            "**Apply as-is / edit / reject (per verb):** "
            + selection.replace("\\", "\\\\"),
            text, count=1)
        text, n2 = re.subn(
            r"\*\*Signed \(Director\):\*\* _+\s+\*\*Date:\*\* _+",
            f"**Signed (Director):** {signed}  **Date:** {date}",
            text, count=1)
        if n1 != 1 or n2 != 1:
            raise DecisionError("selection template drifted — fill the "
                                "block in the file by hand.")
        f.write_text(text, encoding="utf-8")
        return f"recorded Director selection in out/{run_dir.name}/teaching-lines.md"

    raise DecisionError(f"unknown decision kind {kind!r}")


# ---------------------------------------------------------------------------
# the room page
# ---------------------------------------------------------------------------

_ROOM_JS = r"""
const RID = %RID%;
let lastState = null;

function esc(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}

function decisionPanel(d, i){
  const rec = d.recorded
    ? `<span class="badge done">RECORDED</span>
       <a href="/view?p=${encodeURIComponent(d.artifact)}" target="_blank">open the record</a>`
    : `<span class="badge open">AWAITING THE DIRECTOR</span>`;
  let body = '';
  if (d.kind === 'mg-select'){
    body = d.candidates.map(c => `
      <label class="candrow ${c.status!=='ACCEPTED'?'locked':''}">
        <input type="checkbox" class="mgpick-${i}" value="${esc(c.id)}"
          ${c.status!=='ACCEPTED'?'disabled':''}
          ${d.approved.includes(c.id)?'checked':''} ${d.recorded?'disabled':''}>
        <b>${esc(c.name)}</b> <span class="dim">${esc(c.id)} · ${esc(c.status)}</span>
        <div class="dim">${esc(c.premise)}</div>
      </label>`).join('')
      + (d.dashboard ? `<p><a href="/view?p=${encodeURIComponent(d.dashboard)}"
          target="_blank">open the full dashboard (rules, visuals, judge citations)</a></p>` : '')
      + (d.recorded
        ? `<div class="buildrow"><span class="dim">Launch the approved build(s):</span>
           ${d.approved.map(a => `<button class="mini"
             onclick="launchBuild('${esc(a)}')">build ${esc(a)} ▸</button>`).join(' ')}
           <select id="buildmode-${i}"><option>mock</option><option selected>live</option></select></div>`
        : `<div class="act"><input type="text" id="sig-${i}" placeholder="signed (Director)" value="Nicholas Rouke">
           <button onclick="decide(${i},'mg-select')">Record selection ▸</button></div>`);
  }
  if (d.kind === 'crew-ruling'){
    body = `<p class="dim">${esc(d.coherence)}</p>`
      + d.flags.map(f => `<p class="flag">${esc(f)}</p>`).join('')
      + (d.recommendation ? `<details><summary>Keeper's recommendation</summary>
         <p class="dim">${esc(d.recommendation)}</p></details>` : '')
      + (d.recorded ? '' : `
        <div class="act">
          <input type="text" id="klass-${i}" placeholder="class answered (e.g. CONTRADICTS-LOCKED, or n/a)">
          <span class="verdicts">
            <label><input type="radio" name="verdict-${i}" value="UPHOLD"> UPHOLD</label>
            <label><input type="radio" name="verdict-${i}" value="AMEND"> AMEND</label>
            <label><input type="radio" name="verdict-${i}" value="DEFER"> DEFER</label>
          </span>
          <textarea id="canon-${i}" placeholder="CANON line added (AMEND only)"></textarea>
          <input type="text" id="sig-${i}" placeholder="signed (Director)" value="Nicholas Rouke">
          <button onclick="decide(${i},'crew-ruling','${esc(d.file)}')">Record ruling ▸</button>
        </div>`);
  }
  if (d.kind === 'ger-selection'){
    body = `<table class="verbs">` + d.verbs.map(v =>
      `<tr><td><code>${esc(v.verb)}</code></td><td>${esc(v.status)}</td>
       <td>${esc(v.line)}</td></tr>`).join('') + `</table>`
      + (d.recorded ? '' : `
        <div class="act">
          <input type="text" id="sel-${i}" value="Apply as-is"
            placeholder="Apply as-is / edit / reject (per verb)">
          <input type="text" id="sig-${i}" placeholder="signed (Director)" value="Nicholas Rouke">
          <button onclick="decide(${i},'ger-selection')">Record selection ▸</button>
        </div>`);
  }
  return `<div class="card decision"><div class="dhead"><b>${esc(d.title)}</b> ${rec}</div>${body}
          <div class="msg" id="msg-${i}"></div></div>`;
}

async function decide(i, kind, file){
  const payload = {run: RID, kind: kind,
                   signed: (document.querySelector('#sig-'+i)||{}).value};
  if (kind === 'mg-select')
    payload.approved = [...document.querySelectorAll('.mgpick-'+i+':checked')].map(x=>x.value);
  if (kind === 'crew-ruling'){
    payload.file = file;
    payload.klass = (document.querySelector('#klass-'+i)||{}).value;
    const v = document.querySelector('input[name=verdict-'+i+']:checked');
    payload.verdict = v ? v.value : '';
    payload.canon_line = (document.querySelector('#canon-'+i)||{}).value;
  }
  if (kind === 'ger-selection')
    payload.selection = (document.querySelector('#sel-'+i)||{}).value;
  const r = await fetch('/decide', {method:'POST',
    headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  const t = await r.text();
  const el = document.querySelector('#msg-'+i);
  el.innerHTML = r.ok ? `<span class="ok">${esc(t)}</span>`
                      : `<span class="bad">${esc(t)}</span>`;
  if (r.ok) setTimeout(poll, 600);
}

async function launchBuild(id){
  const sel = document.querySelector('select[id^=buildmode]');
  const mode = sel ? sel.value : 'live';
  const rid = 'build-' + id + '-' + new Date().toISOString().slice(11,19).replaceAll(':','');
  await fetch('/start', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({pipeline:'minigame', mode: mode, run_id: rid,
      extra: '--build --select ' + id + ' --from-run ' + RID})});
  window.open('/run?id=' + encodeURIComponent(rid), '_blank');
}

async function poll(){
  const r = await fetch('/run_state?id=' + encodeURIComponent(RID));
  if (!r.ok){ document.querySelector('#status').textContent = 'run not found (yet)';
              setTimeout(poll, 2500); return; }
  const st = await r.json();
  document.querySelector('#status').innerHTML =
    `<span class="badge ${st.state==='running'?'run':(st.ok===false?'bad':'done')}">${esc(st.state)}</span>
     <span class="dim">${esc(st.pipeline||'')} ${esc(st.mode||'')}</span>`;
  document.querySelector('#tail').textContent = st.tail || '(no log yet)';
  document.querySelector('#arts').innerHTML = (st.artifacts||[]).map(a =>
    `<a href="/view?p=${encodeURIComponent('out/'+RID+'/'+a)}"
       ${a.endsWith('.html')?'target="_blank"':''}>${esc(a)}</a>`).join(' · ');
  const dEl = document.querySelector('#decisions');
  const key = JSON.stringify(st.decisions);
  if (key !== lastState){ lastState = key;
    dEl.innerHTML = (st.decisions||[]).length
      ? st.decisions.map(decisionPanel).join('')
      : '<p class="dim">No structured decision gate in this run (or not emitted yet).</p>';
  }
  setTimeout(poll, st.state === 'running' ? 2000 : 6000);
}
poll();
"""

_ROOM_CSS = """
.roomwrap{padding:18px 32px;max-width:1080px}
#status{margin:6px 0 14px}
.badge{font:11px monospace;letter-spacing:.06em;padding:3px 9px;border-radius:10px;
border:1px solid var(--line);color:var(--dim)}
.badge.run{color:var(--gold);border-color:var(--gold)}
.badge.done{color:var(--green);border-color:var(--green)}
.badge.bad{color:var(--ember);border-color:var(--ember)}
.badge.open{color:var(--gold);border-color:var(--gold)}
.card.decision{background:var(--card);border:1px solid var(--gold);border-radius:10px;
padding:16px 20px;margin:14px 0}
.dhead{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;margin-bottom:8px}
.dhead b{color:var(--gold);font-weight:normal;font-size:15.5px}
.dhead a{color:var(--gold);font-size:12.5px}
.card.decision a{color:var(--gold)}
.dim{color:var(--dim);font-size:12.5px}
.candrow{display:block;border:1px solid var(--line);border-radius:8px;
padding:8px 12px;margin:6px 0;cursor:pointer}
.candrow.locked{opacity:.5}
.candrow input{accent-color:var(--gold);margin-right:8px}
.flag{background:#0f0f14;border:1px solid var(--ember);border-radius:8px;
padding:8px 12px;font-size:13px}
.act{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}
.act input[type=text]{flex:1;min-width:180px;background:#0f0f14;color:var(--ink);
border:1px solid var(--line);border-radius:7px;font:12.5px monospace;padding:8px 10px}
.act textarea{width:100%;min-height:52px;background:#0f0f14;color:var(--ink);
border:1px solid var(--line);border-radius:7px;font:12.5px monospace;padding:8px 10px}
.verdicts label{margin-right:10px;font-size:13px;cursor:pointer}
.verdicts input{accent-color:var(--gold)}
.verbs{border-collapse:collapse;font-size:13px}
.verbs td{border-bottom:1px solid var(--line);padding:5px 10px 5px 0;vertical-align:top}
.msg .ok{color:var(--green);font-size:13px}.msg .bad{color:var(--ember);font-size:13px}
button.mini{padding:5px 12px;font-size:12.5px}
.buildrow{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px}
#arts{font-size:12.5px}#arts a{color:var(--dim)}#arts a:hover{color:var(--gold)}
"""


def render_room(run_id: str, base_css: str, page_shell) -> bytes:
    """page_shell is run_console.page(title, body) — reuse the console chrome."""
    body = (f"<div class='roomwrap'>"
            f"<h3 style='margin:4px 0'>run room · "
            f"<span style='color:var(--gold)'>{_html.escape(run_id)}</span></h3>"
            f"<div id='status'>…</div>"
            f"<div id='decisions'></div>"
            f"<h3>log</h3><pre id='tail'>…</pre>"
            f"<h3>artifacts</h3><div id='arts'></div>"
            f"</div>"
            f"<style>{_ROOM_CSS}</style>"
            f"<script>{_ROOM_JS.replace('%RID%', json.dumps(run_id))}</script>")
    return page_shell(f"run · {run_id}", body)


def run_state(run_id: str, out_dir: Path, jobs: list[dict],
              job_state_fn) -> dict | None:
    run_dir = out_dir / run_id
    job = next((j for j in reversed(jobs) if j.get("run_id") == run_id), None)
    if job is None and not run_dir.is_dir():
        return None
    state: dict = {"run_id": run_id}
    if job is not None:
        state.update(job_state_fn(job))
    else:
        state["state"] = "no live job (console restarted or run pre-dates it)"
        mf = run_dir / "manifest.json"
        if mf.exists():
            try:
                state["state"] = json.loads(_read(mf)).get("status", "?")
            except json.JSONDecodeError:
                pass
        state["tail"] = ""
    state["artifacts"] = (sorted(p.name for p in run_dir.iterdir()
                                 if p.is_file())
                          if run_dir.is_dir() else [])
    state["decisions"] = (detect_decisions(run_dir)
                          if run_dir.is_dir() else [])
    return state
