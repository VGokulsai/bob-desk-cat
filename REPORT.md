# Bob, the desk cat: parts and cost report (30 Oct 2026)

Hack Club Fallen project. Bob is my own sketchbook cat, turned into a palm-sized robot with a round screen face. He breathes, blinks, purrs when you pat his head, looks up when you talk, and his ears twitch. Everything runs offline, so the demo works at Maker Faire Shenzhen (11-14 Dec 2026).

## Cost
Robu prices were checked live on 30 Oct 2026. Everything else is an estimate to check when ordering.

| Group | Rupees | Status |
|---|---|---|
| Robu cart: 10 lines, list in bom.csv | **1,297.61** | checked, in cart (shipping shown at checkout) |
| Custom PCB (JLCPCB, 5 pcs, HASL) + small chips from LCSC + shipping to India + customs | about 2,000 - 3,500 | **estimate** |
| 3D-printed shell, local service | about 500 - 1,500 | **estimate** |
| **Total for full Bob** | **about 3,800 - 6,300** | |
| Tools, only if I don't have them (iron, solder, flux, tweezers, multimeter) | about 800 - 1,500 | **estimate** |
| Optional: WeAct ESP32-S3 dev board, for coding before the PCB arrives | 1,099 | checked; probably NOT funded (Fallen rule on dev boards); asked in #fallen-help |

Power: a 5 V 2 A USB charger and a USB-C cable I already own. No battery.

## Who pays
- Fallen funds parts from bom.csv by quality, on an HCB grant card, once the BOM is approved. So **don't pay for the cart yourself yet**; it waits for the grant card.
- The dev board is the one thing I might pay for myself.

## Why each part
- **ESP32-S3-WROOM-1 module:** Fallen wants our own ESP32 board, so the module goes on a PCB I design (no dev boards).
- **Round GC9A01 screen:** Bob's face. It's wired with short jumpers so it can sit in the shell's face, away from the board.
- **2 x SG90:** ears. The 470 uF capacitors stop the servos from resetting the board when they start.
- **Speaker + NS4168 amp:** purr.
- **Electret mic + MCP6001:** hears talking and claps.
- **AP2114H-3.3 (1 A):** clean 3.3 V from USB.
- **Buttons:** BOOT and RESET, so code can be uploaded.

## Next steps
1. Hear back from #fallen-help: dev board allowed? How long does BOM approval and the grant card take?
2. Draw the schematic + PCB in KiCad, and fix the exact resistor and capacitor values.
3. Order the PCB + LCSC parts by **14 Nov**. Order the Robu cart with the grant card.
