// Chrome réel isolé : node tests/final_browser_qa.mjs avant|apres.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const phase=process.argv[2]||'apres',dir='livrables/format-son-ux/finalisation';
const downloadBatch=Date.now().toString(36);
const url=process.env.BILLBOARD_URL||'http://127.0.0.1:8505',port=process.env.BILLBOARD_CDP_PORT||9229;
await fs.mkdir(dir,{recursive:true});
const tabs=await(await fetch(`http://127.0.0.1:${port}/json`)).json();
const tab=tabs.find(t=>t.type==='page'&&t.url.startsWith(url));assert(tab,'Chrome de test doit ouvrir le serveur 8505.');
const ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let id=0;const pending=new Map();
ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.id){pending.get(d.id)?.(d);pending.delete(d.id);}};
const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,d=>d.error?reject(d.error):resolve(d.result));ws.send(JSON.stringify({id:n,method,params}));});
const evaluate=async expression=>{const d=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(d.exceptionDetails)throw Error(JSON.stringify(d.exceptionDetails));return d.result.value;};
const settle=()=>new Promise(r=>setTimeout(r,450));
const wait=async(expression,label)=>{const end=Date.now()+30000;while(Date.now()<end){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,150));}throw Error('Délai : '+label);};
const shot=async name=>{const d=await send('Page.captureScreenshot',{format:'png'});await fs.writeFile(`${dir}/${phase}-${name}.png`,Buffer.from(d.data,'base64'));};
const body=()=>evaluate(`document.querySelector('[data-testid="stMain"]').innerText`);
const click=async selector=>{await wait(`Boolean(document.querySelector(${JSON.stringify(selector)}))`,selector);await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);await settle();};
const pointer=async selector=>{
 await wait(`Boolean(document.querySelector(${JSON.stringify(selector)}))`,selector);
 await evaluate(`document.querySelector(${JSON.stringify(selector)}).scrollIntoView({block:'nearest',inline:'center'})`);await settle();
 const p=await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)}),r=e.getBoundingClientRect(),h=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {x:r.x+r.width/2,y:r.y+r.height/2,hit:e===h||e.contains(h)};})()`);assert(p.hit,'Bouton masqué : '+selector);
 await send('Input.dispatchMouseEvent',{type:'mousePressed',x:p.x,y:p.y,button:'left',clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:p.x,y:p.y,button:'left',clickCount:1});await settle();
};
const radio=async(key,text)=>{await evaluate(`[...document.querySelectorAll('.st-key-${key} label')].find(e=>e.innerText===${JSON.stringify(text)}).click()`);await settle();};
const select=async(key,text)=>{await click(`.st-key-${key} input`);await send('Input.insertText',{text});await settle();await evaluate(`(()=>{const a=[...document.querySelectorAll('[role="option"]')];(a.find(e=>e.innerText===${JSON.stringify(text)})||a.find(e=>e.innerText.includes(${JSON.stringify(text)}))).click();})()`);await settle();};
const sidebar=async open=>{await evaluate(`(()=>{const s=document.querySelector('[data-testid="stSidebar"]');if(s?.getAttribute('aria-expanded')!==${JSON.stringify(String(open))}){const e=document.querySelector(${JSON.stringify(open?'[data-testid="stExpandSidebarButton"]':'[data-testid="stSidebarCollapseButton"]')});(e?.querySelector('button')||e)?.click();}})()`);await settle();};
const groups=[['summary'],['format_trend','duration','sound','instrumentation','genres'],['origins','map'],['ages','formats','teams','reuse'],['data_a','data_b']];
const go=async route=>{const g=groups.findIndex(a=>a.includes(route));const active=await evaluate(`Boolean(document.querySelector('.st-key-group_${g} button[kind="primary"]'))`);const press=phase==='avant'?click:pointer;if(!active)await press(`.st-key-group_${g} button`);if(route!=='summary')await press(`.st-key-nav_${route} button`);await wait(`Boolean(document.querySelector('h1'))`,'page');};
const key=async name=>{const code={Enter:13,ArrowRight:39,Backspace:8}[name];await send('Input.dispatchKeyEvent',{type:'keyDown',key:name,code:name,windowsVirtualKeyCode:code,text:name==='Enter'?'\r':undefined});await send('Input.dispatchKeyEvent',{type:'keyUp',key:name,code:name,windowsVirtualKeyCode:code});await settle();};
// Reprendre uniquement les observations manquantes après un correctif du script,
// avec l'application inchangée ; les scénarios déjà réussis restent dans le rapport.
const reports=process.argv.includes('--resume')?JSON.parse(await fs.readFile(`${dir}/${phase}-chrome.json`,'utf8')):[];
const completed=(scenario,width)=>reports.some(r=>r.scenario===scenario&&r.width===width);
const record=async(scenario,route,width)=>{
 await sidebar(width>=768);await evaluate(`window.scrollTo(0,0);document.querySelector('[data-testid="stMain"]').scrollTo(0,0)`);await settle();
 const m=await evaluate(`(()=>{const main=document.querySelector('[data-testid="stMain"]'),p=document.querySelector('.st-key-primary_nav'),s=document.querySelector('.st-key-secondary_nav'),h=document.querySelector('h1'),n=document.querySelector('.st-key-dashboard_navigation')||document.querySelector('.st-key-format_navigation');return {title:h.innerText,width:innerWidth,height:innerHeight,pageWidth:main.clientWidth,scrollWidth:main.scrollWidth,scrollHeight:main.scrollHeight,clientHeight:main.clientHeight,primary:p.getBoundingClientRect().toJSON(),secondary:s?.getBoundingClientRect().toJSON()||null,navHeight:n?.getBoundingClientRect().height,navPosition:n?getComputedStyle(n.parentElement).position:null,titleTop:h.getBoundingClientRect().top,errors:[...document.querySelectorAll('[data-testid="stException"]')].map(e=>e.innerText),groups:[...p.querySelectorAll('button')].map(e=>e.innerText),subpages:s?[...s.querySelectorAll('button')].map(e=>e.innerText):[],kpis:[...document.querySelectorAll('.kpi-value')].map(e=>{const r=document.createRange();r.selectNodeContents(e);return {text:e.innerText,lines:r.getClientRects().length,width:e.clientWidth,scrollWidth:e.scrollWidth};}),figures:[...document.querySelectorAll('.js-plotly-plot')].map(e=>({height:e.getBoundingClientRect().height,width:e.getBoundingClientRect().width,plotWidth:e._fullLayout._size.w,data:e.data,layout:e.layout})),downloads:document.querySelectorAll('[data-testid="stDownloadButton"]').length};})()`);
 Object.assign(m,{scenario,route});assert.equal(m.width,width);assert.equal(m.errors.length,0);assert(m.scrollWidth<=m.pageWidth+1,scenario+' débordement horizontal');
 for(const f of m.figures)assert(f.plotWidth>=65,'Graphique trop comprimé');
 if(phase==='apres'){
  assert.equal(m.groups[0],'Explorer les n°1');assert.equal(m.navPosition,'sticky');
  assert(m.titleTop>=(m.secondary||m.primary).bottom-1,'Titre sous navigation');
  if(route==='summary'){
   assert.equal(m.title,'Quels repères offrent les titres n°1 ?');assert.equal(m.secondary,null);assert(m.titleTop-m.primary.bottom<40,'Espace de sous-navigation fantôme');
   const text=await body();for(const t of ['1 · Comment les caractéristiques','2 · D’où viennent','3 · Comment les profils','Samples et reprises'])assert(text.includes(t));
   assert(!text.includes('Repères chiffrés'));assert.equal(m.figures.length,0);
   assert.equal(await evaluate(`document.querySelectorAll('.journey').length`),3);assert.equal(await evaluate(`document.querySelectorAll('.journey li').length`),11);
  }
  if(groups[1].includes(route))assert.equal(m.figures.length,1,'Un seul graphique Format');
  if(route.startsWith('data_'))assert(m.downloads>0,'Export CSV disponible');
  if(route==='duration')assert(m.kpis.every(k=>k.lines===1&&k.scrollWidth<=k.width+1),'Valeur KPI sur plusieurs lignes');
  assert(!/Historique\s*:\s*1958|indépendant des années comparées|Les années comparées ne bornent pas cet historique/.test(await body()),'Phrase historique récurrente');
 }
 await shot(`${scenario}-${width}-haut`);
 await evaluate(`document.querySelector('[data-testid="stMain"]').scrollTo(0,10000)`);await settle();
 await send('Input.dispatchMouseEvent',{type:'mouseWheel',x:width-35,y:m.height-170,deltaX:0,deltaY:600});await settle();
 m.scrolled=await evaluate(`(()=>{const main=document.querySelector('[data-testid="stMain"]'),p=document.querySelector('.st-key-primary_nav'),s=document.querySelector('.st-key-secondary_nav');return {scrollTop:main.scrollTop,windowY:window.scrollY,primary:p.getBoundingClientRect().toJSON(),secondary:s?.getBoundingClientRect().toJSON()||null,scrollWidth:main.scrollWidth,clientWidth:main.clientWidth};})()`);
 if(phase==='apres'){
  if(m.scrolled.scrollTop>2)assert(Math.abs(m.scrolled.primary.top-(width<768?72:76))<=2,'Navigation défilée');
  else assert(Math.abs(m.scrolled.primary.top-m.primary.top)<=2,'Navigation déplacée sans défilement de page');
  assert(m.scrolled.primary.bottom<m.height,'Navigation hors écran');
  if(m.scrolled.secondary)assert(m.scrolled.secondary.top>=m.scrolled.primary.bottom-1,'Deux barres superposées');
  assert(m.scrolled.scrollWidth<=m.scrolled.clientWidth+1);
 }
 await shot(`${scenario}-${width}-defilement`);reports.push(m);await fs.writeFile(`${dir}/${phase}-chrome.json`,JSON.stringify(reports,null,2));console.log(`${phase} · ${scenario} · ${width} : ${m.scrollHeight}px ; sticky ${m.scrolled.primary.top.toFixed(1)}px.`);
};
try{
 await send('Page.reload',{ignoreCache:true});await wait(`Boolean(document.querySelector('.st-key-group_0 button'))`,'Streamlit');
 for(const width of [1440,390,320]){
  if(completed('persistance-filtres',width))continue;
  await send('Emulation.setDeviceMetricsOverride',{width,height:width===1440?900:844,deviceScaleFactor:1,mobile:width<768});await settle();
  if(phase==='tables'){
   const downloads=`${process.cwd()}/${dir}/downloads/${downloadBatch}/${width}`;await fs.mkdir(downloads,{recursive:true});
   await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
   for(const route of ['data_a','data_b']){
    await go(route);await record(route+'-export',route,width);
    const r=await evaluate(`document.querySelector('.titles-scroll').getBoundingClientRect().toJSON()`);
    const top=await evaluate(`document.querySelector('.st-key-primary_nav').getBoundingClientRect().top`);
    await send('Input.dispatchMouseEvent',{type:'mouseWheel',x:r.x+r.width/2,y:r.y+r.height/2,deltaX:0,deltaY:650});await settle();
    const scroll=await evaluate(`document.querySelector('.titles-scroll').scrollTop`);assert(scroll>0,'Tableau réellement défilé');
    assert(Math.abs(top-await evaluate(`document.querySelector('.st-key-primary_nav').getBoundingClientRect().top`))<1,'Navigation stable pendant le défilement du tableau');
    assert(await evaluate(`(()=>{const a=document.querySelector('.st-key-export_${route} button').getBoundingClientRect(),b=document.querySelector('.st-key-back_top button').getBoundingClientRect();return a.right<=b.left||b.right<=a.left||a.bottom<=b.top||b.bottom<=a.top;})()`),'Haut recouvre le CSV');
    await shot(route+'-table-defilee-'+width);
    const files=await fs.readdir(downloads);await pointer(`.st-key-export_${route} button`);
    let added=[];for(let n=0;n<40;n++){added=(await fs.readdir(downloads)).filter(f=>!files.includes(f)&&f.endsWith('.csv'));if(added.length)break;await new Promise(r=>setTimeout(r,150));}
    assert.equal(added.length,1,'Téléchargement CSV réel');reports.at(-1).tableScrollTop=scroll;reports.at(-1).downloadFile=downloadBatch+'/'+width+'/'+added[0];
    await fs.writeFile(`${dir}/${phase}-chrome.json`,JSON.stringify(reports,null,2));
   }
   continue;
  }
  const routes=phase==='avant'?['summary','duration','origins','ages','data_a']:groups.flat();
  for(const route of routes){if(completed(route,width))continue;await go(route);await record(route,route,width);}
  if(phase==='avant')continue;
  if(!completed('genres-historique',width)){
  await go('duration');await radio('duration_view','Introduction');await record('introduction','duration',width);
  await radio('duration_view','Évolution');await select('duration_metric','Part de l’introduction');await record('ratio-historique','duration',width);
  await go('sound');await select('sonic','Niveau sonore');await radio('sound_view','Évolution');await record('son-historique','sound',width);
  await go('instrumentation');await radio('instrument_view','Présence');await record('presence','instrumentation',width);
  await go('genres');await radio('genres_view','Historique');await select('genre_history','Rock');await record('genres-historique','genres',width);
  }
  // Navigation clavier réelle depuis le bas de la page, puis filtres conservés.
  if(!completed('accueil-clavier',width)){
  await evaluate(`document.querySelector('.st-key-group_0 button').scrollIntoView({block:'nearest',inline:'center'});document.querySelector('.st-key-group_0 button').focus({preventScroll:true})`);await key('Enter');
  assert((await body()).includes('Quels repères offrent les titres n°1 ?'));await record('accueil-clavier','summary',width);
  }
  await sidebar(true);await select('genre','Pop');await select('decade_a','1980 – 1989');await sidebar(width>=768);
  await go('map');await select('map_country','Porto Rico');await go('teams');await radio('team_role','Producteurs');
  await go('data_b');await pointer('.st-key-search_data_b input');await send('Input.insertText',{text:'cardigan'});await key('Enter');
  assert.equal(await evaluate(`document.querySelectorAll('.titles-table tbody tr').length`),1);
  await go('sound');await select('sonic','Énergie');await radio('sound_view','Évolution');await go('summary');
  const selections=[];
  for(const [group,route,expected] of [[1,'sound','Énergie'],[2,'map','Porto Rico'],[3,'teams','Producteurs'],[4,'data_b','cardigan']]){
   await pointer(`.st-key-group_${group} button`);assert(await evaluate(`Boolean(document.querySelector('.st-key-nav_${route} button[kind="primary"]'))`),'Sous-page mémorisée');
   assert((await body()).includes(expected)||await evaluate(`document.querySelector('.st-key-search_data_b input')?.value==='cardigan'`),'Choix mémorisé');
   const filters=await evaluate(`({genre:document.querySelector('.st-key-genre').textContent,years:document.querySelector('.st-key-decade_a').textContent})`);
   assert(filters.genre.includes('Pop')&&filters.years.includes('1980'),'Filtres globaux conservés');
   selections.push({group,route,expected,filters});await go('summary');
  }
  await go('data_b');await record('persistance-filtres','data_b',width);reports.at(-1).remembered=selections;
  await fs.writeFile(`${dir}/${phase}-chrome.json`,JSON.stringify(reports,null,2));
  // Défauts restaurés avant les mesures de la largeur suivante.
  await sidebar(true);await select('genre','Tous les genres');await select('decade_a','2000 – 2009');await sidebar(width>=768);
  await go('data_b');await pointer('.st-key-search_data_b input');await evaluate(`document.querySelector('.st-key-search_data_b input').select()`);await key('Backspace');await key('Enter');
  await go('map');await select('map_country','Tous');await go('teams');await radio('team_role','Auteurs');
  await go('duration');await radio('duration_view','Durée');await go('sound');await select('sonic','Tempo');await radio('sound_view','Distribution');
  await go('instrumentation');await radio('instrument_view','Rôle central');await go('genres');await radio('genres_view','Comparer les années');await go('summary');
 }
 console.log(`${phase} : ${reports.length} observations Chrome réussies.`);
}catch(error){console.error(error);await shot('echec');await fs.writeFile(`${dir}/${phase}-echec.txt`,String(error)+'\n'+await body());process.exitCode=1;}finally{ws.close();}
