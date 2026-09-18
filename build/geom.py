import json
d = json.load(open('osm.json'))

# Road tiers: 3 = highway/arterial, 2 = collector, 1 = residential street
TIER = {'motorway':3,'motorway_link':3,'trunk':3,'primary':3,'primary_link':3,
        'secondary':2,'secondary_link':2,'tertiary':2,'tertiary_link':2,
        'residential':1,'unclassified':1,'living_street':1,'pedestrian':1}

roads, green, rail = [], [], []
for el in d['elements']:
    t = el.get('tags', {})
    g = el.get('geometry') or []
    pts = [(p['lat'], p['lon']) for p in g if p]
    if len(pts) < 2:
        continue
    # 6 decimals ~ 0.1m; 5 is plenty at neighborhood scale
    q = [[round(la, 5), round(lo, 5)] for la, lo in pts]
    if 'highway' in t and t['highway'] in TIER:
        roads.append({"t": TIER[t['highway']], "n": t.get('name', ""), "p": q})
    elif t.get('railway') == 'rail':
        rail.append({"p": q})
    elif 'leisure' in t or 'landuse' in t:
        kind = t.get('leisure') or t.get('landuse')
        if kind in ('park','pitch','playground','recreation_ground','garden','grass'):
            if len(q) >= 4:
                green.append({"k": 'park' if kind in ('park','recreation_ground','playground') else 'grass',
                              "n": t.get('name',""), "p": q})

# collapse duplicate-name road segments for cleaner labeling
out = {"roads": roads, "green": green, "rail": rail}
s = json.dumps(out, separators=(',', ':'))
open('geom.json','w').write(s)
print("roads:%d green:%d rail:%d  -> %.0f KB" % (len(roads), len(green), len(rail), len(s)/1024))
named = sorted({r['n'] for r in roads if r['n']})
print("named roads:", len(named))
print([n for n in named if any(k in n for k in ('Marconi','Shaw','Daggett','Bischoff','Macklind','Wilson','Sublette','Kingshighway','Columbia','Botanical','Elizabeth','Pattison','Dugan','Lilly','Edwards','Magnolia','59th','Ruggeri','Stephen','Hampton','44'))])
print("parks:", sorted({g['n'] for g in green if g['n']}))
