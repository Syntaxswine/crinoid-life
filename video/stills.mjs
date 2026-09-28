// Contact sheet of the trailer at chosen times: node stills.mjs 1 5 9 ...
import path from 'node:path'; import fs from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer-core';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const times = process.argv.slice(2).map(Number);
const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, args: ['--allow-file-access-from-files'] });
const p = await b.newPage(); await p.setViewport({ width: 1080, height: 1920 });
p.on('pageerror', e => console.log('PAGE ERROR', e.message));
await p.goto(pathToFileURL(path.join(HERE, 'trailer.html')).href + '?render');
await p.evaluate(() => window.ready());
fs.mkdirSync(path.join(HERE, 'out/stills'), { recursive: true });
for (const t of times) {
  const b64 = await p.evaluate(tt => { window.draw(tt); return document.getElementById('c').toDataURL('image/jpeg', .85).slice(23); }, t);
  fs.writeFileSync(path.join(HERE, `out/stills/${t.toFixed(1)}.jpg`), Buffer.from(b64, 'base64'));
}
await b.close();
