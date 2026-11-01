// Recette locale réelle : node tests/format_ux_browser_qa.mjs avant|apres.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const phase=process.argv[2]||'apres';
const dir='livrables/format-son-ux';
const url=process.env.BILLBOARD_URL||'http://127.0.0.1:8505';
const port=process.env.BILLBOARD_CDP_PORT||9229;
await fs.mkdir(dir,{recursive:true});
const pages=await(await fetch(`http://127.0.0.1:${port}/json`)).json();
const page=pages.find(p=>p.type==='page'&&p.url.startsWith(url));assert(page,'Ouvrir le worktree dans Chrome de test.');
const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let id=0;const pending=new Map();
ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.id){pending.get(d.id)?.(d);pending.delete(d.id);}};
const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,d=>d.error?reject(d.error):resolve(d.result));ws.send(JSON.stringify({id:n,method,params}));});
const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
const settle=()=>new Promise(r=>setTimeout(r,600));
const wait=async(expression,label)=>{const end=Date.now()+30000;while(Date.now()<end){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,150));}throw Error('Délai : '+label);};
const click=async selector=>{await wait(`Boolean(document.querySelector(${JSON.stringify(selector)}))`,selector);await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);await settle();};
const radio=async(key,text)=>{await evaluate(`[...document.querySelectorAll('.st-key-${key} label')].find(e=>e.innerText===${JSON.stringify(text)}).click()`);await settle();};
const select=async(key,text)=>{await click(`.st-key-${key} input`);await send('Input.insertText',{text});await settle();await evaluate(`(()=>{const o=[...document.querySelectorAll('[role="option"]')];(o.find(e=>e.innerText===${JSON.stringify(text)})||o.find(e=>e.innerText.includes(${JSON.stringify(text)}))).click();})()`);await settle();};
const groups=[['summary'],['format_trend','duration','sound','instrumentation','genres'],['origins','map'],['ages','formats','teams','reuse'],['data_a','data_b']];
const go=async route=>{await click(`.st-key-group_${groups.findIndex(g=>g.includes(route))} button`);if(route!=='summary')await click(`.st-key-nav_${route} button`);await wait(`Boolean(document.querySelector('h1'))`,'titre');};
const sidebar=async open=>{await evaluate(`(()=>{const s=document.querySelector('[data-testid="stSidebar"]');if(s?.getAttribute('aria-expanded')!==${JSON.stringify(String(open))}){const e=document.querySelector(${JSON.stringify(open?'[data-testid="stExpandSidebarButton"]':'[data-testid="stSidebarCollapseButton"]')});(e?.querySelector('button')||e)?.click();}})()`);await settle();};
const shot=async name=>{const s=await send('Page.captureScreenshot',{format:'png'});await fs.writeFile(`${dir}/${phase}-${name}.png`,Buffer.from(s.data,'base64'));};
const body=()=>evaluate(`document.querySelector('[data-testid="stMain"]').innerText`);
const key=async(name,code)=>{await send('Input.dispatchKeyEvent',{type:'keyDown',key:name,code:name,windowsVirtualKeyCode:code});await send('Input.dispatchKeyEvent',{type:'keyUp',key:name,code:name,windowsVirtualKeyCode:code});await settle();};
const pointer=async selector=>{
 await evaluate(`document.querySelector(${JSON.stringify(selector)}).scrollIntoView({block:'nearest',inline:'center'})`);await settle();
 const r=await evaluate(`document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect().toJSON()`);
 const x=r.x+r.width/2,y=r.y+r.height/2;
 assert(await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)}),h=document.elementFromPoint(${x},${y});return e===h||e.contains(h);})()`),'Cible masquée : '+selector);
 await send('Input.dispatchMouseEvent',{type:'mousePressed',x,y,button:'left',clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button:'left',clickCount:1});await settle();
};
const reports=[];
const hover=async(name,expression,expected)=>{
 await evaluate(`(()=>{const c=document.querySelector('.js-plotly-plot'),nav=document.querySelector('.st-key-dashboard_navigation'),main=document.querySelector('[data-testid="stMain"]');main.scrollTop+=c.getBoundingClientRect().top-(nav.getBoundingClientRect().bottom+42);})()`);await settle();
 const r=await evaluate(expression);
 await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:r.x+r.width/2,y:r.y+r.height/2});await settle();
 const text=await evaluate(`document.querySelector('.hoverlayer')?.textContent`);
 assert(text&&expected.every(value=>text.includes(value)),name+': '+text);assert(!text.includes('Écart'));
 reports.push({scenario:name,width:1440,height:900,hover:text});await shot(name+'-1440');
};
const record=async(name,width,expectedCharts)=>{
 await sidebar(width>=768);
 await evaluate(`window.scrollTo(0,0);document.querySelector('[data-testid="stMain"]').scrollTo(0,0)`);await settle();
 const m=await evaluate(`(()=>{const main=document.querySelector('[data-testid="stMain"]');const nav=document.querySelector('.st-key-primary_nav');const secondary=document.querySelector('.st-key-secondary_nav');return {width:innerWidth,height:innerHeight,title:document.querySelector('h1').innerText,scrollHeight:main.scrollHeight,clientHeight:main.clientHeight,scrollWidth:main.scrollWidth,clientWidth:main.clientWidth,charts:document.querySelectorAll('.js-plotly-plot').length,errors:[...document.querySelectorAll('[data-testid="stException"]')].map(e=>e.innerText),navTop:nav.getBoundingClientRect().top,navBottom:secondary.getBoundingClientRect().bottom,titleTop:document.querySelector('h1').getBoundingClientRect().top,kpis:[...document.querySelectorAll('.kpi-value')].map(e=>{const r=document.createRange();r.selectNodeContents(e);return {text:e.innerText,lines:r.getClientRects().length,width:e.clientWidth,scrollWidth:e.scrollWidth};}),figures:[...document.querySelectorAll('.js-plotly-plot')].map(c=>({height:c.getBoundingClientRect().height,plotWidth:c._fullLayout._size.w,xTitle:c.layout.xaxis?.title?.text,yTitle:c.layout.yaxis?.title?.text,traces:c.data.map(t=>({name:t.name,type:t.type,hovertemplate:t.hovertemplate,texttemplate:t.texttemplate}))}))};})()`);
 assert.equal(m.width,width);assert.equal(m.height,width===1440?900:844);assert.equal(m.errors.length,0);assert(m.scrollWidth<=m.clientWidth+1,name+' déborde');
 for(const figure of m.figures)assert(figure.plotWidth>=65,name+' graphique trop comprimé');
 if(expectedCharts!==undefined)assert.equal(m.charts,expectedCharts,name);
 m.scenario=name;m.scrollDistance=Math.max(0,m.scrollHeight-m.clientHeight);
 await shot(`${name}-${width}`);
 for(let i=0;i<m.charts;i++){await evaluate(`(()=>{const c=document.querySelectorAll('.js-plotly-plot')[${i}],main=document.querySelector('[data-testid="stMain"]');const nav=document.querySelector('.st-key-dashboard_navigation');main.scrollTop+=c.getBoundingClientRect().top-(nav?nav.getBoundingClientRect().bottom+42:90);})()`);await settle();await shot(`${name}-${width}-graphique-${i+1}`);}
 await evaluate(`document.querySelector('[data-testid="stMain"]').scrollTo(0,600)`);await settle();
 m.navTopScrolled=await evaluate(`document.querySelector('.st-key-primary_nav').getBoundingClientRect().top`);
 m.navPosition=await evaluate(`(()=>{const n=document.querySelector('.st-key-dashboard_navigation');return n?getComputedStyle(n.parentElement).position:null;})()`);
 if(phase==='apres'&&groups[1].includes(name)){
  await fs.writeFile(`${dir}/diagnostic-navigation.json`,JSON.stringify(m,null,2));
  assert.equal(m.navPosition,'sticky',name+' navigation');assert(Math.abs(m.navTopScrolled-(width<768?72:76))<=2,name+' navigation défile');
  assert(m.titleTop>=m.navBottom-1,name+' titre masqué');
  if(name==='duration')assert(m.kpis.every(k=>k.lines===1&&k.scrollWidth<=k.width+1),'KPI durée sur plusieurs lignes');
  await send('Input.dispatchMouseEvent',{type:'mouseWheel',x:width-45,y:m.height-170,deltaX:0,deltaY:900});await settle();
  m.navTopAfterWheel=await evaluate(`document.querySelector('.st-key-primary_nav').getBoundingClientRect().top`);
  m.windowScrollY=await evaluate('window.scrollY');
  assert(m.navTopAfterWheel>=(width<768?72:76)-1,name+' navigation masquée après molette');
 }
 await shot(`${name}-${width}-navigation`);
 reports.push(m);await fs.writeFile(`${dir}/${phase}-navigateur.json`,JSON.stringify(reports,null,2));
 console.log(`${phase} · ${name} · ${width} : ${m.scrollHeight}px, ${m.charts} graphique(s).`);
};
try{
 await send('Page.reload',{ignoreCache:true});await wait(`Boolean(document.querySelector('.st-key-group_1 button'))`,'Streamlit');
 for(const width of [1440,390,320]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:width===1440?900:844,deviceScaleFactor:1,mobile:width<768});await settle();
  if(phase==='guides'){
   await go('duration');
   const reference=await evaluate(`(()=>{const e=document.querySelector('.format-reading'),p=e.querySelector('p'),b=e.querySelector('b'),c=getComputedStyle(e);return {background:c.backgroundColor,border:c.borderLeft,padding:c.padding,font:getComputedStyle(p).fontSize,lineHeight:getComputedStyle(p).lineHeight,margin:getComputedStyle(p).margin,titleFont:getComputedStyle(b).fontSize,titleColor:getComputedStyle(b).color};})()`);
   await go('ages');
   const existing=await evaluate(`(()=>{const e=document.querySelector('[class*="st-key-reading_existing_"]'),p=e.querySelector('p'),b=p.querySelector('strong'),c=getComputedStyle(e);return {background:c.backgroundColor,border:c.borderLeft,padding:c.padding,font:getComputedStyle(p).fontSize,lineHeight:getComputedStyle(p).lineHeight,margin:getComputedStyle(p).margin,titleFont:getComputedStyle(b).fontSize,titleColor:getComputedStyle(b).color};})()`);
   assert.deepEqual(existing,reference,'Habillage du guide existant différent de la référence');
   await record('guide-reference',width,1);reports.at(-1).guideStyle=existing;
   await fs.writeFile(`${dir}/${phase}-navigateur.json`,JSON.stringify(reports,null,2));continue;
  }
  for(const [route,before] of [['format_trend',1],['duration',3],['sound',2],['instrumentation',2],['genres',1]]){
   await go(route);await record(route,width,phase==='avant'?before:1);
  }
  if(phase==='apres'){
   await go('duration');await radio('duration_view','Introduction');await record('duration-introduction',width,1);
   await radio('duration_view','Évolution');await select('duration_metric','Part de l’introduction');await record('duration-ratio',width,1);
   await go('sound');await select('sonic','Niveau sonore');await radio('sound_view','Évolution');await record('sound-historique',width,1);
   await go('instrumentation');await radio('instrument_view','Présence');await record('instrumentation-presence',width,1);
   await go('genres');await radio('genres_view','Historique');await select('genre_history','Rock');await record('genres-historique',width,1);
   // Revenir aux défauts pour une comparaison avant/après à réglages identiques.
   await go('duration');await radio('duration_view','Durée');
   await go('sound');await select('sonic','Tempo');await radio('sound_view','Distribution');
   await go('instrumentation');await radio('instrument_view','Rôle central');
   await go('genres');await radio('genres_view','Comparer les années');
   if(width===1440){
    await go('sound');
    await hover('infobulle-tempo',`(()=>{const c=document.querySelector('.js-plotly-plot'),t=c._fullData.filter(t=>t.type==='scatter'&&t.marker?.symbol==='diamond').at(-1);return [...c.querySelectorAll('.scatterlayer .trace')].find(e=>e.classList.contains('trace'+t.uid)).querySelector('.point').getBoundingClientRect().toJSON();})()`,['Médiane : 118 BPM','81 / 81']);
    await go('instrumentation');
    await hover('infobulle-instrumentation',`document.querySelector('.barlayer .trace:nth-child(2) .point:nth-child(2) path').getBoundingClientRect().toJSON()`,['28 / 81 titres','renseignés']);
   }
   // Navigation à la souris depuis le bas de page ; radio et mesure au clavier.
   await go('duration');await evaluate(`document.querySelector('[data-testid="stMain"]').scrollTo(0,600)`);await settle();
   await pointer('.st-key-nav_sound button');assert((await body()).includes('Quelle signature sonore'));
   await record('navigation-souris',width,1);
   await pointer('.st-key-sonic [data-baseweb="select"]');await send('Input.insertText',{text:'Énergie'});await key('ArrowDown',40);await key('Enter',13);
   assert((await body()).includes('Énergie · distribution'));await record('mesure-clavier',width,1);
   await go('duration');await radio('duration_view','Durée');
   await evaluate(`(()=>{const e=document.querySelector('.st-key-duration_view');const main=document.querySelector('[data-testid="stMain"]');main.scrollTop+=e.getBoundingClientRect().top-220;e.querySelector('input').focus({preventScroll:true});})()`);
   await key('ArrowRight',39);
   assert(await evaluate(`[...document.querySelectorAll('.st-key-duration_view label')].some(e=>e.innerText==='Introduction'&&e.querySelector('input')?.checked)`));
   await record('graphique-clavier',width,1);
   // Filtres conservés après un accès réel aux données et export disponible.
   await sidebar(true);await select('genre','Pop');await sidebar(width>=768);
   await evaluate(`[...document.querySelectorAll('[data-testid="stMain"] details summary')].find(e=>e.innerText.includes('Détails')).click()`);await settle();
   await click('.st-key-shortcut_data_b button');assert.equal(await evaluate(`document.querySelectorAll('.titles-table tbody tr').length`),36);
   assert(await evaluate(`Boolean(document.querySelector('.st-key-dashboard_navigation'))`));
   await record('donnees-pop',width,0);
   // Une puis deux sélections vides : les nouveaux modes restent utilisables.
   await sidebar(true);await select('decade_a','1958 – 1959');await select('genre','Non renseigné');
   await go('duration');await record('selection-vide',width,1);
   await sidebar(true);await select('decade_b','1958 – 1959');
   await go('sound');await radio('sound_view','Évolution');await record('deux-selections-vides',width,1);
   await go('genres');await radio('genres_view','Historique');await select('genre_history','Non renseigné');await record('genre-non-renseigne',width,1);
   // Contrôler aussi la seule exception hors rubrique : habillage, texte intact.
   await sidebar(true);await select('genre','Tous les genres');await select('decade_a','2000 – 2009');await select('decade_b','2020 – 2024');
   await go('ages');assert(await evaluate(`Boolean(document.querySelector('.st-key-dashboard_navigation'))`));
   assert(await evaluate(`document.querySelector('[class*="st-key-reading_existing_"]')!==null`));
   await record('encadre-hors-format',width,1);
   await go('duration');await radio('duration_view','Durée');
   await go('sound');await select('sonic','Tempo');await radio('sound_view','Distribution');
   await go('genres');await radio('genres_view','Comparer les années');
  }
 }
 console.log(`${phase}: ${reports.length} observations réussies.`);
}catch(error){console.error(error);await shot('echec');const parents=await evaluate(`(()=>{const a=[];for(let e=document.querySelector('.st-key-dashboard_navigation');e&&a.length<9;e=e.parentElement){const c=getComputedStyle(e);a.push({tag:e.tagName,classes:e.className,testid:e.dataset.testid,position:c.position,overflow:c.overflow,rect:e.getBoundingClientRect().toJSON()});}return a;})()`);await fs.writeFile(`${dir}/${phase}-echec.json`,JSON.stringify({error:String(error),parents,text:await body()},null,2));process.exitCode=1;}finally{ws.close();}
