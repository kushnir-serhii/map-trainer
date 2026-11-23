# Map Trainer

Interactive trainer for learning a country's regions and their capitals on a zoomable map. Available now: the 16 voivodeships of **Poland** and the 24 oblasts + Autonomous Republic of Crimea of **Ukraine**. The interface is in Polish by default; a **PL / UA** switch in the header changes it to Ukrainian (the choice is remembered in the browser). Next to each name, the original in the country's own language is shown in grey (Polish names for Poland in the Ukrainian interface, Ukrainian names for Ukraine in the Polish one).

**Live:** `https://<username>.github.io/map-trainer/`

## Modes

- **Kraje / Країни**: a world map to pick a country. Countries with data are highlighted; the rest are greyed out for now.
- **Przegląd / Огляд**: hover or tap a region to see its name, capital and coat of arms.
- **Nazwij … / Назви …**: a region is highlighted; pick its name and capital from two selects.
- **Znajdź na mapie / Знайди на мапі**: you get a region name, click it on the map.
- **Miasto → … / Місто → …**: a city is marked on the map, click the region it is the capital of.

Each region's coat of arms is shown under its label on the map and next to its name in the panel, to make regions easier to remember (in quizzes it appears only after you answer). Regions you get wrong come back more often. Progress is saved per country in `localStorage`. Local names can be read aloud via the browser's speech synthesis.

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
index.html                page shell
css/style.css             styles (light + dark)
js/app.js                 map, zoom, quiz modes, country picker, progress, UI strings (PL/UK)
data/countries.json       countries that have data (id, names, flag colours)
data/world.json           simplified world outlines for the country picker
data/pl.json, ua.json     regions, SVG paths, capitals, UI wording per interface language
data/herby/<id>/          coats of arms (SVG, one per region id)
scripts/geo.py            geometry helpers for the build scripts
scripts/build-pl.py       rebuilds data/pl.json
scripts/build-ua.py       rebuilds data/ua.json
scripts/build-world.py    rebuilds data/world.json
scripts/fetch-herby.py    downloads coats of arms from Wikimedia Commons: `python scripts/fetch-herby.py ua`
```

## Adding a country

1. Get a GeoJSON of the country's regions.
2. Copy `scripts/build-ua.py` (it handles MultiPolygons and holes, and places labels automatically). Fill in the region names `{uk, pl}`, the spoken local name, the capitals (lat/lon) and the `text` block: one entry per interface language, with whole sentences, because the grammatical gender of the region word differs ("województwo" is neuter, "obwód" masculine, "область" feminine). A region can have more than one capital (as in Kujawsko-Pomorskie and Lubuskie).
3. Add the coat-of-arms file names to `scripts/fetch-herby.py` and run it.
4. Add `{ "id": "<id>", "name": {"pl": "...", "uk": "..."}, "flag": ["#top", "#bottom"] }` to `data/countries.json`. The country then lights up on the world map. Each country is reachable at `#<id>` (for example `#ua`).

## Data

- Poland, region boundaries: [ppatrzyk/polska-geojson](https://github.com/ppatrzyk/polska-geojson).
- Ukraine, region boundaries: [geoBoundaries](https://www.geoboundaries.org/) UKR ADM1 (© OpenStreetMap contributors, ODbL). Kyiv city is drawn as part of Kyiv oblast and Sevastopol as part of Crimea.
- Ukraine, names and centres: Wikidata. Donetsk and Luhansk oblasts use their centres as set by law (Donetsk, Luhansk).
- World map: [Natural Earth](https://www.naturalearthdata.com/) 1:10m admin-0 countries, Ukrainian point-of-view edition (Crimea as part of Ukraine), public domain.
- Coats of arms: Wikimedia Commons, public domain. `scripts/fetch-herby.py` adds a `viewBox` where a file lacks one so it scales.
