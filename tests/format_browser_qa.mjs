// QA locale de Format & son. Chrome isolé : port 9227, Streamlit : port 8504.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const directory = 'livrables/format-son';
const genresOnly = process.argv.includes('--genres-only');
await fs.mkdir(directory, {recursive:true});
const pages = await (await fetch('http://127.0.0.1:9227/json')).json();
const page = pages.find(p => p.type === 'page' && p.url.startsWith('http://127.0.0.1:8504'));
assert(page, 'Ouvrir Streamlit dans Chrome de vérification sur 8504.');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(resolve => ws.addEventListener('open', resolve, {once:true}));
let id = 0;
const pending = new Map();
ws.onmessage = e => {
  const d = JSON.parse(e.data);
  if (d.id) { pending.get(d.id)?.(d); pending.delete(d.id); }
};
const send = (method, params={}) => new Promise((resolve, reject) => {
  const n = ++id;
  pending.set(n, d => d.error ? reject(d.error) : resolve(d.result));
  ws.send(JSON.stringify({id:n,method,params}));
});
const evaluate = async expression => {
  const r = await send('Runtime.evaluate', {expression,returnByValue:true,awaitPromise:true});
  if (r.exceptionDetails) throw Error(JSON.stringify(r.exceptionDetails));
  return r.result.value;
};
const settle = () => new Promise(r => setTimeout(r, 850));
const click = async selector => {
  assert(await evaluate(`Boolean(document.querySelector(${JSON.stringify(selector)}))`), selector);
  await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);
  await settle();
};
const radio = async (key,text) => {
  await evaluate(`[...document.querySelectorAll('.st-key-${key} label')].find(e=>e.innerText===${JSON.stringify(text)}).click()`);
  await settle();
};
const select = async (key,text) => {
  await click(`.st-key-${key} input`);
  await send('Input.insertText', {text});
  await settle();
  await evaluate(`[...document.querySelectorAll('[role="option"]')].find(e=>e.innerText===${JSON.stringify(text)}).click()`);
  await settle();
};
const shot = async name => {
  const result = await send('Page.captureScreenshot', {format:'png'});
  await fs.writeFile(`${directory}/${name}.png`, Buffer.from(result.data,'base64'));
};
const reports = genresOnly ? JSON.parse(await fs.readFile(`${directory}/verification-navigateur.json`,'utf8')) : [];
const check = async (route,width,expectedCharts) => {
  if (width<768) {
    await evaluate(`(()=>{const s=document.querySelector('[data-testid="stSidebar"]');if(s && getComputedStyle(s).visibility!=='hidden' && s.getBoundingClientRect().x>=0) s.querySelector('[data-testid="stSidebarCollapseButton"] button')?.click();})()`);
    await settle();
  }
  const m = await evaluate(`(()=>{
    const main=document.querySelector('[data-testid="stMain"]');
    const charts=[...document.querySelectorAll('.js-plotly-plot')];
    return {title:document.querySelector('h1')?.innerText, width:innerWidth,
      mainWidth:main.clientWidth,scrollWidth:main.scrollWidth,
      errors:[...document.querySelectorAll('[data-testid="stException"]')].map(e=>e.innerText),
      charts:charts.map(c=>({width:c.getBoundingClientRect().width,plotWidth:c._fullLayout?._size.w,
        xTitle:c.layout.xaxis?.title?.text,yTitle:c.layout.yaxis?.title?.text,
        ticks:c.layout.xaxis?.ticktext,tickangle:c.layout.xaxis?.tickangle}))};
  })()`);
  reports.push({route,...m});
  assert.equal(m.width,width);
  assert.equal(m.errors.length,0);
  assert.equal(m.charts.length,expectedCharts);
  assert(m.scrollWidth <= m.mainWidth+1, `${route}/${width}: débordement de page`);
  for (const c of m.charts) assert(c.plotWidth >= 65, `${route}/${width}: graphique trop comprimé`);
  await evaluate(`document.querySelector('[data-testid="stMain"]').scrollTo(0,0)`);
  await settle();
  await shot(`${route}-${width}`);
  for (let i=0;i<m.charts.length;i++) {
    await evaluate(`document.querySelectorAll('.js-plotly-plot')[${i}].scrollIntoView({block:'center'})`);
    await settle();
    await shot(`${route}-${width}-graphique-${i+1}`);
  }
  console.log(`${route} · ${width} px : ${m.charts.length} graphique(s), aucun débordement.`);
};
try {
  await send('Page.reload', {ignoreCache:true});
  await new Promise(r => setTimeout(r,2000));
  for (const width of [1440,390,320]) {
    await send('Emulation.setDeviceMetricsOverride',{width,height:width===1440?1000:844,deviceScaleFactor:1,mobile:width<768});
    await settle();
    if (width<768) {
      await evaluate(`document.querySelector('[data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarCollapseButton"] button')?.click()`);
      await settle();
    }
    if (genresOnly) {
      await click('.st-key-group_1 button');
      await click('.st-key-nav_genres button');
      await radio('genres_view','Comparaison des périodes');
      await check('genres-comparaison',width,1);
      continue;
    }
    await click('.st-key-group_0 button');
    await click('.st-key-shortcut_format_trend button');
    await check('vue-ensemble',width,1);
    for (const [route,count] of [['duration',3],['sound',2],['instrumentation',2],['genres',1]]) {
      await click(`.st-key-nav_${route} button`);
      if(route==='genres')
        await radio('genres_view','Comparaison des périodes');
      await check(route,width,count);
    }
    await radio('genres_view','Évolution historique');
    await select('genre_history','Rock');
    await check('genres-historique',width,1);
    await click('.st-key-nav_duration button');
    await select('duration_metric','Part de l’introduction');
    await check('ratio-introduction',width,3);
    await click('.st-key-nav_sound button');
    await select('sonic','Niveau sonore');
    await check('niveau-sonore',width,2);
    // Retour par Données, avec filtres conservés et vraie table rendue.
    await evaluate(`[...document.querySelectorAll('[data-testid="stMain"] details summary')].find(e=>e.innerText.includes('Détails')).click()`);
    await settle();
    await click('.st-key-shortcut_data_b button');
    assert.equal(await evaluate(`document.querySelectorAll('.titles-table tbody tr').length`),81);
    assert.equal(await evaluate(`document.querySelectorAll('[data-testid="stException"]').length`),0);
  }
  if (!genresOnly) {
  // Survol réel d’une médiane et d’une barre : vérifier les informations accessibles.
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await send('Page.reload',{ignoreCache:true});
  await new Promise(r=>setTimeout(r,1800));
  await click('.st-key-group_1 button');
  await click('.st-key-nav_sound button');
  await select('sonic','Tempo');
  await evaluate(`document.querySelector('.js-plotly-plot').scrollIntoView({block:'center'})`);
  await settle();
  const dot=await evaluate(`document.querySelector('.scatterlayer .point').getBoundingClientRect().toJSON()`);
  await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:dot.x+dot.width/2,y:dot.y+dot.height/2});
  await settle();
  const hover=await evaluate(`document.querySelector('.hoverlayer')?.textContent`);
  assert(hover.includes('Médiane') && hover.includes('BPM') && hover.includes('Exploitables'));
  reports.push({hover});
  await shot('survol-tempo-1440');
  await click('.st-key-nav_instrumentation button');
  await evaluate(`document.querySelector('.js-plotly-plot').scrollIntoView({block:'center'})`);
  await settle();
  const bar=await evaluate(`document.querySelector('.barlayer .point path').getBoundingClientRect().toJSON()`);
  await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:bar.x+bar.width/2,y:bar.y+bar.height/2});
  await settle();
  const barHover=await evaluate(`document.querySelector('.hoverlayer')?.textContent`);
  assert(barHover.includes('Écart') && barHover.includes('titres') && barHover.includes('points'));
  reports.push({barHover});
  await shot('survol-instrumentation-1440');
  }
  await fs.writeFile(`${directory}/verification-navigateur.json`,JSON.stringify(reports,null,2));
  console.log(`${reports.length} contrôles navigateur réussis, captures dans ${directory}.`);
} finally {ws.close();}
