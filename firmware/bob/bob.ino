// Bob, the desk cat: first firmware (untested until the board arrives)
// Face = Gokul's own Bob drawings (face/art), turned into screen images by face/make_faces_h.py
//
// Board: "ESP32S3 Dev Module", USB CDC On Boot = Enabled, PSRAM = OPI PSRAM, Flash = 8MB
// Libraries: Arduino_GFX (moononournation). Servos run on the ESP32's own PWM, no servo library.
// Known-good versions (compiled in CI): ESP32 core "esp32 by Espressif" 3.3.0 + "GFX Library for Arduino" 1.6.0.
//
// What it does:
//   - shows Bob's face (from the drawing) and blinks every few seconds
//   - pat his head -> he rubs into your hand like a real cat: eyes half-shut,
//     face leans side to side, ears tilt with the rub, tail sways, purr
//   - after the pat he licks his paw (lick face) like a cat grooming
//   - pat him 3 times in 10 s -> the 3rd pat annoys him: irritated face, ears flat,
//     tail lashes, then he calms down and the next pat is happy again
//   - loud clap -> he looks up, flicks his tail, and sometimes meows
//   - clap while he's asleep -> he wakes up irritated (no meow)
//   - he meows hello on power-up, and now and then on his own (talk face while he meows)
//   - nobody around for a while -> he falls asleep

#include <Arduino_GFX_Library.h>
#include "bob_faces.h"   // face_idle, face_blink, face_half, face_talk, face_lick, face_irritated (240x240)
#include "bob_meows.h"   // MEOWS[3], MEOW_LEN[3], MEOW_RATE: made by face/make_meows_h.py

// ---------- pins (from the schematic) ----------
const int PIN_SCK = 12, PIN_MOSI = 11, PIN_CS = 10, PIN_DC = 13, PIN_RST = 14;
const int PIN_MIC = 4;        // analog, through the MCP6001 preamp
const int PIN_SPEAKER = 5;    // PWM into the PAM8302 amp
const int PIN_EAR_L = 15, PIN_EAR_R = 16, PIN_TAIL = 17;
const int PIN_TOUCH = 1;      // touch pad on the head

// ---------- CHANGE THESE: how Bob moves ----------
const int EAR_REST = 90;          // ears straight up
const int EAR_TILT = 25;          // how far an ear leans during the rub (degrees)
const int TAIL_REST = 90;
const int TAIL_SWAY = 45;         // how far the tail sways while purring
const int TAIL_FLICK = 40;        // how far the tail flicks on a clap
const int RUB_SHIFT = 8;          // how many pixels his face leans left/right during the rub
const int RUB_STEPS = 6;          // how many rubs per pat
const int RUB_STEP_MS = 280;      // speed of each rub (bigger = slower, lazier cat)
const int PURR_LOW = 85, PURR_HIGH = 100;   // purr sound (Hz)
const unsigned long SLEEP_AFTER_MS = 120000; // fall asleep after 2 min alone
const bool CUTE_SPARKLES = true;  // little shine in his eyes
const int LICK_MS = 700;          // how long he licks his paw after a pat
const int CLAP_MEOW_CHANCE = 3;   // 1 in 3 claps get a meow back
const bool CHATTY = true;         // meows on his own now and then while awake
const unsigned long CHAT_MIN_MS = 45000, CHAT_MAX_MS = 120000;  // gap between his own meows
const int IRRITATE_PATS = 3;      // this many pats...
const unsigned long IRRITATE_WINDOW_MS = 10000;  // ...inside this time and the last one annoys him
const int EAR_FLAT = 60;          // ears go flat to the side when he's irritated (degrees)
const int TAIL_LASH = 35;         // how far the tail lashes when he's irritated
const int LASH_MS = 120;          // speed of each lash (one side to the other)
const int IRRITATED_MS = 1500;    // how long he stays irritated
// sparkle spots (x, y, radius) on the 240x240 face, nudge if they miss the pupils
const int SPARK[4][3] = { {77, 84, 4}, {70, 97, 2}, {157, 84, 4}, {150, 97, 2} };

// ---------- tune these on the real board ----------
int TOUCH_THRESHOLD = 0;      // set in setup() from a no-touch reading
const int CLAP_LEVEL = 1200;  // mic jump that counts as a clap

Arduino_DataBus *bus = new Arduino_ESP32SPI(PIN_DC, PIN_CS, PIN_SCK, PIN_MOSI, GFX_NOT_DEFINED);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, PIN_RST, 0, true);

// SG90 servo on the ESP32's PWM: 50 Hz, pulse 0.5 ms (0 deg) to 2.5 ms (180 deg)
struct Servo {
  int pin = -1;
  void attach(int p) { pin = p; ledcAttach(pin, 50, 14); }   // 14-bit: 16383 = one 20 ms period
  void write(int deg) {
    deg = constrain(deg, 0, 180);
    uint32_t us = 500 + (uint32_t)deg * 2000 / 180;
    ledcWrite(pin, us * 16383 / 20000);
  }
};
Servo earL, earR, tail;
unsigned long lastActivity = 0, nextBlink = 0, nextChat = 0;
unsigned long micQuietUntil = 0;   // ignore the mic right after Bob makes a sound, or he hears himself as a clap
bool asleep = false;

// draw one face picture, shifted dx pixels left/right (for the rub)
void showFace(const uint16_t *img, int dx = 0, bool sparkle = false) {
  if (dx != 0) gfx->fillScreen(0xFFFF);                       // white behind, so no ghost edge
  gfx->draw16bitRGBBitmap(dx, 0, (uint16_t *)img, FACE_W, FACE_H);
  if (sparkle && CUTE_SPARKLES)
    for (auto &s : SPARK) gfx->fillCircle(s[0] + dx, s[1], s[2], 0xFFFF);
  if (asleep) { gfx->setTextColor(0x8410); gfx->setTextSize(3); gfx->setCursor(185, 30); gfx->print("z"); }
}

void open()  { showFace(face_idle, 0, true); }

void tone_ms(int freq, int ms) { ledcWriteTone(PIN_SPEAKER, freq); delay(ms); ledcWriteTone(PIN_SPEAKER, 0); }

// play one recorded meow: 8-bit samples as PWM duty on a fast carrier, with the talk face
void meow(int which) {
  which = constrain(which, 0, 2);
  showFace(face_talk);
  ledcChangeFrequency(PIN_SPEAKER, 40000, 8);              // 40 kHz carrier, 0-255 duty = the waveform
  const uint8_t *s = MEOWS[which];
  uint32_t period = 1000000UL / MEOW_RATE, t = micros();
  for (uint32_t i = 0; i < MEOW_LEN[which]; i++) {
    ledcWrite(PIN_SPEAKER, pgm_read_byte(s + i));
    t += period;
    while ((int32_t)(micros() - t) < 0) {}                  // wait for the next sample time
  }
  ledcWrite(PIN_SPEAKER, 0);
  micQuietUntil = millis() + 600;
  open();
}

// a real cat pat: he leans into your hand, side to side, purring
void rubIntoHand() {
  for (int i = 0; i < RUB_STEPS; i++) {
    int side = (i % 2 == 0) ? 1 : -1;
    showFace(face_half, side * RUB_SHIFT);                    // eyes half-shut, face leans
    earL.write(EAR_REST + side * EAR_TILT);                   // both ears lean the same way
    earR.write(EAR_REST + side * EAR_TILT);
    tail.write(TAIL_REST + side * TAIL_SWAY);
    ledcWriteTone(PIN_SPEAKER, (i % 2) ? PURR_HIGH : PURR_LOW);   // purr runs during the rub
    delay(RUB_STEP_MS);
  }
  ledcWriteTone(PIN_SPEAKER, 0);
  earL.write(EAR_REST); earR.write(EAR_REST); tail.write(TAIL_REST);
  showFace(face_lick); delay(LICK_MS);                      // happy cat: licks his paw after the pat
  micQuietUntil = millis() + 600;
  open();
}

void flickTail() {
  tail.write(TAIL_REST - TAIL_FLICK); delay(180);
  tail.write(TAIL_REST + TAIL_FLICK); delay(180);
  tail.write(TAIL_REST);
}

// too many pats: ears flat, tail lashes, grumpy face, then he calms down
void irritated() {
  showFace(face_irritated);
  earL.write(EAR_REST - EAR_FLAT); earR.write(EAR_REST - EAR_FLAT);
  for (int i = 0; i < 3; i++) {                            // three quick lashes
    tail.write(TAIL_REST - TAIL_LASH); delay(LASH_MS);
    tail.write(TAIL_REST + TAIL_LASH); delay(LASH_MS);
  }
  delay(IRRITATED_MS);
  earL.write(EAR_REST); earR.write(EAR_REST); tail.write(TAIL_REST);
  micQuietUntil = millis() + 600;
  open();
}

// remember this pat; true if it's the IRRITATE_PATS-th one inside IRRITATE_WINDOW_MS
unsigned long patTimes[IRRITATE_PATS];   // newest first
int patCount = 0;
bool tooManyPats() {
  for (int i = IRRITATE_PATS - 1; i > 0; i--) patTimes[i] = patTimes[i - 1];
  patTimes[0] = millis();
  if (patCount < IRRITATE_PATS) patCount++;
  if (patCount == IRRITATE_PATS && patTimes[0] - patTimes[IRRITATE_PATS - 1] <= IRRITATE_WINDOW_MS) {
    patCount = 0;                                           // start counting again, next pat is happy
    return true;
  }
  return false;
}

// face = what he shows while waking up (half-open for a pat, irritated for a clap)
void wake(const uint16_t *face = face_half, int ms = 300) {
  if (asleep) { asleep = false; showFace(face); delay(ms); open(); }
  lastActivity = millis();
}

void setup() {
  Serial.begin(115200);
  gfx->begin();
  ledcAttach(PIN_SPEAKER, 2000, 8);
  earL.attach(PIN_EAR_L); earR.attach(PIN_EAR_R); tail.attach(PIN_TAIL);
  earL.write(EAR_REST); earR.write(EAR_REST); tail.write(TAIL_REST);

  int base = touchRead(PIN_TOUCH);          // reading with no finger
  TOUCH_THRESHOLD = base + base / 5;        // ESP32-S3 value rises when touched; tune if needed
  Serial.printf("touch base %d, threshold %d\n", base, TOUCH_THRESHOLD);

  open();
  delay(400);
  meow(0);                                  // hello
  lastActivity = millis(); nextBlink = millis() + 3000;
  nextChat = millis() + random(CHAT_MIN_MS, CHAT_MAX_MS);
}

void loop() {
  unsigned long now = millis();

  if (touchRead(PIN_TOUCH) > TOUCH_THRESHOLD) {             // pat on the head
    wake();
    if (tooManyPats()) irritated(); else rubIntoHand();
  }

  int a = analogRead(PIN_MIC), b = analogRead(PIN_MIC);    // crude clap check: big jump
  if (millis() > micQuietUntil && (abs(a - b) > CLAP_LEVEL || a > 3900)) {
    bool wasAsleep = asleep;
    wake(face_irritated, IRRITATED_MS);                      // clapped awake: grumpy, no meow
    if (!wasAsleep) {
      flickTail();
      if (random(CLAP_MEOW_CHANCE) == 0) meow(random(3));
    }
    micQuietUntil = millis() + 400;
  }

  if (CHATTY && !asleep && millis() > nextChat) {           // a little meow on his own
    meow(random(3));
    nextChat = millis() + random(CHAT_MIN_MS, CHAT_MAX_MS);
  }

  if (!asleep && now > nextBlink) {                        // blink: half, shut, half, open
    showFace(face_half); delay(40); showFace(face_blink); delay(90);
    showFace(face_half); delay(40); open();
    nextBlink = now + random(2500, 6000);
  }

  if (!asleep && now - lastActivity > SLEEP_AFTER_MS) {    // nap time
    asleep = true; showFace(face_blink);
  }
  delay(20);
}
