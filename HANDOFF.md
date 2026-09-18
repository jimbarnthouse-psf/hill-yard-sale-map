# The Hill Yard Sale Map — handoff

**Live artifact:** https://claude.ai/artifact/XTPHamraY1feVFwMaanuQp (Version 9)
**Live on GitHub Pages:** https://jimbarnthouse-psf.github.io/hill-yard-sale-map/
**Repo:** https://github.com/jimbarnthouse-psf/hill-yard-sale-map (public)
**Event:** Saturday, September 26, 2026, 8am–noon. The Hill, St. Louis 63110.
**Handed off:** September 17, 2026 — 9 days out.
**Owner:** Jim Barnthouse (jim.barnthouse@mac.com)

An interactive map of 59 neighborhood yard sales, numbered as a walking loop.
Built and published two ways:

1. **Claude Artifact** — still **private**; Jim shares it from the artifact
   page's own share menu when he's ready.
2. **GitHub Pages** — public, at the URL above, so the link doesn't show as
   claude.ai. `index.html` at the repo root is a copy of `dist/map.html`;
   `./build.sh` refreshes it automatically on every rebuild (see below).
   `git push` is what ships an update here — GitHub Pages rebuilds itself
   from `main` a minute or so after each push, no separate deploy step.

---

## What this session was asked to do next

Jim asked to hand off "to polish," and picked two priorities:

1. **Visual and design refinement** — typography, spacing, the map's cartography,
   pin collision in dense blocks, the look of the route line and landmark labels.
2. **Real-world testing and edge cases** — test on an actual phone, the sticky map
   while walking, the Directions hand-off, sunlight legibility, slow connections.

He explicitly did *not* pick the printable flyer or the Google My Maps export this
round, though both are still open (see [Open items](#open-items)).

---

## Read this before touching the map

**The map is hand-rendered SVG on purpose. Do not "fix" it by adding Leaflet,
Mapbox or Google Maps tiles.**

The Artifact CSP blocks every external subresource except scripts from a short CDN
allowlist and stylesheets from Google Fonts. That means:

- Raster map tiles from any tile server **will not load** — they're images from a
  non-allowlisted host. Silently. No console error.
- Leaflet's stylesheet and its default marker PNGs are also blocked.
- No `fetch`/XHR/WebSocket to anything.

So the street grid is drawn from real OpenStreetMap geometry that was fetched at
*build* time and inlined into the page (`geom.json`, ~172 KB, 420 roads + 216 green
polygons + rail). The whole page is one self-contained 241 KB file with zero runtime
network dependencies beyond the Google Fonts link. This is also why it loads
instantly on a phone on a bad connection — worth preserving.

Google Maps still does the one thing it's good for here: every stop has a
**Directions →** link that hands off to `google.com/maps/search/?api=1&query=lat,lon`
for turn-by-turn. Navigation, not a fetch, so it works.

---

## How to rebuild

From the project root:

```bash
./build.sh            # page only — after editing build/template.html (the common case)
./build.sh --route    # re-solve the walking loop, then rebuild
./build.sh --data     # re-read the spreadsheet (prints the manual geocode step)
```

Preview locally — the artifact platform supplies its own `<!doctype>`/`<head>`/`<body>`,
so `dist/preview.html` mirrors that wrapper. **Use a server, not `file://`**:

```bash
python3 -m http.server 8731 --directory dist
```

then open `http://localhost:8731/preview.html`.

Verified on handoff: `./build.sh` reproduces the published `dist/map.html`
**byte-identically**, and the route solve is deterministic (`--route` reproduces the
same `stops.json` and `routemeta.json`).

Requirements: Python 3 only, no packages, for everything except `--data`, which needs
`openpyxl` to read the spreadsheet (`pip3 install openpyxl` — it was present on Jim's
machine at handoff). The route solver is pure stdlib and takes ~30s for one penalty
value, ~2.5 min for the full sweep in `route3.py`.

### ⚠️ The one pipeline trap

`build.py` writes `stops.json` in **alphabetical** order. `route_final.py` then
rewrites it in **route** order. If you run `build.py` alone and rebuild, the shipped
numbering silently reverts to alphabetical. `build.sh --route` runs both in order —
prefer it over calling the scripts by hand.

### Publishing an update

The artifact is owned by Jim's account. From a new conversation you must pass the
URL, and **read it first** or the publish is refused:

1. `Artifact` with `action: "read"` and `url: "https://claude.ai/artifact/XTPHamraY1feVFwMaanuQp"`
2. `Artifact` publish with `file_path: <.../dist/map.html>` and the same `url`

Publishing **without** `url` creates a second, separate artifact instead of updating
this one. Also: **omit `favicon` and `icon` on republish** (it keeps 🏷️🗺️ / "map") and
keep the `<title>` as "The Hill Yard Sale Map" — viewers recognize the artifact by these.

To ship the same update to GitHub Pages, `./build.sh` already refreshed
`index.html` — just commit and push:

```bash
git add -A && git commit -m "describe the change" && git push
```

GitHub Pages rebuilds from `main` automatically a minute or so after the push;
no separate deploy step. `gh` is installed at `~/.local/bin/gh` and authenticated
as `jimbarnthouse-psf` (device-flow login, done 2026-09-18) — a fresh session may
need `export PATH="$HOME/.local/bin:$PATH"` if it isn't already on `PATH`.

---

## Files

```
HANDOFF.md                     this file
build.sh                       the only entry point you should need
source/
  Yard Sale Listing FINAL.xlsx Jim's Google Form responses (60 rows, the original source)
build/
  template.html                THE PAGE — all HTML/CSS/JS. Edit this.
  inject.py                    template + data -> dist/
  parse.py                     xlsx -> clean.json + batch.csv
  build.py                     listings + geocodes -> stops.json (+ tags, payment)
  route3.py                    route solver, sweeps street-switch penalties
  route_final.py               single-penalty run; PEN=100 produced the shipped order
  geom.py                      osm.json -> geom.json (compress + tier the roads)
  q.txt                        the Overpass query, to refetch geometry
  clean.json                   60 parsed listings
  batch.csv                    geocoder input
  geo_raw.csv                  Census batch geocoder output
  osm.json                     raw Overpass response (1.8 MB — avoids refetching)
  geom.json                    compressed street geometry, inlined into the page
  stops.json                   THE DATA — 59 stops, in route order
  routemeta.json               loop distance, start, end, outliers
dist/
  map.html                     what gets published
  preview.html                 same page, locally openable
```

Everything in `build/` uses bare relative filenames, so **run the scripts from
inside `build/`** (or just use `build.sh`, which cds for you).

---

## Data provenance and its caveats

**60 spreadsheet rows → 59 map stops.** `5415 Wilson Ave` appears twice (two
different households). They're merged into one pin whose popup lists both, rather
than two pins stacked on one point. `s.sellers` is an array for exactly this reason —
don't assume length 1.

**Geocoding:** 57 of 59 matched exactly against the US Census batch geocoder
(`Public_AR_Current`). Three needed intervention, and Jim then **surveyed all three
by GPS on the ground**; those coordinates are hardcoded in the `MANUAL` dict in
`build.py` and override the geocoder. Every pin is now house-accurate and no pin
carries an "approximate" flag.

- `2107` / `2108 Robert Ruggeri Pl` — the Census has no address ranges for that street.
- `2227 Stephen Ct` — **possible data issue worth raising with Jim.** Neither the
  Census nor OpenStreetMap knows a "Stephen Ct"; both only have a **Stephen Ave** at
  that location. The pin is on the right block either way, but the signup may have a
  typo. Not yet resolved.

**Category tags** (`Household`, `Clothing`, … 13 of them) are regex-derived from the
free-text item descriptions in `build.py`. They're heuristics, not ground truth — a
house selling "cat trees" gets `Pet supplies` because the regex says so. Fine for
filtering, don't present them as authoritative.

**Payment is deliberately binary.** An earlier version had a "Takes cards or apps"
chip that only regex-matched literal "credit card"/"Apple Pay", counting 10 houses
and silently excluding everyone who takes Venmo/Zelle/PayPal/Cash App — the label
promised more than the code did. Jim caught it and specified the right model:
*anything not marked cash-only takes another form*. Now `cashOnly` (17) and
`beyond = not cashOnly` (42), summing to 59. **Keep this invariant.** Each popup still
shows the seller's verbatim payment string, because entries like "Cash, checks (if
buyer is known to seller)" and "Cash (preferred)… $3.00 processing fee applies to
cards" deserve reading in full.

---

## The route, and why it is what it is

A **closed loop** of about **5.23 miles**, 59 stops, default start `5235 Daggett Ave`,
default end `1935 Marconi Ave` — which is **256 ft from the start**, so you park once
and come back to your car.

Jim's constraint was: *don't start or end on any sale that's way off on its own.* Two
sales are genuine geographic outliers (mean distance to their 3 nearest neighbors):

- `4941 Magnolia Ave` — 563 m, nearest neighbor 506 m away. Half a mile south of everything.
- `1631 Sublette Ave` — 549 m, nearest 479 m.

Everything else has a neighbor within ~190 m. Solving as a **loop** satisfies the
constraint structurally: first and last stop are adjacent by definition, so if one is
central both are. The two outliers sit mid-route (`#17` and `#51`); Magnolia is an
unavoidable out-and-back spur (506 m down, 568 m back).

### The legibility/distance tradeoff — a deliberate choice, not an accident

`route3.py` optimizes `distance + PEN × (number of street runs)`. The frontier:

| PEN | miles | street runs | character |
|-----|-------|-------------|-----------|
| 0 | 4.98 | 36 | shortest, but crosses Bischoff 3 separate times |
| 50 | 4.97 | 33 | |
| **100** | **5.23** | **26** | **shipped** — the knee |
| 175 | 5.64 | 22 | |
| 600 | 6.74 | 18 | one street at a time, fully legible |

PEN=100 costs 5% over optimal to cut street-hopping by a third. Jim was told the
numbers and can switch: `python3 route_final.py <PEN>` then `./build.sh`. Distances
are straight-line, so real sidewalk walking is more like 5.5–6 mi.

---

## How the page is built

One file: `build/template.html`. No framework, no build step beyond string
substitution, no libraries at all. ES5-flavored JS in one IIFE.

**Design tokens.** Palette is on `:root` and redefined in *both* a
`@media (prefers-color-scheme: dark)` block guarded `:root:not([data-theme="light"])`
*and* a `:root[data-theme="dark"]` block, because artifact viewers have three theme
states (explicit light, explicit dark, and unstamped "system"). Both themes were
checked. If you add a color, add it to the bare `:root` first — a color defined only
inside a dark block renders one theme's text on the other's background.

Type: Archivo Black (display), Public Sans (body), DM Mono (numbers, addresses,
labels). Deliberately wght-only axes — Google Fonts' CSS2 API needs every axis
specified in order for multi-axis families, which is an easy silent-fallback bug.
Colors are drawn from the neighborhood: `--brick` is The Hill's red brick,
`--basil` its Italian green (also the landmark color), with warm-biased neutrals.

**Projection.** `px(lat, lon)` — equirectangular with an `x` scale of `cos(38.615°)`,
fitted to the stop bounding box plus 9% padding. Exact enough at neighborhood scale.
SVG units equal CSS pixels (the `viewBox` is set to the measured pixel size), so
there's one coordinate space for both the SVG and the HTML marker overlay.

**Pan/zoom.** A `translate/scale` on the SVG `<g id="world">` and on the HTML
`#pinlayer`, driven by pointer events (drag, wheel, 2-finger pinch). Roads use
`vector-effect="non-scaling-stroke"` so stroke widths stay constant in screen pixels.
Street labels counter-scale their `font-size` per zoom and hide below a length
threshold. `clamp()` keeps ≥42% of the drawing on screen.

**Pin sizing.** Pins counter-scale as `pinK/k` where `pinK` ramps 0.70→1.0 between
zoom 1 and 2.5. At the fit-all view, 59 constant-size pins collided badly; shrinking
them when zoomed out fixed it. **Dense-block collision is still the top open visual
issue** — see below.

### The numbering model — important if you touch stops or the list

A stop's identity is **`s.i`, its fixed index in the canonical loop**, which is
`stops.json` array order. The number *printed* on it is derived:

```js
num(s) = ((s.i - startAt + N) % N) + 1
```

`startAt` is which stop the reader chose as #1. Any house can be #1 — the route is a
closed loop, so re-entering it anywhere costs nothing and the drawn route line never
changes; only numbering and list order do. Selection, pins and cards are all keyed on
`s.i`, never on the displayed number. `startAt` persists per-viewer in
`localStorage['hill-start']` (wrapped in try/catch — it throws in private windows and
during thumbnail capture).

**Known consequence, left deliberately:** a reader who picks a start gets the
*preceding* loop stop as their finish, which can be one of the two outliers (starting
at `5004 Bischoff` ends at `4941 Magnolia`). Jim's no-outlier rule holds for the
shipped default; an override can land on one. He was told, and chose to leave reader
freedom in place. He also asked to be offered the option of making those two stops
refuse to be a start — **not implemented, his call.**

### Landmarks

Three orientation markers, green and visually distinct from the brick sale pins, with
a toggle. Coordinates are inline in `template.html` (`LANDMARKS`):

| Landmark | Coordinate source |
|---|---|
| St. Ambrose Catholic Church, 5130 Wilson Ave | the OSM **building**, not the Census street-interpolated point 72 m east |
| The Hill Neighborhood Center, 1935 Marconi Ave | same point as sale stop #59 |
| Berra Park, Macklind & Shaw | centroid of its boundary polygon in `geom.json` |

Labels flip to the opposite side of their dot when the marker drifts past 62% of map
width, so they don't slide under the map controls.

**Open question for Jim:** the Neighborhood Center is *also* sale stop #59 (1935
Marconi, "Italian items"), so it carries both a green landmark marker and a numbered
pin. He was told and left it; he may prefer it be only a sale pin.

---

## Bugs already found and fixed — don't reintroduce these

1. **Payment filter undercounted.** See the payment section above. The lesson: the
   chip label and the predicate have to agree.
2. **Landmark labels slid under the map's zoom buttons** on narrow screens. Fixed by
   flipping the label to the marker's other side past 62% width.
3. **The list overflowed onto the footer on phones.** `#listcol` had
   `min-height: 230px`, which flex can't shrink, so a 230px list spilled out of a
   357px `#split` and painted over `#foot`. Fixed by *changing the mobile model*
   rather than tuning heights: on ≤860px the page scrolls normally
   (`html,body{height:auto}`), the list takes its natural height, and `#mapcol` is
   `position: sticky` at the top so the map stays visible while the list scrolls past.
   The locked-viewport flex layout is desktop-only now. **If you touch the mobile
   layout, re-check this specific interaction.**
4. **Five rows of filter chips pushed the map ~200px down the phone screen.** They're
   now one horizontally-scrollable row under 860px.
5. A stray Cyrillic `А` in a `--mute` hex token (harmless, a duplicate declaration
   overrode it) and sloppy `clamp()`/scale-bar arithmetic — all cleaned up.

### Testing notes

`node --check` on the extracted `<script>` catches syntax errors cheaply:

```bash
node --check <(sed -n '/^<script>$/,/^<\/script>$/p' dist/map.html | sed '1d;$d')
```

The browser pane's synthetic `scroll` action does **not** fire a real `wheel` event,
so wheel-zoom can't be verified that way — it scrolls the page instead. Use the `+`/`−`
buttons, or drive handlers via `javascript_tool`. Wheel zoom itself is a standard
`wheel` listener and works for real users; don't "fix" it based on that false negative.

Useful invariant check after any numbering change:

```js
const nums=[...document.querySelectorAll('#pinlayer button.pin .n')].map(e=>+e.textContent).sort((a,b)=>a-b);
JSON.stringify(nums)===JSON.stringify(Array.from({length:59},(_,i)=>i+1))  // must be true
```

---

## Where to start on the two chosen priorities

### Visual and design refinement

- **Pin collision in dense blocks is the biggest remaining visual problem.** Daggett
  has 7 sales within ~33 m of each other; at low-to-mid zoom those pins overlap and
  the numbers are unreadable. Real options: collision-aware label offsetting, cluster
  badges that expand on zoom, or a spiderfy-on-tap treatment. Note the constraint that
  the numbers are the map↔list cross-reference, so hiding them entirely breaks the model.
- Landmark labels still overlap sale pins in the middle of the map at some zooms. Only
  three, and toggleable, but it's the next collision problem after the pins.
- The route line crossing itself in the dense core reads a bit busy. Consider drawing
  it under the pins with a lighter weight, or an arrowhead/direction cue so the loop's
  direction of travel is legible.
- The tricolore bar in the masthead goes tall and thin when the header wraps on phones.
- There's a visible sliver of a card clipped at the sticky map's bottom edge while
  scrolling on mobile — standard sticky behavior, but a mask or fade would be tidier.

### Real-world testing and edge cases

- **Test on a real phone in sunlight.** This gets used one-handed on a sidewalk on a
  September morning. Contrast of `--mute` text on `--paper`, and the 9.5px mono street
  labels, are the things most likely to fail outdoors.
- `#mapshell` has `touch-action: none`, so a swipe starting on the map pans the map
  instead of scrolling the page. Correct for a map, but verify it doesn't feel like a
  scroll trap now that the phone layout is page-scrolling.
- Verify the **Directions →** hand-off actually opens Google Maps (app or web) on both
  iOS and Android, from inside whatever browser the shared link opens in.
- Check the **"Happening now"** badge. It's anchored to `-05:00` (CDT) via two
  `Date.parse` calls and ticks every 60s; verified across the 8am/noon boundaries and
  from a non-Central timezone. Worth re-checking near the date.
- Print output (`@media print`) was written but **never actually test-printed.**
- 59 pin elements get a style write per frame while panning — verify it's smooth on an
  older phone.

---

## Open items

- **Printable flyer / PDF** — Jim's original ask, still not built. One page: map plus
  the numbered list. He deferred it this round.
- **Google My Maps CSV/KML export** — also originally requested, deferred. All the
  geocoded data is ready in `stops.json`, so this is quick.
- **`2227 Stephen Ct` vs `Stephen Ave`** — unresolved possible typo in the signup.
- **Neighborhood Center double marker** — landmark *and* sale pin. Jim's call.
- **Whether to forbid the two outliers as a chosen start** — offered, he hasn't decided.
- **Late signups.** If more houses register before the 26th, `./build.sh --data`
  re-reads the sheet, but re-geocoding is a manual curl step (`build.sh --data` prints
  it) and any no-match needs a `MANUAL` entry. Note that **adding a house renumbers the
  whole loop**, so if flyers get printed, either print late or switch to fixed IDs and
  append latecomers at the end. Jim has been warned about this.
