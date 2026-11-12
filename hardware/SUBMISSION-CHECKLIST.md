# Fallen design submission checklist

From fallen.hackclub.com/docs/submitting, checked 9 Nov 2026.

## README.md

- [ ] What Bob is and **how to use him**: HIS job (what is there, how-to-use is not)
- [x] Why he made it
- [ ] Screenshot: full 3D assembly (board + shell): HIS job, needs the shell first
- [x] Screenshot: PCB (`hardware/fab/bob-top.png`)
- [x] Screenshot: schematic: `hardware/fab/bob-schematic.png` re-exported 10 Nov from the current schematic (shows PAM8302AASCR; `kicad-cli sch export svg -n`, rendered 3508x2480 on white with headless Edge)
- [ ] Optional: 3D render, pinout, poster

## Repo files

- [x] STEP of the board: `hardware/fab/bob-board.step` (J1 USB-C has no 3D model in it; KiCad's library has none for HRO TYPE-C-31-M-12)
- [ ] J1 3D model, HIS call whether to attach it. The footprint already points at
  `${KICAD10_3DMODEL_DIR}/Connector_USB.3dshapes/USB_C_Receptacle_HRO_TYPE-C-31-M-12.step`, a file KiCad does not ship. Sources found 10 Nov:
  - SnapMagic (SnapEDA), free login: https://www.snapeda.com/parts/TYPE-C-31-M-12/HRO%20Electronics%20Co.,%20Ltd./view-part/
    Licence: CC BY-SA 4.0 with SnapMagic's "Design Exception 1.0" (boards made with it can be shared on any terms; snapeda.com/about/terms, sections 4.1-4.2). The cleanest licence of the three.
  - GitHub, same file name the footprint expects: https://github.com/NabuCasa/yellow-3dshapes/blob/main/USB_C_Receptacle_HRO_TYPE-C-31-M-12.step
    Converted from the ai03 model below. **No licence** on the repo.
  - GitHub original: https://github.com/ai03-2725/Type-C.pretty/blob/master/HRO%20%20TYPE-C-31-M-12.step (made by ryotagoto, 2018). **No licence** on the repo.
  - Ultra Librarian has the symbol and footprint but "No 3D Model Available".
- [ ] STEP of the shell: HIS job (design in Tinkercad/Onshape)
- [ ] Assembly source (.f3d / .FCStd / Onshape link) with the board STEP inside: HIS job
- [x] `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`
- [x] `.kicad_prl`: tracked since commit 9139a4b
- [x] Gerbers zip: `hardware/fab/bob-gerbers-jlcpcb.zip`
- [ ] Firmware (untested is fine): HIS job
- [x] BOM csv with a link per item: `bom.csv` (only the shell has no link, not designed yet). Prices and stock checked live 10 Nov; see `hardware/FUNDING-ESTIMATE.md`
- [ ] BOM fixes, HIS call: MCP6001T is out of stock at Robu (LCSC C116490 has it); the SG90 link is a search that now finds nothing; PAM8302 qty 3 includes 2 spares, and Fallen says not to include extra parts
- [ ] Repo public on GitHub with all of the above pushed: HIS call

## Before ordering

- [x] DRC 0 errors, 0 unconnected, 0 parity; ERC 0 errors (re-checked 12 Nov after the mounting holes)
- [x] Mounting holes: 3 x M2.5 (H1-H3, 2.7 mm NPTH) added 12 Nov; positions in `SHELL-SPEC.md`. No top-right hole (no clear spot near J1); gerbers, drill, STEP, renders and schematic re-exported
- [ ] Warnings, HIS call: DRC 16 (9 silk clipped by mask, 7 silk overlap), ERC 7 (dangling wire ends)
- [ ] JLCPCB quote: check the via size option on the order page accepts 0.2 mm hole / 0.45 mm via (see below)

0.2 mm holes on the board: 8 vias at 0.2/0.45 and 12 in U2's thermal pad at 0.2/0.6.
JLCPCB charges more only for 0.2 mm holes with a via diameter under 0.45 mm, so neither should add cost.
