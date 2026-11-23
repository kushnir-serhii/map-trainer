"""Download region coats of arms into data/herby/<country>/<region id>.svg.

Usage (from the repo root):
    python scripts/fetch-herby.py pl
    python scripts/fetch-herby.py ua
Source: Wikimedia Commons (public domain). Files already present are skipped.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

PL = {n: f'POL województwo {n} COA.svg' for n in [
    'dolnośląskie', 'kujawsko-pomorskie', 'lubelskie', 'lubuskie', 'łódzkie', 'małopolskie', 'mazowieckie', 'opolskie',
    'podkarpackie', 'podlaskie', 'pomorskie', 'śląskie', 'świętokrzyskie', 'warmińsko-mazurskie', 'wielkopolskie',
    'zachodniopomorskie']}
PL_IDS = {'dolnośląskie': 'dolnoslaskie', 'kujawsko-pomorskie': 'kujawsko', 'łódzkie': 'lodzkie', 'małopolskie': 'malopolskie',
          'śląskie': 'slaskie', 'świętokrzyskie': 'swietokrzyskie', 'warmińsko-mazurskie': 'warminsko'}
FILES = {
 'pl': {PL_IDS.get(n, n): f for n, f in PL.items()},
 # file names from Wikidata (P94, coat of arms image)
 'ua': {
  'cherkaska': 'Coat of Arms of Cherkasy Oblast.svg', 'chernihivska': 'Coat of Arms of Chernihiv Oblast.svg',
  'chernivetska': 'Coat of Arms of Chernivtsi Oblast.svg', 'dnipropetrovska': 'Large Coat of Arms of Dnipropetrovsk Oblast.svg',
  'donetska': 'Coat of Arms of Donetsk Oblast 1999.svg', 'ivano-frankivska': 'Ivano-Frankivsk Oblast-COA.svg',
  'kharkivska': 'Coat of Arms of Kharkiv Oblast.svg', 'khersonska': 'Coat of Arms of Kherson Oblast.svg',
  'khmelnytska': 'Coat of Arms of Khmelnytskyi Oblast.svg', 'kirovohradska': 'Coat of Arms of Kirovohrad Oblast.svg',
  'krym': 'Emblem of Crimea.svg', 'kyivska': 'Coat of Arms of Kiev Oblast.svg',
  'luhanska': 'Coat of Arms Luhansk Oblast.svg', 'lvivska': 'Coat of Arms of Lviv Oblast (2001).svg',
  'mykolaivska': 'Coat of arms of Mykolaiv Oblast (2026).svg', 'odeska': 'Coat of Arms of Odesa Oblast.svg',
  'poltavska': 'Coat of Arms of Poltava Oblast.svg', 'rivnenska': 'Coat of Arms of Rivne Oblast.svg',
  'sumska': 'Coat of Arms of Sumy Oblast.svg', 'ternopilska': 'Coat of Arms of Ternopil Oblast.svg',
  'vinnytska': 'Coat of Arms of Vinnytsa Oblast.svg', 'volynska': 'Coat of Arms of Volyn Oblast (lesser).svg',
  'zakarpatska': 'Coat of arms of Zakarpattia Oblast.svg', 'zaporizka': 'Coat of arms of Zaporizhia Oblast.svg',
  'zhytomyrska': 'Coat of Arms of Zhytomyr Oblast (2003).svg'}}

cid = sys.argv[1] if len(sys.argv) > 1 else 'pl'
IDS = FILES[cid]
UA = {'User-Agent': 'map-trainer-build/1.0 (educational map quiz; https://www.mediawiki.org/wiki/API:Etiquette) python-urllib'}
DST = os.path.join(os.path.dirname(__file__), '..', 'data', 'herby', cid)
os.makedirs(DST, exist_ok=True)

by_title = {}
titles = ['File:' + f for f in IDS.values()]
for i in range(0, len(titles), 20):
    q = urllib.parse.urlencode({'action': 'query', 'prop': 'imageinfo', 'iiprop': 'url', 'format': 'json',
                                'titles': '|'.join(titles[i:i + 20])})
    pages = json.load(urllib.request.urlopen(urllib.request.Request(
        'https://commons.wikimedia.org/w/api.php?' + q, headers=UA)))['query']['pages'].values()
    by_title.update({p['title']: p['imageinfo'][0]['url'].split('?')[0] for p in pages if 'imageinfo' in p})

def get(url, tries=20):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1: raise
            # Commons rate limit: wait as told (Retry-After) or back off, then retry
            wait = int(e.headers.get('Retry-After') or 0) or 30 * (i + 1)
            print(f'  rate limited, waiting {wait}s', flush=True)
            time.sleep(wait)

for rid, fname in IDS.items():
    out = os.path.join(DST, rid + '.svg')
    if os.path.exists(out): continue
    url = by_title['File:' + fname]
    time.sleep(15)
    svg = get(url)
    assert svg.lstrip().startswith((b'<?xml', b'<svg', b'<!--', b'<!DOCTYPE')), url
    open(out, 'wb').write(svg)
    print(rid, len(svg))

# Some files have width/height but no viewBox, so browsers would crop instead of scaling them.
# Add viewBox="0 0 w h" in user units (Inkscape 0.4x files give the size in pt, user units are px = pt*4/3).
def px(v):
    v = v.strip()
    return float(v[:-2]) * 4 / 3 if v.endswith('pt') else float(v.rstrip('px'))
for f in sorted(os.listdir(DST)):
    p = os.path.join(DST, f)
    s = open(p, encoding='utf-8').read()
    m = re.search(r'<svg\b[^>]*>', s)
    tag = m.group(0)
    if 'viewBox' in tag: continue
    w = px(re.search(r'\swidth="([^"]+)"', tag).group(1))
    h = px(re.search(r'\sheight="([^"]+)"', tag).group(1))
    s = s[:m.start()] + tag.replace('<svg', f'<svg viewBox="0 0 {w:g} {h:g}"', 1) + s[m.end():]
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('viewBox added:', f, w, h)
