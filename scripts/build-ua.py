"""Build data/ua.json: the 24 oblasts of Ukraine and the Autonomous Republic of Crimea.

Usage (from the repo root):
    python scripts/build-ua.py
Boundaries: geoBoundaries UKR ADM1 (simplified), ODbL, OpenStreetMap contributors; cached in scripts/.cache/.
Names and centres: Wikidata. Kyiv city is drawn as part of Kyiv oblast (its centre), Sevastopol as part of Crimea.
"""
import json, math, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import rings_of, area, simplify, ring_path, inside, label_point

SRC = 'https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/UKR/ADM1/geoBoundaries-UKR-ADM1_simplified.geojson'
CACHE = os.path.join(os.path.dirname(__file__), '.cache', 'ukr-adm1.geojson')
if not os.path.exists(CACHE):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    urllib.request.urlretrieve(SRC, CACHE)
d = json.load(open(CACHE, encoding='utf-8'))

# ISO 3166-2 -> id, Ukrainian name, Polish name, spoken (Ukrainian) name, centre (uk, pl, lat, lon)
META = {
 'UA-05': ('vinnytska', 'Вінницька', 'Winnicki', 'Вінницька область', ('Вінниця', 'Winnica', 49.2372, 28.4672)),
 'UA-07': ('volynska', 'Волинська', 'Wołyński', 'Волинська область', ('Луцьк', 'Łuck', 50.7478, 25.3244)),
 'UA-09': ('luhanska', 'Луганська', 'Ługański', 'Луганська область', ('Луганськ', 'Ługańsk', 48.5717, 39.2973)),
 'UA-12': ('dnipropetrovska', 'Дніпропетровська', 'Dniepropetrowski', 'Дніпропетровська область', ('Дніпро', 'Dniepr', 48.4675, 35.04)),
 'UA-14': ('donetska', 'Донецька', 'Doniecki', 'Донецька область', ('Донецьк', 'Donieck', 48.0158, 37.8028)),
 'UA-18': ('zhytomyrska', 'Житомирська', 'Żytomierski', 'Житомирська область', ('Житомир', 'Żytomierz', 50.2544, 28.6578)),
 'UA-21': ('zakarpatska', 'Закарпатська', 'Zakarpacki', 'Закарпатська область', ('Ужгород', 'Użhorod', 48.6239, 22.295)),
 'UA-23': ('zaporizka', 'Запорізька', 'Zaporoski', 'Запорізька область', ('Запоріжжя', 'Zaporoże', 47.85, 35.1175)),
 'UA-26': ('ivano-frankivska', 'Івано-Франківська', 'Iwanofrankiwski', 'Івано-Франківська область', ('Івано-Франківськ', 'Iwano-Frankiwsk', 48.9228, 24.7106)),
 'UA-32': ('kyivska', 'Київська', 'Kijowski', 'Київська область', ('Київ', 'Kijów', 50.45, 30.5236)),
 'UA-35': ('kirovohradska', 'Кіровоградська', 'Kirowohradzki', 'Кіровоградська область', ('Кропивницький', 'Kropywnycki', 48.5103, 32.2667)),
 'UA-43': ('krym', 'АР Крим', 'Krym', 'Автономна Республіка Крим', ('Сімферополь', 'Symferopol', 44.9484, 34.1)),
 'UA-46': ('lvivska', 'Львівська', 'Lwowski', 'Львівська область', ('Львів', 'Lwów', 49.842, 24.0316)),
 'UA-48': ('mykolaivska', 'Миколаївська', 'Mikołajowski', 'Миколаївська область', ('Миколаїв', 'Mikołajów', 46.975, 31.995)),
 'UA-51': ('odeska', 'Одеська', 'Odeski', 'Одеська область', ('Одеса', 'Odessa', 46.4842, 30.7325)),
 'UA-53': ('poltavska', 'Полтавська', 'Połtawski', 'Полтавська область', ('Полтава', 'Połtawa', 49.5894, 34.5514)),
 'UA-56': ('rivnenska', 'Рівненська', 'Rówieński', 'Рівненська область', ('Рівне', 'Równe', 50.6197, 26.2514)),
 'UA-59': ('sumska', 'Сумська', 'Sumski', 'Сумська область', ('Суми', 'Sumy', 50.9067, 34.7992)),
 'UA-61': ('ternopilska', 'Тернопільська', 'Tarnopolski', 'Тернопільська область', ('Тернопіль', 'Tarnopol', 49.5667, 25.6)),
 'UA-63': ('kharkivska', 'Харківська', 'Charkowski', 'Харківська область', ('Харків', 'Charków', 49.9925, 36.2311)),
 'UA-65': ('khersonska', 'Херсонська', 'Chersoński', 'Херсонська область', ('Херсон', 'Chersoń', 46.6425, 32.625)),
 'UA-68': ('khmelnytska', 'Хмельницька', 'Chmielnicki', 'Хмельницька область', ('Хмельницький', 'Chmielnicki', 49.42, 27.0)),
 'UA-71': ('cherkaska', 'Черкаська', 'Czerkaski', 'Черкаська область', ('Черкаси', 'Czerkasy', 49.4444, 32.0597)),
 'UA-74': ('chernihivska', 'Чернігівська', 'Czernihowski', 'Чернігівська область', ('Чернігів', 'Czernihów', 51.4939, 31.2947)),
 'UA-77': ('chernivetska', 'Чернівецька', 'Czerniowiecki', 'Чернівецька область', ('Чернівці', 'Czerniowce', 48.2908, 25.9344)),
}
MERGE = {'UA-30': 'UA-32', 'UA-40': 'UA-43'}  # Kyiv city -> Kyiv oblast, Sevastopol -> Crimea

K = math.cos(math.radians(48.5))
pr = lambda lon, lat: (lon * K, -lat)
allp = [pr(*c) for f in d['features'] for poly in rings_of(f['geometry']) for c in poly[0]]
minx = min(p[0] for p in allp); maxx = max(p[0] for p in allp)
miny = min(p[1] for p in allp); maxy = max(p[1] for p in allp)
S = 1000 / (maxx - minx)
H = (maxy - miny) * S
def P(lon, lat):
    x, y = pr(lon, lat)
    return ((x - minx) * S, (y - miny) * S)

# collect polygons per region (in svg units)
polys = {iso: [] for iso in META}
for f in d['features']:
    iso = f['properties']['shapeISO']
    iso = MERGE.get(iso, iso)
    for poly in rings_of(f['geometry']):
        polys[iso].append([[P(*c) for c in ring] for ring in poly])

out = []
for iso, (rid, ua, pl, spoken, (cua, cpl, lat, lon)) in META.items():
    pp = polys[iso]
    if iso == 'UA-32':
        # Kyiv oblast surrounds Kyiv city: drop its holes and any piece lying inside another piece
        outers = [p[0] for p in pp]
        pp = [[o] for o in outers if not any(o is not q and abs(area(q)) > abs(area(o)) and inside(o[0], q) for q in outers)]
    rings = []
    for poly in pp:
        for ring in poly:
            s = simplify(ring, 0.5)
            if len(s) >= 4 and abs(area(s)) > 1.5:
                rings.append(s)
    main = max(rings, key=lambda r: abs(area(r)))
    cx, cy = P(lon, lat)
    # keep the centre dot away from the label and from the shield drawn under it
    lx, ly = label_point(main, avoid=[(cx, cy), (cx, cy - 18), (cx, cy - 36)], avoid_w=0.9)
    out.append({'id': rid, 'name': {'uk': ua, 'pl': pl}, 'local': spoken,
                'caps': [{'name': {'uk': cua, 'pl': cpl}, 'local': cua, 'x': round(cx, 1), 'y': round(cy, 1), 'seat': ''}],
                'lx': round(lx, 1), 'ly': round(ly, 1), 'd': ''.join(ring_path(r) for r in rings)})

T = {
 'uk': {'title': 'Області України', 'Unit': 'Область', 'center': 'Обласний центр', 'sayLabel': 'Вимова',
        'tabGuess': 'Назви область', 'tabCity': 'Місто → область',
        'exploreSub': 'Наведи або натисни на область, щоб побачити назву і обласний центр.',
        'guessSub': 'Натисни на область на мапі або візьми випадкову.', 'random': 'Випадкова область',
        'guessQ': 'Що це за виділена область?', 'findQ': 'Знайди на мапі область:',
        'cityQ': 'Синя точка — місто. Натисни на область, центром якої воно є:',
        'hint': 'Область вважається вивченою після 2 правильних відповідей поспіль.'},
 'pl': {'title': 'Obwody Ukrainy', 'Unit': 'Obwód', 'center': 'Stolica obwodu', 'sayLabel': 'Wymowa po ukraińsku',
        'tabGuess': 'Nazwij obwód', 'tabCity': 'Miasto → obwód',
        'exploreSub': 'Najedź kursorem na obwód lub go kliknij, aby zobaczyć nazwę i stolicę.',
        'guessSub': 'Kliknij obwód na mapie albo wylosuj.', 'random': 'Losowy obwód',
        'guessQ': 'Który obwód jest zaznaczony?', 'findQ': 'Znajdź na mapie obwód:',
        'cityQ': 'Niebieska kropka to miasto. Kliknij obwód, którego jest stolicą:',
        'hint': 'Obwód uznaje się za opanowany po 2 poprawnych odpowiedziach z rzędu.'}}
data = {'id': 'ua', 'name': {'uk': 'Україна', 'pl': 'Ukraina'}, 'lang': 'uk-UA', 'w': 1000, 'h': round(H, 1),
        'say': '', 'coa': 'data/herby/ua/', 'coaSize': 30, 'text': T, 'regions': out}
dst = os.path.join(os.path.dirname(__file__), '..', 'data', 'ua.json')
open(dst, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('},{"id"', '},\n{"id"'))
print('wrote', dst, len(out), 'regions', os.path.getsize(dst), 'bytes')
