"""Build data/world.json: simplified country outlines for the country picker.

Usage (from the repo root):
    python scripts/build-world.py
Source: Natural Earth 1:10m admin-0 countries, Ukrainian point-of-view edition (public domain),
cached in scripts/.cache/. Miller projection, Antarctica dropped.
"""
import json, math, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import rings_of, area, simplify, ring_path

SRC = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries_ukr.geojson'
CACHE = os.path.join(os.path.dirname(__file__), '.cache', 'ne_10m_countries_ukr.geojson')
if not os.path.exists(CACHE):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    urllib.request.urlretrieve(SRC, CACHE)
d = json.load(open(CACHE, encoding='utf-8'))

TOP, BOTTOM = 84, -57
miller = lambda lat: 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(max(BOTTOM, min(TOP, lat)))))
S = 1000 / 360
Y0 = miller(TOP)
H = (Y0 - miller(BOTTOM)) * 180 / math.pi * S
def P(lon, lat):
    return ((lon + 180) * S, (Y0 - miller(lat)) * 180 / math.pi * S)

out = []
for f in d['features']:
    p = f['properties']
    iso = p['ISO_A2_EH']
    if iso in ('-99', 'AQ'):
        continue
    rings = []
    for poly in rings_of(f['geometry']):
        s = simplify([P(*c) for c in poly[0]], 0.35)
        if len(s) >= 4:
            rings.append(s)
    if not rings:
        continue
    big = max(abs(area(r)) for r in rings)
    rings = [r for r in rings if abs(area(r)) > 0.6 or abs(area(r)) == big]  # drop tiny islands
    out.append({'id': iso.lower(), 'n': {'uk': p['NAME_UK'], 'pl': p['NAME_PL']},
                'd': ''.join(ring_path(r) for r in rings)})

# merge pieces that share an ISO code (e.g. France has overseas parts as separate features)
merged = {}
for c in out:
    if c['id'] in merged:
        merged[c['id']]['d'] += c['d']
    else:
        merged[c['id']] = c
ex, ey = P(-12, 71)
fx, fy = P(45, 34)
data = {'w': 1000, 'h': round(H, 1), 'focus': [round(ex), round(ey), round(fx - ex), round(fy - ey)],
        'countries': sorted(merged.values(), key=lambda c: c['id'])}
dst = os.path.join(os.path.dirname(__file__), '..', 'data', 'world.json')
open(dst, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('},{"id"', '},\n{"id"'))
print('wrote', dst, len(merged), 'countries', os.path.getsize(dst), 'bytes')
