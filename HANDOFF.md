# The Hill Yard Sale Map — handoff

**Live artifact:** https://claude.ai/artifact/XTPHamraY1feVFwMaanuQp (Version 15)
**Live on GitHub Pages:** https://jimbarnthouse-psf.github.io/hill-yard-sale-map/
**Repo:** https://github.com/jimbarnthouse-psf/hill-yard-sale-map (public)
**Event:** Saturday, September 26, 2026, 8am–noon. The Hill, St. Louis 63110.
**Handed off:** September 17, 2026, updated September 18, 2026 (twice) — 8 days out.
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

## What happened since the original handoff (2026-09-17 → 2026-09-18)

The "polish" round (pin collision, route-direction arrows, contrast/text-size floor,
mobile filter-chip fade) landed, then a real-phone QA pass surfaced and fixed:
mobile layout completely broken on GitHub Pages (missing viewport meta — see
[Read this before touching the map](#read-this-before-touching-the-map)), blurry
zoomed-in pin numbers (`filter:drop-shadow` forcing bitmap rasterization), street
labels vanishing when zoomed into an unlabeled block, a broken list-scroll-to-top
(`scrollTo({behavior:'smooth'})` silently no-ops in real browsers — never trust it,
use instant scroll), and a handful of permanently-stuck clusters (real next-door
houses too close for any zoom to separate — now falls back to a picker). Also: a
PWA manifest + home-screen icon set, an address-list update (one swap), and a
masthead redesign that gave the map more vertical room. Full detail and the
"don't reintroduce these" list is in
[Bugs already found and fixed](#bugs-already-found-and-fixed--dont-reintroduce-these).

All of the above is **live on both deploy targets** as of Version 15 / the latest
`main` push — see the links at the top of this file.

## What happened 2026-09-18 (second session) — the walking path is real now

Three things Jim asked for, after he pointed out that the map showed the *order*
of the sales but never **where to actually walk**:

1. **The route line now follows real streets.** It used to be crow-flies stop to
   stop — a straight line through blocks, backyards and the interstate. It is now
   routed over the OSM street network at build time by the new `build/walk.py`.
   It is also **on by default**; it used to be off, which is why almost nobody saw
   it. See [The drawn path](#the-drawn-path-walkpy) below.
2. **"You are here"** — a live-location dot, behind a toggle, off until tapped.
   Highlights the nearest sale in both map and list; **does not** reorder the list
   and **does not** auto-pan. See [You are here](#you-are-here).
3. **Building outlines: investigated and rejected.** See
   [Why there are no buildings](#why-there-are-no-buildings-on-the-map).
4. **The route order was re-solved on street distance**, which renumbered every
   house. 7.54 → 7.28 mi as drawn.
5. **The whole navigation model was reworked** after Jim tested v16 — one bold
   next-leg instead of 59, closest-to-me list mode, no more "walk it in order".
   See [The navigation rework](#the-navigation-rework-the-third-pass-and-the-important-one).

Artifact **v16 was published before items 4 and 5**, so it is two rounds stale —
republish before relying on it.

The landmark toggle is **gone** — Jim judged the layer wouldn't get used, and the
button slot was better spent on location. The three landmarks themselves are
unchanged and now simply always drawn (which was their default state anyway).

**Still open:** none of this is tested on a real phone yet — see
[You are here](#you-are-here).

### The navigation rework (the third pass, and the important one)

Jim tested v16 and the verdict was that the map still didn't answer the only
question that matters on a sidewalk: **"I'm at this sale, where do I go next?"**
Drawing all 59 legs at one weight was the cause -- in the dense core the line
crosses itself repeatedly and no reader can tell which strand is theirs. When
everything is emphasised, nothing is.

He also pointed out the framing was wrong: **most people will not walk 59 sales
in four hours**, so a page built around "walk it in order" is built around
something almost nobody will do.

What changed:

1. **The route is two layers now.** `gRoute` draws the whole loop faint (17%
   opacity, thin) as context. `gLeg` draws **one leg bold** -- the walk from the
   selected sale to the next one. `showLeg()` sets it; `drawLeg()` renders it.
   Direction chevrons now appear **only on the active leg**, not all 59.
2. **The card's primary action is "Next stop"** -- number, address and real
   walking distance, as a full-width brick button. Tapping it advances to that
   sale and shows *its* onward leg, so the popup walks you around the loop one
   step at a time. This is the feature; everything else supports it.
3. **The destination pin is forced out of its cluster** (`solo()` in
   `updateClusters()`) and ringed (`.pin.dest`). A destination hidden inside a
   cluster badge doesn't answer "where am I going".
   The sale card itself moved off the map entirely in the next pass — see
   [The card came off the map](#the-card-came-off-the-map-fourth-pass).
4. **Two list modes**, `#mnear` / `#mloop`: *Closest to me* (sorts by distance
   from the reader, drops the street headings, puts a distance on every card) and
   *Walking loop*. Choosing "Closest to me" without a position **turns location
   on for you** rather than being a dead button. Losing the fix falls back to
   loop order rather than freezing a stale one.
5. **The "start the loop here" flow is gone**, and with it `startAt`,
   `localStorage['hill-start']` and the renumbering. `num(s)` is now just
   `s.i + 1`. Numbers are the map-to-list cross-reference, nothing more.
6. **Total mileage is gone from the footnote.** It read as a commitment nobody
   was making. `walk_mi` is still computed and still in `routemeta.json`.
7. **The map-control route toggle now hides only the faint loop**, never the bold
   leg. Burying the next-stop line behind a toggle is exactly what made the old
   route line invisible to everyone.

#### The card came off the map (fourth pass)

Jim's verdict on the popup version: *"those location pop ups just take up the
whole map. It's almost unusable."* He was right — on a phone the card covered
most of the thing it was describing.

- **`#nowpanel`**, at the top of the list column, replaces the map popup for
  sales. Desktop: the map column is left completely alone. Phone: it is
  `position: sticky` directly under the sticky `#mapcol`, so the selected sale
  and its **Next stop** button stay on screen while the list scrolls past.
  **Its `top` offset is hard-coded to `#mapcol`'s height (52vh, 50vh under
  520px) — change one and you must change the other.**
- `#pop` still exists but now serves **only the cluster picker**, which is small
  and user-invoked. Its placement went back to a plain above-with-flip; the
  four-position scoring routine below is gone, because the card that needed it
  is no longer on the map. `placePop()` (anchored to a stop) is gone too.
- `fitLeg()` lost its reserved band and just centres the leg, for the same reason.
- **Cards dropped the category tags.** They were regex-derived from the item text
  printed directly above them, so every card restated its own description in
  worse words. Only the "Cash only" chip survives, because that is information
  the description does not carry. The tags still drive the filter chips.
- **Directions is an icon** (arrow-leaving-a-box, `goLink()`), shared by cards and
  the panel. Jim noted he didn't expect to be sent off-site: the glyph is the
  standard external-link mark and the `aria-label` says "opens a new tab". The
  in-page answer to "where do I go" is the bold leg; this is for turn-by-turn
  from somewhere else.
- **Resize re-frames the map.** `measure()` recomputes the projection scale while
  `tx/ty/k` are still in the old one, so the view slid off whatever the reader was
  looking at — most visible on a phone rotating or browser chrome collapsing. The
  resize handler now re-runs `fitLeg()` (or `fit()`).

**A previous pass's `placePopAt()` scored its own position.** That code is gone
now (see above), but the reasoning is worth keeping in case the card ever goes
back over the map: The card is anchored to the selected
pin and the bold leg starts at that same pin, so any fixed side eventually lands
on the line. It now tries four positions around the pin and keeps whichever
covers least of the leg, measured against sampled points. Before: one leg was
**100% hidden behind its own card**. After: worst case is 42%, on the two folded
I-44 footbridge legs, where both endpoints stay visible; 57 of 59 are under 10%.
A hard-coded reserve does not work either: 180px was smaller than a tall card, so
the placement guard flipped it straight back over the leg.

**`--on-accent` is a new palette token.** Text sitting on a `--brick` / `--gold` /
`--basil` / `--you` fill was hard-coded `#fff`. That is fine on the light palette,
but the dark palette turns those accents into light pastels: white on dark-mode
brick measures **3.35:1**, which fails WCAG AA for 13px text, and this map gets
read one-handed in September sunlight. `--on-accent` is `#FFFFFF` light and
`#1C1310` dark, so **light mode is pixel-identical** and dark mode becomes legible.
It covers pin numbers, cluster badges, filter chips, map buttons, the popup number
and the next-stop button. **Use it for any new text on an accent fill.**

### The drawn path (`walk.py`)

`build/walk.py` reads `osm.json` (raw tags — **not** `geom.json`, which tiers roads
for drawing and throws the `highway` tag away), builds a pedestrian graph, snaps
each stop to the nearest walkable edge, and runs Dijkstra between consecutive
stops around the loop. Output is `walk.json`: one `[lat, lon]` polyline per leg,
leg `i` running from stop `i` to stop `i+1`, last leg closing the loop. ~10 KB
inlined, so the page went 262 KB → 280 KB. Runs in under a second.

Two things in it are load-bearing and were each arrived at by fixing a real,
visible bug — **don't undo either without re-checking the other**:

- **Footways are included.** I-44 crosses the bbox (OSM name: "Officer Michael
  Barwick Memorial Highway") and severs Marconi Ave. The only pedestrian link
  across it is a mapped footbridge. Drop footways and the router detours ~700 m
  around an interstate a walker simply crosses.
- **`CROSS = 22.0` adds a connector between any two graph nodes closer than 22 m.**
  Keeping footways reintroduces the opposite problem: where OSM maps a street's
  two sides as separate sidewalk ways, the router will only cross between them at
  a mapped crossing — so walking to the house *directly across the street* became
  a 153 m detour (2336 → 2315 Macklind Ave, 19 m apart). 22 m spans a residential
  street here while staying well under the ~60 m between parallel streets, so it
  never fuses two blocks, and an interstate is far too wide to bridge.

Also: legs between houses less than 30 m apart are drawn as a straight line rather
than routed, because routing next-door neighbours out to the sidewalk and back
drew a pointless hairpin.

`walk.py` is also imported as a module by the route solver — `street_matrix()` is
what it now optimises against. See
[The solver optimises real street distance](#the-solver-optimises-real-street-distance-changed-2026-09-18).

**The distance changed and the page says so.** The footnote used to promise 5.27 mi,
the straight-line figure the solver optimised; nobody was ever going to walk that.
It now quotes `walk_mi`, the drawn distance, currently **7.28 mi**. `walk.py` writes
`walk_mi` into `routemeta.json` on every run. Note `loop_mi` there is the solver's
own figure (7.02) — same units, but it excludes the house-to-sidewalk stubs the drawn
path includes, so the two legitimately differ.

### You are here

`navigator.geolocation.watchPosition()` — a browser API, not a network request, so
it doesn't touch the CSP or this page's zero-runtime-fetch property. **The position
is never transmitted anywhere and there is no backend to send it to. Keep it that
way.**

Decisions Jim made explicitly, so don't quietly reverse them:

- **No auto-pan.** The dot moves; the map stays where the reader put it.
  Recentring would fight someone who has looked ahead or opened a popup.
- **The list never reorders by proximity.** Its whole point is the fixed walking
  loop. The nearest stop is *highlighted* in both map and list instead.
- **Toggle, off by default**, so no one gets a permission prompt they didn't ask
  for. It reuses the map-pin icon the landmark button used to have.

Implementation notes worth keeping:

- The nearest stop can be swallowed by a cluster badge, and a highlight on a
  `display:none` pin helps nobody — `updateClusters()` marks the badge instead,
  and `nearI` is part of its memo key so the badge updates as the reader moves.
- The dot counter-scales (`1/k`) like a landmark; the **accuracy ring does not** —
  it's a real-world radius, so it lives in layer units and rides the zoom. Its
  hide-threshold has to be `r*k`, in screen px, not `r`.
- `#locmsg` joins `.mapui` as a no-go rect for street labels, and re-measures on
  every message because it can grow to two lines.
- Handled and tested: permission denied, position unavailable, reader outside the
  map bbox, and toggling off mid-fix.
- **`--you` is a new palette token** (`#1F62A8` light, `#7FB6EA` dark), added to all
  four palette blocks. It is deliberately *not* `--basil`: green already means
  "landmark" and brick means "sale", so the reader's own position needed its own
  colour or it read as a fourth orientation marker.

**Not yet tested on a real phone** — in particular geolocation in
**standalone/home-screen (PWA) mode**, where iOS Safari's permission prompting and
persistence differ from in-browser. That's the first thing to check on device.

### Why there are no buildings on the map

Jim asked for building outlines to help the map read as a real neighborhood. I
fetched them (`build/qb.txt` is the Overpass query, over the map's own bbox) and
**rejected the result**: OSM has only 398 buildings in the whole area, and

- only **8 of the 59 sale houses** have a mapped building at all, and
- only **16 of the 42** 100 m cells containing sales have any building.

Drawing that scatters a few outlines across a mostly empty map and reads as if
those houses were being singled out — actively misleading on a map whose entire
job is marking specific houses. `qb.txt` is kept so nobody has to re-derive this;
the raw response was deleted.

If the underlying want ("help me recognise where I am") comes back, the honest
version is **block polygons** — shade the areas enclosed by streets, derived from
the road geometry already inlined. That needs no new data and can't be patchy,
because it's computed from the same streets that are already drawn.

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

The same trap applies to `walk.json`, which is the path drawn *between* the stops in
`stops.json` — a stale one draws the last build's route between this build's houses.
`build.sh` now re-runs `walk.py` automatically whenever `stops.json` is newer, so
just use `build.sh`.

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
  walk.py                      stops + OSM streets -> walk.json (THE DRAWN PATH)
  q.txt                        the Overpass query, to refetch geometry
  qb.txt                       the buildings query — see "Why there are no buildings"
  clean.json                   60 parsed listings
  batch.csv                    geocoder input
  geo_raw.csv                  Census batch geocoder output
  osm.json                     raw Overpass response (1.8 MB — avoids refetching)
  geom.json                    compressed street geometry, inlined into the page
  stops.json                   THE DATA — 59 stops, in route order
  walk.json                    the drawn path: one street-following polyline per leg
  routemeta.json               loop distance, start, end, outliers, walked distance
dist/
  map.html                     what gets published
  preview.html                 same page, locally openable
```

Everything in `build/` uses bare relative filenames, so **run the scripts from
inside `build/`** (or just use `build.sh`, which cds for you).

---

## Data provenance and its caveats

**2026-09-18 update:** Jim sent a revised spreadsheet — `5427 Bischoff Ave` dropped,
`5606 Botanical Ave` added (net stop count unchanged, 60 rows in → 59 stops out).
`5606 Botanical Ave` geocoded on the first try (exact Census match, no `MANUAL` entry
needed). Loop grew slightly to 5.27 mi / 26 street runs. `source/Yard Sale Listing
FINAL.xlsx` is now this revised file — the version from the 2026-09-17 handoff is
gone; if you need it, it's in this repo/artifact's history before this date.

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

A **closed loop**, 59 stops, **7.28 miles as drawn and walked** — though the page no
longer tells anyone that, on purpose. `stops.json` array order starts at
`5414 Wilson Ave` and ends at `2023 Macklind Ave`. That start is not surfaced as
*the* start anywhere in the UI; it is simply the array order, and the order the
numbers come from.

Jim's constraint was: *don't start or end on any sale that's way off on its own.* Two
sales are genuine geographic outliers (mean distance to their 3 nearest neighbors) —
unaffected by the 2026-09-18 address swap (5427 Bischoff Ave → 5606 Botanical Ave),
since neither is near either outlier:

- `4941 Magnolia Ave` — 563 m, nearest neighbor 506 m away. Half a mile south of everything.
- `1631 Sublette Ave` — 549 m, nearest 479 m.

Everything else has a neighbor within ~190 m. Solving as a **loop** satisfies the
constraint structurally: first and last stop are adjacent by definition, so if one is
central both are. The outliers sit mid-route (re-check their numbers after any
`--data` or `--route` re-run — they shift); Magnolia is an unavoidable out-and-back
spur.

**Outliers are still measured on straight-line distance**, on purpose, even though
the solver now optimises street distance. Jim's rule is a geographic statement and
the 400 m threshold was tuned against straight-line; switching it would inflate every
isolation score and quietly reclassify stops he already signed off on. `route3.py`
and `route_final.py` keep both matrices (`DS` straight-line, `D` street) for exactly
this reason — **don't collapse them into one.**

### The solver optimises real street distance (changed 2026-09-18)

`route3.py` / `route_final.py` minimise `distance + PEN × (number of street runs)`,
where **`distance` is now metres walked along real streets**, from
`walk.street_matrix()` — one Dijkstra per stop over the pedestrian graph.

It used to be straight-line distance, which on a street grid systematically misjudges
which stop is really "next": two houses back to back across a block are 40 m apart and
a 300 m walk, and the solver would happily pair them. Re-solving on street distance
took the loop from **7.29 mi to 7.02 mi** as the solver measures it (7.54 → 7.28 mi
as drawn, which also counts the short house-to-sidewalk stub at each stop).

This costs ~18 s of Dijkstra before the solve, and `route3.py`'s full sweep is now
~2 min. Both scripts `import walk`, so **they must be run from inside `build/`** —
already true of everything here.

The frontier, re-measured on street distance (2026-09-18):

| PEN | miles | street runs | character |
|-----|-------|-------------|-----------|
| 0 | 6.98 | 32 | shortest, but hops between streets constantly |
| 50 | 7.02 | 27 | |
| **100** | **7.02** | **27** | **shipped** — the knee |
| 175 | 7.22 | 24 | |
| 300 | 7.87 | 20 | |
| 600 | 8.35 | 18 | one street at a time, fully legible |

PEN=100 costs 0.6% over optimal to cut five street runs — a clearer knee than the old
straight-line frontier had. Jim was shown the numbers and can switch:
`python3 route_final.py <PEN>` from `build/`, then `./build.sh`.

**Re-solving renumbers every house.** Same hazard as adding a late signup — if
anything numbered has been printed or shared, it has to happen before that.

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
`stops.json` array order, and that is also the number printed on it:

```js
num(s) = s.i + 1
```

Selection, pins, cards, clusters and the leg lookup are all keyed on `s.i`. The
displayed number is never used as an identity.

**This used to be reader-relative.** A `startAt` let anyone pick a house as #1 and
the whole list renumbered from there, persisted in `localStorage['hill-start']`.
That went out with the "walk it in order" framing (2026-09-18): once the page stops
claiming people will walk all 59 in order, a number that moves is strictly worse
than one that doesn't — and it made the number useless as a thing to point at.
**If you reintroduce reader-relative numbering, you also reintroduce the trap that
`localStorage` throws in private windows and during thumbnail capture.**

This invariant must hold after any change to stops or the list:

```js
const nums=[...document.querySelectorAll('#pinlayer button.pin .n')].map(e=>+e.textContent).sort((a,b)=>a-b);
JSON.stringify(nums)===JSON.stringify(Array.from({length:59},(_,i)=>i+1))  // must be true
```

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
6. **`template.html` had no `<meta charset>` or `<meta name="viewport">` of its own** —
   it relied on the Claude Artifact platform's wrapper to supply both. GitHub Pages
   serves this file raw with no wrapper, so mobile browsers fell back to a ~980px
   virtual viewport, `@media (max-width:860px)` never matched, and the desktop
   two-column layout rendered crushed onto the phone screen in both orientations.
   **The page must declare these itself, always** — never assume a host wrapper.
7. **Pin/cluster numbers went blurry when zoomed in.** Both used
   `filter:drop-shadow(...)`, which forces the browser to rasterize the element
   (including the number) at its pre-zoom size before the map's ancestor zoom-scale
   transform blows that bitmap back up. Swapped for `box-shadow` on the circle
   instead — same look, no forced rasterization. **Never put `filter:` on an element
   that's also inside a scaled/zoomed ancestor and carries text that needs to stay
   sharp.**
8. **Street labels could vanish for a street you were actively zoomed into.** Each
   street used to get exactly one label, at its single longest node-to-node OSM
   segment — for a long, densely-sampled street (Daggett, Bischoff, Wilson) that one
   fixed point could be far off-screen while you browsed a different block of the
   same street, which is visible but unlabeled. Fixed two ways: (a) merge consecutive
   OSM segments that keep roughly the same heading into genuine straight runs
   (±14°) instead of measuring node-to-node, since long straight streets were often
   sampled as many short hops that individually never cleared the length floor; (b)
   label *every* qualifying run per street (capped at 3), not just the longest, so a
   multi-block street keeps a label in view as you pan. If you touch the label logic,
   re-verify by zooming into a block away from a street's most prominent stretch.
9. **`window.scrollTo({behavior:'smooth'})` silently no-ops in at least one real
   browser context** (confirmed by direct measurement, 2026-09-18 — `scrollY` simply
   never changed). This broke the setStart() list-reanchor fix even though it tested
   fine via `scrollIntoView`-based approaches. **Never rely on smooth-scroll
   completing** — use instant `scrollTo(x,y)` / `element.scrollTop=` and verify with
   `getBoundingClientRect()` measurements, not just "did the value change."
10. **A handful of clusters never resolved even at max zoom** (`MAXK=14`) — some
    houses are genuinely next-door neighbors, close enough in real distance that no
    achievable zoom separates their pins past a tappable gap (e.g. 5227/5231/5235
    Daggett Ave, three doors in a row). Tapping the badge would zoom to the cap and
    just sit there, stuck. Fixed with a fallback: if the zoom needed to separate a
    cluster exceeds `MAXK`, tapping it opens a picker (`#pop` repurposed) listing
    each address directly instead of trying to zoom. See `openPicker`/`pickerHTML`.

## Masthead redesign (2026-09-18) — more room for the map

Jim wanted the map bigger. The masthead used to be title+subtitle (sales count/
street count/loop distance/location — all duplicated elsewhere: the tally line and
the footnote) on the left, plus a separate `.whenbox` pill (date/time) on the right
that would **wrap to its own row on narrow screens**, stretching `.tri` (the
tricolore flag bar) tall and thin — a known issue, never fixed until now.

Restructured to just two children in `.mast`: the title block (title + date/time
where the old subtitle was) on the left, `.tri` on the right. No more wrappable
third element, so the flag-bar-goes-tall-and-thin bug is gone structurally, not
patched. Freed height went straight to the map: mobile `#mapcol` went from
`46vh`/`44vh` (≤520px) to `52vh`/`50vh`. Desktop's map grows automatically too,
since `#split` just fills whatever vertical space the header leaves.

**If you touch the masthead again:** `.mast` must stay exactly two flex children
(title block, `.tri`) with no `flex-wrap` — that's what guarantees it never wraps.
Re-verify at 320px width (title wraps to 2 lines internally, `.tri` stays put) and
with the live pill (`#livepill`) shown, not just its default hidden state.

### Testing notes

`node --check` on the extracted `<script>` catches syntax errors cheaply:

```bash
node --check <(sed -n '/^<script>$/,/^<\/script>$/p' dist/map.html | sed '1d;$d')
```

The browser pane's synthetic `scroll` action does **not** fire a real `wheel` event,
so wheel-zoom can't be verified that way — it scrolls the page instead. Use the `+`/`−`
buttons, or drive handlers via `javascript_tool`. Wheel zoom itself is a standard
`wheel` listener and works for real users; don't "fix" it based on that false negative.

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

- **NOT TESTED ON A REAL PHONE.** Everything since v16 — the next-stop flow, the
  two list modes, geolocation in standalone/home-screen (PWA) mode — has only been
  exercised in a desktop browser at an emulated phone size. iOS Safari differs on
  geolocation permission prompting and persistence in standalone mode especially.
  **This is the first thing the next session should do.**
- **Printable flyer / PDF** — Jim's original ask, still not built. One page: map plus
  the numbered list. He deferred it this round.
- **Google My Maps CSV/KML export** — also originally requested, deferred. All the
  geocoded data is ready in `stops.json`, so this is quick.
- **`2227 Stephen Ct` vs `Stephen Ave`** — unresolved possible typo in the signup.
- **Neighborhood Center double marker** — landmark *and* sale pin. Jim's call. Now
  that the landmark toggle is gone there's no way to hide the duplicate, so this is
  slightly more pointed than it was.
- **Late signups.** If more houses register before the 26th, `./build.sh --data`
  re-reads the sheet, but re-geocoding is a manual curl step (`build.sh --data` prints
  it) and any no-match needs a `MANUAL` entry. Note that **adding a house renumbers the
  whole loop**, so if flyers get printed, either print late or switch to fixed IDs and
  append latecomers at the end. Jim has been warned about this.
