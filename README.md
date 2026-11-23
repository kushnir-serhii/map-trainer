# Map Trainer

Interactive trainer for learning a country's regions and their capitals on a zoomable map. The first dataset covers the 16 voivodeships of Poland. The interface is in Polish by default; a **PL / UA** switch in the header changes it to Ukrainian (the choice is remembered in the browser). In the Ukrainian interface the Polish original is shown next to each name.

**Live:** `https://<username>.github.io/map-trainer/`

## Modes

- **Огляд** — hover or tap a region to see its name and capital.
- **Назви регіон** — a region is highlighted; pick its name and capital from two selects.
- **Знайди на мапі** — you get a region name, click it on the map.
- **Місто → регіон** — a city is marked on the map, click the region it is the capital of.

Regions you get wrong come back more often. Progress is saved in `localStorage`. Polish names can be read aloud via the browser's speech synthesis.

## Run locally

The page loads data with `fetch`, so open it through a local server, not by double-clicking `index.html`:

```bash
npx serve .
# or
python -m http.server 8000
```

## Deploy to GitHub Pages

1. Push to `main`.
2. Repo **Settings → Pages → Build and deployment**: Source **Deploy from a branch**, branch `main`, folder `/ (root)`.
3. The site appears at `https://<username>.github.io/map-trainer/`.

No build step. `.nojekyll` makes Pages serve the files as they are.

## Structure

```
index.html            page shell
css/style.css         styles (light + dark)
js/app.js             map, zoom, quiz modes, progress, UI strings (PL/UK)
data/countries.json   list of available countries
data/pl.json          Poland: regions, SVG paths, capitals, UI wording per language
scripts/build-pl.py   rebuilds data/pl.json from GeoJSON
```

## Adding a country

1. Get a GeoJSON of the country's regions.
2. Copy `scripts/build-pl.py`, adapt names, capitals (lat/lon) and the `text` block (one entry per interface language: `pl`, `uk`), and generate `data/<id>.json`. The capital list for each region can have more than one city (as in Kujawsko-Pomorskie and Lubuskie).
3. Add `{ "id": "<id>", "name": {"pl": "...", "uk": "..."}, "flag": ["#top", "#bottom"] }` to `data/countries.json`.

With more than one country, a country selector appears in the header. Each country is reachable at `#<id>` (for example `#pl`).

## Data

Region boundaries come from [ppatrzyk/polska-geojson](https://github.com/ppatrzyk/polska-geojson). Projected to SVG and simplified by `scripts/build-pl.py`.
