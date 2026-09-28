// Plays the real game in headless Chrome by clicking its buttons, stepping the
// stage clock between clicks. Reports page errors, endings reached, frame cost,
// and saves a contact sheet of the first sighting of every scene.
import puppeteer from 'puppeteer-core';
import fs from 'node:fs'; import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const url = process.argv[2] || pathToFileURL(path.resolve(HERE, '../index.html')).href;
const GAMES = +(process.argv[3] || 300);
const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, protocolTimeout: 0 });
const p = await b.newPage(); await p.setViewport({ width: 700, height: 900 });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto(url, { waitUntil: 'load' });
await p.evaluate(() => { try { localStorage.clear() } catch (e) {} ; window.scrollTo = () => {} });
const shots = {};
const res = await p.evaluate(async (GAMES) => {
  const seen = {}, endings = {}, grab = (k) => { if (!seen[k]) seen[k] = document.getElementById('stage-c').toDataURL('image/jpeg', .8) };
  const click = (b) => b.click();
  STAGE._step(2); grab('title');
  for (let g = 0; g < GAMES; g++) {
    document.querySelectorAll('#choices-t .choice')[g % 2].click();
    STAGE._step(.6); grab('larva:' + S.sub);
    for (let n = 0; n < 80; n++) {
      const h2 = document.querySelector('.ending h2');
      if (h2) { const id = window.__lastEnd; break }
      const bs = [...document.querySelectorAll('#choices .choice')];
      if (!bs.length) { seen['STUCK'] = 1; break }
      const pol = g % 3;                       // 0 random, 1 careful, 2 reckless
      const t = bs.map(x => x.querySelector('.lbl').textContent);
      let i = Math.floor(Math.random() * bs.length);
      if (pol === 1) { const k = t.findIndex(x => /Open the fan|Next season|Let go and crawl|Let it have|Allow|Close up|Settle|Regrow|Add to/.test(x)); if (k >= 0) i = k }
      if (pol === 2) { const k = t.findIndex(x => /Open up|Pull it in|Stay where|Open the fan|Next|Settle/.test(x)); if (k >= 0) i = k }
      if (S && S.phase === 'sessile' && S.ev) grab('ev:' + S.ev + (S.visitor ? ':' + S.visitor : ''));
      const label = t[i];
      click(bs[i]);
      STAGE._step(label === 'Settle here' ? 4 : label === 'Let go and crawl' ? 5 : 1.4);
      if (S && S.phase === 'sessile') grab('after:' + label + (S.ev === 'tenant' ? '' : ''));
      const e = document.querySelector('.ending h2');
      if (e) { endings[e.textContent] = (endings[e.textContent] || 0) + 1; STAGE._step(5); grab('END:' + e.textContent); break }
    }
    document.querySelector('#choices .choice').click();
  }
  // frame cost: a busy carb meadow and a present-day current
  const cost = {};
  for (const era of [0, 1]) {
    document.querySelectorAll('#choices-t .choice')[era].click();
    document.querySelector('#choices .choice').click();            // settle (or sand)
    const t0 = performance.now(); STAGE._step(3); cost[era ? 'now' : 'carb'] = +((performance.now() - t0) / 90).toFixed(2);
    document.querySelector('#choices .choice')?.click();
    while (document.querySelector('.ending h2') === null && document.querySelector('#choices .choice')) { const bs = document.querySelectorAll('#choices .choice'); bs[bs.length - 1].click(); }
    document.querySelector('#choices .choice').click();
  }
  return { seen, endings, cost };
}, GAMES);
fs.mkdirSync(path.join(HERE, 'out/play'), { recursive: true });
const keys = Object.keys(res.seen).filter(k => k !== 'STUCK');
for (const k of keys) fs.writeFileSync(path.join(HERE, 'out/play', k.replace(/[^a-z0-9]+/gi, '_') + '.jpg'), Buffer.from(res.seen[k].slice(23), 'base64'));
console.log(JSON.stringify({ errs: [...new Set(errs)], stuck: !!res.seen.STUCK, endings: res.endings, nEndings: Object.keys(res.endings).length, cost_ms_per_frame: res.cost, scenes: keys.length }, null, 1));
await b.close();
