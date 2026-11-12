// Bob, the desk cat: first firmware (untested until the board arrives)
// Face = Gokul's own Bob drawings (face/art), turned into screen images by face/make_faces_h.py
//
// Board: "ESP32S3 Dev Module", USB CDC On Boot = Enabled, PSRAM = OPI PSRAM, Flash = 8MB
// Libraries: Arduino_GFX (moononournation), ESP32Servo
//
// What it does:
//   - shows Bob's face (from the drawing) and blinks every few seconds
//   - pat his head -> he rubs into your hand like a real cat: eyes half-shut,
//     face leans side to side, ears tilt with the rub, tail sways, purr
//   - loud clap -> he looks up and flicks his tail
//   - nobody around for a while -> he falls asleep

#include <Arduino_GFX_Library.h>
#include <ESP32Servo.h>
#include "bob_faces.h"   // face_idle, face_blink, face_half, face_talk, face_lick (240x240)

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
const int TAIL_SWAY = 30;         // how far the tail sways while purring
const int TAIL_FLICK = 40;        // how far the tail flicks on a clap
const int RUB_SHIFT = 8;          // how many pixels his face leans left/right during the rub
const int RUB_STEPS = 6;          // how many rubs per pat
const int RUB_STEP_MS = 280;      // speed of each rub (bigger = slower, lazier cat)
const int PURR_LOW = 85, PURR_HIGH = 100;   // purr sound (Hz)
const unsigned long SLEEP_AFTER_MS = 60000; // fall asleep after 60 s alone
const bool CUTE_SPARKLES = true;  // little shine in his eyes
// sparkle spots (x, y, radius) on the 240x240 face, nudge if they miss the pupils
const int SPARK[4][3] = { {77, 84, 4}, {70, 97, 2}, {157, 84, 4}, {150, 97, 2} };

// ---------- tune these on the real board ----------
int TOUCH_THRESHOLD = 0;      // set in setup() from a no-touch reading
const int CLAP_LEVEL = 1200;  // mic jump that counts as a clap

Arduino_DataBus *bus = new Arduino_ESP32SPI(PIN_DC, PIN_CS, PIN_SCK, PIN_MOSI, GFX_NOT_DEFINED);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, PIN_RST, 0, true);

Servo earL, earR, tail;
unsigned long lastActivity = 0, nextBlink = 0;
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
  open();
}

void flickTail() {
  tail.write(TAIL_REST - TAIL_FLICK); delay(180);
  tail.write(TAIL_REST + TAIL_FLICK); delay(180);
  tail.write(TAIL_REST);
}

void wake() { if (asleep) { asleep = false; showFace(face_half); delay(300); open(); } lastActivity = millis(); }

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
  tone_ms(880, 80); tone_ms(1320, 120);     // hello chirp
  lastActivity = millis(); nextBlink = millis() + 3000;
}

void loop() {
  unsigned long now = millis();

  if (touchRead(PIN_TOUCH) > TOUCH_THRESHOLD) { wake(); rubIntoHand(); }   // pat on the head

  int a = analogRead(PIN_MIC), b = analogRead(PIN_MIC);    // crude clap check: big jump
  if (abs(a - b) > CLAP_LEVEL || a > 3900) { wake(); flickTail(); }

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
