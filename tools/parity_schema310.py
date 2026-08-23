#!/usr/bin/env python3
"""Schema 3.10 parity check (Run 24). Run from the repo root:

    python tools/parity_schema310.py

Asserts that blackboard/sim/harness.py produces BIT-IDENTICAL statistics under
rules-v3.9.1-C.json (ratified) and rules-v3.10-C.json (the 3.10 control, every new
block default-off) across 6 seeds x 5 bot policies x up to 20 sleeps. Pass 'git'
as an argument to additionally diff the current harness against `git show
HEAD~1:blackboard/sim/harness.py` under 3.9.1 (old-harness parity).
"""
import json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM = os.path.join(ROOT, 'blackboard', 'sim')
CODE = r'''
import json, harness as H, bots as B
out = []
for seed in range(6):
    for name, bot in [('nothing', B.bot_do_nothing), ('walk', B.bot_walk_one), ('throughput', B.bot_throughput)]:
        r = H.run(bot, seed, max_sleeps=20)
        for k in ('temple_pos','win_armed_sleep','armed_to_terminal_sleeps','lost_while_armed','pilgrim_tiles','front_travel_sleeps','well_exposure'): r.pop(k, None)
        out.append((name, seed, json.dumps(r, sort_keys=True, default=list)))
    for name, fn in [('campaign', B.run_campaign_v3), ('selfburn', B.run_selfburn)]:
        out.append((name, seed, json.dumps(fn(seed), sort_keys=True, default=list)))
print(json.dumps(out))
'''
def run(harness_src, rules):
    d = tempfile.mkdtemp(prefix='parity310_')
    open(os.path.join(d, 'harness.py'), 'w', encoding='utf-8').write(harness_src)
    open(os.path.join(d, 'bots.py'), 'w', encoding='utf-8').write(open(os.path.join(SIM, 'bots.py'), encoding='utf-8').read())
    env = dict(os.environ, RULES=os.path.abspath(rules), PYTHONPATH=d)
    p = subprocess.run([sys.executable, '-c', CODE], env=env, cwd=d, capture_output=True, text=True)
    if p.returncode:
        print(p.stderr[-2000:]); sys.exit(1)
    return json.loads(p.stdout)
new = open(os.path.join(SIM, 'harness.py'), encoding='utf-8').read()
r391 = os.path.join(ROOT, 'blackboard', 'rules', 'rules-v3.9.1-C.json')
r310 = os.path.join(ROOT, 'blackboard', 'rules', 'rules-v3.10-C.json')
a = run(new, r391); b = run(new, r310)
ok = a == b
print(f"new harness: 3.9.1 == 3.10-control over {len(a)} arms: {ok}")
if 'git' in sys.argv:
    old = subprocess.run(['git', 'show', 'HEAD~1:blackboard/sim/harness.py'], cwd=ROOT, capture_output=True, text=True).stdout
    c = run(old, r391)
    print(f"old harness/3.9.1 == new harness/3.9.1: {c == a}")
    ok = ok and c == a
if not ok:
    for x, y in zip(a, b):
        if x != y: print('FIRST DIFF', x[:2]); break
sys.exit(0 if ok else 1)
