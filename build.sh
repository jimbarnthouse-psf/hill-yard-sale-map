#!/bin/bash
# Rebuild dist/map.html from the data already in build/.
#
#   ./build.sh            page only -- edits to template.html (the common case)
#   ./build.sh --route    re-solve the walking loop, then rebuild the page
#   ./build.sh --data     re-read the spreadsheet, re-solve, rebuild (needs network)
#
# ORDER MATTERS: build.py writes stops.json in ALPHABETICAL order and
# route_final.py then rewrites it in ROUTE order. Running build.py without
# re-running route_final.py leaves the shipped numbering alphabetical.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/build"

case "$1" in
  --data)
    echo "==> parse.py      spreadsheet -> clean.json + batch.csv"
    python3 parse.py
    echo
    echo "!!  Re-geocoding is a manual step. clean.json changed, so batch.csv must"
    echo "!!  be re-sent to the Census batch geocoder and geo_raw.csv replaced:"
    echo
    echo "    curl -s --form addressFile=@batch.csv --form benchmark=Public_AR_Current \\"
    echo "         --form returntype=locations \\"
    echo "         https://geocoding.geo.census.gov/geocoder/locations/addressbatch \\"
    echo "         -o geo_raw.csv"
    echo
    echo "!!  Any address it cannot match needs a MANUAL entry in build.py."
    echo "!!  Then re-run:  ./build.sh --route"
    exit 0
    ;;
  --route)
    echo "==> build.py        listings + geocodes -> stops.json (alphabetical)"
    python3 build.py
    echo
    echo "==> route_final.py  -> stops.json (route order) + routemeta.json"
    python3 route_final.py 100
    ;;
esac

echo
echo "==> inject.py       template + data -> dist/"
python3 inject.py

cd "$ROOT"
if [ -f index.html ]; then
  echo "==> index.html      refreshed from dist/map.html (GitHub Pages serves this)"
  cp dist/map.html index.html
  echo "==> manifest.json + icons  refreshed from dist/ (GitHub Pages serves these too)"
  cp dist/manifest.json dist/*.png .
fi

echo
echo "Done. Preview locally with:"
echo "    python3 -m http.server 8731 --directory dist"
echo "    open http://localhost:8731/preview.html"
