import openpyxl, re, json, csv

wb = openpyxl.load_workbook('../source/Yard Sale Listing FINAL.xlsx', data_only=True)
ws = wb['Form Responses 1']
rows = list(ws.iter_rows(values_only=True))[1:]

listings = []
for r in rows:
    if not r or not r[0]:
        continue
    raw = str(r[0]).strip()
    items = (str(r[1]).strip() if r[1] else "")
    pay = (str(r[2]).strip() if r[2] else "")
    # pull "(Business Name)" out of the address
    venue = ""
    m = re.search(r'\(([^)]+)\)', raw)
    if m:
        venue = m.group(1).strip()
        raw = re.sub(r'\s*\([^)]*\)\s*', ' ', raw).strip()
    # split off apt/unit so the geocoder gets a clean street address
    unit = ""
    m2 = re.search(r'\s+(Apt\.?\s*\S+|Unit\s*\S+|#\S+)$', raw, re.I)
    if m2:
        unit = m2.group(1).strip()
        raw = raw[:m2.start()].strip()
    listings.append({"street": raw, "venue": venue, "unit": unit,
                     "items": re.sub(r'\s*/\s*/\s*', ' ', items).strip(),
                     "pay": pay})

print("listings:", len(listings))
print("unique streets:", len({l['street'] for l in listings}))
with open('clean.json','w') as f:
    json.dump(listings, f, indent=1)

# batch CSV for the Census geocoder: id, street, city, state, zip
with open('batch.csv','w',newline='') as f:
    w = csv.writer(f)
    for i,l in enumerate(listings):
        w.writerow([i, l['street'], 'Saint Louis', 'MO', ''])
print(open('batch.csv').read()[:400])
