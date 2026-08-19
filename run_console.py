#!/usr/bin/env python3
"""uhta crew console — every pipeline behind one local page. No terminal.

    python3 run_console.py            # serves http://127.0.0.1:8765 and opens it

One page per concern:

    /            launch any pipeline (crew / content / builder / ger /
                 minigame) in selftest, mock, or live mode, with a run id and
                 extra args; watch running jobs and their log tails live
    /runs        every run directory, newest first, with its artifacts
    /run?id=...  the RUN ROOM — live log while agents work, then the run's
                 human gate rendered as a form: approve mini-game candidates
                 (and launch builds), rule on a Keeper flag, sign off
                 teaching lines. The button writes the decision into the run
                 directory as recorded evidence.
    /bible       the canon bible — every rule the Evaluators enforce, as
                 cards the Director rules on (uphold / amend / repeal, no
                 ignore); saving writes canon/CANON-RULING.json + .md and
                 the next run obeys it
    /view?p=...  read any artifact — markdown as text, HTML (the mini-game
                 DASHBOARD included) rendered in place
    ruling box   save a DIRECTOR-SELECTION.md into a run folder, and launch
                 the approved build straight from the page

Design constraints, deliberate:

  * stdlib only (http.server + subprocess + threading) — the assignment's
    one-dependency budget stays spent on `anthropic`.
  * the console NEVER talks to an agent. It starts entry points and reads
    the blackboard's files — the same contract the Director already has at
    the terminal, with buttons. The human gates stay exactly where they
    were; this page just walks to them.
  * binds 127.0.0.1 only. It is a cockpit, not a service.
  * live mode: the console loads `.env` itself and passes the key into the
    child process env, so native live runs work the same way docker ones do.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import console_rooms

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
LOGS = OUT / "console-logs"

PIPELINES = {
    "crew":     {"script": "run_crew.py",     "title": "A3 · rules crew",
                 "blurb": "the game's numbers — designer, red-teamer, keeper, playtester"},
    "content":  {"script": "run_content.py",  "title": "A4 · content pipeline",
                 "blurb": "the game's words in bulk — retriever, writer, critic"},
    "builder":  {"script": "run_builder.py",  "title": "A5 · coding agent",
                 "blurb": "GDD → gap → priority → patch"},
    "ger":      {"script": "run_ger.py",      "title": "A6 · narration GER",
                 "blurb": "generator → evaluator → refiner → breaker (verb narration)"},
    "minigame": {"script": "run_minigame.py", "title": "A6 · mini-game GER",
                 "blurb": "designs → judge → YOUR dashboard → programmer"},
}
MODES = {"selftest": ["--selftest"], "mock": ["--mock-llm"], "live": []}

_jobs: list[dict] = []
_lock = threading.Lock()


def _env_with_key() -> dict:
    import os
    env = dict(os.environ)
    # Windows: a child Python with redirected stdout defaults to cp1252,
    # and the first '\u2192' in a blackboard note kills a live run
    # (crew-020353, 2026-08-19). Force UTF-8 for every launched pipeline.
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    envfile = ROOT / ".env"
    if envfile.exists():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip())
    return env


def start_job(pipeline: str, mode: str, run_id: str, extra: str) -> dict:
    spec = PIPELINES[pipeline]
    args = [sys.executable, str(ROOT / spec["script"])] + MODES[mode][:]
    if run_id and mode != "selftest":
        args += ["--run-id", run_id]
    if pipeline == "minigame":
        args += ["--no-open"]          # the console shows the dashboard itself
    if extra.strip():
        args += extra.split()
    LOGS.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%H%M%S")
    log = LOGS / f"{pipeline}-{mode}-{stamp}.log"
    fh = open(log, "w", encoding="utf-8")
    proc = subprocess.Popen(args, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                            env=_env_with_key())
    job = {"id": f"{pipeline}-{mode}-{stamp}", "pipeline": pipeline,
           "mode": mode, "run_id": run_id, "args": " ".join(args[1:]),
           "log": str(log.relative_to(ROOT)), "proc": proc,
           "started": time.strftime("%H:%M:%S")}
    with _lock:
        _jobs.append(job)
    return job


def job_state(j: dict) -> dict:
    rc = j["proc"].poll()
    tail = ""
    try:
        text = (ROOT / j["log"]).read_text(encoding="utf-8", errors="replace")
        tail = "\n".join(text.splitlines()[-14:])
    except OSError:
        pass
    dash = ""
    if j["pipeline"] == "minigame" and j["run_id"]:
        cand = OUT / j["run_id"] / "MINIGAME-DASHBOARD.html"
        if cand.exists():
            dash = f"out/{j['run_id']}/MINIGAME-DASHBOARD.html"
    return {"id": j["id"], "pipeline": j["pipeline"], "mode": j["mode"],
            "run_id": j["run_id"], "started": j["started"],
            "state": "running" if rc is None else f"exit {rc}",
            "ok": rc == 0, "done": rc is not None, "tail": tail,
            "dashboard": dash}


CSS = """
:root{--bg:#0b0b0e;--card:#15151b;--ink:#d8d4c8;--dim:#8a8578;--gold:#e8b64c;
--ember:#c8503c;--green:#5cb46a;--line:#2a2a33}
*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);margin:0;
font:15px/1.55 Georgia,serif}
header{padding:22px 32px 14px;border-bottom:1px solid var(--line);display:flex;
gap:22px;align-items:baseline}
header h1{margin:0;font-size:20px;font-weight:normal}header h1 b{color:var(--gold);font-weight:normal}
header a{color:var(--dim);text-decoration:none;font-size:13px}header a:hover{color:var(--gold)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px;padding:22px 32px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
.card h2{margin:0 0 2px;font-size:16px;color:var(--gold);font-weight:normal}
.card .blurb{color:var(--dim);font-size:12.5px;margin:0 0 12px}
.row{display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap}
select,input[type=text]{background:#0f0f14;color:var(--ink);border:1px solid var(--line);
border-radius:6px;padding:7px 9px;font:13px monospace}
input[type=text]{flex:1;min-width:120px}
button{background:var(--gold);color:#0b0b0e;border:none;font:13.5px Georgia,serif;
padding:8px 16px;border-radius:7px;cursor:pointer}
button.ghost{background:transparent;color:var(--gold);border:1px solid var(--gold)}
.jobs{padding:0 32px 30px}.job{background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:12px 16px;margin-bottom:10px}
.job .head{display:flex;gap:12px;align-items:baseline}
.job .state{font:12px monospace}.ok{color:var(--green)}.bad{color:var(--ember)}
.run{color:var(--gold)}
pre{background:#0f0f14;border:1px solid var(--line);border-radius:8px;padding:10px 12px;
font:11.5px/1.5 monospace;overflow-x:auto;white-space:pre-wrap;color:var(--dim);margin:8px 0 0}
.runsrow{border-bottom:1px solid var(--line);padding:10px 0;display:flex;gap:14px;flex-wrap:wrap}
.runsrow b{color:var(--gold);font-weight:normal;min-width:220px}
.runsrow a{color:var(--dim);font-size:12.5px;text-decoration:none}
.runsrow a:hover{color:var(--gold)}
.wrap{padding:18px 32px}
textarea{width:100%;min-height:120px;background:#0f0f14;color:var(--ink);
border:1px solid var(--line);border-radius:8px;font:12px monospace;padding:10px}
h3{color:var(--gold);font-weight:normal;font-size:14px;letter-spacing:.08em;
text-transform:uppercase}
.note{color:var(--dim);font-size:12.5px}
"""

HOME_JS = """
async function start(p){
  const mode=document.querySelector('#mode-'+p).value;
  const rid=document.querySelector('#rid-'+p).value||p+'-'+new Date().toISOString().slice(11,19).replaceAll(':','');
  const extra=document.querySelector('#extra-'+p).value;
  await fetch('/start',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({pipeline:p,mode:mode,run_id:rid,extra:extra})});
  if (mode !== 'selftest') window.open('/run?id='+encodeURIComponent(rid),'_blank');
  poll();
}
async function saveRuling(){
  const run=document.querySelector('#ruling-run').value.trim();
  const text=document.querySelector('#ruling-text').value;
  if(!run||!text)return alert('run id and ruling text required');
  const r=await fetch('/save_ruling',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run:run,text:text})});
  document.querySelector('#ruling-msg').textContent=await r.text();
}
async function poll(){
  const r=await fetch('/jobs'); const jobs=await r.json();
  const el=document.querySelector('#jobs'); el.innerHTML='';
  for(const j of jobs.reverse()){
    const cls=j.done?(j.ok?'ok':'bad'):'run';
    el.innerHTML+=`<div class="job"><div class="head">
      <b>${j.pipeline}</b><span>${j.mode}</span>
      <span class="run">${j.run_id||''}</span>
      <span class="state ${cls}">${j.state}</span>
      <span class="note">${j.started}</span>
      ${j.run_id?`<a href="/run?id=${encodeURIComponent(j.run_id)}" target="_blank"
         style="color:var(--gold)">room →</a>`:''}
      ${j.dashboard?`<a href="/view?p=${encodeURIComponent(j.dashboard)}" target="_blank"
         style="color:var(--gold)">→ open the Director's dashboard</a>`:''}
      </div><pre>${j.tail.replace(/&/g,'&amp;').replace(/</g,'&lt;')}</pre></div>`;
  }
  if(jobs.some(j=>!j.done))setTimeout(poll,1500); else setTimeout(poll,5000);
}
poll();
"""


def page(title: str, body: str) -> bytes:
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
            f"<body><header><h1><b>uhta</b> · crew console</h1>"
            f"<a href='/'>launch</a><a href='/runs'>runs & artifacts</a>"
            f"<a href='/bible'>canon bible</a>"
            f"</header>{body}</body></html>").encode("utf-8")


def home() -> bytes:
    cards = ""
    for key, spec in PIPELINES.items():
        cards += f"""
<div class="card"><h2>{spec['title']}</h2><p class="blurb">{spec['blurb']}</p>
  <div class="row">
    <select id="mode-{key}"><option>selftest</option><option>mock</option>
      <option>live</option></select>
    <input type="text" id="rid-{key}" placeholder="run id (auto)">
  </div>
  <div class="row"><input type="text" id="extra-{key}"
       placeholder="extra args (e.g. --verbs flame · --slots vigil-hope)"></div>
  <div class="row"><button onclick="start('{key}')">start ▸</button></div>
</div>"""
    ruling = """
<div class="wrap"><h3>Director's ruling → run folder</h3>
<p class="note">Generate the ruling in a mini-game dashboard, paste it here,
and it is written to <code>out/&lt;run&gt;/DIRECTOR-SELECTION.md</code> —
committed evidence. Then launch the approved build above (pipeline
“mini-game”, extra args <code>--build --select &lt;id&gt; --from-run
&lt;run&gt;</code>).</p>
<div class="row"><input type="text" id="ruling-run" placeholder="propose run id (e.g. mg-live)"></div>
<textarea id="ruling-text" placeholder="# DIRECTOR SELECTION — paste from the dashboard"></textarea>
<div class="row" style="margin-top:8px"><button onclick="saveRuling()">save ruling</button>
<span class="note" id="ruling-msg"></span></div></div>"""
    body = (f"<div class='grid'>{cards}</div>"
            f"<div class='jobs'><h3 style='padding:0 32px'>jobs</h3><div style='padding:0 32px' id='jobs'></div></div>"
            f"{ruling}<script>{HOME_JS}</script>")
    return page("uhta crew console", body)


def runs_page() -> bytes:
    rows = ""
    if OUT.exists():
        dirs = sorted([d for d in OUT.iterdir() if d.is_dir()],
                      key=lambda d: d.stat().st_mtime, reverse=True)
        for d in dirs[:60]:
            arts = sorted(p.name for p in d.iterdir() if p.is_file())
            links = " · ".join(
                f"<a href='/view?p={urllib.parse.quote(f'out/{d.name}/{a}')}'"
                f"{' target=_blank' if a.endswith('.html') else ''}>{html.escape(a)}</a>"
                for a in arts[:12])
            more = f" <span class='note'>+{len(arts)-12} more</span>" if len(arts) > 12 else ""
            room = (f"<a href='/run?id={urllib.parse.quote(d.name)}' "
                    f"style='color:var(--gold)'>room →</a> · ")
            rows += (f"<div class='runsrow'><b>{html.escape(d.name)}</b>"
                     f"<span>{room}{links}{more}</span></div>")
    return page("runs", f"<div class='wrap'>{rows or '<p>no runs yet</p>'}</div>")


def safe_out_path(rel: str) -> Path | None:
    p = (ROOT / rel).resolve()
    try:
        p.relative_to(OUT.resolve())
    except ValueError:
        return None
    return p if p.is_file() else None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code: int, body: bytes, ctype: str = "text/html; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/":
            return self._send(200, home())
        if url.path == "/runs":
            return self._send(200, runs_page())
        if url.path == "/jobs":
            with _lock:
                states = [job_state(j) for j in _jobs]
            return self._send(200, json.dumps(states).encode(),
                              "application/json")
        if url.path == "/run":
            rid = re.sub(r"[^A-Za-z0-9._-]", "",
                         urllib.parse.parse_qs(url.query).get("id", [""])[0])
            if not rid:
                return self._send(404, b"no run id")
            return self._send(200, console_rooms.render_room(rid, CSS, page))
        if url.path == "/run_state":
            rid = re.sub(r"[^A-Za-z0-9._-]", "",
                         urllib.parse.parse_qs(url.query).get("id", [""])[0])
            with _lock:
                jobs = list(_jobs)
            st = console_rooms.run_state(rid, OUT, jobs, job_state)
            if st is None:
                return self._send(404, b"unknown run")
            return self._send(200, json.dumps(st).encode(),
                              "application/json")
        if url.path == "/bible":
            # regenerate from the CURRENT registry + ruling every time —
            # the console is long-running; the canon must never be stale
            from crew.bible import render_bible
            from crew.canon import Canon, CanonError
            try:
                return self._send(200,
                                  render_bible(Canon.load()).encode("utf-8"))
            except CanonError as exc:
                return self._send(500, page("canon error",
                    f"<div class='wrap'><h3>canon error</h3>"
                    f"<pre>{html.escape(str(exc))}</pre></div>"))
        if url.path == "/view":
            rel = urllib.parse.parse_qs(url.query).get("p", [""])[0]
            p = safe_out_path(rel)
            if not p:
                return self._send(404, b"not found")
            data = p.read_bytes()
            if p.suffix == ".html":
                return self._send(200, data)
            if p.suffix == ".png":
                return self._send(200, data, "image/png")
            body = (f"<div class='wrap'><h3>{html.escape(rel)}</h3>"
                    f"<pre>{html.escape(data.decode('utf-8', 'replace'))}</pre></div>")
            return self._send(200, page(rel, body))
        return self._send(404, b"not found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, b"bad json")
        if self.path == "/start":
            pipeline = data.get("pipeline")
            mode = data.get("mode")
            if pipeline not in PIPELINES or mode not in MODES:
                return self._send(400, b"unknown pipeline or mode")
            rid = re.sub(r"[^A-Za-z0-9._-]", "", str(data.get("run_id", "")))
            extra = str(data.get("extra", ""))[:300]
            job = start_job(pipeline, mode, rid, extra)
            return self._send(200, json.dumps({"started": job["id"]}).encode(),
                              "application/json")
        if self.path == "/decide":
            rid = re.sub(r"[^A-Za-z0-9._-]", "", str(data.get("run", "")))
            run_dir = OUT / rid
            if not rid or not run_dir.is_dir():
                return self._send(404, f"no run directory out/{rid}".encode())
            try:
                msg = console_rooms.record_decision(
                    run_dir, str(data.get("kind", "")), data)
            except console_rooms.DecisionError as exc:
                return self._send(400, str(exc).encode("utf-8"))
            return self._send(200, msg.encode("utf-8"))
        if self.path == "/save_canon":
            # A canon ruling from the Bible page. Validated against the
            # registry BEFORE it touches disk; the prior ruling (if any) is
            # preserved in the new file's history array — rulings replace,
            # they never erase.
            from crew.canon import render_ruling_md, validate_ruling
            rules_path = ROOT / "canon" / "rules.json"
            if not rules_path.exists():
                return self._send(500, b"canon/rules.json missing")
            registry = json.loads(rules_path.read_text(encoding="utf-8"))
            ruling = {k: v for k, v in data.items() if k != "history"}
            ruling_path = ROOT / "canon" / "CANON-RULING.json"
            history = []
            if ruling_path.exists():
                try:
                    prior = json.loads(ruling_path.read_text(encoding="utf-8"))
                    history = (prior.pop("history", None) or []) + [prior]
                except json.JSONDecodeError:
                    pass
            if history:
                ruling["history"] = history[-20:]
            errors = validate_ruling(registry, ruling)
            if errors:
                return self._send(400, ("REJECTED — " + "; ".join(errors))
                                  .encode("utf-8"))
            ruling_path.write_text(
                json.dumps(ruling, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
            (ROOT / "canon" / "CANON-RULING.md").write_text(
                render_ruling_md(registry, ruling), encoding="utf-8")
            n = len([r for r in (ruling.get("rules") or {})])
            p = len([r for r in (ruling.get("proposals") or {})])
            return self._send(200, (
                f"saved canon/CANON-RULING.json + .md ({n} rule ruling(s), "
                f"{p} proposal choice(s)"
                + (f", {len(history)} prior preserved in history" if history
                   else "") + ") — the next run obeys it").encode("utf-8"))
        if self.path == "/save_ruling":
            rid = re.sub(r"[^A-Za-z0-9._-]", "", str(data.get("run", "")))
            run_dir = OUT / rid
            if not rid or not run_dir.is_dir():
                return self._send(404, f"no run directory out/{rid}".encode())
            text = str(data.get("text", ""))[:20000]
            (run_dir / "DIRECTOR-SELECTION.md").write_text(text, encoding="utf-8")
            return self._send(200, f"saved out/{rid}/DIRECTOR-SELECTION.md".encode())
        return self._send(404, b"not found")


def main() -> int:
    port = 8765
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    in_container = Path("/.dockerenv").exists()
    # native: localhost only (a cockpit, not a service). In docker the
    # container boundary provides the isolation and 127.0.0.1 would be
    # unreachable from the host browser — bind wide INSIDE the container
    # and let `-p 8765:8765` decide what the host exposes.
    host = "0.0.0.0" if in_container else "127.0.0.1"
    if "--host" in sys.argv:
        host = sys.argv[sys.argv.index("--host") + 1]
    srv = ThreadingHTTPServer((host, port), Handler)
    url = f"http://127.0.0.1:{port}"
    print(f"uhta crew console · {url}   (bound {host}, Ctrl+C to stop)")
    if in_container:
        print("  (in docker — open the URL above in your host browser)")
    elif "--no-open" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nconsole stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
