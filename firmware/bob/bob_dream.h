// Bob's dream world, ported from sim/dream.js: three pixel stories on an 80x80 grid (3 screen px each).
// No pictures: every frame is drawn from short sprite strings and rectangles, because the flash is nearly full.
// Plain C++ with no Arduino calls, so firmware/dream_check/ can build it on a PC and diff it against dream.js.
//   dream::frame(scene, t) fills dream::buf (80*80 RGB565) with that scene at t seconds. 0 city, 1 home, 2 sky.
#pragma once
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <initializer_list>

namespace dream {

const int N = 80, SCENES = 3;
uint16_t buf[N * N];

constexpr uint16_t C(uint32_t h) { return ((h >> 8) & 0xF800) | ((h >> 5) & 0x07E0) | ((h >> 3) & 0x001F); }
static inline int rnd(float v) { return (int)floorf(v + 0.5f); }   // Math.round
static inline float clamp01(float x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
static inline float ease(float x) { return x < 0.5f ? 2 * x * x : 1 - 2 * (1 - x) * (1 - x); }
static inline float hyp(float x, float y) { return sqrtf(x * x + y * y); }

static void put(float fx, float fy, int w, int h, uint16_t c) {
  int x = rnd(fx), y = rnd(fy);
  int x0 = x < 0 ? 0 : x, x1 = x + w > N ? N : x + w, y0 = y < 0 ? 0 : y, y1 = y + h > N ? N : y + h;
  for (int j = y0; j < y1; j++) for (int i = x0; i < x1; i++) buf[j * N + i] = c;
}
static double hsh(int a, int b = 0) {   // stable 0..1 noise, same as dream.js
  uint32_t h = (uint32_t)a * 374761393u + (uint32_t)b * 668265263u;
  h = (h ^ (h >> 13)) * 1274126177u;
  return (double)(h ^ (h >> 16)) / 4294967296.0;
}

struct Pal {   // sprite char -> colour; -1 = see-through
  int32_t c[128];
  Pal() { for (auto &v : c) v = -1; }
  Pal(const char *keys, std::initializer_list<uint32_t> cols) : Pal() { const uint32_t *p = cols.begin(); for (; *keys; keys++) c[(int)*keys] = C(*p++); }
  Pal &s(char k, uint16_t v) { c[(int)k] = v; return *this; }
  uint16_t operator[](char k) const { return c[(int)k]; }
};
static void spr(const char *const *rows, int n, float fx, float fy, const Pal &p) {
  int x = rnd(fx), y = rnd(fy);
  for (int r = 0; r < n; r++) for (int c = 0; rows[r][c]; c++) { int32_t v = p.c[rows[r][c] & 127]; if (v >= 0) put(x + c, y + r, 1, 1, v); }
}
#define SPR(a, x, y, p) spr(a, sizeof(a) / sizeof(*a), x, y, p)
static void disc(int cx, int cy, int r, uint16_t col) { for (int y = -r; y <= r; y++) for (int x = -r; x <= r; x++) if (x * x + y * y <= r * r + r) put(cx + x, cy + y, 1, 1, col); }
static void sparkle(float x, float y, int k, uint16_t col) { put(x, y - k, 1, 2 * k + 1, col); put(x - k, y, 2 * k + 1, 1, col); }

enum { OPEN, SHUT, HAPPY };
const uint16_t WHITE = C(0xffffff);

// ---- Bob, big (home and sky) ----
const char *const BOB_HEAD[] = {
  ".k...........k.", ".kk.........kk.", ".kpk.......kpk.", ".kpk.......kpk.", "kgpk.......kpgk", "kgpk.......kpgk",
  "kgppk.....kppgk", "kgppgk...kgppgk", "kgppgkkkkkgppgk", "kgwwwwwgwwwwwgk", "kwwwwwwwwwwwwwk", "kwwxaywwwxaywwk",
  "kwwbfbwwwbfbwwk", "kwwcdcwwwcdcwwk", "kgqwwwwpwwwwqgk", ".kgwwwkwkwwwgk.", "..kgwwwwwwwgk..", "...kgwwwwwgk...",
  "....kgwwwgk....", ".....kgwgk.....", "......kwk......"};
const char *const BOB_SIDE[] = {"..kkkkkkkkkk...", ".kllllllllllk..", ".klllllllllwwk.", ".kwwwwwwwwwwwk.", "..kwwwwwwwwwk..", "...kkkkkkkkk..."};
const char *const BOB_SIT[] = {
  ".....kwwwwwk.....", "....kgwwwwwgk....", "...kggwwwwwggk...", "...kgwwwwwwwgk...", "..kggwwwwwwwggk..", "..kgwkwwkwwkwgk..",
  ".kggwkwwkwwkwggk.", ".kgwwkwwkwwkwwgk.", "kgwwwkwwkwwkwwwgk", "kppwwkwwkwwkwwppk", ".kkkkkkkkkkkkkkk."};
const Pal BOB_PAL("kglwpq", {0x2a2622, 0x8f8a84, 0xd6d1ca, 0xffffff, 0xe46aa0, 0xffffff});
const uint16_t B_EYE = C(0x1e1a18), B_BLUSH = C(0xf7a8c8), B_LEGN = C(0xe9e5df), B_GREY = C(0x8f8a84);

static Pal eyesFor(int look, int mood, bool blush) {
  Pal p = BOB_PAL;
  if (blush) p.s('q', B_BLUSH);
  const uint16_t E = B_EYE, L = WHITE;
  if (mood == OPEN) p.s('x', look > 0 ? WHITE : E).s('y', look > 0 ? E : WHITE).s('a', E).s('b', E).s('f', E).s('c', L).s('d', E);
  else if (mood == HAPPY) p.s('x', L).s('a', E).s('y', L).s('b', E).s('f', L).s('c', L).s('d', L);
  else p.s('x', L).s('a', L).s('y', L).s('b', E).s('f', E).s('c', L).s('d', L);
  return p;
}
static void tail(const float (*pts)[2], int n, int t, uint16_t col) {   // outline pass, then fill pass
  for (int i = 0; i < n; i++) put(pts[i][0] - 1, pts[i][1] - 1, t + 2, t + 2, BOB_PAL['k']);
  for (int i = 0; i < n; i++) put(pts[i][0], pts[i][1], t, t, col);
}
static void leg(int x, int y, int len, int dx, uint16_t col, uint16_t paw) {
  for (int i = 0; i < len; i++) put(x + rnd((float)dx * i / (len - 1 > 1 ? len - 1 : 1)), y + i, 2, 1, i == len - 1 ? paw : col);
}
// Bob seen from the side, walking (head turned to you). Returns the top-centre of his head in hx, hy.
static void walker(int bx, int ground, int f, int look, int mood, bool blush, float t, int &hx, int &hy) {
  static const int STEP[4] = {2, 0, -2, 0};
  int by = ground - 10 - f % 2, lens[4], dxs[4];
  const int offs[4] = {0, 2, 2, 0};
  for (int k = 0; k < 4; k++) { int i = (f + offs[k]) % 4; lens[k] = ground - (by + 5) - (i == 3 ? 1 : 0); dxs[k] = STEP[i]; }
  float sway = sinf(t * 3) * 0.8f, pts[8][2];
  for (int i = 1; i <= 8; i++) { pts[i - 1][0] = bx + 1 - i * 0.5f + sinf(t * 2.5f - i * 0.45f) * i * 0.12f * sway; pts[i - 1][1] = by + 1 - i * 0.95f + (i > 6 ? (i - 6) * 0.4f : 0); }
  tail(pts, 8, 1, B_GREY);
  leg(bx + 4, by + 5, lens[0], dxs[0], B_GREY, B_GREY);
  leg(bx + 12, by + 5, lens[1], dxs[1], B_GREY, B_GREY);
  SPR(BOB_SIDE, bx, by, BOB_PAL);
  leg(bx + 2, by + 5, lens[2], dxs[2], B_LEGN, WHITE);
  leg(bx + 10, by + 5, lens[3], dxs[3], B_LEGN, WHITE);
  hx = bx + 5; hy = by - 17;
  SPR(BOB_HEAD, hx, hy, eyesFor(look, mood, blush));
  hx += 7;
}

const char *const HEART[] = {".r.r.", "rrrrr", "rrrrr", ".rrr.", "..r.."};
const char *const HEART_BIG[] = {".rr.rr.", "rhrrrrr", "rrrrrrr", "rrrrrrr", ".rrrrr.", "..rrr..", "...r..."};
const Pal HEART_PAL("rh", {0xff4f7e, 0xffd0dc});
const char *const FISH[] = {"..xxx.x", ".xexxxx", "..xxx.x"};

// ================= 1. City night: a long rooftop walk with her, then they sit and watch the full moon =================
struct Small {
  const char *const *head; int headN; const char *const *side; int sideN; const char *const *back; int backN;
  Pal pal; int hx, hy, legs[4], legLen; uint16_t nr, fr, paw, tail, stripe; bool bob;
};
const char *const BS_HEAD[] = {".k.......k.", "kpk.....kpk", "kpk.....kpk", "kppk...kppk", "kgppkkkppgk", "kgwwwgwwwgk", "kwwwwwwwwwk",
  "kwxawwwxawk", "kwbbwwwbbwk", "kgwwwpwwwgk", ".kgwwwwwgk.", "..kgwwwgk..", "...kgwgk...", "....kkk...."};
const char *const BS_SIDE[] = {"..kkkkkkkk..", ".kglllllggk.", "kgggggggggwk", ".kwwwwwwwwk."};
const char *const BS_BACK[] = {"..k.......k..", ".krk.....krk.", ".krk.....krk.", ".krgk...kgrk.", ".krgpkkkpgrk.", ".krrrrrrrrrk.",
  "krgggggggggrk", "kgggggggggggk", ".kgggggggggk.", "..kkgggggkk..", "..krgggggrk..", ".krggglgggrk.", ".kgggglggggk.",
  "kgggggggggggk", "kgggggggggggk", "kgggggggggggk", ".kkkkkkkkkkk."};
const char *const GS_HEAD[] = {".k.....k.", "kpk...kpk", "kookkkook", "kodododok", "koooooook", "kxyoooxyk", "koccpccok", ".kccccck.", "..kkkkk.."};
const char *const GS_SIDE[] = {"..kkkkkk..", ".kodoodok.", "koooooocck", ".kcccccck."};
const char *const GS_BACK[] = {"..k.....k..", ".krk...krk.", ".krokkkork.", "krrrrrrrrrk", "koooodooook", "koooodooook", ".koooooook.",
  "..kkoookk..", ".krooooork.", "kddoooooddk", "koooooooook", "kddoooooddk", "koooooooook", ".kkkkkkkkk."};
#define LEN(a) (int)(sizeof(a) / sizeof(*a))
const Small BS = {BS_HEAD, LEN(BS_HEAD), BS_SIDE, LEN(BS_SIDE), BS_BACK, LEN(BS_BACK),
  Pal("kglwpr", {0x2a2622, 0x8f8a84, 0xb9b3ab, 0xffffff, 0xe46aa0, 0xd9d4e6}), 4, -11, {2, 3, 8, 9}, 3,
  C(0xe9e5df), C(0x6f6a64), C(0xffffff), C(0x8f8a84), 0, true};
const Small GS = {GS_HEAD, LEN(GS_HEAD), GS_SIDE, LEN(GS_SIDE), GS_BACK, LEN(GS_BACK),
  Pal("kodcpbBr", {0x3a2418, 0xf39a4a, 0xc8622a, 0xffe7c7, 0xff8fa8, 0x2fc4b2, 0x16807a, 0xffc890}), 3, -6, {2, 3, 6, 7}, 2,
  C(0xf39a4a), C(0xb0561f), C(0xffe7c7), C(0xf39a4a), C(0xc8622a), false};
const char *const BOW_S[] = {"b.b", "bBb"};
const uint16_t DARK_EYE = C(0x1e1a18), IRIS = C(0x7ccf4a);

static void smallWalker(const Small &cat, int bx, int ground, int f, bool moving, int look, int mood, float t) {
  static const int STEP_S[4] = {1, 0, -1, 0};
  int by = ground - cat.sideN - cat.legLen - (moving && f % 2 ? 1 : 0);
  float sway = sinf(t * 3) * (moving ? 0.7f : 1.3f);
  for (int pass = 0; pass < 2; pass++) for (int i = 1; i <= 6; i++) {   // tail: outline pass, then 1 px fill, striped if she has stripes
    float x = bx + 1 - i * 0.5f + sinf(t * 2.5f - i * 0.5f) * i * 0.15f * sway, y = by + 1 - i * 0.9f + (i > 4 ? (i - 4) * 0.6f : 0);
    if (pass == 0) put(x - 1, y - 1, 3, 3, cat.pal['k']);
    else put(x, y, 1, 1, cat.stripe && (i - 1) % 3 == 2 ? cat.stripe : cat.tail);
  }
  int top = by + cat.sideN;
  auto lg = [&](int i, uint16_t col, uint16_t paw) {   // legs 0 near back, 1 far back, 2 near front, 3 far front
    int ph = (f + (i == 0 || i == 3 ? 0 : 2)) % 4, dx = moving ? STEP_S[ph] : 0, len = ground - top - (moving && ph == 3 ? 1 : 0);
    for (int j = 0; j < len; j++) put(bx + cat.legs[i] + rnd((float)dx * j / (len - 1 > 1 ? len - 1 : 1)), top + j, 1, 1, j == len - 1 ? paw : col);
  };
  lg(1, cat.fr, cat.fr); lg(3, cat.fr, cat.fr);
  spr(cat.side, cat.sideN, bx, by, cat.pal);
  lg(0, cat.nr, cat.paw); lg(2, cat.nr, cat.paw);
  int hx = bx + cat.hx, hy = by + cat.hy;
  Pal p = cat.pal;
  if (cat.bob) { if (mood == OPEN) p.s('x', DARK_EYE).s('a', DARK_EYE).s('b', DARK_EYE); else p.s('x', p['w']).s('a', p['w']).s('b', DARK_EYE); }
  else if (mood == OPEN) p.s('x', look > 0 ? IRIS : DARK_EYE).s('y', look > 0 ? DARK_EYE : IRIS);
  else p.s('x', p['d']).s('y', p['d']);
  spr(cat.head, cat.headN, hx, hy, p);
  if (!cat.bob) SPR(BOW_S, hx + 6, hy, cat.pal);
}

const float CITY_T = 16, WALK_V = 11, WALK_END = 8.4f, BRAKE = 0.7f, SIT_AT = 9.8f;
const int G = 66, MX = 40, MY = 21, MR = 10;
const uint32_t CSKY[10] = {0x0b0f2a, 0x0e1332, 0x11173b, 0x151b45, 0x1a1f4f, 0x20245a, 0x272a64, 0x302f6d, 0x3a3474, 0x453a7a};
const char *const TANK[] = {"..aaa..", ".aaaaa.", "abbbbba", "aaaaaaa", "abbbbba", "aaaaaaa", ".a...a.", ".a...a."};
// their tails meet between them and curl up into a heart: Bob's grey makes one side, hers the other
const int TAIL_B[12][2] = {{36, -2}, {37, -1}, {38, -1}, {39, -2}, {40, -3}, {41, -4}, {42, -5}, {43, -6}, {43, -7}, {42, -8}, {41, -8}, {40, -7}};

static float scrollAt(float T) {
  if (T < WALK_END) return WALK_V * T;
  float u = clamp01((T - WALK_END) / BRAKE);
  return WALK_V * (WALK_END + BRAKE * (u - u * u / 2));
}
static int fdiv(float a, int b) { return (int)floorf(a / b); }

static void city(float t) {
  float T = fmodf(t, CITY_T), S = scrollAt(T);
  for (int i = 0; i < 10; i++) put(0, i * 7, N, 7, C(CSKY[i]));
  for (int i = 0; i < 70; i++) {                                                         // stars, none in front of the moon
    int x = (int)(hsh(i, 1) * N), y = (int)(hsh(i, 2) * 46); float tw = sinf(t * 2.1f + i * 1.7f);
    if (hyp(x - MX, y - MY) < 16 || tw < -0.5f) continue;
    if (i % 9 == 0 && tw > 0.6f) sparkle(x, y, 1, C(0xc9ceff));
    put(x, y, 1, 1, tw > 0.8f ? WHITE : i % 3 ? C(0x8a90c8) : C(0xc9ceff));
  }
  if (T > 12.6f && T < 13.1f) {                                                          // one shooting star while they sit
    float u = (T - 12.6f) / 0.5f;
    for (int k = 0; k < 6; k++) { float v = u - k * 0.04f; if (v > 0) put(70 - v * 18, 5 + v * 9, 1, 1, k ? C(0x8a90c8) : WHITE); }
  }
  for (int y = -MR - 5; y <= MR + 5; y++) for (int x = -MR - 5; x <= MR + 5; x++) {      // big full moon, soft glow
    float d = hyp(x, y);
    if (d < MR + 2.5f || (d < MR + 5 && (x + y) % 2 == 0)) put(MX + x, MY + y, 1, 1, d < MR + 2.5f ? C(0x3a3f86) : C(0x2a2f6e));
  }
  disc(MX, MY, MR, C(0xfff1c4));
  for (int y = -MR; y <= MR; y++) for (int x = -MR; x <= MR; x++)                        // shaded right limb
    if (x * x + y * y <= MR * MR + MR && hyp(x - 3, y + 2) > MR - 0.5f) put(MX + x, MY + y, 1, 1, C(0xecdca4));
  static const int CRATER[5][4] = {{-4, -3, 3, 2}, {2, 3, 3, 2}, {-2, 4, 2, 1}, {4, -4, 2, 1}, {-6, 1, 1, 2}};
  for (auto &c : CRATER) put(MX + c[0], MY + c[1], c[2], c[3], C(0xe2d096));
  put(MX - 5, MY - 6, 2, 1, C(0xfffbe8)); put(MX - 6, MY - 5, 1, 2, C(0xfffbe8));

  float far = S * 0.1f;                                                                  // far skyline, hazy
  for (int c = fdiv(far, 6) - 1; c <= fdiv(far + N, 6) + 1; c++) {
    float x = c * 6 - far; int w = 5 + (int)(hsh(c, 3) * 3);
    bool tall = hsh(c, 13) > 0.7 && (c * 6 < 18 || c * 6 > 64); int top = (tall ? 27 : 36) + (int)(hsh(c, 4) * 11);
    const uint16_t FARC = C(0x1f2656);
    put(x, top, w, G - top, FARC);
    if (tall) { put(x + 1, top - 2, w - 2, 2, FARC); put(x + (w >> 1), top - 7, 1, 5, FARC); if (sinf(t * 3 + c) > 0.2f) put(x + (w >> 1), top - 8, 1, 1, C(0xff5a5a)); }
    else if (hsh(c, 5) > 0.72) put(x + 2, top - 3, 1, 3, FARC);
    for (int wy = top + 2; wy < G; wy += 3) for (int wx = 1; wx < w - 1; wx += 2) if (hsh(c * 13 + wx, wy) > 0.84) put(x + wx, wy, 1, 1, C(0x8c7f6a));
  }
  float mid = S * 0.3f;                                                                  // middle blocks: water tanks, small windows, neon
  for (int c = fdiv(mid, 13) - 1; c <= fdiv(mid + N, 13) + 1; c++) {
    float x = c * 13 - mid; int w = 9 + (int)(hsh(c, 6) * 4), top = 39 + (int)(hsh(c, 7) * 14);
    put(x, top, w, G - top, C(0x171c46)); put(x, top - 1, w, 1, C(0x2b3170)); put(x, top, 1, G - top, C(0x232a60));
    for (int wy = top + 2; wy < G; wy += 2) for (int wx = 2; wx < w - 1; wx += 2) {
      double h = hsh(c * 17 + wx, wy);
      if (h > 0.7) put(x + wx, wy, 1, 1, h > 0.96 ? C(0x9fd8ff) : h > 0.85 ? C(0xffdf8a) : C(0xf2b24a));
    }
    double roof = hsh(c, 8);
    if (roof > 0.55) SPR(TANK, x + ((w - 7) >> 1), top - 9, Pal("ab", {0x3d4488, 0x272d66}));
    else if (roof > 0.3) { put(x + w - 3, top - 5, 1, 5, C(0x2b3170)); put(x + w - 5, top - 4, 5, 1, C(0x2b3170)); }
    if (hsh(c, 9) > 0.62) {                                                              // vertical neon blade sign, flickers
      bool on = sinf(t * 6 + c * 2) > -0.8f || sinf(t * 1.1f + c) > 0.6f; uint16_t col = hsh(c, 10) > 0.5 ? C(0xff6fae) : C(0x4fe3d0);
      put(x - 1, top + 3, 3, 9, C(0x2a1430));
      for (int k = 0; k < 4; k++) put(x, top + 4 + k * 2, 1, 1, on ? col : C(0x4a2a4a));
    }
  }
  float nearS = S * 0.55f;                                                               // near rooftops, a fish billboard
  for (int c = fdiv(nearS, 22) - 1; c <= fdiv(nearS + N, 22) + 1; c++) {
    float x = c * 22 - nearS; int w = 15 + (int)(hsh(c, 11) * 5), top = 54 + (int)(hsh(c, 12) * 5);
    put(x, top, w, G - top, C(0x100d28)); put(x, top - 1, w, 1, C(0x221d48));
    for (int wy = top + 3; wy < G - 1; wy += 4) for (int wx = 2; wx < w - 2; wx += 4) if (hsh(c * 7 + wx, wy) > 0.6) put(x + wx, wy, 2, 2, C(0xe8a640));
    if (((c % 3) + 3) % 3 == 1) {
      bool on = sinf(t * 5 + c) > -0.75f;
      put(x + 3, top - 9, 1, 8, C(0x221d48)); put(x + 13, top - 9, 1, 8, C(0x221d48));
      put(x + 2, top - 13, 13, 6, C(0x2a1430)); put(x + 2, top - 13, 13, 1, C(0x4a2450));
      SPR(FISH, x + 5, top - 11, Pal("xe", {on ? 0xff6faeu : 0x6a3456u, 0x2a1430}));
    }
  }
  put(0, G, N, 1, C(0x8b7fae)); put(0, G + 1, N, 1, C(0x5a4c7c)); put(0, G + 2, N, N - G - 2, C(0x2b2244));   // our rooftop ledge
  for (int y = G + 4; y < N; y += 3) {
    put(0, y, N, 1, C(0x221a38));
    for (float x = -fmodf(S + (y % 2) * 3, 6); x < N; x += 6) put(x, y + 1, 1, 2, C(0x221a38));
  }
  for (int c = fdiv(S, 19) - 1; c <= fdiv(S + N, 19) + 1; c++) {                         // things on our roof, behind the cats
    float x = c * 19 - S + 6; double k = hsh(c, 30);
    if (k < 0.3) { put(x, G - 5, 2, 5, C(0x5a5080)); put(x - 1, G - 6, 4, 1, C(0x7a6ea4)); }
    else if (k < 0.5) { put(x, G - 7, 4, 7, C(0x7a3e34)); put(x - 1, G - 8, 6, 1, C(0xa89a8a)); put(x, G - 4, 4, 1, C(0x5a2c24)); }
    else if (k < 0.65) { put(x, G - 4, 7, 4, C(0x4c4468)); put(x, G - 4, 7, 1, C(0x6c6490)); put(x + 1, G - 3, 2, 2, C(0x2e2844)); }
  }

  int f = (int)floorf(S / 2.4f) % 4; bool moving = T < WALK_END + BRAKE;
  if (T < SIT_AT) {
    bool blinkB = fmodf(T, 3.3f) < 0.12f, blinkG = fmodf(T + 1.4f, 2.9f) < 0.12f;
    smallWalker(BS, 22, G, f, moving, 1, blinkB ? SHUT : OPEN, t);
    smallWalker(GS, 41, G, (f + 1) % 4, moving, moving ? 1 : -1, blinkG ? SHUT : OPEN, t);   // stopped: a look at each other
  } else {
    int dy = T < SIT_AT + 0.1f ? -2 : T < SIT_AT + 0.2f ? -1 : 0;                         // settle down onto the ledge
    spr(BS.back, BS.backN, 24, G - BS.backN + dy, BS.pal);
    spr(GS.back, GS.backN, 45, G - GS.backN + dy, GS.pal);
    SPR(BOW_S, 53, G - GS.backN + dy + 2, GS.pal);                                       // on her right ear
    float k = ease(clamp01((T - SIT_AT - 0.6f) / 1.8f)), wob = sinf(t * 2.2f);
    for (int side = 0; side < 2; side++) {                                               // her tail, then his
      int dir = side ? 1 : -1; uint16_t col = side ? BS.pal['l'] : GS.tail;
      float fx0 = side ? TAIL_B[0][0] : 80 - TAIL_B[0][0];
      for (int i = 0; i < 12; i++) {
        float tx = side ? TAIL_B[i][0] : 80 - TAIL_B[i][0], ty = TAIL_B[i][1];
        float frx = fx0 + dir * i * 0.45f, fry = -1 - i * 0.45f, u = clamp01(k * 1.6f - (i / 12.0f) * 0.6f);
        put(rnd(frx + (tx - frx) * u + (i > 6 ? dir * wob * (1 - k) : 0)), rnd(G + fry + (ty - fry) * u), 1, 1, col);
      }
    }
  }
  float fade = T / 0.35f; if (fade > 1) fade = 1; if ((CITY_T - T) / 0.6f < fade) fade = (CITY_T - T) / 0.6f;   // soft loop: dark in, dark out
  if (fade < 1) for (auto &p : buf) {
    int r = (p >> 8) & 0xF8, g = (p >> 3) & 0xFC, b = (p << 3) & 0xF8;
    r = 8 + (r - 8) * fade; g = 10 + (g - 10) * fade; b = 30 + (b - 30) * fade;
    p = C((r << 16) | (g << 8) | b);
  }
}

// ================= 2. Home: Bob eats from his bowl in a warm room, it magically refills =================
const float HOME_T = 6.6f;
const char *const BOWL[] = {"kRiiiiiiiiiiiRk", "kBBBBBBBBBBBBBk", ".kBBWBBBBBWBBk.", ".kBBBBBBBBBBBk.", "..kkkkkkkkkkk.."};
const char *const QMARK[] = {".ww.", "w..w", "..w.", ".w..", "....", ".w.."};
const char *const LEAF[] = {".gg", "ggG", "gG."};

static void home(float t) {
  float T = fmodf(t, HOME_T);
  put(0, 0, N, 56, C(0xf2d3a8));                                                          // wall + lamp glow
  for (int x = 2; x < N; x += 8) put(x, 0, 2, 56, C(0xebc795));
  float fl = sinf(t * 5) * 0.4f;
  for (int y = 0; y < 56; y++) for (int x = 44; x < N; x++) {
    float d = hyp(x - 67, y - 22);
    if (d < 11 + fl || (d < 17 + fl && (x + y) % 2 == 0)) put(x, y, 1, 1, (x - 2) % 8 < 2 ? C(0xf7dcae) : C(0xfbe7c4));
  }
  put(0, 54, N, 2, C(0xe3b67e)); put(0, 56, N, 1, C(0xc99a66));                           // skirting
  put(0, 57, N, 23, C(0xb0723f));                                                         // floorboards
  for (int y = 60; y < N; y += 4) { put(0, y, N, 1, C(0x93592e)); for (int x = (y * 7) % 13; x < N; x += 13) put(x, y + 1, 1, 3, C(0x93592e)); }
  for (int y = -6; y <= 6; y++) for (int x = -29; x <= 29; x++) {                         // rug
    float e = (x * x) / 841.0f + (y * y) / 36.0f;
    if (e <= 1) put(40 + x, 71 + y, 1, 1, e > 0.8f ? C(0x8f2f45) : e > 0.6f ? C(0xf0b44c) : (x + y) % 4 == 0 ? C(0xc85068) : C(0xb8425a));
  }
  put(13, 13, 20, 22, C(0x7a4a2c)); put(14, 14, 18, 20, C(0x26325e));                     // window, rainy night
  put(14, 14, 18, 3, C(0x1e2850));
  for (int i = 0; i < 16; i++) put(14 + fmodf(hsh(i, 7) * 18 + T * 3, 18), 14 + fmodf(hsh(i, 8) * 20 + T * 26, 20), 1, 2, C(0x8fa8dc));
  put(22, 14, 2, 20, C(0x7a4a2c)); put(14, 23, 18, 2, C(0x7a4a2c));
  put(11, 34, 24, 2, C(0x9a6a44));                                                        // sill
  for (int cx : {10, 33}) { put(cx, 11, 3, 25, C(0xc95a5a)); put(cx + 1, 11, 1, 25, C(0xa84646)); }
  put(10, 10, 26, 1, C(0x6a3e24));
  put(67, 25, 1, 31, C(0x4a3426)); put(64, 55, 7, 2, C(0x4a3426));                        // floor lamp
  static const int SHADE[6][3] = {{66, 15, 3}, {65, 16, 5}, {64, 17, 7}, {63, 18, 9}, {62, 19, 11}, {62, 20, 11}};
  for (auto &s : SHADE) put(s[0], s[1], s[2], 1, C(0xffcf73));
  put(62, 21, 11, 1, C(0xe8a94a)); put(65, 22, 5, 1, C(0xfff3c8));
  put(13, 50, 8, 7, C(0xc9623a)); put(12, 49, 10, 2, C(0xe07a4a)); put(14, 56, 6, 1, C(0xa24a2a));   // plant
  const Pal LEAF_PAL("gG", {0x4e9a4a, 0x7cc46a});
  for (int i = 0; i < 5; i++) {
    float a = -1.2f + i * 0.6f, sw = sinf(t * 1.5f + i) * 0.6f;
    SPR(LEAF, 15 + sinf(a) * 5 + sw, 44 - cosf(a) * 4 - (i % 2) * 2, LEAF_PAL);
  }
  disc(63, 66, 3, C(0x6f8fe0)); put(61, 65, 4, 1, C(0x4a68b8)); put(62, 67, 3, 1, C(0x4a68b8));   // yarn ball + loose thread
  put(66, 68, 4, 1, C(0x6f8fe0)); put(70, 69, 3, 1, C(0x6f8fe0));

  // the story: six bites empty the bowl, he looks up (?), it sparkles full again, a big happy heart
  int dip = 0, mood = OPEN, look = 1, food = 3, bite = 0; bool blush = false; float swish = 1, b = 0;
  if (T < 3.6f) {
    bite = (int)floorf(T / 0.6f); b = fmodf(T, 0.6f) / 0.6f;
    dip = rnd(7 * sinf(3.14159265f * (b / 0.8f < 1 ? b / 0.8f : 1)));
    if (b > 0.45f && b < 0.8f) dip -= (int)floorf(b * 20) % 2;                              // chewing
    mood = HAPPY;
    food = 3 - (bite + (b > 0.5f ? 1 : 0)) / 2;
  } else if (T < 4.6f) { food = 0; look = T < 4.0f || T > 4.3f ? 1 : -1; }
  else if (T < 5.6f) { food = (int)floorf((T - 4.6f) * 4); if (food > 3) food = 3; }
  else { mood = HAPPY; blush = true; swish = 2.5f; }
  const int bx = 32, by = 59;
  float pts[10][2];                                                                         // fluffy tail curls up his right side
  for (int i = 1; i <= 10; i++) { pts[i - 1][0] = bx + 14 + i * 0.75f - (i > 6 ? (i - 6) * 1.1f : 0) + sinf(t * 2 * swish - i * 0.5f) * i * 0.14f; pts[i - 1][1] = by + 9 - i * 1.05f; }
  tail(pts, 10, 2, B_GREY);
  SPR(BOB_SIT, bx, by, BOB_PAL);
  SPR(BOB_HEAD, bx + 1, by - 19 + dip, eyesFor(look, mood, blush || dip > 4));
  SPR(BOWL, 33, 65, Pal("kRiBW", {0x1f2a4a, 0x9fc0ff, food > 0 ? 0x9a5a28u : 0x2a3f7au, 0x4f7fd8, 0xffffff}));
  static const int KIB[3][2] = {{35, 11}, {37, 7}, {39, 3}};
  for (int i = 0; i < 3; i++) if (food > i) for (int k = 0; k < KIB[i][1]; k++) put(KIB[i][0] + k, 64 - i, 1, 1, hsh(k, i) > 0.5 ? C(0x9a5a28) : C(0xc98a4a));
  if (T < 3.6f && b > 0.45f) for (int k = 0; k < 2; k++) {                                  // crumbs fly out on each bite
    float u = (b - 0.45f) / 0.55f, sp = 4 + hsh(bite, k) * 5; int side = k ? 1 : -1;
    put(40 + side * (3 + u * sp), 63 - 8 * u + 10 * u * u, 1, 1, C(0xc98a4a));
  }
  if (T >= 3.8f && T < 4.6f) SPR(QMARK, 50, 34, Pal("w", {0x2a2622}));
  if (T >= 4.6f && T < 5.8f) for (int k = 0; k < 4; k++) {
    float ph = fmodf(T * 3 + k * 0.37f, 1);
    sparkle(34 + hsh(k, 11) * 13, 58 + hsh(k, 12) * 6 - ph * 4, ph < 0.5f ? 1 : 0, ph < 0.5f ? C(0xfff6a8) : WHITE);
  }
  if (T >= 5.6f) SPR(HEART_BIG, 49, 36 - (T - 5.6f) * 8, HEART_PAL);
}

// ================= 3. Sky: Bob paddles through the stars with the fish =================
const float SKY_T = 6.4f;
const uint32_t SSKY[10] = {0x1b1440, 0x221852, 0x2c1d63, 0x3a2373, 0x4c2a82, 0x62338c, 0x7a3d91, 0x8a4596, 0x9a4f98, 0xa85a96};
struct Fish { uint32_t col; float y0, sp, ph; };
const Fish FISHES[4] = {{0xffb020, 22, 8, 0}, {0xff7aa2, 46, 5, 0.33f}, {0x7fd1f7, 30, 11, 0.66f}, {0xffe066, 58, 7, 0.15f}};

static void sky(float t) {
  float T = fmodf(t, SKY_T);
  for (int i = 0; i < 10; i++) put(0, i * 8, N, 8, C(SSKY[i]));
  for (int i = 0; i < 50; i++) {
    float x = fmodf(hsh(i, 1) * N + t * 2, N), tw = sinf(t * 2.2f + i * 1.3f); int y = (int)(hsh(i, 2) * 70);
    if (tw > -0.3f) put(x, y, 1, 1, tw > 0.8f ? WHITE : C(0xc9c2ff));
  }
  disc(22, 18, 7, C(0xfff3c4)); disc(25, 16, 6, C(SSKY[2]));                                // crescent moon
  static const float CLOUD[3][3] = {{24, 4, 14}, {58, 7, 18}, {12, 2.5f, 10}};               // clouds drift past
  for (auto &c : CLOUD) {
    int y = c[0], w = c[2]; float x = N - fmodf(t * c[1] + y * 3, N + w + 10);
    put(x, y, w, 3, C(0x8c7fd1)); put(x + 3, y - 2, w - 7, 2, C(0x8c7fd1)); put(x + 1, y + 3, w - 2, 1, C(0x6f63b4));
  }
  for (auto &fi : FISHES) {                                                                   // fish swim the other way
    float x = N + 6 - fmodf(t * fi.sp + fi.ph * (N + 14), N + 14), y = fi.y0 + sinf(t * 2 + fi.ph * 9) * 2;
    uint16_t col = C(fi.col);
    SPR(FISH, x, y, Pal("xe", {fi.col, 0x1b1440}));
    if (sinf(t * 9 + fi.ph * 7) > 0) put(x + 7, y + 1, 1, 1, col); else { put(x + 7, y, 1, 1, col); put(x + 7, y + 2, 1, 1, col); }
  }
  int f = (int)floorf(t * 6) % 4, bob = rnd(sinf(t * 1.6f) * 3);
  bool happy = T > 3.6f && T < 5.2f;
  int hx, hy;
  walker(24, 58 + bob, f, 1, happy ? HAPPY : OPEN, happy, t, hx, hy);                         // paddling in the air
  if (happy) { float k = (T - 3.6f) / 1.6f; if (k < 0.85f || (int)floorf(T * 12) % 2) SPR(HEART, hx + 9, hy - 2 - k * 7, HEART_PAL); }
  for (int i = 0; i < 3; i++) {                                                               // stardust trail behind him
    float ph = fmodf(t * 1.5f + i / 3.0f, 1);
    put(22 - ph * 12, 50 + bob + i * 2 + ph * 3, 1, 1, ph < 0.5f ? C(0xfff6a8) : C(0xc9c2ff));
  }
}

void frame(int scene, float t) { if (scene == 0) city(t); else if (scene == 1) home(t); else sky(t); }

}  // namespace dream
