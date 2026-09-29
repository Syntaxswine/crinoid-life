// Every ending's stage on a phone and a laptop, the text hidden: node endshots.mjs
import path from 'node:path'; import fs from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer-core';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, protocolTimeout: 0 });
fs.mkdirSync(path.join(HERE, 'out/ends'), { recursive: true });
const IDS = ['drift','sand','starved','cup','eaten','feather','landlord','apart','drawer','limestone','beads'];
for (const [name, vp] of [['phone', { width: 390, height: 844 }], ['desk', { width: 1366, height: 768 }]]) {
  const p = await b.newPage(); await p.setViewport(vp);
  p.on('pageerror', e => console.log(name, 'PAGE ERROR', e.message));
  await p.goto(pathToFileURL(path.join(HERE, '../index.html')).href);
  for (const id of IDS) {
    await p.evaluate(id => { document.querySelector('.wrap').style.visibility = 'hidden';
      document.querySelector('#choices-t .choice').click(); document.querySelector('#choices .choice').click();
      S.tenants = ['brittle', 'eulimid', 'worm', 'lobster']; S.snail = true; STAGE.sync(); STAGE._step(2); STAGE.cue('end', id); STAGE._step(id === 'eaten' ? 5 : 6); }, id);
    await p.screenshot({ path: path.join(HERE, `out/ends/${name}-${id}.jpg`), quality: 70 });
    await p.goto(pathToFileURL(path.join(HERE, '../index.html')).href);
  }
  await p.close();
}
await b.close();
