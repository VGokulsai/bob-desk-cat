# Bob shell: measurements and constraints

Reference numbers for designing the shell. This is not a design. Where a value comes
from a datasheet, measure your own part with calipers before you print. Cheap modules vary.

All board coordinates are in mm, top view, **origin at the board's top-left corner**,
x to the right, y down. (In KiCad that corner is (149.5, 46.5). `fab/bob-positions.csv`
uses the same points with y negated.) Extracted from `bob's project.kicad_pcb` on 11 Nov 2026.

## 1. The board

| What | Value |
|---|---|
| Outline | 73.0 x 62.5 mm rectangle, square corners |
| Thickness | 1.6 mm |
| Mounting holes | **None.** The board has no mounting holes; see "Holding the board" below |
| Parts side | Everything is on the top. The bottom only has through-hole pin tails |
| Bottom clearance | Leave 3 mm under the board for header/switch tails and solder, or trim them |

### Top view

```
       x=0                                                           x=73
      +-------------------------------------------------------------------------+
  0.0 |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~          +-------+|
      |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~          |.......||
      |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~          |J1 USB.|| <- USB-C mouth, right edge
      |      ~~~~~~~~~~~~~~~~~ANTENNA KEEPOUT~~~~~~~~~~~~~~~~          |.......||
 10.0 |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~          +-------+|
      |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            +--+   |
      |      ~~~~~~~~~~~~~~~+-----------------+~~~~~~~~~~~~~~            |U1|   |
      |      ~~~~~~~~~~~~~~~|.................|~~~~~~~~~~~~~~            +--+   |
 20.0 |      ~~~~~~~~~~~~~~~|.................|~~~~~~~~~~~~~~                   |
      |                     |.................|                                 |
      |  +-----+            |.................|                             +--+|
      |  |.SW1.|            |....ESP32-S3.....|        +-----+          +3-+|..||
 30.0 |  +-----+            |.................|   +--+ |.U4..|          +--+|..||
      | +-----+             |.................|   |J4| +-----+              |..||
      | |.SW2.|             |.................|   +--+                      |J2||
      | |.....|             |.................|                             |..||
 40.0 | +-----+             +-----------------+                             |..||
      |                                                                     |..||
      |                                                                     +--+|
      |                                                       +-------+ +--++--+|
 50.0 |                                                       |..C14..| |5.||6.||
      |                                                       |.......| |..||..||
      |+--+                                                   +-------+ +--++--+|
      ||M.|                                                      +--J7---+      |
 60.0 |+--+                                                      +-------+      |
      +-------------------------------------------------------------------------+  y=62.5
 1 char = 1 mm across, 1 row = 2.5 mm down.  3 = J3 touch, 5/6 = J5/J6 ears, M = MK1 mic
```

### Connectors and parts the shell cares about

Body = the part's outline on the F.Fab layer. Heights are above the board's top surface.

| Ref | What | Body x (mm) | Body y (mm) | Height | Notes |
|---|---|---|---|---|---|
| J1 | USB-C, HRO TYPE-C-31-M-12 | 64.8 to 72.1 | 1.2 to 10.2 | about 3.2 | Mouth faces **+x (right edge)**, centred at **y = 5.68**. Mouth is 0.9 mm in from the edge |
| J2 | Display header, 1x7, 2.54 mm | pins at x 71.0 | pins y 28.76 to 44.00 | 8.5 bare, about 16.5 with a Dupont housing on | Pin 1 (top) to 7: GND, 3V3, SCL, SDA, RES, DC, CS |
| J3 | Touch pad wire, 1 pin | pin at (67.0, 30.5) | | 8.5 / 16.5 | Wire runs from here to a pad you put in the shell |
| J4 | Speaker, 1x2 | pins at x 45.0 | y 31.46, 34.00 | 8.5 / 16.5 | Speaker's own 300 mm lead plugs in here |
| J5 | Left ear servo, 1x3 | pins at x 67.0 | y 49.42, 51.96, 54.50 | 8.5 / about 17 with the servo plug | Pin 1 (top) GND, 5V, signal = SG90 brown, red, orange |
| J6 | Right ear servo, 1x3 | pins at x 71.0 | y 49.42, 51.96, 54.50 | same | same pin order |
| J7 | Tail servo, 1x3, runs left-right | pins at y 59.8 | x 65.04 (pin 1), 62.50, 59.96 | same | same pin order |
| MK1 | Mic, 1x2 | pins at x 2.0 | y 57.46 (GND), 60.00 (+) | 8.5 / 16.5 | Capsule is off-board on wires |
| SW1 | RESET (EN), 6x6 tact | 2.0 to 8.0 | 25.0 to 31.0 | 5.0 | Pushes down from the top |
| SW2 | BOOT (IO0), 6x6 tact | 1.75 to 7.75 | 34.75 to 40.75 | 5.0 | Only needed to recover a bad flash |
| U2 | ESP32-S3-WROOM-1 | 21.4 to 39.4 | 16.5 to 42.0 | 3.1 (18 x 25.5 x 3.1 module) | Antenna is the top end (y 16.5 side) |
| C14 | 470 uF, 8 x 10 can | 55.6 to 63.9 | 48.4 to 56.7 | **about 10.5, tallest soldered part** | Product title: D8 x L10 mm |
| U1 | 3.3 V LDO, SOT-223 | 66.0 to 69.7 | 12.6 to 19.3 | 1.8 | The warm part (5 V to 3.3 V drop) |
| U4 | Speaker amp, MSOP-8 | 48.3 to 54.7 | 29.8 to 33.3 | about 1.1 | |

Antenna keepout (copper keepout from the footprint): x 6.4 to 54.4, y 1.5 to 22.5.

**Tallest thing over the board:** a Dupont or servo plug on a vertical header, about 16.5 to
17 mm, plus room for the wire to bend (about 5 mm more). If you want a flatter body, that is
the number to beat; the soldered parts stop at about 10.5 mm (C14).

### Free board edge (for rails, clips or ribs)

No courtyard within 2 mm of the edge in these spans:

| Edge | Free spans |
|---|---|
| Top (y = 0) | x 0 to 6.4, and x 54.4 to 63.2 (x 6.4 to 54.4 is only antenna keepout, no parts, plastic is fine there) |
| Bottom (y = 62.5) | x 7.9 to 58.2 |
| Left (x = 0) | y 0 to 24.2, y 41.5 to 55.7 |
| Right (x = 73) | y 19.5 to 22.4, y 56.3 to 62.5 |

### Holding the board (no holes, so pick one)

| Option | How | Trade-off |
|---|---|---|
| Slide-in rails | Two grooves on the left and right walls, 1.6 mm board + clearance (see fits), board slides in from the bottom edge | Easy, no screws. Right edge is crowded (J1, J2, J6), so the lip over the top can only be about 1 mm deep there, or rails go on top/bottom edges instead |
| Ledge + clamp ribs | Board sits on a ledge or 4 short posts underneath; ribs on the lid press down on free top-surface spots | Simple to print. Needs the lid to close on the right height |
| Snap clips | Flexible hooks over the board edge at free spans | Neat, but clips break in PLA if too short; make the flex arm 10 mm or longer |
| Glue or double-sided foam | Hot glue at the corners | Fastest. Hard to repair |

## 2. Off-board parts

### GC9A01 1.28" round display (GoldenMorning, 7 pin)

| What | Value | Source |
|---|---|---|
| Module outline | 38.00 x 45.50 x 11.20 mm (round board plus the header tab; 11.2 includes the pins) | [GoldenMorning GMT128-02 page](https://goldenmorninglcd.com/tft-display-module/1.28-inch-240x240-gc9a01-gmt128-02/) |
| Active (visible) area | 32.40 mm diameter | same; also [LCD wiki](https://www.lcdwiki.com/1.28inch_IPS_Module) |
| Glass panel | 35.6 x 37.74 x 1.55 mm | [panel datasheet via Electrokit](https://www.electrokit.com/upload/quick/d8/f0/de53_1.28_LCD.pdf) |
| Pins | 7, 2.54 mm: GND, VCC, SCL, SDA, RES, DC, CS, on the tab side | GoldenMorning page |
| Mounting holes | Not stated on any page found. Check your module | |

Face opening: at least 32.4 mm across so no pixels hide; the glass is 35.6 mm, so a 33 to 34 mm
window with a pocket behind it for the glass and board holds it from the front. The GoldenMorning page
lists the model as both GMT128-02 and GMT128-06, so measure the one Robu sends.
Robu's own page refused automated fetches (403), so these are the maker's numbers.

### SG90 servo (x3)

Generic SG90s differ by a few tenths of a mm between batches, so measure one before you print.

| What | Value | Source |
|---|---|---|
| Body (top view) | about 22.5 to 23.0 x 11.8 to 12.2 mm | [TowerPro SG90](https://towerpro.com.tw/product/sg90-7/) gives 23 x 12.2 x 29; [kernelCAD](https://kernelcad.com/standards/micro-servo/) gives 22.5 x 11.8 |
| Body height (bottom to top of case) | 22.7 mm | TowerPro table "B", kernelCAD |
| Overall height to top of shaft | about 29 to 30 mm | TowerPro 29, kernelCAD 29.9 |
| Tab tip to tab tip | 32.3 mm | TowerPro table "E" |
| Tab hole spacing | 27.2 to 27.5 mm, holes 2.0 mm | kernelCAD 27.2; [sargineer](https://sargineer.com/p/mg90s-micro-servo) 27.25 |
| Tab thickness | 2.5 mm | kernelCAD |
| Tab underside above the bottom | about 15.9 mm | sargineer ("flange sitting on 15.9 shelf") |
| Output shaft | Centred across the width, near one end (the gear tower end) | |
| Wire | 250 mm, exits low on the shaft end; JR plug, 2.54 mm | TowerPro, [New Screwdriver notes](https://newscrewdriver.com/2020/12/26/notes-on-micro-servo-enclosure/) |
| Travel | about 180 deg (Robu listing), 90 deg on some datasheets | |

Pocket: a 23.0 x 12.2 mm cutout with the tabs resting on a shelf is the usual fit (sargineer);
add your clearance. Leave a slot for the wire on the shaft end. Horns come in the bag (single, double,
cross) with screws; measure the horn you pick, since ears and tail attach to it.

### Electret mic, 9.7 mm (Dragonstate AMF-O97L45-DB)

| What | Value | Source |
|---|---|---|
| Diameter | 9.7 mm | [LCSC C20200114](https://www.lcsc.com/product-detail/C20200114.html) |
| Height | **Not listed** by LCSC or the resellers found. 9.7 mm capsules are often 4.5 to 6.7 mm tall: measure | |
| Mounting | Through-hole pins; on wires to MK1 | |

### Speaker (INGHAI GSPK3005TN-8R0.5W-L300S-2.54T)

| What | Value | Source |
|---|---|---|
| Diameter | 30.0 mm | [INGHAI spec sheet (LCSC)](https://atta.szlcsc.com/upload/public/pdf/source/20250915/668447A35218A76F374B60351E6AF0B3.pdf) |
| Depth | 5.0 mm | same |
| Lead | 300 mm, 2.54 mm plug, goes to J4 | [Robu INGHAI listing](https://oldwp.robu.in/brand/inghai/) |
| Range | 200 to 5000 Hz | spec sheet |

### 470 uF cap (C14, Lelon VZH471M1CTR-0810)

8 mm diameter can, 10 mm nominal height ("D8xL10mm" in the [Robu title](https://robu.in/product/vzh471m1ctr-0810-lelon-470uf-16v-%c2%b120-smdd8xl10mm-aluminum-electrolytic-capacitors-smd-rohs-2/)).
Allow 10.5 mm. It is the tallest soldered part.

## 3. Printing

**Fallen:** the public docs (fallen.hackclub.com/docs, source in
[hackclub/fallen](https://github.com/hackclub/fallen), checked 11 Nov) say nothing about how Fallen
prints parts. They only mention 3D printers as XP prizes, and say to put the cheapest manufacturing
in `bom.csv`. The "big 3D printing event" in #fallen-bulletin has no public details I could find. Watch the channel.

**Hack Club's standing route:** [Printing Legion](https://printlegion.hackclub.com), teens with printers who print for other teens.
Upload the STL; the printer is reimbursed for filament. Several members are listed in India. Printers listed there range
from A1 mini (180 mm cube) up, so **keep each part under 180 x 180 x 180 mm** and any printer can take it.

### Typical FDM numbers (starting points; print a test piece first)

| What | Value |
|---|---|
| Minimum wall | 0.8 mm prints anywhere ([Protolabs/Hubs](https://www.hubs.com/knowledge-base/key-design-considerations-3d-printing/)); use **1.6 to 2.0 mm** for a shell that gets handled |
| Overhangs without support | up to about 45 deg (same source) |
| Loose / sliding fit (lid, board in a rail) | 0.3 to 0.4 mm gap per side |
| Snug / press fit (servo in pocket) | 0.1 to 0.2 mm per side |
| Holes print small | add about 0.2 mm to small hole diameters |
| Board rail groove | 1.6 mm board: 2.0 mm wide groove, 1.5 mm deep |
| Self-tapping screw boss, M2 | pilot hole 1.6 to 1.8 mm, boss outer diameter 4.5 to 5 mm |
| Self-tapping screw boss, M2.5 | pilot hole 2.1 to 2.2 mm, boss outer diameter 5.5 to 6 mm |
| Heat-set inserts | hole size comes from the insert's own datasheet; boss wall at least 1.5 mm around it |
| Servo tab screws | the screws in the SG90 bag self-tap into a 1.6 to 1.8 mm pilot hole |
| Big flat faces | warp; add ribs or fillets (Hubs) |

## 4. Layout options

These are options with trade-offs, not a choice. The choice is yours.

### Board orientation

| Option | Trade-off |
|---|---|
| Board flat in the base, parts up | Stable, heavy part low. Base footprint at least 73 x 62.5 + walls (about 78 x 67). Headers face up into the body, so the body needs about 22 mm of height above the board |
| Board upright behind the face | Smaller footprint. USB-C then exits a side or the bottom; C14 and the headers stick out about 17 mm toward the face |

### Ears (2 servos) and tail (1 servo)

| Option | Trade-off |
|---|---|
| Ear servos in the head, shaft up, horn inside the ear | Ears turn around a vertical axis (swivel). Needs head width of about 2 x 23 + 38 mm display |
| Ear servos lying sideways, shaft out through the head's sides | Ears tilt forward and back (flick). Each servo needs about 30 mm along the head's width |
| Tail servo in the back of the body, shaft out the back | Tail wags side to side. Short wire run to J7 (bottom right of the board) |
| Tail servo in the base, shaft up | Tail sweeps in a horizontal arc. Base must be taller than 30 mm there |

Wire reach: servo leads are 250 mm and plug straight onto J5/J6/J7, so any position in a desk-sized cat reaches.
Keep the servo motors and screws away from the antenna area (board top band, y 0 to 22) where you can.

### Display (face)

Display connects by 20 cm jumpers from J2, so it can sit anywhere. Window 32.4 to 34 mm; module needs
38 mm across behind the face and 45.5 mm in the direction of its header tab.

### Speaker and mic

| Option | Trade-off |
|---|---|
| Speaker facing down into the base, with feet to lift it | Hidden grille; sound bounces off the desk |
| Speaker facing out the front or chest | Loudest. Grille holes over about 25 mm of the 30 mm cone |
| Speaker on the back | Tidy front, quieter |

A grille of 1.5 to 2 mm holes works. A closed cavity behind the speaker gives more bass than an open shell.
Mic: a 1 to 2 mm hole in front of the capsule face, away from the speaker and servos (servo whine is picked up).

### USB-C access

Mouth is on the board's right edge at y = 5.68, recessed 0.9 mm. A USB-C plug's overmold is roughly
12.5 x 6.5 mm, so the wall cutout should be at least about 13 x 7 mm, centred on the port.
A 13 mm cutout reaches about 0.8 mm past the board's top edge (5.68 - 6.5), so the corner wall near J1 is open there.
Wall at the port: keep it thin (1.5 to 2 mm) so the plug seats fully.

### Touch pad ("pat the head")

J3 is one pin. Wire it to a piece of copper tape or foil stuck on the **inside** of the head's top.
Keep the plastic over the pad thin (about 1 to 2 mm); thicker walls weaken the reading, and the threshold is set in firmware.
Bigger pad = easier to trigger. Keep it away from the servo wires.

### Airflow

The LDO (U1, at x 66 to 70, y 12.6 to 19.3) is the warm part, right next to J1. A few slots on that
side near the USB cutout are enough. No fan needed.

### Part split

| Split | Trade-off |
|---|---|
| Base + body + head (3 parts) | Each prints without much support; head comes off to reach the ear servos |
| Base + one-piece body/head shell (2 parts) | Fewer seams, harder to reach servos and the display |
| Front half + back half (clamshell) | Easy to assemble around the wires; visible seam down the sides |

Keep each part under 180 mm on every side (smallest Printing Legion printer).

## Still to measure

- Mic capsule height
- Display module board: holes, exact tab length and where the pins sit on it
- One SG90 from the actual batch: body, tab height, shaft position
- The servo horns you will use
