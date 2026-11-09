# Fallen design submission checklist

From fallen.hackclub.com/docs/submitting, checked 9 Nov 2026.

## README.md

- [ ] What Bob is and **how to use him**: HIS job (what is there, how-to-use is not)
- [x] Why he made it
- [ ] Screenshot: full 3D assembly (board + shell): HIS job, needs the shell first
- [x] Screenshot: PCB (`hardware/fab/bob-top.png`)
- [ ] Screenshot: schematic: HIS job, re-export `hardware/fab/bob-schematic.png` from KiCad (current PNG shows the old amp chip name)
- [ ] Optional: 3D render, pinout, poster

## Repo files

- [x] STEP of the board: `hardware/fab/bob-board.step` (J1 USB-C has no 3D model in it; KiCad's library has none for HRO TYPE-C-31-M-12)
- [ ] STEP of the shell: HIS job (design in Tinkercad/Onshape)
- [ ] Assembly source (.f3d / .FCStd / Onshape link) with the board STEP inside: HIS job
- [x] `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`
- [ ] `.kicad_prl`: missing, it is in `.gitignore` but Fallen lists it
- [x] Gerbers zip: `hardware/fab/bob-gerbers-jlcpcb.zip`
- [ ] Firmware (untested is fine): HIS job
- [x] BOM csv with a link per item: `bom.csv` (only the shell has no link, not designed yet)
- [ ] Repo public on GitHub with all of the above pushed: HIS call

## Before ordering

- [x] DRC 0 errors, 0 unconnected, 0 parity; ERC 0 errors
- [ ] Warnings, HIS call: DRC 16 (9 silk clipped by mask, 7 silk overlap), ERC 7 (dangling wire ends)
- [ ] JLCPCB quote: check the via size option on the order page accepts 0.2 mm hole / 0.45 mm via (see below)

0.2 mm holes on the board: 8 vias at 0.2/0.45 and 12 in U2's thermal pad at 0.2/0.6.
JLCPCB charges more only for 0.2 mm holes with a via diameter under 0.45 mm, so neither should add cost.
