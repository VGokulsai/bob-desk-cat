// Bob's dream world: three little pixel stories on an 80x80 grid (3 screen px each on the 240 px round screen).
// Everything is drawn from short sprite strings and rectangles, no image files, so the ESP32 can draw the same.
// One source for both: sim/index.html loads it as a script, face/make_dream_gif.py runs it with node.
//   DREAM.frame(scene, t) -> RGBA bytes (80*80*4) of that scene at t seconds
(function () {
const N = 80;
const buf = new Uint8ClampedArray(N * N * 4);
const RGB = {};
const rgb = c => RGB[c] || (RGB[c] = [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16)));
function put(x, y, w, h, c) {
  const [r, g, b] = rgb(c);
  x = Math.round(x); y = Math.round(y);
  for (let j = Math.max(0, y); j < Math.min(N, y + h); j++)
    for (let i = Math.max(0, x); i < Math.min(N, x + w); i++) { const k = (j * N + i) * 4; buf[k] = r; buf[k + 1] = g; buf[k + 2] = b; buf[k + 3] = 255; }
}
const hash = (a, b = 0) => {   // stable 0..1 noise, same on every device
  let h = Math.imul(a | 0, 374761393) + Math.imul(b | 0, 668265263);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
};
function spr(rows, x, y, pal) {   // '.' or any char not in pal = see-through
  x = Math.round(x); y = Math.round(y);
  for (let r = 0; r < rows.length; r++) for (let c = 0; c < rows[r].length; c++) { const col = pal[rows[r][c]]; if (col) put(x + c, y + r, 1, 1, col); }
}
function disc(cx, cy, r, col) { for (let y = -r; y <= r; y++) for (let x = -r; x <= r; x++) if (x * x + y * y <= r * r + r) put(cx + x, cy + y, 1, 1, col); }
const ease = x => x < 0.5 ? 2 * x * x : 1 - 2 * (1 - x) * (1 - x);
const clamp01 = x => Math.max(0, Math.min(1, x));

// ---- the cats ----
// Bob, from Gokul's drawing: tall ears with pink insides, white heart-shaped face, grey fur, big dark eyes.
// Eye cells: x a y / b f b / c d c, filled per mood by eyesFor() (open, shut, happy ^).
const BOB_HEAD = [
  '.k...........k.',
  '.kk.........kk.',
  '.kpk.......kpk.',
  '.kpk.......kpk.',
  'kgpk.......kpgk',
  'kgpk.......kpgk',
  'kgppk.....kppgk',
  'kgppgk...kgppgk',
  'kgppgkkkkkgppgk',
  'kgwwwwwgwwwwwgk',
  'kwwwwwwwwwwwwwk',
  'kwwxaywwwxaywwk',
  'kwwbfbwwwbfbwwk',
  'kwwcdcwwwcdcwwk',
  'kgqwwwwpwwwwqgk',
  '.kgwwwkwkwwwgk.',
  '..kgwwwwwwwgk..',
  '...kgwwwwwgk...',
  '....kgwwwgk....',
  '.....kgwgk.....',
  '......kwk......'];
const BOB_SIDE = [   // body seen from the side, facing right; head sits on its front end
  '..kkkkkkkkkk...',
  '.kllllllllllk..',
  '.klllllllllwwk.',
  '.kwwwwwwwwwwwk.',
  '..kwwwwwwwwwk..',
  '...kkkkkkkkk...'];
const BOB_SIT = [    // sitting, facing you, like the drawing: front legs in the middle, pink pads on the back feet
  '.....kwwwwwk.....',
  '....kgwwwwwgk....',
  '...kggwwwwwggk...',
  '...kgwwwwwwwgk...',
  '..kggwwwwwwwggk..',
  '..kgwkwwkwwkwgk..',
  '.kggwkwwkwwkwggk.',
  '.kgwwkwwkwwkwwgk.',
  'kgwwwkwwkwwkwwwgk',
  'kppwwkwwkwwkwwppk',
  '.kkkkkkkkkkkkkkk.'];
const BOB = { head: BOB_HEAD, side: BOB_SIDE, hdx: 5, hdy: -17,
  pal: { k: '#2a2622', g: '#8f8a84', l: '#d6d1ca', w: '#ffffff', p: '#e46aa0', q: '#ffffff' },
  eye: '#1e1a18', shine: '#ffffff', lid: '#ffffff', blush: '#f7a8c8',
  legNear: '#e9e5df', legFar: '#8f8a84', paw: '#ffffff', tail: '#8f8a84', fluffy: false };

// Her: a ginger tabby with a cream muzzle, short round ears, green eyes and a teal bow. Smaller than Bob.
const GIN_HEAD = [
  '.k.........k.',
  '.kk.......kk.',
  'kock.....kcok',
  'koockkkkkcook',
  'kooodododoook',
  'koooooooooook',
  'kooxyoooxyook',
  'koouvooouvook',
  'koqcccpcccqok',
  '.kocckckccok.',
  '..kocccccok..',
  '...kkkkkkk...'];
const GIN_SIDE = [
  '..kkkkkkkkkk...',
  '.kodoodoodook..',
  '.kooooooooocck.',
  '.kccccccccccck.',
  '..kccccccccck..',
  '...kkkkkkkkk...'];
const BOW = ['b...b', 'bbBbb', 'b...b'];
const GIN = { head: GIN_HEAD, side: GIN_SIDE, hdx: 6, hdy: -9,
  pal: { k: '#3a2418', o: '#f39a4a', d: '#c8622a', c: '#ffe7c7', p: '#ff8fa8', q: '#f39a4a', b: '#2fc4b2', B: '#16807a' },
  eye: '#1e1a18', iris: '#7ccf4a', lid: '#f39a4a', blush: '#ff7f9a',
  legNear: '#f39a4a', legFar: '#c8622a', paw: '#ffe7c7', tail: '#f39a4a', stripe: '#c8622a', fluffy: true };

// look: +1 right, -1 left. mood: 'open' | 'shut' | 'happy' (^ ^)
function eyesFor(cat, look, mood, blush) {
  const p = Object.assign({}, cat.pal);
  if (blush) p.q = cat.blush;
  const E = cat.eye, L = cat.lid;
  if (cat === BOB) {
    if (mood === 'open') Object.assign(p, { x: look > 0 ? cat.shine : E, y: look > 0 ? E : cat.shine, a: E, b: E, f: E, c: L, d: E });
    else if (mood === 'happy') Object.assign(p, { x: L, a: E, y: L, b: E, f: L, c: L, d: L });
    else Object.assign(p, { x: L, a: L, y: L, b: E, f: E, c: L, d: L });
  } else {
    const I = cat.iris;
    if (mood === 'open') Object.assign(p, look > 0 ? { x: I, y: E, u: I, v: E } : { x: E, y: I, u: E, v: I });
    else Object.assign(p, { x: E, y: E, u: L, v: L });
  }
  return p;
}

function tail(pts, cat) {   // outline pass, then fill pass; fluffy = thicker, striped
  const t = cat.fluffy ? 2 : 1;
  for (const [x, y] of pts) put(x - 1, y - 1, t + 2, t + 2, cat.pal.k);
  pts.forEach(([x, y], i) => put(x, y, t, t, cat.fluffy && i % 3 === 2 ? cat.stripe : cat.tail));
}
function leg(x, y, len, dx, col, paw) {
  for (let i = 0; i < len; i++) put(x + Math.round(dx * i / Math.max(1, len - 1)), y + i, 2, 1, i === len - 1 ? paw : col);
}

// a cat seen from the side (head turned to you). bx = left of body, ground = row under its feet.
// pose: walk (f = frame 0..3), stand, crouch, up, air, down, land
const STEP = [2, 0, -2, 0];
function walker(cat, bx, ground, pose, f, look, mood, blush, t) {
  let by = ground - 10, hy = 0, legs;   // legs: [far back, far front, near back, near front] as [len, dx]
  const L = (dx, lift = 0) => [ground - (by + 5) - lift, dx];
  if (pose === 'walk') {
    by -= f % 2;                                      // body rises on the passing frames
    const lg = o => { const i = (f + o) % 4; return L(STEP[i], i === 3 ? 1 : 0); };
    legs = [lg(0), lg(2), lg(2), lg(0)];
  } else if (pose === 'crouch' || pose === 'land') {
    by += 2; hy = pose === 'land' ? 1 : 0;            // squash
    legs = [L(-1), L(1), L(-1), L(1)];
  } else if (pose === 'up') { hy = -1; legs = [[6, -3], [4, 3], [6, -3], [4, 3]]; }      // stretch: push off
  else if (pose === 'air') legs = [[3, -1], [3, 1], [3, -1], [3, 1]];                     // tucked
  else if (pose === 'down') legs = [[3, -2], [5, 2], [3, -2], [5, 2]];                    // reach for the ground
  else legs = [L(0), L(0), L(0), L(0)];
  if (pose === 'up' || pose === 'air' || pose === 'down') by = ground - 10;            // caller lifts ground
  const sway = Math.sin(t * 3) * (pose === 'stand' ? 1.6 : 0.8);
  const pts = [];
  for (let i = 1; i <= 8; i++) pts.push([bx + 1 - i * 0.5 + Math.sin(t * 2.5 - i * 0.45) * i * 0.12 * sway, by + 1 - i * 0.95 + (i > 6 ? (i - 6) * 0.4 : 0)]);
  tail(pts, cat);
  leg(bx + 4, by + 5, legs[0][0], legs[0][1], cat.legFar, cat.legFar);
  leg(bx + 12, by + 5, legs[1][0], legs[1][1], cat.legFar, cat.legFar);
  spr(cat.side, bx, by, cat.pal);
  leg(bx + 2, by + 5, legs[2][0], legs[2][1], cat.legNear, cat.paw);
  leg(bx + 10, by + 5, legs[3][0], legs[3][1], cat.legNear, cat.paw);
  const hx = bx + cat.hdx, hyy = by + cat.hdy + hy;
  spr(cat.head, hx, hyy, eyesFor(cat, look, mood, blush));
  if (cat === GIN) spr(BOW, hx + 8, hyy - 1, cat.pal);
  return [hx + (cat.head[0].length >> 1), hyy];       // top-centre of the head, for hearts
}

const HEART = ['.r.r.', 'rrrrr', 'rrrrr', '.rrr.', '..r..'];
const HEART_BIG = ['.rr.rr.', 'rhrrrrr', 'rrrrrrr', 'rrrrrrr', '.rrrrr.', '..rrr..', '...r...'];
const HEART_PAL = { r: '#ff4f7e', h: '#ffd0dc' };
function sparkle(x, y, k, col) { put(x, y - k, 1, 2 * k + 1, col); put(x - k, y, 2 * k + 1, 1, col); }

// ================= 1. City night: Bob and her run the rooftops =================
const CITY_T = 7.6;
const SEGS = [[0, 9], [1.4, 12], [4.7, 0], [6.3, 9]];   // [from second, speed in grid px/s]: walk, run + jumps, stop, walk
function scrollAt(T) {
  let s = 0;
  SEGS.forEach(([t0, v], i) => { const t1 = i + 1 < SEGS.length ? SEGS[i + 1][0] : CITY_T; if (T > t0) s += v * (Math.min(T, t1) - t0); });
  return s;
}
const LOOP_PX = scrollAt(CITY_T);
const G = 64, BOB_X = 18, GIN_X = 45, JUMP_W = 9, JUMP_H = 11;
const WALL0 = scrollAt(2.0) + GIN_X + 10;                // she clears the wall at 2.0 s, Bob a moment later
const FISH = ['..xxx.x', '.xexxxx', '..xxx.x'];
const CSKY = ['#121635', '#161c44', '#1c2353', '#232a62', '#2d3170', '#3a387c', '#4a3f86', '#584690'];

function jumpPose(S, cx) {   // where a cat is in its jump over the nearest wall: [pose, height]
  const k = Math.round((S + cx - WALL0) / LOOP_PX), u = (S + cx - (k * LOOP_PX + WALL0 - JUMP_W / 2)) / JUMP_W;
  if (u > -0.22 && u <= 0) return ['crouch', 0];
  if (u > 0 && u < 1) return [u < 0.3 ? 'up' : u < 0.7 ? 'air' : 'down', Math.round(JUMP_H * 4 * u * (1 - u))];
  if (u >= 1 && u < 1.18) return ['land', 0];
  return null;
}

function city(t) {
  const T = t % CITY_T, S = Math.floor(t / CITY_T) * LOOP_PX + scrollAt(T);
  CSKY.forEach((c, i) => put(0, i * 8, N, 8, c));
  put(0, 64, N, 16, CSKY[7]);
  for (let i = 0; i < 46; i++) {
    const x = hash(i, 1) * N | 0, y = hash(i, 2) * 46 | 0, tw = Math.sin(t * 2.3 + i * 1.7);
    if (tw > -0.4) put(x, y, 1, 1, tw > 0.85 ? '#ffffff' : '#8a90c8');
  }
  disc(57, 17, 8, '#262d68'); disc(57, 17, 6, '#fff1c4');                              // moon and its glow
  put(54, 15, 2, 2, '#ecdca4'); put(59, 19, 2, 1, '#ecdca4'); put(58, 13, 1, 1, '#ecdca4');
  const far = S * 0.15;                                                                   // far skyline
  for (let c = Math.floor(far / 7) - 1; c <= Math.floor((far + N) / 7) + 1; c++) {
    const x = c * 7 - far, top = 38 + (hash(c, 3) * 12 | 0);
    put(x, top, 6, 30, '#222a5c');
    if (hash(c, 4) > 0.7) put(x + 2, top - 3, 1, 3, '#222a5c');                          // antenna
    for (let wy = top + 2; wy < 62; wy += 3) for (let wx = 1; wx < 5; wx += 2) if (hash(c * 31 + wx, wy) > 0.82) put(x + wx, wy, 1, 1, '#9d8f6a');
  }
  const mid = S * 0.45;                                                                   // nearer houses with warm windows
  for (let c = Math.floor(mid / 14) - 1; c <= Math.floor((mid + N) / 14) + 1; c++) {
    const x = c * 14 - mid, w = 11 + (hash(c, 5) * 2 | 0), top = 34 + (hash(c, 6) * 10 | 0);
    put(x, top, w, 40, '#181c42'); put(x + w - 1, top, 1, 40, '#262c5e'); put(x - 1, top - 1, w + 2, 1, '#2a2f62');
    for (let wy = top + 3; wy < 60; wy += 4) for (let wx = 2; wx < w - 2; wx += 3) {
      const lit = hash(c * 17 + wx, wy) > 0.68 !== (hash(c, wx * wy) > 0.97 && Math.sin(t * 0.8 + c) > 0);
      put(x + wx, wy, 2, 2, lit ? '#f2c055' : '#22285a');
      if (lit) put(x + wx, wy + 1, 2, 1, '#d09838');
    }
    if (((c % 4) + 4) % 4 === 1) {                                                        // a fish-shop sign, neon, flickering
      put(x + 1, top + 5, 10, 6, '#2a1430'); put(x + 1, top + 5, 10, 1, '#4a2450');
      const on = Math.sin(t * 7 + c) > -0.7 || Math.sin(t * 1.3) > 0.5;
      spr(FISH, x + 3, top + 7, { x: on ? '#ff6fae' : '#6a3456', e: '#2a1430' });
    }
  }
  put(0, G, N, 1, '#7a6690'); put(0, G + 1, N, 1, '#4a3a62'); put(0, G + 2, N, 14, '#2c2140');   // our rooftop
  for (let y = G + 4; y < N; y += 3) {
    put(0, y, N, 1, '#1f1730');
    for (let x = -((S + (y % 2) * 3) % 6); x < N; x += 6) put(x, y + 1, 1, 2, '#1f1730');
  }
  for (let k = Math.floor(S / LOOP_PX) - 1; k <= Math.floor(S / LOOP_PX) + 2; k++) {      // the wall they jump
    const wx = k * LOOP_PX + WALL0 - S - 2;
    put(wx, G - 8, 5, 8, '#9a4f3c');
    for (let y = G - 6; y < G; y += 2) put(wx, y, 5, 1, '#5e2c22');
    put(wx + 2, G - 7, 1, 1, '#5e2c22'); put(wx + 1, G - 5, 1, 1, '#5e2c22'); put(wx + 3, G - 3, 1, 1, '#5e2c22');
    put(wx - 1, G - 9, 7, 1, '#c9b8a0');
  }
  const pause = T >= 4.7 && T < 6.3, f = Math.floor(S / 2.2) % 4;
  const cats = [[BOB, BOB_X], [GIN, GIN_X]], heads = [];
  for (const [cat, x] of cats) {
    const j = pause ? null : jumpPose(S, x + 10);
    const look = pause && cat === GIN ? -1 : 1;
    const mood = pause && T > 5.6 ? 'happy' : 'open';
    heads.push(j ? walker(cat, x, G - j[1], j[0], f, look, mood, false, t)
                 : walker(cat, x, G, pause ? 'stand' : 'walk', f, look, mood, pause && T > 5.0, t));
  }
  if (pause && T > 5.0) {                                                                  // a tiny heart between them
    const k = (T - 5.0) / 1.3, hx = (heads[0][0] + heads[1][0]) / 2 - 2;
    if (k < 1 && (k < 0.8 || Math.floor(T * 12) % 2)) spr(HEART, hx, heads[1][1] - 4 - k * 6, HEART_PAL);
  }
}

// ================= 2. Home: Bob eats from his bowl in a warm room, it magically refills =================
const HOME_T = 6.6;
const BOWL = ['kRiiiiiiiiiiiRk', 'kBBBBBBBBBBBBBk', '.kBBWBBBBBWBBk.', '.kBBBBBBBBBBBk.', '..kkkkkkkkkkk..'];
const QMARK = ['.ww.', 'w..w', '..w.', '.w..', '....', '.w..'];
const LEAF = ['.gg', 'ggG', 'gG.'];

function home(t) {
  const T = t % HOME_T;
  put(0, 0, N, 56, '#f2d3a8');                                                             // wall + lamp glow
  for (let x = 2; x < N; x += 8) put(x, 0, 2, 56, '#ebc795');
  for (let y = 0; y < 56; y++) for (let x = 44; x < N; x++) {
    const d = Math.hypot(x - 67, y - 22), fl = Math.sin(t * 5) * 0.4;
    if (d < 11 + fl || (d < 17 + fl && (x + y) % 2 === 0)) put(x, y, 1, 1, (x - 2) % 8 < 2 ? '#f7dcae' : '#fbe7c4');
  }
  put(0, 54, N, 2, '#e3b67e'); put(0, 56, N, 1, '#c99a66');                               // skirting
  put(0, 57, N, 23, '#b0723f');                                                            // floorboards
  for (let y = 60; y < N; y += 4) { put(0, y, N, 1, '#93592e'); for (let x = (y * 7) % 13; x < N; x += 13) put(x, y + 1, 1, 3, '#93592e'); }
  for (let y = -6; y <= 6; y++) for (let x = -29; x <= 29; x++) {                          // rug
    const e = (x * x) / 841 + (y * y) / 36;
    if (e <= 1) put(40 + x, 71 + y, 1, 1, e > 0.8 ? '#8f2f45' : e > 0.6 ? '#f0b44c' : (x + y) % 4 === 0 ? '#c85068' : '#b8425a');
  }
  put(13, 13, 20, 22, '#7a4a2c'); put(14, 14, 18, 20, '#26325e');                          // window, rainy night
  put(14, 14, 18, 3, '#1e2850');
  for (let i = 0; i < 16; i++) {
    const x = 14 + ((hash(i, 7) * 18 + T * 3) % 18), y = 14 + ((hash(i, 8) * 20 + T * 26) % 20);
    put(x, y, 1, 2, '#8fa8dc');
  }
  put(22, 14, 2, 20, '#7a4a2c'); put(14, 23, 18, 2, '#7a4a2c');
  put(11, 34, 24, 2, '#9a6a44');                                                           // sill
  for (const cx of [10, 33]) { put(cx, 11, 3, 25, '#c95a5a'); put(cx + 1, 11, 1, 25, '#a84646'); }
  put(10, 10, 26, 1, '#6a3e24');
  put(67, 25, 1, 31, '#4a3426'); put(64, 55, 7, 2, '#4a3426');                             // floor lamp
  [[66, 15, 3], [65, 16, 5], [64, 17, 7], [63, 18, 9], [62, 19, 11], [62, 20, 11]].forEach(([x, y, w]) => put(x, y, w, 1, '#ffcf73'));
  put(62, 21, 11, 1, '#e8a94a'); put(65, 22, 5, 1, '#fff3c8');
  put(13, 50, 8, 7, '#c9623a'); put(12, 49, 10, 2, '#e07a4a'); put(14, 56, 6, 1, '#a24a2a');   // plant
  for (let i = 0; i < 5; i++) {
    const a = -1.2 + i * 0.6, sw = Math.sin(t * 1.5 + i) * 0.6;
    spr(LEAF, 15 + Math.sin(a) * 5 + sw, 44 - Math.cos(a) * 4 - (i % 2) * 2, { g: '#4e9a4a', G: '#7cc46a' });
  }
  disc(63, 66, 3, '#6f8fe0'); put(61, 65, 4, 1, '#4a68b8'); put(62, 67, 3, 1, '#4a68b8');   // yarn ball + loose thread
  put(66, 68, 4, 1, '#6f8fe0'); put(70, 69, 3, 1, '#6f8fe0');

  // the story: six bites empty the bowl, he looks up (?), it sparkles full again, a big happy heart
  let dip = 0, mood = 'open', look = 1, food = 3, blush = false, swish = 1;
  if (T < 3.6) {
    const bite = Math.floor(T / 0.6), b = (T % 0.6) / 0.6;
    dip = Math.round(7 * Math.sin(Math.PI * Math.min(1, b / 0.8)));
    if (b > 0.45 && b < 0.8) dip -= Math.floor(b * 20) % 2;                                  // chewing
    mood = 'happy';
    food = 3 - Math.floor((bite + (b > 0.5 ? 1 : 0)) / 2);
  } else if (T < 4.6) { food = 0; look = T < 4.0 || T > 4.3 ? 1 : -1; }
  else if (T < 5.6) food = Math.min(3, Math.floor((T - 4.6) * 4));
  else { mood = 'happy'; blush = true; swish = 2.5; }
  const bx = 32, by = 59;
  const pts = [];                                                                           // tail curls up his right side
  for (let i = 1; i <= 10; i++) pts.push([bx + 14 + i * 0.75 - (i > 6 ? (i - 6) * 1.1 : 0) + Math.sin(t * 2 * swish - i * 0.5) * i * 0.14, by + 9 - i * 1.05]);
  tail(pts, Object.assign({}, BOB, { fluffy: true, stripe: BOB.tail }));
  spr(BOB_SIT, bx, by, BOB.pal);
  spr(BOB_HEAD, bx + 1, by - 19 + dip, eyesFor(BOB, look, mood, blush || dip > 4));
  const kib = food > 0 ? '#9a5a28' : '#2a3f7a';
  spr(BOWL, 33, 65, { k: '#1f2a4a', R: '#9fc0ff', i: kib, B: '#4f7fd8', W: '#ffffff' });
  [[35, 11], [37, 7], [39, 3]].forEach(([x, w], i) => {
    if (food > i) for (let k = 0; k < w; k++) put(x + k, 64 - i, 1, 1, hash(k, i) > 0.5 ? '#9a5a28' : '#c98a4a');
  });
  if (T < 3.6) {                                                                            // crumbs fly out on each bite
    const bite = Math.floor(T / 0.6), b = (T % 0.6) / 0.6;
    if (b > 0.45) for (let k = 0; k < 2; k++) {
      const u = (b - 0.45) / 0.55, side = k ? 1 : -1, sp = 4 + hash(bite, k) * 5;
      put(40 + side * (3 + u * sp), 63 - 8 * u + 10 * u * u, 1, 1, '#c98a4a');
    }
  }
  if (T >= 3.8 && T < 4.6) spr(QMARK, 50, 34, { w: '#2a2622' });
  if (T >= 4.6 && T < 5.8) for (let k = 0; k < 4; k++) {
    const ph = (T * 3 + k * 0.37) % 1;
    sparkle(34 + hash(k, 11) * 13, 58 + hash(k, 12) * 6 - ph * 4, ph < 0.5 ? 1 : 0, ph < 0.5 ? '#fff6a8' : '#ffffff');
  }
  if (T >= 5.6) { const k = (T - 5.6) / 1.0; spr(HEART_BIG, 49, 36 - k * 8, HEART_PAL); }
}

// ================= 3. Sky: Bob paddles through the stars with the fish =================
const SKY_T = 6.4;
const SSKY = ['#1b1440', '#221852', '#2c1d63', '#3a2373', '#4c2a82', '#62338c', '#7a3d91', '#8a4596', '#9a4f98', '#a85a96'];
const FISHES = [['#ffb020', 22, 8, 0], ['#ff7aa2', 46, 5, 0.33], ['#7fd1f7', 30, 11, 0.66], ['#ffe066', 58, 7, 0.15]];

function sky(t) {
  const T = t % SKY_T;
  SSKY.forEach((c, i) => put(0, i * 8, N, 8, c));
  for (let i = 0; i < 50; i++) {
    const x = (hash(i, 1) * N + t * 2) % N, y = hash(i, 2) * 70 | 0, tw = Math.sin(t * 2.2 + i * 1.3);
    if (tw > -0.3) put(x, y, 1, 1, tw > 0.8 ? '#ffffff' : '#c9c2ff');
  }
  disc(22, 18, 7, '#fff3c4'); disc(25, 16, 6, SSKY[2]);                                     // crescent moon
  for (const [y, sp, w] of [[24, 4, 14], [58, 7, 18], [12, 2.5, 10]]) {                       // clouds drift past
    const x = N - ((t * sp + y * 3) % (N + w + 10));
    put(x, y, w, 3, '#8c7fd1'); put(x + 3, y - 2, w - 7, 2, '#8c7fd1'); put(x + 1, y + 3, w - 2, 1, '#6f63b4');
  }
  for (const [col, y0, sp, ph] of FISHES) {                                                   // fish swim the other way
    const x = N + 6 - ((t * sp + ph * (N + 14)) % (N + 14)), y = y0 + Math.sin(t * 2 + ph * 9) * 2;
    spr(FISH, x, y, { x: col, e: '#1b1440' });
    if (Math.sin(t * 9 + ph * 7) > 0) put(x + 7, y + 1, 1, 1, col); else { put(x + 7, y, 1, 1, col); put(x + 7, y + 2, 1, 1, col); }
  }
  const f = Math.floor(t * 6) % 4, bob = Math.round(Math.sin(t * 1.6) * 3);
  const happy = T > 3.6 && T < 5.2;
  const [hx, hy] = walker(BOB, 24, 58 + bob, 'walk', f, 1, happy ? 'happy' : 'open', happy, t);   // paddling in the air
  if (happy) { const k = (T - 3.6) / 1.6; if (k < 0.85 || Math.floor(T * 12) % 2) spr(HEART, hx + 9, hy - 2 - k * 7, HEART_PAL); }
  for (let i = 0; i < 3; i++) {                                                               // stardust trail behind him
    const ph = (t * 1.5 + i / 3) % 1;
    put(22 - ph * 12, 50 + bob + i * 2 + ph * 3, 1, 1, ph < 0.5 ? '#fff6a8' : '#c9c2ff');
  }
}

const SCENES = { city, home, sky };
const DREAM = {
  N, SCENES: Object.keys(SCENES),
  PERIOD: { city: CITY_T, home: HOME_T, sky: SKY_T },
  KEY: { city: 5.8, home: 6.0, sky: 4.2 },   // a still that tells the story, for reduced motion
  TITLE: { city: 'roaming the city at night with a friend', home: 'a full food bowl at home', sky: 'paddling through the stars with the fish' },
  frame(scene, t) { SCENES[scene](t); return buf; }
};
if (typeof module !== 'undefined') module.exports = DREAM; else window.DREAM = DREAM;
})();
