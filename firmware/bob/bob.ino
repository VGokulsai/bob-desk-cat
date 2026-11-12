// Bob, the desk cat: first firmware (untested until the board arrives)
// AI-assisted starter, reviewed and owned by Gokul. Disclosed in the journal.
//
// Board: "ESP32S3 Dev Module", USB CDC On Boot = Enabled, PSRAM = OPI PSRAM, Flash = 8MB
// Libraries: Arduino_GFX (moononournation), ESP32Servo
//
// What it does:
//   - draws Bob's face on the round screen and blinks every few seconds
//   - pat his head (touch pad) -> happy eyes, ears wiggle, purr sound
//   - loud clap (mic) -> he looks up and flicks his tail
//   - nobody around for a while -> he falls asleep

#include <Arduino_GFX_Library.h>
#include <ESP32Servo.h>

// ---------- pins (from the schematic) ----------
const int PIN_SCK = 12, PIN_MOSI = 11, PIN_CS = 10, PIN_DC = 13, PIN_RST = 14;
const int PIN_MIC = 4;        // analog, through the MCP6001 preamp
const int PIN_SPEAKER = 5;    // PWM into the PAM8302 amp
const int PIN_EAR_L = 15, PIN_EAR_R = 16, PIN_TAIL = 17;
const int PIN_TOUCH = 1;      // touch pad on the head

// ---------- tune these on the real board ----------
int TOUCH_THRESHOLD = 0;      // set in setup() from a no-touch reading
const int CLAP_LEVEL = 1200;  // mic jump that counts as a clap
const unsigned long SLEEP_AFTER_MS = 60000;

Arduino_DataBus *bus = new Arduino_ESP32SPI(PIN_DC, PIN_CS, PIN_SCK, PIN_MOSI, GFX_NOT_DEFINED);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, PIN_RST, 0, true);

Servo earL, earR, tail;
unsigned long lastActivity = 0, nextBlink = 0;
bool asleep = false;

const uint16_t FUR = 0x2945, EYE = 0xFFFF, PUPIL = 0x0000, NOSE = 0xFB2C;

void drawFace(const char *mood) {
  gfx->fillScreen(FUR);
  if (!strcmp(mood, "open")) {
    gfx->fillCircle(80, 105, 26, EYE);  gfx->fillCircle(160, 105, 26, EYE);
    gfx->fillCircle(80, 108, 12, PUPIL); gfx->fillCircle(160, 108, 12, PUPIL);
  } else if (!strcmp(mood, "happy")) {   // ^ ^ eyes
    gfx->fillArc(80, 115, 24, 20, 200, 340, EYE);
    gfx->fillArc(160, 115, 24, 20, 200, 340, EYE);
  } else {                               // closed / asleep
    gfx->fillRect(56, 104, 48, 5, EYE);  gfx->fillRect(136, 104, 48, 5, EYE);
  }
  gfx->fillTriangle(110, 150, 130, 150, 120, 162, NOSE);
  if (asleep) { gfx->setTextColor(EYE); gfx->setTextSize(3); gfx->setCursor(170, 40); gfx->print("z"); }
}

void tone_ms(int freq, int ms) {
  ledcWriteTone(PIN_SPEAKER, freq); delay(ms); ledcWriteTone(PIN_SPEAKER, 0);
}

void purr() {                       // a low rumbling purr
  for (int i = 0; i < 12; i++) { tone_ms(90 + (i % 2) * 15, 60); delay(20); }
}

void wiggleEars() {
  for (int i = 0; i < 3; i++) {
    earL.write(60); earR.write(120); delay(150);
    earL.write(90); earR.write(90);  delay(150);
  }
}

void flickTail() { tail.write(50); delay(200); tail.write(130); delay(200); tail.write(90); }

void wake() { if (asleep) { asleep = false; drawFace("open"); } lastActivity = millis(); }

void setup() {
  Serial.begin(115200);
  gfx->begin();
  ledcAttach(PIN_SPEAKER, 2000, 8);
  earL.attach(PIN_EAR_L); earR.attach(PIN_EAR_R); tail.attach(PIN_TAIL);
  earL.write(90); earR.write(90); tail.write(90);

  int base = touchRead(PIN_TOUCH);          // reading with no finger
  TOUCH_THRESHOLD = base + base / 5;        // ESP32-S3 value rises when touched; tune if needed
  Serial.printf("touch base %d, threshold %d\n", base, TOUCH_THRESHOLD);

  drawFace("open");
  tone_ms(880, 80); tone_ms(1320, 120);     // hello chirp
  lastActivity = millis(); nextBlink = millis() + 3000;
}

void loop() {
  unsigned long now = millis();

  if (touchRead(PIN_TOUCH) > TOUCH_THRESHOLD) {           // pat on the head
    wake(); drawFace("happy"); wiggleEars(); purr(); drawFace("open");
  }

  int a = analogRead(PIN_MIC), b = analogRead(PIN_MIC);    // crude clap check: big jump
  if (abs(a - b) > CLAP_LEVEL || a > 3900) { wake(); flickTail(); }

  if (!asleep && now > nextBlink) {                        // blink
    drawFace("closed"); delay(120); drawFace("open");
    nextBlink = now + random(2500, 6000);
  }

  if (!asleep && now - lastActivity > SLEEP_AFTER_MS) {    // nap time
    asleep = true; drawFace("closed");
  }
  delay(20);
}
