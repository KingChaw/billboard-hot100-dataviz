// Vérification visuelle locale ; nécessite Chrome --remote-debugging-port=9226.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const pages=await (await fetch('http://127.0.0.1:9226/json')).json();
const page=pages.find(p=>p.type==='page'&&p.url.startsWith('http://127.0.0.1:8502'));
if(!page) throw Error('Ouvrir http://127.0.0.1:8502 dans le Chrome de vérification.');
const ws=new WebSocket(page.webSocketDebuggerUrl);
await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let id=0;const pending=new Map();
ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.id){pending.get(d.id)?.(d);pending.delete(d.id)}};
const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,d=>d.error?reject(d.error):resolve(d.result));ws.send(JSON.stringify({id:n,method,params}))});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
const settle=()=>new Promise(r=>setTimeout(r,700));
const click=async selector=>{await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);await settle();};
const radio=async(key,text)=>{await evaluate(`[...document.querySelectorAll('.st-key-${key} label')].find(e=>e.innerText===${JSON.stringify(text)}).click()`);await settle();};
const select=async(key,text)=>{
 await click(`.st-key-${key} input`);
 await send('Input.insertText',{text}); await settle();
 const options=await evaluate(`[...document.querySelectorAll('[role="option"]')].map(e=>e.innerText)`);
 const chosen=options.find(e=>e===text)||options.find(e=>e.includes(text));
 if(!chosen)throw Error(`Option absente: ${key} ${text}: ${options}`);
 await evaluate(`[...document.querySelectorAll('[role="option"]')].find(e=>e.innerText===${JSON.stringify(chosen)}).click()`);await settle();
};
const routeGroups=[['summary'],['format_trend','duration','intro','sound','central','presence','genres'],['origin_trend','origins','map'],['ages','formats','collabs','teams','reuse'],['data_a','data_b']];
const go=async route=>{
 const group=routeGroups.findIndex(routes=>routes.includes(route));
 await click(`.st-key-group_${group} button`);
 await click(`.st-key-nav_${route} button`);
};
const dimensions=async(width,height)=>{await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<768});await settle();};
const shot=async name=>{const s=await send('Page.captureScreenshot',{format:'png'});await fs.writeFile(`livrables/captures/${name}.png`,Buffer.from(s.data,'base64'));};
const measure=()=>evaluate(`(()=>{const m=document.querySelector('[data-testid="stMain"]');const f=document.querySelector('.js-plotly-plot');return {title:document.querySelector('h1')?.innerText,width:innerWidth,height:innerHeight,mainWidth:m.clientWidth,scrollWidth:m.scrollWidth,scrollHeight:m.scrollHeight,scrollTop:m.scrollTop,charts:document.querySelectorAll('.js-plotly-plot').length,errors:[...document.querySelectorAll('[data-testid="stException"]')].map(e=>e.innerText),chart:f?f.getBoundingClientRect().toJSON():null}})()`);
const mode=process.argv[2]||'suite';
try {
 await send('Page.bringToFront');
 await dimensions(1440,900);
 // Chaque parcours repart d’une session neuve, avec la référence 2020–2024.
 await send('Page.reload',{ignoreCache:true});await new Promise(r=>setTimeout(r,1700));
 const reports=[];
 if(mode==='scenario'){
  await select('decade_a','2010 – 2019');
  await click('.st-key-shortcut_intro button');
  assert((await evaluate('document.body.innerText')).includes('10 à 11 s'));
  await shot('apres-intro-1440');
  // Survol réel de la boîte B : relever la lisibilité des statistiques.
  const rect=await evaluate(`document.querySelectorAll('.scatterlayer .trace')[1].querySelector('.point').getBoundingClientRect().toJSON()`);
  await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:rect.x+rect.width/2,y:rect.y+rect.height/2});await settle();
  const hover=await evaluate(`document.querySelector('.hoverlayer')?.textContent`);assert(hover.includes('Médiane'));assert(hover.includes('7–18'));reports.push({hover});
  await shot('apres-intro-infobulle');
  await evaluate(`[...document.querySelectorAll('[data-testid="stMain"] details summary')].find(e=>e.innerText.includes('Titres associés')).click()`);await settle();
  await radio('titles_period_intro','2020 – 2024');
  await click('.st-key-examples_intro input');
  const rows=await evaluate(`[...document.querySelectorAll('.titles-table tbody tr')].map(r=>[...r.querySelectorAll('td')].map(c=>c.innerText))`);
  assert.deepEqual(rows.map(r=>r[0].trim()),['cardigan','Life Goes On','Like That']);
  await evaluate(`document.querySelector('.titles-scroll').scrollIntoView({block:'center'})`);await settle();
  await shot('apres-intro-exemples');
  await fs.mkdir('/private/tmp/billboard-v4-download',{recursive:true});
  await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:'/private/tmp/billboard-v4-download'});
  await click('[data-testid="stDownloadButton"] button');
  const files=await fs.readdir('/private/tmp/billboard-v4-download');
  const downloaded=await fs.readFile('/private/tmp/billboard-v4-download/'+files.find(x=>x.endsWith('.csv')),'utf8');
  reports.push({rows,downloaded});
  // Le bouton et un changement de page réinitialisent le défilement principal.
  await click('.st-key-back_top button');
  assert.equal((await measure()).scrollTop,0);
  await evaluate(`document.querySelector('[data-testid="stMain"]').scrollTo(0,9999)`);
  await go('teams');assert.equal((await measure()).scrollTop,0);
  // Clavier : focus visible puis activation native d’une aide de légende.
  await go('origins');
  await evaluate(`document.querySelector('.category-legend summary').focus()`);
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',text:'\r',windowsVirtualKeyCode:13});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await settle();
  assert(await evaluate(`document.querySelector('.category-legend details').open`));
  reports.push({keyboardLegend:true});
  await dimensions(390,844);
  await send('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:1});
  const sr=await evaluate(`document.querySelector('.category-legend summary').getBoundingClientRect().toJSON()`);
  await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:sr.x+sr.width/2,y:sr.y+sr.height/2}]});
  await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await settle();
  assert.equal(await evaluate(`document.querySelector('.category-legend details').open`),false);
  reports.push({touchLegend:true});
 } else {
  const routes=['summary','format_trend','duration','intro','sound','central','presence','genres','origin_trend','origins','map','ages','formats','collabs','teams','reuse','data_a','data_b'];
  for(const width of [1440,390,320]){
   await dimensions(width,width===1440?900:844);
   for(const route of routes){
    await go(route);const m=await measure();reports.push({route,...m});
    if(route==='format_trend' && width<400)assert.equal(await evaluate(`document.querySelector('.js-plotly-plot').layout.xaxis.tickangle`),-55);
    assert.equal(m.errors.length,0);assert(m.scrollWidth<=m.mainWidth+1,`${route}/${width} dépasse horizontalement`);
    if(['format_trend','origins','collabs','genres','map'].includes(route)) {
     await shot(`apres-${route}-${width}`);
     if(width<768){
      await evaluate(`document.querySelector('.js-plotly-plot').scrollIntoView({block:'start'})`);await settle();
      await shot(`apres-${route}-${width}-graphique`);
     }
    }
   }
  }
  await dimensions(1440,900);
  await go('teams');await radio('teams_view','Évolution par décennie');await shot('apres-equipes-evolution');
  await go('reuse');await radio('reuse_view','Évolution par décennie');await shot('apres-reutilisation-evolution');
  await go('map');await radio('country_view','Comparaison des périodes');await shot('apres-pays-comparaison');
  await select('map_country','Porto Rico');await shot('apres-porto-rico');
  reports.push({territory:await evaluate(`document.querySelector('[data-testid="stMain"]').innerText`)});
  await go('origins');
  for(const type of ['deuteranopia','protanopia','tritanopia']){
   await send('Emulation.setEmulatedVisionDeficiency',{type});await shot(`apres-origines-${type}`);
  }
  await send('Emulation.setEmulatedVisionDeficiency',{type:'none'});
 }
 await fs.writeFile(`livrables/verification-navigateur-${mode}.json`,JSON.stringify(reports,null,2));
 console.log(`${mode}: ${reports.length} observations enregistrées, contrôles réussis.`);
} finally {ws.close();}
