"""Route the walking loop along real streets instead of straight lines.

The drawn route used to be crow-flies stop-to-stop, which cut through blocks and
backyards and so never actually told a reader where to walk. This builds a
pedestrian graph from the raw OSM ways in osm.json, snaps each stop to the
nearest walkable edge, and runs Dijkstra between consecutive stops around the
closed loop.

Reads osm.json (raw tags) rather than geom.json on purpose: geom.py tiers roads
for drawing and throws away the highway tag, so it can't tell a motorway from a
primary, and it drops footways entirely -- both of which matter for walking.

Output: walk.json, one polyline of [lat, lon] per leg, leg i running from stop i
to stop i+1 (the last leg closes the loop back to stop 0).
"""
import json, io, os, math, heapq

HERE = os.path.dirname(os.path.abspath(__file__))

# Walkable ways. Motorways and trunks are excluded -- I-44 crosses this bbox
# (mapped as "Officer Michael Barwick Memorial Highway") and is not somewhere to
# route a reader.
#
# Footways matter and are kept: I-44 severs Marconi Ave, and the only pedestrian
# link across it is a mapped footbridge. Drop footways and the router detours
# ~700 m around an interstate a walker can simply cross.
#
# Alleys (highway=service) are excluded for legibility: The Hill has a full alley
# grid, and routing through it would be shorter but would read as nonsense.
WALK = set("""residential unclassified living_street pedestrian tertiary tertiary_link
secondary secondary_link primary primary_link road footway path steps""".split())

# Keeping footways reintroduces the opposite problem: where OSM maps a street's
# two sides as separate sidewalk ways, the router will only cross between them at
# a mapped crossing, so reaching the house directly opposite became a 150 m
# detour. CROSS adds a connector between any two nodes closer together than this,
# which lets a walker cross a street anywhere -- as they actually do at a yard
# sale. Sized to span a residential street (sidewalk to sidewalk is ~20 m here)
# while staying well under the ~60 m between parallel streets, so it never fuses
# two different blocks. An interstate is far wider than this, so it stays severed.
CROSS = 22.0

LAT0 = 38.615
MLAT = 111320.0
MLON = 111320.0 * math.cos(math.radians(LAT0))


def m(a, b):
    """Straight-line metres between two (lat, lon) points."""
    dy = (a[0] - b[0]) * MLAT
    dx = (a[1] - b[1]) * MLON
    return math.hypot(dx, dy)


def load_edges():
    d = json.load(io.open(os.path.join(HERE, 'osm.json'), encoding='utf-8'))
    edges = []
    for el in d['elements']:
        t = el.get('tags', {})
        if t.get('highway') not in WALK:
            continue
        g = el.get('geometry') or []
        pts = [(round(p['lat'], 5), round(p['lon'], 5)) for p in g if p]
        # collapse repeated nodes, which would otherwise make zero-length edges
        pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
        for i in range(len(pts) - 1):
            edges.append((pts[i], pts[i + 1]))
    return edges


def project(p, a, b):
    """Nearest point to p on segment a-b, plus the distance to it, in metres."""
    ay, ax = a[0] * MLAT, a[1] * MLON
    by, bx = b[0] * MLAT, b[1] * MLON
    py, px = p[0] * MLAT, p[1] * MLON
    vy, vx = by - ay, bx - ax
    L2 = vy * vy + vx * vx
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((py - ay) * vy + (px - ax) * vx) / L2))
    qy, qx = ay + t * vy, ax + t * vx
    q = (round(qy / MLAT, 6), round(qx / MLON, 6))
    return q, math.hypot(py - qy, px - qx), t


SHORT = 30.0   # below this, two houses are neighbours: walk straight over, don't route


def build_graph(stops):
    """Pedestrian graph plus one snap point per stop, ready for Dijkstra."""
    edges = load_edges()

    # Snap every stop to the nearest walkable edge FIRST, so the edges those snap
    # points land on can be split before the graph is built. Splitting after the
    # fact would leave the snap point stranded off the network.
    snaps = []
    for s in stops:
        p = (s['lat'], s['lon'])
        best = None
        for ei, (a, b) in enumerate(edges):
            q, dist, t = project(p, a, b)
            if best is None or dist < best[1]:
                best = (q, dist, ei, t)
        snaps.append(best)

    splits = {}
    for i, (q, dist, ei, t) in enumerate(snaps):
        splits.setdefault(ei, []).append((t, q))

    adj = {}

    def link(u, v):
        if u == v:
            return
        w = m(u, v)
        adj.setdefault(u, []).append((v, w))
        adj.setdefault(v, []).append((u, w))

    for ei, (a, b) in enumerate(edges):
        if ei in splits:
            # an edge can carry more than one snap point -- next-door neighbours
            # land on the same stretch of street
            chain = [(0.0, a)] + sorted(splits[ei]) + [(1.0, b)]
            for i in range(len(chain) - 1):
                link(chain[i][1], chain[i + 1][1])
        else:
            link(a, b)

    # Street-crossing connectors (see CROSS). Bucketed into a CROSS-sized grid so
    # only neighbouring cells are compared -- the pairwise scan over every node
    # would be minutes of work for the same answer.
    cell = {}
    for nd in adj:
        key = (int(nd[0] * MLAT // CROSS), int(nd[1] * MLON // CROSS))
        cell.setdefault(key, []).append(nd)
    crossings = 0
    for (cy, cx), nodes in cell.items():
        cand = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                cand.extend(cell.get((cy + dy, cx + dx), ()))
        for u in nodes:
            near = set(v for v, _ in adj[u])
            for v in cand:
                if v <= u or v in near or m(u, v) > CROSS:
                    continue
                link(u, v)
                crossings += 1
    return adj, snaps, crossings


def dijkstra(adj, src, dst=None):
    """Distances from src. Stops early at dst when one is given.
    Returns (dist, prev)."""
    dist = {src: 0.0}
    prev = {}
    pq = [(0.0, src)]
    seen = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in seen:
            continue
        seen.add(u)
        if u == dst:
            break
        for v, w in adj.get(u, ()):
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev


def path_between(adj, a, b):
    if a == b:
        return [a]
    dist, prev = dijkstra(adj, a, b)
    if b not in dist:
        return None
    path, u = [b], b
    while u != a:
        u = prev[u]
        path.append(u)
    path.reverse()
    return path


def street_matrix(stops, adj=None, snaps=None):
    """All-pairs walking distance between stops, in metres, along real streets.

    This is what the route solver should be minimising: route3.py/route_final.py
    have always used straight-line distance, which on a street grid systematically
    misjudges which stop is really "next" -- two houses back to back across a block
    are 40 m apart and a 300 m walk.

    One Dijkstra per stop over the whole graph, then read off the other stops'
    snap points. Falls back to straight-line for any pair the graph can't connect,
    so the matrix is always complete.
    """
    if adj is None:
        adj, snaps, _ = build_graph(stops)
    n = len(stops)
    pts = [(s['lat'], s['lon']) for s in stops]
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        dist, _ = dijkstra(adj, snaps[i][0])
        for j in range(n):
            if j == i:
                continue
            straight = m(pts[i], pts[j])
            if straight < SHORT:
                D[i][j] = straight
                continue
            d = dist.get(snaps[j][0])
            D[i][j] = straight if d is None else d
    # Dijkstra is symmetric here, but snapping is not exactly -- average the two
    # directions so the solver can't exploit a difference that isn't real.
    for i in range(n):
        for j in range(i + 1, n):
            avg = (D[i][j] + D[j][i]) / 2
            D[i][j] = D[j][i] = avg
    return D


def legs_for(stops, adj, snaps):
    """One street-following polyline per leg, in stops order, closing the loop."""
    legs, total, failed = [], 0.0, 0
    n = len(stops)
    for i in range(n):
        a, b = stops[i], stops[(i + 1) % n]
        pa, pb = snaps[i][0], snaps[(i + 1) % n][0]
        if m((a['lat'], a['lon']), (b['lat'], b['lon'])) < SHORT:
            # Next-door neighbours. Routing them out to the street and back draws
            # a pointless hairpin over a few metres -- just join the two houses.
            legs.append([[round(a['lat'], 5), round(a['lon'], 5)],
                         [round(b['lat'], 5), round(b['lon'], 5)]])
            total += m((a['lat'], a['lon']), (b['lat'], b['lon']))
            continue
        path = path_between(adj, pa, pb)
        if path is None:
            # Disconnected graph -- fall back to the straight line for this leg
            # rather than dropping it, so the loop always closes.
            failed += 1
            legs.append([[a['lat'], a['lon']], [b['lat'], b['lon']]])
            total += m((a['lat'], a['lon']), (b['lat'], b['lon']))
            continue
        pts = [(a['lat'], a['lon'])] + path + [(b['lat'], b['lon'])]
        pts = [p for j, p in enumerate(pts) if j == 0 or p != pts[j - 1]]
        for j in range(len(pts) - 1):
            total += m(pts[j], pts[j + 1])
        legs.append([[round(p[0], 5), round(p[1], 5)] for p in pts])
    return legs, total, failed


def main():
    stops = json.load(io.open(os.path.join(HERE, 'stops.json'), encoding='utf-8'))
    adj, snaps, crossings = build_graph(stops)
    legs, total, failed = legs_for(stops, adj, snaps)

    out = json.dumps(legs, separators=(',', ':'))
    io.open(os.path.join(HERE, 'walk.json'), 'w', encoding='utf-8').write(out)

    # routemeta.json's loop_mi is the straight-line distance. Even now that the
    # solver optimises street distance, the two differ, and walk_mi is the one
    # the page quotes to readers.
    mp = os.path.join(HERE, 'routemeta.json')
    meta = json.load(io.open(mp, encoding='utf-8'))
    meta['walk_mi'] = round(total / 1609.344, 2)
    io.open(mp, 'w', encoding='utf-8').write(json.dumps(meta) + '\n')

    snapmax = max(s[1] for s in snaps)
    pts = sum(len(l) for l in legs)
    print('graph: %d nodes, %d crossing connectors' % (len(adj), crossings))
    print('walk.json  %d legs, %d points, %.0f KB' % (len(legs), pts, len(out) / 1024))
    print('street-following loop: %.2f mi   (worst snap %.0f m from the house)'
          % (total / 1609.344, snapmax))
    if failed:
        print('!! %d leg(s) had no street path and fell back to a straight line' % failed)


if __name__ == '__main__':
    main()
