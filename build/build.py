import json, csv, re

listings = json.load(open('clean.json'))

# --- attach coordinates ---
geo = {}
for row in csv.reader(open('geo_raw.csv')):
    if len(row) >= 6 and row[2] == 'Match':
        lon, lat = row[5].split(',')
        geo[int(row[0])] = (float(lat), float(lon), row[3])

MANUAL = {  # surveyed on the ground by the organizer — these override the geocoder
    '2107 Robert Ruggeri Pl': (38.615042868571145, -90.26947552349579, 'Exact'),
    '2108 Robert Ruggeri Pl': (38.61494512008195,  -90.26910398074021, 'Exact'),
    '2227 Stephen Ct':        (38.615148498795286, -90.28231801483308, 'Exact'),
}

for i, l in enumerate(listings):
    if l['street'] in MANUAL:
        lat, lon, q = MANUAL[l['street']]
    elif i in geo:
        lat, lon, q = geo[i]
    else:
        lat = lon = None; q = 'None'
    l['lat'], l['lon'], l['q'] = lat, lon, q

# --- category tags from the items text ---
TAGS = [
 ("Kids & baby",     r"\bkid|\bbaby|toys?\b|children"),
 ("Clothing",        r"cloth|shoes|apparel|shirts?\b|belts|dress|jacket|pants|activewear|accessor"),
 ("Furniture",       r"furniture|\bbar\b|closet|cabinet|table|desk"),
 ("Household",       r"household|housewares|kitchen|home goods|home decor|appliance|decor|holiday|christmas|seasonal|glass|dishes"),
 ("Vintage & antiques", r"vintage|antique|collectib|retro|mid.century|knick|memorabilia|jewelry|junque"),
 ("Tools & hardware",r"\btools?\b|hardware|ladder|lawn equip|car parts|sprayer"),
 ("Books & media",   r"\bbooks?\b|records|albums|\bdvd|\bcds?\b|magazin|media|rpm"),
 ("Art & crafts",    r"\bart\b|artwork|craft|fabric|soaps|candles|bowls|leatherwork|screen print|ornament"),
 ("Sports & outdoors", r"exercise|bike|bicycle|golf|sporting|outdoor|recreation|pool table|weights|martial|dart|chess|camping|sleeping bag"),
 ("Garden & plants", r"garden|plants?\b|plant starter"),
 ("Electronics",     r"computer|electronic|vacuum|dehumidif|air purif|steam mop"),
 ("Pet supplies",    r"\bpet\b|\bcat\b|\bdog\b|litter|scratcher"),
]
for l in listings:
    txt = l['items'].lower()
    l['tags'] = [name for name, pat in TAGS if re.search(pat, txt)]
    if not l['tags']:
        l['tags'] = ["Misc"]
    l['cashOnly'] = bool(re.search(r'cash only|^cash\s*$', l['pay'].strip(), re.I))
    l['beyond'] = not l['cashOnly']   # anything not marked cash-only takes another form

# --- group listings that share an address, then number by street ---
def key(l):
    m = re.match(r'(\d+)\s+(.*)', l['street'])
    return (m.group(2).lower(), int(m.group(1))) if m else (l['street'].lower(), 0)

groups = {}
for l in sorted(listings, key=key):
    groups.setdefault(l['street'], []).append(l)

stops = []
for n, (addr, ls) in enumerate(groups.items(), 1):
    stops.append({
        "n": n, "addr": addr,
        "venue": next((x['venue'] for x in ls if x['venue']), ""),
        "lat": ls[0]['lat'], "lon": ls[0]['lon'], "q": ls[0]['q'],
        "street": key(ls[0])[0].title(),
        "sellers": [{"items": x['items'], "pay": x['pay'], "tags": x['tags'],
                     "cashOnly": x['cashOnly']} for x in ls],
        "tags": sorted({t for x in ls for t in x['tags']}),
        "cashOnly": all(x['cashOnly'] for x in ls),
        "beyond": any(x['beyond'] for x in ls),
    })

lats = [s['lat'] for s in stops if s['lat']]
lons = [s['lon'] for s in stops if s['lon']]
print("stops: %d   listings: %d   missing coords: %d"
      % (len(stops), len(listings), sum(1 for s in stops if not s['lat'])))
print("center: %.6f, %.6f" % (sum(lats)/len(lats), sum(lons)/len(lons)))
print("bbox: lat %.5f..%.5f  lon %.5f..%.5f" % (min(lats), max(lats), min(lons), max(lons)))
print("approx/flagged:", [(s['n'], s['addr'], s['q']) for s in stops if s['q'] != 'Exact'])
from collections import Counter
print("tags:", Counter(t for s in stops for t in s['tags']).most_common())
print("streets:", len({s['street'] for s in stops}))
json.dump(stops, open('stops.json','w'), indent=1)
