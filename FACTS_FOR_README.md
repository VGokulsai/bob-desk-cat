# FACTS FOR GOKUL TO WRITE HIS OWN README FROM - NOT THE README

Raw facts only, pulled from the KiCad files and bom.csv on 8 Nov 2026. No prose on purpose:
Fallen requires the README and docs to be written by hand. Delete this file before submitting
if you don't want it in the repo.

## Board
- Size: 73.0 x 62.5 mm (Edge.Cuts rectangle, 149.5,46.5 to 222.5,109 mm)
- Layers: 2 copper (F.Cu, B.Cu), 1.6 mm thick
- Copper pour: 1 GND zone on B.Cu
- Footprints: 38
- Tracks: 263 segments (188 on F.Cu, 75 on B.Cu), widths 0.15 / 0.2 / 0.25 / 0.4 / 0.5 mm
- Vias: 79 (71 x 0.3 mm drill / 0.6 mm pad, 8 x 0.2 mm drill / 0.45 mm pad)
- Other plated holes: 12 x 0.2 mm (thermal vias inside the ESP32 module's GND pad footprint), 4 x 0.6, 21 x 1.0, 8 x 1.1 mm
- KiCad version: 10.0.6

## Checks (run 8 Nov 2026 with kicad-cli 10)
- ERC: 0 errors, 7 warnings (all "unconnected wire endpoint")
- DRC: 0 errors, 16 warnings (9 silk_over_copper, 7 silk_overlap), 0 unconnected items
- Schematic parity (PCB vs schematic): 0 issues
- Parity check proven live: the old PCB against the new schematic gave 13 parity issues, so 0 is a real 0

## MCU
- Espressif ESP32-S3-WROOM-1 module (U2); bom.csv buys the N8R8 version (8 MB flash, 8 MB PSRAM)
- IO35, IO36, IO37 left unconnected (schematic symbol marks them PSRAM)

## Pin map (from the netlist)
| Function | ESP32-S3 pin | Goes to |
|---|---|---|
| Screen SCL | IO12 (module pin 20) | J2 pin 3 |
| Screen SDA | IO11 (pin 19) | J2 pin 4 |
| Screen RES | IO14 (pin 22) | J2 pin 5 |
| Screen DC | IO13 (pin 21) | J2 pin 6 |
| Screen CS | IO10 (pin 18) | J2 pin 7 |
| Left ear servo signal | IO15 (pin 8) | J5 pin 3 |
| Right ear servo signal | IO16 (pin 9) | J6 pin 3 |
| Tail servo signal | IO17 (pin 10) | J7 pin 3 |
| Touch pad | IO1 (pin 39) | R4 1k -> J3 |
| Mic (op-amp output) | IO4 (pin 4) | U3 MCP6001 output |
| Speaker signal | IO5 (pin 5) | R10 1k -> C9 10nF -> C10 0.1uF -> U4 PAM8302 IN+ |
| USB D- / D+ | pins 13 / 14 (native USB) | J1 USB-C |
| Reset | EN (pin 3) | R3 10k pull-up to 3.3V, C5 1uF, SW1 to GND |
| Boot | IO0 (pin 27) | SW2 to GND |

- J2 screen header order: GND, VCC (3.3V), SCL, SDA, RES, DC, CS (7 pins, no backlight pin)
- Servo headers J5/J6/J7: pin 1 GND, pin 2 +5V, pin 3 signal
- Unused ESP32 pins (unconnected): IO2, IO3, IO6, IO7, IO8, IO9, IO18, IO21, IO35-IO42, IO45, IO46, IO47, IO48, RXD0, TXD0

## Power
- USB-C VBUS = +5V rail: servos, PAM8302 amp, AP2114H input
- AP2114H-3.3 (U1): +5V -> +3V3 for the ESP32, screen, mic op-amp
- C14 470uF on +5V (servo buffer)
- CC1 / CC2: 5.1k pull-downs (R1, R2)
- PAM8302 shutdown pin (~SD) tied to +5V, so the amp is always on

## Mic circuit numbers
- MK1 bias: R5 2.2k from 3.3V
- Coupling: C8 1uF
- Bias divider: R7 / R8 100k / 100k (half of 3.3V)
- Op-amp gain: 1 + R6/R9 = 1 + 100k/1k = 101x (about 40 dB), R9 to GND through C7 10uF

## Speaker circuit numbers
- R10 1k + C9 10nF low-pass: corner about 15.9 kHz (1 / (2 x pi x 1k x 10nF))
- C10 0.1uF into IN+, C11 0.1uF from IN- to GND

## Schematic part list (38 parts, 23 BOM lines after the fix)
| Refs | Value | Qty |
|---|---|---|
| C1-C3, C7, C12 | 10uF 0805 | 5 |
| C4, C6, C10, C11, C13 | 0.1uF 0805 | 5 |
| C5, C8 | 1uF 0805 | 2 |
| C9 | 10nF 0805 | 1 |
| C14 | 470uF electrolytic 8x10 | 1 |
| R1, R2 | 5.1k 0805 | 2 |
| R3 | 10k 0805 | 1 |
| R4, R9, R10 | 1k 0805 | 3 |
| R5 | 2.2k 0805 | 1 |
| R6-R8 | 100k 0805 | 3 |
| U1 | AP2114H-3.3 (SOT-223) | 1 |
| U2 | ESP32-S3-WROOM-1 | 1 |
| U3 | MCP6001 (SOT-23-5) | 1 |
| U4 | PAM8302AAS (SOIC-8) | 1 |
| J1 | USB-C 16-pin (footprint HRO TYPE-C-31-M-12) | 1 |
| J2 | 1x07 header (screen) | 1 |
| J3 | 1x01 header (touch) | 1 |
| J4 | 1x02 header (speaker) | 1 |
| J5, J6, J7 | 1x03 headers (ear L, ear R, tail) | 3 |
| MK1 | 1x02 header (mic) | 1 |
| SW1, SW2 | 6 mm tactile, through-hole (RESET, BOOT) | 2 |

## Cost (from bom.csv, not re-checked today)
- Priced lines: 10 of 16, all Robu
- Total of priced lines: Rs 1,674.61 (matches the "cart total Rs1674.61 on 4 Nov" note in bom.csv)
- Biggest items: 3 x SG90 Rs 555, GC9A01 screen Rs 449, ESP32-S3 module Rs 409
- No price yet: JLCPCB PCB, USB-C receptacle, PAM8302AAS, electret mic, 0805 passives, 3D-printed shell

## Fab outputs (hardware/fab/)
- bob-gerbers-jlcpcb.zip: 9 Gerber layers (Protel extensions) + PTH and NPTH Excellon drill (mm) + job file, 12 files
- bob-bom.csv: grouped schematic BOM, 23 lines
- bob-positions.csv: pick-and-place, 38 parts, mm
- bob-schematic.pdf: schematic
- bob-schematic.png: schematic image, 3508 x 2480
- bob-top.png: 3D render, top
- bob-bottom.png: 3D render, bottom

## Images to link
- hardware/fab/bob-top.png
- hardware/fab/bob-bottom.png
- hardware/fab/bob-schematic.png
- face/preview.png (already in README)
- banner.png (already in README)

## Things in the current docs that no longer match the design
- README: "about 73 x 63 mm" (actual 73.0 x 62.5)
- README status: "PCB layout ... routing the last few wires, then DRC" (board is routed, DRC 0 errors)
- REPORT.md: Robu cart Rs 1,297.61 and "2 x SG90" (bom.csv now: 3 x SG90, Rs 1,674.61)
- REPORT.md: "NS4168 amp" (board uses PAM8302AAS)
- REPORT.md next steps still say "Draw the schematic + PCB in KiCad"
