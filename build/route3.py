"""Route with a tunable penalty for hopping between streets.

PEN=0 is the pure shortest loop (efficient, but bounces between streets).
Large PEN forces one street at a time (legible, but longer). The knee in
between is a route a person can actually follow without losing much distance.
"""
import json, math, sys

S = json.load(open('stops.json'))
CL = math.cos(math.radians(38.615))
def xy(s): return (s['lon']*111320*CL, s['lat']*111320)
P = [xy(s) for s in S]; n = len(P)
D = [[math.hypot(P[i][0]-P[j][0], P[i][1]-P[j][1]) for j in range(n)] for i in range(n)]
ST = [s['street'] for s in S]

def dist(o): return sum(D[o[i]][o[(i+1) % len(o)]] for i in range(len(o)))
def runs(o): return sum(1 for i in range(len(o)) if ST[o[i]] != ST[o[i-1]])

def make_cost(pen):
    def cost(o): return dist(o) + pen*runs(o)
    return cost

def improve(o, cost):
    imp = True
    while imp:
        imp = False
        base = cost(o)
        for i in range(len(o)-1):                       # 2-opt
            for j in range(i+2, len(o)):
                if i == 0 and j == len(o)-1: continue
                cand = o[:i+1] + o[i+1:j+1][::-1] + o[j+1:]
                v = cost(cand)
                if v < base - 1e-9:
                    o, base, imp = cand, v, True
        for L in (1, 2, 3):                             # or-opt
            i = 0
            while i + L <= len(o):
                seg = o[i:i+L]; rest = o[:i] + o[i+L:]
                if len(rest) >= 2:
                    best = None
                    for k in range(len(rest)+1):
                        for sg in (seg, seg[::-1]):
                            cand = rest[:k] + sg + rest[k:]
                            v = cost(cand)
                            if v < base - 1e-9 and (best is None or v < best[0]):
                                best = (v, cand)
                    if best: o, base, imp = best[1], best[0], True
                i += 1
    return o

iso = {}
for i in range(n):
    ds = sorted(D[i][j] for j in range(n) if j != i); iso[i] = sum(ds[:3])/3
OUT = {i for i in range(n) if iso[i] > 400}

def solve(pen, starts=14):
    cost = make_cost(pen); best = None
    for st in range(0, n, max(1, n//starts)):
        unv = set(range(n)); o = [st]; unv.discard(st)
        while unv:
            nx = min(unv, key=lambda j: D[o[-1]][j] + (0 if ST[j] == ST[o[-1]] else pen))
            o.append(nx); unv.discard(nx)
        o = improve(o, cost); v = cost(o)
        if best is None or v < best[0]: best = (v, o[:])
    return best[1]

def rotate(o):
    """start and end in the dense core, on a street boundary"""
    cands = []
    for r in range(n):
        rot = o[r:] + o[:r]
        f, l = rot[0], rot[-1]
        if f in OUT or l in OUT: continue
        cands.append((0 if ST[f] != ST[l] else 1, max(iso[f], iso[l]), r, rot))
    cands.sort(key=lambda t: (t[0], t[1]))
    return cands[0][3]

results = {}
for pen in (0, 50, 100, 175, 300, 600, 1500):
    o = rotate(solve(pen))
    results[pen] = o
    print("PEN %-5d  %.2f mi  %2d street runs   start %-22s end %s"
          % (pen, dist(o)/1609.34, runs(o), S[o[0]]['addr'], S[o[-1]]['addr']))

pick = int(sys.argv[1]) if len(sys.argv) > 1 else None
if pick is not None:
    o = results[pick]
    seq = [S[i] for i in o]
    for i, s in enumerate(seq, 1): s['n'] = i
    json.dump(seq, open('stops.json', 'w'), indent=1)
    json.dump({"loop_mi": round(dist(o)/1609.34, 2), "runs": runs(o),
               "start": seq[0]['addr'], "end": seq[-1]['addr'],
               "outliers": [S[i]['addr'] for i in OUT]},
              open('routemeta.json', 'w'))
    print("\nWROTE PEN=%d\n" % pick)
    last = None
    for idx, s in enumerate(seq):
        if s['street'] != last:
            last = s['street']; print("  --- %s" % last)
        print("   %2d  %-30s%s" % (s['n'], s['addr'],
              "   <-- outlier" if o[idx] in OUT else ""))
