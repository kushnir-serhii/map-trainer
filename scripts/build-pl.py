"""Build data/pl.json from the voivodeship GeoJSON.

Usage (from the repo root):
    python scripts/build-pl.py
Downloads the GeoJSON (ppatrzyk/polska-geojson) if it is not cached in scripts/.cache/.
"""
import json, math, os, re, urllib.request
capF=lambda s:re.sub(r'(^|-)(\w)',lambda m:m.group(1)+m.group(2).upper(),s)  # 'kujawsko-pomorskie' -> 'Kujawsko-Pomorskie'
SRC = 'https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-min.geojson'
CACHE = os.path.join(os.path.dirname(__file__), '.cache', 'wojewodztwa.geojson')
if not os.path.exists(CACHE):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    urllib.request.urlretrieve(SRC, CACHE)
d = json.load(open(CACHE, encoding='utf-8'))
K=math.cos(math.radians(52))
def pr(lon,lat): return (lon*K, -lat)
pts=[pr(*c) for f in d['features'] for c in f['geometry']['coordinates'][0]]
minx=min(p[0] for p in pts);maxx=max(p[0] for p in pts);miny=min(p[1] for p in pts);maxy=max(p[1] for p in pts)
S=1000/(maxx-minx)
def P(lon,lat):
    x,y=pr(lon,lat);return ((x-minx)*S,(y-miny)*S)
H=(maxy-miny)*S
meta={
'śląskie':('slaskie','Сілезьке'),'opolskie':('opolskie','Опольське'),'wielkopolskie':('wielkopolskie','Великопольське'),
'zachodniopomorskie':('zachodniopomorskie','Західнопоморське'),'świętokrzyskie':('swietokrzyskie','Свентокшиське'),
'kujawsko-pomorskie':('kujawsko','Куявсько-Поморське'),'podlaskie':('podlaskie','Підляське'),'dolnośląskie':('dolnoslaskie','Нижньосілезьке'),
'podkarpackie':('podkarpackie','Підкарпатське'),'małopolskie':('malopolskie','Малопольське'),'pomorskie':('pomorskie','Поморське'),
'warmińsko-mazurskie':('warminsko','Вармінсько-Мазурське'),'łódzkie':('lodzkie','Лодзинське'),'mazowieckie':('mazowieckie','Мазовецьке'),
'lubelskie':('lubelskie','Люблінське'),'lubuskie':('lubuskie','Любуське')}
caps={
'dolnoslaskie':[('Вроцлав','Wrocław',51.107,17.038,'')],
'kujawsko':[('Бидгощ','Bydgoszcz',53.123,18.008,'voivode'),('Торунь','Toruń',53.013,18.598,'sejmik')],
'lubelskie':[('Люблін','Lublin',51.246,22.568,'')],
'lubuskie':[('Гожув-Великопольський','Gorzów Wielkopolski',52.730,15.238,'voivode'),('Зелена Гура','Zielona Góra',51.935,15.506,'sejmik')],
'lodzkie':[('Лодзь','Łódź',51.759,19.456,'')],
'malopolskie':[('Краків','Kraków',50.065,19.945,'')],
'mazowieckie':[('Варшава','Warszawa',52.230,21.012,'')],
'opolskie':[('Ополе','Opole',50.675,17.921,'')],
'podkarpackie':[('Ряшів (Жешув)','Rzeszów',50.041,21.999,'')],
'podlaskie':[('Білосток','Białystok',53.133,23.169,'')],
'pomorskie':[('Гданськ','Gdańsk',54.352,18.646,'')],
'slaskie':[('Катовиці','Katowice',50.264,19.024,'')],
'swietokrzyskie':[('Кельці','Kielce',50.866,20.628,'')],
'warminsko':[('Ольштин','Olsztyn',53.778,20.480,'')],
'wielkopolskie':[('Познань','Poznań',52.406,16.925,'')],
'zachodniopomorskie':[('Щецин','Szczecin',53.428,14.553,'')]}
# manual label nudges (svg units) to keep labels off city dots
nudge={'mazowieckie':(0,40),'pomorskie':(0,35),'slaskie':(0,-18),'malopolskie':(25,30),'kujawsko':(0,30),'lubuskie':(5,-20),'wielkopolskie':(0,40),'dolnoslaskie':(-10,30),'lodzkie':(0,30),'zachodniopomorskie':(15,30),'warminsko':(0,30),'podlaskie':(-10,40),'lubelskie':(0,40),'podkarpackie':(0,35),'swietokrzyskie':(0,26),'opolskie':(0,24)}
out=[]
for f in d['features']:
    ring=f['geometry']['coordinates'][0]
    xy=[P(*c) for c in ring]
    # simplify: drop points closer than 1.2 units
    s=[xy[0]]
    for p in xy[1:]:
        if math.hypot(p[0]-s[-1][0],p[1]-s[-1][1])>1.2: s.append(p)
    path='M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in s)+'Z'
    A=cx=cy=0
    for i in range(len(xy)-1):
        x0,y0=xy[i];x1,y1=xy[i+1];c=x0*y1-x1*y0;A+=c;cx+=(x0+x1)*c;cy+=(y0+y1)*c
    A/=2;cx/=6*A;cy/=6*A
    pl=f['properties']['nazwa'];rid,ua=meta[pl]
    nx,ny=nudge.get(rid,(0,0))
    cl=[]
    for cua,cpl,lat,lon,seat in caps[rid]:
        x,y=P(lon,lat);cl.append({'ua':cua,'pl':cpl,'x':round(x,1),'y':round(y,1),'seat':seat})
    cl=[{'name':{'uk':c['ua'],'pl':c['pl']},'local':c['pl'],'x':c['x'],'y':c['y'],'seat':c['seat']} for c in cl]
    out.append({'id':rid,'name':{'uk':ua,'pl':capF(pl)},'local':pl,'caps':cl,'lx':round(cx+nx,1),'ly':round(cy+ny,1),'d':path})
data={'id':'pl','name':{'uk':'Польща','pl':'Polska'},'lang':'pl-PL','w':1000,'h':round(H,1),'say':'województwo',
 'coa':'data/herby/pl/',  # coats of arms: <coa><region id>.svg, see fetch-herby-pl.py
 # UI wording per interface language; seat keys ('voivode'/'sejmik') are translated via 'seats'
 'text':{
  "uk": {
   "title": "Воєводства Польщі",
   "Unit": "Воєводство",
   "center": "Головне місто",
   "sayLabel": "Вимова польською",
   "seats": {
    "voivode": "воєвода",
    "sejmik": "сеймик"
   },
   "tabGuess": "Назви воєводство",
   "tabCity": "Місто → воєводство",
   "exploreSub": "Наведи або натисни на воєводство, щоб побачити назву і головне місто.",
   "guessSub": "Натисни на воєводство на мапі або візьми випадкове.",
   "random": "Випадкове воєводство",
   "guessQ": "Що це за виділене воєводство?",
   "findQ": "Знайди на мапі воєводство:",
   "cityQ": "Синя точка — місто. Натисни на воєводство, центром якого воно є:",
   "hint": "Воєводство вважається вивченим після 2 правильних відповідей поспіль."
  },
  "pl": {
   "title": "Województwa Polski",
   "Unit": "Województwo",
   "center": "Stolica",
   "sayLabel": "Wymowa",
   "seats": {
    "voivode": "wojewoda",
    "sejmik": "sejmik"
   },
   "tabGuess": "Nazwij województwo",
   "tabCity": "Miasto → województwo",
   "exploreSub": "Najedź kursorem na województwo lub je kliknij, aby zobaczyć nazwę i stolicę.",
   "guessSub": "Kliknij województwo na mapie albo wylosuj.",
   "random": "Losowe województwo",
   "guessQ": "Które województwo jest zaznaczone?",
   "findQ": "Znajdź na mapie województwo:",
   "cityQ": "Niebieska kropka to miasto. Kliknij województwo, którego jest stolicą:",
   "hint": "Województwo uznaje się za opanowane po 2 poprawnych odpowiedziach z rzędu."
  }
 },
 'regions':out}
dst=os.path.join(os.path.dirname(__file__),'..','data','pl.json')
open(dst,'w',encoding='utf-8').write(json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('},{"id"','},\n{"id"'))
print('wrote', dst, len(out), 'regions')
