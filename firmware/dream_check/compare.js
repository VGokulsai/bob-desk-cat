// Diffs the firmware's dream frames (raw RGB565 from dream_check) against sim/dream.js at the same times.
// Float vs double maths can move a stray pixel, so each frame may differ in up to 1% of its pixels.
// usage: node compare.js fw.bin
const fs = require('fs'), path = require('path');
const D = require(path.join(__dirname, '..', '..', 'sim', 'dream.js'));
const frames = [...fs.readFileSync(path.join(__dirname, 'times.h'), 'utf8').matchAll(/\{(\d), ([\d.]+)f\}/g)].map(m => [+m[1], +m[2]]);
const fw = fs.readFileSync(process.argv[2]), n = D.N * D.N, LIMIT = 0.01;
if (!frames.length || fw.length !== frames.length * n * 2) { console.log(`FAIL: expected ${frames.length} frames, got ${fw.length / n / 2}`); process.exit(1); }
let bad = 0;
frames.forEach(([s, t], j) => {
  const b = D.frame(D.SCENES[s], t);
  let diff = 0;
  for (let i = 0; i < n; i++) {
    const p = fw.readUInt16LE((j * n + i) * 2);   // the city fade rounds a little differently: allow one colour step
    if (Math.abs((b[i * 4] >> 3) - (p >> 11)) > 1 || Math.abs((b[i * 4 + 1] >> 2) - ((p >> 5) & 63)) > 1 || Math.abs((b[i * 4 + 2] >> 3) - (p & 31)) > 1) diff++;
  }
  const ok = diff / n <= LIMIT;
  if (!ok) bad++;
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${D.SCENES[s].padEnd(4)} t=${t}: ${diff} of ${n} pixels differ`);
});
console.log(bad ? `FAIL: ${bad} frames differ` : 'firmware dreams match the sim');
process.exit(bad ? 1 : 0);
