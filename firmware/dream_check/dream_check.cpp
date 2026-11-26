// Builds the firmware's dream drawing (bob/bob_dream.h) on a PC and writes frames as raw RGB565 to stdout.
// compare.js runs the same times through sim/dream.js and fails if the two disagree. Run by CI.
//   g++ -O2 -o dream_check dream_check.cpp && ./dream_check > fw.bin && node compare.js fw.bin
#include <stdio.h>
#include "../bob/bob_dream.h"
#include "times.h"

int main() {
  for (auto &f : FRAMES) { dream::frame(f.scene, f.t); fwrite(dream::buf, 2, dream::N * dream::N, stdout); }
  return 0;
}
