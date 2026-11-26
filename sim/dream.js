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

// look: +1 right, -1 left. mood: 'open' | 'shut' | 'happy' (^ ^)
function eyesFor(cat, look, mood, blush) {
  const p = Object.assign({}, cat.pal);
  if (blush) p.q = cat.blush;
  const E = cat.eye, L = cat.lid;
  if (mood === 'open') Object.assign(p, { x: look > 0 ? cat.shine : E, y: look > 0 ? E : cat.shine, a: E, b: E, f: E, c: L, d: E });
  else if (mood === 'happy') Object.assign(p, { x: L, a: E, y: L, b: E, f: L, c: L, d: L });
  else Object.assign(p, { x: L, a: L, y: L, b: E, f: E, c: L, d: L });
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
  return [hx + (cat.head[0].length >> 1), hyy];       // top-centre of the head, for hearts
}

const HEART = ['.r.r.', 'rrrrr', 'rrrrr', '.rrr.', '..r..'];
const HEART_BIG = ['.rr.rr.', 'rhrrrrr', 'rrrrrrr', 'rrrrrrr', '.rrrrr.', '..rrr..', '...r...'];
const HEART_PAL = { r: '#ff4f7e', h: '#ffd0dc' };
function sparkle(x, y, k, col) { put(x, y - k, 1, 2 * k + 1, col); put(x - k, y, 2 * k + 1, 1, col); }

// ================= 1. City night: a long rooftop walk with her, then they sit and watch the full moon =================
// The camera sits far back here, so both cats are small sprites of their own and the whole skyline fits.
const BS = {   // Bob, small: tall pink ears, white heart face, grey fur, big dark eyes
  pal: { k: '#2a2622', g: '#8f8a84', l: '#b9b3ab', w: '#ffffff', p: '#e46aa0', r: '#d9d4e6' },
  head: [
    '.k.......k.',
    'kpk.....kpk',
    'kpk.....kpk',
    'kppk...kppk',
    'kgppkkkppgk',
    'kgwwwgwwwgk',
    'kwwwwwwwwwk',
    'kwxawwwxawk',
    'kwbbwwwbbwk',
    'kgwwwpwwwgk',
    '.kgwwwwwgk.',
    '..kgwwwgk..',
    '...kgwgk...',
    '....kkk....'],
  side: [
    '..kkkkkkkk..',
    '.kglllllggk.',
    'kgggggggggwk',
    '.kwwwwwwwwk.'],
  back: [            // sitting, seen from behind, moonlight catching his edges
    '..k.......k..',
    '.krk.....krk.',
    '.krk.....krk.',
    '.krgk...kgrk.',
    '.krgpkkkpgrk.',
    '.krrrrrrrrrk.',
    'krgggggggggrk',
    'kgggggggggggk',
    '.kgggggggggk.',
    '..kkgggggkk..',
    '..krgggggrk..',
    '.krggglgggrk.',
    '.kgggglggggk.',
    'kgggggggggggk',
    'kgggggggggggk',
    'kgggggggggggk',
    '.kkkkkkkkkkk.'],
  hx: 4, hy: -11, legs: [2, 3, 8, 9], legLen: 3, near: '#e9e5df', far: '#6f6a64', paw: '#ffffff', tail: '#8f8a84' };
const GS = {   // her, small: ginger tabby, cream muzzle, short round ears, green eyes, teal bow
  pal: { k: '#3a2418', o: '#f39a4a', d: '#c8622a', c: '#ffe7c7', p: '#ff8fa8', b: '#2fc4b2', B: '#16807a', r: '#ffc890' },
  head: [
    '.k.....k.',
    'kpk...kpk',
    'kookkkook',
    'kodododok',
    'koooooook',
    'kxyoooxyk',
    'koccpccok',
    '.kccccck.',
    '..kkkkk..'],
  side: [
    '..kkkkkk..',
    '.kodoodok.',
    'koooooocck',
    '.kcccccck.'],
  back: [
    '..k.....k..',
    '.krk...krk.',
    '.krokkkork.',
    'krrrrrrrrrk',
    'koooodooook',
    'koooodooook',
    '.koooooook.',
    '..kkoookk..',
    '.krooooork.',
    'kddoooooddk',
    'koooooooook',
    'kddoooooddk',
    'koooooooook',
    '.kkkkkkkkk.'],
  hx: 3, hy: -6, legs: [2, 3, 6, 7], legLen: 2, near: '#f39a4a', far: '#b0561f', paw: '#ffe7c7', tail: '#f39a4a', stripe: '#c8622a' };
const BOW_S = ['b.b', 'bBb'];
const FISH = ['..xxx.x', '.xexxxx', '..xxx.x'];   // the billboard here, and the fish in the sky dream
const DARK_EYE = '#1e1a18', IRIS = '#7ccf4a';

function smallEyes(cat, look, mood) {
  const p = Object.assign({}, cat.pal);
  if (cat === BS) Object.assign(p, mood === 'open' ? { x: DARK_EYE, a: DARK_EYE, b: DARK_EYE } : { x: p.w, a: p.w, b: DARK_EYE });
  else Object.assign(p, mood === 'open' ? (look > 0 ? { x: IRIS, y: DARK_EYE } : { x: DARK_EYE, y: IRIS }) : { x: p.d, y: p.d });
  return p;
}
function tailS(pts, cat) {   // outline pass, then a 1 px fill, striped if she has stripes
  for (const [x, y] of pts) put(x - 1, y - 1, 3, 3, cat.pal.k);
  pts.forEach(([x, y], i) => put(x, y, 1, 1, cat.stripe && i % 3 === 2 ? cat.stripe : cat.tail));
}
const STEP_S = [1, 0, -1, 0];
function smallWalker(cat, bx, ground, f, moving, look, mood, t) {   // side-on body, head turned to you
  const by = ground - cat.side.length - cat.legLen - (moving && f % 2 ? 1 : 0);
  const sway = Math.sin(t * 3) * (moving ? 0.7 : 1.3), pts = [];
  for (let i = 1; i <= 6; i++) pts.push([bx + 1 - i * 0.5 + Math.sin(t * 2.5 - i * 0.5) * i * 0.15 * sway, by + 1 - i * 0.9 + (i > 4 ? (i - 4) * 0.6 : 0)]);
  tailS(pts, cat);
  const top = by + cat.side.length;
  const leg = (i, col, paw) => {   // legs 0 near back, 1 far back, 2 near front, 3 far front; diagonal pairs step together
    const ph = (f + (i === 0 || i === 3 ? 0 : 2)) % 4, dx = moving ? STEP_S[ph] : 0, len = ground - top - (moving && ph === 3 ? 1 : 0);
    for (let j = 0; j < len; j++) put(bx + cat.legs[i] + Math.round(dx * j / Math.max(1, len - 1)), top + j, 1, 1, j === len - 1 ? paw : col);
  };
  leg(1, cat.far, cat.far); leg(3, cat.far, cat.far);
  spr(cat.side, bx, by, cat.pal);
  leg(0, cat.near, cat.paw); leg(2, cat.near, cat.paw);
  const hx = bx + cat.hx, hy = by + cat.hy;
  spr(cat.head, hx, hy, smallEyes(cat, look, mood));
  if (cat === GS) spr(BOW_S, hx + 6, hy, cat.pal);
}

const CITY_T = 16, WALK_V = 11, WALK_END = 8.4, BRAKE = 0.7, SIT_AT = 9.8;
const scrollAt = T => T < WALK_END ? WALK_V * T : WALK_V * (WALK_END + BRAKE * (u => u - u * u / 2)(clamp01((T - WALK_END) / BRAKE)));
const G = 66, MOON = [40, 21, 10];
const CSKY = ['#0b0f2a', '#0e1332', '#11173b', '#151b45', '#1a1f4f', '#20245a', '#272a64', '#302f6d', '#3a3474', '#453a7a'];
const TANK = ['..aaa..', '.aaaaa.', 'abbbbba', 'aaaaaaa', 'abbbbba', 'aaaaaaa', '.a...a.', '.a...a.'];
// their tails meet between them and curl up into a heart: Bob's grey makes one side, hers the other
const TAIL_B = [[36, -2], [37, -1], [38, -1], [39, -2], [40, -3], [41, -4], [42, -5], [43, -6], [43, -7], [42, -8], [41, -8], [40, -7]];
const TAIL_G = TAIL_B.map(([x, y]) => [80 - x, y]);
const lazy = (pts, dir) => pts.map(([x, y], i) => [pts[0][0] + dir * i * 0.45, -1 - i * 0.45]);   // the same tail, loosely raised

function city(t) {
  const T = t % CITY_T, S = scrollAt(T);
  CSKY.forEach((c, i) => put(0, i * 7, N, 7, c));
  for (let i = 0; i < 70; i++) {                                                          // stars, none in front of the moon
    const x = hash(i, 1) * N | 0, y = hash(i, 2) * 46 | 0, tw = Math.sin(t * 2.1 + i * 1.7);
    if (Math.hypot(x - MOON[0], y - MOON[1]) < 16 || tw < -0.5) continue;
    if (i % 9 === 0 && tw > 0.6) sparkle(x, y, 1, '#c9ceff');
    put(x, y, 1, 1, tw > 0.8 ? '#ffffff' : i % 3 ? '#8a90c8' : '#c9ceff');
  }
  if (T > 12.6 && T < 13.1) {                                                             // one shooting star while they sit
    const u = (T - 12.6) / 0.5;
    for (let k = 0; k < 6; k++) { const v = u - k * 0.04; if (v > 0) put(70 - v * 18, 5 + v * 9, 1, 1, k ? '#8a90c8' : '#ffffff'); }
  }
  const [mx, my, mr] = MOON;                                                              // big full moon, soft glow
  for (let y = -mr - 5; y <= mr + 5; y++) for (let x = -mr - 5; x <= mr + 5; x++) {
    const d = Math.hypot(x, y);
    if (d < mr + 2.5 || (d < mr + 5 && (x + y) % 2 === 0)) put(mx + x, my + y, 1, 1, d < mr + 2.5 ? '#3a3f86' : '#2a2f6e');
  }
  disc(mx, my, mr, '#fff1c4');
  for (let y = -mr; y <= mr; y++) for (let x = -mr; x <= mr; x++) {                      // shaded right limb
    const d = x * x + y * y;
    if (d <= mr * mr + mr && Math.hypot(x - 3, y + 2) > mr - 0.5) put(mx + x, my + y, 1, 1, '#ecdca4');
  }
  [[-4, -3, 3, 2], [2, 3, 3, 2], [-2, 4, 2, 1], [4, -4, 2, 1], [-6, 1, 1, 2]].forEach(([x, y, w, h]) => put(mx + x, my + y, w, h, '#e2d096'));
  put(mx - 5, my - 6, 2, 1, '#fffbe8'); put(mx - 6, my - 5, 1, 2, '#fffbe8');

  const far = S * 0.1;                                                                    // far skyline, hazy
  for (let c = Math.floor(far / 6) - 1; c <= Math.floor((far + N) / 6) + 1; c++) {
    const x = c * 6 - far, w = 5 + (hash(c, 3) * 3 | 0), tall = hash(c, 13) > 0.7 && (c * 6 < 18 || c * 6 > 64), top = (tall ? 27 : 36) + (hash(c, 4) * 11 | 0);
    put(x, top, w, G - top, '#1f2656');
    if (tall) { put(x + 1, top - 2, w - 2, 2, '#1f2656'); put(x + (w >> 1), top - 7, 1, 5, '#1f2656'); if (Math.sin(t * 3 + c) > 0.2) put(x + (w >> 1), top - 8, 1, 1, '#ff5a5a'); }
    else if (hash(c, 5) > 0.72) put(x + 2, top - 3, 1, 3, '#1f2656');
    for (let wy = top + 2; wy < G; wy += 3) for (let wx = 1; wx < w - 1; wx += 2) if (hash(c * 13 + wx, wy) > 0.84) put(x + wx, wy, 1, 1, '#8c7f6a');
  }
  const mid = S * 0.3;                                                                    // middle blocks: water tanks, many small windows, neon
  for (let c = Math.floor(mid / 13) - 1; c <= Math.floor((mid + N) / 13) + 1; c++) {
    const x = c * 13 - mid, w = 9 + (hash(c, 6) * 4 | 0), top = 39 + (hash(c, 7) * 14 | 0);
    put(x, top, w, G - top, '#171c46'); put(x, top - 1, w, 1, '#2b3170'); put(x, top, 1, G - top, '#232a60');
    for (let wy = top + 2; wy < G; wy += 2) for (let wx = 2; wx < w - 1; wx += 2) {
      const h = hash(c * 17 + wx, wy);
      if (h > 0.7) put(x + wx, wy, 1, 1, h > 0.96 ? '#9fd8ff' : h > 0.85 ? '#ffdf8a' : '#f2b24a');
    }
    const roof = hash(c, 8);
    if (roof > 0.55) spr(TANK, x + ((w - 7) >> 1), top - 9, { a: '#3d4488', b: '#272d66' });
    else if (roof > 0.3) { put(x + w - 3, top - 5, 1, 5, '#2b3170'); put(x + w - 5, top - 4, 5, 1, '#2b3170'); }
    if (hash(c, 9) > 0.62) {                                                              // vertical neon blade sign, flickers
      const on = Math.sin(t * 6 + c * 2) > -0.8 || Math.sin(t * 1.1 + c) > 0.6, col = hash(c, 10) > 0.5 ? '#ff6fae' : '#4fe3d0';
      put(x - 1, top + 3, 3, 9, '#2a1430');
      for (let k = 0; k < 4; k++) put(x, top + 4 + k * 2, 1, 1, on ? col : '#4a2a4a');
    }
  }
  const near = S * 0.55;                                                                  // near rooftops, a fish billboard
  for (let c = Math.floor(near / 22) - 1; c <= Math.floor((near + N) / 22) + 1; c++) {
    const x = c * 22 - near, w = 15 + (hash(c, 11) * 5 | 0), top = 54 + (hash(c, 12) * 5 | 0);
    put(x, top, w, G - top, '#100d28'); put(x, top - 1, w, 1, '#221d48');
    for (let wy = top + 3; wy < G - 1; wy += 4) for (let wx = 2; wx < w - 2; wx += 4) if (hash(c * 7 + wx, wy) > 0.6) put(x + wx, wy, 2, 2, '#e8a640');
    if (((c % 3) + 3) % 3 === 1) {
      const on = Math.sin(t * 5 + c) > -0.75;
      put(x + 3, top - 9, 1, 8, '#221d48'); put(x + 13, top - 9, 1, 8, '#221d48');
      put(x + 2, top - 13, 13, 6, '#2a1430'); put(x + 2, top - 13, 13, 1, '#4a2450');
      spr(FISH, x + 5, top - 11, { x: on ? '#ff6fae' : '#6a3456', e: '#2a1430' });
    }
  }
  put(0, G, N, 1, '#8b7fae'); put(0, G + 1, N, 1, '#5a4c7c'); put(0, G + 2, N, N - G - 2, '#2b2244');   // our rooftop ledge
  for (let y = G + 4; y < N; y += 3) {
    put(0, y, N, 1, '#221a38');
    for (let x = -((S + (y % 2) * 3) % 6); x < N; x += 6) put(x, y + 1, 1, 2, '#221a38');
  }
  for (let c = Math.floor(S / 19) - 1; c <= Math.floor((S + N) / 19) + 1; c++) {          // things on our roof, behind the cats
    const x = c * 19 - S + 6, k = hash(c, 30);
    if (k < 0.3) { put(x, G - 5, 2, 5, '#5a5080'); put(x - 1, G - 6, 4, 1, '#7a6ea4'); }
    else if (k < 0.5) { put(x, G - 7, 4, 7, '#7a3e34'); put(x - 1, G - 8, 6, 1, '#a89a8a'); put(x, G - 4, 4, 1, '#5a2c24'); }
    else if (k < 0.65) { put(x, G - 4, 7, 4, '#4c4468'); put(x, G - 4, 7, 1, '#6c6490'); put(x + 1, G - 3, 2, 2, '#2e2844'); }
  }

  const sit = T >= SIT_AT, f = Math.floor(S / 2.4) % 4, moving = T < WALK_END + BRAKE;
  if (!sit) {
    const glance = !moving;                                                               // stopped: a look at each other
    const blinkB = (T % 3.3) < 0.12, blinkG = ((T + 1.4) % 2.9) < 0.12;
    smallWalker(BS, 22, G, f, moving, 1, blinkB ? 'shut' : 'open', t);
    smallWalker(GS, 41, G, (f + 1) % 4, moving, glance ? -1 : 1, blinkG ? 'shut' : 'open', t);
  } else {
    const dy = T < SIT_AT + 0.1 ? -2 : T < SIT_AT + 0.2 ? -1 : 0;                         // settle down onto the ledge
    spr(BS.back, 24, G - BS.back.length + dy, BS.pal);
    spr(GS.back, 45, G - GS.back.length + dy, GS.pal);
    spr(BOW_S, 53, G - GS.back.length + dy + 2, GS.pal);                                  // on her right ear
    const k = ease(clamp01((T - SIT_AT - 0.6) / 1.8)), wob = Math.sin(t * 2.2);
    const curl = (to, dir) => { const from = lazy(to, dir); return to.map(([x, y], i) => {
      const u = clamp01(k * 1.6 - (i / to.length) * 0.6);
      return [Math.round(from[i][0] + (x - from[i][0]) * u + (i > 6 ? dir * wob * (1 - k) : 0)), Math.round(G + from[i][1] + (y - from[i][1]) * u)];
    }); };
    const line = (pts, col) => pts.forEach(([x, y]) => put(x, y, 1, 1, col));   // no outline: at this size it swallows the shape
    line(curl(TAIL_G, -1), GS.tail);
    line(curl(TAIL_B, 1), BS.pal.l);
  }
  const fade = Math.min(1, T / 0.35, (CITY_T - T) / 0.6);                                  // soft loop: dark in, dark out
  if (fade < 1) for (let i = 0; i < buf.length; i += 4) { buf[i] = 8 + (buf[i] - 8) * fade; buf[i + 1] = 10 + (buf[i + 1] - 10) * fade; buf[i + 2] = 30 + (buf[i + 2] - 30) * fade; }
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
  KEY: { city: 13.0, home: 6.0, sky: 4.2 },   // a still that tells the story, for reduced motion
  TITLE: { city: 'a rooftop walk with a friend, then the full moon', home: 'a full food bowl at home', sky: 'paddling through the stars with the fish' },
  frame(scene, t) { SCENES[scene](t); return buf; }
};
if (typeof module !== 'undefined') module.exports = DREAM; else window.DREAM = DREAM;
})();
