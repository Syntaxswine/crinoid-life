// Screenshots of the real game at desktop and phone size: node shots.mjs
import path from 'node:path'; import fs from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer-core';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const url = pathToFileURL(path.join(HERE, '../index.html')).href;
const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, protocolTimeout: 0 });
fs.mkdirSync(path.join(HERE, 'out/shots'), { recursive: true });
for (const [name, vp] of [['desk', { width: 1366, height: 768 }], ['phone', { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true }]]) {
  const p = await b.newPage(); await p.setViewport(vp);
  p.on('pageerror', e => console.log(name, 'PAGE ERROR', e.message));
  await p.goto(url); await new Promise(r => setTimeout(r, 400));
  await p.screenshot({ path: path.join(HERE, `out/shots/${name}-0-title.jpg`), quality: 80 });
  const click = async (i = 0) => { await p.evaluate(i => { const g = [...document.querySelectorAll("#choices .choice")], bs = g.length ? g : [...document.querySelectorAll("#choices-t .choice")]; bs[Math.min(i, bs.length - 1)].click(); }, i); await p.evaluate(() => STAGE._step(3)); await new Promise(r => setTimeout(r, 700)); };
  await click(0); await p.screenshot({ path: path.join(HERE, `out/shots/${name}-1-larva.jpg`), quality: 80 });
  await click(0); await p.screenshot({ path: path.join(HERE, `out/shots/${name}-2-settled.jpg`), quality: 80 });
  for (let i = 0; i < 4; i++) await click(0);
  await p.screenshot({ path: path.join(HERE, `out/shots/${name}-3-seasons.jpg`), quality: 80 });
  const info = await p.evaluate(() => ({ cw: document.getElementById('stage-c').width, scrollY, top: document.getElementById('choices').getBoundingClientRect().top, hud: document.getElementById('hud').offsetHeight }));
  console.log(name, JSON.stringify(info));
  await p.close();
}
await b.close();
