"""Inline the data into template.html and write dist/map.html (+ a local preview).

template.html carries three placeholders -- __GEOM__, __STOPS__, __META__ -- which
are replaced with the contents of geom.json, stops.json and routemeta.json. The
page ships as one self-contained file because the Artifact CSP blocks every
external fetch (see HANDOFF.md).
"""
import json, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, '..', 'dist')

def read(name):
    return io.open(os.path.join(HERE, name), encoding='utf-8').read()

def compact(name):
    return json.dumps(json.load(io.open(os.path.join(HERE, name), encoding='utf-8')),
                      separators=(',', ':'))

tpl = read('template.html')
out = (tpl.replace('__GEOM__',  read('geom.json').strip())
          .replace('__STOPS__', compact('stops.json'))
          .replace('__META__',  compact('routemeta.json')))

for ph in ('__GEOM__', '__STOPS__', '__META__'):
    if ph in out:
        raise SystemExit('ERROR: placeholder %s was not substituted' % ph)

os.makedirs(DIST, exist_ok=True)
io.open(os.path.join(DIST, 'map.html'), 'w', encoding='utf-8').write(out)

# The artifact platform wraps the file in its own <!doctype>/<head>/<body>.
# This mirrors that wrapper so the page can be opened locally and look right.
WRAP_HEAD = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{color-scheme:light dark;padding-top:env(safe-area-inset-top,0px);
padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""
io.open(os.path.join(DIST, 'preview.html'), 'w', encoding='utf-8').write(
    WRAP_HEAD + out + '\n</body></html>\n')

stops = json.load(io.open(os.path.join(HERE, 'stops.json'), encoding='utf-8'))
meta = json.load(io.open(os.path.join(HERE, 'routemeta.json'), encoding='utf-8'))
print('dist/map.html      %6.0f KB' % (len(out) / 1024))
print('dist/preview.html  (open this one in a browser)')
print('%d stops, %.2f mi loop, starts %s' % (len(stops), meta['loop_mi'], meta['start']))
