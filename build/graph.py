"""Emit the pedestrian street graph for the page to route on at runtime.

walk.py routes stop-to-stop at build time, which is enough to draw the loop. But
the reader wants the walk from *where they are standing* to a sale, and their
position isn't known until they open the page -- so the graph has to ship.

Compactness matters: this is inlined into a single self-contained HTML file that
has to load on a phone on a bad connection.

  - Coordinates are integers at 1e-5 degrees (~1 m), delta-coded against the
    previous node in a spatially sorted order, so most deltas are tiny.
  - Edge endpoints are node indices, delta-coded on the first endpoint.
  - The ~26k street-crossing connectors are NOT shipped. They are derived from
    the node positions alone, so the page rebuilds them in one grid pass at load
    (see CROSS in walk.py and rebuildCrossings() in the template). Shipping them
    would nearly quadruple the edge count for information the page already has.
"""
import json, io, os
import walk

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    stops = json.load(io.open(os.path.join(HERE, 'stops.json'), encoding='utf-8'))
    adj, snaps, _ = walk.build_graph(stops, add_crossings=False)

    # Spatial sort so consecutive nodes are near each other and the deltas stay
    # small. Plain lexicographic on the rounded coords is enough here.
    nodes = sorted(adj)
    idx = {n: i for i, n in enumerate(nodes)}

    flat, plat, plon = [], 0, 0
    for la, lo in nodes:
        ila, ilo = int(round(la * 1e5)), int(round(lo * 1e5))
        flat.append(ila - plat)
        flat.append(ilo - plon)
        plat, plon = ila, ilo

    # Undirected edges, each once, sorted so the first endpoint delta-codes well.
    seen = set()
    pairs = []
    for u in adj:
        for v, _w in adj[u]:
            a, b = idx[u], idx[v]
            if a > b:
                a, b = b, a
            if (a, b) in seen:
                continue
            seen.add((a, b))
            pairs.append((a, b))
    pairs.sort()

    edges, pa = [], 0
    for a, b in pairs:
        edges.append(a - pa)
        edges.append(b - a)
        pa = a

    # The stops' snap points are graph nodes already (build_graph splits the edge
    # they landed on), so the page only needs their indices.
    snapidx = [idx[s[0]] for s in snaps]

    out = {'n': flat, 'e': edges, 's': snapidx}
    js = json.dumps(out, separators=(',', ':'))
    io.open(os.path.join(HERE, 'graph.json'), 'w', encoding='utf-8').write(js)
    print('graph.json  %d nodes, %d edges, %d snaps -> %.0f KB'
          % (len(nodes), len(pairs), len(snapidx), len(js) / 1024))


if __name__ == '__main__':
    main()
