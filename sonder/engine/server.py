"""server.py — serves the terminal page and the DM over localhost. Stdlib only.

  GET  /                 the terminal (web/index.html)
  GET  /api/perspectives the six people you can be
  POST /api/new          {perspective, seed?}      -> opening + session id
  POST /api/turn         {session, text}           -> the turn record
  GET  /api/state?session=ID
  GET  /api/transcript?session=ID  (markdown)
"""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from . import world, story, agent, art
from .session import Session

WEB = Path(__file__).resolve().parent.parent / "web" / "index.html"


def make_handler(dm, default_seed=None, allow_pick=False):
    sessions: dict[str, Session] = {}
    lock = threading.Lock()

    class H(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # quiet
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _json(self):
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")

        def do_GET(self):
            u = urlparse(self.path)
            if u.path in ("/", "/index.html"):
                page = WEB.read_text(encoding="utf-8").replace("__TITLE_ART__", json.dumps(art.TITLE))
                return self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            if u.path == "/api/info":
                return self._send(200, {"dm": {"backend": dm.name, "model": getattr(dm, "model", "")},
                                        "eras": list(story.ERA_OPENERS), "allow_pick": allow_pick})
            q = parse_qs(u.query)
            sid = (q.get("session") or [""])[0]
            s = sessions.get(sid)
            if u.path == "/api/state":
                return self._send(200, s.state()) if s else self._send(404, {"error": "no such session"})
            if u.path == "/api/transcript":
                if not s:
                    return self._send(404, {"error": "no such session"})
                return self._send(200, (s.dir / "transcript.md").read_bytes(), "text/markdown; charset=utf-8")
            return self._send(404, {"error": "not found"})

        def do_POST(self):
            u = urlparse(self.path)
            try:
                body = self._json()
                if u.path == "/api/new":
                    # the player does not choose who they are (Director ruling 2026-08-21);
                    # --dev-pick re-enables it for testing only
                    p = body.get("perspective") if allow_pick else None
                    era = body.get("era") if allow_pick else None
                    seed = body.get("seed", default_seed)
                    s = Session(dm, p, seed=seed, era=era)
                    with lock:
                        sessions[s.id] = s
                    out = dict(s.opening)
                    out["session"] = s.id
                    out["dm"] = {"backend": dm.name, "model": getattr(dm, "model", "")}
                    return self._send(200, out)
                if u.path == "/api/turn":
                    s = sessions.get(body.get("session", ""))
                    if not s:
                        return self._send(404, {"error": "no such session — start again"})
                    with lock:  # one turn at a time per process; the ledger is not re-entrant
                        rec = s.turn(body.get("text", ""))
                    return self._send(200, rec)
                return self._send(404, {"error": "not found"})
            except agent.DMError as e:
                return self._send(502, {"error": str(e)})
            except Exception as e:  # surface it in the terminal rather than a blank 500
                return self._send(500, {"error": f"{type(e).__name__}: {e}"})

    return H


def serve(dm, host="127.0.0.1", port=8765, default_seed=None, open_browser=True, allow_pick=False):
    httpd = ThreadingHTTPServer((host, port), make_handler(dm, default_seed, allow_pick))
    url = f"http://{host}:{port}/"
    print(f"sonder — DM backend: {dm.name} ({getattr(dm, 'model', '')})\nserving {url}  (Ctrl+C to stop)")
    if open_browser:
        try:
            import webbrowser
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
