/* Map Trainer — learn regions and their capitals on a zoomable map.
   Country data lives in data/<id>.json; the list of countries in data/countries.json. */
(async () => {
const $ = id => document.getElementById(id);
/* interface language: Polish by default, Ukrainian on request; remembered in this browser */
const LKEY='map-trainer:lang';
let LANG='pl'; try{const v=localStorage.getItem(LKEY);if(v==='uk'||v==='pl')LANG=v}catch(e){}
const I18N={
uk:{country:'Країна',lang:'Мова інтерфейсу',mode:'Режим',map:'Інтерактивна мапа',zin:'Наблизити',zout:'Віддалити',zreset:'Скинути масштаб',
  explore:'Огляд',guess:u=>`Назви ${u}`,find:'Знайди на мапі',city:u=>`Місто → ${u}`,
  lgSel:'питання / вибрано',lgOk:'вивчено / правильно',lgPart:'вивчається',lgBad:'помилка',
  sOk:'правильно',sAll:'спроб',sKnown:'вивчено',progress:'Прогрес',progressAria:'Прогрес вивчення',
  hint:U=>`${U} вважається вивченим після 2 правильних відповідей поспіль.`,
  weakNone:'Помилок ще не було.',weakAsk:'Частіше питатиму: ',weakOk:'Слабких місць немає — так тримати.',
  labels:'Підписи на мапі',reset:'Очистити прогрес',resetQ:'Видалити всі відповіді та прогрес? Це не можна скасувати.',resetYes:'Так, очистити',cancel:'Скасувати',
  note:'Колесо миші чи два пальці — масштаб, перетягування — рух мапи. Прогрес зберігається в цьому браузері.',
  loadFail:'Не вдалося завантажити дані. Відкрий сторінку через вебсервер (див. README).',
  noVoice:'У системі немає голосу для цієї мови — вимова може бути неточною',
  seat:'резиденція',centerShort:'Центр',
  exploreSub:u=>`Наведи або натисни на ${u}, щоб побачити назву і головне місто.`,
  exploreTip:'Порада: вимкни «Підписи на мапі» і перевір, чи пам’ятаєш назви. Біля назви є кнопка вимови.',
  guessSub:u=>`Натисни на ${u} на мапі або візьми випадкове.`,random:u=>`Випадкове ${u}`,
  guessQ:u=>`Що це за виділене ${u}?`,pickTwo:'Обери назву і будь-який із двох центрів.',pickOne:'Обери назву і головне місто.',
  choose:'— обери —',check:'Перевірити',skip:'Пропустити',right:'Правильно!',almost:'Не зовсім.',next:'Далі →',
  findQ:u=>`Знайди на мапі ${u}:`,cityQ:u=>`Синя точка — місто. Натисни на ${u}, центром якого воно є:`,
  wrong:n=>`Ні, це ${n} (червоним). Правильно — зеленим:`},
pl:{country:'Kraj',lang:'Język interfejsu',mode:'Tryb',map:'Interaktywna mapa',zin:'Przybliż',zout:'Oddal',zreset:'Resetuj powiększenie',
  explore:'Przegląd',guess:u=>`Nazwij ${u}`,find:'Znajdź na mapie',city:u=>`Miasto → ${u}`,
  lgSel:'pytanie / wybrane',lgOk:'opanowane / dobrze',lgPart:'w trakcie nauki',lgBad:'błąd',
  sOk:'dobrze',sAll:'prób',sKnown:'opanowane',progress:'Postęp',progressAria:'Postęp nauki',
  hint:U=>`${U} uznaje się za opanowane po 2 poprawnych odpowiedziach z rzędu.`,
  weakNone:'Na razie bez błędów.',weakAsk:'Do powtórki: ',weakOk:'Brak słabych punktów — tak trzymaj.',
  labels:'Podpisy na mapie',reset:'Wyczyść postęp',resetQ:'Usunąć wszystkie odpowiedzi i postęp? Tego nie da się cofnąć.',resetYes:'Tak, wyczyść',cancel:'Anuluj',
  note:'Kółko myszy lub dwa palce — powiększenie, przeciąganie — przesuwanie mapy. Postęp zapisuje się w tej przeglądarce.',
  loadFail:'Nie udało się wczytać danych. Otwórz stronę przez serwer WWW (zob. README).',
  noVoice:'W systemie brak głosu dla tego języka — wymowa może być niedokładna',
  seat:'siedziba',centerShort:'Stolica',
  exploreSub:u=>`Najedź kursorem na ${u} lub je kliknij, aby zobaczyć nazwę i stolicę.`,
  exploreTip:'Wskazówka: wyłącz „Podpisy na mapie” i sprawdź, czy pamiętasz nazwy. Obok nazwy jest przycisk wymowy.',
  guessSub:u=>`Kliknij ${u} na mapie albo wylosuj.`,random:u=>`Losowe ${u}`,
  guessQ:u=>`Które ${u} jest zaznaczone?`,pickTwo:'Wybierz nazwę i jedną z dwóch stolic.',pickOne:'Wybierz nazwę i stolicę.',
  choose:'— wybierz —',check:'Sprawdź',skip:'Pomiń',right:'Dobrze!',almost:'Nie do końca.',next:'Dalej →',
  findQ:u=>`Znajdź na mapie ${u}:`,cityQ:u=>`Niebieska kropka to miasto. Kliknij ${u}, którego jest stolicą:`,
  wrong:n=>`Nie, to ${n} (na czerwono). Poprawnie — na zielono:`}};
const L=I18N[LANG];
document.documentElement.lang=LANG;
document.querySelectorAll('[data-i]').forEach(el=>{const v=L[el.dataset.i];if(typeof v==='string')el.textContent=v});
document.querySelectorAll('[data-i-aria]').forEach(el=>el.setAttribute('aria-label',L[el.dataset.iAria]));
document.querySelectorAll('#lang button').forEach(b=>{b.setAttribute('aria-pressed',b.dataset.l===LANG);
  b.onclick=()=>{if(b.dataset.l===LANG)return;try{localStorage.setItem(LKEY,b.dataset.l)}catch(e){}location.reload()}});
let COUNTRIES, DATA;
try {
  COUNTRIES = await fetch('data/countries.json').then(r => r.json());
  const want = location.hash.slice(1);
  const cid = COUNTRIES.some(c => c.id === want) ? want : COUNTRIES[0].id;
  DATA = await fetch(`data/${cid}.json`).then(r => r.json());
} catch (e) {
  document.getElementById('panel').innerHTML = `<p>${L.loadFail}</p>`;
  return;
}
const T = DATA.text[LANG], KEY = 'map-trainer:' + DATA.id;
document.title = T.title + ' · Map Trainer';
$('title').textContent = T.title;
const meta = COUNTRIES.find(c => c.id === DATA.id);
if (meta && meta.flag) $('flag').style.background = `linear-gradient(${meta.flag[0]} 50%, ${meta.flag[1]} 50%)`;
if (COUNTRIES.length > 1) {
  const sel = $('country');
  sel.innerHTML = COUNTRIES.map(c => `<option value="${c.id}"${c.id === DATA.id ? ' selected' : ''}>${c.name[LANG]}</option>`).join('');
  sel.hidden = false;
  sel.onchange = () => { location.hash = sel.value; };
}
window.addEventListener('hashchange', () => location.reload());
{const tb=document.querySelectorAll('#tabs button');tb[1].textContent=L.guess(T.unit);tb[3].textContent=L.city(T.unit);}
$('hint').textContent=L.hint(T.Unit);

/* names in the interface language; `alt` is the other-language name shown in grey (Ukrainian UI shows the Polish original).
   Polish region names are lowercase adjectives ("śląskie"); capitalise them when they stand alone. */
const capF=s=>s.replace(/(^|-)(\p{L})/gu,(m,a,b)=>a+b.toUpperCase());
const R=DATA.regions.map(r=>LANG==='pl'
  ?{...r,name:capF(r.local),alt:'',caps:r.caps.map(c=>({...c,name:c.local,alt:''}))}
  :{...r,alt:r.local,caps:r.caps.map(c=>({...c,alt:c.local}))});
const byId=Object.fromEntries(R.map(r=>[r.id,r]));
const NS='http://www.w3.org/2000/svg';
const svg=document.getElementById('map'), panel=document.getElementById('panel');
const BASE={x:-20,y:-20,w:DATA.w+40,h:DATA.h+40};
let vb={...BASE};
const uaSort=(a,b)=>a.localeCompare(b,LANG);
const regOpts=R.map(r=>r.name).sort(uaSort);
const CITIES=R.flatMap(r=>r.caps.map(c=>({...c,rid:r.id})));
const cityOpts=CITIES.map(c=>c.name).sort(uaSort);

/* storage */
const store={get(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
let P=store.get(KEY,{w:{},streak:{},ok:0,all:0});

/* build svg */
svg.innerHTML=`<g id="gR">${R.map(r=>`<path class="reg" id="r-${r.id}" data-id="${r.id}" d="${r.d}"></path>`).join('')}</g>
<g id="gD">${CITIES.map((c,i)=>`<circle class="dot" id="c-${i}" cx="${c.x}" cy="${c.y}" r="4"/>`).join('')}</g>
<g id="gT"></g><g id="gL"></g>`;
const gL=document.getElementById('gL'), gT=document.getElementById('gT');
const regEl=id=>document.getElementById('r-'+id);

let U=1; // svg units per screen px
function applyVB(){
  svg.setAttribute('viewBox',`${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
  const ctm=svg.getScreenCTM(); U=ctm?1/ctm.a:1;
  gL.setAttribute('font-size',13*U);
  document.querySelectorAll('.dot').forEach(d=>d.setAttribute('r',(d.classList.contains('tgt')?7:4)*U));
  document.querySelectorAll('.ring').forEach(d=>d.setAttribute('r',10*U));
}
function clampVB(){
  vb.w=Math.min(BASE.w,Math.max(BASE.w/8,vb.w)); vb.h=vb.w*BASE.h/BASE.w;
  vb.x=Math.min(BASE.x+BASE.w-vb.w*.3,Math.max(BASE.x-vb.w*.7,vb.x));
  vb.y=Math.min(BASE.y+BASE.h-vb.h*.3,Math.max(BASE.y-vb.h*.7,vb.y));
}
function toSvg(cx,cy){const p=svg.createSVGPoint();p.x=cx;p.y=cy;return p.matrixTransform(svg.getScreenCTM().inverse())}
function zoomAt(sx,sy,k){const nw=vb.w/k;const f=nw/vb.w;vb.x=sx-(sx-vb.x)*f;vb.y=sy-(sy-vb.y)*f;vb.w=nw;vb.h=nw*BASE.h/BASE.w;clampVB();applyVB()}
function zoomCenter(k){zoomAt(vb.x+vb.w/2,vb.y+vb.h/2,k)}
svg.addEventListener('wheel',e=>{e.preventDefault();const p=toSvg(e.clientX,e.clientY);zoomAt(p.x,p.y,e.deltaY<0?1.2:1/1.2)},{passive:false});
document.getElementById('zin').onclick=()=>zoomCenter(1.4);
document.getElementById('zout').onclick=()=>zoomCenter(1/1.4);
document.getElementById('zreset').onclick=()=>{vb={...BASE};applyVB()};

const ptrs=new Map(); let down=null, pinch=null;
svg.addEventListener('pointerdown',e=>{
  svg.setPointerCapture(e.pointerId);
  ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(ptrs.size===1){const t=e.target.closest&&e.target.closest('.reg');down={x:e.clientX,y:e.clientY,id:t?t.dataset.id:null,moved:false}}
  else if(ptrs.size===2){const [a,b]=[...ptrs.values()];pinch={d:Math.hypot(a.x-b.x,a.y-b.y)};if(down)down.moved=true}
});
svg.addEventListener('pointermove',e=>{
  if(!ptrs.has(e.pointerId)){hover(e);return}
  const prev=ptrs.get(e.pointerId); ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(ptrs.size===2&&pinch){const [a,b]=[...ptrs.values()];const d=Math.hypot(a.x-b.x,a.y-b.y);const m=toSvg((a.x+b.x)/2,(a.y+b.y)/2);zoomAt(m.x,m.y,d/pinch.d);pinch.d=d;return}
  if(down&&ptrs.size===1){
    if(Math.hypot(e.clientX-down.x,e.clientY-down.y)>6){down.moved=true;svg.classList.add('drag')}
    if(down.moved){vb.x-=(e.clientX-prev.x)*U;vb.y-=(e.clientY-prev.y)*U;clampVB();applyVB()}
  }
});
function up(e){
  ptrs.delete(e.pointerId); svg.classList.remove('drag');
  if(ptrs.size<2)pinch=null;
  if(ptrs.size===0&&down){if(!down.moved&&down.id)onRegion(down.id);down=null}
}
svg.addEventListener('pointerup',up);svg.addEventListener('pointercancel',up);
svg.addEventListener('pointerleave',()=>{if(mode==='explore'&&!locked)renderExplore(null)});
new ResizeObserver(applyVB).observe(svg);

/* labels & marks */
/* labels: on by default in the overview, off in quizzes (they would give the answer away); remembered per mode */
const labelsOn={explore:true};
let showAll=false, revealed=new Set();
function drawLabels(){
  const ids=showAll?R.map(r=>r.id):[...revealed];
  gL.innerHTML=ids.map(id=>{const r=byId[id];return `<text class="lab" x="${r.lx}" y="${r.ly}">${r.name}</text>`+
    (showAll||mode!=='explore'?r.caps.map(c=>`<text class="lab cty" x="${c.x}" y="${c.y-9}" dy="-0.2em">${c.name.replace(/\s*\(.*\)/,'')}</text>`).join(''):'')}).join('');
}
document.getElementById('labels').onchange=e=>{showAll=labelsOn[mode]=e.target.checked;drawLabels()};
function clearMarks(){R.forEach(r=>regEl(r.id).classList.remove('sel','ok','part','bad','now'))}
/* map colours come from saved progress, so they survive a page refresh:
   2+ right in a row = learned (green), 1 right = learning (light green), last answer wrong = red */
function paintProgress(){clearMarks();R.forEach(r=>{const s=P.streak[r.id]||0, last=P.last?.[r.id];
  const c=s>=2?'ok':s===1?'part':(last===0||(last===undefined&&W(r.id)>3))?'bad':null; if(c)regEl(r.id).classList.add(c)})}
function mark(id,c,now){const el=regEl(id);el.classList.remove('sel','ok','part','bad','now');if(c){el.classList.add(c);if(now||c==='sel')el.classList.add('now');el.parentNode.appendChild(el)}}
function target(i){document.querySelectorAll('.dot').forEach(d=>d.classList.remove('tgt'));gT.innerHTML='';
  if(i==null){applyVB();return}const c=CITIES[i];document.getElementById('c-'+i).classList.add('tgt');
  gT.innerHTML=`<circle class="ring" cx="${c.x}" cy="${c.y}" r="10"/>`;applyVB()}

/* progress: weight per region, higher = asked more often */
const W=id=>P.w[id]??3;
function record(id,ok){
  P.all++; if(ok)P.ok++;
  P.w[id]=ok?Math.max(1,W(id)-1):Math.min(8,W(id)+2);
  P.streak[id]=ok?(P.streak[id]||0)+1:0; (P.last=P.last||{})[id]=ok?1:0;
  store.set(KEY,P); stats();
}
function pickWeighted(exclude){
  const pool=R.filter(r=>r.id!==exclude); let t=pool.reduce((s,r)=>s+W(r.id),0)*Math.random();
  for(const r of pool){t-=W(r.id);if(t<=0)return r.id} return pool[0].id;
}
function stats(){
  const known=R.filter(r=>(P.streak[r.id]||0)>=2).length;
  document.getElementById('sOk').textContent=P.ok;document.getElementById('sAll').textContent=P.all;
  /* bar = partial credit: each region needs 2 correct in a row, so 1 correct already fills half of its share */
  const pts=R.reduce((s,r)=>s+Math.min(2,P.streak[r.id]||0),0), pct=Math.round(pts/(R.length*2)*100);
  document.getElementById('sKnown').textContent=known+'/'+R.length;document.getElementById('sBar').style.width=pct+'%';
  document.getElementById('sBarWrap').setAttribute('aria-valuenow',pct);document.getElementById('sPct').textContent=pct+'%';
  const weak=R.filter(r=>W(r.id)>3).sort((a,b)=>W(b.id)-W(a.id)).slice(0,4).map(r=>r.name);
  document.getElementById('weak').textContent=weak.length?L.weakAsk+weak.join(', ')+'.':(P.all?L.weakOk:L.weakNone);
}
const rBox=$('resetBox'), rBtn=$('resetP');
rBtn.onclick=()=>{rBox.hidden=false;rBtn.hidden=true;$('resetNo').focus()};
$('resetNo').onclick=()=>{rBox.hidden=true;rBtn.hidden=false;rBtn.focus()};
$('resetYes').onclick=()=>{P={w:{},streak:{},last:{},ok:0,all:0};store.set(KEY,P);stats();setMode(mode);rBox.hidden=true;rBtn.hidden=false;rBtn.focus()};

/* speech */
const canSay='speechSynthesis' in window;
/* pick a voice for the country's language explicitly; without one the browser may read with a wrong accent or stay silent */
let voice=null;
const findVoice=()=>{if(!canSay)return;const vs=speechSynthesis.getVoices(),l=DATA.lang.toLowerCase(),b=l.split('-')[0];
  voice=vs.find(v=>v.lang.toLowerCase().replace('_','-')===l)||vs.find(v=>v.lang.toLowerCase().startsWith(b))||null};
if(canSay){findVoice();speechSynthesis.addEventListener?.('voiceschanged',findVoice)}
function say(t,btn){if(!canSay)return;try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.lang=DATA.lang;if(voice)u.voice=voice;u.rate=.9;
  if(btn){btn.classList.add('on');u.onend=u.onerror=()=>btn.classList.remove('on')}
  speechSynthesis.speak(u);
  if(!voice&&btn&&speechSynthesis.getVoices().length){btn.title=L.noVoice}}catch(e){}}
const SPK='<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M3 9v6h4l5 4V5L7 9H3zm13.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z"/></svg>';
const sayBtn=r=>canSay?`<button class="btn sm spk" data-say="${DATA.say?DATA.say+' ':''}${r.local}. ${r.caps.map(c=>c.local).join(', ')}">${SPK}${T.sayLabel}</button>`:'';
panel.addEventListener('click',e=>{const b=e.target.closest('[data-say]');if(b)say(b.dataset.say,b)});

const alt=x=>x.alt?` <span class="pl" lang="pl">${x.alt}</span>`:'';
const seat=c=>T.seats?.[c.seat]||c.seat;
const opts=(arr,ph)=>`<option value="">${ph}</option>`+arr.map(v=>`<option>${v}</option>`).join('');

/* modes */
let mode='explore', locked=null, st={};
function setMode(m){
  mode=m; showAll=!!labelsOn[m]; $('labels').checked=showAll; locked=null; st={}; revealed.clear(); paintProgress(); target(null);
  document.querySelectorAll('#tabs button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.m===m));
  ({explore:()=>renderExplore(null),guess:()=>renderGuess(pickWeighted()),find:nextFind,city:nextCity})[m]();
  drawLabels();
}
document.getElementById('tabs').onclick=e=>{const b=e.target.closest('button');if(b)setMode(b.dataset.m)};

function hover(e){if(mode!=='explore'||locked)return;const t=e.target.closest&&e.target.closest('.reg');renderExplore(t?t.dataset.id:null)}
function renderExplore(id){
  if(st.hov===id&&id)return; st.hov=id;
  if(!id){panel.innerHTML=`<div class="qh"><h2>${L.explore}</h2><p class="sub">${L.exploreSub(T.unit)}</p></div><p class="note" style="margin-top:6px">${L.exploreTip}</p>`;return}
  const r=byId[id];
  panel.innerHTML=`<div class="qh"><p class="big" style="margin:0">${r.name}</p>${alt(r)}</div><div class="qh" style="margin-top:4px"><span>${L.centerShort}: ${r.caps.map(c=>`<b>${c.name}</b>${alt(c)}${c.seat?` <small class="pl">(${seat(c)})</small>`:''}`).join(' · ')}</span></div><div class="row">${sayBtn(r)}</div>`;
}

function renderGuess(id){
  paintProgress();
  if(!id){panel.innerHTML=`<div class="qh"><h2>${L.guess(T.unit)}</h2><p class="sub">${L.guessSub(T.unit)}</p></div><div class="row"><button class="btn pri" id="rnd">${L.random(T.unit)}</button></div>`;
    document.getElementById('rnd').onclick=()=>renderGuess(pickWeighted(st.cur));return}
  st.cur=id; mark(id,'sel');
  const r=byId[id];
  panel.innerHTML=`<div class="qh"><h2>${L.guessQ(T.unit)}</h2><p class="sub">${r.caps.length>1?L.pickTwo:L.pickOne}</p></div>
  <div class="form"><div><label for="sR">${T.Unit}</label><select id="sR">${opts(regOpts,L.choose)}</select></div>
  <div><label for="sC">${T.center}</label><select id="sC">${opts(cityOpts,L.choose)}</select></div>
  <div class="row" id="btns"><button class="btn pri" id="chk" disabled>${L.check}</button><button class="btn" id="skip">${L.skip}</button></div></div><div id="fb"></div>`;
  const sR=document.getElementById('sR'),sC=document.getElementById('sC'),chk=document.getElementById('chk');
  const en=()=>chk.disabled=!(sR.value&&sC.value); sR.onchange=en; sC.onchange=en;
  document.getElementById('skip').onclick=()=>renderGuess(pickWeighted(id));
  chk.onclick=()=>{
    const okR=sR.value===r.name, okC=r.caps.some(c=>c.name===sC.value), ok=okR&&okC;
    sR.className=okR?'ok':'bad'; sC.className=okC?'ok':'bad'; sR.disabled=sC.disabled=true;
    record(id,ok); mark(id,ok?'ok':'bad',true); revealed.add(id); drawLabels();
    document.getElementById('fb').innerHTML=`<div class="fbrow"><div class="fb ${ok?'ok':'bad'}">${ok?L.right:L.almost} <b>${r.name}</b>${r.alt?` (${r.alt})`:''} — ${r.caps.map(c=>c.name).join(' / ')}</div><div class="row">${sayBtn(r)}<button class="btn pri" id="nx">${L.next}</button></div></div>`;
    document.getElementById('btns').remove();
    document.getElementById('nx').onclick=()=>renderGuess(pickWeighted(id)); document.getElementById('nx').focus();
  };
}

function nextFind(){
  paintProgress();
  st.cur=pickWeighted(st.cur); st.answered=false; const r=byId[st.cur];
  panel.innerHTML=`<p class="sub">${L.findQ(T.unit)}</p><div class="qh"><p class="big" style="margin:0">${r.name}</p>${alt(r)}</div><div id="fb"></div>`;
}
function nextCity(){
  paintProgress();
  const rid=pickWeighted(st.cur); st.cur=rid; st.answered=false;
  const list=CITIES.map((c,i)=>i).filter(i=>CITIES[i].rid===rid), ci=list[Math.floor(Math.random()*list.length)]; target(ci); const c=CITIES[ci];
  panel.innerHTML=`<p class="sub">${L.cityQ(T.unit)}</p><div class="qh"><p class="big" style="margin:0">${c.name}</p>${alt(c)}</div><div id="fb"></div>`;
}
function answerClick(id){
  if(st.answered)return; st.answered=true; const ok=id===st.cur, r=byId[st.cur];
  record(st.cur,ok);
  if(ok)mark(st.cur,'ok',true); else{mark(id,'bad',true);mark(st.cur,'ok',true)} revealed.add(st.cur); drawLabels();
  document.getElementById('fb').innerHTML=`<div class="fbrow"><div class="fb ${ok?'ok':'bad'}">${ok?L.right:L.wrong(byId[id].name)} <b>${r.name}</b> — ${r.caps.map(c=>c.name).join(' / ')}</div><div class="row">${sayBtn(r)}<button class="btn pri" id="nx">${L.next}</button></div></div>`;
  const nx=document.getElementById('nx'); nx.onclick=()=>mode==='find'?nextFind():nextCity(); nx.focus();
}

function onRegion(id){
  if(mode==='explore'){locked=locked===id?null:id;paintProgress();if(locked)mark(id,'sel');st.hov=undefined;renderExplore(locked||id)}
  else if(mode==='guess'){if(!document.getElementById('nx')&&st.cur===id)return;renderGuess(id)}
  else answerClick(id);
}
document.addEventListener('keydown',e=>{if(e.key==='+'||e.key==='=')zoomCenter(1.3);if(e.key==='-')zoomCenter(1/1.3);if(e.key==='0'){vb={...BASE};applyVB()}});

stats(); setMode('explore'); applyVB();
})();
